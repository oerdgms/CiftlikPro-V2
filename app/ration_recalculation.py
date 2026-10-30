"""Preview and apply a new solution to the same beef ration, with stale-write checks."""
import hashlib
import json
import math
import secrets
from datetime import datetime, timedelta, date
from html import escape
from urllib.parse import urlencode


def init_schema(c):
    c.execute('''create table if not exists ration_recalc_previews(
        token TEXT PRIMARY KEY, username TEXT NOT NULL, ration_id INTEGER NOT NULL,
        created_at TEXT NOT NULL, payload TEXT NOT NULL)''')


def state(ns, c, rid):
    row = c.execute('select * from rations where id=? and active=1', (rid,)).fetchone()
    if not row or str(row['ration_type'] or 'Besi') == 'Süt':
        raise ValueError('Aktif besi rasyonu bulunamadı.')
    summary = ns['ration_summary'](rid, c)
    feeds = [dict(feed) for feed in summary['items']]
    if len(feeds) < 2:
        raise ValueError('Yeniden hesaplamak için rasyonda en az iki yem olmalıdır.')
    if any(not int(feed.get('active', 1) or 0) for feed in feeds):
        raise ValueError('Rasyonda pasif yem var; önce yem seçimini güncelleyin.')
    ration = dict(row)
    encoded = json.dumps({'ration': ration, 'feeds': feeds, 'date': date.today().isoformat()}, sort_keys=True, ensure_ascii=False)
    return ration, feeds, hashlib.sha256(encoded.encode()).hexdigest(), summary


def prepare(ns, rid, username, weight, percent):
    with ns['db']() as c:
        ration, feeds, fingerprint, before = state(ns, c, rid)
    weight = float(str(weight if weight not in ('', None) else ration['target_weight_kg']).replace(',', '.'))
    percent = ns['beef_dm_percentage'](percent if percent not in ('', None) else ration['target_dm_pct_bw'])
    if not math.isfinite(weight) or not 150 <= weight <= 900:
        raise ValueError('Canlı ağırlık 150–900 kg arasında olmalıdır.')
    locked = {int(f['id']): float(f['kg_per_head_day']) for f in feeds if f['locked']}
    solved, targets, warning = ns['solve_smart_ration'](feeds, weight, float(ration['target_adg_kg']),
        ration['animal_type'], float(ration['target_age_months'] or 0), ration['target_beef_phase'] or 'Otomatik',
        percent, fixed_quantities=locked)
    if not solved:
        raise ValueError(warning or 'Mevcut yemlerle hedefleri karşılayan çözüm bulunamadı.')
    quantities, metrics, _ = solved
    if len(quantities) != len(feeds) or any(not math.isfinite(float(q)) or q < 0 for q in quantities):
        raise ValueError('Hesap sonucu geçersiz; mevcut rasyon korunuyor.')
    for feed, qty in zip(feeds, quantities):
        if feed['locked'] and abs(qty - float(feed['kg_per_head_day'])) > 1e-9:
            raise ValueError('Kilitli yem miktarı korunamadı; mevcut rasyon değişmedi.')
    payload = {'fingerprint': fingerprint, 'weight': weight, 'percent': percent,
        'name': ration['name'], 'warning': warning or '', 'target_dm': targets['dmi_kg'],
        'before': {k: before[k] for k in ('dm_kg', 'cp_pct_dm', 'cost')},
        'after': {k: metrics[k] for k in ('dm_kg', 'cp_pct_dm', 'cost')},
        'items': [{'item_id': f['item_id'], 'feed_id': f['id'], 'name': f['name'],
            'before': float(f['kg_per_head_day']), 'after': float(q), 'locked': int(f['locked'])}
            for f, q in zip(feeds, quantities)]}
    token = secrets.token_hex(24)
    with ns['db']() as c:
        # A second user may have changed the ration while the optimizer was running.
        if state(ns, c, rid)[2] != fingerprint:
            raise ValueError('Hesaplama sırasında rasyon veya yem bilgileri değişti. Yeniden hesaplayın.')
        c.execute('delete from ration_recalc_previews where created_at<?', ((datetime.now()-timedelta(minutes=20)).isoformat(),))
        c.execute('insert into ration_recalc_previews values(?,?,?,?,?)',
            (token, username, rid, datetime.now().isoformat(), json.dumps(payload, ensure_ascii=False)))
    return token


def load(c, token, username):
    row = c.execute('select * from ration_recalc_previews where token=? and username=?', (token, username)).fetchone()
    if not row or datetime.fromisoformat(row['created_at']) < datetime.now()-timedelta(minutes=20):
        raise ValueError('Önizleme bulunamadı veya süresi doldu. Yeniden hesaplayın.')
    return row, json.loads(row['payload'])


def preview_html(c, token, username):
    row, p = load(c, token, username)
    esc = lambda value: escape(str(value), quote=True)
    fmt = lambda value: f'{value:.2f}'.replace('.', ',')
    items = ''.join(f'<tr><td>{esc(i["name"])}{" · Kilitli" if i["locked"] else ""}</td>'
        f'<td>{fmt(i["before"])}</td><td>{fmt(i["after"])}</td></tr>' for i in p['items'])
    metrics = ''.join(f'<tr><td>{name}</td><td>{fmt(p["before"][key])}</td><td>{fmt(p["after"][key])}</td></tr>'
        for key, name in [('dm_kg', 'KM (kg/gün)'), ('cp_pct_dm', 'HP (% KM)'), ('cost', 'Maliyet (TL/baş/gün)')])
    warning = f'<p role="status">{esc(p["warning"])}</p>' if p['warning'] else ''
    return f'''<section class="card cp-recalc-preview"><h1>Rasyonu Yeniden Hesapla</h1>
      <h2>{esc(p['name'])}</h2><p>{fmt(p['weight'])} kg · KM %{fmt(p['percent'])} · hedef {fmt(p['target_dm'])} kg KM/gün</p>
      <p>Mevcut rasyon henüz değişmedi. Onayladığınızda aynı rasyon güncellenecek; padok bağlantıları korunacak.</p>
      <div class="tablewrap"><table><thead><tr><th>Değer</th><th>Mevcut</th><th>Yeni</th></tr></thead><tbody>{metrics}</tbody></table></div>
      <div class="tablewrap"><table><thead><tr><th>Yem</th><th>Mevcut kg</th><th>Yeni kg</th></tr></thead><tbody>{items}</tbody></table></div>{warning}
      <form method="post" action="/ration/recalculate-apply" data-submit-lock="1"><input type="hidden" name="token" value="{esc(token)}">
      <div class="cp-recalc-actions"><a class="btn alt" href="/ration-workbench?id={row['ration_id']}">Vazgeç</a><button class="btn" type="submit">Aynı Rasyona Uygula</button></div></form>
      </section><style>.cp-recalc-preview{{max-width:960px;margin:12px auto;min-width:0}}.cp-recalc-preview table{{width:100%;table-layout:fixed}}.cp-recalc-preview td,.cp-recalc-preview th{{overflow-wrap:anywhere;white-space:normal}}.cp-recalc-preview th:first-child{{width:50%}}.cp-recalc-actions{{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}}.cp-recalc-preview .btn{{min-height:42px}}</style>'''


def apply(ns, token, username):
    with ns['db']() as c:
        c.execute('BEGIN IMMEDIATE')
        row, p = load(c, token, username)
        rid = int(row['ration_id'])
        if state(ns, c, rid)[2] != p['fingerprint']:
            raise ValueError('Önizlemeden sonra rasyon veya yem bilgileri değişti. Güncel kayıtlarla yeniden hesaplayın.')
        for item in p['items']:
            if abs(item['before'] - item['after']) <= 1e-9:
                continue
            if item['locked']:
                raise ValueError('Kilitli yem değiştirilemez.')
            c.execute('update ration_items set kg_per_head_day=? where id=? and ration_id=?', (item['after'], item['item_id'], rid))
            ns['record_ration_item_history'](c, rid, item['feed_id'], item['after'], notes='Aynı rasyonu yeniden hesaplama')
        c.execute('''update rations set target_weight_kg=?,target_dm_pct_bw=?,
            notes=coalesce(notes,'') || ? where id=?''', (p['weight'], p['percent'],
            '\nBesi Hayvanı İhtiyaç Motoru V2 · yeniden hesaplandı ' + datetime.now().isoformat(timespec='seconds'), rid))
        c.execute('delete from ration_recalc_previews where token=?', (token,))
    return rid
