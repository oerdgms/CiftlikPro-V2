"""Unified health workspace over the existing Enterprise health ledger.

Plans never create applications or expenses. Targets are saved as animal IDs,
not reevaluated from paddock membership. The legacy routes remain compatible.
"""
from text_search import matches as search_matches
import calendar
import hashlib
import hmac
import html
import json
import secrets
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import parse_qs, urlencode, urlparse

import reproduction_sync as sync

BUILD = 'AppEdition2.0.30-UnifiedHealth'
CATEGORIES = {
    'vaccine': ('Aşı', 'vaccine', 'blue'),
    'parasite': ('Parazit', 'parasite', 'orange'),
    'vitamin': ('Vitamin / Mineral', 'vitamin', 'purple'),
    'treatment': ('Hastalık / Tedavi', 'treatment', 'red'),
    'sync': ('Senkronizasyon', 'sync', 'green'),
}
KINDS = {'vaccine':'Aşı', 'parasite':'Parazit', 'vitamin':'Vitamin / Mineral', 'treatment':'İlaç'}
DEFINITIONS = {
    'vaccine':['Şap', 'Enterotoksemi (Karma, Mera)', 'IBR–BVD–PI–BRS', 'Pastörella'],
    'parasite':['İç Parazit', 'Dış Parazit', 'İç / Dış Parazit'],
    'vitamin':['Vitamin / Mineral', 'Vitamin Desteği', 'Mineral Desteği'],
    'treatment':['Tedavi Kontrolü', 'Muayene'],
}
ICON_PATHS = {
    'vaccine':'<path d="m16 3 5 5M14 5l5 5M12 7l5 5-8 8-5-5zM4 20l-2 2M10 10l3 3"/>',
    'parasite':'<path d="M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7z"/>',
    'vitamin':'<path d="m9 5-5 5a6 6 0 0 0 9 9l6-6a6 6 0 0 0-9-9zM8 8l8 8"/>',
    'treatment':'<path d="M8 3h8v5h5v8h-5v5H8v-5H3V8h5z"/>',
    'sync':'<path d="M20 8a8 8 0 0 0-14-3L3 8m0-5v5h5M4 16a8 8 0 0 0 14 3l3-3m0 5v-5h-5"/>',
    'calendar':'<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 2v6M17 2v6M3 11h18M8 15h1M15 15h1"/>',
    'clock':'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
    'alert':'<path d="m12 3 10 18H2zM12 9v5M12 17h.01"/>',
    'heart':'<path d="M20 5c-3-3-7-1-8 2-2-3-6-5-9-2-5 6 9 15 9 15S25 11 20 5zM5 12h4l2-4 3 8 2-4h3"/>',
    'box':'<path d="m3 7 9-5 9 5v12l-9 3-9-3zM3 7l9 5 9-5M12 12v10"/>',
    'person':'<circle cx="12" cy="7" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',
}


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def norm(value):
    return str(value or '').replace('I','ı').replace('İ','i').casefold().strip()


def icon(key):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+ICON_PATHS.get(key,ICON_PATHS['treatment'])+'</svg>'


def today():
    return sync.now().date()


def stamp():
    return sync.now().isoformat(timespec='seconds')


def day(value, label='Tarih'):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        raise ValueError(label+' geçersiz.')


def integer(value, label, minimum=0, maximum=3650):
    try:
        result=int(str(value))
        if not minimum <= result <= maximum:raise ValueError()
        return result
    except (ValueError, TypeError, OverflowError):
        raise ValueError(label+' geçersiz.')


def text(value, label, maximum=2000):
    result=str(value or '').strip()
    if len(result)>maximum:raise ValueError(label+' çok uzun.')
    return result


def cents(value):
    try:
        number=Decimal(str(value or '0').replace(',','.'))
        if not number.is_finite() or not 0<=number<=Decimal('10000000'):raise ValueError()
        return int((number*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, OverflowError):
        raise ValueError('Tutar geçersiz.')


def add_interval(start, value, unit):
    if unit=='days':return start+timedelta(days=value)
    if unit!='months':raise ValueError('Tekrar birimi geçersiz.')
    index=start.year*12+start.month-1+value
    year,month=divmod(index,12);month+=1
    if year>9999:raise ValueError('Tekrar tarihi geçersiz.')
    return date(year,month,min(start.day,calendar.monthrange(year,month)[1]))


def init_schema(c):
    c.executescript('''
        create table if not exists health_program_meta (
            course_id integer primary key, category text not null,
            repeat_value integer not null default 0, repeat_unit text not null default 'months',
            rapel_days integer not null default 0, revision integer not null default 1,
            request_key text not null unique, case_id integer);
        create table if not exists health_definitions (
            id integer primary key, category text not null, name text not null,
            unique(category,name));
        create table if not exists health_cases (
            id integer primary key, diagnosis text not null, illness_date text not null,
            veterinarian text not null default '', vet_cents integer not null default 0,
            medicine_cents integer not null default 0, notes text not null default '',
            treatment_note text not null default '', status text not null default 'active',
            closed_date text, revision integer not null default 1, request_key text not null unique,
            created_at text not null, created_by text not null);
        create table if not exists health_case_targets (
            id integer primary key, case_id integer not null, animal_id integer, calf_id integer,
            health_id integer, finance_id integer);
        create index if not exists idx_health_case_targets_case on health_case_targets(case_id);
        create index if not exists idx_health_cases_status on health_cases(status,illness_date);
    ''')
    columns={r[1] for r in c.execute('pragma table_info(health_tasks)')}
    if 'cycle_no' not in columns:c.execute('alter table health_tasks add column cycle_no integer not null default 0')
    if 'cycle_start' not in columns:c.execute('alter table health_tasks add column cycle_start text')
    meta_columns={r[1] for r in c.execute('pragma table_info(health_program_meta)')}
    if 'schedule_mode' not in meta_columns:c.execute("alter table health_program_meta add column schedule_mode text not null default 'repeat'")
    for category,names in DEFINITIONS.items():
        c.executemany('insert or ignore into health_definitions(category,name) values(?,?)',[(category,name) for name in names])


def subjects(c):
    result=[]
    for source,table in [('animal','animals'),('calf','calves')]:
        extra=' and a.promoted_animal_id is null' if source=='calf' else ''
        column='animal_id' if source=='animal' else 'calf_id'
        for r in c.execute(f'''select a.*,p.name paddock_name from {table} a left join paddocks p on p.id=a.paddock_id
            where coalesce(a.status,'Aktif')='Aktif'{extra} and not exists
            (select 1 from animal_losses l where l.{column}=a.id) order by a.tag'''):
            a=dict(r)
            result.append({'ref':source+':'+str(a['id']),'id':a['id'],'source':source,'tag':a['tag'],
                'nickname':a.get('nickname') or '', 'gender':a.get('gender') or '',
                'paddock_id':str(a.get('paddock_id') or ''),'paddock':a.get('paddock_name') or a.get('paddock') or 'Padoksuz'})
    return sorted(result,key=lambda a:norm(a['tag']))


def selected_subjects(c, raw_refs):
    try:refs=json.loads(raw_refs) if isinstance(raw_refs,str) else raw_refs
    except (ValueError, TypeError):raise ValueError('Hayvan seçimi geçersiz.')
    if not isinstance(refs,list) or not 1<=len(refs)<=500:raise ValueError('En az bir, en fazla 500 hayvan seçin.')
    lookup={a['ref']:a for a in subjects(c)}
    refs=list(dict.fromkeys(str(ref) for ref in refs))
    if any(ref not in lookup for ref in refs):raise ValueError('Seçimde aktif olmayan hayvan var. Hayvan seçimini yenileyin.')
    return [lookup[ref] for ref in refs]


def target_ids(a):
    return (a['id'],None) if a['source']=='animal' else (None,a['id'])


def category_for(kind, product='', stored=None):
    if stored in CATEGORIES:return stored
    name=norm(kind+' '+str(product or ''))
    if 'senkron' in name:return 'sync'
    if kind=='Aşı' or 'gebelik aşı' in name:return 'vaccine'
    if any(word in name for word in ('parazit','antiparazit','anthelmint')):return 'parasite'
    if any(word in name for word in ('vitamin','mineral')):return 'vitamin'
    return 'treatment'


def add_cycle(c, course_id, a, start, cycle, cost_cents, rapel_days):
    aid,cid=target_ids(a)
    for dose,offset in [(1,0)]+([(2,rapel_days)] if rapel_days else []):
        exists=c.execute('''select 1 from health_tasks where course_id=? and coalesce(animal_id,0)=?
            and coalesce(calf_id,0)=? and cycle_no=? and dose_no=?''',(course_id,aid or 0,cid or 0,cycle,dose)).fetchone()
        if exists:continue
        c.execute('''insert into health_tasks(course_id,animal_id,calf_id,planned_date,dose_no,dose_total,
            status,cost,cycle_no,cycle_start) values(?,?,?,?,?,?,'Bekliyor',?,?,?)''',
            (course_id,aid,cid,(start+timedelta(days=offset)).isoformat(),dose,2 if rapel_days else 1,cost_cents/100,cycle,start.isoformat()))


def save_program(ns,c,data,username):
    c.execute('BEGIN IMMEDIATE')
    pid=integer(data.get('id') or 0,'Program',0,2147483647)
    existing=c.execute('''select hc.*,m.category,m.repeat_value,m.repeat_unit,m.rapel_days,m.revision,m.schedule_mode
        from health_courses hc join health_program_meta m on m.course_id=hc.id where hc.id=?''',(pid,)).fetchone() if pid else None
    if pid and not existing:raise ValueError('Program bulunamadı.')
    request_key=text(data.get('request_key'),'İstek',100)
    if not pid:
        if len(request_key)<16:raise ValueError('Formu yenileyerek tekrar deneyin.')
        previous=c.execute('select course_id from health_program_meta where request_key=?',(request_key,)).fetchone()
        if previous:return previous[0]
    if existing and str(existing['revision'])!=str(data.get('revision')):raise ValueError('Program başka bir ekranda değişti. Sayfayı yenileyin.')
    category=data.get('category')
    if category not in KINDS:raise ValueError('Sağlık kategorisi seçin.')
    product=text(data.get('product'),'İşlem adı',150)
    if not product:raise ValueError('İşlem adı zorunludur.')
    start=day(data.get('start_date'),'İlk uygulama tarihi')
    repeat=integer(data.get('repeat_value') or 0,'Tekrar aralığı',0,3650)
    unit=data.get('repeat_unit','months')
    if unit not in ('days','months') or (unit=='months' and repeat>120):raise ValueError('Tekrar aralığı geçersiz.')
    rapel=integer(data.get('rapel_days') or 0,'Rapel gün sayısı',0,365) if data.get('rapel')=='yes' else 0
    if data.get('rapel')=='yes' and not rapel:raise ValueError('Rapel için gün sayısını girin.')
    if repeat and rapel and start+timedelta(days=rapel)>=add_interval(start,repeat,unit):raise ValueError('Rapel tarihi sonraki tekrar tarihinden önce olmalıdır.')
    schedule_mode='course' if category=='treatment' and data.get('schedule_mode')=='course' else 'repeat'
    treatment_days=integer(data.get('treatment_days') or 1,'Uygulama günü',1,60) if schedule_mode=='course' else 1
    treatment_interval=integer(data.get('treatment_interval_days') or 1,'Uygulama aralığı',1,365) if schedule_mode=='course' else 1
    daily=integer(data.get('times_per_day') or 1,'Günlük uygulama',1,6) if schedule_mode=='course' else 1
    if schedule_mode=='course':repeat=0;rapel=0
    cost=cents(data.get('cost'));notes=text(data.get('notes'),'Açıklama')
    chosen=selected_subjects(c,data.get('subjects_json','[]'))
    completed=c.execute("select count(*) from health_tasks where course_id=? and status in ('Tamamlandı','Yapıldı')",(pid,)).fetchone()[0] if pid else 0
    if completed:
        old_refs={('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id']) for r in c.execute('select distinct animal_id,calf_id from health_tasks where course_id=?',(pid,))}
        schedule=(existing['category'],existing['start_date'],existing['repeat_value'],existing['repeat_unit'],existing['rapel_days'],existing['schedule_mode'],existing['treatment_days'],existing['treatment_interval_days'],existing['times_per_day'])
        if set(a['ref'] for a in chosen)!=old_refs or (category,start.isoformat(),repeat,unit,rapel,schedule_mode,treatment_days,treatment_interval,daily)!=schedule:
            raise ValueError('Uygulaması yapılmış programda hayvanlar ve takvim korunur. Yeni takvim için yeni program açın.')
    if existing:
        c.execute('update health_courses set product=?,cost_per_application=?,notes=? where id=?',(product,cost/100,notes,pid))
        c.execute('update health_program_meta set revision=revision+1 where course_id=?',(pid,))
        c.execute("update health_tasks set cost=?,notes=? where course_id=? and status='Bekliyor'",(cost/100,notes,pid))
        if not completed:
            c.execute('delete from health_tasks where course_id=?',(pid,))
            c.execute('''update health_courses set kind=?,start_date=?,scope_type=?,paddock_id=null,dose_count=?,interval_days=? where id=?''',
                (KINDS[category],start.isoformat(),'multi' if len(chosen)>1 else 'single',2 if rapel else 1,rapel,pid))
            c.execute('update health_program_meta set category=?,repeat_value=?,repeat_unit=?,rapel_days=? where course_id=?',(category,repeat,unit,rapel,pid))
    else:
        pid=c.execute('''insert into health_courses(kind,product,scope_type,start_date,dose_count,interval_days,
            cost_per_application,notes,created_at) values(?,?,?,?,?,?,?,?,?)''',
            (KINDS[category],product,'multi' if len(chosen)>1 else 'single',start.isoformat(),2 if rapel else 1,rapel,cost/100,notes,stamp())).lastrowid
        c.execute('''insert into health_program_meta(course_id,category,repeat_value,repeat_unit,rapel_days,request_key)
            values(?,?,?,?,?,?)''',(pid,category,repeat,unit,rapel,request_key))
    if not completed:
        c.execute('update health_courses set treatment_days=?,treatment_interval_days=?,times_per_day=? where id=?',(treatment_days,treatment_interval,daily,pid))
        c.execute('update health_program_meta set schedule_mode=? where course_id=?',(schedule_mode,pid))
        if schedule_mode=='course':
            ns['create_health_course_tasks'](c,pid,[(a,cid,label['tag']) for label in chosen for a,cid in [target_ids(label)]],
                'İlaç',start.isoformat(),cost/100,notes,treatment_days=treatment_days,times_per_day=daily,treatment_interval_days=treatment_interval)
        else:
            for a in chosen:add_cycle(c,pid,a,start,1,cost,rapel)
    c.execute('insert or ignore into health_definitions(category,name) values(?,?)',(category,product))
    if not existing and data.get('mode')=='record':
        if start>today():raise ValueError('Gelecekteki uygulama yapılmış olarak kaydedilemez.')
        ids=[r[0] for r in c.execute('select id from health_tasks where course_id=? and dose_no=1 and day_no=1 and application_no=1',(pid,))]
        for tid in ids:complete_task(ns,c,tid,start,username)
    return pid


def complete_task(ns,c,tid,actual,username):
    t=c.execute('''select t.*,hc.kind,hc.product,hc.active,hc.cost_per_application,m.repeat_value,m.repeat_unit,m.rapel_days
        from health_tasks t join health_courses hc on hc.id=t.course_id
        left join health_program_meta m on m.course_id=hc.id where t.id=?''',(tid,)).fetchone()
    if not t:raise ValueError('Uygulama bulunamadı.')
    if t['status'] in ('Tamamlandı','Yapıldı'):return False
    if t['status']!='Bekliyor' or not t['active']:raise ValueError('Program kapatılmış veya uygulama artık beklemiyor.')
    if actual>today():raise ValueError('Gelecekteki uygulama yapılmış olarak kaydedilemez.')
    source='animal' if t['animal_id'] else 'calf'
    refs=selected_subjects(c,[source+':'+str(t['animal_id'] or t['calf_id'])])
    if t['dose_no']>1:
        earlier=c.execute('''select completed_date,status from health_tasks where course_id=? and coalesce(animal_id,0)=?
            and coalesce(calf_id,0)=? and cycle_no=? and dose_no<? order by dose_no desc limit 1''',
            (t['course_id'],t['animal_id'] or 0,t['calf_id'] or 0,t['cycle_no'],t['dose_no'])).fetchone()
        if earlier and (earlier['status'] not in ('Tamamlandı','Yapıldı') or actual.isoformat()<str(earlier['completed_date'] or '')):
            raise ValueError('Önce bu hayvanın ilk uygulamasını kaydedin. Rapel tarihi ilk uygulamadan önce olamaz.')
    cost=cents(t['cost']);fid=None
    product=t['product']+((' · Rapel' if t['dose_no']>1 else '') if t['rapel_days'] else (f' · {t["dose_no"]}. Doz' if t['kind']=='Aşı' else ''))
    if cost:
        fid=c.execute('''insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,calf_id,created_at)
            values(?,'Gider',?,?,?,'Nakit',?,?,?)''',(actual.isoformat(),t['kind'],cost/100,product,t['animal_id'],t['calf_id'],stamp())).lastrowid
    c.execute('''insert into health(animal_id,calf_id,kind,product,applied_date,cost,notes,finance_id,course_id,task_id)
        values(?,?,?,?,?,?,?,?,?,?)''',(t['animal_id'],t['calf_id'],t['kind'],product,actual.isoformat(),cost/100,
        f'Plan #{t["course_id"]} · Planlanan {t["planned_date"]} · {username}',fid,t['course_id'],tid))
    c.execute("update health_tasks set status='Tamamlandı',completed_date=? where id=?",(actual.isoformat(),tid))
    if t['rapel_days'] is not None and t['dose_no']==1:
        c.execute('''update health_tasks set planned_date=?,cycle_start=? where course_id=? and coalesce(animal_id,0)=?
            and coalesce(calf_id,0)=? and cycle_no=? and dose_no=2 and status='Bekliyor' ''',
            ((actual+timedelta(days=t['rapel_days'])).isoformat(),actual.isoformat(),t['course_id'],t['animal_id'] or 0,t['calf_id'] or 0,t['cycle_no']))
        if t['repeat_value']:
            next_start=add_interval(actual,t['repeat_value'],t['repeat_unit'])
            add_cycle(c,t['course_id'],refs[0],next_start,t['cycle_no']+1,cents(t['cost_per_application']),t['rapel_days'])
    return True


def split_cost(total,count,index):
    return total//count+(1 if index<total%count else 0)


def save_case(ns,c,data,username):
    c.execute('BEGIN IMMEDIATE')
    cid=integer(data.get('id') or 0,'Hastalık kaydı',0,2147483647)
    old=c.execute('select * from health_cases where id=?',(cid,)).fetchone() if cid else None
    if cid and not old:raise ValueError('Hastalık kaydı bulunamadı.')
    key=text(data.get('request_key'),'İstek',100)
    if not cid:
        if len(key)<16:raise ValueError('Formu yenileyin.')
        previous=c.execute('select id from health_cases where request_key=?',(key,)).fetchone()
        if previous:return previous[0]
    if old and str(old['revision'])!=str(data.get('revision')):raise ValueError('Hastalık kaydı değişti. Sayfayı yenileyin.')
    diagnosis=text(data.get('diagnosis'),'Hastalık / belirti',150)
    if not diagnosis:raise ValueError('Hastalık / belirti girin.')
    illness=day(data.get('illness_date'),'Hastalık tarihi')
    if illness>today():raise ValueError('Hastalık tarihi gelecekte olamaz.')
    veterinarian=text(data.get('veterinarian'),'Veteriner',150)
    notes=text(data.get('notes'),'Açıklama');treatment=text(data.get('treatment_note'),'Tedavi notu')
    vet=cents(data.get('vet_cost'));med=cents(data.get('medicine_cost'))
    chosen=selected_subjects(c,data.get('subjects_json','[]'))
    if old:
        targets=[dict(r) for r in c.execute('select * from health_case_targets where case_id=? order by id',(cid,))]
        old_refs={('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id']) for r in targets}
        if set(a['ref'] for a in chosen)!=old_refs:raise ValueError('Kayıtlı hastalığın hayvan seçimi korunur. Diğer hayvanlar için yeni kayıt açın.')
        c.execute('''update health_cases set diagnosis=?,illness_date=?,veterinarian=?,vet_cents=?,medicine_cents=?,notes=?,treatment_note=?,revision=revision+1 where id=?''',
            (diagnosis,illness.isoformat(),veterinarian,vet,med,notes,treatment,cid))
    else:
        cid=c.execute('''insert into health_cases(diagnosis,illness_date,veterinarian,vet_cents,medicine_cents,notes,treatment_note,request_key,created_at,created_by)
            values(?,?,?,?,?,?,?,?,?,?)''',(diagnosis,illness.isoformat(),veterinarian,vet,med,notes,treatment,key,stamp(),username)).lastrowid
        targets=[]
        for a in chosen:
            aid,calfid=target_ids(a)
            target_id=c.execute('insert into health_case_targets(case_id,animal_id,calf_id) values(?,?,?)',(cid,aid,calfid)).lastrowid
            targets.append({'id':target_id,'animal_id':aid,'calf_id':calfid,'health_id':None,'finance_id':None})
    for index,t in enumerate(targets):
        amount=split_cost(vet+med,len(targets),index)/100
        description='Hastalık kaydı · '+diagnosis
        fid=t['finance_id']
        if fid and not c.execute('select 1 from finance where id=?',(fid,)).fetchone():fid=None
        if amount and fid:
            c.execute('update finance set tx_date=?,amount=?,description=? where id=?',(illness.isoformat(),amount,description,fid))
        elif amount:
            fid=c.execute('''insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,calf_id,created_at)
                values(?,'Gider','Sağlık',?,?,'Nakit',?,?,?)''',(illness.isoformat(),amount,description,t['animal_id'],t['calf_id'],stamp())).lastrowid
        elif fid:c.execute('delete from finance where id=?',(fid,));fid=None
        detail=f'Hastalık #{cid} · {veterinarian} · {treatment} · {notes}'
        hid=t['health_id']
        if hid and c.execute('select 1 from health where id=?',(hid,)).fetchone():
            c.execute('update health set product=?,applied_date=?,cost=?,notes=?,finance_id=? where id=?',(diagnosis,illness.isoformat(),amount,detail,fid,hid))
        else:
            hid=c.execute('''insert into health(animal_id,calf_id,kind,product,applied_date,cost,notes,finance_id)
                values(?,?,'Hastalık',?,?,?,?,?)''',(t['animal_id'],t['calf_id'],diagnosis,illness.isoformat(),amount,detail,fid)).lastrowid
        c.execute('update health_case_targets set health_id=?,finance_id=? where id=?',(hid,fid,t['id']))
    return cid


def action(ns,c,data,username):
    c.execute('BEGIN IMMEDIATE')
    act=data.get('action');result='Kayıt güncellendi.'
    if act=='complete':
        actual=day(data.get('actual_date'),'Gerçek uygulama tarihi')
        tid=integer(data.get('task_id'),'Uygulama',1,2147483647)
        complete_task(ns,c,tid,actual,username)
        return 'Uygulama sağlık geçmişine kaydedildi.'
    if act in ('pause','resume','delete_program'):
        pid=integer(data.get('course_id'),'Program',1,2147483647)
        p=c.execute('select * from health_courses where id=?',(pid,)).fetchone()
        if not p:raise ValueError('Program bulunamadı.')
        if act=='resume':
            c.execute('update health_courses set active=1 where id=?',(pid,))
        else:
            c.execute('update health_courses set active=0 where id=?',(pid,))
            if act=='delete_program':
                c.execute("delete from health_tasks where course_id=? and status='Bekliyor'",(pid,))
                result='Program kaldırıldı. Yapılan uygulamalar sağlık geçmişinde korundu.'
        c.execute('update health_program_meta set revision=revision+1 where course_id=?',(pid,))
    elif act=='delete_record':
        hid=integer(data.get('health_id'),'Uygulama',1,2147483647)
        record=c.execute('select h.*,m.course_id managed_course from health h join health_program_meta m on m.course_id=h.course_id where h.id=?',(hid,)).fetchone()
        if not record:raise ValueError('Program uygulaması bulunamadı.')
        task=c.execute('select * from health_tasks where id=?',(record['task_id'],)).fetchone()
        if task and task['dose_no']==1:
            later=c.execute("""select 1 from health_tasks where course_id=? and coalesce(animal_id,0)=?
                and coalesce(calf_id,0)=? and (cycle_no>? or (cycle_no=? and dose_no>1))
                and status in ('Tamamlandı','Yapıldı') limit 1""",
                (task['course_id'],task['animal_id'] or 0,task['calf_id'] or 0,task['cycle_no'],task['cycle_no'])).fetchone()
            if later:raise ValueError('Bu uygulamaya bağlı rapel veya tekrar yapılmış. Önce sonraki uygulamaları geri alın.')
            c.execute("""delete from health_tasks where course_id=? and coalesce(animal_id,0)=? and coalesce(calf_id,0)=?
                and cycle_no>? and status='Bekliyor'""",(task['course_id'],task['animal_id'] or 0,task['calf_id'] or 0,task['cycle_no']))
        if record['finance_id']:c.execute('delete from finance where id=?',(record['finance_id'],))
        c.execute('delete from health where id=?',(hid,))
        c.execute("update health_tasks set status='Bekliyor',completed_date=null where id=?",(record['task_id'],))
        result='Uygulama geri alındı ve bağlı gider silindi. İşlem yeniden bekliyor.'
    elif act in ('close_case','reopen_case','delete_case'):
        cid=integer(data.get('case_id'),'Hastalık kaydı',1,2147483647)
        case=c.execute('select * from health_cases where id=?',(cid,)).fetchone()
        if not case:raise ValueError('Hastalık kaydı bulunamadı.')
        if act=='delete_case':
            for target in c.execute('select health_id,finance_id from health_case_targets where case_id=?',(cid,)).fetchall():
                if target['health_id']:c.execute('delete from health where id=?',(target['health_id'],))
                if target['finance_id']:c.execute('delete from finance where id=?',(target['finance_id'],))
            c.execute('delete from health_case_targets where case_id=?',(cid,));c.execute('delete from health_cases where id=?',(cid,))
            result='Hastalık kaydı ve bu kayda ait giderler silindi.'
        else:
            c.execute('update health_cases set status=?,closed_date=?,revision=revision+1 where id=?',
                ('closed' if act=='close_case' else 'active',today().isoformat() if act=='close_case' else None,cid))
    else:raise ValueError('İşlem geçersiz.')
    return result



def edit_record(ns,c,data,username):
    c.execute('BEGIN IMMEDIATE')
    hid=integer(data.get('id'),'Uygulama',1,2147483647)
    r=c.execute('select h.* from health h join health_program_meta m on m.course_id=h.course_id where h.id=?',(hid,)).fetchone()
    if not r:raise ValueError('Program uygulaması bulunamadı.')
    actual=day(data.get('applied_date'),'Uygulama tarihi')
    if actual>today():raise ValueError('Gelecekteki uygulama yapılmış olarak kaydedilemez.')
    if actual.isoformat()!=r['applied_date']:
        raise ValueError('Takvim bağlantısı olan uygulamanın tarihini değiştirmek için uygulamayı geri alıp doğru tarihle yeniden kaydedin.')
    product=text(data.get('product'),'İşlem adı',150)
    if not product:raise ValueError('İşlem adı zorunludur.')
    amount=cents(data.get('cost'));note=text(data.get('notes'),'Açıklama')
    fid=r['finance_id']
    if fid and not c.execute('select 1 from finance where id=?',(fid,)).fetchone():fid=None
    if amount and fid:c.execute('update finance set amount=?,description=? where id=?',(amount/100,product,fid))
    elif amount:
        fid=c.execute("insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,calf_id,created_at) values(?,'Gider',?,?,?,'Nakit',?,?,?)",
            (actual.isoformat(),r['kind'],amount/100,product,r['animal_id'],r['calf_id'],stamp())).lastrowid
    elif fid:c.execute('delete from finance where id=?',(fid,));fid=None
    c.execute('update health set product=?,cost=?,notes=?,finance_id=? where id=?',(product,amount/100,note,fid,hid))
    return 'Uygulama ve bağlı gider güncellendi.'

def workspace_data(ns,c):
    active={a['ref']:a for a in subjects(c)}
    pending=[]
    for raw in c.execute('''select t.*,hc.kind,hc.product,hc.scope_type,m.category from health_tasks t
        join health_courses hc on hc.id=t.course_id left join health_program_meta m on m.course_id=hc.id
        where t.status='Bekliyor' and coalesce(hc.active,1)=1 order by t.planned_date,t.id'''):
        r=dict(raw);ref=('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id'])
        if ref not in active:continue
        a=active[ref];category=category_for(r['kind'],r['product'],r['category'])
        detail=('Rapel' if r['dose_no']>1 and r['category'] else f'{r["dose_no"]} / {r["dose_total"]}. doz') if r['kind']=='Aşı' or r['dose_total']>1 else 'Planlı uygulama'
        if r['kind']=='İlaç' and (not r['category'] or r['day_total']>1 or r['applications_per_day']>1):detail=f'{r["day_no"]} / {r["day_total"]}. gün · {r["application_no"]} / {r["applications_per_day"]}'
        pending.append({'date':r['planned_date'],'category':category,'title':r['product'],'subject':a['tag'],
            'nickname':a['nickname'],'paddock':a['paddock'],'detail':detail,'source':'course','id':r['id'],
            'course_id':r['course_id'],'plan_ref':f"{r['course_id']}:{r['planned_date']}:{r['dose_no']}:{r['day_no']}:{r['application_no']}",'url':'/health?'+urlencode({'category':category,'plan':r['course_id']}),
            'edit_url':('/health?'+urlencode({'category':category,'edit':r['course_id']})) if r['category'] else '/health-plan-edit?id='+str(r['course_id'])})
    for raw in c.execute("select * from health where coalesce(next_date,'')<>'' order by next_date,id"):
        r=dict(raw);ref=('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id'])
        if ref not in active:continue
        a=active[ref]
        pending.append({'date':r['next_date'],'category':category_for(r['kind'] or '',r['product']),
            'title':r['product'] or r['kind'],'subject':a['tag'],'nickname':a['nickname'],'paddock':a['paddock'],
            'detail':'Önceki kayıttan plan','source':'legacy','id':r['id'],'url':'/health-edit?id='+str(r['id']),
            'edit_url':'/health-edit?id='+str(r['id'])})
    for r in ns['pregnancy_vaccine_tasks'](c,horizon_days=370):
        ref='animal:'+str(r['animal_id'])
        if ref not in active:continue
        a=active[ref]
        pending.append({'date':r['task_date'],'category':'vaccine','title':str(r['month'])+'. Ay Gebelik Aşısı',
            'subject':a['tag'],'nickname':a['nickname'],'paddock':a['paddock'],'detail':'Gebelik planı',
            'source':'pregnancy','id':r['insemination_id'],'animal_id':r['animal_id'],'month':r['month'],'url':'/reproduction-center'})
    for r in sync.task_entries(ns,c):
        a=active.get('animal:'+str(r['animal_id']),{})
        pending.append({'date':r['date'],'time':r['planned_at'][11:16],'category':'sync','title':r['task'].replace('Senkronizasyon · ',''),
            'subject':r['subject'],'nickname':a.get('nickname',''),'paddock':a.get('paddock',''),
            'detail':r['detail'],'source':'sync','id':r['sync_step_id'],'state':r['state'],
            'url':'/health?'+urlencode({'category':'sync','plan':r['sync_plan_id'],'animal':r['animal_id']})+'#sync-step-'+str(r['sync_step_id'])})
    for r in pending:
        r.setdefault('state','overdue' if r['date']<today().isoformat() else 'today' if r['date']==today().isoformat() else 'upcoming')
        r['search']=norm(' '.join(str(r.get(k) or '') for k in ('title','subject','nickname','paddock','detail')))
    pending.sort(key=lambda r:(r['date'],r.get('time',''),norm(r['subject']),r['id']))
    history=[]
    for raw in c.execute('''select h.*,m.category,a.tag adult_tag,a.nickname,p.name adult_pad,
        ca.tag calf_tag,pc.name calf_pad,ct.case_id,ss.plan_id sync_plan_id
        from health h left join health_program_meta m on m.course_id=h.course_id
        left join animals a on a.id=h.animal_id left join paddocks p on p.id=a.paddock_id
        left join calves ca on ca.id=h.calf_id left join paddocks pc on pc.id=ca.paddock_id
        left join health_case_targets ct on ct.health_id=h.id
        left join (select s.health_id,e.plan_id from repro_sync_steps s join repro_sync_animals e on e.id=s.enrollment_id) ss on ss.health_id=h.id
        where coalesce(h.applied_date,'')<>'' and h.applied_date<=?
        order by h.applied_date desc,h.id desc''',(today().isoformat(),)):
        r=dict(raw)
        category=category_for(r['kind'] or '',r['product'],r['category'])
        edit=('/health?record_edit='+str(r['id'])) if r['category'] else '/health-edit?id='+str(r['id'])
        if r['sync_plan_id']:edit='/health?category=sync&plan='+str(r['sync_plan_id'])
        elif r['case_id']:edit='/health?category=treatment&case_edit='+str(r['case_id'])
        elif r['treatment_id']:edit='/treatment-edit?id='+str(r['treatment_id'])
        history.append({'id':r['id'],'category':category,'date':r['applied_date'] or '',
            'title':r['product'] or r['kind'] or 'Sağlık kaydı','subject':r['adult_tag'] or r['calf_tag'] or 'Arşiv kaydı',
            'nickname':r['nickname'] or '', 'paddock':r['adult_pad'] or r['calf_pad'] or '',
            'cost':float(r['cost'] or 0),'edit_url':edit,'kind':r['kind'],'notes':r['notes'] or '',
            'search':norm(' '.join(str(r.get(k) or '') for k in ('product','kind','adult_tag','calf_tag','nickname','notes'))),
            'date_label':'Hastalık kaydı' if r['case_id'] else 'Yapıldı',
            'linked':bool(r['sync_plan_id'] or r['case_id'] or r['treatment_id']), 'program_record':bool(r['category'])})
    cases=[];patient_refs=set()
    for raw in c.execute('select * from health_cases order by status,illness_date desc,id desc'):
        r=dict(raw);targets=[]
        for target in c.execute('''select ct.*,a.tag adult_tag,a.nickname,ca.tag calf_tag from health_case_targets ct
            left join animals a on a.id=ct.animal_id left join calves ca on ca.id=ct.calf_id where ct.case_id=? order by ct.id''',(r['id'],)):
            t=dict(target);ref=('animal:' if t['animal_id'] else 'calf:')+str(t['animal_id'] or t['calf_id'])
            targets.append(t['adult_tag'] or t['calf_tag'] or 'Arşiv kaydı')
            if r['status']=='active' and ref in active:patient_refs.add(ref)
        r['tags']=' · '.join(targets);r['count']=len(targets);r['search']=norm(r['diagnosis']+' '+r['tags']+' '+r['veterinarian'])
        cases.append(r)
    treatments=[]
    for raw in c.execute('''select t.*,a.tag adult_tag,ca.tag calf_tag,m.product_name from treatments t
        left join animals a on a.id=t.animal_id left join calves ca on ca.id=t.calf_id
        left join medicine_catalog m on m.id=t.medicine_id where t.status='Aktif' order by t.start_date desc,t.id desc'''):
        r=dict(raw);ref=('animal:' if r['animal_id'] else 'calf:')+str(r['animal_id'] or r['calf_id'])
        if ref not in active:continue
        patient_refs.add(ref);treatments.append(r)
    return {'pending':pending,'history':history,'cases':cases,'treatments':treatments,'patient_count':len(patient_refs),'subjects':list(active.values())}


def csrf_token(handler):
    return sync.csrf_token(handler)


def safe_return(value):
    parsed=urlparse(value or '/health')
    if parsed.scheme or parsed.netloc or parsed.path!='/health':return '/health'
    return parsed.geturl()


def install(ns):
    from pathlib import Path
    import re
    import health_views as views
    original_init=ns['init_db']
    def init_db(*args,**kwargs):
        result=original_init(*args,**kwargs)
        with ns['db']() as c:init_schema(c)
        return result
    ns['init_db']=init_db
    original_page=ns['page']
    def page(title,body,path='/',user='admin',flash=''):
        if path=='/medicines':
            body='<nav class="health-subsection-nav" style="margin-bottom:16px"><a class="btn alt" href="/health">‹ Sağlık Yönetimi</a></nav>'+body
        return original_page(title,body,path,user,flash)
    ns['page']=page
    cls=ns['App'];original_get,original_post=cls.do_GET,cls.do_POST
    def authorized(handler):
        if not handler.require():return False
        allowed,_,message=ns['license_status']()
        if not allowed:handler.redirect('/license',message);return False
        return True
    def do_GET(self):
        parsed=urlparse(self.path)
        if parsed.path.startswith('/app-assets/health-center.'):
            filename=parsed.path.removeprefix('/app-assets/')
            if filename in ('health-center.css','health-center.js'):
                import mobile_ui
                content=(Path(__file__).parent/'mobile_assets'/filename).read_bytes()
                return mobile_ui.send_bytes(self,content,'text/css' if filename.endswith('.css') else 'application/javascript')
        if parsed.path in ('/health-center/print','/health-center/report.pdf'):
            if not authorized(self):return
            query=parse_qs(parsed.query)
            category=(query.get('category') or ['general'])[0]
            mode=(query.get('tab') or ['planned'])[0]
            state=(query.get('filter') or ['all'])[0]
            search=norm((query.get('search') or [''])[0])
            with ns['db']() as c:data=workspace_data(ns,c)
            records=data['history'] if mode=='done' else data['pending']
            records=[r for r in records if (category=='general' or r['category']==category) and (not search or search_matches(search,r['search']))]
            if mode!='done' and state in ('today','overdue','upcoming'):
                records=[r for r in records if r['state']==state and (state!='upcoming' or r['date']<=(today()+timedelta(days=30)).isoformat())]
            rows=[{'date':ns['fmt_date'](r['date']),'title':r['title'],'category':CATEGORIES[r['category']][0],
                'subject':r['subject'],'paddock':r['paddock'],'status':('Yapıldı' if mode=='done' else {'today':'Bugün','overdue':'Gecikti','upcoming':'Planlandı'}[r['state']])} for r in records]
            columns=[('Tarih','date'),('İşlem','title'),('Kategori','category'),('Hayvan','subject'),('Padok','paddock'),('Durum','status')]
            title='Sağlık Yönetimi · '+('Yapılan Uygulamalar' if mode=='done' else 'İş Planı')
            subtitle=str(len(rows))+' kayıt · '+ns['fmt_date'](today().isoformat())
            if parsed.path.endswith('/print'):
                return self.send_html(ns['simple_table_print'](title,subtitle,columns,rows,'/health-center/report.pdf?'+parsed.query))
            payload=ns['simple_table_pdf'](title,subtitle,columns,rows)
            self.send_response(200);self.send_header('Content-Type','application/pdf');self.send_header('Content-Disposition','attachment; filename="saglik_yonetimi.pdf"');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload);return
        if parsed.path!='/health':return original_get(self)
        if not authorized(self):return
        query=parse_qs(parsed.query)
        try:
            with ns['db']() as c:
                body=views.markup(ns,c,query,csrf_token(self))
            document=ns['page']('Sağlık Yönetimi',body,'/health',self.user()['username'],(query.get('msg') or [''])[0])
            return self.send_html(document)
        except (ValueError,TypeError,OverflowError) as exc:return self.redirect('/health',str(exc))
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ('/health-center/program','/health-center/case','/health-center/record','/health-center/action'):return original_post(self)
        if not authorized(self):return
        back='/health'
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=131072:raise ValueError('Gönderilen kayıt çok büyük veya geçersiz.')
            fields=parse_qs(self.rfile.read(length).decode('utf-8'),keep_blank_values=True,max_num_fields=80)
            data={k:v[0] for k,v in fields.items()};back=safe_return(data.get('return_to'))
            if not hmac.compare_digest(data.get('csrf',''),csrf_token(self)):raise ValueError('Oturum değişti. Sayfayı yenileyerek tekrar deneyin.')
            with ns['db']() as c:
                if path.endswith('/program'):
                    pid=save_program(ns,c,data,self.user()['username']);message='Sağlık programı kaydedildi.'
                    back='/health?'+urlencode({'category':data['category'],'tab':'planned','plan':pid})
                elif path.endswith('/case'):
                    cid=save_case(ns,c,data,self.user()['username']);message='Hastalık kaydı kaydedildi.'
                    back='/health?category=treatment'
                elif path.endswith('/record'):message=edit_record(ns,c,data,self.user()['username'])
                else:message=action(ns,c,data,self.user()['username'])
            ns['audit'](self.user()['username'],'Sağlık Yönetimi',message,self.client_ip())
        except (ValueError,TypeError,OverflowError,UnicodeDecodeError) as exc:return self.redirect(back,str(exc))
        return self.redirect(back,message)
    cls.do_GET,cls.do_POST=do_GET,do_POST
