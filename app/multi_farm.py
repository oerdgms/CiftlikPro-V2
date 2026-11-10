"""Request-local enterprise storage, shared accounts and explicit form boundaries."""
from collections.abc import MutableMapping
from contextlib import contextmanager
from contextvars import ContextVar
from html import escape, unescape
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import threading
import logging
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

_storage = ContextVar('ciftlik_storage', default=None)
_selected = ContextVar('ciftlik_selected_farm', default=None)
_registry_lock = threading.RLock()
_account_sync_lock = threading.RLock()
_account_sync_signatures = {}
PRIMARY = 'primary'
IDENTITY_PATHS = {'/login','/forgot-password','/forgot-verify','/forgot-reset','/password-change','/users','/users/new','/users/edit'}
PUBLIC_PATHS = {'/login','/forgot-password','/forgot-verify','/forgot-reset','/license','/license-info','/app-install','/app-build.json','/app-manifest.json','/app-service-worker.js','/favicon.ico'}


@contextmanager
def connection(path, **kwargs):
    con=sqlite3.connect(path, **kwargs)
    con.row_factory=sqlite3.Row
    try:
        with con:yield con
    finally:
        con.close()


def current_id():
    return (_storage.get() or {}).get('id', PRIMARY)


@contextmanager
def scope(farm):
    token = _storage.set(farm)
    try:
        yield
    finally:
        _storage.reset(token)


class ScopedPath(os.PathLike):
    def __init__(self, base, filename):
        self.base = Path(base)
        self.filename = filename
    def path(self):
        farm = _storage.get()
        return (Path(farm['directory'])/self.filename if self.filename else Path(farm['directory'])) if farm and farm['id'] != PRIMARY else self.base
    def __fspath__(self):return os.fspath(self.path())
    def __str__(self):return str(self.path())
    def __truediv__(self, other):return self.path()/other
    def __getattr__(self, name):return getattr(self.path(),name)
    def __repr__(self):return repr(self.path())


class ScopedPreviews(MutableMapping):
    def __init__(self, original):
        self.original=original;self.values={}
    def bucket(self):
        farm=_storage.get()
        if not farm or farm['id']==PRIMARY:return self.original
        return self.values.setdefault(str(farm['directory']),{})
    def __getitem__(self,key):return self.bucket()[key]
    def __setitem__(self,key,value):self.bucket()[key]=value
    def __delitem__(self,key):del self.bucket()[key]
    def __iter__(self):return iter(self.bucket())
    def __len__(self):return len(self.bucket())


class Registry:
    def __init__(self,ns):
        self.ns=ns
        value=ns['DB']
        self.primary_db=value.base if isinstance(value,ScopedPath) else Path(value)
        self.root=self.primary_db.parent
        self.file=self.root/'enterprises.sqlite3'
    def connect(self):
        return connection(self.file,timeout=15)
    def primary_name(self):
        try:
            with connection(self.primary_db) as c:
                row=c.execute("select setting_value from settings where setting_key='farm_name'").fetchone()
            return (row[0] if row else '') or 'İlk İşletmem'
        except sqlite3.Error:return 'İlk İşletmem'
    def ensure(self):
        if self.file.exists():
            with self.connect() as c:
                try:
                    if c.execute('select 1 from enterprises where id=?',(PRIMARY,)).fetchone() and c.execute("select 1 from sqlite_master where name='enterprise_access'").fetchone():return
                except sqlite3.Error:pass
        with _registry_lock:
            with self.connect() as c:
                c.executescript('''CREATE TABLE IF NOT EXISTS enterprises(id TEXT PRIMARY KEY,name TEXT NOT NULL,ready INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS enterprise_access(farm_id TEXT NOT NULL,username TEXT NOT NULL,PRIMARY KEY(farm_id,username));''')
                c.execute('insert or ignore into enterprises(id,name,ready) values(?,?,1)',(PRIMARY,self.primary_name()))
    def farm(self,fid):
        if not self.file.exists() and fid==PRIMARY:
            return {'id':PRIMARY,'name':self.primary_name(),'directory':str(self.root)}
        if not self.file.exists():return None
        if not re.fullmatch(r'(primary|f_[a-f0-9]{16})',str(fid or '')):return None
        with self.connect() as c:row=c.execute('select * from enterprises where id=? and ready=1',(fid,)).fetchone()
        if not row:return None
        farm=dict(row)
        farm['directory']=str(self.root if fid==PRIMARY else self.root/'enterprises'/fid)
        return farm
    def farms(self):
        self.ensure()
        with self.connect() as c:ids=[r[0] for r in c.execute('select id from enterprises where ready=1 order by case when id=? then 0 else 1 end,rowid',(PRIMARY,))]
        return [self.farm(fid) for fid in ids]
    def account(self,username):
        try:
            with connection(self.primary_db) as c:
                c.row_factory=sqlite3.Row
                row=c.execute('select * from users where username=? and active=1',(username,)).fetchone()
            return dict(row) if row else None
        except sqlite3.Error:return None
    def allowed(self,account,fid):
        if not account:return False
        if account.get('role')=='admin' or fid==PRIMARY:return True
        if not self.file.exists():return False
        with self.connect() as c:return c.execute('select 1 from enterprise_access where farm_id=? and username=?',(fid,account['username'])).fetchone() is not None
    def sync_accounts(self,farm,force=False):
        if farm['id']==PRIMARY:return
        # Read shared accounts once. Do not reopen/scan every enterprise users
        # table for every request, or queue competing DELETE/INSERT transactions.
        # Permissions themselves are always checked against the primary database.
        with _account_sync_lock:
            with connection(self.primary_db) as source:
                # last_login belongs to the primary identity store; it is not a credential change.
                cols=[r[1] for r in source.execute('pragma table_info(users)') if r[1]!='last_login']
                names=','.join('"'+x+'"' for x in cols)
                rows=[tuple(r) for r in source.execute('select '+names+' from users order by id')]
            path=Path(farm['directory'])/'ciftlik.db'
            stat=path.stat()
            key=(str(self.primary_db.resolve()),str(path.resolve()))
            # File identity protects delete/recreate/restore within the same process.
            signature=(tuple(cols),tuple(rows),stat.st_dev,stat.st_ino)
            with _account_sync_lock:
                if not force and _account_sync_signatures.get(key)==signature:return
                with connection(path,timeout=5) as target:
                    self._write_accounts(target,cols,rows)
                stat=path.stat()
                signature=(tuple(cols),tuple(rows),stat.st_dev,stat.st_ino)
                if len(_account_sync_signatures)>=128:_account_sync_signatures.clear()
                _account_sync_signatures[key]=signature
    def _write_accounts(self,target,cols,rows):
        shared=[r[1] for r in target.execute('pragma table_info(users)') if r[1] in cols]
        names=','.join('"'+x+'"' for x in shared)
        rows=[tuple(row[cols.index(col)] for col in shared) for row in rows]
        old=[tuple(r) for r in target.execute('select '+names+' from users order by id')]
        if old==rows:return
        # IDs remain those of the shared account table, including existing audit references.
        target.execute('delete from users')
        target.executemany('insert into users('+names+') values('+','.join('?' for _ in shared)+')',rows)
    def snapshot_index(self):
        target=self.root/'enterprise-index-backups'
        target.mkdir(exist_ok=True)
        destination=target/'enterprises-last.sqlite3'
        with self.connect() as source,connection(destination) as out:source.backup(out)
    def create(self,name):
        name=str(name or '').strip()
        if not name or len(name)>100:raise ValueError('İşletme adı 1–100 karakter olmalıdır.')
        self.ensure()
        with _registry_lock:
            with self.connect() as c:
                if c.execute('select 1 from enterprises where lower(name)=lower(?)',(name,)).fetchone():raise ValueError('Bu işletme adı zaten kullanılıyor.')
            fid='f_'+secrets.token_hex(8)
            farm={'id':fid,'name':name,'directory':str(self.root/'enterprises'/fid)}
            folder=Path(farm['directory']);folder.mkdir(parents=True)
            self.snapshot_index()
            try:
                with scope(farm):
                    self.ns['init_db']()
                    self.ns['ensure_archive_schema']()
                    self.ns['setting_set']('farm_name',name)
                self.sync_accounts(farm)
                with self.connect() as c:c.execute('insert into enterprises values(?,?,1)',(fid,name))
            except Exception:
                shutil.rmtree(folder,ignore_errors=True)
                raise
            return farm


def farm_url(value,fid):
    if not value or value.startswith(('#','data:','blob:','javascript:','mailto:','tel:')):return value
    url=urlsplit(unescape(value))
    if url.scheme or url.netloc or not url.path.startswith('/'):return value
    if url.path.startswith('/app-assets/') or url.path in PUBLIC_PATHS:return value
    query=parse_qs(url.query,keep_blank_values=True)
    if 'farm' not in query:query['farm']=[fid]
    return urlunsplit(('', '',url.path,urlencode(query,doseq=True),url.fragment))


_TAG=re.compile(r'<(?:a|form|button|input|img|source)\b[^>]*>',re.I)
_ATTR=re.compile(r'\b(href|formaction|action|src|data-photo-original)\s*=\s*([\"\'])(.*?)\2',re.I)

def enhance_document(document,handler,ns):
    if urlsplit(handler.path).path=='/login':
        from login_experience import document as login_document
        return login_document(document,handler,Registry(ns))
    if not handler.user() or '<body' not in document:return document
    farm=_selected.get()
    if not farm:
        registry=Registry(ns)
        farm=registry.farm(PRIMARY)
    fid=farm['id']
    enabled=Registry(ns).file.exists()
    def tag(match):
        value=match.group()
        if value.lower().startswith('<form') and not re.search(r'\baction\s*=',value,re.I):
            value=value[:-1]+' action="'+escape(farm_url(handler.path,fid),quote=True)+'">'
        return _ATTR.sub(lambda m:m.group(1)+'='+m.group(2)+escape(farm_url(m.group(3),fid),quote=True)+m.group(2),value)
    # Never edit JavaScript literals or CSS while decorating HTML attributes.
    parts=re.split(r'(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)',document,flags=re.I|re.S)
    document=''.join(p if i%2 or not enabled else _TAG.sub(tag,p) for i,p in enumerate(parts))
    request_url=urlsplit(handler.path)
    request_query=parse_qs(request_url.query)
    is_home=(request_url.path=='/' and request_query.get('app_view',[''])[0] not in ('modules','tasks')
             and request_query.get('edit',[''])[0]!='1')
    path=request_url.path
    print_report=path in {'/health/tasks/print','/health/plans/print','/dashboard/tasks/print',
                          '/reproduction-center/print','/reports/animals/print'}
    return_to_reports=(print_report or path in {'/agriculture/reports','/animals/import','/animals/import-preview'}
                       or (path=='/reports' and 'tab' in request_query)
                       or (path in {'/paddocks','/feeds','/milk-center'} and request_query.get('from_reports')==['1']))
    marker=''
    if not print_report:
        bar_class='cp-enterprise-bar'+(' cp-enterprise-bar--home' if is_home else '')
        marker='<div id="cpEnterpriseBar" class="'+bar_class+'"><a href="/farms?farm='+fid+'"><small>Aktif işletme</small><strong>'+escape(farm['name'])+'</strong><span>Değiştir ›</span></a></div>'
    if return_to_reports:
        # Replace existing print-page return links with one common top action.
        if print_report:
            document=re.sub(r'<a href="/reports(?:\?[^"]*)?(?:#animal-report)?">(?:← )?Raporlara Dön</a>','',document)
            # The compact task print template has an implicit head. Close it
            # explicitly so the common report styles are loaded there too.
            if '</head>' not in document:
                document=re.sub(r'(<html\b[^>]*>)',r'\1<head>',document,count=1)
                document=re.sub(r'(<body\b[^>]*>)',r'</head>\1',document,count=1)
        back=escape(farm_url('/reports',fid) if enabled else '/reports',quote=True)
        marker+='<nav class="cp-report-return" aria-label="Rapor gezinmesi"><a href="'+back+'"><span aria-hidden="true">←</span> Raporlara Dön</a></nav>'
    if marker:
        container=r'(<main\b[^>]*>)' if '<main' in document and not print_report else r'(<body\b[^>]*>)'
        document=re.sub(container,lambda m:m.group()+marker,document,count=1)
    config=json.dumps({'id':fid,'name':farm['name']},ensure_ascii=False).replace('<','\\u003c')
    head='<link rel="stylesheet" href="/app-assets/farms.css"><script id="cpEnterpriseConfig" type="application/json">'+config+'</script><script src="/app-assets/farms.js"></script>'
    if not enabled:head='<link rel="stylesheet" href="/app-assets/farms.css">'
    # Settings already exist in the menu. Keep one enterprise switch, rather
    # than a second button opening the same business settings screen.
    document=re.sub(r'<a class="cp-ref-business-link"[^>]*>.*?</a>',
                    '<a class="cp-ref-business-link" href="/farms?farm='+fid+'">İşletmeler · Değiştir</a>',document,count=1,flags=re.S)
    return document.replace('</head>',head+'</head>',1)


def csrf_token(handler):
    account=handler.user()
    session=handler._farm_ns['SESSIONS'].get(handler.parse_cookie())
    if not account or session is None:return ''
    return session.setdefault('farm_csrf',secrets.token_urlsafe(24))


def management(handler,ns,registry,farm):
    account=handler.user();is_admin=account.get('role')=='admin'
    token=csrf_token(handler)
    hidden='<input type="hidden" name="csrf" value="'+token+'">'
    cards=[]
    for item in registry.farms():
        if not registry.allowed(account,item['id']):continue
        active=item['id']==farm['id']
        cards.append('<article class="cp-enterprise-card"><div><h2>'+escape(item['name'])+'</h2><p>'+('Şu anda açık' if active else 'Ayrı hayvan, stok, rasyon ve finans kayıtları')+'</p></div><form method="post" action="/farms/switch">'+hidden+'<input type="hidden" name="target" value="'+item['id']+'"><button class="btn"'+(' disabled' if active else '')+'>'+('Seçili' if active else 'İşletmeyi Aç')+'</button></form></article>')
    body='<section class="cp-enterprises"><h1>İşletmeler</h1><p>Her işletmenin kayıtları ve fotoğrafları ayrıdır. İşletme adı üstte görünür.</p>'+''.join(cards)
    if is_admin:
        body+='<section class="cp-enterprise-card"><h2>İşletme Ekle</h2><form method="post" action="/farms/create">'+hidden+'<label>İşletme adı<input name="name" maxlength="100" required autocomplete="organization"></label><button class="btn">Yeni İşletme Oluştur</button></form></section>'
        with connection(registry.primary_db) as c:users=c.execute("select username,full_name,role from users where active=1 order by username").fetchall()
        body+='<section class="cp-enterprise-card"><h2>Kullanıcı Erişimi</h2><p>Yöneticiler tüm işletmelere erişir. Diğer hesaplar ilk işletmeye ve burada izin verilen işletmelere erişir. Hesaplar ve şifreler ortaktır.</p><a class="btn alt" href="/users">Kullanıcı Yönetimi</a>'
        farms=registry.farms()
        for username,full_name,role in users:
            if role=='admin':continue
            body+='<form method="post" action="/farms/access" class="cp-enterprise-access">'+hidden+'<input type="hidden" name="username" value="'+escape(username,quote=True)+'"><h3>'+escape(full_name or username)+'</h3>'
            for item in farms:
                if item['id']==PRIMARY:continue
                checked=' checked' if registry.allowed({'username':username,'role':role},item['id']) else ''
                body+='<label><input type="checkbox" name="access_'+item['id']+'" value="1"'+checked+'>'+escape(item['name'])+'</label>'
            body+='<button class="btn alt">Erişimi Kaydet</button></form>'
        body+='</section>'
    body+='</section>'
    return handler.send_html(ns['page']('İşletmeler',body,'/farms',account['username']))


def install(ns):
    if ns.get('_multi_farm_installed'):return
    ns['_multi_farm_installed']=True
    for key,filename in [('DB','ciftlik.db'),('UPLOADS','uploads'),('BACKUPS','backups'),('DATA_ROOT','')]:
        ns[key]=ScopedPath(ns[key],filename)
    ns['ANIMAL_IMPORT_PREVIEWS']=ScopedPreviews(ns['ANIMAL_IMPORT_PREVIEWS'])
    app=ns['App'];old_get=app.do_GET;old_post=app.do_POST;old_user=app.user;old_header=app.send_header
    app._farm_ns=ns
    def user(self):
        if hasattr(self,'_farm_account'):return self._farm_account
        value=old_user(self)
        registry=getattr(self,'_farm_registry',None)
        if value and registry and registry.file.exists():
            account=registry.account(value['username'])
            self._farm_account={k:account.get(k) for k in ('id','username','role','full_name')} if account else None
            return self._farm_account
        return value
    app.user=user
    def send_header(self,name,value):
        from login_experience import login_header
        value,extra_cookie=login_header(self,name,value,ns)
        if extra_cookie:old_header(self,'Set-Cookie',extra_cookie)
        farm=_selected.get()
        if name.lower()=='location' and farm:value=farm_url(value,farm['id'])
        return old_header(self,name,value)
    app.send_header=send_header
    def request(self,original):
        url=urlsplit(self.path);registry=Registry(ns);self._farm_registry=registry
        if self.command=='GET' and url.path=='/settings':
            return self.redirect('/farm-profile'+('?' + url.query if url.query else ''))
        if url.path.startswith('/app-assets/') or url.path in PUBLIC_PATHS or url.path in IDENTITY_PATHS:
            with scope(None):
                if self.command=='POST' and url.path=='/login':
                    from login_experience import login_post
                    return login_post(self,original,registry,ns)
                return original(self)
        query=parse_qs(url.query)
        requested=(query.get('farm') or [None])[0] or self.headers.get('X-CiftlikPro-Farm')
        if not requested:
            referer=urlsplit(self.headers.get('Referer',''))
            if referer.netloc==self.headers.get('Host'):
                requested=(parse_qs(referer.query).get('farm') or [None])[0]
        account=None if self.headers.get('Authorization','').lower().startswith('bearer ') else self.user()
        session=ns['SESSIONS'].get(self.parse_cookie()) or {}
        if not requested and (self.command=='POST' or url.path.startswith('/uploads/') or url.path=='/photo-preview'):requested=PRIMARY
        requested=requested or session.get('active_farm') or PRIMARY
        if url.path.startswith('/farms'):registry.ensure()
        if not registry.file.exists() and requested==PRIMARY:
            return original(self)
        farm=registry.farm(requested)
        if not farm:return self.send_html('İşletme bulunamadı.',404)
        selected=_selected.set(farm)
        try:
            if account and not registry.allowed(account,farm['id']):return self.send_html('Bu işletmeye erişim izniniz yok. <a href="/farms">İşletmeler</a>',403)
            photo=url.path.startswith('/uploads/') or url.path=='/photo-preview'
            if photo and not account:return self.send_html('Fotoğraf için giriş yapın.',401)
            if not account and not url.path.startswith('/api/v1/'):
                return self.redirect('/login')
            if url.path.startswith('/farms'):
                allowed,_,message=ns['license_status']()
                if not allowed:return self.redirect('/license',message)
            if self.command=='GET' and account and not photo and not url.path.startswith('/api/') and 'farm' not in query:
                return self.redirect(farm_url(self.path,farm['id']))
            if farm['id']!=PRIMARY and not photo:
                registry.sync_accounts(farm,force=url.path=='/api/v1/login')
            if self.command=='POST' and url.path=='/api/v1/login':
                length=int(self.headers.get('Content-Length','0') or 0)
                if length>1048576:return self.send_json({'ok':False,'message':'İstek çok büyük.'},413)
                raw=self.rfile.read(length);self.rfile=io.BytesIO(raw)
                try:body=json.loads(raw)
                except (ValueError,UnicodeError):body={}
                identity=registry.account(str(body.get('username','')).strip()) if isinstance(body,dict) else None
                if identity and ns['password_verify'](str(body.get('password','')),identity['password']) and not registry.allowed(identity,farm['id']):
                    return self.send_json({'ok':False,'message':'Bu işletmeye erişim izniniz yok.'},403)
            with scope(farm):
                if url.path=='/farms' and self.command=='GET':
                    if not self.require():return
                    return management(self,ns,registry,farm)
                if url.path.startswith('/farms/') and self.command=='POST':
                    if not self.require():return
                    data=self.form()
                    if not secrets.compare_digest(data.get('csrf',''),csrf_token(self)):return self.send_html('Oturum doğrulaması başarısız. İşletmeler sayfasını tekrar açın.',403)
                    if url.path=='/farms/switch':
                        target=registry.farm(data.get('target',''))
                        if not target or not registry.allowed(account,target['id']):return self.send_html('Bu işletmeye erişim izniniz yok.',403)
                        session['active_farm']=target['id']
                        return self.redirect('/?farm='+target['id'])
                    if not self.require_admin():return
                    if url.path=='/farms/create':
                        try:target=registry.create(data.get('name',''))
                        except (ValueError,sqlite3.Error,OSError) as exc:return self.redirect('/farms',str(exc))
                        session['active_farm']=target['id']
                        ns['audit'](account['username'],'İşletme oluşturdu',target['name'],self.client_ip())
                        return self.redirect('/?farm='+target['id'])
                    if url.path=='/farms/access':
                        username=data.get('username','');target=registry.account(username)
                        if not target or target['role']=='admin':return self.send_html('Kullanıcı seçimi geçersiz.',400)
                        registry.snapshot_index()
                        with registry.connect() as c:
                            c.execute('delete from enterprise_access where username=?',(username,))
                            for item in registry.farms():
                                if data.get('access_'+item['id'])=='1':c.execute('insert into enterprise_access values(?,?)',(item['id'],username))
                        ns['audit'](account['username'],'İşletme erişimi güncelledi',username,self.client_ip())
                        return self.redirect('/farms','Kullanıcı erişimi kaydedildi.')
                    return self.send_html('İşlem bulunamadı.',404)
                result=original(self)
                if self.command=='POST' and url.path=='/farm-profile':
                    name=ns['setting_get']('farm_name',farm['name'])
                    if name:
                        with registry.connect() as c:c.execute('update enterprises set name=? where id=?',(name,farm['id']))
                return result
        finally:
            _selected.reset(selected)
    def do_GET(self):
        # A disconnected browser must not trigger a second response. Database
        # contention before response headers gets a readable retry screen.
        self._farm_response_started=False
        self.__dict__.pop('_farm_account',None)
        try:return request(self,old_get)
        except (BrokenPipeError,ConnectionResetError):return
        except Exception as exc:
            logging.exception('ÇiftlikPro GET failed: %s',urlsplit(self.path).path)
            if self._farm_response_started:return
            busy=isinstance(exc,sqlite3.OperationalError) and any(s in str(exc).lower() for s in ('locked','busy'))
            message='İşletme şu anda başka bir işlemi tamamlıyor. Biraz sonra yeniden deneyin.' if busy else 'Sayfa açılamadı. Yeniden deneyin. Sorun sürerse sunucu kayıtlarını kontrol edin.'
            if urlsplit(self.path).path.startswith('/api/'):
                return self.send_json({'ok':False,'message':message},503 if busy else 500)
            retry=escape(self.path,quote=True)
            body=('<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ÇiftlikPro · Yeniden dene</title><style>body{font:16px system-ui;background:#eff5f1;color:#193c2b;padding:24px}main{max-width:460px;margin:12vh auto;background:white;padding:24px;border-radius:18px}a{display:inline-block;padding:12px;margin:8px 8px 0 0;color:#086044}</style><main><h1>Bağlantıyı yeniden deneyin</h1><p>'+message+'</p><a href="'+retry+'">Yeniden dene</a><a href="/login">Giriş ekranı</a></main></html>').encode('utf-8')
            self.send_response(503 if busy else 500)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(body)))
            if busy:self.send_header('Retry-After','2')
            self.end_headers();self.wfile.write(body)
    def do_POST(self):
        self._farm_response_started=False
        self.__dict__.pop('_farm_account',None)
        if urlsplit(self.path).path!='/login':return request(self,old_post)
        try:return request(self,old_post)
        except (BrokenPipeError,ConnectionResetError):return
        except Exception as exc:
            logging.exception('ÇiftlikPro sign-in failed')
            if self._farm_response_started:return
            message='Giriş işlemi tamamlanamadı. Biraz sonra yeniden deneyin.'
            chosen=getattr(self,'_login_target','primary')
            url='/login?'+urlencode({'login_farm':chosen,'msg':message})
            # Only redirect to the GET form. Never replay credentials or POSTs.
            return self.redirect(url)
    old_end_headers=app.end_headers
    def end_headers(self):
        self._farm_response_started=True
        return old_end_headers(self)
    app.end_headers=end_headers
    app.do_GET=do_GET;app.do_POST=do_POST
    original_backup_dir=ns['configured_backup_dir']
    def configured_backup_dir():
        result=original_backup_dir()
        if current_id()!=PRIMARY and ns['get_setting']('backup_directory','').strip():
            result=Path(result)/('isletme-'+current_id())
            result.mkdir(parents=True,exist_ok=True)
        return result
    ns['configured_backup_dir']=configured_backup_dir
    original_validate=ns['validate_backup_zip']
    def validate_backup_zip(path):
        ok,message,manifest=original_validate(path)
        if ok and (manifest.get('farm_id') or PRIMARY)!=current_id():
            return False,'Bu yedek başka bir işletmeye ait. Önce ait olduğu işletmeyi açın.',None
        return ok,message,manifest
    ns['validate_backup_zip']=validate_backup_zip
    original_restore=ns['restore_backup_zip']
    def restore_backup_zip(*args,**kwargs):
        try:return original_restore(*args,**kwargs)
        finally:
            with _account_sync_lock:_account_sync_signatures.clear()
    ns['restore_backup_zip']=restore_backup_zip
    original_export=ns['export_payload']
    def export_payload():
        payload=original_export()
        payload['farm_id']=current_id()
        return payload
    ns['export_payload']=export_payload
    original_import=ns['import_payload']
    def import_payload(payload,strategy='skip'):
        if isinstance(payload,dict) and payload.get('farm_id') and payload['farm_id']!=current_id():
            raise ValueError('Bu JSON başka bir işletmeye ait. Ait olduğu işletmeyi açın.')
        return original_import(payload,strategy)
    ns['import_payload']=import_payload
    original_daily=ns['daily_backup']
    def daily_backup():
        registry=Registry(ns)
        if _storage.get() is not None or not registry.file.exists():return original_daily()
        for farm in registry.farms():
            with scope(farm):original_daily()
    ns['daily_backup']=daily_backup
    original_init=ns['init_db']
    def init_db():
        result=original_init()
        registry=Registry(ns)
        if _storage.get() is None and registry.file.exists():
            for farm in registry.farms():
                if farm['id']==PRIMARY:continue
                with scope(farm):original_init();ns['ensure_archive_schema']()
                registry.sync_accounts(farm)
        return result
    ns['init_db']=init_db
    original_api_user=ns['_api_auth_user']
    def api_auth_user(handler):
        account=original_api_user(handler)
        registry=getattr(handler,'_farm_registry',None)
        if account and registry and registry.file.exists():
            actual=registry.account(account['username'])
            if not actual or not registry.allowed(actual,current_id()):return None
            account.update({key:actual[key] for key in ('id','role','full_name')})
        return account
    ns['_api_auth_user']=api_auth_user
