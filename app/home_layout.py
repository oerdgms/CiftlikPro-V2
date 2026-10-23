"""Per-user home layout stored in the same database as the desktop dashboard."""
import html
import json
from urllib.parse import parse_qs, urlparse

SECTIONS = {'business':'İşletme Bilgileri', 'summary':'Sürü Özeti', 'tasks':'Yaklaşan İşlemler'}
CARDS = {'all':'Genel', 'lactating':'Sağmal', 'dry':'Kuru', 'calf':'Buzağı', 'heifer':'Düve', 'male':'Erkek'}
DEFAULT = {'sections':list(SECTIONS), 'cards':list(CARDS), 'task_limit':3}


def esc(value):
    return html.escape(str(value),quote=True)


def defaults():
    return {k:list(v) if isinstance(v,list) else v for k,v in DEFAULT.items()}


def validate(data):
    if not isinstance(data,dict):raise ValueError('Düzen geçersiz.')
    for name,allowed in (('sections',SECTIONS),('cards',CARDS)):
        values=data.get(name)
        if not isinstance(values,list) or not values or any(not isinstance(v,str) or v not in allowed for v in values) or len(set(values))!=len(values):
            raise ValueError('En az bir bölüm ve bir sürü kartı seçin; tekrarlanan seçim kullanmayın.')
    if type(data.get('task_limit')) is not int or data['task_limit'] not in (3,5,10):
        raise ValueError('Yaklaşan işlem sayısı 3, 5 veya 10 olmalıdır.')
    return {k:list(data[k]) for k in ('sections','cards')}|{'task_limit':data['task_limit']}


def load(ns, username):
    with ns['db']() as c:
        row=c.execute('select setting_value from settings where setting_key=?',('reference_home_'+username,)).fetchone()
    if row:
        try:return validate(json.loads(row['setting_value']))
        except (ValueError,TypeError):pass
    return defaults()


def save(ns, username, data):
    data=validate(data)
    with ns['db']() as c:
        c.execute('insert into settings(setting_key,setting_value) values(?,?) on conflict(setting_key) do update set setting_value=excluded.setting_value',('reference_home_'+username,json.dumps(data)))
    return data


def editor(ns, username):
    config=load(ns,username)
    def choices(name, labels):
        order=config[name]+[key for key in labels if key not in config[name]]
        return ''.join(f'<li data-layout-item><label><input type="checkbox" name="{name}" value="{key}" {"checked" if key in config[name] else ""}><span>{esc(labels[key])}</span></label><span class="cp-layout-move"><button type="button" data-layout-up aria-label="{esc(labels[key])} yukarı">↑</button><button type="button" data-layout-down aria-label="{esc(labels[key])} aşağı">↓</button></span></li>' for key in order)
    options=''.join(f'<option value="{n}" {"selected" if n==config["task_limit"] else ""}>{n} işlem</option>' for n in (3,5,10))
    return f'''<section class="cp-layout-editor"><header class="cp-shared-head"><div><span class="cp-dairy-eyebrow">KİŞİSEL GÖRÜNÜM</span><h1>Ana Sayfa Düzeni</h1><p>Gösterilecekleri seç, oklarla sırala ve kaydet.</p></div><a class="btn alt" href="/">Ana sayfaya dön</a></header><form method="post" action="/home-layout/save" data-layout-form><div class="cp-layout-columns"><section class="card"><h2>Mobil ana sayfa bölümleri</h2><p class="mut">Telefonunda gösterilecek bölümler ve sıraları.</p><ul class="cp-layout-choices">{choices('sections',SECTIONS)}</ul><label>Yaklaşan işlem sayısı<select name="task_limit">{options}</select></label></section><section class="card"><h2>Sürü kartları</h2><p class="mut">Mobil ve masaüstü sürü özetinde aynı seçim ve sıra kullanılır.</p><ul class="cp-layout-choices">{choices('cards',CARDS)}</ul></section></div><div class="cp-layout-actions"><button class="btn" type="submit" name="action" value="save">Düzeni Kaydet</button><button class="btn alt" type="submit" form="cpHomeReset">Varsayılana Dön</button><span data-layout-message role="status"></span></div></form><form method="post" action="/home-layout/reset" id="cpHomeReset"><input type="hidden" name="action" value="reset"></form><section class="card cp-layout-desktop"><h2>Masaüstündeki diğer dashboard kartları</h2><p class="mut">Gelir, gider, performans ve diğer masaüstü kartlarını mevcut düzenleyiciden değiştirebilirsin.</p><a class="btn alt" href="/?edit=1&amp;desktop_editor=1">Masaüstü kartlarını düzenle</a><p class="cp-layout-mobile-note">Bu düzenleyiciyi bilgisayardan aç.</p></section></section><script src="/app-assets/shared.js?v=2.0.29" defer></script>'''


def install(ns):
    app=ns['App'];original_get,original_post=app.do_GET,app.do_POST
    def authorized(handler):
        if not handler.require():return False
        ok,_,message=ns['license_status']()
        if not ok:handler.redirect('/license',message);return False
        return True
    def do_GET(self):
        if urlparse(self.path).path!='/home-layout':return original_get(self)
        if not authorized(self):return
        msg=(parse_qs(urlparse(self.path).query).get('msg') or [''])[0]
        return self.send_html(ns['page']('Ana Sayfa Düzeni',editor(ns,self.user()['username']),'/home-layout',self.user()['username'],msg))
    def do_POST(self):
        if urlparse(self.path).path not in ('/home-layout/save','/home-layout/reset'):return original_post(self)
        if not authorized(self):return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=8192:raise ValueError('Düzen geçersiz.')
            form=parse_qs(self.rfile.read(size).decode('utf-8'),keep_blank_values=True)
            data=defaults() if urlparse(self.path).path=='/home-layout/reset' or form.get('action')==['reset'] else {'sections':form.get('sections',[]),'cards':form.get('cards',[]),'task_limit':int((form.get('task_limit') or ['0'])[0])}
            save(ns,self.user()['username'],data)
        except (ValueError,TypeError,UnicodeError):return self.redirect('/home-layout','Düzen kaydedilemedi. En az bir bölüm ve bir kart seçin.')
        return self.redirect('/home-layout','Ana sayfa düzenin kaydedildi.')
    app.do_GET,app.do_POST=do_GET,do_POST
