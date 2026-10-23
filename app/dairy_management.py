"""Explicit dairy status, independent of milk-entry frequency and calving estimates."""
import html
from datetime import date, datetime
from urllib.parse import parse_qs, urlencode, urlparse


LABELS = {'unknown':'Belirtilmedi', 'lactating':'Laktasyonda (Sağmal)',
          'dry':'Kuru', 'heifer':'Düve', 'not_lactating':'Laktasyonda değil'}


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def init_schema(c):
    c.execute("""create table if not exists animal_dairy_status (
        animal_id integer primary key references animals(id) on delete cascade,
        status text not null check(status in ('unknown','lactating','dry','heifer','not_lactating')),
        effective_date text not null, lactation_start text, lactation_number integer,
        notes text not null default '', updated_at text not null, updated_by text not null)""")
    c.execute("""create table if not exists animal_dairy_status_history (
        id integer primary key autoincrement, animal_id integer not null references animals(id) on delete cascade,
        old_status text not null, status text not null, effective_date text not null,
        lactation_start text, lactation_number integer, notes text not null default '',
        updated_at text not null, updated_by text not null)""")
    c.execute('create index if not exists idx_dairy_history_animal on animal_dairy_status_history(animal_id,id)')
    # Core connections may have foreign_keys disabled; never leave orphaned status data.
    c.execute('''create trigger if not exists delete_animal_dairy_status after delete on animals begin
        delete from animal_dairy_status where animal_id=old.id;
        delete from animal_dairy_status_history where animal_id=old.id;
        end''')


def status_rows(c):
    return {r['animal_id']:dict(r) for r in c.execute('select * from animal_dairy_status')}


def current_status(c, animal, rows=None):
    animal = dict(animal)
    row = (rows if rows is not None else status_rows(c)).get(animal['id'])
    result = dict(row) if row else {'status':'unknown', 'lactation_start':None,
        'lactation_number':None, 'effective_date':None, 'notes':''}
    dry_since = animal.get('dry_since') or ''
    if animal.get('gender') != 'Dişi':
        result.update(status='unknown', lactation_start=None, lactation_number=None)
    elif dry_since and dry_since <= date.today().isoformat():
        # Honor the existing explicit reproductive dry-off operation as well.
        result.update(status='dry', effective_date=dry_since, lactation_start=None, lactation_number=None)
    elif result['status'] == 'dry':
        # Birth/dry-off cancellation cleared the core flag: request an explicit new status.
        result.update(status='unknown', lactation_start=None, lactation_number=None)
    result['label'] = LABELS[result['status']]
    result['dim'] = ((date.today()-date.fromisoformat(result['lactation_start'])).days
        if result['status']=='lactating' and result.get('lactation_start') else None)
    return result


def parse_day(value, label, required=False):
    if not value and not required:
        return None
    try:
        stamp = date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(label+' geçerli bir tarih olmalıdır.') from None
    if stamp > date.today():
        raise ValueError(label+' gelecekte olamaz.')
    return stamp.isoformat()


def save_status(c, ids, status, effective_date, lactation_start='', lactation_number='', notes='', username='admin', bulk=False):
    """Validate the entire selection first, then commit status and history atomically."""
    if status not in LABELS:
        raise ValueError('Geçerli bir laktasyon durumu seçin.')
    if not isinstance(ids, (list,tuple)) or not 1 <= len(ids) <= 500:
        raise ValueError('1–500 hayvan seçin.')
    if any(isinstance(aid,bool) or not str(aid).isdigit() or int(aid)<=0 for aid in ids):
        raise ValueError('Hayvan seçimi geçersiz.')
    ids = list(dict.fromkeys(int(aid) for aid in ids))
    effective_date = parse_day(effective_date, 'Durum tarihi', True)
    start = parse_day(lactation_start, 'Laktasyon başlangıcı') if status=='lactating' else None
    if start and start > effective_date:
        raise ValueError('Laktasyon başlangıcı durum tarihinden sonra olamaz.')
    number = None
    if status=='lactating' and lactation_number:
        if not str(lactation_number).isdigit() or not 1 <= int(lactation_number) <= 99:
            raise ValueError('Laktasyon sırası 1–99 arasında tam sayı olmalıdır.')
        number = int(lactation_number)
    notes = str(notes or '').strip()
    if len(notes)>1000:
        raise ValueError('Not en fazla 1000 karakter olabilir.')
    c.execute('BEGIN IMMEDIATE')
    placeholders = ','.join('?' for _ in ids)
    animals = c.execute(f"""select * from animals a where a.id in ({placeholders})
        and a.gender='Dişi' and coalesce(a.status,'Aktif')='Aktif'
        and not exists(select 1 from animal_losses l where l.animal_id=a.id)""",ids).fetchall()
    if len(animals)!=len(ids):
        raise ValueError('Yalnız aktif yetişkin dişi hayvanlar seçilebilir. Hiçbir kayıt değişmedi.')
    rows = status_rows(c)
    stamp = datetime.now().isoformat(timespec='microseconds')
    for animal in animals:
        previous = current_status(c,animal,rows)
        chosen_start, chosen_number = start, number
        # A blank bulk field preserves a known start/number within the same current lactation.
        if bulk and status=='lactating' and previous['status']=='lactating':
            chosen_start = chosen_start or previous.get('lactation_start')
            chosen_number = chosen_number or previous.get('lactation_number')
        if chosen_start and chosen_start > effective_date:
            raise ValueError('Laktasyon başlangıcı durum tarihinden sonra olamaz. Hiçbir kayıt değişmedi.')
        if chosen_start and animal['birth_date'] and chosen_start < animal['birth_date']:
            raise ValueError('Laktasyon başlangıcı hayvanın doğum tarihinden önce olamaz. Hiçbir kayıt değişmedi.')
        values = (animal['id'],status,effective_date,chosen_start,chosen_number,notes,stamp,username)
        c.execute('''insert into animal_dairy_status(animal_id,status,effective_date,lactation_start,lactation_number,notes,updated_at,updated_by)
            values(?,?,?,?,?,?,?,?) on conflict(animal_id) do update set status=excluded.status,
            effective_date=excluded.effective_date,lactation_start=excluded.lactation_start,
            lactation_number=excluded.lactation_number,notes=excluded.notes,
            updated_at=excluded.updated_at,updated_by=excluded.updated_by''',values)
        c.execute('''insert into animal_dairy_status_history(animal_id,old_status,status,effective_date,lactation_start,lactation_number,notes,updated_at,updated_by)
            values(?,?,?,?,?,?,?,?,?)''',(animal['id'],previous['status'],*values[1:]))
        c.execute('update animals set dry_since=? where id=?',(effective_date if status=='dry' else None,animal['id']))
    return len(ids)


def page_markup(ns, query):
    raw_id = (query.get('animal') or [''])[0]
    single = bool(raw_id)
    if single and (not raw_id.isdigit() or int(raw_id)<=0):
        raise ValueError('Hayvan bulunamadı.')
    with ns['db']() as c:
        animals = c.execute("""select a.*,(select max(measure_date) from milk m where m.animal_id=a.id
            and liters>0 and measure_date<=date('now')) last_milk from animals a
            where gender='Dişi' and coalesce(status,'Aktif')='Aktif'
            and not exists(select 1 from animal_losses l where l.animal_id=a.id) order by tag""").fetchall()
        rows = status_rows(c)
        if single:
            animals = [a for a in animals if a['id']==int(raw_id)]
            if not animals:raise ValueError('Yalnız aktif yetişkin dişi hayvanların laktasyon durumu düzenlenebilir.')
        history = c.execute('select * from animal_dairy_status_history where animal_id=? order by id desc limit 12',(int(raw_id),)).fetchall() if single else []
        selected = current_status(c,animals[0],rows) if single else {'status':'lactating'}
    status_options = ''.join(f'<option value="{key}" {"selected" if selected["status"]==key else ""}>{label}</option>' for key,label in LABELS.items())
    listing = ''
    for a in animals:
        state = current_status(None,a,rows)
        search = ' '.join(str(a[k] or '') for k in ('tag','nickname','paddock'))
        listing += f'''<label class="cp-dairy-animal" data-dairy-search="{esc(search)}"><input type="checkbox" name="animal_id" value="{a['id']}" {"checked" if single else ""}><span><b>{esc(a['tag'])}</b><small>{esc(a['nickname'] or a['paddock'] or 'Padoksuz')} · {esc(state['label'])}</small><small>Son süt: {esc(ns['fmt_date'](a['last_milk'])) if a['last_milk'] else 'Kayıt yok'}</small></span></label>'''
    filters = '' if single else '''<label class="cp-dairy-search">Hayvan ara<input type="search" data-dairy-search-input placeholder="Küpe no, ad veya padok"></label><div class="cp-dairy-select-tools"><button type="button" class="btn alt" data-dairy-select>Görünenleri seç</button><button type="button" class="btn alt" data-dairy-clear>Seçimi temizle</button><b data-dairy-count role="status">0 hayvan seçili</b></div>'''
    return_to = '/animal?id='+raw_id+'#growth' if single else '/all-animals?group=lactating'
    history_html = ''.join(f'<li><b>{esc(LABELS[r["status"]])}</b><span>{esc(ns["fmt_date"](r["effective_date"]))} · {esc(r["updated_by"])}</span></li>' for r in history)
    return f'''<section class="cp-dairy-workspace"><header><div><span class="cp-dairy-eyebrow">SÜT & LAKTASYON</span><h1>Laktasyon Durumu</h1></div><a href="{esc(return_to)}">Listeye / hayvana dön ›</a></header><p>Sağımdaki hayvanları kendin belirle. Süt girişi veya doğum kaydı bu seçimi otomatik değiştirmez.</p><form method="post" action="/dairy-status/save" data-dairy-form><input type="hidden" name="single" value="{raw_id if single else ''}"><div class="cp-dairy-layout"><section class="card"><h2>{esc(animals[0]['tag']) if single else 'Hayvanları seç'}</h2>{filters}<div class="cp-dairy-animals">{listing or '<p>Aktif yetişkin dişi hayvan bulunamadı.</p>'}</div><p class="cp-dairy-no-results" hidden>Aramana uygun hayvan bulunamadı.</p></section><section class="card cp-dairy-editor"><h2>{'Durumu düzenle' if single else 'Seçililere uygulanacak durum'}</h2><label>Laktasyon durumu<select name="status" required>{status_options}</select></label><label>Durum tarihi<input type="date" name="effective_date" value="{date.today().isoformat()}" max="{date.today().isoformat()}" required></label><div data-dairy-lactation-fields><label>Laktasyon başlangıcı <small>İsteğe bağlı</small><input type="date" name="lactation_start" value="{esc(selected.get('lactation_start'))}" max="{date.today().isoformat()}"></label><label>Kaçıncı laktasyon? <small>İsteğe bağlı</small><input type="number" name="lactation_number" value="{esc(selected.get('lactation_number'))}" min="1" max="99" step="1" placeholder="Örn. 2"></label><p class="cp-dairy-hint">Başlangıç bilinmiyorsa boş bırak; sağım günü tahmin edilmez. {'Toplu işlemde boş bırakılan başlangıç ve sıra, mevcut laktasyondaki hayvanda korunur.' if not single else ''}</p></div><label>Not<textarea name="notes" maxlength="1000" rows="3">{esc(selected.get('notes'))}</textarea></label><p class="cp-dairy-hint" data-dairy-message>Seçtiğin hayvanların durumu güncellenecek.</p><button class="btn cp-dairy-save" type="submit" {'' if single else 'disabled'}>Kaydet</button><noscript><p>Toplu kayıt için tarayıcıda JavaScript etkin olmalıdır.</p></noscript></section></div></form>{'<section class="card"><h2>Durum geçmişi</h2><ul class="cp-dairy-history">'+history_html+'</ul></section>' if history else ''}</section><script src="/app-assets/dairy.js?v=2.0.33" defer></script>'''


def install(ns):
    original_init = ns['init_db']
    def init_db(*args, **kwargs):
        result = original_init(*args, **kwargs)
        with ns['db']() as c:init_schema(c)
        return result
    ns['init_db'] = init_db
    app = ns['App']
    original_get, original_post = app.do_GET, app.do_POST
    def authorized(handler):
        allowed, _, message = ns['license_status']()
        if not allowed:
            handler.redirect('/license',message)
            return False
        return bool(handler.require())
    def do_GET(self):
        if urlparse(self.path).path!='/dairy-status':return original_get(self)
        if not authorized(self):return
        query = parse_qs(urlparse(self.path).query)
        try:body = page_markup(ns,query)
        except ValueError as exc:return self.redirect('/all-animals',str(exc))
        return self.send_html(ns['page']('Laktasyon Durumu',body,'/dairy-status',self.user()['username'],(query.get('msg') or [''])[0]))
    def do_POST(self):
        if urlparse(self.path).path!='/dairy-status/save':return original_post(self)
        if not authorized(self):return
        try:size = int(self.headers.get('Content-Length','0') or 0)
        except ValueError:return self.redirect('/dairy-status','Gönderilen seçim geçersiz.')
        if not 0 < size <= 131072:return self.redirect('/dairy-status','Gönderilen seçim geçersiz.')
        form = parse_qs(self.rfile.read(size).decode('utf-8'),keep_blank_values=True)
        get = lambda key:(form.get(key) or [''])[0]
        single = get('single')
        return_to = '/animal?id='+single+'#growth' if single.isdigit() and int(single)>0 else '/all-animals?group=lactating'
        error_to = '/dairy-status'+('?' + urlencode({'animal':single}) if single.isdigit() else '')
        try:
            ids = form.get('animal_id') or []
            if single and (not single.isdigit() or ids!=[single]):raise ValueError('Hayvan seçimi geçersiz.')
            with ns['db']() as c:
                count = save_status(c,ids,get('status'),get('effective_date'),get('lactation_start'),get('lactation_number'),get('notes'),self.user()['username'],bulk=not bool(single))
        except (ValueError,TypeError) as exc:return self.redirect(error_to,str(exc))
        ns['audit'](self.user()['username'],'Manuel laktasyon durumu',f'{count} hayvan · {LABELS[get("status")]}',self.client_ip())
        return self.redirect(return_to,f'{count} hayvanın laktasyon durumu kaydedildi.')
    app.do_GET, app.do_POST = do_GET, do_POST
