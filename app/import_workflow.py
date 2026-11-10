"""One import destination; in-page errors and an explicit preview/confirm step."""
import html
import os
from pathlib import Path
import secrets
import time
from datetime import date
from urllib.parse import parse_qs, urlsplit, urlencode, urlunsplit


def esc(value):return html.escape(str(value or ''),quote=True)


def form_markup(message='',kind=''):
    notice='<div class="cp-import-notice" role="alert">'+esc(message)+'</div>' if message else ''
    return '''<section class="cp-import-screen"><h1>Hayvan İçe Aktarma</h1><p class="mut">Dosyayı seçin, okunabilen kayıtları kontrol edin ve yalnız onayladığınızda seçili işletmeye aktarın.</p>'''+notice+'''<section class="card cp-import-card"><h2>Excel / CSV / PDF dosyası</h2><form method="post" action="/animals/import-preview" enctype="multipart/form-data" class="form" data-animal-import-form>
    <label class="full">Hayvan listesi<input type="file" name="animal_file" accept=".xlsx,.csv,.pdf,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv" required></label>
    <p class="full mut">En fazla 12 MB. PDF dosyasının seçilebilir metin içermesi gerekir. Fotoğraf taramalarını okumak için OCR gerekir; bu sürüm OCR yapmaz.</p>
    <div class="full"><button type="submit" class="btn blue" data-import-submit>Dosyayı Oku ve Önizle</button></div><p class="full cp-import-progress" role="status" aria-live="polite" data-import-status></p></form></section>
    <div class="cp-import-links"><a class="btn alt" href="/data">JSON / Yedek Aktarımı</a><a class="btn alt" href="/reports?tab=animals">Sürü Raporları</a></div></section>'''


def preview_markup(preview,token):
    rows=preview['rows'];ready=sum(bool(r['valid']) for r in rows)
    cards=[]
    for row in rows[:500]:
        state='Aktarılabilir' if row['valid'] else 'Atlanacak'
        born=row.get('birth_date') or ''
        if born:born='Doğum: '+date.fromisoformat(born).strftime('%d/%m/%Y')
        details=' · '.join(str(x) for x in (row.get('record_type'),row.get('breed'),born) if x)
        notes='; '.join(row.get('issues',[]))
        cards.append('<article class="cp-import-row"><header><b>'+esc(row['tag'])+'</b><span>'+state+'</span></header><p>'+esc(details)+'</p>'+('<p class="cp-import-issues">'+esc(notes)+'</p>' if notes else '')+'</article>')
    more='<p class="mut">İlk 500 satır gösteriliyor; toplam '+str(len(rows))+' satır kontrol edildi.</p>' if len(rows)>500 else ''
    return '<section class="cp-import-screen"><h1>Hayvan İçe Aktarma Önizlemesi</h1><p>'+esc(preview['filename'])+'</p><div class="cp-import-notice">'+str(len(rows))+' satır · '+str(ready)+' aktarılabilir · '+str(len(rows)-ready)+' atlanacak. Henüz kayıt aktarılmadı.</div><div class="cp-import-rows">'+''.join(cards)+'</div>'+more+'<form method="post" action="/animals/import-confirm" onsubmit="return confirm(\''+str(ready)+' geçerli kayıt seçili işletmeye aktarılsın mı?\')"><input type="hidden" name="token" value="'+esc(token)+'"><button type="submit" class="btn"'+('' if ready else ' disabled')+'>'+str(ready)+' Geçerli Kaydı İçe Aktar</button></form><p><a class="btn alt" href="/animals/import">İptal / Başka Dosya Seç</a></p></section>'


def enhance(document,handler):
    if not handler.user():return document
    # Retain old bookmarks, including report anchors, without the mobile report hub.
    document=document.replace('/reports#animal-import','/animals/import')
    document=document.replace('/reports?tab=import','/animals/import?')
    document=document.replace('href="#animal-import"','href="/animals/import"')
    document=document.replace('href=\'#animal-import\'','href=\'/animals/import\'')
    if 'data-report-tab="import"' in document:
        document=document.replace('<button class="module-tab" data-report-tab="import">📥 İçe Aktarma</button>', '<a class="module-tab" href="/animals/import">📥 İçe Aktarma</a>')
    if 'data-animal-import-form' in document or urlsplit(handler.path).path=='/animals/import-preview':
        document=document.replace('</head>','<link rel="stylesheet" href="/app-assets/import.css"><script src="/app-assets/import.js" defer></script></head>',1)
    return document


def install(ns):
    app=ns['App'];original_get=app.do_GET;original_post=app.do_POST;original_redirect=app.redirect
    def redirect(self,url,msg=''):
        parsed=urlsplit(url)
        if urlsplit(self.path).path.startswith('/animals/import') and parsed.path=='/reports':
            if parsed.fragment=='animal-import':url='/animals/import'
            elif parsed.fragment=='animal-report':url='/reports?tab=animals'
        return original_redirect(self,url,msg)
    app.redirect=redirect
    def authorized(handler):
        if not ns['license_status']()[0]:handler.redirect('/license');return False
        return handler.require_admin()
    def show(handler,message='',status=200):
        return handler.send_html(ns['page']('Hayvan İçe Aktarma',form_markup(message),'/animals/import',handler.user()['username']),status)
    def do_GET(self):
        url=urlsplit(self.path);query=parse_qs(url.query)
        if url.path=='/reports' and (query.get('tab') or [''])[0]=='import':
            if not authorized(self):return
            query.pop('tab',None)
            return self.redirect('/animals/import'+('?' + urlencode(query,doseq=True) if query else ''))
        if url.path=='/animals/import-preview':
            if not authorized(self):return
            token=(query.get('token') or [''])[0]
            with ns['ANIMAL_IMPORT_LOCK']:preview=ns['ANIMAL_IMPORT_PREVIEWS'].get(token)
            if not preview or preview.get('username')!=self.user()['username'] or time.time()-float(preview.get('created_at',0))>7200:
                return show(self,'Önizleme bulunamadı veya süresi doldu. Dosyayı yeniden seçin.',422)
            return self.send_html(ns['page']('İçe Aktarma Önizlemesi',preview_markup(preview,token),'/animals/import-preview',self.user()['username'],(query.get('msg') or [''])[0]))
        if url.path=='/animals/import':
            if not authorized(self):return
            return show(self,(query.get('msg') or [''])[0])
        return original_get(self)
    def do_POST(self):
        if urlsplit(self.path).path!='/animals/import-preview':return original_post(self)
        if not authorized(self):return
        ajax='application/json' in self.headers.get('Accept','')
        def error(message,status=422):
            if ajax:return self.send_json({'ok':False,'message':message},status)
            return show(self,message,status)
        try:
            size=int(self.headers.get('Content-Length','0') or 0)
            if size>13*1024*1024:return error('Dosya 12 MB sınırını aşıyor.',413)
            fields=self.post_data();upload=fields.get('animal_file')
            if not isinstance(upload,dict) or not upload.get('filename') or not upload.get('content'):
                return error('Lütfen bir XLSX, CSV veya metin içeren PDF dosyası seçin.')
            raw=ns['parse_animal_import_file'](upload['filename'],upload['content'])
            rows=ns['prepare_animal_import'](upload['filename'],raw)
            if not rows:return error('Dosyada aktarılabilecek hayvan satırı bulunamadı.')
        except Exception as exc:
            message=str(exc)
            if 'taranmış' in message or 'görüntü biçiminde' in message:
                message='Bu PDF fotoğraf olarak taranmış; seçilebilir metin içermiyor. Henüz hiçbir kayıt aktarılmadı. Bakanlık sisteminden alınan metin içeren PDF, Excel veya CSV dosyası seçin. Taranmış PDF için önce OCR ile metin çıkarılması ve küpelerin kontrol edilmesi gerekir.'
            else:message='Dosya okunamadı: '+message
            return error(message)
        token=secrets.token_urlsafe(24);now=time.time()
        with ns['ANIMAL_IMPORT_LOCK']:
            previews=ns['ANIMAL_IMPORT_PREVIEWS']
            for key,item in list(previews.items()):
                if now-float(item.get('created_at') or 0)>7200:previews.pop(key,None)
            previews[token]={'username':self.user()['username'],'filename':os.path.basename(upload['filename']),'created_at':now,'rows':rows}
        ns['audit'](self.user()['username'],'Hayvan içe aktarma önizlemesi',os.path.basename(upload['filename'])+' · '+str(len(rows))+' satır',self.client_ip())
        url='/animals/import-preview?token='+token
        from multi_farm import current_id,farm_url
        url=farm_url(url,current_id())
        if ajax:return self.send_json({'ok':True,'redirect':url})
        return self.redirect(url)
    app.do_GET=do_GET;app.do_POST=do_POST
