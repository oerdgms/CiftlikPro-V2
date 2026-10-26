"""Mobile reference presentation, backed exclusively by Enterprise records.

No record handlers or database migrations live in this module. Desktop markup
and all existing forms remain available through mobile_ui.
"""
import html
from datetime import date, timedelta
from urllib.parse import parse_qs, urlencode, urlparse
from text_search import matches as search_matches
import dairy_management as dairy
import home_layout


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


PATHS = {
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'chevron': '<path d="m9 5 7 7-7 7"/>',
    'down': '<path d="m6 9 6 6 6-6"/>',
    'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    'filter': '<path d="M3 4h18l-7 8v7l-4 2v-9z"/>',
    'identity': '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8" cy="10" r="2"/><path d="M5 16c0-4 6-4 6 0M14 9h4M14 13h4M14 17h2"/>',
    'birth': '<path d="M3 10h18v11H3zM2 6h20v4H2zM12 6v15"/><path d="M12 6C2 7 6-3 12 6c6-9 10 1 0 0"/>',
    'shield': '<path d="m12 2 8 4v7c0 5-8 9-8 9s-8-4-8-9V6z"/><path d="M12 7v9M8 11h8"/>',
    'heart': '<path d="M12 21 3 12C-3 3 7-1 12 6 17-1 27 3 21 12z"/><path d="M5 12h4l2-4 3 8 2-4h3"/>',
    'camera': '<rect x="2" y="6" width="20" height="15" rx="3"/><path d="m8 6 2-3h4l2 3"/><circle cx="12" cy="13" r="4"/>',
    'edit': '<path d="m16 3 5 5-12 12-6 1 1-6zM13 6l5 5"/>',
    'history': '<path d="M3 11a9 9 0 1 1 3 8M3 4v7h7M12 7v6l4 2"/>',
    'exit': '<path d="M9 3H4v18h5M13 7l5 5-5 5M8 12h13"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="m7 12 3 3 7-7"/>',
    'flame': '<path d="M12 2c2 6-5 7-3 12 3 0 5-3 5-6 8 7 5 14-2 14C2 22 1 12 7 8c0 3 1 4 2 4-1-5 4-6 3-10z"/>',
    'more': '<circle cx="12" cy="5" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="12" cy="19" r="1"/>',
}


def glyph(name, base=None):
    if name not in PATHS and base:
        return base(name)
    return '<svg class="cp-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+PATHS.get(name, PATHS['identity'])+'</svg>'


def cow():
    # A code-native placeholder; a real animal photo always takes precedence.
    return '''<svg class="cp-ref-cow" viewBox="0 0 88 64" aria-hidden="true"><path d="M23 35c-7 3-10-3-12-8" fill="none" stroke="#603f2a" stroke-width="3" stroke-linecap="round"/><path d="M26 41v16h7l3-15m22-1 1 16h7V35" fill="#fff6e8" stroke="#875233" stroke-width="2"/><path d="M24 25c5-7 36-7 43 2l-2 19H26z" fill="#fff9ee" stroke="#875233" stroke-width="2"/><path d="M27 25c14-7 19 0 17 9-6 8-12 6-18 8zm25 0c7-3 14 0 15 7l-2 10c-9 2-15-3-13-17" fill="#a15a32"/><path d="m62 21 3-8 5 6m10 0 4-6 2 10" fill="#e6caa4" stroke="#875233" stroke-width="2"/><path d="m62 23-7-5 1 10 9 3m17-9 5-4v10l-6 3" fill="#a15a32" stroke="#875233" stroke-width="2"/><path d="M65 18h15l3 18-8 9-12-8z" fill="#a15a32" stroke="#74462c" stroke-width="2"/><path d="m70 19 5-1 1 18-6 1z" fill="#fff8ea"/><ellipse cx="73" cy="37" rx="10" ry="6" fill="#e6bca2"/><circle cx="68" cy="28" r="1.5" fill="#2d2828"/><circle cx="79" cy="28" r="1.5" fill="#2d2828"/><circle cx="69" cy="37" r="1" fill="#704c3c"/><circle cx="77" cy="37" r="1" fill="#704c3c"/></svg>'''


def photo(url, tag, zoom=True):
    if url:
        return f'<img src="{esc(url)}" alt="{esc(tag)} fotoğrafı" loading="lazy"{" data-photo-zoom" if zoom else ""}>'
    return cow()


def day(value):
    try:
        return date.fromisoformat(str(value or '')[:10])
    except ValueError:
        return None


def profile(ns, username):
    with ns['db']() as c:
        row = c.execute('select full_name from users where username=?', (username,)).fetchone()
    name = row['full_name'] if row and row['full_name'] else username
    ok, payload, message = ns['license_status']()
    payload = payload or {}
    expiry = payload.get('expires_on') or payload.get('expires') or payload.get('expires_at') or payload.get('expiry_date') or payload.get('expiry')
    expires = day(expiry)
    note = ('Bitiş: '+ns['fmt_date'](expires.isoformat())+' · '+str(max(0, (expires-date.today()).days))+' gün kaldı') if expires else ('Lisans etkin' if ok else (message or 'Lisans bilgilerini görüntüle'))
    return {'name':name, 'initials':''.join(x[0] for x in name.split()[:2]).upper(), 'license_ok':bool(ok), 'license_note':note}


def herd_records(ns, c):
    """One classification for mobile summary and list; no inactive/promoted duplicates."""
    adults = c.execute("""select a.*,coalesce(nullif(a.photo_url,''),(select '/uploads/'||filename from animal_photos p where p.animal_id=a.id order by id limit 1),'') list_photo,
        (select max(birth_date) from calves ca where ca.mother_id=a.id and birth_date<=date('now')) last_birth,
        (select max(measure_date) from milk m where m.animal_id=a.id and liters>0 and measure_date<=date('now')) last_milk,
        (select liters from milk m where m.animal_id=a.id and measure_date<=date('now') order by measure_date desc,id desc limit 1) milk_liters
        from animals a where coalesce(a.status,'Aktif')='Aktif' and not exists(select 1 from animal_losses l where l.animal_id=a.id)""").fetchall()
    calves = c.execute("""select ca.*,coalesce(nullif(ca.photo_url,''),(select '/uploads/'||filename from calf_photos p where p.calf_id=ca.id order by id limit 1),'') list_photo from calves ca
        where promoted_animal_id is null and coalesce(ca.status,'Aktif')='Aktif' and not exists(select 1 from animal_losses l where l.calf_id=ca.id)""").fetchall()
    pregnancies = ns['active_pregnancy_records'](c)
    heat_ids = {int(r['animal_id']) for r in c.execute('select animal_id,max(estrus_date) d from estrus_records where estrus_date<=? group by animal_id having d>=?', (date.today().isoformat(), (date.today()-timedelta(days=2)).isoformat()))}
    records = []
    dairy_rows = dairy.status_rows(c)
    for original, source in [(r,'animal') for r in adults]+[(r,'calf') for r in calves]:
        r = dict(original)
        female = r['gender']=='Dişi'
        state = dairy.current_status(c,r,dairy_rows) if source=='animal' and female else {'status':'unknown'}
        dry = state['status']=='dry'
        lactating = state['status']=='lactating'
        heifer = state['status']=='heifer'
        group = 'calf' if source=='calf' else 'dry' if dry else 'lactating' if lactating else 'heifer' if heifer else 'female' if female else 'male'
        pregnant = source=='animal' and r['id'] in pregnancies
        heat = source=='animal' and female and r['id'] in heat_ids and not pregnant
        r.update(source=source, kind='calf' if source=='calf' else 'female' if female else 'male', group=group, pregnant=pregnant, heat=heat, dairy_status=state['status'])
        r['labels'] = [('Buzağı','blue')] if source=='calf' else [('Kuru','orange')] if dry else [('Sağmal','green')] if lactating else [('Düve','purple')] if heifer else [(r['gender'] or 'Hayvan','blue')]
        if pregnant:r['labels'].append(('Gebe','green'))
        elif heat:r['labels'].append(('Kızgın','pink'))
        if lactating:r['labels'].append(('Laktasyonda','blue'))
        elif source=='animal' and female and not dry and not heifer:r['labels'].append((dairy.LABELS[state['status']],'blue'))
        records.append(r)
    return records


def badges(record):
    return ''.join(f'<span class="cp-ref-badge cp-tone-{tone}">{esc(label)}</span>' for label,tone in record['labels'])


def summary_cards(counts, records):
    cards = [('Genel',counts['total'],'','green','paddocks'),('Sağmal',sum(r['group']=='lactating' for r in records),'lactating','peach','cow'),('Kuru',sum(r['group']=='dry' for r in records),'dry','pink','cow'),('Buzağı',counts['calf'],'calf','mint','cow'),('Düve',sum(r['group']=='heifer' for r in records),'heifer','lavender','cow'),('Erkek',counts['male'],'male','rose','cow')]
    return [dict(key=key or 'all', label=label, count=count, tone=tone, kind=kind,
        url='/all-animals'+('?' + urlencode({'kind':key} if key in ('calf','male') else {'group':key}) if key else ''))
        for label,count,key,tone,kind in cards]


def home(ns, username, icon, task_url):
    with ns['db']() as c:
        counts = ns['dashboard_herd_counts'](c)
        records = herd_records(ns,c)
    config = home_layout.load(ns, username)
    card_map = {card['key']:card for card in summary_cards(counts,records)}
    cards = [card_map[key] for key in config['cards']]
    summary = ''
    for card in cards:
        label,count,tone,kind,url = (card[k] for k in ('label','count','tone','kind','url'))
        art = icon('paddocks') if kind!='cow' else cow()
        summary += f'<a class="cp-ref-stat cp-bg-{tone}" href="{esc(url)}"><span>{art}</span><small>{label}</small><b>{count}</b></a>'
    rows = ns['dashboard_export_tasks']('all')
    states = {key:sum(row['state']==key for row in rows) for key in ('today','upcoming','overdue')}
    tasks = ''
    for row in rows:
        kind = 'finance' if row.get('source')=='finance' else 'health'
        detail = row.get('detail') or ''
        if row.get('source')=='course' and row.get('target_count',0)>3 and row.get('target_tags'):
            tags = row['target_tags'].split(', ')
            detail = detail.removesuffix(' · '+row['target_tags'])+' · '+', '.join(tags[:2])+f" ve {row['target_count']-2} diğer hayvan"
        tasks += f'<a class="cp-task cp-{kind}" data-cp-state="{esc(row["state"])}" href="{esc(task_url(row))}"><span class="cp-ref-task-icon cp-tone-{ "orange" if kind=="finance" else "blue"}">{icon(kind)}</span><div><b>{esc(row["task"])}</b><span>{esc(row["subject"])}{(" · "+esc(detail)) if detail else ""}</span></div><small class="cp-ref-due cp-tone-{ "pink" if row["state"] in ("today","overdue") else "blue"}">{esc(row["status"])}</small></a>'
    tabs = ''.join(f'<button type="button" data-cp-task-filter="{key}">{label}<span>{count}</span></button>' for key,label,count in [('all','Tümü',len(rows)),('today','Bugün',states['today']),('upcoming','Yaklaşan',states['upcoming']),('overdue','Geciken',states['overdue'])])
    parts = {
        'business':f'<details class="cp-ref-business" data-cp-home-section="business"><summary><span class="cp-tone-blue">{glyph("identity")}</span><div><b>İşletme Bilgileri</b><small>Sürü, padok, yem, finans özeti</small></div>{glyph("down")}</summary><div class="cp-ref-business-links"><a href="/farm-profile">İşletme ayarları {glyph("chevron")}</a><a href="/paddocks">Padokları görüntüle {glyph("chevron")}</a><a href="/finance">Finans özeti {glyph("chevron")}</a></div></details>',
        'summary':f'<section data-cp-home-section="summary"><div class="cp-ref-heading"><h2>Sürü Özeti</h2><a href="/all-animals">Tümü ›</a></div><div class="cp-ref-summary">{summary}</div></section>',
        'tasks':f'<section class="cp-home-jobs" data-cp-home-section="tasks"><div class="cp-ref-heading cp-section-head"><h2>Yaklaşan İşlemler</h2><span class="cp-total" hidden>{len(rows)}</span><a href="/?app_view=tasks">Tümü ›</a></div><div class="cp-task-tabs cp-ref-task-tabs">{tabs}</div><div class="cp-ref-task-list cp-task-list">{tasks}</div><div class="cp-empty cp-filter-empty" hidden>Planlanan iş veya bekleyen ödeme yok.</div></section>'
    }
    ordered = config['sections']+[key for key in home_layout.SECTIONS if key not in config['sections']]
    content = ''.join(parts[key] if key in config['sections'] else parts[key].replace('data-cp-home-section="'+key+'"','data-cp-home-section="'+key+'" hidden',1) for key in ordered)
    return f'<section class="cp-ref cp-ref-home cp-home cp-mobile-only" data-task-limit="{config["task_limit"]}">{content}<div class="cp-ref-home-foot"><a href="/home-layout">Ana sayfayı düzenle</a><a href="/notifications">Bildirimler {icon("bell")}</a></div></section>'


def herd_selection(ns, request_url):
    q = parse_qs(urlparse(request_url).query)
    get = lambda key,default='':(q.get(key) or [default])[0]
    group, kind, term, pad = get('group'), get('kind','all'), get('q').strip(), get('paddock')
    if kind not in ('all','female','male','calf'):kind='all'
    if group not in ('','lactating','dry','heifer','pregnant','heat'):group=''
    with ns['db']() as c:records = herd_records(ns,c)
    paddocks = sorted({r['paddock'] for r in records if r.get('paddock')})
    def norm(text):return str(text).replace('I','ı').replace('İ','i').casefold()
    selected = [r for r in records if (kind=='all' or r['kind']==kind) and (not group or (r['pregnant'] if group=='pregnant' else r['heat'] if group=='heat' else r['group']==group)) and (not pad or r.get('paddock')==pad) and search_matches(term, *(r.get(k) for k in ('tag','nickname','breed','paddock','gender','notes')))]
    sort = get('sort','animal');reverse = get('dir','asc')=='desc'
    sort_field = {'animal':'tag','kind':'kind','breed':'breed','paddock':'paddock','age':'birth_date','status':'status'}.get(sort,'tag')
    def sort_value(r):
        return ns['animal_age_months'](r.get('birth_date')) if sort=='age' else norm(r.get(sort_field) or '')
    populated = [r for r in selected if sort_value(r) not in (None,'')]
    missing = [r for r in selected if sort_value(r) in (None,'')]
    selected = sorted(populated,key=sort_value,reverse=reverse)+missing
    try:size=int(get('per_page','15'))
    except ValueError:size=15
    if size not in (10,15,30):size=15
    pages = max(1,(len(selected)+size-1)//size)
    try:page=max(1,min(pages,int(get('page','1'))))
    except ValueError:page=1
    def link(**changes):
        args = {key:value[0] for key,value in q.items() if value and value[0]}
        args.update(changes)
        return '/all-animals?'+urlencode({k:v for k,v in args.items() if v not in ('',None)})
    return {'group':group, 'kind':kind, 'term':term, 'pad':pad, 'paddocks':paddocks, 'selected':selected, 'sort':sort, 'reverse':reverse, 'size':size, 'pages':pages, 'page':page, 'link':link}


def list_markup(ns, request_url, icon):
    view = herd_selection(ns, request_url)
    group, kind, term, pad, paddocks, selected, sort, reverse, size, pages, page, link = (view[k] for k in ('group', 'kind', 'term', 'pad', 'paddocks', 'selected', 'sort', 'reverse', 'size', 'pages', 'page', 'link'))
    chips = ''.join(f'<a data-ref-list-link class="{ "active" if group==key else ""}" href="{esc(link(group=key,kind="all",page=1))}">{label}</a>' for key,label in [('','Tümü'),('lactating','Sağmal'),('dry','Kuru'),('heifer','Düve'),('pregnant','Gebe'),('heat','Kızgın')])
    rows = ''
    for r in selected[(page-1)*size:page*size]:
        url = ('/animal?id=' if r['source']=='animal' else '/calf?id=')+str(r['id'])
        edit = ('/animal-edit?id=' if r['source']=='animal' else '/calf-edit?id=')+str(r['id'])
        notes = ' · '.join(x for x in [r.get('nickname'),ns['age_text'](r.get('birth_date')),r.get('breed')] if x)
        if r.get('last_milk') and r.get('milk_liters') is not None and r['group']=='lactating':
            notes += f' · Son süt {float(r["milk_liters"]):.1f} L'
        rows += f'''<article class="cp-ref-animal-row"><a class="cp-ref-animal-open" href="{url}"><span class="cp-ref-list-photo">{photo(r['list_photo'],r['tag'],False)}</span><div><b>{esc(r['tag'])}</b><div class="cp-ref-badges">{badges(r)}</div><small>{esc(notes)}</small><small>{esc(r.get('paddock') or 'Padoksuz')}</small></div>{glyph('chevron')}</a><a class="cp-ref-row-edit" href="{edit}" aria-label="{esc(r['tag'])} kaydını düzenle">{glyph('edit')}</a></article>'''
    if not rows:rows='<div class="cp-ref-empty">Aramana uygun hayvan bulunamadı.<a href="/all-animals">Filtreleri temizle</a></div>'
    options = '<option value="">Tüm padoklar</option>'+''.join(f'<option {"selected" if pad==p else ""} value="{esc(p)}">{esc(p)}</option>' for p in paddocks)
    kinds = ''.join(f'<option value="{key}" {"selected" if kind==key else ""}>{label}</option>' for key,label in [('all','Tüm hayvanlar'),('female','Dişi'),('male','Erkek'),('calf','Buzağı')])
    pager = (f'<a data-ref-list-link href="{esc(link(page=page-1))}">‹ Önceki</a>' if page>1 else '<span></span>')+f'<span>{page} / {pages}</span>'+(f'<a data-ref-list-link href="{esc(link(page=page+1))}">Sonraki ›</a>' if page<pages else '<span></span>')
    return f'''<section class="cp-ref cp-ref-list" aria-label="Hayvanlar"><form id="cpRefHerdForm" method="get" action="/all-animals"><label class="cp-ref-search">{glyph('search')}<input type="search" name="q" value="{esc(term)}" placeholder="Küpe no, ad, takip no ara…" aria-label="Hayvan ara" autocomplete="off"><button type="submit" aria-label="Ara">{glyph('chevron')}</button></label><input type="hidden" name="group" value="{esc(group)}"><div class="cp-ref-filter-row"><nav class="cp-ref-chips" aria-label="Hayvan durumu">{chips}</nav><button type="button" class="cp-ref-filter-button" aria-label="Diğer filtreler" aria-controls="cpRefFilters" aria-expanded="false">{glyph('filter')}</button></div><details id="cpRefFilters" class="cp-ref-filters"><summary>Diğer filtreler</summary><div><label>Hayvan türü<select id="cpRefKind" name="kind">{kinds}</select></label><label>Padok<select name="paddock">{options}</select></label><label>Sıralama<select name="sort">{''.join(f'<option value="{k}" {"selected" if sort==k else ""}>{label}</option>' for k,label in [('animal','Küpe no'),('age','Yaş'),('breed','Irk'),('paddock','Padok')])}</select></label><label>Sıra<select name="dir"><option value="asc" {"selected" if not reverse else ""}>Artan</option><option value="desc" {"selected" if reverse else ""}>Azalan</option></select></label><label>Göster<select name="per_page">{''.join(f'<option value="{n}" {"selected" if n==size else ""}>{n} kayıt</option>' for n in (10,15,30))}</select></label><button class="cp-ref-button" type="submit">Filtrele</button></div><a href="/archive/sold">Satılan</a><a href="/archive/slaughtered">Kesilen</a><a href="/archive/lost">Ölen / Kayıp</a><a href="/all-animals">Temizle</a></details></form><div class="cp-ref-list-status" role="status">{len(selected)} hayvan{(' · '+esc(pad)) if pad else ''}</div><div id="cpRefListResults">{rows}<nav class="cp-ref-pagination" aria-label="Sayfalar">{pager}</nav></div></section>'''


def keyvalues(items):
    return '<dl class="cp-ref-kv">'+''.join(f'<div><dt>{esc(label)}</dt><dd>{esc(value) if value not in (None,"") else "—"}</dd></div>' for label,value in items)+'</dl>'


def accordion(name,title,body,icon,opened=False):
    return f'<details class="cp-ref-accordion" data-ref-section="{name}" {"open" if opened else ""}><summary><span class="cp-tone-{ "pink" if name in ("health","reproduction") else "orange" if name=="finance" else "blue"}">{icon}</span><b>{esc(title)}</b>{glyph("down")}</summary><div class="cp-ref-accordion-body">{body}</div></details>'


def detail_markup(ns, request_url, icon):
    parsed = urlparse(request_url);source = 'calf' if parsed.path=='/calf' else 'animal'
    raw_id = (parse_qs(parsed.query).get('id') or [''])[0]
    if not raw_id.isdigit():return ''
    sid = int(raw_id);table = 'calves' if source=='calf' else 'animals';column = 'calf_id' if source=='calf' else 'animal_id'
    with ns['db']() as c:
        original = c.execute(f'select * from {table} where id=?',(sid,)).fetchone()
        if not original:return ''
        a = dict(original)
        pregnant = ns['current_pregnancy_record'](c,sid) if source=='animal' and a['gender']=='Dişi' else None
        milk = ns['dairy_lactation_summary'](c,sid) if source=='animal' and a['gender']=='Dişi' else None
        financial = ns['animal_financial_summary'](c,original,source)
        feed = ns['animal_current_feed_context'](original,c)
        mother = c.execute('select tag from animals where id=?',(a.get('mother_id'),)).fetchone()
        pad = c.execute('select * from paddocks where id=?',(a.get('paddock_id'),)).fetchone()
        moves = c.execute('select ph.*,p.name target_name from paddock_history ph left join paddocks p on p.id=ph.to_paddock_id where animal_source=? and animal_id=? order by moved_at desc,id desc',(source,sid)).fetchall()
        health = c.execute(f'select * from health where {column}=? order by applied_date desc,id desc',(sid,)).fetchall()
        pending = c.execute(f"select t.*,hc.product,hc.kind from health_tasks t join health_courses hc on hc.id=t.course_id where t.{column}=? and t.status='Bekliyor' and coalesce(hc.active,1)=1 order by t.planned_date,t.id",(sid,)).fetchall()
        treatments = c.execute(f"select count(*) from treatments where {column}=? and status='Aktif' and start_date<=? and (coalesce(end_date,'')='' or end_date>=?)",(sid,date.today().isoformat(),date.today().isoformat())).fetchone()[0]
        ins = c.execute('select * from inseminations where animal_id=? order by insemination_date desc,id desc',(sid,)).fetchall() if source=='animal' else []
        estrus = c.execute('select * from estrus_records where animal_id=? order by estrus_date desc,id desc',(sid,)).fetchall() if source=='animal' else []
        cycle = ns['estrus_cycle_profile'](c,sid) if source=='animal' and a['gender']=='Dişi' else {}
        photos = c.execute(f'select * from {"calf_photos" if source=="calf" else "animal_photos"} where {column}=? order by created_at desc,id desc',(sid,)).fetchall()
        weight = c.execute(f'select * from {"calf_weights" if source=="calf" else "weights"} where {column}=? order by measure_date desc,id desc limit 1',(sid,)).fetchone()
        loss = c.execute(f'select id from animal_losses where {column}=?',(sid,)).fetchone()
        dairy_state = dairy.current_status(c,a) if source=='animal' and a['gender']=='Dişi' else None
        dairy_history = c.execute('select * from animal_dairy_status_history where animal_id=? order by id desc limit 20',(sid,)).fetchall() if dairy_state else []
    active = a.get('status','Aktif')=='Aktif' and not loss and not a.get('promoted_animal_id')
    fmt = ns['fmt_date'];money=ns['money'];due = (pregnant['due_date'] or '') if pregnant else ''
    start = day(pregnant['insemination_date']) if pregnant else None
    gestation = f'{max(0,(date.today()-start).days)/30.4:.1f} ay' if start else '—'
    life_type = 'Buzağı' if source=='calf' else 'Sağmal' if dairy_state and dairy_state['status']=='lactating' else dairy_state['label'] if dairy_state else 'Erkek'
    route = '/calf' if source=='calf' else '/animal';edit=('/calf-edit' if source=='calf' else '/animal-edit')+'?id='+str(sid)
    purl='/paddocks'+('?selected='+str(a['paddock_id']) if a.get('paddock_id') else '')
    pic = a.get('photo_url') or ('/uploads/'+photos[0]['filename'] if photos else '')
    identity = keyvalues([('Küpe No',a['tag']),('Adı / Takip No',a.get('nickname')),('Doğum Tarihi',fmt(a.get('birth_date'))),('Yaşı',ns['age_text'](a.get('birth_date'))),('Irk',a.get('breed')),('Hayvan Tipi',life_type),('Anne Küpe No',mother['tag'] if mother else ''),('Baba Küpe No',a.get('father_tag')),('Cinsiyet',a['gender']),('Durum',a.get('status') or 'Aktif')])
    identity += f'<a class="cp-ref-bar" href="{edit}">Temel bilgileri düzenle {glyph("edit")}</a>'
    dairy_info = ''
    if dairy_state:
        dairy_info = keyvalues([('Laktasyon Durumu',dairy_state['label']),('Laktasyon Başlangıcı',fmt(dairy_state.get('lactation_start'))),('Laktasyon Sırası',dairy_state.get('lactation_number'))])
        if active:dairy_info += f'<a class="cp-ref-bar" href="/dairy-status?animal={sid}">Laktasyon durumunu düzenle {glyph("edit")}</a>'
        identity += dairy_info
    reproduction = keyvalues([('Gebelik Durumu','Gebe' if pregnant else 'Aktif gebelik yok'),('Gebelik Yaşı',gestation),('Tohumlama Tarihi',fmt(pregnant['insemination_date']) if pregnant else ''),('Beklenen Doğum',fmt(due)),('Son Kızgınlık',fmt(estrus[0]['estrus_date']) if estrus else ''),('Kızgınlık Periyodu',str(cycle.get('cycle_days'))+' gün' if cycle.get('cycle_days') else '')])
    if source=='animal':
        reproduction += '<div class="cp-ref-subhead"><b>Tohumlama Kayıtları</b><a href="/inseminations?animal='+str(sid)+'">+ Ekle</a></div><div class="cp-ref-rows">'
        for r in ins[:5]:
            reproduction += f'<a href="/inseminations?animal={sid}"><span>{esc(fmt(r["insemination_date"]))}</span><span>{r["attempt"]}. deneme</span><span class="cp-ref-badge cp-tone-{ "green" if ns["is_pregnant_value"](r["pregnancy_result"]) else "pink"}">{esc(r["pregnancy_result"])}</span></a>'
        reproduction += ('<p class="cp-ref-note">Henüz tohumlama kaydı yok.</p>' if not ins else '')+'</div>'
        reproduction += f'<a class="cp-ref-bar" href="/reproduction-center?animal={sid}">Tüm üreme bilgilerini gör ›</a><div data-ref-legacy="reproduction"></div>'
    hstats = f'<div class="cp-ref-health-stats"><div class="cp-tone-green">{glyph("shield")}<small>Yaklaşan Aşı</small><b>{sum(r["kind"]=="Aşı" for r in pending)}</b></div><div class="cp-tone-blue">{glyph("shield")}<small>Aktif Tedavi</small><b>{treatments}</b></div><div class="cp-tone-orange">{glyph("shield")}<small>Geçmiş Kayıt</small><b>{len(health)}</b></div></div>'
    hrows = '<div class="cp-ref-rows">'
    for r in pending[:5]:
        hrows += f'<a href="/health?{esc(urlencode({"search":a["tag"],"plan":r["course_id"],"filter":"all"}))}"><span class="cp-tone-blue">{icon("health")}</span><div><b>{esc(r["product"])}</b><small>{esc(fmt(r["planned_date"]))} · {r["dose_no"]}. doz</small></div><span class="cp-ref-badge cp-tone-orange">{ "Gecikti" if str(r["planned_date"])<date.today().isoformat() else "Bugün" if str(r["planned_date"])==date.today().isoformat() else "Planlandı"}</span></a>'
    for r in health[:3]:
        hrows += f'<div><span class="cp-tone-blue">{icon("health")}</span><div><b>{esc(r["product"] or r["kind"])}</b><small>{esc(fmt(r["applied_date"]))}</small></div><span class="cp-ref-badge cp-tone-green">Yapıldı</span></div>'
    hrows += ('<p class="cp-ref-note">Sağlık kaydı veya planı bulunmuyor.</p>' if not pending and not health else '')+'</div>'
    hrows += f'<a class="cp-ref-bar" href="/health?{esc(urlencode({"search":a["tag"]}))}">Tüm sağlık kayıtlarını gör ›</a><div data-ref-legacy="health"></div>'
    ration = keyvalues([('Aktif Rasyon',feed.get('ration_name') or 'Atanmadı'),('Günlük Yem Maliyeti',money(feed['feed_cost'])),('Ek Yem Maliyeti',money(feed.get('extra_feed_cost',0))),('Atama Başlangıcı',fmt(feed.get('start_date')))])+f'<a class="cp-ref-bar" href="{purl}">Rasyon detayını aç ›</a>'
    since = str(moves[0]['moved_at'])[:10] if moves else a.get('entry_date') or a.get('purchase_date')
    paddock = keyvalues([('Mevcut Padok',pad['name'] if pad else a.get('paddock')),('Padokta Süre',str(max(0,(date.today()-day(since)).days))+' gün' if day(since) else ''),('Son Taşıma',fmt(since))])+f'<a class="cp-ref-bar" href="{purl}">Padok bilgilerini gör ›</a>'
    finance = '<div class="cp-ref-money-grid">'+keyvalues([('Gelir',money(financial['income'])),('Gider',money(financial['expense']))])+f'<div class="cp-ref-net {"negative" if financial["net_profit"]<0 else ""}"><span>Net</span><b>{esc(money(financial["net_profit"]))}</b></div>'+keyvalues([('Günlük Maliyet',money(financial['daily'])),('Toplam Maliyet',money(financial['total_cost']))])+'</div><p class="cp-ref-note">Net = gelir − gider − rasyon ve bakım maliyeti.</p><div data-ref-legacy="finance"></div>'
    frows = '<div class="cp-ref-subhead"><b>İşlem Geçmişi</b></div><div class="cp-ref-rows">'
    for r in financial['finance_rows'][:5]:
        frows+=f'<a href="/finance/edit?id={r["id"]}"><span>{esc(fmt(r["tx_date"]))}</span><span>{esc(r["category"])}</span><b>{esc(money(r["amount"]))}</b></a>'
    frows+=('<p class="cp-ref-note">Bağlı finans kaydı yok.</p>' if not financial['finance_rows'] else '')+'</div>'
    gallery='<div class="cp-ref-gallery">'+''.join(f'<figure><img src="/uploads/{esc(r["filename"])}" alt="{esc(r["caption"] or a["tag"])}" loading="lazy" data-photo-zoom data-photo-caption="{esc(r["caption"] or a["tag"])}"><figcaption>{esc(r["caption"])}</figcaption></figure>' for r in photos)+f'<button type="button" data-ref-photo-add>{icon("plus")}<span>Fotoğraf Ekle</span></button></div><div data-ref-upload="{source}"></div>'
    events=[]
    events += [(r['effective_date'],'Laktasyon: '+dairy.LABELS[r['status']],r['notes'] or 'Manuel durum kaydı','green') for r in dairy_history]
    if pregnant:events.append((pregnant['insemination_date'],'Gebe',fmt(due)+' tahmini doğum','green'))
    events += [(r['insemination_date'],'Tohumlama',r['pregnancy_result'] or 'Kontrol bekleniyor','blue') for r in ins]
    events += [(r['estrus_date'],'Kızgınlık',r['notes'] or 'Kızgınlık kaydı','orange') for r in estrus[:6]]
    events += [(r['applied_date'],r['kind'],r['product'] or 'Sağlık kaydı','green') for r in health[:6]]
    events += [(r['moved_at'],'Padok Değişimi',r['target_name'] or 'Padoksuz','blue') for r in moves[:5]]
    if a.get('birth_date'):events.append((a['birth_date'],'Doğum',a['tag'],'orange'))
    if a.get('entry_date') or a.get('purchase_date'):events.append((a.get('entry_date') or a['purchase_date'],'İşletmeye Giriş',a.get('arrival_source') or 'Giriş kaydı','blue'))
    events.sort(key=lambda e:str(e[0] or ''),reverse=True)
    def timeline(limit):
        return '<ol class="cp-ref-timeline">'+''.join(f'<li class="cp-tone-{tone}"><span>+</span><div><b>{esc(label)}</b><time>{esc(fmt(str(stamp)[:10]))}</time><small>{esc(note)}</small></div></li>' for stamp,label,note,tone in events[:limit])+'</ol>'
    quick=[('shield','Durum Ekle','state','blue'),('birth','Doğum Ekle','birth','pink'),('health','Sağlık Kaydı','health','red'),('paddocks','Padok Ata','paddock','purple'),('milk','Süt / Kilo','growth','green'),('ration','Rasyon','ration','blue'),('camera','Fotoğraf Ekle','photos','blue'),('edit','Düzenle','edit','orange')]
    if a['gender']!='Dişi' or source=='calf':
        quick[1]=('history','Geçmiş','history','pink')
        quick[4]=('reports','Tartım Ekle','growth','green')
    actions=''
    for kind,label,action,tone in quick:
        url = edit if action=='edit' else '/animal-events?'+urlencode({'source':source,'id':sid,'event':'birth'}) if action=='birth' else '/paddocks?'+urlencode({'app_action':'move','subject':source+':'+str(sid)}) if action=='paddock' else '/health?'+urlencode({'app_action':'add','subject':source+':'+str(sid),'search':a['tag']}) if action=='health' else ''
        tag='a' if url else 'button';attrs=f'href="{esc(url)}"'+(' data-cp-state-url aria-haspopup="dialog"' if action=='birth' else '') if url else f'type="button" data-ref-action="{action}"'
        if not active and action in ('state','birth','paddock','health'):continue
        actions+=f'<{tag} {attrs}><span class="cp-ref-action-icon cp-tone-{tone}">{glyph(kind,icon)}</span><small>{label}</small></{tag}>'
    accordions=accordion('identity','Temel Kimlik Bilgileri',identity,glyph('identity'),True)
    if source=='animal' and a['gender']=='Dişi':
        if active:
            reproduction+=f'<a class="cp-ref-bar" href="/synchronization?new=1&amp;animal={sid}">↻ Senkronizasyon Tanımla ›</a>'
        accordions+=accordion('reproduction','Üreme Bilgileri',reproduction,glyph('heart'))
    accordions+=accordion('health','Sağlık Bilgileri',hstats+hrows,glyph('heart'))
    accordions+=accordion('ration','Rasyon & Beslenme',ration,icon('feeds'))+accordion('paddock','Padok Bilgileri',paddock,icon('paddocks'))
    accordions+=accordion('growth','Süt & Kilo Bilgileri' if milk else 'Kilo & Gelişim',dairy_info+keyvalues([('Son Canlı Ağırlık',str(weight['weight'])+' kg' if weight else ''),('Son Tartım',fmt(weight['measure_date']) if weight else '')])+ '<div data-ref-legacy="growth"></div>',icon('reports'))
    accordions+=accordion('finance','Finansal Bilgiler',finance+frows,icon('finance'))+accordion('photos','Fotoğraflar',gallery,glyph('camera'))
    accordions+=accordion('history','Hayvan Yaşam Döngüsü',timeline(100)+'<div data-ref-legacy="history"></div>',glyph('history'))
    delete_form = f'''<details class="cp-ref-delete"><summary>Kaydı Sil</summary><p class="cp-ref-note">Hayvan ve bağlı kayıtları kalıcı olarak silinir.</p><form method="post" action="/{source}-delete" onsubmit="return confirm('Bu hayvan ve bağlı kayıtları kalıcı olarak silinsin mi?')"><input type="hidden" name="id" value="{sid}"><button type="submit" class="btn red">Hayvan Kaydını Sil</button></form></details>'''
    accordions+=accordion('operations','Satış / Zayiat','<div data-ref-legacy="operations"></div>'+delete_form,icon('finance'))
    tabs=[('general','Genel')]+([('reproduction','Üreme')] if source=='animal' and a['gender']=='Dişi' else [])+[('health','Sağlık'),('ration','Rasyon'),('growth','Süt / Kilo' if milk else 'Kilo'),('finance','Finans'),('photos','Fotoğraflar'),('history','Geçmiş')]
    tabhtml=''.join(f'<button type="button" role="tab" data-ref-tab="{key}" aria-selected="{str(key=="general").lower()}" class="{"active" if key=="general" else ""}">{label}</button>' for key,label in tabs)
    return f'''<section class="cp-ref cp-ref-detail" data-ref-source="{source}" data-ref-id="{sid}"><div class="cp-ref-overview"><header class="cp-ref-profile"><span class="cp-ref-profile-photo">{photo(pic,a['tag'])}</span><div><h1>{esc(a['tag'])}</h1><p>{esc(ns['age_text'](a.get('birth_date')))} · {esc(a['gender'])} · {esc(a.get('breed') or 'Irk belirtilmedi')}</p><div class="cp-ref-badges"><span class="cp-ref-badge cp-tone-pink">{esc(life_type)}</span><span class="cp-ref-badge cp-tone-blue">{esc(a.get('status') or 'Aktif')}</span>{'<span class="cp-ref-badge cp-tone-green">Gebe</span>' if pregnant else ''}</div></div></header><div class="cp-ref-vitals"><div><small>{'Son Süt' if milk else 'Son Kilo'}</small><b>{str(round(milk['daily'][max(milk['daily'])],1))+' L' if milk and milk['daily'] else '—' if milk else str(weight['weight'])+' kg' if weight else '—'}</b></div><div><small>Gebelik D.</small><b>{'Gebe' if pregnant else '—'}</b></div><div><small>{'Sağım Günü' if milk else 'Yaş'}</small><b>{str(dairy_state['dim'])+' gün' if milk and dairy_state and dairy_state['dim'] is not None else '—' if milk else esc(ns['age_text'](a.get('birth_date')))}</b></div></div><div class="cp-ref-heading"><h2>Hızlı İşlemler</h2></div><div class="cp-ref-actions">{actions}</div><section class="cp-ref-life"><div class="cp-ref-heading"><h2>Hayvan Yaşam Döngüsü</h2></div>{timeline(3)}<button type="button" class="cp-ref-bar" data-ref-action="history">Tüm yaşam döngüsünü gör ›</button></section></div><nav class="cp-ref-detail-tabs" role="tablist" aria-label="Hayvan bilgileri">{tabhtml}</nav><div class="cp-ref-detail-sections">{accordions}</div></section>'''
