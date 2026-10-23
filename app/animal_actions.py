"""Animal-specific event chooser; saves use existing Enterprise record handlers."""
from datetime import date
from urllib.parse import parse_qs, urlencode, urlparse

import dairy_management as dairy
import mobile_reference as ref

esc = ref.esc
CHOICES = [
    ('heat','Kızgınlık Gösterdi','Gözlem tarihi ve belirtiler','flame','red'),
    ('note','İşletme Notu','Hayvan kartındaki notu düzenle','edit','slate'),
    ('inseminated','Tohumlandı','Tohumlama tarihi ve boğa bilgisi','tube','blue'),
    ('pregnant','Gebe','Son tohumlamanın sonucunu kaydet','check','purple'),
    ('empty','Boş / Gebe Değil','Son tohumlamanın sonucunu kaydet','history','slate'),
    ('lactating','Sağmal / Laktasyonda','Sağıma başlangıç ve laktasyon sırası','milk','green'),
    ('dry','Kuru','Kuruya çıkış tarihini kaydet','pause','blue'),
    ('heifer','Düve','Manuel hayvan tipini belirle','animals','purple'),
    ('birth','Doğum Yaptı','Anne seçili buzağı kaydı','birth','pink'),
    ('health','Sağlık Kaydı','Aşı, ilaç veya muayene planı','heart','red'),
    ('weight','Kilo Ölçümü','Tarih ve canlı ağırlık','weight','teal'),
]
GENERAL = {'note','health','weight'}
EXTRA_ICONS = {
    'birth':'<path d="m6 8-3-3v6l3 2M18 8l3-3v6l-3 2M6 6h12v10l-3 4H9l-3-4zM8 13h8v5H8zM9 9h.01M15 9h.01M7 6 6 3M17 6l1-3"/>',
    'tube':'<path d="M8 3h8M9 3v15a3 3 0 0 0 6 0V3M9 10h6M12 14h3M9 17h2"/>',
    'milk':'<path d="M9 3h6v4l3 5v9H6v-9l3-5zM9 7h6M6 13h12"/>',
    'pause':'<circle cx="12" cy="12" r="9"/><path d="M9 8v8M15 8v8"/>',
    'animals':'<path d="m6 8-3-3v6l3 2M18 8l3-3v6l-3 2M6 6h12v10l-3 4H9l-3-4zM8 13h8v5H8zM9 9h.01M15 9h.01"/>',
    'weight':'<path d="M6 7h12l3 14H3z"/><circle cx="12" cy="5" r="3"/><path d="M8 12v5M8 15l3-3M8 15l3 2M16 13c-4-3-4 6 0 3h-1"/>',
}


def icon(name):
    if name not in EXTRA_ICONS:return ref.glyph(name)
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+EXTRA_ICONS[name]+'</svg>'


def subject(c, source, raw_id):
    if source not in ('animal','calf') or not str(raw_id).isdigit() or not 0 < int(raw_id) < 2**63:
        raise ValueError('Hayvan seçimi geçersiz.')
    table,column = ('animals','animal_id') if source=='animal' else ('calves','calf_id')
    animal=c.execute(f"select * from {table} a where id=? and coalesce(status,'Aktif')='Aktif' and not exists(select 1 from animal_losses l where l.{column}=a.id)",(int(raw_id),)).fetchone()
    if not animal or (source=='calf' and animal['promoted_animal_id']):
        raise ValueError('Aktif hayvan bulunamadı.')
    return dict(animal)


def markup(ns, query):
    source=(query.get('source') or ['animal'])[0];raw_id=(query.get('id') or [''])[0]
    event=(query.get('event') or [''])[0]
    with ns['db']() as c:
        animal=subject(c,source,raw_id);sid=animal['id']
        female=source=='animal' and animal['gender']=='Dişi'
        options=[x for x in CHOICES if female or x[0] in GENERAL]
        choice=next((x for x in options if x[0]==event),None)
        if event and not choice:raise ValueError('Bu hayvan için işlem seçimi geçersiz.')
        state=dairy.current_status(c,animal) if female else None
        latest=c.execute('select * from inseminations where animal_id=? order by insemination_date desc,id desc limit 1',(sid,)).fetchone() if female else None
        pregnant=bool(ns['is_currently_pregnant'](c,sid)) if female else False
    def url(action=''):
        return '/animal-events?'+urlencode({'source':source,'id':sid,**({'event':action} if action else {})})
    title=choice[1] if choice else 'Durum Seçin'
    if event=='birth':title='Doğum Bilgisi Ekle'
    heading=('<a class="cp-state-back" data-cp-state-step href="'+esc(url())+'" aria-label="Durum seçimine dön">'+ref.glyph('chevron')+'</a>') if event else ''
    header='<header class="cp-state-head"><div>'+heading+'<h2 id="cpStateTitle">'+esc(title)+'</h2></div><a class="cp-state-cancel" data-cp-state-close href="/'+source+'?id='+str(sid)+'">Vazgeç</a></header>'
    name=animal['tag']+(' · '+animal['nickname'] if animal.get('nickname') else '')
    status=state['label'] if female else ('Buzağı' if source=='calf' else animal['gender'])
    context='<div class="cp-state-subject"><span class="cp-state-subject-icon">'+icon('animals')+'</span><div><b>'+esc(name)+'</b><small>'+esc(status)+(' · Gebe' if pregnant else '')+'</small></div></div>'
    hidden=f'<input type="hidden" name="{source}_id" value="{sid}">'
    today=date.today().isoformat()
    def field(label,name,value='',kind='text',extra='',wide=False):
        return '<label'+(' class="cp-state-full"' if wide else '')+'><span>'+label+'</span><input type="'+kind+'" name="'+name+'" value="'+esc(value)+'" '+extra+'></label>'
    def day(label,name,value=today):return field(label+' <em>*</em>',name,value,'date',f'max="{today}" required')
    def note(value=''):return '<label class="cp-state-full"><span>Not</span><textarea name="notes" rows="3" maxlength="1000" placeholder="İsteğe bağlı">'+esc(value)+'</textarea></label>'
    def form(action,fields,submit='Kaydet'):
        return '<form class="cp-state-form" method="post" action="'+action+'">'+fields+'<footer class="cp-state-form-foot"><button class="cp-state-save" type="submit">'+esc(submit)+'</button></footer></form>'
    def message(text,action,label):
        return '<div class="cp-state-message"><p>'+esc(text)+'</p><a class="cp-state-save" data-cp-state-step href="'+esc(url(action))+'">'+esc(label)+'</a></div>'
    if not event:
        links=''
        for key,label,detail,glyph,tone in options:
            target=('/'+source+'-edit?'+urlencode({'id':sid,'focus':'notes'})) if key=='note' else ('/health?'+urlencode({'app_action':'add','subject':source+':'+str(sid),'search':animal['tag']})) if key=='health' else url(key)
            links+='<a class="cp-state-choice" '+('data-cp-state-step ' if key not in ('note','health') else '')+'href="'+esc(target)+'"><span class="cp-state-icon cp-state-'+tone+'">'+icon(glyph)+'</span><span><b>'+label+'</b><small>'+detail+'</small></span>'+ref.glyph('chevron')+'</a>'
        body='<nav class="cp-state-choices" aria-label="Eklenecek durum veya işlem">'+links+'</nav>'
    elif event in ('heat','inseminated') and pregnant:
        body='<div class="cp-state-message"><p>Bu hayvanın aktif gebelik kaydı var. Yeni kızgınlık veya tohumlama kaydından önce mevcut gebelik sonucunu kontrol et.</p><a class="cp-state-save" href="/reproduction-center?animal='+str(sid)+'">Gebelik kaydını aç</a></div>'
    elif event=='heat':
        body=form('/estrus',hidden+day('Kızgınlık Tarihi','estrus_date')+field('Gözlenen Belirtiler','signs',extra='maxlength="500" placeholder="Örn. hareketlilik, atlama"')+note(),'Kızgınlık Kaydı Ekle')
    elif event=='inseminated':
        body=form('/inseminations',hidden+day('Tohumlama Tarihi','insemination_date')+field('Baba Küpe / Boğa No','bull_tag',extra='maxlength="80"')+field('Boğa Adı','bull_name',extra='maxlength="120"')+field('Tohumlayan','inseminator',extra='maxlength="120" placeholder="Veteriner / teknisyen"')+'<p class="cp-state-hint cp-state-full">Kayıt kontrol bekliyor durumunda açılır. Gebelik sonucu daha sonra eklenir.</p>','Tohumlama Kaydı Ekle')
    elif event in ('pregnant','empty'):
        if not latest or str(latest['pregnancy_result'] or '') in ('Doğum','Abort','Atık'):
            body=message('Sonucu güncellenecek açık bir tohumlama kaydı yok. Önce gerçek tohumlama tarihini kaydet.','inseminated','Tohumlama Kaydı Ekle')
        else:
            result='Pozitif' if event=='pregnant' else 'Negatif'
            fields=f'<input type="hidden" name="id" value="{latest["id"]}"><input type="hidden" name="pregnancy_result" value="{result}"><input type="hidden" name="return_to" value="/reproduction-center?animal={sid}">'
            fields+='<div class="cp-state-result cp-state-full"><span>Tohumlama Tarihi</span><b>'+esc(ns['fmt_date'](latest['insemination_date']))+'</b><span>Kaydedilecek Sonuç</span><b>'+('Gebe' if event=='pregnant' else 'Gebe Değil')+'</b></div><p class="cp-state-hint cp-state-full">Yalnız bu hayvanın son tohumlama sonucu güncellenir.</p>'
            body=form('/reproduction-status',fields,'Gebelik Sonucunu Kaydet')
    elif event in ('lactating','dry','heifer'):
        fields=hidden+f'<input type="hidden" name="single" value="{sid}"><input type="hidden" name="status" value="{event}">'+day('Durum Tarihi','effective_date')
        if event=='lactating':
            fields+=field('Laktasyon Başlangıcı <small>İsteğe bağlı</small>','lactation_start',state.get('lactation_start') or '','date',f'max="{today}"')+field('Laktasyon Sırası <small>İsteğe bağlı</small>','lactation_number',state.get('lactation_number') or '','number','min="1" max="99" step="1"')+'<p class="cp-state-hint cp-state-full">Başlangıç bilinmiyorsa boş bırakabilirsin; sağım günü tahmin edilmez.</p>'
        body=form('/dairy-status/save',fields+note(),('Kuruya Çıkışı Kaydet' if event=='dry' else 'Durumu Kaydet'))
    elif event=='birth':
        fields=f'<input type="hidden" name="mother_id" value="{sid}"><input type="hidden" name="arrival_source" value="Çiftlikte Doğdu"><input type="hidden" name="purpose" value="Damızlık"><input type="hidden" name="paddock_id" value="{animal.get("paddock_id") or ""}">'
        fields+=day('Doğum Tarihi','birth_date')+field('Buzağı Küpe No <em>*</em>','tag',extra='required maxlength="30" placeholder="TR ile başlayan küpe numarası"')+'<label><span>Cinsiyet <em>*</em></span><select name="gender" required><option value="">Seçiniz</option><option>Dişi</option><option>Erkek</option></select></label>'+field('Irk <em>*</em>','breed',animal.get('breed') or '',extra='required maxlength="120"')+field('Adı / Takip No','nickname',extra='maxlength="120"')+field('Baba Küpe No','father_tag',latest['bull_tag'] if latest else '',extra='maxlength="80"')+note()
        body=form('/animal-add',fields,'Doğum Bilgisi Ekle')
    elif event=='weight':
        body=form('/'+source+'/weight',hidden+day('Ölçüm Tarihi','measure_date')+field('Canlı Ağırlık (kg) <em>*</em>','weight',kind='number',extra='required min="0.1" step="0.1" placeholder="0,0"')+note(),'Kilo Ölçümü Ekle')
    else:
        raise ValueError('Bu işlem ilgili kayıt ekranından açılır.')
    return '<section class="cp-state-content" lang="tr" data-cp-state-content data-cp-state-event="'+esc(event)+'"><div class="cp-state-handle" aria-hidden="true"></div>'+header+context+'<div class="cp-state-body">'+body+'</div></section>'


def install(ns):
    app=ns['App'];original_get=app.do_GET
    def do_GET(self):
        if urlparse(self.path).path!='/animal-events':return original_get(self)
        if not self.require():return
        allowed,_,message=ns['license_status']()
        if not allowed:return self.redirect('/license',message)
        query=parse_qs(urlparse(self.path).query)
        try:body=markup(ns,query)
        except ValueError as exc:return self.send_html(esc(str(exc)),400)
        if query.get('fragment')==['1']:return self.send_html(body)
        return self.send_html(ns['page']('Durum Ekle',body,'/animal-events',self.user()['username'],(query.get('msg') or [''])[0]))
    app.do_GET=do_GET
