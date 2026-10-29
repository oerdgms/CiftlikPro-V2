"""Read-only finance grouping backed by explicit health-program provenance."""
from collections import defaultdict
from contextvars import ContextVar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from html import escape
import json
import re
from urllib.parse import parse_qs, urlencode, urlparse


REQUEST_URL = ContextVar('cp_finance_request_url', default='/finance')
ASSET_VERSION = '2.0.41'
STATES = [('all', 'Tümü'), ('pending', 'Bekleyen'), ('overdue', 'Gecikmiş'),
          ('income', 'Gelir'), ('expense', 'Gider'), ('loss', 'Zarar')]


def esc(value):
    return escape(str(value if value is not None else ''), quote=True)


def cents(value):
    return int((Decimal(str(value or 0)) * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def filters(request_url, today):
    query = parse_qs(urlparse(request_url).query)
    get = lambda key, default='': (query.get(key) or [default])[0]
    result = {key: get(key) for key in ('type', 'category', 'q')}
    result.update(start=get('start', today.replace(day=1).isoformat()), end=get('end', today.isoformat()))
    result['q'] = result['q'].strip()
    result['status'] = get('status', 'all').lower() or 'all'
    if result['status'] not in dict(STATES):
        result['status'] = 'all'
    try:
        result['per_page'] = int(get('per_page', '20'))
    except ValueError:
        result['per_page'] = 20
    if result['per_page'] not in (10, 20, 50):
        result['per_page'] = 20
    try:
        result['page'] = max(1, int(get('page', '1')))
    except ValueError:
        result['page'] = 1
    return result


def finance_url(values, **changes):
    params = {key: values[key] for key in ('start', 'end', 'type', 'category', 'q', 'status', 'per_page', 'page')}
    params.update(changes)
    return '/finance?' + urlencode(params)


def state(row, today):
    if row['tx_type'] == 'Gelir':
        return 'income'
    if row['tx_type'] == 'Zarar':
        return 'loss'
    if row['payment_method'] == 'Vadeli' and row['payment_status'] != 'Ödendi':
        try:
            if date.fromisoformat(str(row['due_date'])) < today:
                return 'overdue'
        except ValueError:
            pass
        return 'pending'
    return 'expense'


def provenance(c, start, end):
    records = defaultdict(list)
    for raw in c.execute('''select h.id health_id,h.finance_id,h.course_id,h.task_id,
        h.animal_id,h.calf_id,h.kind health_kind,h.applied_date,
        t.course_id task_course,t.animal_id task_animal,t.calf_id task_calf,
        t.planned_date,t.dose_no,t.day_no,t.application_no,t.cycle_no,
        hc.kind course_kind,m.category managed_category,ct.case_id,
        ct.finance_id case_finance,ct.animal_id case_animal,ct.calf_id case_calf
        from health h join finance f on f.id=h.finance_id
        left join health_tasks t on t.id=h.task_id
        left join health_courses hc on hc.id=h.course_id
        left join health_program_meta m on m.course_id=h.course_id
        left join health_case_targets ct on ct.health_id=h.id
        where f.tx_date between ? and ?''', (start, end)):
        records[raw['finance_id']].append(dict(raw))
    return {fid: rows[0] for fid, rows in records.items() if len(rows) == 1}


def group_key(row, record):
    if not record or row['tx_type'] != 'Gider' or cents(row['amount']) <= 0:
        return None
    subject = (row['animal_id'], row['calf_id'])
    if subject != (record['animal_id'], record['calf_id']) or subject == (None, None):
        return None
    if row['animal_status_action'] or row['feed_item_count']:
        return None
    if record['course_id'] and record['task_id']:
        if record['course_id'] != record['task_course'] or subject != (record['task_animal'], record['task_calf']):
            return None
        if row['category'] != record['health_kind'] or record['health_kind'] != record['course_kind']:
            return None
        scope = ('course', record['course_id'], record['cycle_no'], record['dose_no'],
                 record['day_no'], record['application_no'], record['planned_date'])
    elif record['case_id'] and record['case_finance'] == row['id']:
        if subject != (record['case_animal'], record['case_calf']) or row['category'] != 'Sağlık':
            return None
        scope = ('case', record['case_id'])
    else:
        return None
    # Equal product names or dates alone never establish a group. Keep edited
    # descriptions, different payment terms, doses and repeat cycles separate.
    terms = tuple(row[key] or '' for key in ('tx_date', 'tx_type', 'category', 'description',
                  'payment_method', 'due_date', 'payment_status', 'paid_date', 'supplier', 'invoice_no'))
    return sha256(json.dumps((scope, terms), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def group_rows(rows, records):
    buckets = defaultdict(list)
    for row in rows:
        row['_health'] = records.get(row['id'])
        row['_group_key'] = group_key(row, row['_health'])
        if row['_group_key']:
            buckets[row['_group_key']].append(row)
    groups = {key: members for key, members in buckets.items() if len(members) > 1 and
              len({(r['animal_id'], r['calf_id']) for r in members}) == len(members)}
    result = []
    seen = set()
    for row in rows:
        key = row['_group_key']
        if key in groups:
            if key in seen:
                continue
            seen.add(key)
            members = groups[key]
            entry = dict(row)
            entry.update(amount=sum(cents(r['amount']) for r in members) / 100,
                         members=members, group_id=key)
            result.append(entry)
        else:
            result.append(dict(row, members=[row], group_id=None))
    return result


def load(ns, request_url):
    today = ns['date'].today()
    values = filters(request_url, today)
    sql = '''select f.*,coalesce(a.tag,ca.tag) tag,
        coalesce(a.nickname,ca.nickname,'') nickname,
        coalesce(nullif(a.paddock,''),nullif(ca.paddock,''),'') paddock,
        case when f.category='Süt Satışı'
             then coalesce((select group_concat(a2.tag, ', ') from finance_animals fa
                  join animals a2 on a2.id=fa.animal_id
                  where fa.finance_id=f.id and fa.relation_type='Süt Satışı'),a.tag)
             else coalesce(a.tag,ca.tag) end related_tags,
        (select count(*) from finance_feed_items ffi where ffi.finance_id=f.id) feed_item_count
        from finance f left join animals a on a.id=f.animal_id
        left join calves ca on ca.id=f.calf_id where tx_date between ? and ?'''
    args = [values['start'], values['end']]
    for field, column in [('type', 'tx_type'), ('category', 'category')]:
        if values[field]:
            sql += ' and f.' + column + '=?'
            args.append(values[field])
    sql += ' order by f.tx_date desc,f.id desc'
    with ns['db']() as c:
        rows = [dict(r) for r in c.execute(sql, args)]
        records = provenance(c, values['start'], values['end'])
        if values['q']:
            rows = [r for r in rows if ns['search_matches'](values['q'], *(r[key] for key in
                    ('description', 'supplier', 'invoice_no', 'tag', 'related_tags', 'category')))]
        entries = group_rows(rows, records)
        counts = dict.fromkeys(dict(STATES), 0)
        counts['all'] = len(entries)
        for entry in entries:
            current = state(entry, today)
            counts[current] += 1
            if current == 'overdue':
                counts['pending'] += 1
        selected = [r for r in entries if values['status'] == 'all' or
                    (state(r, today) in ('pending', 'overdue') if values['status'] == 'pending'
                     else state(r, today) == values['status'])]
        pages = max(1, (len(selected) + values['per_page'] - 1) // values['per_page'])
        values['page'] = min(values['page'], pages)
        offset = (values['page'] - 1) * values['per_page']
        visible = selected[offset:offset + values['per_page']]
        feed_items = defaultdict(list)
        invoice_ids = [r['id'] for r in visible if not r['group_id'] and r['feed_item_count']]
        if invoice_ids:
            placeholders = ','.join('?' for _ in invoice_ids)
            for raw in c.execute('''select ffi.*,fc.name feed_name from finance_feed_items ffi
                    join feed_catalog fc on fc.id=ffi.feed_id where ffi.finance_id in ('''+placeholders+') order by ffi.id', invoice_ids):
                feed_items[raw['finance_id']].append(dict(raw))
    return {'filters': values, 'entries': entries, 'selected': selected, 'visible': visible,
            'counts': counts, 'pages': pages, 'offset': offset, 'feed_items': feed_items,
            'has_groups': any(r['group_id'] for r in entries),
            'raw_count': sum(len(r['members']) for r in selected)}


def phase(row):
    record = row['_health']
    if record['case_id']:
        return 'Hastalık kaydı'
    labels = []
    if record['cycle_no'] > 1:
        labels.append(str(record['cycle_no']) + '. dönem')
    if record['health_kind'] == 'Aşı':
        labels.append(str(record['dose_no']) + '. doz')
    elif record['day_no'] > 1 or record['application_no'] > 1:
        labels.append(str(record['day_no']) + '. gün')
        labels.append(str(record['application_no']) + '. uygulama')
    return ' · '.join(labels) or 'Sağlık uygulaması'


def detail_url(entry, values):
    return '/finance/health-group?' + urlencode({'group': entry['group_id'], 'return_to': finance_url(values)})


def due_cell(ns, row):
    if row['payment_method'] != 'Vadeli':
        return '<span class="mut">-</span>'
    if row['payment_status'] == 'Ödendi':
        return '<span class="pill">✅ Ödendi<br>' + esc(ns['fmt_date'](row['paid_date'])) + '</span>'
    try:
        days = (date.fromisoformat(str(row['due_date'])) - ns['date'].today()).days
    except ValueError:
        days = 9999
    badge = '🔴 Gecikmiş' if days < 0 else '🟠 Bugün' if days == 0 else f'🟡 {days} gün'
    return '<span class="pill">' + badge + '<br>' + esc(ns['fmt_date'](row['due_date'])) + '</span>'


def description_cell(ns, row, items):
    base = esc(row['description']) or '<span class="mut">-</span>'
    if not items:
        return base
    money = ns['money']
    meta = [('Tedarikçi: ' + esc(row['supplier'])) if row['supplier'] else '',
            ('Fatura No: ' + esc(row['invoice_no'])) if row['invoice_no'] else '']
    lines = ''.join(f'<div class="feed-invoice-line"><b>{esc(x["feed_name"])}</b><span>{float(x["quantity"] or 0):g} {esc(x["unit"])} × {money(x["purchase_unit_price"])} = <b>{money(x["line_total"])}</b></span><small>{float(x["quantity_kg"] or 0):g} kg · stok maliyeti {money(x["unit_price"])}/kg</small></div>' for x in items)
    payment = ''
    if row['payment_method'] == 'Vadeli':
        paid = row['payment_status'] == 'Ödendi'
        label = '✅ Ödendi' if paid else '🕒 Ödenmedi / Bekliyor'
        when = ns['fmt_date'](row['paid_date'] if paid else row['due_date'])
        action = '/finance/unmark-paid' if paid else '/finance/mark-paid'
        question = 'Bu faturayı tekrar Ödenmedi/Bekliyor durumuna almak istiyor musunuz?' if paid else 'Bu faturayı Ödendi olarak işaretlemek istiyor musunuz?'
        button = '↩ Ödenmedi Yap' if paid else '✅ Ödendi Yap'
        extra = '' if paid else f'<input type="hidden" name="paid_date" value="{ns["date"].today().isoformat()}">'
        payment = f'<div class="feed-invoice-payment {"paid" if paid else "pending"}"><div><b>{label}</b><span>{"" if paid else "Vade: "}{esc(when)}</span></div><form method="post" action="{action}" data-submit-lock="1" data-submit-text="⏳ İşleniyor…" onsubmit="return confirm(\'{question}\')"><input type="hidden" name="id" value="{row["id"]}">{extra}<button class="btn{(" alt" if paid else "")}">{button}</button></form></div>'
    preview_id = 'feedInvoicePreview' + str(row['id'])
    panel = '<div class="feed-invoice-meta">' + (' · '.join(filter(None, meta)) or 'Fatura bilgisi') + '</div>' + lines + f'<div class="feed-invoice-total">Toplam <b>{money(row["amount"])}</b></div>' + payment
    return f'<button type="button" class="feed-invoice-preview-btn" onclick="openFeedInvoicePreview(\'{preview_id}\')">🧾 Yem Faturası · {len(items)} kalem</button><template id="{preview_id}">{panel}</template><div class="mut">{base}</div>'


def transaction_row(ns, row, model):
    values = model['filters']
    if row['group_id']:
        url = esc(detail_url(row, values))
        title = esc(row['description'] or row['category'])
        count = len(row['members'])
        description = f'<a class="cp-finance-group-title" href="{url}">{title}</a><span class="cp-finance-group-meta">{count} hayvan · {esc(phase(row))}</span>'
        related = f'<span class="cp-finance-group-badge">{count} hayvan</span>'
        actions = f'<a class="btn alt" href="{url}">Dağılımı gör ›</a>'
        attrs = f' class="cp-finance-group" data-finance-group="{row["group_id"]}"'
    else:
        description = description_cell(ns, row, model['feed_items'].get(row['id'], []))
        related = esc(row['related_tags'])
        if row['animal_status_action'] == 'AGRI_INTERNAL':
            actions = '<a class="btn alt" href="/agriculture/transfers">Tarım Transferine Git</a>'
        else:
            actions = f'<a class="btn alt" href="/finance/edit?id={row["id"]}">Düzenle</a><form method="post" action="/finance/delete" onsubmit="return confirm(\'Bu finans kaydı silinsin mi? Bağlı yem stokları da geri alınır.\')"><input type="hidden" name="id" value="{row["id"]}"><button class="btn danger">Sil</button></form>'
        attrs = ''
    status = 'Tarım İç Transferi' if row['animal_status_action'] == 'AGRI_INTERNAL' else (row['animal_status_action'] or '-')
    cells = [esc(ns['fmt_date'](row['tx_date'])), esc(row['tx_type']), esc(row['category']), description,
             related, esc(status), esc(row['payment_method']), due_cell(ns, row),
             '<b>' + esc(ns['money'](row['amount'])) + '</b>', '<div class="finance-actions">' + actions + '</div>']
    return '<tr' + attrs + '>' + ''.join('<td>' + cell + '</td>' for cell in cells) + '</tr>'


def decorate(ns, body, request_url):
    if 'id="financeRecords"' not in body or 'class="finance-table"' not in body:
        return body
    model = load(ns, request_url)
    if not model['has_groups']:
        return body
    values = model['filters']
    content = ''.join(transaction_row(ns, row, model) for row in model['visible']) or '<tr><td colspan="10" class="workspace-empty">Filtrelere uygun finans kaydı bulunamadı.</td></tr>'
    table = '<table class="finance-table"><tr>' + ''.join('<th>' + label + '</th>' for label in ('Tarih', 'Tür', 'Kategori', 'Açıklama', 'Hayvan', 'Durum', 'Ödeme', 'Vade', 'Tutar', 'İşlem')) + '</tr>' + content + '</table>'
    body = re.sub(r'<table class="finance-table">.*?</table>', lambda _: table, body, count=1, flags=re.S)
    tabs = '<nav class="count-tabs">' + ''.join(f'<a class="count-tab {"active" if values["status"] == key else ""}" href="{esc(finance_url(values, status=key, page=1))}">{label}<b>{model["counts"][key]}</b></a>' for key, label in STATES) + '</nav>'
    body = re.sub(r'<nav class="count-tabs">.*?</nav>', lambda _: tabs, body, count=1, flags=re.S)
    count = len(model['selected'])
    label = f'{count} işlem · {model["raw_count"]} kayıt'
    body = re.sub(r'<span class="filter-count-pill">\d+ kayıt</span>', lambda _: '<span class="filter-count-pill">' + label + '</span>', body, count=1)
    previous = f'<a class="btn alt" href="{esc(finance_url(values, page=values["page"] - 1))}">← Önceki</a>' if values['page'] > 1 else ''
    following = f'<a class="btn alt" href="{esc(finance_url(values, page=values["page"] + 1))}">Sonraki →</a>' if values['page'] < model['pages'] else ''
    pager = f'<div class="workspace-pager"><span class="mut">{label} · Sayfa {values["page"]}/{model["pages"]}</span><div>{previous}{following}</div></div>'
    body = re.sub(r'<div class="workspace-pager">.*?</div></div>', lambda _: pager, body, count=1, flags=re.S)
    return f'<link rel="stylesheet" href="/app-assets/finance-groups.css?v={ASSET_VERSION}">' + body


def safe_return(raw):
    parsed = urlparse(str(raw or ''))
    if parsed.scheme or parsed.netloc or parsed.path != '/finance' or len(raw or '') > 3000:
        return '/finance'
    return '/finance' + ('?' + parsed.query if parsed.query else '')


def detail(ns, request_url):
    query = parse_qs(urlparse(request_url).query)
    back = safe_return((query.get('return_to') or ['/finance'])[0])
    key = (query.get('group') or [''])[0]
    if not re.fullmatch('[0-9a-f]{64}', key):
        return None, back
    model = load(ns, back)
    entry = next((r for r in model['selected'] if r['group_id'] == key), None)
    if not entry:
        return None, back
    cards = ''
    for row in sorted(entry['members'], key=lambda r: str(r['tag'] or '')):
        record = row['_health']
        sid = row['animal_id'] or row['calf_id']
        animal_url = ('/animal?id=' if row['animal_id'] else '/calf?id=') + str(sid)
        edit = '/health?record_edit=' + str(record['health_id']) if record['managed_category'] else '/health-edit?id=' + str(record['health_id'])
        if record['case_id']:
            edit = '/health?category=treatment&case_edit=' + str(record['case_id'])
        search = ' '.join(str(row[key] or '') for key in ('tag', 'nickname', 'paddock'))
        cards += f'<article class="cp-finance-member" data-finance-member data-search="{esc(search)}"><div><a href="{animal_url}">{esc(row["tag"] or "Arşiv kaydı")}</a><small>{esc(row["nickname"] or ("Buzağı" if row["calf_id"] else "Hayvan"))}{(" · " + esc(row["paddock"])) if row["paddock"] else ""}</small></div><b>{esc(ns["money"](row["amount"]))}</b><a class="cp-finance-member-edit" href="{esc(edit)}">Sağlık kaydı ›</a></article>'
    amounts = {cents(r['amount']) for r in entry['members']}
    each = ns['money'](next(iter(amounts)) / 100) + ' / hayvan' if len(amounts) == 1 else 'Hayvana göre dağılım'
    title = entry['description'] or entry['category']
    body = f'''<link rel="stylesheet" href="/app-assets/finance-groups.css?v={ASSET_VERSION}"><section class="cp-finance-group-detail">
      <header><a class="cp-finance-back" href="{esc(back)}">← Finansa dön</a><span class="cp-finance-detail-eyebrow">TOPLU SAĞLIK GİDERİ</span><h1>{esc(title)}</h1><p>{esc(ns['fmt_date'](entry['tx_date']))} · {esc(phase(entry))} · {esc(entry['payment_method'])}</p></header>
      <div class="cp-finance-group-summary"><div><small>Toplam gider</small><strong>{esc(ns['money'](entry['amount']))}</strong></div><div><small>Hayvan sayısı</small><b>{len(entry['members'])}</b></div><div><small>Dağılım</small><b>{esc(each)}</b></div></div>
      <p class="cp-finance-group-note">Bu toplam aşağıdaki hayvanlara ait giderlerden oluşur. Her hayvanın payı kendi maliyetinde izlenir.</p>
      <div class="cp-finance-member-head"><h2>Hayvanlara dağılım</h2><span data-finance-member-count>{len(entry['members'])} hayvan</span></div>
      <label class="cp-finance-member-search">Hayvan ara<input type="search" data-finance-member-search placeholder="Küpe, ad veya padok ara" autocomplete="off"></label>
      <div class="cp-finance-member-list">{cards}</div><p class="cp-finance-members-empty" data-finance-members-empty hidden>Aramana uygun hayvan bulunamadı.</p>
      </section><script src="/app-assets/finance-groups.js?v={ASSET_VERSION}" defer></script>'''
    return body, back


def install(ns):
    app = ns['App']
    original_get = app.do_GET
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/finance/health-group':
            allowed, _, message = ns['license_status']()
            if not allowed:
                return self.redirect('/license', message)
            if not self.require():
                return
            body, back = detail(ns, self.path)
            if body is None:
                return self.redirect(back, 'Bu sağlık işlemi güncellenmiş olabilir. Finans listesini yeniden açın.')
            return self.send_html(ns['page']('Toplu Sağlık Gideri', body, path, self.user()['username']))
        if path == '/finance':
            token = REQUEST_URL.set(self.path)
            try:
                return original_get(self)
            finally:
                REQUEST_URL.reset(token)
        return original_get(self)
    app.do_GET = do_GET
