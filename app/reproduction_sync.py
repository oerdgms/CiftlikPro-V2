"""Shared, per-animal synchronization schedules and recorded applications.

Calendar templates contain timing only. Product, dose and route are supplied
by the veterinarian; creating a plan never records an application or expense.
"""
import hashlib
import hmac
import html
import json
import secrets
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import parse_qs, urlencode, urlparse

import dairy_management as dairy

BUILD = 'AppEdition2.0.28-Synchronization'
SOURCE_COW = 'https://www.dcrcouncil.org/wp-content/uploads/2019/04/Dairy-Cow-Protocol-Sheet-Updated-2018.pdf'
SOURCE_HEIFER = 'https://www.dcrcouncil.org/wp-content/uploads/2018/12/Dairy-Heifer-Protocol-Sheet-Updated-2018.pdf'
SECRET = secrets.token_bytes(32)
GROUPS = {'all':'Tüm uygun dişiler', 'postpartum':'Doğum sonrası', 'heifer':'Düveler', 'open':'Boş inekler'}
KINDS = {'medicine':'Hormon / ilaç', 'device':'CIDR / cihaz', 'insemination':'Tohumlama', 'check':'Kontrol'}
STATES = {'active':'Aktif', 'completed':'Tamamlandı', 'cancelled':'İptal edildi'}


def esc(value):
    return html.escape(str(value if value is not None else ''), quote=True)


def now():
    # All saved schedule times are local farm wall time (Türkiye), not UTC.
    return datetime.now(timezone(timedelta(hours=3))).replace(tzinfo=None, second=0, microsecond=0)


def stamp(value):
    return value.isoformat(timespec='minutes')


def display_time(value):
    try:
        return datetime.fromisoformat(value).strftime('%d/%m/%Y %H:%M')
    except (ValueError, TypeError):
        return '—'


def step(hours, name, hormone='', kind='medicine'):
    return {'offset_minutes':round(hours*60), 'name':name, 'hormone':hormone,
            'kind':kind, 'product':'', 'dose':'', 'unit':'', 'route':''}


def ovsynch(start=0, second=56):
    return [step(start,'GnRH','GnRH'), step(start+168,'Prostaglandin','PGF'),
            step(start+168+second,'GnRH','GnRH'),
            step(start+240,'Planlı tohumlama',kind='insemination')]


# DCRC timing sheets, checked 22/10/2026. Named variants are explicit, not V1/V2.
PROTOCOLS = {
    'ovsynch56': {'name':'Ovsynch 56','audience':'cow','steps':ovsynch(),'source':SOURCE_COW},
    'ovsynch48': {'name':'Ovsynch 48','audience':'cow','steps':ovsynch(second=48),'source':SOURCE_COW},
    'double_ovsynch': {'name':'Double Ovsynch','audience':'cow','steps':[
        step(0,'Ön hazırlık · GnRH','GnRH'), step(168,'Ön hazırlık · Prostaglandin','PGF'),
        step(240,'Ön hazırlık · GnRH','GnRH')]+ovsynch(408),'source':SOURCE_COW},
    'presynch12': {'name':'Presynch 12 / Ovsynch 56','audience':'cow','steps':[
        step(0,'Ön hazırlık · Prostaglandin','PGF'), step(336,'Ön hazırlık · Prostaglandin','PGF')]+ovsynch(624),'source':SOURCE_COW},
    'presynch14': {'name':'Presynch 14 / Ovsynch 56','audience':'cow','steps':[
        step(0,'Ön hazırlık · Prostaglandin','PGF'), step(336,'Ön hazırlık · Prostaglandin','PGF')]+ovsynch(672),'source':SOURCE_COW},
    'g6g': {'name':'G6G / Ovsynch 56','audience':'cow','steps':[
        step(0,'Ön hazırlık · Prostaglandin','PGF'),step(48,'Ön hazırlık · GnRH','GnRH')]+ovsynch(192),'source':SOURCE_COW},
    'cidr5_2pgf': {'name':'Düve · 5 gün CIDR-Synch (GnRH + 2 PGF)','audience':'heifer','steps':[
        step(0,'CIDR yerleştirme',kind='device'), step(0,'GnRH','GnRH'),
        step(120,'CIDR çıkarma',kind='device'), step(120,'Prostaglandin · 1','PGF'),
        step(144,'Prostaglandin · 2','PGF'),step(192,'GnRH','GnRH'),
        step(192,'Planlı tohumlama',kind='insemination')],'source':SOURCE_HEIFER},
    'cidr5_1pgf': {'name':'Düve · 5 gün CIDR-Synch (başlangıç GnRH yok, 1 PGF)','audience':'heifer','steps':[
        step(0,'CIDR yerleştirme',kind='device'),step(120,'CIDR çıkarma',kind='device'),
        step(120,'Prostaglandin','PGF'),step(192,'GnRH','GnRH'),
        step(192,'Planlı tohumlama',kind='insemination')],'source':SOURCE_HEIFER},
    'custom': {'name':'Veterinerin özel planı','audience':'all',
               'steps':[step(0,'İlk uygulama')],'source':''},
}


def init_schema(c):
    c.executescript('''
        create table if not exists repro_sync_plans (
            id integer primary key autoincrement, protocol_key text not null,
            title text not null, start_at text not null, steps_json text not null,
            target_group text not null, veterinarian text not null default '',
            vet_fee_cents integer not null default 0, hormone_fee_cents integer not null default 0,
            notes text not null default '', status text not null default 'active',
            request_key text not null unique, revision integer not null default 1,
            created_at text not null, created_by text not null);
        create table if not exists repro_sync_animals (
            id integer primary key autoincrement, plan_id integer not null,
            animal_id integer not null, status text not null default 'active',
            finance_id integer, posted_at text, unique(plan_id,animal_id));
        create unique index if not exists idx_sync_one_active on repro_sync_animals(animal_id) where status='active';
        create table if not exists repro_sync_steps (
            id integer primary key autoincrement, enrollment_id integer not null,
            step_no integer not null, name text not null, kind text not null,
            hormone text not null default '', product text not null default '',
            dose text not null default '', unit text not null default '', route text not null default '',
            planned_at text not null, status text not null default 'pending',
            revision integer not null default 1,
            applied_at text, applied_by text, note text not null default '',
            health_id integer, insemination_id integer, unique(enrollment_id,step_no));
        create index if not exists idx_sync_steps_due on repro_sync_steps(status,planned_at);
        create table if not exists repro_sync_events (
            id integer primary key autoincrement, plan_id integer not null,
            enrollment_id integer, step_id integer, action text not null,
            detail text not null, created_at text not null, username text not null);
        create trigger if not exists delete_sync_plan after delete on repro_sync_plans begin
            delete from repro_sync_steps where enrollment_id in (select id from repro_sync_animals where plan_id=old.id);
            delete from repro_sync_animals where plan_id=old.id;
            delete from repro_sync_events where plan_id=old.id;
        end;
        create trigger if not exists delete_sync_animal after delete on animals begin
            update repro_sync_steps set status='cancelled' where status='pending' and enrollment_id in
                (select id from repro_sync_animals where animal_id=old.id);
            update repro_sync_animals set status='cancelled' where animal_id=old.id;
        end;
    ''')


def text_field(value, label, maximum=300):
    value = str(value or '').strip()
    if len(value)>maximum:
        raise ValueError(label+f' en fazla {maximum} karakter olabilir.')
    return value


def positive_id(value):
    if isinstance(value,bool) or not str(value).isdigit() or int(value)<=0:
        raise ValueError('Geçerli bir kayıt seçin.')
    return int(value)


def parse_time(value, label):
    try:
        result = datetime.fromisoformat(str(value))
        if result.tzinfo is not None or result.second or result.microsecond:
            raise ValueError()
        if not 2000<=result.year<=2100:
            raise ValueError()
        return result
    except (ValueError, TypeError):
        raise ValueError(label+' geçerli bir tarih ve saat olmalıdır.') from None


def cents(value):
    try:
        result = Decimal(str(value or '0').replace(',','.'))
        if not result.is_finite() or not 0<=result<=Decimal('10000000'):
            raise InvalidOperation()
        return int((result*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    except (InvalidOperation,ValueError):
        raise ValueError('Ücretler 0–10.000.000 TL arasında olmalıdır.') from None


def dose_value(value, required=False):
    raw = text_field(value,'Doz',30)
    if not raw and not required:
        return ''
    try:
        num = Decimal(raw.replace(',','.'))
        if not num.is_finite() or not 0<num<=1000000:
            raise InvalidOperation()
        return format(num,'f')
    except InvalidOperation:
        raise ValueError('Doz pozitif bir sayı olmalıdır; boşsa veteriner planından girin.') from None


def normalize_steps(value):
    try:
        rows = json.loads(value) if isinstance(value,str) else value
    except (ValueError,TypeError):
        raise ValueError('Uygulama adımları okunamadı.') from None
    if not isinstance(rows,list) or not 1<=len(rows)<=30:
        raise ValueError('1–30 uygulama adımı tanımlayın.')
    result=[]
    previous=-1
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError('Uygulama adımı geçersiz.')
        offset=row.get('offset_minutes')
        if isinstance(offset,bool) or not isinstance(offset,int) or not 0<=offset<=527040 or offset<previous:
            raise ValueError('Adımları başlangıçtan itibaren artan gün/saat sırasıyla girin (en çok 366 gün).')
        previous=offset
        name=text_field(row.get('name'),'Uygulama adı',120)
        kind=row.get('kind')
        if not name or kind not in KINDS:
            raise ValueError('Her adımın adını ve türünü girin.')
        result.append({'offset_minutes':offset,'name':name,'kind':kind,
            'hormone':text_field(row.get('hormone'),'Hormon',100),
            'product':text_field(row.get('product'),'Ürün',150),
            'dose':dose_value(row.get('dose')),'unit':text_field(row.get('unit'),'Birim',30),
            'route':text_field(row.get('route'),'Uygulama yolu',80)})
    return result


def animal_rows(ns,c,ids=None):
    """No calving history alone is never treated as proof of being a heifer."""
    condition=''
    params=[now().date().isoformat(),now().date().isoformat()]
    if ids is not None:
        if not ids:return []
        condition=' and a.id in ('+','.join('?' for _ in ids)+')'
        params.extend(ids)
    rows=c.execute('''select a.*,d.status dairy_status,
        (select max(birth_date) from calves where mother_id=a.id and birth_date<=?) calf_birth,
        (select max(birth_date) from animals where mother_id=a.id and birth_date<=?) animal_birth,
        (select id from inseminations where animal_id=a.id order by insemination_date desc,id desc limit 1) latest_ins,
        (select pregnancy_result from inseminations where animal_id=a.id order by insemination_date desc,id desc limit 1) latest_result,
        (select insemination_date from inseminations where animal_id=a.id order by insemination_date desc,id desc limit 1) latest_ins_date,
        (select plan_id from repro_sync_animals where animal_id=a.id and status='active') active_plan,
        exists(select 1 from animal_losses l where l.animal_id=a.id) lost
        from animals a left join animal_dairy_status d on d.animal_id=a.id
        where a.gender='Dişi' '''+condition+' order by a.tag',params).fetchall()
    out=[]
    for raw in rows:
        r=dict(raw)
        birth=max(r['calf_birth'] or '',r['animal_birth'] or '')
        r['last_birth']=birth
        r['postpartum_days']=(now().date()-datetime.fromisoformat(birth).date()).days if birth else None
        r['group']='postpartum' if birth else 'heifer' if r['dairy_status']=='heifer' else 'open'
        r['reason']=''
        if (r.get('status') or 'Aktif')!='Aktif' or r['lost']:
            r['reason']='Pasif / arşivde'
        elif ns['current_pregnancy_record'](c,r['id']):
            r['reason']='Gebe'
        elif r['latest_ins'] and (r['latest_ins_date'] or '')>=(birth or '') and (r['latest_result'] or '').strip().casefold() not in ('negatif','gebe değil','gebe degil','negatif (boş)'):
            r['reason']='Gebelik kontrolü / sonuç bekleniyor'
        elif (r.get('dry_since') or '') and r['dry_since']<=now().date().isoformat():
            r['reason']='Kuru dönem · üreme kontrolü gerekli'
        r['group_label']=GROUPS[r['group']] if r['group']!='postpartum' else f'Doğumdan {r["postpartum_days"]} gün'
        if r['group']=='open' and not birth:
            r['group_label']='Boş / doğum geçmişi belirtilmedi'
        out.append(r)
    return out


def validate_animals(ns,c,ids,protocol_key,group,plan_id=None):
    if not isinstance(ids,(tuple,list)) or not 1<=len(ids)<=300:
        raise ValueError('1–300 hayvan seçin.')
    ids=list(dict.fromkeys(positive_id(i) for i in ids))
    lookup={r['id']:r for r in animal_rows(ns,c,ids)}
    result=[]
    for aid in ids:
        r=lookup.get(aid)
        if not r:
            raise ValueError('Yalnız aktif yetişkin dişi hayvanlar seçilebilir.')
        reason=r['reason']
        if r['active_plan'] and r['active_plan']!=plan_id:
            reason='Aktif senkronizasyon planı var'
        if reason:
            raise ValueError(r['tag']+' · '+reason+'. Hiçbir kayıt değişmedi.')
        if group!='all' and group!=r['group'] and not (group=='open' and r['group']=='postpartum'):
            raise ValueError(r['tag']+' seçilen hayvan grubunda değil.')
        audience=PROTOCOLS[protocol_key]['audience']
        if audience=='heifer' and r['group']!='heifer':
            raise ValueError(r['tag']+' için önce Düve durumunu belirleyin veya veterinerin özel planını seçin.')
        if audience=='cow' and r['group']=='heifer':
            raise ValueError(r['tag']+' düve olarak kayıtlı. Düve takvimini veya veterinerin özel planını seçin.')
        result.append(r)
    return result


def log_event(c,pid,user,action,detail='',enrollment=None,task=None):
    c.execute('''insert into repro_sync_events(plan_id,enrollment_id,step_id,action,detail,created_at,username)
        values(?,?,?,?,?,?,?)''',(pid,enrollment,task,action,detail,stamp(now()),user))


def save_plan(ns,c,data,ids,username):
    key=data.get('protocol_key')
    if key not in PROTOCOLS:
        raise ValueError('Bir senkronizasyon takvimi seçin.')
    group=data.get('target_group','all')
    if group not in GROUPS:
        raise ValueError('Geçerli bir hayvan grubu seçin.')
    if data.get('veterinary_review')!='yes':
        raise ValueError('Takvim ve hayvan uygunluğunun veteriner planına göre kontrol edildiğini işaretleyin.')
    start=parse_time(data.get('start_at'),'Başlangıç')
    steps=normalize_steps(data.get('steps_json'))
    title=text_field(data.get('title') or PROTOCOLS[key]['name'],'Plan adı',150)
    vet=text_field(data.get('veterinarian'),'Veteriner hekim',150)
    notes=text_field(data.get('notes'),'Açıklama',2000)
    fees=(cents(data.get('vet_fee')),cents(data.get('hormone_fee')))
    pid=positive_id(data['id']) if data.get('id') else None
    token=text_field(data.get('request_key'),'İstek anahtarı',100)
    if not pid and len(token)<16:
        raise ValueError('Formun süresi doldu. Sayfayı yenileyin.')
    c.execute('BEGIN IMMEDIATE')
    if not pid:
        existing=c.execute('select id from repro_sync_plans where request_key=? and created_by=?',(token,username)).fetchone()
        if existing:
            return existing['id']
    old=c.execute('select * from repro_sync_plans where id=?',(pid,)).fetchone() if pid else None
    if pid:
        if not old or old['status']!='active':
            raise ValueError('Yalnız aktif planlar düzenlenebilir.')
        if str(old['revision'])!=str(data.get('revision')):
            raise ValueError('Plan başka bir ekranda değişti. Sayfayı yenileyin.')
        if c.execute('''select 1 from repro_sync_steps s join repro_sync_animals a on a.id=s.enrollment_id
            where a.plan_id=? and (s.status='done' or a.posted_at is not null) limit 1''',(pid,)).fetchone():
            raise ValueError('Başlatılmış planda her uygulamanın Düzenle alanını kullanın; planı yeniden oluşturmayın.')
    animals=validate_animals(ns,c,ids,key,group,pid)
    payload=(key,title,stamp(start),json.dumps(steps,ensure_ascii=False),group,vet,*fees,notes)
    if old:
        c.execute('''update repro_sync_plans set protocol_key=?,title=?,start_at=?,steps_json=?,target_group=?,
            veterinarian=?,vet_fee_cents=?,hormone_fee_cents=?,notes=?,revision=revision+1 where id=?''',(*payload,pid))
        c.execute('delete from repro_sync_steps where enrollment_id in (select id from repro_sync_animals where plan_id=?)',(pid,))
        c.execute('delete from repro_sync_animals where plan_id=?',(pid,))
    else:
        pid=c.execute('''insert into repro_sync_plans(protocol_key,title,start_at,steps_json,target_group,veterinarian,
            vet_fee_cents,hormone_fee_cents,notes,request_key,created_at,created_by) values(?,?,?,?,?,?,?,?,?,?,?,?)''',
            (*payload,token,stamp(now()),username)).lastrowid
    for animal in animals:
        eid=c.execute('insert into repro_sync_animals(plan_id,animal_id) values(?,?)',(pid,animal['id'])).lastrowid
        for n,s in enumerate(steps,1):
            planned=start+timedelta(minutes=s['offset_minutes'])
            c.execute('''insert into repro_sync_steps(enrollment_id,step_no,name,kind,hormone,product,dose,unit,route,planned_at)
                values(?,?,?,?,?,?,?,?,?,?)''',(eid,n,s['name'],s['kind'],s['hormone'],s['product'],s['dose'],s['unit'],s['route'],stamp(planned)))
    log_event(c,pid,username,'Plan düzenlendi' if old else 'Plan oluşturuldu',f'{len(animals)} hayvan · {len(steps)} adım')
    return pid


def update_states(c,pid):
    c.execute('''update repro_sync_animals set status='completed' where plan_id=? and status='active'
        and not exists(select 1 from repro_sync_steps where enrollment_id=repro_sync_animals.id and status='pending')''',(pid,))
    statuses=[r[0] for r in c.execute('select status from repro_sync_animals where plan_id=?',(pid,))]
    state='active' if 'active' in statuses else 'completed' if 'completed' in statuses else 'cancelled'
    c.execute('update repro_sync_plans set status=?,revision=revision+1 where id=?',(state,pid))


def task_record(c,tid):
    r=c.execute('''select s.*,a.plan_id,a.animal_id,a.status enrollment_status,p.status plan_status,
        p.veterinarian,p.title from repro_sync_steps s join repro_sync_animals a on a.id=s.enrollment_id
        join repro_sync_plans p on p.id=a.plan_id where s.id=?''',(positive_id(tid),)).fetchone()
    if not r:
        raise ValueError('Uygulama bulunamadı.')
    return dict(r)


def perform_action(ns,c,data,username):
    """All writes are serialized; repeated completion/finance POSTs are harmless."""
    action=data.get('action')
    pid=positive_id(data.get('plan_id'))
    c.execute('BEGIN IMMEDIATE')
    p=c.execute('select * from repro_sync_plans where id=?',(pid,)).fetchone()
    if not p:
        raise ValueError('Plan bulunamadı.')
    if action in ('complete','update_step'):
        s=task_record(c,data.get('step_id'))
        if s['plan_id']!=pid:
            raise ValueError('Uygulama bu plana ait değil.')
        if s['status']=='done' and action=='complete':
            return pid
        if s['status']!='pending' or p['status']!='active' or s['enrollment_status']!='active':
            raise ValueError('Bu uygulama kapatılmış. Sayfayı yenileyin.')
        if str(data.get('step_revision',''))!=str(s['revision']):
            raise ValueError('Uygulama başka bir ekranda değişti. Sayfayı yenileyin.')
        product=text_field(data.get('product',s['product']),'Ürün',150)
        dose=dose_value(data.get('dose',s['dose']),required=action=='complete' and s['kind']=='medicine')
        unit=text_field(data.get('unit',s['unit']),'Birim',30)
        route=text_field(data.get('route',s['route']),'Uygulama yolu',80)
        note=text_field(data.get('note'),'Uygulama notu',1000)
        if action=='update_step':
            planned=parse_time(data.get('planned_at'),'Uygulama')
            if not note:
                raise ValueError('Değişiklik nedenini / veteriner notunu girin.')
            before=c.execute('select max(planned_at) from repro_sync_steps where enrollment_id=? and step_no<?',(s['enrollment_id'],s['step_no'])).fetchone()[0]
            after=c.execute('select min(planned_at) from repro_sync_steps where enrollment_id=? and step_no>?',(s['enrollment_id'],s['step_no'])).fetchone()[0]
            if stamp(planned)<p['start_at'] or (before and stamp(planned)<before) or (after and stamp(planned)>after):
                raise ValueError('Yeni saat plan başlangıcından önce olamaz ve önceki / sonraki adımların sırasını değiştiremez.')
            c.execute('''update repro_sync_steps set planned_at=?,product=?,dose=?,unit=?,route=?,note=?,revision=revision+1 where id=?''',
                (stamp(planned),product,dose,unit,route,note,s['id']))
            c.execute('update repro_sync_plans set revision=revision+1 where id=?',(pid,))
            log_event(c,pid,username,'Uygulama düzenlendi',s['planned_at']+' → '+stamp(planned)+' · '+note,s['enrollment_id'],s['id'])
            return pid
        applied=parse_time(data.get('applied_at'),'Gerçekleşen uygulama')
        if applied>now():
            raise ValueError('Gelecekteki bir uygulama yapılmış olarak kaydedilemez.')
        lookup={r['id']:r for r in animal_rows(ns,c,[s['animal_id']])}
        animal=lookup.get(s['animal_id'])
        if not animal or (animal.get('status') or 'Aktif')!='Aktif' or animal['lost']:
            raise ValueError('Hayvan artık aktif değil; planını iptal edin.')
        reason=animal['reason']
        # An already recorded same-day insemination may be linked explicitly below.
        if reason and not (s['kind'] in ('check','insemination') and reason.startswith('Gebelik kontrolü')):
            raise ValueError(animal['tag']+' · '+reason+'. Önce üreme kaydını kontrol edin.')
        if s['kind']=='medicine' and (not product or not unit or not route):
            raise ValueError('Uygulamayı tamamlamak için veterinerin belirlediği ürün, doz, birim ve yolu girin.')
        if c.execute('''select 1 from repro_sync_steps where enrollment_id=? and status='pending'
            and planned_at<? and id<>? limit 1''',(s['enrollment_id'],s['planned_at'],s['id'])).fetchone():
            raise ValueError('Önce bu hayvanın önceki bekleyen adımlarını kaydedin veya planı veterinerle düzenleyin.')
        if applied<parse_time(p['start_at'],'Başlangıç'):
            raise ValueError('Gerçekleşen uygulama planın başlangıcından önce olamaz.')
        iid=None
        if s['kind']=='insemination':
            if data.get('confirm_insemination')!='yes':
                raise ValueError('Gerçek tohumlama kaydı oluşturma / bağlama seçeneğini işaretleyin.')
            day=applied.date().isoformat()
            existing=c.execute('select * from inseminations where animal_id=? and insemination_date=? order by id desc limit 1',(s['animal_id'],day)).fetchone()
            if existing:
                iid=existing['id']
            else:
                if animal['reason']:
                    raise ValueError('Önce önceki tohumlamanın gebelik sonucunu kontrol edin.')
                attempt=(c.execute('select max(attempt) from inseminations where animal_id=?',(s['animal_id'],)).fetchone()[0] or 0)+1
                if attempt>3:
                    raise ValueError('Üç tohumlama denemesi kayıtlı. Tohumlama ekranındaki mevcut kayıtları düzenleyin.')
                iid=c.execute('''insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date,bull_tag,bull_name,inseminator)
                    values(?,?,?,'Bekleniyor','',?,'',?)''',(s['animal_id'],attempt,day,
                    text_field(data.get('bull_tag'),'Boğa / sperma küpesi',100),text_field(data.get('inseminator') or p['veterinarian'],'Tohumlayan',150))).lastrowid
        detail=f"Senkronizasyon #{pid} · {p['title']} · {s['step_no']}. adım · {display_time(stamp(applied))} · {dose} {unit} · {route} · {p['veterinarian']}"
        if note:detail+=' · '+note
        hid=c.execute('''insert into health(animal_id,kind,product,applied_date,cost,notes)
            values(?,'Senkronizasyon',?,?,0,?)''',(s['animal_id'],product or s['name'],applied.date().isoformat(),detail)).lastrowid
        c.execute('''update repro_sync_steps set status='done',applied_at=?,applied_by=?,product=?,dose=?,unit=?,route=?,note=?,health_id=?,insemination_id=?,revision=revision+1 where id=?''',
            (stamp(applied),username,product,dose,unit,route,note,hid,iid,s['id']))
        log_event(c,pid,username,'Uygulandı',detail,s['enrollment_id'],s['id'])
        update_states(c,pid)
    elif action in ('cancel','cancel_animal'):
        reason=text_field(data.get('reason'),'İptal nedeni',1000)
        if not reason:
            raise ValueError('İptal nedenini girin.')
        if action=='cancel_animal':
            eid=positive_id(data.get('enrollment_id'))
            target=c.execute('select * from repro_sync_animals where id=? and plan_id=?',(eid,pid)).fetchone()
            if not target or target['status']!='active':
                raise ValueError('Bu hayvanın planı zaten kapatılmış.')
            c.execute("update repro_sync_steps set status='cancelled' where enrollment_id=? and status='pending'",(eid,))
            c.execute("update repro_sync_animals set status='cancelled' where id=?",(eid,))
        else:
            if p['status']!='active':
                raise ValueError('Bu plan zaten kapatılmış.')
            eid=None
            c.execute("update repro_sync_steps set status='cancelled' where status='pending' and enrollment_id in (select id from repro_sync_animals where plan_id=?)",(pid,))
            c.execute("update repro_sync_animals set status='cancelled' where plan_id=? and status='active'",(pid,))
        log_event(c,pid,username,'Hayvan planı iptal edildi' if eid else 'Plan iptal edildi',reason,eid)
        update_states(c,pid)
    elif action=='finance':
        if p['status']=='cancelled':
            raise ValueError('İptal edilmiş plandan yeni gider oluşturulamaz.')
        amount=p['vet_fee_cents']+p['hormone_fee_cents']
        if amount<=0:
            raise ValueError('Planda hayvan başı ücret tanımlı değil.')
        tx_date=parse_time(data.get('expense_at'),'Gider').date().isoformat()
        if tx_date>now().date().isoformat():
            raise ValueError('Gider tarihi gelecekte olamaz.')
        count=0
        for a in c.execute("select * from repro_sync_animals where plan_id=? and status<>'cancelled' and posted_at is null",(pid,)).fetchall():
            active=c.execute('select 1 from animals where id=?',(a['animal_id'],)).fetchone()
            if not active:continue
            fid=c.execute('''insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at)
                values(?,'Gider','Veteriner / Sağlık',?,?,'Nakit',?,?)''',(tx_date,amount/100,
                f"Senkronizasyon #{pid} · {p['title']} · Veteriner {p['vet_fee_cents']/100:.2f} TL + hormon {p['hormone_fee_cents']/100:.2f} TL",
                a['animal_id'],stamp(now()))).lastrowid
            c.execute('update repro_sync_animals set finance_id=?,posted_at=? where id=?',(fid,stamp(now()),a['id']))
            count+=1
        if count:
            c.execute('update repro_sync_plans set revision=revision+1 where id=?',(pid,))
            log_event(c,pid,username,'Finansa işlendi',f'{count} hayvan · Hayvan başı {amount/100:.2f} TL')
    elif action=='delete':
        if c.execute('''select 1 from repro_sync_steps s join repro_sync_animals a on a.id=s.enrollment_id
            where a.plan_id=? and (s.status='done' or a.posted_at is not null) limit 1''',(pid,)).fetchone():
            raise ValueError('Uygulaması veya finans kaydı bulunan plan silinemez; bekleyen adımları iptal edebilirsiniz.')
        c.execute('delete from repro_sync_plans where id=?',(pid,))
        return None
    else:
        raise ValueError('Geçersiz işlem.')
    return pid


def task_entries(ns,c,horizon_days=None):
    current=now()
    cutoff=(current.date()+timedelta(days=horizon_days)).isoformat() if horizon_days is not None else '9999-12-31'
    tasks=c.execute('''select s.*,a.animal_id,a.plan_id,p.title from repro_sync_steps s
        join repro_sync_animals a on a.id=s.enrollment_id join repro_sync_plans p on p.id=a.plan_id
        where s.status='pending' and a.status='active' and p.status='active' and substr(s.planned_at,1,10)<=?
        order by s.planned_at,a.animal_id,s.step_no''',(cutoff,)).fetchall()
    if not tasks:return []
    animals={r['id']:r for r in animal_rows(ns,c,list({r['animal_id'] for r in tasks}))}
    result=[]
    for raw in tasks:
        s=dict(raw);a=animals.get(s['animal_id'])
        if not a:continue
        reason=a['reason']
        if reason and not (s['kind'] in ('check','insemination') and reason.startswith('Gebelik kontrolü')):continue
        planned=parse_time(s['planned_at'],'Uygulama')
        state='overdue' if planned<current else 'today' if planned.date()==current.date() else 'upcoming'
        state_label='Saati geçti' if state=='overdue' else 'Bugün' if state=='today' else 'Yaklaşan'
        url='/synchronization?'+urlencode({'plan':s['plan_id'],'animal':s['animal_id']})+'#sync-step-'+str(s['id'])
        result.append({'date':planned.date().isoformat(),'planned_at':s['planned_at'],
            'subject':a['tag'],'task':'Senkronizasyon · '+s['name'],
            'detail':planned.strftime('%H:%M')+' · '+s['title']+(' · '+s['dose']+' '+s['unit'] if s['dose'] else ''),
            'state':state,'status':state_label+' · '+planned.strftime('%H:%M'),
            'source':'synchronization','key':'sync:'+str(s['id']),'url':url,'sync_plan_id':s['plan_id'],
            'sync_step_id':s['id'],'animal_id':s['animal_id']})
    return result


def hidden(name,value):
    return f'<input type="hidden" name="{esc(name)}" value="{esc(value)}">'


def action_form(token,pid,action,content,extra='',confirm=''):
    confirmation=f' data-sync-confirm="{esc(confirm)}"' if confirm else ''
    return f'<form method="post" action="/synchronization/action" class="sync-action-form"{confirmation}>'+hidden('csrf',token)+hidden('plan_id',pid)+hidden('action',action)+extra+content+'</form>'


def editor_markup(ns,c,query,token):
    raw_id=(query.get('edit') or [''])[0]
    plan=c.execute('select * from repro_sync_plans where id=?',(positive_id(raw_id),)).fetchone() if raw_id else None
    if raw_id and (not plan or plan['status']!='active'):
        raise ValueError('Aktif plan bulunamadı.')
    p=dict(plan) if plan else {}
    ids=[r[0] for r in c.execute('select animal_id from repro_sync_animals where plan_id=?',(p.get('id',0),))]
    if not p and (query.get('animal') or [''])[0].isdigit():ids=[int(query['animal'][0])]
    selected_key=p.get('protocol_key','')
    protocol_options='<option value="">Takvim seçin</option>'+''.join(f'<option value="{key}" {"selected" if key==selected_key else ""}>{esc(v["name"])}</option>' for key,v in PROTOCOLS.items())
    group=p.get('target_group','all')
    group_options=''.join(f'<option value="{key}" {"selected" if key==group else ""}>{label}</option>' for key,label in GROUPS.items())
    listing=''
    for a in animal_rows(ns,c):
        if (a.get('status') or 'Aktif')!='Aktif' or a['lost']:continue
        reason=a['reason'] or ('Aktif senkronizasyon planı var' if a['active_plan'] and a['active_plan']!=p.get('id') else '')
        tags=' '.join(str(a.get(k) or '') for k in ('tag','nickname','paddock'))
        checked=' checked' if a['id'] in ids else ''
        disabled=' disabled' if reason else ''
        memberships=a['group']+(' open' if a['group']=='postpartum' else '')
        listing+=f'<label class="sync-animal-row" data-sync-search="{esc(tags)}" data-sync-group="{memberships}" data-sync-eligible="{0 if reason else 1}"><input type="checkbox" name="animal_id" value="{a["id"]}"{checked}{disabled}><span><b>{esc(a["tag"])}</b><small>{esc(a.get("nickname") or a.get("paddock") or "Padoksuz")} · {esc(a["group_label"])}</small>{"<small class=sync-blocked>"+esc(reason)+"</small>" if reason else ""}</span></label>'
    settings=ns['reproduction_settings']()
    data={'protocols':PROTOCOLS,'steps':json.loads(p['steps_json']) if p else [],'vwp_day':settings['vwp_day']}
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    is_open=bool(raw_id or (query.get('new') or [''])[0]=='1')
    return f'''<dialog id="syncEditor" class="sync-editor" {"data-open" if is_open else ""}><div class="sync-editor-head"><div><small>ÜREME YÖNETİMİ</small><h2>{'Senkronizasyonu Düzenle' if p else 'Senkronizasyon Tanımla'}</h2></div><button type="button" class="sync-close" data-sync-close aria-label="Kapat">×</button></div>
      <form method="post" action="/synchronization/save" id="syncPlanForm" class="sync-form">
      {hidden('csrf',token)}{hidden('id',p.get('id',''))}{hidden('revision',p.get('revision',''))}{hidden('request_key',secrets.token_urlsafe(24))}
      <input type="hidden" name="steps_json" id="syncStepsJson"><div id="syncFormError" class="sync-error" role="alert" hidden></div>
      <div class="sync-fields"><label>Senkronizasyon takvimi *<select name="protocol_key" id="syncProtocol" required>{protocol_options}</select></label><label>Plan adı<input name="title" value="{esc(p.get('title',''))}" maxlength="150" placeholder="Örn. Ekim doğum sonrası grup"></label><label>Başlangıç tarihi ve saati *<input type="datetime-local" name="start_at" id="syncStart" value="{esc(p.get('start_at',stamp(now())))}" required></label><label>Hayvan grubu<select name="target_group" id="syncGroup">{group_options}</select></label></div>
      <p class="sync-note">Başlangıç saatinden uygulama takvimi hesaplanır. Hazır takvimler zamanlama şablonudur; ürün, doz ve uygulama yolunu veteriner planından girin.</p>
      <details class="sync-picker" open><summary>Uygulama yapılacak hayvanlar <b id="syncSelectedCount">0 seçili</b></summary><input type="search" id="syncAnimalSearch" placeholder="Küpe, ad veya padok ara" aria-label="Hayvan ara"><div class="sync-picker-tools"><button type="button" class="btn alt" id="syncSelectVisible">Görünen uygunları seç</button><button type="button" class="btn alt" id="syncClearSelection">Seçimi temizle</button></div><div class="sync-animal-list">{listing or '<p>Aktif dişi hayvan bulunamadı.</p>'}</div><small>Doğum sonrası gün, uygunluk kararı yerine geçmez. İşletmenin kayıtlı bekleme süresi {settings['vwp_day']} gündür; başlangıcı veterinerinizle belirleyin.</small></details>
      <div class="sync-section-title"><h3>Uygulama takvimi</h3><button type="button" id="syncAddStep" class="btn alt">＋ Adım ekle</button></div><p class="sync-note" id="syncTemplateNote">Takvim seçerek başlayın.</p><div id="syncStepEditor" class="sync-step-editor"></div>
      <div class="sync-fields"><label>Veteriner hekim<input name="veterinarian" maxlength="150" value="{esc(p.get('veterinarian',''))}" placeholder="Veteriner hekim adı"></label><label>Hayvan başı veteriner ücreti (TL)<input type="number" name="vet_fee" min="0" step="0.01" max="10000000" value="{p.get('vet_fee_cents',0)/100:g}" inputmode="decimal"></label><label>Hayvan başı hormon / ilaç ücreti (TL)<input type="number" name="hormone_fee" min="0" max="10000000" step="0.01" value="{p.get('hormone_fee_cents',0)/100:g}" inputmode="decimal"></label><label class="sync-full">Açıklama<textarea name="notes" rows="2" maxlength="2000" placeholder="Veteriner planı, muayene notu…">{esc(p.get('notes',''))}</textarea></label></div>
      <p class="sync-note" id="syncCostPreview">Plan kaydı gider oluşturmaz. Gerçek gideri plan ayrıntısından ayrıca işleyebilirsiniz.</p><label class="sync-review"><input type="checkbox" name="veterinary_review" value="yes" required><span>Hayvanların uygunluğunu, takvimi ve uygulama bilgilerini veteriner planına göre kontrol ettim.</span></label><div class="sync-editor-footer"><button type="button" class="btn alt" data-sync-close>Vazgeç</button><button type="submit" class="btn" id="syncSave">{'Değişiklikleri Kaydet' if p else 'Senkronizasyon Tanımla'}</button></div></form><script type="application/json" id="syncEditorData">{payload}</script></dialog>'''


def step_markup(s,p,animal,token):
    done=s['status']=='done';pending=s['status']=='pending'
    status='Yapıldı' if done else 'İptal' if not pending else 'Saati geçti' if s['planned_at']<stamp(now()) else 'Bekliyor'
    amount=' '.join(x for x in (s['product'] or s['hormone'],s['dose'],s['unit'],s['route']) if x)
    form=''
    reason=animal.get('reason','')
    blocked=reason and not (s['kind'] in ('check','insemination') and reason.startswith('Gebelik kontrolü'))
    if pending and p['status']=='active' and animal['enrollment_status']=='active':
        extra=hidden('step_id',s['id'])+hidden('step_revision',s['revision'])
        fields=f'''<div class="sync-fields"><label>Ürün<input name="product" value="{esc(s['product'])}" maxlength="150" {'required' if s['kind']=='medicine' else ''}></label><label>Doz<input name="dose" value="{esc(s['dose'])}" inputmode="decimal" maxlength="30" {'required' if s['kind']=='medicine' else ''}></label><label>Birim<input name="unit" value="{esc(s['unit'])}" placeholder="ml, mg, µg, adet…" maxlength="30" {'required' if s['kind']=='medicine' else ''}></label><label>Uygulama yolu<input name="route" value="{esc(s['route'])}" maxlength="80" {'required' if s['kind']=='medicine' else ''}></label></div>'''
        ai=''
        if s['kind']=='insemination':
            ai='<label class="sync-review"><input type="checkbox" name="confirm_insemination" value="yes" required><span>Gerçek tohumlama kaydını oluştur / aynı günkü kaydı bağla.</span></label><div class="sync-fields"><label>Boğa / sperma küpesi<input name="bull_tag" maxlength="100"></label><label>Tohumlayan<input name="inseminator" maxlength="150" value="'+esc(p['veterinarian'])+'"></label></div>'
        if not blocked:
            form+='<details class="sync-step-entry"><summary>✓ '+('Tohumlamayı kaydet' if s['kind']=='insemination' else 'Uygulamayı kaydet')+'</summary>'+action_form(token,p['id'],'complete',fields+f'<label>Gerçekleşen tarih ve saat<input type="datetime-local" name="applied_at" value="{stamp(now())}" max="{stamp(now())}" required></label><label>Uygulama notu<textarea name="note" maxlength="1000" rows="2"></textarea></label>'+ai+'<p class="sync-note">Gerçekleşen saat kaydedilir; sonraki uygulama saatleri değişmez.</p><button class="btn">'+('Tohumlamayı Kaydet ve Tamamla' if s['kind']=='insemination' else 'Yapıldı Olarak Kaydet')+'</button>',extra)+'</details>'
        form+='<details class="sync-step-edit"><summary>Düzenle</summary>'+action_form(token,p['id'],'update_step',fields+f'<label>Planlanan tarih ve saat<input type="datetime-local" name="planned_at" value="{esc(s["planned_at"])}" required></label><label>Değişiklik nedeni / veteriner notu<textarea name="note" maxlength="1000" rows="2" required></textarea></label><p class="sync-note">Bu değişiklik yalnız bu hayvanın bu adımına uygulanır.</p><button class="btn alt">Uygulamayı Güncelle</button>',extra)+'</details>'
    applied=f'<small>Gerçekleşen: {display_time(s["applied_at"])} · {esc(s["applied_by"])}{(" · "+esc(s["note"])) if s["note"] else ""}</small>' if done else ''
    insem=f'<a href="/inseminations?animal={animal["animal_id"]}">Tohumlama kaydı ›</a>' if s['insemination_id'] else ''
    return f'<article class="sync-step {"done" if done else "late" if status=="Saati geçti" else ""}" id="sync-step-{s["id"]}"><span class="sync-step-number">{s["step_no"]}</span><div class="sync-step-content"><div class="sync-step-title"><b>{esc(s["name"])}</b><span class="sync-badge">{status}</span></div><time>{display_time(s["planned_at"])}</time><small>{esc(amount or KINDS[s["kind"]])}</small>{applied}{insem}{form}</div></article>'


def detail_markup(ns,c,pid,query,token):
    raw=c.execute('select * from repro_sync_plans where id=?',(positive_id(pid),)).fetchone()
    if not raw:
        raise ValueError('Senkronizasyon planı bulunamadı.')
    p=dict(raw)
    animals=[dict(r) for r in c.execute('''select a.*,coalesce(an.tag,'Silinmiş hayvan') tag,
        a.status enrollment_status from repro_sync_animals a left join animals an on an.id=a.animal_id
        where a.plan_id=? order by an.tag''',(p['id'],))]
    lookup={r['id']:r for r in animal_rows(ns,c)}
    selected=(query.get('animal') or [''])[0]
    cards=''
    for a in animals:
        live=lookup.get(a['animal_id'],{})
        a['reason']=live.get('reason','Hayvan silinmiş / aktif değil' if a['tag']=='Silinmiş hayvan' else '')
        tasks=[dict(r) for r in c.execute('select * from repro_sync_steps where enrollment_id=? order by step_no',(a['id'],))]
        complete=sum(s['status']=='done' for s in tasks)
        focus=' data-sync-focus' if str(a['animal_id'])==selected else ''
        warning=f'<p class="sync-error">{esc(a["reason"])} · Uygulamadan önce üreme / hayvan kaydını kontrol edin.</p>' if a['reason'] and a['enrollment_status']=='active' else ''
        cancel=''
        if a['enrollment_status']=='active':
            cancel='<details class="sync-cancel"><summary>Bu hayvanın planını iptal et</summary>'+action_form(token,p['id'],'cancel_animal','<label>İptal nedeni<input name="reason" maxlength="1000" required></label><button class="btn alt">Hayvan Planını İptal Et</button>',hidden('enrollment_id',a['id']),'Bu hayvanın bekleyen uygulamaları iptal edilsin mi?')+'</details>'
        finance=f'<a href="/finance/edit?id={a["finance_id"]}">Finans kaydı ›</a>' if a['posted_at'] else ''
        cards+=f'<details class="sync-animal-detail"{focus} {"open" if len(animals)==1 or str(a["animal_id"])==selected else ""}><summary><span><b>{esc(a["tag"])}</b><small>{STATES[a["enrollment_status"]]} · {complete}/{len(tasks)} uygulama</small></span><span>⌄</span></summary><div class="sync-animal-body"><a href="/animal?id={a["animal_id"]}">Hayvan kartı ›</a>{finance}{warning}<div class="sync-timeline">'+''.join(step_markup(s,p,a,token) for s in tasks)+f'</div>{cancel}</div></details>'
    started=c.execute('''select 1 from repro_sync_steps s join repro_sync_animals a on a.id=s.enrollment_id
        where a.plan_id=? and (s.status='done' or a.posted_at is not null) limit 1''',(p['id'],)).fetchone()
    controls=''
    if not started and p['status']=='active':controls+=f'<a class="btn alt" href="/synchronization?edit={p["id"]}">Planı Düzenle</a>'
    if not started:controls+=action_form(token,p['id'],'delete','<button class="btn alt">Planı Sil</button>',confirm='Uygulama ve gider içermeyen bu plan silinsin mi?')
    fees=p['vet_fee_cents']+p['hormone_fee_cents']
    unposted=sum(not a['posted_at'] and a['enrollment_status']!='cancelled' and a['tag']!='Silinmiş hayvan' for a in animals)
    finance=''
    if fees and unposted and p['status']!='cancelled':
        finance='<details class="sync-finance"><summary>Gideri finansa işle · '+esc(ns['money'](fees/100*unposted))+'</summary>'+action_form(token,p['id'],'finance',f'<p>{unposted} hayvan × {esc(ns["money"](fees/100))}. Her hayvana bir gider kaydı eklenir.</p><label>Gider tarihi ve saati<input type="datetime-local" name="expense_at" value="{stamp(now())}" max="{stamp(now())}" required></label><button class="btn">Gideri Finansa İşle</button>',confirm='Gösterilen toplam tutar nakit gider olarak finansa işlensin mi?')+'</details>'
    cancellation=''
    if p['status']=='active':cancellation='<details class="sync-cancel"><summary>Planın kalanını iptal et</summary>'+action_form(token,p['id'],'cancel','<label>İptal nedeni<input name="reason" maxlength="1000" required></label><button class="btn alt">Bekleyen Uygulamaları İptal Et</button>',confirm='Plandaki tüm bekleyen uygulamalar iptal edilsin mi?')+'</details>'
    events=''.join(f'<li><b>{esc(r["action"])}</b><span>{display_time(r["created_at"])} · {esc(r["username"])}</span><small>{esc(r["detail"])}</small></li>' for r in c.execute('select * from repro_sync_events where plan_id=? order by id desc limit 100',(p['id'],)))
    return f'''<section class="sync-detail"><a class="sync-back" href="/synchronization">‹ Tüm planlar</a><header class="sync-page-head"><div><small>{esc(PROTOCOLS.get(p['protocol_key'],{}).get('name','Özel plan'))}</small><h1>{esc(p['title'])}</h1><p>{display_time(p['start_at'])} · {len(animals)} hayvan · {STATES[p['status']]}</p></div><div class="sync-actions">{controls}</div></header><div class="sync-plan-meta"><span><b>Veteriner</b>{esc(p['veterinarian'] or 'Belirtilmedi')}</span><span><b>Hayvan başı planlanan ücret</b>{esc(ns['money'](fees/100))}</span><span><b>Plan toplamı</b>{esc(ns['money'](fees/100*len(animals)))}</span></div><p class="sync-note">{esc(p['notes'])}</p>{finance}<p class="sync-note">Uygulamaları her hayvanın kartından kaydedin. Saatler Türkiye saatidir. Sonraki adımlar gecikmeyle otomatik kaydırılmaz.</p>{cards}{cancellation}<details class="sync-history"><summary>İşlem geçmişi</summary><ol>{events or '<li>İşlem yok.</li>'}</ol></details></section>'''


def page_markup(ns,query,token):
    with ns['db']() as c:
        if (query.get('plan') or [''])[0]:
            content=detail_markup(ns,c,query['plan'][0],query,token)
            editor=''
        else:
            filt=(query.get('status') or ['active'])[0]
            if filt not in ('active','completed','cancelled','all'):filt='active'
            term=text_field((query.get('q') or [''])[0],'Arama',150)
            plans=[dict(r) for r in c.execute('''select p.*,count(a.id) animal_count,
                (select min(s.planned_at) from repro_sync_steps s join repro_sync_animals x on x.id=s.enrollment_id
                 where x.plan_id=p.id and x.status='active' and s.status='pending') next_at,
                group_concat(an.tag,' · ') tags from repro_sync_plans p left join repro_sync_animals a on a.plan_id=p.id
                left join animals an on an.id=a.animal_id group by p.id order by p.id desc''')]
            counts={key:sum(p['status']==key for p in plans) for key in STATES}
            tabs=''.join(f'<a class="{"active" if filt==key else ""}" href="/synchronization?{urlencode({"status":key,"q":term})}">{label} <b>{len(plans) if key=="all" else counts[key]}</b></a>' for key,label in [('active','Aktif'),('completed','Tamamlanan'),('cancelled','İptal'),('all','Tümü')])
            cards=''
            norm=lambda s:str(s or '').replace('I','ı').replace('İ','i').casefold()
            for p in plans:
                if filt!='all' and p['status']!=filt:continue
                if term and norm(term) not in norm(p['title']+' '+(p['tags'] or '')+' '+p['veterinarian']):continue
                cards+=f'<a class="sync-plan-card" href="/synchronization?plan={p["id"]}"><span class="sync-plan-icon">↻</span><div><span class="sync-card-top"><b>{esc(p["title"])}</b><span class="sync-badge">{STATES[p["status"]]}</span></span><p>{p["animal_count"]} hayvan · Başlangıç {display_time(p["start_at"])}</p><small>{esc(p["tags"] or "")}</small><span class="sync-next">{("Sıradaki uygulama · "+display_time(p["next_at"])) if p["next_at"] else "Bekleyen uygulama yok"}</span></div><span>›</span></a>'
            content=f'''<header class="sync-page-head"><div><small>ÜREME & SAĞLIK</small><h1>Senkronizasyon</h1><p>Doğum sonrası inekler, düveler ve boş inekler.</p></div><button class="btn" type="button" data-sync-open>＋ Senkronizasyon Tanımla</button></header><nav class="sync-tabs">{tabs}</nav><form method="get" class="sync-search"><input type="hidden" name="status" value="{filt}"><input type="search" name="q" placeholder="Plan adı, küpe veya veteriner ara" value="{esc(term)}"><button class="btn alt">Ara</button></form><div class="sync-plan-list">{cards or '<div class="sync-empty"><span>↻</span><h2>Bu görünümde senkronizasyon planı yok</h2><p>Hayvanları seçin, veterinerin belirlediği takvimi tanımlayın.</p><button class="btn alt" type="button" data-sync-open>İlk planı oluştur</button></div>'}</div>'''
            editor=editor_markup(ns,c,query,token)
    return '<link rel="stylesheet" href="/app-assets/synchronization.css?v=2.0.41"><section class="sync-workspace">'+content+'</section>'+editor+'<script src="/app-assets/synchronization.js?v=2.0.41" defer></script>'


def csrf_token(handler):
    return hmac.new(SECRET,str(handler.parse_cookie()).encode(),hashlib.sha256).hexdigest()


def install(ns):
    original_init=ns['init_db']
    def init_db(*args,**kwargs):
        result=original_init(*args,**kwargs)
        with ns['db']() as c:init_schema(c)
        return result
    ns['init_db']=init_db
    original_entries=ns['health_plan_entries']
    def health_plan_entries(c,horizon_days=None):
        rows=original_entries(c,horizon_days)
        rows.extend(task_entries(ns,c,horizon_days))
        return sorted(rows,key=lambda r:(r['date'],r.get('planned_at',''),str(r['subject']),r['key']))
    ns['health_plan_entries']=health_plan_entries
    original_page=ns['page']
    def page(title,body,path='/',user='admin',flash=''):
        if path=='/reproduction-center':
            # Keep the entry beside the other reproduction actions.
            anchor='<a class="btn alt" href="/inseminations">＋ Tohumlama</a>'
            entry='<a class="btn alt cp-repro-sync" href="/synchronization">↻ Senkronizasyon</a>'
            body=body.replace(anchor,anchor+entry,1)
        return original_page(title,body,path,user,flash)
    ns['page']=page
    cls=ns['App'];original_get,original_post=cls.do_GET,cls.do_POST
    original_send_html=cls.send_html
    def send_html(self,document,status=200,headers=None):
        # Mobile animal cards are added by the previous send_html wrapper.
        # The shared shortcut is inserted before it so both presentations expose it.
        path=urlparse(self.path).path
        if path=='/animal' and self.user():
            aid=(parse_qs(urlparse(self.path).query).get('id') or [''])[0]
            if aid.isdigit():
                with ns['db']() as c:
                    animal=c.execute("select id from animals where id=? and gender='Dişi' and coalesce(status,'Aktif')='Aktif'",(int(aid),)).fetchone()
                if animal:
                    link='<p class="sync-animal-shortcut"><a class="btn alt" href="/synchronization?new=1&amp;animal='+aid+'">↻ Senkronizasyon Tanımla</a></p>'
                    document=document.replace('</main>',link+'</main>',1)
        return original_send_html(self,document,status,headers)
    cls.send_html=send_html
    def authorized(handler):
        if not handler.require():return False
        allowed,_,message=ns['license_status']()
        if not allowed:
            handler.redirect('/license',message)
            return False
        return True
    def do_GET(self):
        if urlparse(self.path).path!='/synchronization':return original_get(self)
        if not authorized(self):return
        query=parse_qs(urlparse(self.path).query)
        try:
            body=page_markup(ns,query,csrf_token(self))
            body=body.replace('<section class="sync-workspace">','<section class="sync-workspace"><a class="sync-back" href="/reproduction-center">‹ Üreme Yönetimi</a>',1)
        except ValueError as exc:return self.redirect('/synchronization',str(exc))
        return self.send_html(ns['page']('Senkronizasyon',body,'/synchronization',self.user()['username'],(query.get('msg') or [''])[0]))
    def do_POST(self):
        path=urlparse(self.path).path
        if path not in ('/synchronization/save','/synchronization/action'):return original_post(self)
        if not authorized(self):return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=262144:raise ValueError('Gönderilen plan çok büyük veya geçersiz.')
            form=parse_qs(self.rfile.read(length).decode('utf-8'),keep_blank_values=True,max_num_fields=400)
            data={k:v[0] for k,v in form.items()}
            if not hmac.compare_digest(data.get('csrf',''),csrf_token(self)):
                raise ValueError('Oturum değişti. Sayfayı yenileyerek tekrar deneyin.')
            with ns['db']() as c:
                pid=save_plan(ns,c,data,form.get('animal_id',[]),self.user()['username']) if path.endswith('/save') else perform_action(ns,c,data,self.user()['username'])
        except (ValueError,TypeError,OverflowError,UnicodeDecodeError) as exc:
            return self.redirect('/synchronization',str(exc))
        ns['audit'](self.user()['username'],'Senkronizasyon',f'Plan {pid or "silindi"}',self.client_ip())
        return self.redirect('/synchronization'+('?plan='+str(pid) if pid else ''),'Senkronizasyon kaydı güncellendi.')
    cls.do_GET,cls.do_POST=do_GET,do_POST
