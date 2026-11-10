"""Tape-based estimates, kept separate from recorded scale weights."""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from html import escape
import re

# Beef cattle tape formula: girth(in)² × length(in) / 300 gives pounds.
# University of Arizona Cooperative Extension, How Much Does Your Animal Weigh?
KG_DIVISOR = Decimal(300) * Decimal('2.54')**3 / Decimal('0.45359237')
METHOD = 'beef_tape_300_v1'


def identifier(value):
    if not re.fullmatch(r'[1-9][0-9]{0,18}', str(value or '')):
        raise ValueError('Kayıt numarası geçersiz.')
    result = int(value)
    if result >= 2**63:
        raise ValueError('Kayıt numarası geçersiz.')
    return result


def centimeters(value):
    value = str(value or '').strip()
    if not re.fullmatch(r'[0-9]{1,3}(?:[.,][0-9]{1,2})?', value):
        raise ValueError('Ölçüleri santimetre olarak girin (örnek: 165,5).')
    return Decimal(value.replace(',', '.'))


def save(connection, animal_id, fields, today):
    measure_date = fields.get('measure_date', '')
    try:
        measured = date.fromisoformat(measure_date)
    except (TypeError, ValueError):
        raise ValueError('Ölçüm tarihi geçersiz.') from None
    if measured.isoformat() != measure_date or measured > today:
        raise ValueError('Geçerli bir ölçüm tarihi seçin; ileri tarih kullanılamaz.')
    girth = centimeters(fields.get('girth_cm'))
    length = centimeters(fields.get('length_cm'))
    if not (50 <= girth <= 300 and 50 <= length <= 250):
        raise ValueError('Göğüs çevresi 50–300 cm, gövde uzunluğu 50–250 cm arasında olmalı.')
    result = (girth*girth*length/KG_DIVISOR).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    # Keep the active-animal check and the write in one transaction.
    connection.execute('begin immediate')
    animal = connection.execute('select status from animals where id=?', (animal_id,)).fetchone()
    if not animal or animal['status'] != 'Aktif':
        raise ValueError('Tahmin yalnız aktif hayvanlara kaydedilebilir.')
    connection.execute('''
        insert into weight_estimates(animal_id,measure_date,girth_cm,length_cm,estimated_kg,method,notes)
        values(?,?,?,?,?,?,?)
        on conflict(animal_id,measure_date) do update set
            girth_cm=excluded.girth_cm,length_cm=excluded.length_cm,
            estimated_kg=excluded.estimated_kg,method=excluded.method,notes=excluded.notes
        ''', (animal_id, measure_date, float(girth), float(length), float(result),
              METHOD, str(fields.get('notes') or '').strip()[:300]))
    return result


def panel(animal_id, records, active, token, today, fmt_date):
    hidden = (f'<input type="hidden" name="animal_id" value="{int(animal_id)}">'
              f'<input type="hidden" name="csrf" value="{escape(token)}">')
    form = ''
    if active:
        form = f'''<details class="weight-estimate-entry"><summary>Mezuradan Tahmin Ekle / Düzelt</summary>
        <p class="mut">Güvenli sabitleme varsa göğüs çevresini ön bacakların hemen arkasından, gövde uzunluğunu omuz ucundan sağrı ucuna ölçün.</p>
        <form method="post" action="/animal/estimate-weight" class="form" data-submit-lock="1" data-weight-estimate data-divisor="{float(KG_DIVISOR)}">
        {hidden}
        <label>Göğüs Çevresi (cm)<input name="girth_cm" inputmode="decimal" required maxlength="6" placeholder="Örn. 160"></label>
        <label>Gövde Uzunluğu (cm)<input name="length_cm" inputmode="decimal" required maxlength="6" placeholder="Örn. 130"></label>
        <label>Ölçüm Tarihi<input type="date" name="measure_date" value="{today}" max="{today}" required></label>
        <label>Not (isteğe bağlı)<input name="notes" maxlength="300"></label>
        <div class="full"><output class="weight-estimate-preview" aria-live="polite" hidden></output>
        <p class="mut">Aynı tarih için yeniden kaydederseniz o günün tahmini güncellenir.</p>
        <button type="submit" class="btn">Tahmini Ağırlığı Kaydet</button></div></form></details>
        <script>(()=>{{
          const form=document.querySelector('[data-weight-estimate]');if(!form)return;
          const out=form.querySelector('output'), num=new Intl.NumberFormat('tr-TR',{{minimumFractionDigits:1,maximumFractionDigits:1}});
          const read=name=>{{const v=form.elements[name].value.trim();return /^[0-9]{{1,3}}([.,][0-9]{{1,2}})?$/.test(v)?Number(v.replace(',','.')):NaN;}};
          function preview(){{
            const g=read('girth_cm'),l=read('length_cm');
            const valid=g>=50&&g<=300&&l>=50&&l<=250;
            out.hidden=!valid;
            out.textContent=valid?'Tahmini ağırlık: ≈ '+num.format(g*g*l/Number(form.dataset.divisor))+' kg':'';
          }}
          form.addEventListener('input',preview);preview();
        }})();</script>'''
    history = []
    for row in records:
        kg = f"{row['estimated_kg']:.1f}".replace('.', ',')
        girth = f"{row['girth_cm']:g}".replace('.', ',')
        length = f"{row['length_cm']:g}".replace('.', ',')
        notes = f'<small>{escape(row["notes"])}</small>' if row['notes'] else ''
        deletion = f'''<form method="post" action="/animal/estimate-weight/delete" onsubmit="return confirm('Bu tahmini ağırlık silinsin mi?')">
        {hidden}<input type="hidden" name="estimate_id" value="{row['id']}"><button type="submit" class="btn alt">Sil</button></form>'''
        history.append(f'''<li><div><b>≈ {kg} kg</b> · {fmt_date(row['measure_date'])}
        <small>Mezura · Göğüs {girth} cm · Gövde {length} cm</small>{notes}</div>{deletion}</li>''')
    records_html = '<ul class="weight-estimate-list">'+''.join(history)+'</ul>' if history else '<p class="mut">Henüz tahmin kaydı yok.</p>'
    return f'''<section class="card panel-card weight-estimates"><h2>Tahmini Ağırlık</h2>
    <p class="mut">Mezura ile hesaplanır. Tartım geçmişine ve günlük canlı ağırlık artışına katılmaz.</p>{form}{records_html}</section>'''
