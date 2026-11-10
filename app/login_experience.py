"""Business selection at sign-in; early photo loading with an inline preview."""
import base64
from functools import lru_cache
from html import escape
from http.cookies import SimpleCookie
import io
import re
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit


@lru_cache(maxsize=1)
def preview_data():
    from mobile_ui import ASSETS
    return 'data:image/jpeg;base64,'+base64.b64encode((ASSETS/'login-preview.jpg').read_bytes()).decode('ascii')


def remembered_farm(handler):
    try:
        cookie=SimpleCookie(handler.headers.get('Cookie',''))
        return cookie['cp_login_farm'].value if 'cp_login_farm' in cookie else 'primary'
    except Exception:return 'primary'


def document(html,handler,registry):
    choices=registry.farms() if registry.file.exists() else [registry.farm('primary')]
    query=parse_qs(urlsplit(handler.path).query)
    selected=(query.get('login_farm') or [remembered_farm(handler)])[0]
    if selected not in {r['id'] for r in choices}:selected='primary'
    options=''.join('<option value="'+r['id']+'"'+(' selected' if r['id']==selected else '')+'>'+escape(r['name'])+'</option>' for r in choices)
    field='<label for="cpLoginFarm">İşletme</label><select id="cpLoginFarm" name="login_farm" required aria-label="Giriş yapılacak işletme">'+options+'</select>'
    html=re.sub(r'(<form\b[^>]*\bclass="login-form"[^>]*>)',lambda m:m.group()+field,html,count=1)
    html=html.replace('name="username" autocomplete="username" required autofocus','id="cpLoginUsername" name="username" autocomplete="username" autocapitalize="none" spellcheck="false" enterkeyhint="next" required')
    html=html.replace('<label>Kullanıcı adı</label>','<label for="cpLoginUsername">Kullanıcı adı</label>',1)
    html=html.replace('<label>Şifre</label>','<label for="loginPassword">Şifre</label>',1)
    # This tiny same-photo background is decoded with the document. The full image
    # remains a separate cacheable request and is never awaited by the login form.
    css='''<style id="cpLoginFirstPaint">
    .login-form #cpLoginFarm{display:block;width:100%;max-width:100%;min-width:0;min-height:46px;padding:11px 12px;border:1px solid #ccd9d0;border-radius:11px;background:#fff;color:#193a2b;font:inherit;font-size:16px;box-sizing:border-box}
    @layer ciftlikpro-mobile {@media(max-width:900px){
     html.cp-login-stage{background:#153e2a url("PREVIEW") center/cover fixed!important}
     html body.cp-app.cp-login{background-image:url("/app-assets/login.jpg"),url("PREVIEW")!important;background-position:center,center!important;background-size:cover,cover!important;background-repeat:no-repeat,no-repeat!important;background-attachment:fixed,fixed!important}
     html.cp-login-stage body.cp-app.cp-login .login-shell{min-height:100svh!important;padding:calc(28px + env(safe-area-inset-top)) 22px calc(12px + env(safe-area-inset-bottom))!important}
     html.cp-login-stage body.cp-app.cp-login .login-logo{font-size:29px!important}
     html.cp-login-stage body.cp-app.cp-login .login-visual p{margin:14px 0 0!important}
     html.cp-login-stage body.cp-app.cp-login .login-panel{padding-top:clamp(160px,24svh,240px)!important;margin-top:auto!important}
     html.cp-login-stage body.cp-app.cp-login .login-form label{margin:7px 0 3px!important;font-size:11px!important}
     html.cp-login-stage body.cp-app.cp-login .login-form input,html.cp-login-stage body.cp-app.cp-login #cpLoginFarm{height:44px!important;min-height:44px!important;padding:9px 12px!important;font-size:16px!important}
     html.cp-login-stage body.cp-app.cp-login .password-wrap #loginPassword{height:44px!important;min-height:44px!important;padding:9px 88px 9px 12px!important}
     html.cp-login-stage body.cp-app.cp-login .password-toggle{width:80px!important;height:44px!important;min-height:44px!important}
     html.cp-login-stage body.cp-app.cp-login .login-submit{margin-top:12px!important;min-height:44px!important;height:44px!important}
     html.cp-login-stage body.cp-app.cp-login .forgot{margin-top:7px!important;min-height:32px!important;display:flex!important;align-items:center!important;justify-content:center!important}
     html.cp-login-stage body.cp-app.cp-login .cp-pwa-login{width:auto!important;align-self:center!important;min-height:36px!important;margin:5px auto 0!important;padding:6px 14px!important;font-size:11px!important;border-radius:9px!important;background:#ffffffdb!important}
     html.cp-login-stage body.cp-app.cp-login .login-version{margin-top:8px!important;font-size:9px!important}
     @media(max-height:650px){html.cp-login-stage body.cp-app.cp-login .login-shell{padding-top:18px!important}html.cp-login-stage body.cp-app.cp-login .login-panel{padding-top:90px!important}}
     html body.cp-app.cp-login #cpLoginFarm{font-size:16px!important;min-height:47px!important;width:100%!important;max-width:100%!important;margin:0!important;padding:11px 12px!important;background:#fffffff0!important;border:1px solid #ffffffa0!important;border-radius:10px!important;color:#193a2b!important}
    }}
    </style>'''.replace('PREVIEW',preview_data())
    def html_tag(match):
        tag=match.group()
        if re.search(r'\bclass=',tag):return re.sub(r'(\bclass=[\"\'])',r'\1cp-login-stage ',tag,count=1)
        return tag[:-1]+' class="cp-login-stage">'
    html=re.sub(r'<html\b[^>]*>',html_tag,html,count=1)
    html=re.sub(r'(<head\b[^>]*>)',lambda m:m.group()+'<link rel="preload" as="image" href="/app-assets/login.jpg" media="(max-width:900px)" fetchpriority="high">',html,count=1)
    feedback='''<script id="cpLoginFeedback">(function(){function init(){var f=document.querySelector('.login-form'),b=f&&f.querySelector('.login-submit');if(!b)return;var label=b.textContent;f.addEventListener('submit',function(){b.textContent='İşletme açılıyor…';b.disabled=true;b.setAttribute('aria-busy','true')});window.addEventListener('pageshow',function(){b.textContent=label;b.disabled=false;b.removeAttribute('aria-busy')})}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()})();</script>'''
    return html.replace('</head>',css+'</head>',1).replace('</body>',feedback+'</body>',1)


def login_post(handler,original,registry,ns):
    # Keep the canonical license, password migration, session and audit handler.
    if not ns['license_status']()[0]:return original(handler)
    try:length=int(handler.headers.get('Content-Length','0') or 0)
    except ValueError:return handler.send_html('Geçersiz giriş isteği.',400)
    if length<0 or length>65536:return handler.send_html('Giriş isteği çok büyük.',413)
    raw=handler.rfile.read(length)
    handler.rfile=io.BytesIO(raw)
    try:fields=parse_qs(raw.decode('utf-8'))
    except UnicodeError:return handler.send_html('Geçersiz giriş isteği.',400)
    chosen=(fields.get('login_farm') or ['primary'])[0]
    target=registry.farm(chosen)
    if not target:return handler.redirect('/login','İşletme bulunamadı. Tekrar seçin.')
    handler._login_target=chosen
    username=(fields.get('username') or [''])[0].strip()
    password=(fields.get('password') or [''])[0]
    account=registry.account(username)
    if account and not registry.allowed(account,chosen) and ns['password_verify'](password,account['password']):
        ns['audit'](username,'İşletme giriş izni reddedildi',chosen,handler.client_ip())
        return handler.redirect('/login','Bu işletmeye giriş izniniz yok. Yetkili olduğunuz işletmeyi seçin.')
    return original(handler)


def login_header(handler,name,value,ns):
    chosen=getattr(handler,'_login_target',None)
    if not chosen:return value,None
    cookie=None
    if name.lower()=='set-cookie' and value.startswith('sid='):
        sid=value.split(';',1)[0].split('=',1)[1]
        session=ns['SESSIONS'].get(sid)
        if session is not None:
            session['active_farm']=chosen
            cookie='cp_login_farm='+chosen+'; Max-Age=31536000; HttpOnly; SameSite=Lax; Path=/'
    if name.lower()=='location':
        url=urlsplit(value);query=parse_qs(url.query,keep_blank_values=True)
        if url.path=='/':query['farm']=[chosen]
        elif url.path=='/login':query['login_farm']=[chosen]
        value=urlunsplit(('', '',url.path,urlencode(query,doseq=True),url.fragment))
    return value,cookie
