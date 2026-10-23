"""Responsive, server-rendered views for the shared health workspace."""
import calendar
import json
import secrets
from datetime import date, timedelta
from urllib.parse import urlencode

import health_center as hc
import reproduction_sync as sync

esc=hc.esc


def value(query,key,default=''):
    return (query.get(key) or [default])[0]


def link(query=None,**changes):
    params={k:v[0] for k,v in (query or {}).items() if k not in ('msg','new','edit','case_edit','app_action','page')}
    params.update(changes)
    return '/health?'+urlencode({k:v for k,v in params.items() if v is not None and v!=''})


def hidden(name,value):
    return f'<input type="hidden" name="{esc(name)}" value="{esc(value)}">'


def action_form(token,act,label,**fields):
    confirm=fields.pop('confirm','')
    back=fields.pop('return_to','/health')
    return '<form method="post" action="/health-center/action" class="hc-inline"'+(f' data-hc-confirm="{esc(confirm)}"' if confirm else '')+'>'+hidden('csrf',token)+hidden('action',act)+hidden('return_to',back)+''.join(hidden(k,v) for k,v in fields.items())+f'<button class="hc-text-button" type="submit">{esc(label)}</button></form>'


def empty(title,description='',button=''):
    return '<div class="hc-empty">'+hc.icon('heart')+f'<b>{esc(title)}</b>'+(f'<p>{esc(description)}</p>' if description else '')+button+'</div>'


def status_badge(state):
    return '<span class="hc-badge hc-badge-'+state+'">'+{'today':'Bugün','overdue':'Gecikti','upcoming':'Planlandı','done':'Yapıldı'}[state]+'</span>'


def task_rows(ns,rows,token,query):
    content=''
    for r in rows:
        category=r['category'];label,ico,tone=hc.CATEGORIES[category]
        date_text=ns['fmt_date'](r['date'])+(' · '+r['time'] if r.get('time') else '')
        if r['source']=='course':
            control=f'<button class="hc-done" type="button" data-hc-complete="{r["id"]}" data-hc-title="{esc(r["title"])}" data-hc-subject="{esc(r["subject"])}">Yapıldı</button>'
            menu='<details class="hc-more"><summary aria-label="İşlem seçenekleri">···</summary><div><a href="'+esc(r['edit_url'])+'">Programı düzenle</a>'+action_form(token,'pause','Programı duraklat',course_id=r['course_id'],return_to=link(query),confirm='Bu programın tüm bekleyen işlemleri duraklatılsın mı?')+'</div></details>'
        elif r['source']=='sync':
            control='<a class="hc-done" href="'+esc(r['url'])+'">Adımı aç</a>';menu=''
        elif r['source']=='legacy':
            control='<form class="hc-inline" method="post" action="/health/plan-done">'+hidden('source_id',r['id'])+hidden('return_to',link(query))+'<button class="hc-done" type="submit">Bugün yapıldı</button></form>'
            menu='<a class="hc-small-link" href="'+esc(r['edit_url'])+'">Düzenle</a>'
        else:
            control='<form class="hc-inline" method="post" action="/pregnancy-vaccine/done">'+hidden('animal_id',r['animal_id'])+hidden('insemination_id',r['id'])+hidden('month',r['month'])+hidden('return_to',link(query))+'<button class="hc-done" type="submit">Bugün yapıldı</button></form>';menu=''
        content+=f'''<article class="hc-task" id="health-task-{r['id']}" data-hc-task data-health-course="{r.get('course_id','')}" data-health-plan-ref="{esc(r.get('plan_ref',''))}" data-category="{category}" data-date="{esc(r['date'])}">
          <div class="hc-task-main"><span class="hc-icon hc-{tone}">{hc.icon(ico)}</span><div><b>{esc(r['title'])}</b><small>{esc(label)} · {esc(r['detail'])}</small></div></div>
          <div class="hc-task-subject"><b>{esc(r['subject'])}</b><small>{esc(r.get('nickname') or r.get('paddock') or 'Padoksuz')}</small></div>
          <div class="hc-task-date">{esc(date_text)}</div><div class="hc-task-status">{status_badge(r['state'])}</div><div class="hc-task-actions">{control}{menu}</div></article>'''
    return '<div class="hc-task-head"><span>İşlem</span><span>Hayvan / Grup</span><span>Tarih</span><span>Durum</span><span>İşlem</span></div><div class="hc-task-list">'+content+'</div>' if rows else empty('Bu görünümde planlı işlem yok.','Yeni bir sağlık işlemi ekleyebilir veya filtreleri değiştirebilirsin.')


def history_rows(ns,rows,token,query):
    content=''
    for r in rows:
        label,ico,tone=hc.CATEGORIES[r['category']]
        remove=action_form(token,'delete_record','Uygulamayı geri al',health_id=r['id'],return_to=link(query),confirm='Uygulama ve bağlı gider silinip işlem yeniden beklemeye alınsın mı?') if r['program_record'] else '' if r['linked'] else '<form method="post" action="/health-delete" class="hc-inline" data-hc-confirm="Bu uygulama ve ona bağlı gider kaydı silinsin mi?">'+hidden('id',r['id'])+'<button class="hc-danger-link" type="submit">Sil</button></form>'
        content+=f'''<article class="hc-history"><span class="hc-icon hc-{tone}">{hc.icon(ico)}</span><div class="hc-history-title"><b>{esc(r['title'])}</b><small>{esc(r['subject'])}{(' · '+esc(r['nickname'])) if r['nickname'] else ''}</small></div><div class="hc-history-date"><b>{esc(ns['fmt_date'](r['date']))}</b><small>{esc(r['date_label'])}</small></div><span class="hc-history-cost">{esc(ns['money'](r['cost']))}</span><details class="hc-more"><summary aria-label="Uygulama seçenekleri">···</summary><div><a href="{esc(r['edit_url'])}">{'Detay / Düzenle' if r['linked'] else 'Düzenle'}</a>{remove}</div></details></article>'''
    return '<div class="hc-history-list">'+content+'</div>' if rows else empty('Henüz uygulama kaydı yok.','Yapılan işlemler burada ve hayvanın sağlık geçmişinde görünür.')


def picker(subjects,selected=None,locked=False):
    selected=set(selected or []);paddocks=sorted({(a['paddock_id'],a['paddock']) for a in subjects if a['paddock_id']},key=lambda p:hc.norm(p[1]))
    options='<option value="">Tüm padoklar</option>'+''.join(f'<option value="{esc(key)}">{esc(name)}</option>' for key,name in paddocks)
    rows=''
    for a in subjects:
        checked=' checked' if a['ref'] in selected else ''
        disabled=' disabled' if locked else ''
        rows+=f'<label class="hc-animal-option" data-search="{esc(hc.norm(a["tag"]+" "+a["nickname"]+" "+a["paddock"]))}" data-paddock="{esc(a["paddock_id"])}" data-gender="{esc(a["gender"])}"><input type="checkbox" value="{a["ref"]}"{checked}{disabled}><span><b>{esc(a["tag"])}</b><small>{esc(a["nickname"] or ("Buzağı" if a["source"]=="calf" else a["gender"]))} · {esc(a["paddock"])}</small></span></label>'
    return f'''<fieldset class="hc-picker" data-hc-picker><legend>Uygulama yapılacak hayvanlar <b data-hc-selected>{len(selected)} seçili</b></legend>
      {hidden('subjects_json',json.dumps(list(selected)))}<div class="hc-picker-filters"><input type="search" data-hc-animal-search placeholder="Küpe, ad veya padok ara" aria-label="Hayvan ara"><select data-hc-paddock aria-label="Padok">{options}</select><select data-hc-gender aria-label="Cinsiyet"><option value="">Tüm cinsiyetler</option><option>Dişi</option><option>Erkek</option></select></div>
      {('<p class="hc-note">Uygulaması kayıtlı hayvan seçimi korunur.</p>' if locked else '<div class="hc-picker-tools"><button type="button" data-hc-select-visible>Görünenleri seç</button><button type="button" data-hc-clear>Seçimi temizle</button></div>')}
      <div class="hc-animal-options">{rows or '<p class="hc-note">Aktif hayvan bulunamadı.</p>'}</div><p class="hc-note" data-hc-picker-empty hidden>Bu filtrede hayvan yok.</p></fieldset>'''


def dialog_head(title,small='SAĞLIK YÖNETİMİ'):
    return '<header class="hc-dialog-head"><div><small>'+esc(small)+'</small><h2>'+esc(title)+'</h2></div><button type="button" class="hc-close" data-hc-close aria-label="Kapat">×</button></header>'


def program_dialog(c,subjects,query,token):
    pid=value(query,'edit');p={};selected=[];completed=False
    if pid:
        row=c.execute('''select hc.*,m.category,m.repeat_value,m.repeat_unit,m.rapel_days,m.revision,m.schedule_mode from health_courses hc
            join health_program_meta m on m.course_id=hc.id where hc.id=?''',(hc.integer(pid,'Program',1,2147483647),)).fetchone()
        if not row:raise ValueError('Program bulunamadı.')
        p=dict(row)
        selected=[('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id']) for r in c.execute('select distinct animal_id,calf_id from health_tasks where course_id=?',(pid,))]
        completed=bool(c.execute("select 1 from health_tasks where course_id=? and status in ('Tamamlandı','Yapıldı') limit 1",(pid,)).fetchone())
    if not p and value(query,'subject'):selected=[value(query,'subject')]
    category=p.get('category') or (value(query,'category') if value(query,'category') in hc.KINDS else 'vaccine')
    options=''.join(f'<option value="{key}" {"selected" if category==key else ""}>{esc(val[0])}</option>' for key,val in hc.CATEGORIES.items() if key in hc.KINDS)
    definitions={key:[r[0] for r in c.execute('select name from health_definitions where category=? order by name',(key,))] for key in hc.KINDS}
    for r in c.execute('select distinct kind,product from health_courses where coalesce(product,\'\')<>\'\''):
        cat=hc.category_for(r['kind'],r['product'])
        if cat in definitions and r['product'] not in definitions[cat]:definitions[cat].append(r['product'])
    payload=json.dumps(definitions,ensure_ascii=False).replace('<','\\u003c')
    fixed=' disabled' if completed else ''
    fixed_fields=''.join(hidden(k,v) for k,v in {'category':category,'start_date':p.get('start_date',''),'repeat_value':p.get('repeat_value',0),'repeat_unit':p.get('repeat_unit','months'),'rapel':'yes' if p.get('rapel_days') else 'no','rapel_days':p.get('rapel_days',0),'schedule_mode':p.get('schedule_mode','repeat'),'treatment_days':p.get('treatment_days',1),'treatment_interval_days':p.get('treatment_interval_days',1),'times_per_day':p.get('times_per_day',1)}.items()) if completed else ''
    date_value=p.get('start_date',hc.today().isoformat())
    return f'''<dialog id="hcProgram" class="hc-dialog" {'data-hc-auto' if pid else ''}>{dialog_head('Sağlık Programını Düzenle' if p else 'Sağlık İşlemi Ekle')}
      <form method="post" action="/health-center/program" class="hc-form" data-hc-program>
      {hidden('csrf',token)}{hidden('id',p.get('id',''))}{hidden('revision',p.get('revision',''))}{hidden('request_key',secrets.token_urlsafe(24))}{hidden('return_to',link(query))}{fixed_fields}
      <div class="hc-form-grid"><label>Kategori *<select name="category" id="hcProgramCategory"{fixed}>{options}</select></label><label>Kayıt türü<select name="mode" {'disabled' if p else ''}><option value="plan">Plan oluştur</option><option value="record">Yapılan uygulamayı kaydet</option></select></label>
      <label class="hc-full">Ürün / işlem adı *<input name="product" id="hcProduct" list="hcDefinitions" value="{esc(p.get('product',''))}" required maxlength="150" placeholder="Listeden seç veya yeni bir ad yaz" autocomplete="off"><datalist id="hcDefinitions"></datalist></label>
      <label>İlk uygulama tarihi *<input type="date" name="start_date" value="{esc(date_value)}" required{fixed}></label><label>Hayvan başı uygulama tutarı (₺)<input type="number" name="cost" step="0.01" min="0" max="10000000" inputmode="decimal" value="{p.get('cost_per_application',0):g}"></label>
      <div class="hc-full hc-course-fields" data-hc-treatment-options {'' if category=='treatment' else 'hidden'}><label>Plan düzeni<select name="schedule_mode" data-hc-schedule-mode{fixed}><option value="repeat">Tekli / tekrarlı uygulama</option><option value="course" {'selected' if p.get('schedule_mode')=='course' else ''}>Çok günlük tedavi planı</option></select></label><div class="hc-treatment-grid" data-hc-course {'' if p.get('schedule_mode')=='course' else 'hidden'}><label>Kaç Uygulama Günü?<input type="number" name="treatment_days" min="1" max="60" value="{p.get('treatment_days',1)}"{fixed}></label><label>Kaç Günde Bir?<input type="number" name="treatment_interval_days" min="1" max="365" value="{p.get('treatment_interval_days',1)}"{fixed}></label><label>Günde kaç uygulama?<input type="number" name="times_per_day" min="1" max="6" value="{p.get('times_per_day',1)}"{fixed}></label></div></div><div class="hc-full hc-repeat-fields" data-hc-repeat-fields><label>Tekrar aralığı<input type="number" name="repeat_value" min="0" max="3650" value="{p.get('repeat_value',0)}"{fixed}></label><label>Birim<select name="repeat_unit"{fixed}><option value="days" {'selected' if p.get('repeat_unit')=='days' else ''}>Gün</option><option value="months" {'selected' if p.get('repeat_unit','months')=='months' else ''}>Ay</option></select></label><small>0 = tek sefer. Sonraki tekrar, gerçek uygulama tarihinden hesaplanır.</small></div>
      <div class="hc-full hc-rapel-grid" data-hc-rapel-group><label>Rapel var mı?<select name="rapel" data-hc-rapel{fixed}><option value="no">Hayır</option><option value="yes" {'selected' if p.get('rapel_days') else ''}>Evet</option></select></label><label data-hc-rapel-days {'hidden' if not p.get('rapel_days') else ''}>Rapel kaç gün sonra?<input type="number" name="rapel_days" min="1" max="365" value="{p.get('rapel_days') or ''}" placeholder="Gün sayısı"{fixed}></label></div></div>
      {picker(subjects,selected,completed)}
      <label>Açıklama<textarea name="notes" rows="2" maxlength="2000" placeholder="Uygulama veya veteriner planı notu">{esc(p.get('notes',''))}</textarea></label>
      <p class="hc-note">Plan oluşturmak uygulama veya gider kaydı oluşturmaz. Uygulama tamamlandığında hayvanın sağlık geçmişine işlenir.</p>
      <p class="hc-form-error" role="alert" hidden></p><footer class="hc-dialog-footer"><button type="button" class="hc-secondary" data-hc-close>Vazgeç</button><button class="hc-primary" type="submit">{'Değişiklikleri Kaydet' if p else 'Kaydet'}</button></footer></form><script type="application/json" id="hcDefinitionsData">{payload}</script></dialog>'''


def case_dialog(c,subjects,query,token):
    cid=value(query,'case_edit');p={};selected=[]
    if cid:
        row=c.execute('select * from health_cases where id=?',(hc.integer(cid,'Hastalık kaydı',1,2147483647),)).fetchone()
        if not row:raise ValueError('Hastalık kaydı bulunamadı.')
        p=dict(row)
        selected=[('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id']) for r in c.execute('select * from health_case_targets where case_id=?',(cid,))]
    if not p and value(query,'subject'):selected=[value(query,'subject')]
    diseases=''.join(f'<option value="{esc(r[0])}"></option>' for r in c.execute('select name from disease_catalog where active=1 order by name'))
    return f'''<dialog id="hcCase" class="hc-dialog" {'data-hc-auto' if cid else ''}>{dialog_head('Hastalık Kaydını Düzenle' if p else 'Hasta Hayvan Kaydet')}
      <form method="post" action="/health-center/case" class="hc-form">
      {hidden('csrf',token)}{hidden('id',p.get('id',''))}{hidden('revision',p.get('revision',''))}{hidden('request_key',secrets.token_urlsafe(24))}{hidden('return_to',link(query))}
      <div class="hc-form-grid"><label>Hastalık tarihi *<input type="date" name="illness_date" max="{hc.today().isoformat()}" value="{p.get('illness_date',hc.today().isoformat())}" required></label><label>Veteriner hekim<input name="veterinarian" value="{esc(p.get('veterinarian',''))}" maxlength="150" placeholder="İsteğe bağlı"></label>
      <label class="hc-full">Hastalık / belirti *<input name="diagnosis" value="{esc(p.get('diagnosis',''))}" list="hcDiseaseNames" required maxlength="150" placeholder="Listeden seç veya açıklama yaz"><datalist id="hcDiseaseNames">{diseases}</datalist></label>
      <label>Toplam veteriner tutarı (₺)<input name="vet_cost" type="number" min="0" step="0.01" max="10000000" value="{p.get('vet_cents',0)/100:g}" inputmode="decimal"></label><label>Harici ilaç / tedavi tutarı (₺)<input name="medicine_cost" type="number" min="0" step="0.01" max="10000000" value="{p.get('medicine_cents',0)/100:g}" inputmode="decimal"></label></div>
      <p class="hc-note">Tutarlar isteğe bağlıdır ve seçilen hayvanlara eşit dağıtılır. Stoktan kullanılan ilaçları İlaç Stoku bölümündeki Tedavi Kaydı ile kaydedebilirsin.</p>
      {picker(subjects,selected,bool(p))}<label>Tedavi / takip notu<textarea name="treatment_note" rows="2" maxlength="2000" placeholder="Veterinerin belirlediği tedavi ve takip notu">{esc(p.get('treatment_note',''))}</textarea></label>
      <label>Açıklama<textarea name="notes" rows="2" maxlength="2000" placeholder="İsteğe bağlı">{esc(p.get('notes',''))}</textarea></label><p class="hc-form-error" role="alert" hidden></p>
      <footer class="hc-dialog-footer"><button type="button" class="hc-secondary" data-hc-close>Vazgeç</button><button class="hc-primary" type="submit">{'Değişiklikleri Kaydet' if p else 'Hasta Hayvan Kaydet'}</button></footer></form></dialog>'''


def dialogs(c,subjects,query,token):
    chooser=''.join(f'<button type="button" class="hc-choice" data-hc-choice="{key}"><span class="hc-icon hc-{tone}">{hc.icon(ico)}</span><span><b>{esc(label)}</b><small>{"Program ve uygulama kaydı" if key not in ("treatment","sync") else "Hastalık, muayene ve takip" if key=="treatment" else "Program ve hayvan seçimi"}</small></span><span>›</span></button>' for key,(label,ico,tone) in hc.CATEGORIES.items())
    complete=f'''<dialog id="hcComplete" class="hc-dialog hc-dialog-small">{dialog_head('Uygulamayı Kaydet')}<form method="post" action="/health-center/action" class="hc-form">{hidden('csrf',token)}{hidden('action','complete')}{hidden('task_id','')}{hidden('return_to',link(query))}<p class="hc-complete-label"></p><label>Gerçek uygulama tarihi *<input name="actual_date" type="date" max="{hc.today().isoformat()}" value="{hc.today().isoformat()}" required></label><p class="hc-note">Yalnız bu hayvanın seçilen uygulaması tamamlanır.</p><footer class="hc-dialog-footer"><button type="button" class="hc-secondary" data-hc-close>Vazgeç</button><button type="submit" class="hc-primary">Yapıldı Olarak Kaydet</button></footer></form></dialog>'''
    return '<dialog id="hcChooser" class="hc-dialog hc-dialog-small">'+dialog_head('Sağlık İşlemi Ekle')+'<div class="hc-choices">'+chooser+'</div></dialog>'+program_dialog(c,subjects,{k:v for k,v in query.items() if k!='edit'} if value(query,'category')=='sync' else query,token)+case_dialog(c,subjects,query,token)+complete



def record_dialog(c,query,token):
    hid=value(query,'record_edit')
    if not hid:return ''
    r=c.execute('select h.* from health h join health_program_meta m on m.course_id=h.course_id where h.id=?',(hc.integer(hid,'Uygulama',1,2147483647),)).fetchone()
    if not r:raise ValueError('Uygulama bulunamadı.')
    return f'''<dialog id="hcRecord" class="hc-dialog hc-dialog-small" data-hc-auto>{dialog_head('Uygulamayı Düzenle')}<form class="hc-form" method="post" action="/health-center/record">{hidden('csrf',token)}{hidden('id',r['id'])}{hidden('return_to','/health?tab=done')}<label>İşlem adı *<input name="product" maxlength="150" required value="{esc(r['product'])}"></label><label>Uygulama tarihi<input type="date" name="applied_date" value="{esc(r['applied_date'])}" readonly></label><p class="hc-note">Tarih düzeltmesi için uygulamayı geri alıp doğru tarihle yeniden kaydet.</p><label>Tutar (₺)<input name="cost" type="number" min="0" max="10000000" step="0.01" value="{float(r['cost'] or 0):g}"></label><label>Açıklama<textarea name="notes" maxlength="2000" rows="3">{esc(r['notes'])}</textarea></label><footer class="hc-dialog-footer"><button type="button" class="hc-secondary" data-hc-close>Vazgeç</button><button class="hc-primary" type="submit">Kaydet</button></footer></form></dialog>'''

def cases_markup(ns,data,token,query,overview=False):
    state=value(query,'case_status','active');term=hc.norm(value(query,'search'))
    cases=[r for r in data['cases'] if (r['status']=='active' if overview else state=='all' or r['status']==state) and (not term or hc.search_matches(term,r['search']))]
    body=''
    for r in cases[:4] if overview else cases:
        back=link(query);cid=r['id'];active=r['status']=='active'
        button=action_form(token,'close_case' if active else 'reopen_case','İyileşti' if active else 'Yeniden aç',case_id=cid,return_to=back)
        remove=action_form(token,'delete_case','Sil',case_id=cid,return_to=back,confirm='Hastalık kaydı ve bu kayda ait giderler silinsin mi? Diğer tedavi kayıtları korunur.')
        body+=f'''<article class="hc-patient"><span class="hc-icon hc-red">{hc.icon('heart')}</span><div class="hc-patient-body"><div class="hc-patient-title"><b>{esc(r['diagnosis'])}</b><span class="hc-badge {'hc-badge-today' if active else 'hc-badge-done'}">{'Takipte' if active else 'İyileşti'}</span></div><small>{esc(r['tags'])}</small><small>{esc(ns['fmt_date'](r['illness_date']))}{(' · '+esc(r['veterinarian'])) if r['veterinarian'] else ''}</small>{('<p>'+esc(r['treatment_note'])+'</p>') if r['treatment_note'] else ''}<div class="hc-patient-actions"><a href="{esc(link(query,category='treatment',case_edit=cid))}">Detay / Düzenle</a>{button}<details class="hc-more"><summary aria-label="Hastalık seçenekleri">···</summary><div>{remove}</div></details></div></div></article>'''
    for r in data['treatments'][:2] if overview else data['treatments']:
        body+=f'<article class="hc-patient"><span class="hc-icon hc-red">{hc.icon("treatment")}</span><div class="hc-patient-body"><b>{esc(r["diagnosis"] or r["product_name"] or "İlaç tedavisi")}</b><small>{esc(r["adult_tag"] or r["calf_tag"])} · {esc(r["product_name"])}</small><small>İlaç tedavisi · {esc(ns["fmt_date"](r["start_date"]))}</small><div class="hc-patient-actions"><a href="/treatment-edit?id={r["id"]}">Tedavi detayları</a></div></div></article>'
    if not body:body=empty('Aktif hasta hayvan bulunmuyor.' if state=='active' else 'Bu görünümde hastalık kaydı yok.')
    heading=f'<header class="hc-section-head"><h2>Hasta Hayvanlar <span>{data["patient_count"]}</span></h2>'+(f'<a href="{esc(link(category="treatment"))}">Tümünü gör ›</a>' if overview else '<div class="hc-patient-add"><button class="hc-text-button" type="button" data-hc-program-category="treatment">Takip Planı</button><button class="hc-text-button" type="button" data-hc-open="hcCase">+ Hasta Kaydet</button></div>')+'</header>'
    tabs='' if overview else '<nav class="hc-tabs">'+''.join(f'<a class="{"active" if key==state else ""}" href="{esc(link(query,case_status=key))}">{label}</a>' for key,label in [('active','Aktif'),('closed','İyileşenler'),('all','Tümü')])+'</nav>'
    return '<section class="hc-panel">'+heading+tabs+'<div class="hc-patients">'+body+'</div></section>'


def program_cards(ns,c,query,token):
    category=value(query,'category','general');term=hc.norm(value(query,'search'));cards=''
    for raw in c.execute('''select hc.*,m.category,m.repeat_value,m.repeat_unit,m.rapel_days,
        (select count(*) from health_tasks t where t.course_id=hc.id and t.status='Bekliyor') pending_count,
        (select count(*) from health_tasks t where t.course_id=hc.id and t.status in ('Tamamlandı','Yapıldı')) done_count,
        (select min(planned_date) from health_tasks t where t.course_id=hc.id and t.status='Bekliyor') next_date
        from health_courses hc left join health_program_meta m on m.course_id=hc.id order by hc.id desc'''):
        r=dict(raw);cat=hc.category_for(r['kind'],r['product'],r['category'])
        if category not in ('general',cat):continue
        tags=[x[0] or x[1] or '' for x in c.execute('''select distinct a.tag,ca.tag from health_tasks t
            left join animals a on a.id=t.animal_id left join calves ca on ca.id=t.calf_id where course_id=?''',(r['id'],))]
        if not tags:continue
        if term and not hc.search_matches(term,r['product'],' '.join(tags)):continue
        edit=link(query,edit=r['id']) if r['category'] else '/health-plan-edit?id='+str(r['id'])
        controls=action_form(token,'pause' if r['active'] else 'resume','Duraklat' if r['active'] else 'Devam et',course_id=r['id'],return_to=link(query))
        controls+=action_form(token,'delete_program','Programı kaldır',course_id=r['id'],return_to=link(query),confirm='Bekleyen işlemler kaldırılsın mı? Yapılan uygulamalar geçmişte korunur.')
        repeat=(f'Her {r["repeat_value"]} '+('günde' if r['repeat_unit']=='days' else 'ayda')+' bir') if r['repeat_value'] else 'Tek sefer'
        schedule=repeat+(' · '+str(r['rapel_days'])+' gün sonra rapel' if r['rapel_days'] else '')
        if r['kind']=='İlaç' and (r['treatment_days']>1 or r['times_per_day']>1):
            schedule=f"{r['treatment_days']} uygulama günü · {r['treatment_interval_days']} günde bir · günde {r['times_per_day']} uygulama"
        cards+=f'''<article class="hc-program-card"><div><b>{esc(r['product'])}</b><span class="hc-badge {'hc-badge-done' if r['active'] else 'hc-badge-upcoming'}">{'Aktif' if r['active'] else 'Duraklatıldı'}</span></div><small>{len(tags)} hayvan · {esc(schedule if r['category'] or r['kind']=='İlaç' else 'Önceki sağlık programı')}</small><p>{esc(' · '.join(tags))}</p><small>{r['pending_count']} bekleyen · {r['done_count']} yapılan{(' · Sıradaki '+esc(ns['fmt_date'](r['next_date']))) if r['next_date'] else ''}</small><footer><a href="{esc(edit)}">Düzenle</a><details class="hc-more"><summary aria-label="Program seçenekleri">···</summary><div>{controls}</div></details></footer></article>'''
    return '<details class="hc-programs"><summary>Kayıtlı Programlar</summary><div class="hc-program-grid">'+(cards or '<p class="hc-note">Henüz kayıtlı program yok.</p>')+'</div></details>'


def calendar_markup(ns,data,query,token):
    raw=value(query,'month',hc.today().strftime('%Y-%m'))
    try:
        first=date.fromisoformat(raw+'-01')
        if not 1900<=first.year<=2200:raise ValueError()
    except ValueError:raise ValueError('Takvim ayı geçersiz.')
    selected=value(query,'date',hc.today().isoformat() if first.strftime('%Y-%m')==hc.today().strftime('%Y-%m') else first.isoformat())
    selected_day=hc.day(selected)
    if selected_day.strftime('%Y-%m')!=first.strftime('%Y-%m'):selected_day=first
    selected=selected_day.isoformat()
    months=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    category=value(query,'category','general');term=hc.norm(value(query,'search'))
    pending=[r for r in data['pending'] if category in ('general',r['category']) and (not term or hc.search_matches(term,r['search']))]
    history=[r for r in data['history'] if category in ('general',r['category']) and (not term or hc.search_matches(term,r['search']))]
    markers={}
    for r in pending:markers.setdefault(r['date'],set()).add(r['category'])
    for r in history:markers.setdefault(r['date'],set()).add('done')
    cells=''.join('<span class="hc-calendar-blank"></span>' for _ in range(first.weekday()))
    for number in range(1,calendar.monthrange(first.year,first.month)[1]+1):
        current=first.replace(day=number).isoformat();dots=''.join('<i class="hc-dot hc-dot-'+cat+'"></i>' for cat in sorted(markers.get(current,[])))
        cells+=f'<a class="hc-calendar-day {"selected" if current==selected else ""} {"today" if current==hc.today().isoformat() else ""}" href="{esc(link(query,date=current,month=first.strftime("%Y-%m")))}" aria-label="{number} {months[first.month-1]} · {len([r for r in pending if r["date"]==current])} planlı işlem" {"aria-current=date" if current==selected else ""}><b>{number}</b><span>{dots}</span></a>'
    previous=hc.add_interval(first,-1,'months').strftime('%Y-%m');following=hc.add_interval(first,1,'months').strftime('%Y-%m')
    nav=f'<div class="hc-calendar-nav"><a href="{esc(link(query,month=previous,date=""))}" aria-label="Önceki ay">‹</a><h3>{months[first.month-1]} {first.year}</h3><a href="{esc(link(query,month=following,date=""))}" aria-label="Sonraki ay">›</a></div>'
    grid='<div class="hc-calendar-grid">'+''.join('<span class="hc-weekday">'+d+'</span>' for d in ['Pt','Sa','Ça','Pe','Cu','Ct','Pa'])+cells+'</div>'
    rows=[r for r in pending if r['date']==selected];done=[r for r in history if r['date']==selected]
    daybody=task_rows(ns,rows,token,query)
    if done:daybody+='<h3 class="hc-calendar-done-title">Yapılan Uygulamalar</h3>'+history_rows(ns,done,token,query)
    return '<div class="hc-calendar-layout"><section class="hc-calendar-month">'+nav+grid+'<p class="hc-note">Renkli noktalar planları, yeşil nokta geçmiş kayıtları gösterir.</p></section><section class="hc-calendar-detail"><h3>'+esc(ns['fmt_date'](selected))+' · Günün İşlemleri</h3>'+daybody+'</section></div>'


def markup(ns,c,query,token):
    category=value(query,'category','general')
    if category not in ('general',*hc.CATEGORIES):category='general'
    query=dict(query);query['category']=[category]
    data=hc.workspace_data(ns,c);term=hc.norm(value(query,'search'));filt=value(query,'filter','all');tab=value(query,'tab','planned');view=value(query,'view','agenda')
    if filt=='history':tab='done'
    if filt not in ('all','today','overdue','upcoming','history'):filt='all'
    scoped=[r for r in data['pending'] if category in ('general',r['category']) and (not term or hc.search_matches(term,r['search']))]
    focused_plan=value(query,'plan') if category!='sync' else ''
    if focused_plan:
        plan_id=hc.integer(focused_plan,'Program',1,2147483647)
        scoped=[r for r in scoped if r.get('course_id')==plan_id]
        if value(query,'task'):scoped=[r for r in scoped if r.get('plan_ref')==value(query,'task')]

    counts={state:sum(r['state']==state and (state!='upcoming' or r['date']<=(hc.today()+timedelta(days=30)).isoformat()) for r in scoped) for state in ('today','overdue','upcoming')}
    kpis=''
    for state,label,ico,tone in [('today','Bugün','calendar','blue'),('overdue','Geciken','alert','red'),('upcoming','Yaklaşan','clock','orange'),('patients','Tedavide','heart','green')]:
        count=data['patient_count'] if state=='patients' else counts[state]
        target=link(category='treatment') if state=='patients' else link(query,filter=state,view='agenda',tab='planned',plan='')
        kpis+=f'<a class="hc-kpi hc-{tone} {"active" if filt==state else ""}" href="{esc(target)}"><span class="hc-icon">{hc.icon(ico)}</span><div><small>{label}</small><b>{count}</b></div>{"<em>30 gün</em>" if state=="upcoming" else ""}</a>'
    tiles=''
    for key,(label,ico,tone) in hc.CATEGORIES.items():
        tiles+=f'<a class="hc-category hc-{tone} {"active" if category==key else ""}" href="{esc(link(category=key))}" {"aria-current=page" if category==key else ""}><span class="hc-icon">{hc.icon(ico)}</span><b>{esc(label)}</b></a>'
    category_nav='<nav class="hc-categories" aria-label="Sağlık kategorileri">'+tiles+'</nav>'
    top=f'''<header class="hc-heading"><div><small>ÇİFTLİKPRO ENTERPRISE</small><h1>Sağlık Yönetimi</h1><p>Sürünün sağlığı tek ekranda.</p></div><button class="hc-primary hc-main-add" type="button" data-hc-open="hcChooser"><span>+</span> Sağlık İşlemi Ekle</button></header>
      <div class="hc-overview-link"><a href="/health" class="{'active' if category=='general' else ''}">Genel Bakış</a><span>{esc(ns['fmt_date'](hc.today().isoformat()))}</span></div><section class="hc-kpis" aria-label="Sağlık özeti">{kpis}</section>{category_nav}'''
    utilities='<nav class="hc-utilities" aria-label="Sağlık araçları"><a href="/medicines">'+hc.icon('box')+'<span>İlaç Stoku ve Tedaviler</span><b>›</b></a><a href="/medicines?tab=visits">'+hc.icon('person')+'<span>Veteriner Kayıtları</span><b>›</b></a><a href="'+esc(link(query,view='calendar'))+'">'+hc.icon('calendar')+'<span>Sağlık Takvimi</span><b>›</b></a></nav>'
    content=''
    if category=='sync' and view!='calendar':
        sync_query={k:v for k,v in query.items() if k not in ('category','filter','tab','view')}
        if value(query,'search'):sync_query['q']=[value(query,'search')]
        sync_body=sync.page_markup(ns,sync_query,token)
        sync_body=sync_body.replace('href="/synchronization?', 'href="/health?category=sync&amp;').replace('href="/synchronization"','href="/health?category=sync"')
        sync_body=sync_body.replace('method="get" class="sync-search">','method="get" class="sync-search">'+hidden('category','sync'))
        content='<section class="hc-sync-area">'+sync_body+'</section>'
    else:
        if category=='treatment' and view!='calendar':content+=cases_markup(ns,data,token,query)
        history=[r for r in data['history'] if category in ('general',r['category']) and (not term or hc.search_matches(term,r['search']))]
        tabs='<nav class="hc-tabs" aria-label="Sağlık kayıt türü">'+''.join(f'<a class="{"active" if tab==key else ""}" href="{esc(link(query,tab=key,filter="all"))}">{label} <b>{len(history) if key=="done" else len(scoped)}</b></a>' for key,label in [('planned','Planlananlar'),('done','Yapılanlar')])+'</nav>'
        timefilters='<nav class="hc-time-filters">'+''.join(f'<a class="{"active" if filt==key else ""}" href="{esc(link(query,filter=key,tab="planned"))}">{label}</a>' for key,label in [('all','Tümü'),('today','Bugün'),('overdue','Geciken'),('upcoming','Yaklaşan')])+'</nav>' if tab!='done' else ''
        export_query=urlencode({'category':category,'tab':tab,'filter':filt,'search':value(query,'search')})
        output='<details class="hc-more hc-output"><summary aria-label="Çıktı seçenekleri">···</summary><div><a target="_blank" rel="noopener" href="/health-center/print?'+esc(export_query)+'">Yazdır</a><a href="/health-center/report.pdf?'+esc(export_query)+'">PDF indir</a></div></details>'
        toolbar=f'''<header class="hc-section-head"><h2>{'Sağlık Takvimi' if view=='calendar' else 'Sağlık İşlemleri'}</h2><div class="hc-view-switch"><a class="{'active' if view!='calendar' else ''}" href="{esc(link(query,view='agenda'))}">Liste</a><a class="{'active' if view=='calendar' else ''}" href="{esc(link(query,view='calendar'))}">Takvim</a></div>{output}</header>
          <form class="hc-search" method="get">{hidden('category',category)}{hidden('view',view)}{hidden('tab',tab)}{hidden('filter',filt)}<input type="search" name="search" value="{esc(value(query,'search'))}" placeholder="Küpe, ad, işlem veya padok ara" aria-label="Sağlık kayıtlarında ara"><button class="hc-secondary" type="submit">Ara</button>{('<a href="'+esc(link(query,search=''))+'">Temizle</a>') if term else ''}</form>'''
        if view=='calendar':listing=calendar_markup(ns,data,query,token)
        else:
            filtered=history if tab=='done' else [r for r in scoped if filt=='all' or (r['state']==filt and (filt!='upcoming' or r['date']<=(hc.today()+timedelta(days=30)).isoformat()))]
            page=hc.integer(value(query,'page','1'),'Sayfa',1,100000);pages=max(1,(len(filtered)+24)//25);page=min(page,pages)
            rows=filtered[(page-1)*25:page*25]
            listing=tabs+timefilters+(history_rows(ns,rows,token,query) if tab=='done' else task_rows(ns,rows,token,query))
            if pages>1:listing+='<nav class="hc-pagination">'+(f'<a href="{esc(link(query,page=page-1))}">‹ Önceki</a>' if page>1 else '<span></span>')+f'<span>{page} / {pages} · {len(filtered)} kayıt</span>'+(f'<a href="{esc(link(query,page=page+1))}">Sonraki ›</a>' if page<pages else '<span></span>')+'</nav>'
        content+='<section class="hc-panel hc-agenda">'+toolbar+listing+'</section>'
        if view!='calendar' and tab!='done':content+=program_cards(ns,c,query,token)
        if category=='general' and view!='calendar' and tab!='done':
            content+='<div class="hc-bottom-grid">'+cases_markup(ns,data,token,query,overview=True)+'<section class="hc-panel"><header class="hc-section-head"><h2>Son Uygulamalar</h2><a href="/health?tab=done">Tümünü gör ›</a></header>'+history_rows(ns,data['history'][:4],token,query)+'</section></div>'
    auto=' data-hc-add-auto' if value(query,'app_action')=='add' else ''
    return '<link rel="stylesheet" href="/app-assets/health-center.css?v=2.0.30"><section id="healthCenter" class="hc-workspace" data-category="'+category+'"'+auto+'>'+top+content+utilities+'</section>'+dialogs(c,data['subjects'],query,token)+record_dialog(c,query,token)+'<script src="/app-assets/health-center.js?v=2.0.33" defer></script>'
