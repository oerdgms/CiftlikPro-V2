"""App Edition presentation. All records still use Enterprise routes and forms."""
import html
import json
import re
import gzip
from pathlib import Path
from urllib.parse import urlparse, urlencode

BUILD = 'AppEdition2.0.8-DashboardPerformance'
ASSETS = Path(__file__).resolve().parent / 'mobile_assets'
MOBILE_VIEWPORT = 'width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover'

ICONS = {
    'home': '<path d="m3 10 9-7 9 7v10H3z"/><path d="M9 20v-7h6v7"/>',
    'animals': '<path d="m6 8-3-3v6l3 2M18 8l3-3v6l-3 2"/><path d="M6 6h12v10l-3 4H9l-3-4z"/><path d="M8 13h8v5H8z"/><path d="M9 9h.01M15 9h.01"/>',
    'jobs': '<path d="M9 5h6v3H9zM9 6H5v15h14V6h-4"/><path d="m8 15 3 3 5-6"/>',
    'paddocks': '<path d="M4 3v18M10 3v18M16 3v18M22 3v18M2 8h22M2 16h22"/>',
    'modules': '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
    'finance': '<ellipse cx="9" cy="5" rx="6" ry="3"/><path d="M3 5v6c0 4 12 4 12 0V5M3 11v6c0 4 12 4 12 0v-6"/><path d="M18 6h3v13h-3"/>',
    'feeds': '<path d="M6 21 18 3M9 16c-6 1-7-4-7-4 5-2 8 0 7 4M12 12c-5-1-5-5-5-5 5-1 7 1 5 5M16 8c-1-5 2-6 2-6 4 3 3 6-2 6M10 17c1-4 6-5 8-3-1 5-5 6-8 3M14 12c3-3 7-2 8 1-4 3-6 3-8-1"/>',
    'ration': '<path d="M12 3v17M3 20h18M5 5h14M5 5l-3 8h6zM19 5l-3 8h6z"/>',
    'health': '<path d="m16 3 5 5M14 5l5 5M12 7l5 5-8 8-5-5zM4 20l-2 2M10 10l3 3"/>',
    'reproduction': '<circle cx="12" cy="8" r="5"/><path d="M12 13v9M8 18h8"/>',
    'milk': '<path d="M9 2h6v5l3 4v10H6V11l3-4zM9 7h6M6 13h12"/>',
    'farm': '<path d="M12 21V9M12 14C3 15 3 5 3 5c8-1 10 3 9 9M12 10c0-8 9-8 9-8 1 7-3 10-9 8"/>',
    'reports': '<path d="M4 21V12h4v9M10 21V7h4v14M16 21V3h4v18M2 21h20"/>',
    'settings': '<path d="m9 3-1 3-3 1-2 4 2 2 1 4 4 1 2 3 3-2 4-1 1-4 2-3-2-3-3-1-1-3z"/><circle cx="12" cy="12" r="3"/>',
    'back': '<path d="m14 5-7 7 7 7M7 12h14"/>',
    'bell': '<path d="M5 17h14l-2-4V9a5 5 0 0 0-10 0v4zM10 20h4"/>',
    'plus': '<path d="M12 5v14M5 12h14"/>',
    'close': '<path d="m6 6 12 12M6 18 18 6"/>',
}


def icon(name):
    return '<svg class="cp-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + ICONS.get(name, ICONS['modules']) + '</svg>'


def esc(value):
    return html.escape(str(value or ''), quote=True)


def task_url(row):
    if row.get('source') == 'finance':
        return '/finance/edit?' + urlencode({'id': row['finance_id']}) + '#payment-status'
    if row.get('course_id'):
        return '/health?' + urlencode({'filter': row['state'], 'plan': row['course_id'], 'task': row.get('plan_ref', '')})
    return '/health?' + urlencode({'filter': row.get('state', 'all'), 'search': row.get('subject', '')})


def home_markup(ns, username):
    """The same Dashboard helpers supply counts and individual health/payment tasks."""
    with ns['db']() as connection:
        counts = ns['dashboard_herd_counts'](connection)
        pregnant = len(ns['active_pregnancy_records'](connection))
        paddocks = connection.execute('select count(*) from paddocks where active=1').fetchone()[0]
        account = connection.execute('select full_name from users where username=?', (username,)).fetchone()
    display = account['full_name'] if account and account['full_name'] else username
    rows = ns['dashboard_export_tasks']('all')
    states = {key: sum(row['state'] == key for row in rows) for key in ('today', 'upcoming', 'overdue')}
    now = ns['datetime'].now()
    greeting = 'Günaydın' if 5 <= now.hour < 12 else 'İyi günler' if 12 <= now.hour < 18 else 'İyi akşamlar' if 18 <= now.hour < 23 else 'İyi geceler'
    date_label = now.strftime('%d/%m/%Y')
    weekday = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar'][now.weekday()]
    metrics = [
        ('animals', '/all-animals', counts['total'], 'Aktif hayvan', 'green'),
        ('paddocks', '/paddocks', paddocks, 'Aktif padok', 'blue'),
        ('reproduction', '/reproduction-center?stage=pregnant', pregnant, 'Gebe', 'pink'),
        ('jobs', '/?app_view=tasks', states['today'], 'Bugünün işi', 'orange'),
    ]
    metric_html = ''.join(f'<a class="cp-stat cp-{color}" href="{url}"><span>{icon(kind)}</span><div><b>{value}</b><small>{label}</small></div></a>' for kind,url,value,label,color in metrics)
    task_html = ''
    for row in rows:
        kind = 'finance' if row['source'] == 'finance' else 'health'
        task_html += (
            f'<a class="cp-task cp-{kind}" data-cp-state="{esc(row["state"])}" href="{esc(task_url(row))}">'
            f'<span class="cp-task-icon">{icon(kind)}</span><div><b>{esc(row["subject"])}</b>'
            f'<span>{esc(row["task"])} · {esc(row.get("detail", ""))}</span></div>'
            f'<small><time>{esc(ns["fmt_date"](row["date"]))}</time><em class="cp-due cp-{esc(row["state"])}">{esc(row["status"])}</em></small></a>'
        )
    if not rows:
        task_html = '<div class="cp-empty">Planlanan iş veya bekleyen ödeme yok.</div>'
    tabs = ''.join(
        f'<button type="button" data-cp-task-filter="{key}" class="{"active" if key=="today" else ""}">{label}<span>{value}</span></button>'
        for key,label,value in [('today','Bugün',states['today']),('upcoming','Yaklaşan',states['upcoming']),('overdue','Geciken',states['overdue']),('all','Tümü',len(rows))]
    )
    return f'''<section class="cp-home cp-mobile-only">
    <a class="cp-welcome" href="/farm-profile"><span class="cp-sun">☀</span><div><b>{greeting}, {esc(display)}</b><span>{date_label} · {weekday}</span></div><span>›</span></a>
    <div class="cp-stats">{metric_html}</div>
    <section class="cp-home-jobs"><div class="cp-section-head"><h2>Bugünün işleri</h2><span class="cp-total">{states['today']}</span><a href="/?app_view=tasks">Tümü ›</a></div>
    <div class="cp-task-tabs">{tabs}</div><div class="cp-task-list">{task_html}</div><div class="cp-empty cp-filter-empty" hidden>Bu grupta bekleyen iş yok.</div></section>
    <div class="cp-shortcuts"><a href="/rations">{icon('ration')}<span>Rasyon</span></a><a href="/health">{icon('health')}<span>Sağlık</span></a><a href="/finance">{icon('finance')}<span>Finans</span></a><a href="/feeds">{icon('feeds')}<span>Yem & Stok</span></a></div>
    <a class="cp-business-more" href="/farm-profile#farm-settings">İşletme bilgileri ve ayarlar <span>›</span></a>
    </section>'''


def shell_markup(title, path, username):
    titles = {'/':'ÇiftlikPro Mobile','/all-animals':'Hayvanlar','/paddocks':'Padoklar','/finance':'Finans','/health':'Sağlık Merkezi','/rations':'Rasyonlar','/ration-workbench':'Rasyon Detayı','/reproduction-center':'Üreme Merkezi','/feeds':'Yem & Stok','/milk-center':'Süt Merkezi','/reports':'Raporlar','/farm-profile':'Ayarlar'}
    display_title = titles.get(path, title)
    back_url = '/' if path in titles else '/?app_view=modules'
    leading = f'<a class="cp-header-back" href="{back_url}" aria-label="Geri">{icon("back")}</a>' if path != '/' else '<span class="cp-leaf">'+icon('farm')+'</span>'
    header = f'<header class="cp-app-header"><div class="cp-header-title">{leading}<div><b id="cpScreenTitle">{esc(display_title)}</b><small id="cpScreenSubtitle">{esc(username) if path=="/" else "ÇiftlikPro Enterprise"}</small></div></div><a class="cp-notifications" href="/notifications" aria-label="Bugünün işleri ve bildirimler">{icon("bell")}<i id="cpNotificationDot" hidden></i></a></header>'
    links = [('home','/','Ana Sayfa'),('animals','/all-animals','Hayvanlar'),('jobs','/?app_view=tasks','İşler'),('paddocks','/paddocks','Padoklar'),('modules','/?app_view=modules','Modüller')]
    nav = '<nav class="cp-bottom-nav" aria-label="Mobil ana menü">' + ''.join(f'<a data-cp-nav="{key}" href="{url}">{icon(key)}<span>{label}</span></a>' for key,url,label in links) + '</nav>'
    quick = '<div class="cp-overlay" id="cpQuickOverlay" hidden><section class="cp-sheet" role="dialog" aria-modal="true" aria-labelledby="cpQuickTitle" tabindex="-1"><div class="cp-sheet-head"><h2 id="cpQuickTitle">Hızlı işlem</h2><button type="button" class="cp-icon-button" data-cp-close aria-label="Kapat">'+icon('close')+'</button></div><div class="cp-quick-grid">'
    actions = [('animals','/animal-add?entry=adult','Hayvan ekle'),('animals','/animal-add?entry=calf','Buzağı ekle'),('health','/health?app_action=add','Sağlık planı'),('finance','/finance?app_action=add','Finans kaydı'),('paddocks','/paddocks?app_action=move','Padok taşıma'),('ration','/rations?app_action=add','Rasyon ekle'),('milk','/milk-center','Süt kaydı')]
    quick += ''.join(f'<a data-cp-quick="{kind}" href="{url}">{icon(kind)}<span>{label}</span></a>' for kind,url,label in actions) + '</div></section></div>'
    fab = '<button type="button" class="cp-global-fab" id="cpGlobalAdd" aria-label="Yeni kayıt ve hızlı işlemler">'+icon('plus')+'</button>'
    return header + nav + fab + quick + '<div class="cp-network-status" role="status" hidden>Bağlantı yok. Kaydetmek için çiftlik sunucusuna bağlanın.</div>'


HEAD = '''<meta name="theme-color" content="#063e2b"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"><meta name="apple-mobile-web-app-title" content="ÇiftlikPro"><link rel="manifest" href="/app-manifest.json"><link rel="apple-touch-icon" href="/app-assets/icon-192.png"><link rel="icon" href="/app-assets/icon.svg" type="image/svg+xml"><link rel="stylesheet" href="/app-assets/mobile.css?v=2.0.8">'''


def enhance(document, title='', path='/', user='admin', login=False, extra=None):
    if 'id="cpAppConfig"' in document:
        return document
    document = document.replace('href="/#approaching-estrus"', 'href="/notifications"')
    viewport_pattern = re.compile(r'<meta\b(?=[^>]*\bname=(["\'])viewport\1)[^>]*>', re.I)
    viewport_tag = f'<meta name="viewport" content="{MOBILE_VIEWPORT}">'
    if viewport_pattern.search(document):
        document = viewport_pattern.sub(viewport_tag, document, count=1)
    else:
        document = document.replace('</head>', viewport_tag + '</head>', 1)
    config = json.dumps({'build':BUILD,'path':path,'title':title,'user':user,'login':login,**(extra or {})}, ensure_ascii=False).replace('<', '\\u003c')
    route = 'home' if path == '/' else re.sub('[^a-z0-9-]', '-', path.strip('/'))
    classes = f'cp-app cp-route-{route}{" cp-login" if login else ""}'
    def body_tag(match):
        attrs = match.group(1)
        current = re.search(r'\bclass=(["\'])(.*?)\1', attrs)
        if current:
            attrs = attrs[:current.start()] + 'class="' + esc(current.group(2)) + ' ' + classes + '"' + attrs[current.end():]
        else:
            attrs += ' class="' + classes + '"'
        return '<body' + attrs + '>'
    document = re.sub(r'<body([^>]*)>', body_tag, document, count=1)
    document = document.replace('</head>', HEAD + '</head>', 1)
    # The smart form calls this existing UI controller before the footer script
    # defines it. Hoist its exact definition; no record or pregnancy rule changes.
    if 'id="smartAnimalForm"' in document:
        controller = re.search(r'(function toggleEntryPregnancy\(\)\s*\{.*?\n\})', document, re.S)
        if controller:
            document = document.replace('</head>', '<script id="cpEarlyPregnancyUI">'+controller.group(1)+'</script></head>',1)
    extra = '' if login else shell_markup(title, path, user)
    extra += f'<script type="application/json" id="cpAppConfig">{config}</script><script src="/app-assets/mobile.js?v=2.0.8" defer></script>'
    return document.replace('</body>', extra + '</body>', 1)


def install(ns):
    # Decorate after all historical visual layers; never overwrite a record handler.
    original_page = ns['_page_before_app_edition']
    def page(title, body, path='/', user='admin', flash=''):
        extra = {}
        if 'data-animal-panel="history"' in body:
            subject = re.search(r'name="animal_id" value="(\d+)"', body)
            if subject:
                body = body.replace('data-animal-tab="history">↶ Geçmiş', 'data-animal-tab="operations">Satış / Zayiat')
                body = body.replace('data-animal-panel="history"', 'data-animal-panel="operations"')
                body = body.replace("showAnimalPanel('history');", "showAnimalPanel('operations');")
                body = body.replace('</nav>', '<button class="animal-card-tab" data-animal-tab="history">↶ Geçmiş</button></nav>', 1)
                history_panel = '<section class="animal-card-panel" data-animal-panel="history">'+animal_history_markup(ns, int(subject.group(1)))+'</section>'
                body = body.replace('<script>(function(){const tabs=[...document.querySelectorAll', history_panel+'<script>(function(){const tabs=[...document.querySelectorAll', 1)
        if path == '/':
            body = home_markup(ns, user) + body
        if path == '/rations':
            today = ns['date'].today().isoformat()
            with ns['db']() as c:
                meta = {str(r['id']): {'feed_count':r['feed_count'],'paddocks':[]} for r in c.execute('select r.id,(select count(*) from ration_items ri where ri.ration_id=r.id) feed_count from rations r where r.active=1')}
                for row in c.execute("""select pr.ration_id,p.name from paddock_rations pr join paddocks p on p.id=pr.paddock_id where pr.active=1 and p.active=1 and pr.start_date<=? and (pr.end_date is null or trim(pr.end_date)='' or pr.end_date>=?) order by p.name""",(today,today)):
                    item = meta.get(str(row['ration_id']))
                    if item is not None and row['name'] not in item['paddocks']:
                        item['paddocks'].append(row['name'])
            extra['ration_meta'] = meta
        return enhance(original_page(title, body, path, user, flash), title, path, user, extra=extra)
    ns['page'] = page
    ns['APP_EDITION_BUILD'] = BUILD
    app = ns['App']
    original_get = app.do_GET
    original_post = app.do_POST
    original_send_html = app.send_html
    def send_html(self, document, status=200, headers=None):
        path = urlparse(self.path).path
        if path == '/login' and 'class="login-shell"' in document:
            document = enhance(document, 'Giriş', path, '', login=True)
        match = re.search(r'(<script type="application/json" id="cpAppConfig">)(.*?)(</script>)',document,re.S)
        if match:
            config = json.loads(match.group(2))
            config['request_url'] = self.path
            payload = json.dumps(config,ensure_ascii=False).replace('<','\\u003c')
            document = document[:match.start(2)]+payload+document[match.end(2):]
        # Compress negotiated responses, including authenticated pages; no page cache.
        if accepts_gzip(self) and len(document) > 1024:
            send_response_bytes(self, gzip.compress(document.encode('utf-8'), compresslevel=5), 'text/html; charset=utf-8', status, [('Content-Encoding','gzip'),('Vary','Accept-Encoding'),('Cache-Control','no-store'),*(headers or [])])
        else:
            original_send_html(self, document, status, headers)
    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/notifications':
            allowed, _, message = ns['license_status']()
            if not allowed:
                return self.redirect('/license', message)
            if not self.require():
                return
            account = self.user()
            return self.send_html(ns['page']('Bildirimler', notifications_markup(ns), path, account['username']))
        if path in ('/mobile','/mobile/'):
            return self.redirect('/')
        if path == '/app-manifest.json':
            manifest = {'id':'/','name':'ÇiftlikPro Enterprise','short_name':'ÇiftlikPro','lang':'tr','start_url':'/','scope':'/','display':'standalone','background_color':'#f5f8f6','theme_color':'#063e2b','icons':[{'src':'/app-assets/icon-192.png','sizes':'192x192','type':'image/png','purpose':'any maskable'},{'src':'/app-assets/icon-512.png','sizes':'512x512','type':'image/png','purpose':'any maskable'}]}
            return send_bytes(self, json.dumps(manifest, ensure_ascii=False).encode(), 'application/manifest+json')
        if path == '/app-service-worker.js':
            return send_bytes(self, (ASSETS/'service-worker.js').read_bytes(), 'application/javascript', [('Service-Worker-Allowed','/')])
        if path.startswith('/app-assets/'):
            filename = path.removeprefix('/app-assets/')
            allowed = {'mobile.css':'text/css','mobile.js':'application/javascript','icon.svg':'image/svg+xml','icon-192.png':'image/png','icon-512.png':'image/png','login.jpg':'image/jpeg','offline.html':'text/html; charset=utf-8'}
            if filename not in allowed or not (ASSETS/filename).is_file():
                return original_send_html(self, 'Dosya bulunamadı', 404)
            return send_bytes(self, (ASSETS/filename).read_bytes(), allowed[filename])
        return original_get(self)
    app.send_html = send_html
    app.do_GET = do_GET
    def do_POST(self):
        if urlparse(self.path).path != '/paddock/assign-many':
            return original_post(self)
        allowed, _, message = ns['license_status']()
        if not allowed:
            return self.redirect('/license', message)
        if not self.require():
            return
        form = self.form()
        try:
            refs = json.loads(form.get('animal_refs') or '[]')
            destination = int(form.get('paddock_id') or 0)
            if not isinstance(refs, list) or not 1 <= len(refs) <= 500:
                raise ValueError('Taşınacak hayvanları seçin.')
            with ns['db']() as c:
                result = move_subjects(ns, c, refs, destination, (form.get('notes') or '').strip())
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            return self.redirect('/paddocks', str(exc))
        ns['audit'](self.user()['username'], 'Toplu hayvan padok taşıma', f'{len(result)} hayvan -> {destination}', self.client_ip())
        return self.redirect('/paddocks?selected='+str(destination), f'{len(result)} hayvanın padoku güncellendi.')
    app.do_POST = do_POST


def move_subjects(ns, connection, refs, destination, notes=''):
    """Atomic bulk version of the existing assign operation, with canonical helpers."""
    connection.execute('BEGIN IMMEDIATE')
    target = connection.execute('select id,name,capacity from paddocks where id=? and active=1',(destination,)).fetchone()
    if not target:
        raise ValueError('Aktif hedef padok seçin.')
    selected = []
    seen = set()
    for ref in refs:
        if not isinstance(ref, str) or ':' not in ref:
            raise ValueError('Hayvan seçimi geçersiz.')
        source, raw_id = ref.split(':',1)
        if source not in ('animal','calf') or not raw_id.isdigit():
            raise ValueError('Hayvan seçimi geçersiz.')
        animal_id = int(raw_id)
        if (source, animal_id) in seen:
            continue
        seen.add((source,animal_id))
        table = 'animals' if source=='animal' else 'calves'
        column = 'animal_id' if source=='animal' else 'calf_id'
        calf_clause = ' and promoted_animal_id is null' if source=='calf' else ''
        row = connection.execute(f"""select id,tag,paddock_id from {table} where id=? and coalesce(status,'Aktif')='Aktif'{calf_clause} and not exists(select 1 from animal_losses l where l.{column}={table}.id)""",(animal_id,)).fetchone()
        if not row:
            raise ValueError('Seçimde aktif olmayan veya bulunamayan hayvan var. Hiçbir hayvan taşınmadı.')
        if row['paddock_id'] != destination:
            selected.append((source,animal_id,row['tag'],row['paddock_id']))
    capacity = int(target['capacity'] or 0)
    if capacity and ns['paddock_population'](destination, connection) + len(selected) > capacity:
        raise ValueError(f'{target["name"]} kapasitesi yeterli değil. Hiçbir hayvan taşınmadı.')
    stamp = ns['datetime'].now().isoformat(timespec='seconds')
    changed_paddocks = {destination}
    for source, animal_id, tag, old_paddock in selected:
        ns['sync_paddock_text'](connection, source, animal_id, destination)
        connection.execute('insert into paddock_history(animal_source,animal_id,from_paddock_id,to_paddock_id,moved_at,notes) values(?,?,?,?,?,?)',(source,animal_id,old_paddock,destination,stamp,notes))
        if old_paddock:
            changed_paddocks.add(old_paddock)
    for paddock_id in changed_paddocks:
        connection.execute('update paddocks set updated_at=? where id=?',(stamp,paddock_id))
    return selected


def accepts_gzip(handler):
    for item in (handler.headers.get('Accept-Encoding') or '').lower().split(','):
        parts = item.strip().split(';')
        if parts[0] == 'gzip':
            return not any(part.strip() in ('q=0', 'q=0.0', 'q=0.00', 'q=0.000') for part in parts[1:])
    return False


def send_response_bytes(handler, data, mime, status=200, headers=()):
    try:
        handler.send_response(status)
        handler.send_header('Content-Type', mime)
        handler.send_header('Content-Length', str(len(data)))
        for name, value in headers:
            handler.send_header(name, value)
        handler.end_headers()
        handler.wfile.write(data)
    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        pass


def send_bytes(handler, data, mime, headers=()):
    cache = 'public, max-age=31536000, immutable' if 'v=' in urlparse(handler.path).query else 'no-cache'
    response_headers = [('Cache-Control',cache),*headers]
    if mime in ('text/css', 'application/javascript', 'application/manifest+json') and accepts_gzip(handler):
        data = gzip.compress(data, compresslevel=5)
        response_headers += [('Content-Encoding','gzip'),('Vary','Accept-Encoding')]
    send_response_bytes(handler, data, mime, headers=response_headers)


def notifications_markup(ns):
    rows = ns['dashboard_export_tasks']('all')
    cards = ''.join(f'<a class="cp-notification-item card" href="{esc(task_url(row))}"><b>{esc(row["subject"])} · {esc(row["task"])}</b><span>{esc(ns["fmt_date"](row["date"]))} · {esc(row["status"])} · {esc(row.get("detail",""))}</span></a>' for row in rows)
    today = ns['date'].today()
    reproductive = []
    with ns['db']() as c:
        pregnancies = ns['active_pregnancy_records'](c)
        latest = {}
        for row in c.execute("select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where coalesce(a.status,'Aktif')='Aktif' and not exists(select 1 from animal_losses l where l.animal_id=a.id) order by e.estrus_date desc,e.id desc"):
            if row['animal_id'] in latest or row['animal_id'] in pregnancies:
                continue
            latest[row['animal_id']] = row
            cycle = ns['next_estrus_cycle'](c, row, today)
            if cycle and cycle['end'] >= today and cycle['start'] <= today+ns['timedelta'](days=30):
                reproductive.append((cycle['center'], '/reproduction-center?stage=estrus&animal='+str(row['animal_id']), row['tag']+' · Kızgınlık takibi', ns['fmt_date'](cycle['start'].isoformat())+' – '+ns['fmt_date'](cycle['end'].isoformat())))
        for aid, row in pregnancies.items():
            try:
                due = ns['date'].fromisoformat(row['due_date'])
            except (ValueError,TypeError):
                continue
            if today <= due <= today+ns['timedelta'](days=60):
                animal = c.execute('select tag from animals where id=?',(aid,)).fetchone()
                reproductive.append((due, '/reproduction-center?stage=birth&animal='+str(aid), animal['tag']+' · Yaklaşan doğum', ns['fmt_date'](due.isoformat())))
    reproductive.sort(key=lambda item:item[0])
    reproductive_cards = ''.join(f'<a class="cp-notification-item card" href="{esc(url)}"><b>{esc(label)}</b><span>{esc(detail)}</span></a>' for _,url,label,detail in reproductive)
    return '<h1>🔔 Bildirimler</h1><p>Sağlık görevleri ve bekleyen ödemeler</p><div class="cp-notification-list">'+(cards or '<div class="card">Bekleyen sağlık görevi veya ödeme yok.</div>')+'</div><div class="card cp-notification-links"><h2>Üreme bildirimleri</h2><div class="cp-notification-list">'+(reproductive_cards or '<p>Yaklaşan kızgınlık veya doğum bildirimi yok.</p>')+'</div><a class="btn alt" href="/estrus">Kızgınlık takibi</a> <a class="btn alt" href="/reproduction-center?stage=birth">Yaklaşan doğumlar</a></div>'


def animal_history_markup(ns, aid):
    # Read existing records only; sales and loss forms remain in their own panel.
    events = []
    fmt = ns['fmt_date']
    with ns['db']() as c:
        animal = c.execute('select * from animals where id=?', (aid,)).fetchone()
        if animal and animal['purchase_date']:
            events.append((animal['purchase_date'], 'İşletmeye giriş', animal['tag']))
        for row in c.execute('select applied_date,kind,product,notes from health where animal_id=? order by applied_date desc,id desc', (aid,)):
            events.append((row['applied_date'], 'Sağlık · '+str(row['kind'] or ''), str(row['product'] or '')+' · '+str(row['notes'] or '')))
        for row in c.execute('select measure_date,weight,notes from weights where animal_id=? order by measure_date desc,id desc', (aid,)):
            events.append((row['measure_date'], 'Tartım', str(row['weight'])+' kg · '+str(row['notes'] or '')))
        for row in c.execute('select insemination_date,attempt,pregnancy_result from inseminations where animal_id=? order by insemination_date desc,id desc', (aid,)):
            events.append((row['insemination_date'], 'Tohumlama', str(row['attempt'])+'. deneme · '+str(row['pregnancy_result'] or '')))
        for row in c.execute("select moved_at,notes from paddock_history where animal_source='animal' and animal_id=? order by moved_at desc,id desc", (aid,)):
            events.append((row['moved_at'], 'Padok hareketi', row['notes']))
        for row in c.execute('select tx_date,tx_type,description,amount from finance where animal_id=? order by tx_date desc,id desc', (aid,)):
            events.append((row['tx_date'], 'Finans · '+str(row['tx_type']), str(row['description'] or '')+' · '+ns['money'](row['amount'])))
    events.sort(key=lambda item: str(item[0] or ''), reverse=True)
    items = ''.join(f'<div class="animal-360-event"><b>{esc(fmt(str(day or "")[:10]))}</b> · {esc(label)}<small>{esc(detail)}</small></div>' for day,label,detail in events)
    return '<div class="card cp-animal-history"><h2>Hayvan Geçmişi</h2><div class="cp-history-events">'+(items or '<p>Bu hayvana ait geçmiş kayıt yok.</p>')+'</div></div>'
