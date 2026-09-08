"""CiftlikPro Tarim & Ziraat modulu.

Tarim muhasebesi hayvancilik finansindan ayri tutulur. Yalnizca ic transfer
islemi, ayni bag kimligiyle tarim geliri + hayvancilik yem gideri + yem stogu
olusturur.
"""

from datetime import date, datetime
from html import escape


class AgricultureError(ValueError):
    pass


AGRI_PATHS = {
    "/agriculture",
    "/agriculture/fields",
    "/agriculture/seasons",
    "/agriculture/operations",
    "/agriculture/inputs",
    "/agriculture/harvests",
    "/agriculture/transfers",
    "/agriculture/finance",
    "/agriculture/reports",
}


def h(value):
    return escape(str(value or ""), quote=True)


def money(value):
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        number = 0.0
    text = f"{number:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return "₺" + text


def fmt_date(value):
    try:
        return datetime.strptime(str(value or "")[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return h(value) or "-"


def as_float(form, name, default=0.0):
    raw = str(form.get(name, "") or "").strip().replace(" ", "")
    if not raw:
        return float(default)
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        return float(raw)
    except ValueError as exc:
        raise AgricultureError(f"{name} alanı geçerli bir sayı olmalıdır.") from exc


def as_int(form, name, default=0):
    try:
        return int(str(form.get(name, default) or default).strip())
    except ValueError as exc:
        raise AgricultureError(f"{name} alanı geçersiz.") from exc


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def init_schema(c):
    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS agri_fields(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT,
            ownership_type TEXT NOT NULL DEFAULT 'Özmal',
            area_da REAL NOT NULL DEFAULT 0,
            water_type TEXT DEFAULT 'Kuru',
            province TEXT, district TEXT, village TEXT, block_no TEXT, parcel_no TEXT,
            landlord TEXT, rent_start TEXT, rent_end TEXT, rent_amount REAL DEFAULT 0,
            rent_payment_date TEXT, rent_finance_id INTEGER,
            notes TEXT, active INTEGER DEFAULT 1, created_at TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_agri_field_name_active
            ON agri_fields(name) WHERE active=1;

        CREATE TABLE IF NOT EXISTS agri_seasons(
            id INTEGER PRIMARY KEY,
            field_id INTEGER NOT NULL,
            season_year INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            cultivated_area_da REAL NOT NULL,
            start_date TEXT,
            expected_yield_kg_da REAL DEFAULT 0,
            status TEXT DEFAULT 'Planlandı',
            notes TEXT, closed_at TEXT, created_at TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS ux_agri_season
            ON agri_seasons(field_id,season_year,crop_name);

        CREATE TABLE IF NOT EXISTS agri_finance(
            id INTEGER PRIMARY KEY,
            tx_date TEXT NOT NULL,
            tx_type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            payment_method TEXT,
            field_id INTEGER,
            season_id INTEGER,
            source_type TEXT,
            source_id INTEGER,
            internal_transfer_id INTEGER,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agri_input_catalog(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'kg',
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agri_input_transactions(
            id INTEGER PRIMARY KEY,
            input_id INTEGER NOT NULL,
            tx_date TEXT NOT NULL,
            tx_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL DEFAULT 0,
            supplier TEXT, lot_no TEXT, notes TEXT,
            finance_id INTEGER,
            source_type TEXT,
            source_id INTEGER,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agri_operations(
            id INTEGER PRIMARY KEY,
            season_id INTEGER NOT NULL,
            operation_date TEXT NOT NULL,
            operation_type TEXT NOT NULL,
            area_da REAL DEFAULT 0,
            fuel_liters REAL DEFAULT 0,
            fuel_unit_price REAL DEFAULT 0,
            labor_cost REAL DEFAULT 0,
            contractor_cost REAL DEFAULT 0,
            other_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            finance_id INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agri_operation_inputs(
            id INTEGER PRIMARY KEY,
            operation_id INTEGER NOT NULL,
            input_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit_cost REAL NOT NULL,
            stock_tx_id INTEGER,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agri_harvest_lots(
            id INTEGER PRIMARY KEY,
            season_id INTEGER NOT NULL,
            harvest_date TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            moisture_pct REAL DEFAULT 0,
            quality TEXT,
            warehouse TEXT,
            estimated_market_price REAL DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS agri_product_transactions(
            id INTEGER PRIMARY KEY,
            harvest_lot_id INTEGER NOT NULL,
            tx_date TEXT NOT NULL,
            tx_type TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            unit_price REAL DEFAULT 0,
            source_type TEXT,
            source_id INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agri_sales(
            id INTEGER PRIMARY KEY,
            harvest_lot_id INTEGER NOT NULL,
            sale_date TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            unit_price REAL NOT NULL,
            buyer TEXT,
            payment_method TEXT,
            finance_id INTEGER,
            stock_tx_id INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agri_internal_transfers(
            id INTEGER PRIMARY KEY,
            harvest_lot_id INTEGER NOT NULL,
            transfer_date TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            unit_price REAL NOT NULL,
            feed_id INTEGER NOT NULL,
            agri_finance_id INTEGER,
            livestock_finance_id INTEGER,
            feed_stock_tx_id INTEGER,
            feed_price_id INTEGER,
            product_stock_tx_id INTEGER,
            notes TEXT,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS ix_agri_seasons_field ON agri_seasons(field_id,season_year);
        CREATE INDEX IF NOT EXISTS ix_agri_operations_season ON agri_operations(season_id,operation_date);
        CREATE INDEX IF NOT EXISTS ix_agri_finance_date ON agri_finance(tx_date,tx_type);
        CREATE INDEX IF NOT EXISTS ix_agri_input_tx ON agri_input_transactions(input_id,tx_date);
        CREATE INDEX IF NOT EXISTS ix_agri_harvest_season ON agri_harvest_lots(season_id,harvest_date);
        CREATE INDEX IF NOT EXISTS ix_agri_product_tx ON agri_product_transactions(harvest_lot_id,tx_date);
        """
    )


def input_balance(c, input_id):
    row = c.execute(
        """SELECT COALESCE(SUM(CASE WHEN tx_type IN ('Giriş','Sayım +') THEN quantity
                 ELSE -quantity END),0) qty
           FROM agri_input_transactions WHERE input_id=?""",
        (input_id,),
    ).fetchone()
    return float(row["qty"] or 0)


def input_average_cost(c, input_id):
    row = c.execute(
        """SELECT COALESCE(SUM(quantity*unit_cost),0) value,
                  COALESCE(SUM(quantity),0) qty
           FROM agri_input_transactions
           WHERE input_id=? AND tx_type IN ('Giriş','Sayım +') AND unit_cost>0""",
        (input_id,),
    ).fetchone()
    qty = float(row["qty"] or 0)
    return float(row["value"] or 0) / qty if qty > 0 else 0.0


def harvest_balance(c, lot_id):
    row = c.execute(
        """SELECT COALESCE(SUM(CASE WHEN tx_type='Giriş' THEN quantity_kg
                 ELSE -quantity_kg END),0) qty
           FROM agri_product_transactions WHERE harvest_lot_id=?""",
        (lot_id,),
    ).fetchone()
    return float(row["qty"] or 0)


def feed_stock_balance(c, feed_id):
    row = c.execute(
        """SELECT COALESCE(SUM(CASE
                 WHEN tx_type IN ('Giriş','Sayım +') THEN quantity_kg
                 WHEN tx_type IN ('Çıkış','Tüketim','Sayım -') THEN -quantity_kg
                 ELSE 0 END),0) qty
           FROM feed_stock_transactions WHERE feed_id=?""",
        (feed_id,),
    ).fetchone()
    return float(row["qty"] or 0)


def season_cost(c, season_id):
    operation = c.execute(
        "SELECT COALESCE(SUM(total_cost),0) v FROM agri_operations WHERE season_id=?",
        (season_id,),
    ).fetchone()["v"]
    inputs = c.execute(
        """SELECT COALESCE(SUM(oi.quantity*oi.unit_cost),0) v
           FROM agri_operation_inputs oi JOIN agri_operations o ON o.id=oi.operation_id
           WHERE o.season_id=?""",
        (season_id,),
    ).fetchone()["v"]
    other = c.execute(
        """SELECT COALESCE(SUM(amount),0) v FROM agri_finance
           WHERE season_id=? AND tx_type='Gider'
             AND COALESCE(source_type,'') NOT IN ('operation','input_purchase')""",
        (season_id,),
    ).fetchone()["v"]
    season = c.execute(
        """SELECT s.*,f.area_da field_area,f.rent_amount
           FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id WHERE s.id=?""",
        (season_id,),
    ).fetchone()
    rent_share = 0.0
    if season and float(season["rent_amount"] or 0) > 0:
        total_area = c.execute(
            "SELECT COALESCE(SUM(cultivated_area_da),0) v FROM agri_seasons WHERE field_id=? AND season_year=?",
            (season["field_id"], season["season_year"]),
        ).fetchone()["v"]
        if float(total_area or 0) > 0:
            rent_share = float(season["rent_amount"] or 0) * float(season["cultivated_area_da"] or 0) / float(total_area)
    return round(float(operation or 0) + float(inputs or 0) + float(other or 0) + rent_share, 2)


def season_harvest(c, season_id):
    row = c.execute(
        "SELECT COALESCE(SUM(quantity_kg),0) qty FROM agri_harvest_lots WHERE season_id=?",
        (season_id,),
    ).fetchone()
    return float(row["qty"] or 0)


def season_value(c, season_id):
    realized = c.execute(
        """SELECT COALESCE(SUM(amount),0) v FROM agri_finance
           WHERE season_id=? AND tx_type='Gelir'""",
        (season_id,),
    ).fetchone()["v"]
    lots = c.execute(
        "SELECT id,estimated_market_price FROM agri_harvest_lots WHERE season_id=?",
        (season_id,),
    ).fetchall()
    stock_value = sum(harvest_balance(c, r["id"]) * float(r["estimated_market_price"] or 0) for r in lots)
    return round(float(realized or 0) + stock_value, 2), round(float(realized or 0), 2), round(stock_value, 2)


AGRI_CSS = """
<style id="agri-module-css">
.agri-head{display:flex;justify-content:space-between;align-items:center;gap:14px;margin:2px 0 10px}.agri-head h1{margin:0 0 3px;font-size:25px}.agri-head p{margin:0}.agri-actions{display:flex;gap:8px;flex-wrap:wrap}
.agri-tabs{display:flex;gap:7px;overflow-x:auto;margin:0 0 10px;padding:2px 0}.agri-tabs a{white-space:nowrap;padding:8px 11px;border:1px solid #d8e5dc;border-radius:999px;background:#fff;color:#28543d;font-size:12px;font-weight:800}.agri-tabs a.on{background:#117344;color:#fff;border-color:#117344}
.agri-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:9px;margin-bottom:10px}.agri-kpi{background:#fff;border:1px solid #dce6df;border-radius:9px;padding:13px}.agri-kpi span{display:block;color:#62766a;font-size:12px;font-weight:750}.agri-kpi b{display:block;color:#0c6238;font-size:24px;margin-top:6px}.agri-kpi.warn b{color:#a56800}
.agri-grid{display:grid;grid-template-columns:1.45fr 1fr;gap:10px}.agri-grid.equal{grid-template-columns:1fr 1fr}.agri-card-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 10px}.agri-card-title h2{font-size:17px;margin:0}.agri-table-wrap{overflow:auto}.agri-status{display:inline-flex;padding:5px 8px;border-radius:999px;background:#e7f5eb;color:#13713e;font-weight:800;font-size:11px}.agri-status.wait{background:#fff1d4;color:#9a6200}.agri-negative{color:#b42318}.agri-positive{color:#08783f}.agri-note{background:#eef7f1;border:1px solid #d9e9de;border-radius:8px;padding:10px;color:#315e45;font-size:12px;margin-bottom:10px}.agri-form-actions,.agri-row-actions{display:flex;gap:6px;flex-wrap:wrap;align-items:center}.agri-row-actions form{display:inline-flex;margin:0}.agri-mini-list{display:grid;gap:7px}.agri-mini-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 9px;border-bottom:1px solid #e7ede9}.agri-mini-row:last-child{border-bottom:0}.agri-progress{height:8px;background:#e8eeea;border-radius:99px;overflow:hidden;margin-top:5px}.agri-progress i{display:block;height:100%;background:#11804a;border-radius:99px}.agri-danger{background:#fff4f2;border-color:#f0d2cc}.agri-transfer-box{background:#f4faf6;border:1px solid #d7eadc;border-radius:9px;padding:11px}.agri-subtle{font-size:11px;color:#6b7c72}.agri-two-tables{display:grid;grid-template-columns:1fr 1fr;gap:10px}body:has(.agri-head) input[type=checkbox]{width:auto!important;margin-right:7px}
@media(max-width:1100px){.agri-grid,.agri-grid.equal,.agri-two-tables{grid-template-columns:1fr}.agri-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:650px){.agri-head{align-items:flex-start;flex-direction:column}.agri-actions{display:grid;grid-template-columns:1fr 1fr;width:100%}.agri-actions .btn{text-align:center}.agri-kpis{grid-template-columns:1fr 1fr}.agri-kpi{padding:10px}.agri-kpi b{font-size:19px}.agri-card-title{align-items:flex-start}.agri-card-title h2{font-size:16px}.agri-form-actions{display:grid;grid-template-columns:1fr;width:100%}.agri-form-actions .btn{text-align:center}body:has(.agri-head) .form{grid-template-columns:1fr!important}}
</style>
"""


TABS = [
    ("Genel Bakış", "/agriculture"),
    ("Tarlalar", "/agriculture/fields"),
    ("Üretim Sezonları", "/agriculture/seasons"),
    ("Tarla İşlemleri", "/agriculture/operations"),
    ("Girdi & Depo", "/agriculture/inputs"),
    ("Hasat & Mahsul", "/agriculture/harvests"),
    ("Satış & İç Transfer", "/agriculture/transfers"),
    ("Tarım Finans", "/agriculture/finance"),
    ("Tarım Raporları", "/agriculture/reports"),
]


def shell(active, content, actions=""):
    tabs = "".join(f'<a class="{"on" if active == url else ""}" href="{url}">{h(label)}</a>' for label, url in TABS)
    return (
        AGRI_CSS
        + f'<header class="agri-head"><div><h1>🌾 Tarım & Ziraat Yönetimi</h1><p class="mut">Tarla, sezon, maliyet, hasat ve hayvancılığa iç transfer yönetimi</p></div><div class="agri-actions">{actions}</div></header>'
        + f'<nav class="agri-tabs">{tabs}</nav>'
        + content
    )


def field_options(rows, selected=None):
    return "".join(f'<option value="{r["id"]}" {"selected" if str(r["id"]) == str(selected) else ""}>{h(r["name"])} · {float(r["area_da"] or 0):g} da</option>' for r in rows)


def season_options(rows, selected=None):
    return "".join(f'<option value="{r["id"]}" {"selected" if str(r["id"]) == str(selected) else ""}>{h(r["season_year"])} · {h(r["field_name"])} · {h(r["crop_name"])}</option>' for r in rows)


def lot_options(c, lots, selected=None):
    parts = []
    for r in lots:
        balance = harvest_balance(c, r["id"])
        if balance <= 0 and str(r["id"]) != str(selected):
            continue
        parts.append(f'<option value="{r["id"]}" data-price="{float(r["estimated_market_price"] or 0):g}" data-product="{h(r["product_name"])}" {"selected" if str(r["id"]) == str(selected) else ""}>{h(r["product_name"])} · {h(r["field_name"])} · {balance:,.2f} kg</option>')
    return "".join(parts)


def dashboard(c):
    year = date.today().year
    fields = c.execute("SELECT * FROM agri_fields WHERE active=1 ORDER BY name").fetchall()
    seasons = c.execute(
        """SELECT s.*,f.name field_name FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id
           WHERE s.season_year=? ORDER BY s.id DESC""",
        (year,),
    ).fetchall()
    total_area = sum(float(r["area_da"] or 0) for r in fields)
    total_cost = sum(season_cost(c, r["id"]) for r in seasons)
    lots = c.execute("SELECT * FROM agri_harvest_lots ORDER BY harvest_date DESC,id DESC").fetchall()
    stock_qty = sum(max(0, harvest_balance(c, r["id"])) for r in lots)
    total_value = sum(season_value(c, r["id"])[0] for r in seasons)
    profit = total_value - total_cost
    season_rows = []
    for r in seasons[:8]:
        cost = season_cost(c, r["id"])
        harvested = season_harvest(c, r["id"])
        yield_da = harvested / float(r["cultivated_area_da"] or 1)
        status_cls = "wait" if r["status"] in ("Planlandı", "Devam Ediyor", "Hasat Bekliyor") else ""
        season_rows.append(
            f'<tr><td><b>{h(r["field_name"])}</b></td><td>{h(r["crop_name"])}</td><td>{float(r["cultivated_area_da"]):g} da</td><td>{money(cost)}</td><td>{yield_da:,.1f} kg/da</td><td><span class="agri-status {status_cls}">{h(r["status"])}</span></td></tr>'
        )
    operations = c.execute(
        """SELECT o.*,s.crop_name,f.name field_name FROM agri_operations o
           JOIN agri_seasons s ON s.id=o.season_id JOIN agri_fields f ON f.id=s.field_id
           ORDER BY o.operation_date DESC,o.id DESC LIMIT 6"""
    ).fetchall()
    products = []
    for r in lots:
        bal = harvest_balance(c, r["id"])
        if bal > 0:
            products.append(f'<div class="agri-mini-row"><span><b>{h(r["product_name"])}</b><small class="mut"> · {h(r["warehouse"]) or "Depo belirtilmedi"}</small></span><b>{bal:,.2f} kg</b></div>')
    ops = "".join(f'<div class="agri-mini-row"><span><b>{h(r["operation_type"])}</b><small class="mut"> · {h(r["field_name"])}</small></span><span>{fmt_date(r["operation_date"])} · <b>{money(r["total_cost"])}</b></span></div>' for r in operations)
    content = f"""
    <section class="agri-kpis">
      <div class="agri-kpi"><span>Toplam Arazi</span><b>{total_area:,.1f} da</b></div>
      <div class="agri-kpi warn"><span>{year} Sezon Maliyeti</span><b>{money(total_cost)}</b></div>
      <div class="agri-kpi"><span>Hasat Stoku</span><b>{stock_qty:,.0f} kg</b></div>
      <div class="agri-kpi"><span>Sezon Ekonomik Sonucu</span><b class="{'agri-positive' if profit >= 0 else 'agri-negative'}">{money(profit)}</b></div>
    </section>
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>🌱 Aktif Üretim Sezonları</h2><a class="btn alt" href="/agriculture/seasons">Tümünü Gör</a></div><div class="agri-table-wrap"><table><tr><th>Tarla</th><th>Ürün</th><th>Alan</th><th>Maliyet</th><th>Verim</th><th>Durum</th></tr>{''.join(season_rows) or '<tr><td colspan="6">Bu yıl için üretim sezonu kaydı yok.</td></tr>'}</table></div></div>
      <div class="card"><div class="agri-card-title"><h2>📦 Mahsul Stoku</h2><a class="btn alt" href="/agriculture/harvests">Hasat Gir</a></div><div class="agri-mini-list">{''.join(products[:8]) or '<p class="mut">Henüz mahsul stoğu yok.</p>'}</div></div>
    </section>
    <section class="agri-grid equal" style="margin-top:10px">
      <div class="card"><div class="agri-card-title"><h2>⚙️ Son Tarla İşlemleri</h2><a class="btn alt" href="/agriculture/operations">İşlem Kaydet</a></div>{ops or '<p class="mut">Henüz tarla işlemi yok.</p>'}</div>
      <div class="card"><div class="agri-card-title"><h2>⇄ Hayvancılığa İç Transfer</h2><a class="btn" href="/agriculture/transfers">İç Transfer Oluştur</a></div><p class="mut">Mahsul çıkışı, tarım iç satış geliri, hayvancılık yem gideri ve yem stok girişi tek bağlı işlemle oluşturulur.</p><div class="agri-note">İç transferler kasa/banka hareketi değildir. İşletme geneli raporunda gelir ve gider birbirini götürür.</div></div>
    </section>
    """
    actions = '<a class="btn" href="/agriculture/fields">+ Tarla Ekle</a><a class="btn blue" href="/agriculture/operations">+ İşlem Kaydet</a>'
    return "Tarım & Ziraat", shell("/agriculture", content, actions)


def fields_page(c, q):
    edit_id = (q.get("edit") or [""])[0]
    rec = c.execute("SELECT * FROM agri_fields WHERE id=?", (edit_id,)).fetchone() if edit_id else None
    rows = c.execute("SELECT * FROM agri_fields WHERE active=1 ORDER BY name").fetchall()
    def val(name, default=""):
        return h(rec[name] if rec else default)
    ownership = rec["ownership_type"] if rec else "Özmal"
    water = rec["water_type"] if rec else "Kuru"
    table_rows = "".join(
        f'<tr><td><b>{h(r["name"])}</b><div class="mut">{h(r["code"])}</div></td><td>{h(r["ownership_type"])}</td><td>{float(r["area_da"] or 0):g} da</td><td>{h(r["water_type"])}</td><td>{h(r["village"]) or "-"}</td><td>{h(r["block_no"]) or "-"} / {h(r["parcel_no"]) or "-"}</td><td>{money(r["rent_amount"]) if r["ownership_type"] == "Kiralık" else "-"}</td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/fields?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/field/delete" onsubmit="return confirm(\'Tarla ve bağlı kira kaydı silinsin mi? Bağlı sezon varsa işlem engellenir.\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></div></td></tr>'
        for r in rows
    )
    content = f"""
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>🗺️ {'Tarla Düzenle' if rec else 'Yeni Tarla Kartı'}</h2></div>
        <form method="post" action="/agriculture/field/save" class="form"><input type="hidden" name="id" value="{val('id')}">
          <label>Tarla Adı<input name="name" value="{val('name')}" required></label><label>Kod<input name="code" value="{val('code')}"></label>
          <label>Mülkiyet<select name="ownership_type"><option {'selected' if ownership == 'Özmal' else ''}>Özmal</option><option {'selected' if ownership == 'Kiralık' else ''}>Kiralık</option></select></label><label>Alan (dekar)<input type="number" min="0.01" step="0.01" name="area_da" value="{val('area_da')}" required></label>
          <label>Sulama Durumu<select name="water_type"><option {'selected' if water == 'Kuru' else ''}>Kuru</option><option {'selected' if water == 'Sulu' else ''}>Sulu</option><option {'selected' if water == 'Kısmi Sulu' else ''}>Kısmi Sulu</option></select></label><label>Köy / Mevki<input name="village" value="{val('village')}"></label>
          <label>İl<input name="province" value="{val('province')}"></label><label>İlçe<input name="district" value="{val('district')}"></label>
          <label>Ada<input name="block_no" value="{val('block_no')}"></label><label>Parsel<input name="parcel_no" value="{val('parcel_no')}"></label>
          <label>Kiraya Veren<input name="landlord" value="{val('landlord')}"></label><label>Yıllık Kira Tutarı<input type="number" min="0" step="0.01" name="rent_amount" value="{val('rent_amount',0)}"></label>
          <label>Kira Başlangıç<input type="date" name="rent_start" value="{val('rent_start')}"></label><label>Kira Bitiş<input type="date" name="rent_end" value="{val('rent_end')}"></label>
          <label>Kira Ödeme Tarihi<input type="date" name="rent_payment_date" value="{val('rent_payment_date',date.today().isoformat())}"></label><label><input type="checkbox" name="post_rent" value="yes" {'checked' if rec and rec['rent_finance_id'] else ''}> Kira bedelini Tarım Finans'a gider yaz</label>
          <label class="full">Not<textarea name="notes">{val('notes')}</textarea></label><div class="full agri-form-actions"><button class="btn">💾 Tarla Kartını Kaydet</button>{'<a class="btn alt" href="/agriculture/fields">İptal</a>' if rec else ''}</div>
        </form></div>
      <div class="card"><h2>Tarla Kaydı Mantığı</h2><div class="agri-note">Özmal arazinin satın alma bedeli yıllık üretim gideri sayılmaz. Kiralık arazinin kira bedeli Tarım Finans'a gider yazılır ve üretim sezonlarına ekilen alan oranında dağıtılır.</div><p class="mut">Ada, parsel, kira bitişi ve geçmiş sezonlar tarla kartında korunur.</p></div>
    </section>
    <div class="card" style="margin-top:10px"><div class="agri-card-title"><h2>Kayıtlı Tarlalar</h2><span class="pill">{len(rows)} aktif tarla</span></div><div class="agri-table-wrap"><table style="min-width:1000px"><tr><th>Tarla</th><th>Mülkiyet</th><th>Alan</th><th>Sulama</th><th>Mevki</th><th>Ada/Parsel</th><th>Kira</th><th>İşlem</th></tr>{table_rows or '<tr><td colspan="8">Henüz tarla kaydı yok.</td></tr>'}</table></div></div>
    """
    return "Tarlalar", shell("/agriculture/fields", content)


def seasons_page(c, q):
    edit_id=(q.get('edit') or [''])[0]
    rec=c.execute('SELECT * FROM agri_seasons WHERE id=?',(edit_id,)).fetchone() if edit_id else None
    fields = c.execute("SELECT * FROM agri_fields WHERE active=1 ORDER BY name").fetchall()
    rows = c.execute("""SELECT s.*,f.name field_name,f.area_da field_area FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id ORDER BY s.season_year DESC,s.id DESC""").fetchall()
    table_rows=[]
    for r in rows:
        cost=season_cost(c,r['id']);qty=season_harvest(c,r['id']);value,realized,stock=season_value(c,r['id']);profit=value-cost
        table_rows.append(f'<tr><td>{r["season_year"]}</td><td><b>{h(r["field_name"])}</b></td><td>{h(r["crop_name"])}</td><td>{float(r["cultivated_area_da"]):g} da</td><td>{money(cost)}</td><td>{qty:,.2f} kg</td><td>{money(realized)}</td><td>{money(stock)}</td><td><b class="{"agri-positive" if profit>=0 else "agri-negative"}">{money(profit)}</b></td><td><span class="agri-status">{h(r["status"])}</span></td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/seasons?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/season/close"><input type="hidden" name="id" value="{r["id"]}"><button class="btn alt">Kapat</button></form><form method="post" action="/agriculture/season/delete" onsubmit="return confirm(\'Sezon silinsin mi? Bağlı işlem, hasat veya finans kaydı varsa engellenir.\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></div></td></tr>')
    def sval(name,default=''):
        return h(rec[name] if rec else default)
    status=rec['status'] if rec else 'Planlandı'
    content=f"""
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>🌱 {'Üretim Sezonunu Düzenle' if rec else 'Yeni Üretim Sezonu'}</h2></div><form method="post" action="/agriculture/season/save" class="form"><input type="hidden" name="id" value="{sval('id')}">
        <label>Tarla<select name="field_id" required><option value="">Seçin…</option>{field_options(fields,rec['field_id'] if rec else None)}</select></label><label>Sezon Yılı<input type="number" min="2000" max="2100" name="season_year" value="{sval('season_year',date.today().year)}" required></label>
        <label>Ekilecek Ürün<input name="crop_name" value="{sval('crop_name')}" list="cropList" placeholder="Arpa, buğday, silajlık mısır…" required><datalist id="cropList"><option>Arpa</option><option>Buğday</option><option>Silajlık Mısır</option><option>Yonca</option><option>Fiğ</option><option>Nohut</option></datalist></label><label>Ekilen Alan (da)<input type="number" min="0.01" step="0.01" name="cultivated_area_da" value="{sval('cultivated_area_da')}" required></label>
        <label>Başlangıç Tarihi<input type="date" name="start_date" value="{sval('start_date',date.today().isoformat())}"></label><label>Hedef Verim (kg/da)<input type="number" min="0" step="0.01" name="expected_yield_kg_da" value="{sval('expected_yield_kg_da')}"></label>
        <label>Durum<select name="status">{''.join(f'<option {"selected" if status==x else ""}>{x}</option>' for x in ('Planlandı','Devam Ediyor','Hasat Bekliyor','Hasat Tamamlandı','Kapandı'))}</select></label><label>Not<input name="notes" value="{sval('notes')}"></label><div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if rec else 'Sezonu Oluştur'}</button>{'<a class="btn alt" href="/agriculture/seasons">İptal</a>' if rec else ''}</div>
      </form></div>
      <div class="card"><h2>Sezon Maliyet Mantığı</h2><p class="mut">Tarla işlemleri, kullanılan girdiler, kira payı ve sezona bağlanan diğer giderler birleştirilir. Hasat stoğu piyasa değeriyle ayrıca gösterilir; gerçek gelir yalnız satış veya iç transferde oluşur.</p></div>
    </section>
    <div class="card" style="margin-top:10px"><div class="agri-card-title"><h2>Üretim Sezonları</h2><span class="pill">{len(rows)} sezon</span></div><div class="agri-table-wrap"><table style="min-width:1350px"><tr><th>Yıl</th><th>Tarla</th><th>Ürün</th><th>Alan</th><th>Maliyet</th><th>Hasat</th><th>Gerçekleşen Gelir</th><th>Kalan Stok Değeri</th><th>Ekonomik Sonuç</th><th>Durum</th><th>İşlem</th></tr>{''.join(table_rows) or '<tr><td colspan="11">Henüz üretim sezonu yok.</td></tr>'}</table></div></div>
    """
    return "Üretim Sezonları",shell("/agriculture/seasons",content)


def operations_page(c, q):
    edit_id=(q.get('edit') or [''])[0]
    rec=c.execute("""SELECT o.*,oi.input_id,oi.quantity input_qty,af.payment_method FROM agri_operations o LEFT JOIN agri_operation_inputs oi ON oi.operation_id=o.id LEFT JOIN agri_finance af ON af.id=o.finance_id WHERE o.id=?""",(edit_id,)).fetchone() if edit_id else None
    seasons=c.execute("""SELECT s.*,f.name field_name FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id WHERE s.status<>'Kapandı' OR s.id=? ORDER BY s.season_year DESC,f.name""",(rec['season_id'] if rec else 0,)).fetchall()
    inputs=c.execute("SELECT * FROM agri_input_catalog WHERE active=1 ORDER BY category,name").fetchall()
    rows=c.execute("""SELECT o.*,s.crop_name,s.season_year,f.name field_name,oi.quantity input_qty,oi.unit_cost input_unit_cost,ic.name input_name,ic.unit input_unit FROM agri_operations o JOIN agri_seasons s ON s.id=o.season_id JOIN agri_fields f ON f.id=s.field_id LEFT JOIN agri_operation_inputs oi ON oi.operation_id=o.id LEFT JOIN agri_input_catalog ic ON ic.id=oi.input_id ORDER BY o.operation_date DESC,o.id DESC LIMIT 100""").fetchall()
    input_opts=''.join(f'<option value="{r["id"]}" {"selected" if rec and str(rec["input_id"] or "")==str(r["id"]) else ""}>{h(r["category"])} · {h(r["name"])} · stok {input_balance(c,r["id"]):,.2f} {h(r["unit"])}</option>' for r in inputs)
    table_rows=''.join(f'<tr><td>{fmt_date(r["operation_date"])}</td><td><b>{h(r["field_name"])}</b><div class="mut">{h(r["crop_name"])} · {r["season_year"]}</div></td><td>{h(r["operation_type"])}</td><td>{float(r["area_da"] or 0):g} da</td><td>{money(r["total_cost"])}</td><td>{h(r["input_name"]) or "-"}</td><td>{(f"{float(r['input_qty']):g} {h(r['input_unit'])} · {money(float(r['input_qty'])*float(r['input_unit_cost']))}" if r["input_name"] else "-")}</td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/operations?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/operation/delete" onsubmit="return confirm(\'İşlem, girdi çıkışı ve bağlı finans kaydı geri alınsın mı?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil / Geri Al</button></form></div></td></tr>' for r in rows)
    def oval(name,default=0):return h(rec[name] if rec and rec[name] is not None else default)
    op_type=rec['operation_type'] if rec else 'Anız Bozma';payment=(rec['payment_method'] if rec and rec['payment_method'] else 'Nakit')
    content=f"""
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>⚙️ {'Tarla İşlemini Düzenle' if rec else 'Tarla İşlemi Kaydet'}</h2></div><form method="post" action="/agriculture/operation/save" class="form"><input type="hidden" name="id" value="{oval('id','')}">
        <label>Üretim Sezonu<select name="season_id" required><option value="">Seçin…</option>{season_options(seasons,rec['season_id'] if rec else None)}</select></label><label>İşlem Tarihi<input type="date" name="operation_date" value="{oval('operation_date',date.today().isoformat())}" required></label>
        <label>İşlem Türü<select name="operation_type">{''.join(f'<option {"selected" if op_type==x else ""}>{x}</option>' for x in ('Anız Bozma','Sürme','İkileme','Diskaro / Tırmık','Ekim','Taban Gübreleme','Üst Gübreleme','İlaçlama','Sulama','Biçerdöver','Balya','Yükleme','Nakliye','Diğer'))}</select></label><label>İşlenen Alan (da)<input type="number" min="0" step="0.01" name="area_da" value="{oval('area_da')}"></label>
        <label>Mazot (litre)<input type="number" min="0" step="0.01" name="fuel_liters" value="{oval('fuel_liters')}"></label><label>Mazot ₺/litre<input type="number" min="0" step="0.01" name="fuel_unit_price" value="{oval('fuel_unit_price')}"></label>
        <label>İşçilik<input type="number" min="0" step="0.01" name="labor_cost" value="{oval('labor_cost')}"></label><label>Dış Hizmet / Müteahhit<input type="number" min="0" step="0.01" name="contractor_cost" value="{oval('contractor_cost')}"></label>
        <label>Diğer Maliyet<input type="number" min="0" step="0.01" name="other_cost" value="{oval('other_cost')}"></label><label>Ödeme Yöntemi<select name="payment_method">{''.join(f'<option {"selected" if payment==x else ""}>{x}</option>' for x in ('Nakit','Banka','Vadeli','Tahakkuk'))}</select></label>
        <label class="full">Depodan Kullanılan Girdi<select name="input_id"><option value="">Girdi kullanılmadı</option>{input_opts}</select></label><label>Girdi Miktarı<input type="number" min="0" step="0.001" name="input_quantity" value="{oval('input_qty')}"></label><label class="full">Not<textarea name="notes">{oval('notes','')}</textarea></label>
        <div class="full agri-note">Mazot + işçilik + dış hizmet + diğer maliyet Tarım Finans'a tek gider olarak yazılır. Depodan kullanılan tohum/gübre/ilaç tekrar finans gideri oluşturmaz; yalnız sezona maliyet olarak dağıtılır.</div><div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if rec else 'İşlemi ve Maliyeti Kaydet'}</button>{'<a class="btn alt" href="/agriculture/operations">İptal</a>' if rec else ''}</div>
      </form></div>
      <div class="card"><h2>Hazır İşlem Türleri</h2><p class="mut">Sürme, ikileme, diskaro, ekim, gübreleme, ilaçlama, sulama, hasat, balya ve nakliye kayıtları aynı üretim sezonunda birikir.</p><div class="agri-note">Girdi stoğu yetersizse sistem işlemi kaydetmez ve hangi girdinin eksik olduğunu açıkça söyler.</div></div>
    </section>
    <div class="card" style="margin-top:10px"><div class="agri-card-title"><h2>Son Tarla İşlemleri</h2><span class="pill">{len(rows)} kayıt</span></div><div class="agri-table-wrap"><table style="min-width:1100px"><tr><th>Tarih</th><th>Tarla/Sezon</th><th>İşlem</th><th>Alan</th><th>İşlem Maliyeti</th><th>Girdi</th><th>Girdi Maliyeti</th><th>İşlem</th></tr>{table_rows or '<tr><td colspan="8">Henüz tarla işlemi yok.</td></tr>'}</table></div></div>
    """
    return "Tarla İşlemleri",shell("/agriculture/operations",content)


def inputs_page(c, q):
    edit_id=(q.get('edit') or [''])[0]
    rec=c.execute("""SELECT t.*,i.name input_name,i.category,i.unit,af.payment_method FROM agri_input_transactions t JOIN agri_input_catalog i ON i.id=t.input_id LEFT JOIN agri_finance af ON af.id=t.finance_id WHERE t.id=? AND t.tx_type='Giriş'""",(edit_id,)).fetchone() if edit_id else None
    rows=c.execute("SELECT * FROM agri_input_catalog WHERE active=1 ORDER BY category,name").fetchall()
    purchases=c.execute("""SELECT t.*,i.name input_name,i.unit FROM agri_input_transactions t JOIN agri_input_catalog i ON i.id=t.input_id WHERE t.tx_type='Giriş' ORDER BY t.tx_date DESC,t.id DESC LIMIT 100""").fetchall()
    stock_rows=''.join(f'<tr><td><b>{h(r["name"])}</b></td><td>{h(r["category"])}</td><td>{input_balance(c,r["id"]):,.3f} {h(r["unit"])}</td><td>{money(input_average_cost(c,r["id"]))}/{h(r["unit"])}</td><td>{money(input_balance(c,r["id"])*input_average_cost(c,r["id"]))}</td></tr>' for r in rows)
    purchase_rows=''.join(f'<tr><td>{fmt_date(r["tx_date"])}</td><td>{h(r["input_name"])}</td><td>{float(r["quantity"]):,.3f} {h(r["unit"])}</td><td>{money(r["unit_cost"])}</td><td>{h(r["supplier"]) or "-"}</td><td>{h(r["lot_no"]) or "-"}</td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/inputs?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/input/delete" onsubmit="return confirm(\'Alım ve bağlı Tarım Finans gideri geri alınsın mı?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil / Geri Al</button></form></div></td></tr>' for r in purchases)
    def ival(name,default=''):return h(rec[name] if rec and rec[name] is not None else default)
    content=f"""
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>📦 {'Girdi Alımını Düzenle' if rec else 'Girdi Satın Al / Stok Girişi'}</h2></div><form method="post" action="/agriculture/input/purchase" class="form"><input type="hidden" name="id" value="{ival('id')}">
        <label>Girdi Adı<input name="name" value="{ival('input_name')}" list="inputNames" placeholder="Üre 46, DAP, sertifikalı arpa tohumu…" required><datalist id="inputNames">{''.join(f'<option>{h(r["name"])}</option>' for r in rows)}</datalist></label><label>Kategori<select name="category">{''.join(f'<option {"selected" if rec and rec["category"]==x else ""}>{x}</option>' for x in ('Tohum','Gübre','Zirai İlaç','Mazot','Sulama Malzemesi','Diğer'))}</select></label>
        <label>Birim<select name="unit">{''.join(f'<option {"selected" if rec and rec["unit"]==x else ""}>{x}</option>' for x in ('kg','litre','adet','ton'))}</select></label><label>Miktar<input type="number" min="0.001" step="0.001" name="quantity" value="{ival('quantity')}" required></label>
        <label>Birim Maliyet<input type="number" min="0" step="0.01" name="unit_cost" value="{ival('unit_cost')}" required></label><label>Tarih<input type="date" name="tx_date" value="{ival('tx_date',date.today().isoformat())}" required></label>
        <label>Tedarikçi<input name="supplier" value="{ival('supplier')}"></label><label>Parti / Lot<input name="lot_no" value="{ival('lot_no')}"></label><label>Ödeme Yöntemi<select name="payment_method">{''.join(f'<option {"selected" if rec and rec["payment_method"]==x else ""}>{x}</option>' for x in ('Nakit','Banka','Vadeli'))}</select></label><label>Not<input name="notes" value="{ival('notes')}"></label>
        <div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if rec else 'Stok ve Tarım Gideri Oluştur'}</button>{'<a class="btn alt" href="/agriculture/inputs">İptal</a>' if rec else ''}</div>
      </form></div>
      <div class="card"><h2>Çift Kayıt Koruması</h2><div class="agri-note">Satın alma sırasında Tarım Finans'a gider yazılır. Girdi tarlada kullanıldığında stoktan düşer ve sezona maliyet atanır; ikinci bir finans gideri oluşmaz.</div></div>
    </section>
    <section class="agri-two-tables" style="margin-top:10px"><div class="card"><div class="agri-card-title"><h2>Girdi Stokları</h2><span class="pill">{len(rows)} ürün</span></div><div class="agri-table-wrap"><table><tr><th>Girdi</th><th>Kategori</th><th>Stok</th><th>Ort. Maliyet</th><th>Stok Değeri</th></tr>{stock_rows or '<tr><td colspan="5">Girdi stoğu yok.</td></tr>'}</table></div></div><div class="card"><div class="agri-card-title"><h2>Son Alımlar</h2></div><div class="agri-table-wrap"><table style="min-width:850px"><tr><th>Tarih</th><th>Girdi</th><th>Miktar</th><th>Birim</th><th>Tedarikçi</th><th>Lot</th><th>İşlem</th></tr>{purchase_rows or '<tr><td colspan="7">Girdi alımı yok.</td></tr>'}</table></div></div></section>
    """
    return "Girdi & Depo",shell("/agriculture/inputs",content)


def harvests_page(c, q):
    edit_id=(q.get('edit') or [''])[0]
    rec=c.execute('SELECT * FROM agri_harvest_lots WHERE id=?',(edit_id,)).fetchone() if edit_id else None
    seasons=c.execute("""SELECT s.*,f.name field_name FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id ORDER BY s.season_year DESC,f.name""").fetchall()
    lots=c.execute("""SELECT l.*,s.crop_name,s.season_year,f.name field_name FROM agri_harvest_lots l JOIN agri_seasons s ON s.id=l.season_id JOIN agri_fields f ON f.id=s.field_id ORDER BY l.harvest_date DESC,l.id DESC""").fetchall()
    lot_rows=[]
    for r in lots:
        bal=harvest_balance(c,r['id']);lot_rows.append(f'<tr><td>{fmt_date(r["harvest_date"])}</td><td><b>{h(r["product_name"])}</b><div class="mut">{h(r["field_name"])} · {r["season_year"]}</div></td><td>{float(r["quantity_kg"]):,.2f} kg</td><td><b>{bal:,.2f} kg</b></td><td>{float(r["moisture_pct"] or 0):g}%</td><td>{h(r["quality"]) or "-"}</td><td>{h(r["warehouse"]) or "-"}</td><td>{money(r["estimated_market_price"])}/kg</td><td>{money(bal*float(r["estimated_market_price"] or 0))}</td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/harvests?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/harvest/delete" onsubmit="return confirm(\'Hasat kaydı silinsin mi? Bağlı çıkış varsa engellenir.\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></div></td></tr>')
    def hval(name,default=''):return h(rec[name] if rec and rec[name] is not None else default)
    content=f"""
    <section class="agri-grid">
      <div class="card"><div class="agri-card-title"><h2>🌾 {'Hasat Kaydını Düzenle' if rec else 'Hasat / Mahsul Stok Girişi'}</h2></div><form method="post" action="/agriculture/harvest/save" class="form"><input type="hidden" name="id" value="{hval('id')}">
        <label>Üretim Sezonu<select name="season_id" required><option value="">Seçin…</option>{season_options(seasons,rec['season_id'] if rec else None)}</select></label><label>Hasat Tarihi<input type="date" name="harvest_date" value="{hval('harvest_date',date.today().isoformat())}" required></label>
        <label>Mahsul<input name="product_name" value="{hval('product_name')}" placeholder="Arpa, buğday, saman, mısır silajı…" required></label><label>Miktar (kg)<input type="number" min="0.01" step="0.01" name="quantity_kg" value="{hval('quantity_kg')}" required></label>
        <label>Nem (%)<input type="number" min="0" max="100" step="0.01" name="moisture_pct" value="{hval('moisture_pct',0)}"></label><label>Kalite / Sınıf<input name="quality" value="{hval('quality')}"></label>
        <label>Depo<input name="warehouse" value="{hval('warehouse')}" placeholder="Merkez depo, silo 1…"></label><label>Tahmini Piyasa ₺/kg<input type="number" min="0" step="0.01" name="estimated_market_price" value="{hval('estimated_market_price',0)}"></label>
        <label class="full">Not<textarea name="notes">{hval('notes')}</textarea></label><div class="full agri-note">Hasat, mahsul stoğunu artırır; tek başına nakit gelir oluşturmaz. Stok değeri sezonun ekonomik sonucunda ayrıca gösterilir.</div><div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if rec else 'Hasadı Stoğa Al'}</button>{'<a class="btn alt" href="/agriculture/harvests">İptal</a>' if rec else ''}</div>
      </form></div>
      <div class="card"><h2>Verim ve Birim Maliyet</h2><p class="mut">Hasat kaydından sonra sistem kg/dekar verimi ve toplam sezon maliyetinden yaklaşık TL/kg üretim maliyetini hesaplar. Ana ürün ve saman gibi yan ürünler ayrı stok lotu olarak kaydedilebilir.</p></div>
    </section>
    <div class="card" style="margin-top:10px"><div class="agri-card-title"><h2>Mahsul Stokları</h2><span class="pill">{len(lots)} hasat lotu</span></div><div class="agri-table-wrap"><table style="min-width:1250px"><tr><th>Tarih</th><th>Mahsul / Tarla</th><th>Hasat</th><th>Kalan</th><th>Nem</th><th>Kalite</th><th>Depo</th><th>Piyasa</th><th>Stok Değeri</th><th>İşlem</th></tr>{''.join(lot_rows) or '<tr><td colspan="10">Henüz hasat kaydı yok.</td></tr>'}</table></div></div>
    """
    return "Hasat & Mahsul",shell("/agriculture/harvests",content)


def transfers_page(c, q):
    edit_transfer=(q.get('edit_transfer') or [''])[0]
    edit_sale=(q.get('edit_sale') or [''])[0]
    transfer_rec=c.execute('SELECT * FROM agri_internal_transfers WHERE id=?',(edit_transfer,)).fetchone() if edit_transfer else None
    sale_rec=c.execute('SELECT * FROM agri_sales WHERE id=?',(edit_sale,)).fetchone() if edit_sale else None
    lots=c.execute("""SELECT l.*,f.name field_name FROM agri_harvest_lots l JOIN agri_seasons s ON s.id=l.season_id JOIN agri_fields f ON f.id=s.field_id ORDER BY l.harvest_date DESC,l.id DESC""").fetchall()
    feeds=c.execute("SELECT id,name FROM feed_catalog WHERE active=1 ORDER BY name").fetchall()
    transfers=c.execute("""SELECT t.*,l.product_name,f.name feed_name,af.description agri_description FROM agri_internal_transfers t JOIN agri_harvest_lots l ON l.id=t.harvest_lot_id JOIN feed_catalog f ON f.id=t.feed_id LEFT JOIN agri_finance af ON af.id=t.agri_finance_id ORDER BY t.transfer_date DESC,t.id DESC""").fetchall()
    sales=c.execute("""SELECT s.*,l.product_name FROM agri_sales s JOIN agri_harvest_lots l ON l.id=s.harvest_lot_id ORDER BY s.sale_date DESC,s.id DESC""").fetchall()
    transfer_rows=''.join(f'<tr><td>{fmt_date(r["transfer_date"])}</td><td>{h(r["product_name"])}</td><td>{float(r["quantity_kg"]):,.2f} kg</td><td>{money(r["unit_price"])}</td><td>{money(float(r["quantity_kg"])*float(r["unit_price"]))}</td><td>{h(r["feed_name"])}</td><td><span class="agri-status">Bağlı 3 hareket</span></td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/transfers?edit_transfer={r["id"]}">Düzenle</a><form method="post" action="/agriculture/transfer/delete" onsubmit="return confirm(\'Tarım geliri, hayvancılık gideri ve yem stok girişi birlikte geri alınsın mı?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil / Geri Al</button></form></div></td></tr>' for r in transfers)
    sale_rows=''.join(f'<tr><td>{fmt_date(r["sale_date"])}</td><td>{h(r["product_name"])}</td><td>{float(r["quantity_kg"]):,.2f} kg</td><td>{money(r["unit_price"])}</td><td><b>{money(float(r["quantity_kg"])*float(r["unit_price"]))}</b></td><td>{h(r["buyer"]) or "-"}</td><td><div class="agri-row-actions"><a class="btn alt" href="/agriculture/transfers?edit_sale={r["id"]}">Düzenle</a><form method="post" action="/agriculture/sale/delete" onsubmit="return confirm(\'Satış geliri ve stok çıkışı geri alınsın mı?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil / Geri Al</button></form></div></td></tr>' for r in sales)
    def tval(name,default=''):return h(transfer_rec[name] if transfer_rec and transfer_rec[name] is not None else default)
    def sval(name,default=''):return h(sale_rec[name] if sale_rec and sale_rec[name] is not None else default)
    transfer_feed_options=''.join(f'<option value="{r["id"]}" {"selected" if transfer_rec and str(transfer_rec["feed_id"])==str(r["id"]) else ""}>{h(r["name"])}</option>' for r in feeds)
    sale_payment=sale_rec['payment_method'] if sale_rec and sale_rec['payment_method'] else 'Nakit'
    content=f"""
    <section class="agri-grid equal">
      <div class="card agri-transfer-box"><div class="agri-card-title"><h2>⇄ {'İç Transferi Düzenle' if transfer_rec else 'Hayvancılığa İç Transfer'}</h2></div><form method="post" action="/agriculture/transfer/save" class="form"><input type="hidden" name="id" value="{tval('id')}">
        <label>Mahsul Lotu<select id="agriTransferLot" name="harvest_lot_id" required><option value="">Seçin…</option>{lot_options(c,lots,transfer_rec['harvest_lot_id'] if transfer_rec else None)}</select></label><label>Tarih<input type="date" name="transfer_date" value="{tval('transfer_date',date.today().isoformat())}" required></label>
        <label>Miktar (kg)<input type="number" min="0.01" step="0.01" name="quantity_kg" value="{tval('quantity_kg')}" required></label><label>İç Transfer ₺/kg<input id="agriTransferPrice" type="number" min="0.01" step="0.01" name="unit_price" value="{tval('unit_price')}" required></label>
        <label class="full">Hedef Yem<select id="agriTransferFeed" name="feed_id" required><option value="">Yem Kataloğundan seçin…</option>{transfer_feed_options}</select></label><label class="full">Not<input name="notes" value="{tval('notes')}"></label>
        <div class="full agri-note">Tarım iç satış geliri + hayvancılık yem gideri + yem stok girişi oluşturur. Kasa/banka hareketi yaratmaz.</div><div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if transfer_rec else 'İç Transfer Oluştur'}</button>{'<a class="btn alt" href="/agriculture/transfers">İptal</a>' if transfer_rec else ''}</div>
      </form></div>
      <div class="card"><div class="agri-card-title"><h2>🚚 {'Dış Satışı Düzenle' if sale_rec else 'Dışarı Mahsul Satışı'}</h2></div><form method="post" action="/agriculture/sale/save" class="form"><input type="hidden" name="id" value="{sval('id')}">
        <label>Mahsul Lotu<select id="agriSaleLot" name="harvest_lot_id" required><option value="">Seçin…</option>{lot_options(c,lots,sale_rec['harvest_lot_id'] if sale_rec else None)}</select></label><label>Satış Tarihi<input type="date" name="sale_date" value="{sval('sale_date',date.today().isoformat())}" required></label>
        <label>Miktar (kg)<input type="number" min="0.01" step="0.01" name="quantity_kg" value="{sval('quantity_kg')}" required></label><label>Satış ₺/kg<input id="agriSalePrice" type="number" min="0.01" step="0.01" name="unit_price" value="{sval('unit_price')}" required></label>
        <label>Alıcı<input name="buyer" value="{sval('buyer')}"></label><label>Ödeme<select name="payment_method">{''.join(f'<option {"selected" if sale_payment==x else ""}>{x}</option>' for x in ('Nakit','Banka','Vadeli'))}</select></label><label class="full">Not<input name="notes" value="{sval('notes')}"></label><div class="full agri-form-actions"><button class="btn blue">{'Değişiklikleri Kaydet' if sale_rec else 'Dış Satışı Kaydet'}</button>{'<a class="btn alt" href="/agriculture/transfers">İptal</a>' if sale_rec else ''}</div>
      </form></div>
    </section>
    <script>
    (function(){{
      function normalize(value){{return (value || '').toLocaleLowerCase('tr-TR').replace(/[^a-z0-9çğıöşü]/g,'');}}
      function bindLot(selectId, priceId, feedId){{
        var lot=document.getElementById(selectId), price=document.getElementById(priceId);
        if(!lot || !price) return;
        lot.addEventListener('change',function(){{
          var option=lot.options[lot.selectedIndex];
          if(option && option.dataset.price && Number(option.dataset.price)>0) price.value=Number(option.dataset.price).toFixed(2);
          if(feedId && option){{
            var feed=document.getElementById(feedId), product=normalize(option.dataset.product);
            if(feed && product) for(var i=1;i<feed.options.length;i++){{
              var candidate=normalize(feed.options[i].text);
              if(candidate.includes(product) || product.includes(candidate)){{feed.selectedIndex=i;break;}}
            }}
          }}
        }});
      }}
      bindLot('agriTransferLot','agriTransferPrice','agriTransferFeed');
      bindLot('agriSaleLot','agriSalePrice');
    }})();
    </script>
    <section class="agri-two-tables" style="margin-top:10px"><div class="card"><div class="agri-card-title"><h2>İç Transfer Geçmişi</h2></div><div class="agri-table-wrap"><table style="min-width:900px"><tr><th>Tarih</th><th>Mahsul</th><th>Miktar</th><th>₺/kg</th><th>Toplam</th><th>Hedef Yem</th><th>Bağ</th><th>İşlem</th></tr>{transfer_rows or '<tr><td colspan="8">İç transfer yok.</td></tr>'}</table></div></div><div class="card"><div class="agri-card-title"><h2>Dış Satışlar</h2></div><div class="agri-table-wrap"><table style="min-width:800px"><tr><th>Tarih</th><th>Mahsul</th><th>Miktar</th><th>₺/kg</th><th>Toplam</th><th>Alıcı</th><th>İşlem</th></tr>{sale_rows or '<tr><td colspan="7">Dış satış yok.</td></tr>'}</table></div></div></section>
    """
    return "Satış & İç Transfer",shell("/agriculture/transfers",content)


def finance_page(c, q):
    edit_id=(q.get('edit') or [''])[0]
    rec=c.execute("SELECT * FROM agri_finance WHERE id=? AND COALESCE(source_type,'')=''",(edit_id,)).fetchone() if edit_id else None
    fields=c.execute("SELECT * FROM agri_fields WHERE active=1 ORDER BY name").fetchall()
    seasons=c.execute("""SELECT s.*,f.name field_name FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id ORDER BY s.season_year DESC,f.name""").fetchall()
    rows=c.execute("""SELECT af.*,f.name field_name,s.crop_name,s.season_year FROM agri_finance af LEFT JOIN agri_fields f ON f.id=af.field_id LEFT JOIN agri_seasons s ON s.id=af.season_id ORDER BY af.tx_date DESC,af.id DESC LIMIT 250""").fetchall()
    totals=c.execute("""SELECT
        COALESCE(SUM(CASE WHEN tx_type='Gelir' THEN amount ELSE 0 END),0) income,
        COALESCE(SUM(CASE WHEN tx_type='Gider' THEN amount ELSE 0 END),0) expense,
        COALESCE(SUM(CASE WHEN source_type='internal_transfer' THEN amount ELSE 0 END),0) internal_total
        FROM agri_finance""").fetchone()
    inc=float(totals['income'] or 0);exp=float(totals['expense'] or 0);internal_total=float(totals['internal_total'] or 0)
    def finance_action(r):
        if r['source_type']:
            source_links={'field_rent':'/agriculture/fields?edit=','operation':'/agriculture/operations?edit=','input_purchase':'/agriculture/inputs?edit=','sale':'/agriculture/transfers?edit_sale=','internal_transfer':'/agriculture/transfers?edit_transfer='}
            target=source_links.get(r['source_type'])
            return f'<a class="btn alt" href="{target}{r["source_id"]}">Kaynağa Git</a>' if target and r['source_id'] else '<span class="agri-status">Otomatik</span>'
        return f'<div class="agri-row-actions"><a class="btn alt" href="/agriculture/finance?edit={r["id"]}">Düzenle</a><form method="post" action="/agriculture/finance/delete" onsubmit="return confirm(\'Tarım finans kaydı silinsin mi?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></div>'
    table_rows=''.join(f'<tr><td>{fmt_date(r["tx_date"])}</td><td>{h(r["tx_type"])}</td><td>{h(r["category"])}</td><td>{h(r["description"])}</td><td>{h(r["field_name"]) or "-"}</td><td>{(str(r["season_year"])+" · "+h(r["crop_name"])) if r["season_id"] else "-"}</td><td>{h(r["payment_method"])}</td><td><b>{money(r["amount"])}</b></td><td>{finance_action(r)}</td></tr>' for r in rows)
    def fval(name,default=''):return h(rec[name] if rec and rec[name] is not None else default)
    tx_type=rec['tx_type'] if rec else 'Gider';category=rec['category'] if rec else 'Kira';payment=rec['payment_method'] if rec and rec['payment_method'] else 'Nakit'
    content=f"""
    <section class="agri-kpis"><div class="agri-kpi"><span>Tarım Geliri</span><b>{money(inc)}</b></div><div class="agri-kpi warn"><span>Tarım Gideri</span><b>{money(exp)}</b></div><div class="agri-kpi"><span>Tarım Defteri Neti</span><b>{money(inc-exp)}</b></div><div class="agri-kpi"><span>Hayvancılığa İç Transfer</span><b>{money(internal_total)}</b><small class="agri-subtle">Kasa hareketi değildir</small></div></section>
    <section class="agri-grid"><div class="card"><div class="agri-card-title"><h2>💰 {'Tarım Finans Kaydını Düzenle' if rec else 'Diğer Tarım Gelir/Gideri'}</h2></div><form method="post" action="/agriculture/finance/save" class="form"><input type="hidden" name="id" value="{fval('id')}">
      <label>Tarih<input type="date" name="tx_date" value="{fval('tx_date',date.today().isoformat())}" required></label><label>Tür<select name="tx_type">{''.join(f'<option {"selected" if tx_type==x else ""}>{x}</option>' for x in ('Gider','Gelir'))}</select></label>
      <label>Kategori<select name="category">{''.join(f'<option {"selected" if category==x else ""}>{x}</option>' for x in ('Kira','Elektrik','Sulama','Yakıt','İşçilik','Bakım / Onarım','Nakliye','Destekleme','Mahsul Satışı','Diğer'))}</select></label><label>Tutar<input type="number" min="0.01" step="0.01" name="amount" value="{fval('amount')}" required></label>
      <label>Tarla<select name="field_id"><option value="">Genel</option>{field_options(fields,rec['field_id'] if rec else None)}</select></label><label>Sezon<select name="season_id"><option value="">Genel</option>{season_options(seasons,rec['season_id'] if rec else None)}</select></label>
      <label>Ödeme<select name="payment_method">{''.join(f'<option {"selected" if payment==x else ""}>{x}</option>' for x in ('Nakit','Banka','Vadeli','Tahakkuk'))}</select></label><label>Açıklama<input name="description" value="{fval('description')}"></label><div class="full agri-form-actions"><button class="btn">{'Değişiklikleri Kaydet' if rec else 'Tarım Finansına Kaydet'}</button>{'<a class="btn alt" href="/agriculture/finance">İptal</a>' if rec else ''}</div>
    </form></div><div class="card"><h2>Ayrı İşletme Kolu</h2><div class="agri-note">Bu kayıtlar mevcut hayvancılık Finans ekranına ve hayvancılık kârına eklenmez. Tarım & Ziraat raporlarında ayrı tutulur.</div><p class="mut">İç transferler yönetimsel gelir/giderdir ve gerçek kasa hareketi değildir.</p></div></section>
    <div class="card" style="margin-top:10px"><div class="agri-card-title"><h2>Tarım Finans Hareketleri</h2><span class="pill">{len(rows)} kayıt</span></div><div class="agri-table-wrap"><table style="min-width:1200px"><tr><th>Tarih</th><th>Tür</th><th>Kategori</th><th>Açıklama</th><th>Tarla</th><th>Sezon</th><th>Ödeme</th><th>Tutar</th><th>İşlem</th></tr>{table_rows or '<tr><td colspan="9">Tarım finans kaydı yok.</td></tr>'}</table></div></div>
    """
    return "Tarım Finans",shell("/agriculture/finance",content)


def reports_page(c, q):
    try:
        year=int((q.get('year') or [date.today().year])[0])
    except (TypeError, ValueError):
        year=date.today().year
    year=min(2100,max(2000,year))
    seasons=c.execute("""SELECT s.*,f.name field_name FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id WHERE s.season_year=? ORDER BY f.name,s.crop_name""",(year,)).fetchall()
    rows=[];total_cost=total_value=total_harvest=0
    for r in seasons:
        cost=season_cost(c,r['id']);qty=season_harvest(c,r['id']);value,realized,stock=season_value(c,r['id']);profit=value-cost
        total_cost+=cost;total_value+=value;total_harvest+=qty
        rows.append(f'<tr><td>{h(r["field_name"])}</td><td>{h(r["crop_name"])}</td><td>{float(r["cultivated_area_da"]):g} da</td><td>{money(cost)}</td><td>{qty:,.2f} kg</td><td>{(qty/float(r["cultivated_area_da"] or 1)):,.1f} kg/da</td><td>{money(cost/qty) if qty>0 else "-"}</td><td>{money(realized)}</td><td>{money(stock)}</td><td><b class="{"agri-positive" if profit>=0 else "agri-negative"}">{money(profit)}</b></td></tr>')
    finance=c.execute("SELECT tx_type,category,SUM(amount) amount FROM agri_finance WHERE substr(tx_date,1,4)=? GROUP BY tx_type,category ORDER BY tx_type,amount DESC",(str(year),)).fetchall()
    finance_rows=''.join(f'<tr><td>{h(r["tx_type"])}</td><td>{h(r["category"])}</td><td><b>{money(r["amount"])}</b></td></tr>' for r in finance)
    content=f"""
    <form method="get" class="card" style="margin-bottom:10px"><div class="form"><label>Rapor Yılı<input type="number" min="2000" max="2100" name="year" value="{year}"></label><div style="align-self:end"><button class="btn">Raporu Getir</button></div></div></form>
    <section class="agri-kpis"><div class="agri-kpi"><span>Toplam Üretim Maliyeti</span><b>{money(total_cost)}</b></div><div class="agri-kpi"><span>Toplam Hasat</span><b>{total_harvest:,.0f} kg</b></div><div class="agri-kpi"><span>Satış + Transfer + Stok Değeri</span><b>{money(total_value)}</b></div><div class="agri-kpi"><span>Sezon Ekonomik Sonucu</span><b>{money(total_value-total_cost)}</b></div></section>
    <section class="agri-grid"><div class="card"><div class="agri-card-title"><h2>{year} Tarla / Ürün Kârlılığı</h2></div><div class="agri-table-wrap"><table style="min-width:1150px"><tr><th>Tarla</th><th>Ürün</th><th>Alan</th><th>Maliyet</th><th>Hasat</th><th>Verim</th><th>Üretim ₺/kg</th><th>Gerçek Gelir</th><th>Kalan Stok</th><th>Ekonomik Sonuç</th></tr>{''.join(rows) or '<tr><td colspan="10">Bu yıl için sezon kaydı yok.</td></tr>'}</table></div></div><div class="card"><div class="agri-card-title"><h2>Tarım Finans Özeti</h2></div><table><tr><th>Tür</th><th>Kategori</th><th>Toplam</th></tr>{finance_rows or '<tr><td colspan="3">Kayıt yok.</td></tr>'}</table><div class="agri-note" style="margin-top:10px"><b>İşletme geneli:</b> İç transfer tarımda gelir, hayvancılıkta gider olarak bölüm kârlılığını gösterir; konsolide toplamda birbirini götürür.</div></div></section>
    """
    return "Tarım Raporları",shell("/agriculture/reports",content)


def render_get(c, path, q):
    if path == "/agriculture": return dashboard(c)
    if path == "/agriculture/fields": return fields_page(c,q)
    if path == "/agriculture/seasons": return seasons_page(c,q)
    if path == "/agriculture/operations": return operations_page(c,q)
    if path == "/agriculture/inputs": return inputs_page(c,q)
    if path == "/agriculture/harvests": return harvests_page(c,q)
    if path == "/agriculture/transfers": return transfers_page(c,q)
    if path == "/agriculture/finance": return finance_page(c,q)
    if path == "/agriculture/reports": return reports_page(c,q)
    return None


def _field_and_season(c, season_id):
    row=c.execute("""SELECT s.*,f.name field_name,f.area_da field_area FROM agri_seasons s JOIN agri_fields f ON f.id=s.field_id WHERE s.id=?""",(season_id,)).fetchone()
    if not row: raise AgricultureError("Üretim sezonu bulunamadı.")
    return row


def handle_post(c, path, f):
    created=now_iso()
    if path=="/agriculture/field/save":
        record_id=as_int(f,"id",0);name=str(f.get('name') or '').strip();area=as_float(f,'area_da')
        if not name or area<=0:raise AgricultureError("Tarla adı ve 0'dan büyük alan zorunludur.")
        ownership=str(f.get('ownership_type') or 'Özmal');rent=as_float(f,'rent_amount') if ownership=='Kiralık' else 0.0
        values=(name,str(f.get('code') or '').strip(),ownership,area,str(f.get('water_type') or 'Kuru'),str(f.get('province') or '').strip(),str(f.get('district') or '').strip(),str(f.get('village') or '').strip(),str(f.get('block_no') or '').strip(),str(f.get('parcel_no') or '').strip(),str(f.get('landlord') or '').strip(),str(f.get('rent_start') or '').strip(),str(f.get('rent_end') or '').strip(),rent,str(f.get('rent_payment_date') or '').strip(),str(f.get('notes') or '').strip())
        if record_id:
            old=c.execute('SELECT * FROM agri_fields WHERE id=?',(record_id,)).fetchone()
            if not old:raise AgricultureError('Tarla kaydı bulunamadı.')
            c.execute("""UPDATE agri_fields SET name=?,code=?,ownership_type=?,area_da=?,water_type=?,province=?,district=?,village=?,block_no=?,parcel_no=?,landlord=?,rent_start=?,rent_end=?,rent_amount=?,rent_payment_date=?,notes=? WHERE id=?""",(*values,record_id))
        else:
            c.execute("""INSERT INTO agri_fields(name,code,ownership_type,area_da,water_type,province,district,village,block_no,parcel_no,landlord,rent_start,rent_end,rent_amount,rent_payment_date,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(*values,created));record_id=c.execute('SELECT last_insert_rowid()').fetchone()[0];old=None
        rent_finance_id=(old['rent_finance_id'] if old else None)
        if f.get('post_rent')=='yes' and ownership=='Kiralık' and rent>0:
            if rent_finance_id:
                c.execute("UPDATE agri_finance SET tx_date=?,amount=?,description=?,field_id=? WHERE id=?",(f.get('rent_payment_date') or date.today().isoformat(),rent,f'{name} yıllık arazi kirası',record_id,rent_finance_id))
            else:
                c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,source_type,source_id,created_at) VALUES(?,'Gider','Kira',?,?,?,?, 'field_rent',?,?)""",(f.get('rent_payment_date') or date.today().isoformat(),rent,f'{name} yıllık arazi kirası','Tahakkuk',record_id,record_id,created));rent_finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            c.execute('UPDATE agri_fields SET rent_finance_id=? WHERE id=?',(rent_finance_id,record_id))
        elif rent_finance_id:
            c.execute('DELETE FROM agri_finance WHERE id=?',(rent_finance_id,));c.execute('UPDATE agri_fields SET rent_finance_id=NULL WHERE id=?',(record_id,))
        return '/agriculture/fields','Tarla kartı kaydedildi.','Tarla kartını kaydetti',name

    if path=="/agriculture/field/archive":
        rid=as_int(f,'id');row=c.execute('SELECT name FROM agri_fields WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('Tarla bulunamadı.')
        c.execute('UPDATE agri_fields SET active=0 WHERE id=?',(rid,))
        return '/agriculture/fields','Tarla pasife alındı; geçmiş sezonlar korundu.','Tarlayı pasife aldı',row['name']

    if path=="/agriculture/field/delete":
        rid=as_int(f,'id');row=c.execute('SELECT * FROM agri_fields WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('Tarla bulunamadı.')
        if c.execute('SELECT 1 FROM agri_seasons WHERE field_id=? LIMIT 1',(rid,)).fetchone():raise AgricultureError('Bu tarlaya bağlı üretim sezonu var. Önce bağlı sezonları silin.')
        other_finance=c.execute('SELECT 1 FROM agri_finance WHERE field_id=? AND id<>COALESCE(?,0) LIMIT 1',(rid,row['rent_finance_id'])).fetchone()
        if other_finance:raise AgricultureError('Bu tarlaya bağlı Tarım Finans kaydı var. Önce bağlı finans kaydını silin.')
        if row['rent_finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(row['rent_finance_id'],))
        c.execute('DELETE FROM agri_fields WHERE id=?',(rid,))
        return '/agriculture/fields','Tarla ve bağlı kira kaydı silindi.','Tarlayı sildi',row['name']

    if path=="/agriculture/season/save":
        rid=as_int(f,'id',0);field_id=as_int(f,'field_id');year=as_int(f,'season_year');crop=str(f.get('crop_name') or '').strip();area=as_float(f,'cultivated_area_da')
        field=c.execute('SELECT * FROM agri_fields WHERE id=? AND active=1',(field_id,)).fetchone()
        if not field:raise AgricultureError('Aktif tarla seçilmelidir.')
        if not crop or area<=0 or area>float(field['area_da'] or 0)+0.001:raise AgricultureError(f'Ekilen alan 0 ile tarla alanı ({float(field["area_da"]):g} da) arasında olmalıdır.')
        values=(field_id,year,crop,area,f.get('start_date') or '',as_float(f,'expected_yield_kg_da'),f.get('status') or 'Planlandı',f.get('notes') or '')
        if rid:
            if not c.execute('SELECT 1 FROM agri_seasons WHERE id=?',(rid,)).fetchone():raise AgricultureError('Üretim sezonu bulunamadı.')
            c.execute('UPDATE agri_seasons SET field_id=?,season_year=?,crop_name=?,cultivated_area_da=?,start_date=?,expected_yield_kg_da=?,status=?,notes=? WHERE id=?',(*values,rid))
        else:c.execute("""INSERT INTO agri_seasons(field_id,season_year,crop_name,cultivated_area_da,start_date,expected_yield_kg_da,status,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)""",(*values,created))
        return '/agriculture/seasons','Üretim sezonu güncellendi.' if rid else 'Üretim sezonu oluşturuldu.','Üretim sezonunu güncelledi' if rid else 'Üretim sezonu oluşturdu',f'{field["name"]} · {year} · {crop}'

    if path=="/agriculture/season/delete":
        rid=as_int(f,'id');row=_field_and_season(c,rid)
        linked=sum(c.execute(sql,(rid,)).fetchone()[0] for sql in ('SELECT COUNT(*) FROM agri_operations WHERE season_id=?','SELECT COUNT(*) FROM agri_harvest_lots WHERE season_id=?','SELECT COUNT(*) FROM agri_finance WHERE season_id=?'))
        if linked:raise AgricultureError('Bu sezona bağlı işlem, hasat veya finans kaydı var. Önce bağlı kayıtları silin.')
        c.execute('DELETE FROM agri_seasons WHERE id=?',(rid,))
        return '/agriculture/seasons','Üretim sezonu silindi.','Üretim sezonunu sildi',f'{row["field_name"]} · {row["crop_name"]}'

    if path=="/agriculture/season/close":
        rid=as_int(f,'id');row=_field_and_season(c,rid);c.execute("UPDATE agri_seasons SET status='Kapandı',closed_at=? WHERE id=?",(created,rid))
        return '/agriculture/seasons','Sezon kapatıldı; geçmiş maliyet ve stok kayıtları donduruldu.','Üretim sezonunu kapattı',f'{row["field_name"]} · {row["crop_name"]}'

    if path=="/agriculture/input/purchase":
        rid=as_int(f,'id',0);name=str(f.get('name') or '').strip();category=str(f.get('category') or 'Diğer');unit=str(f.get('unit') or 'kg');qty=as_float(f,'quantity');unit_cost=as_float(f,'unit_cost')
        if not name or qty<=0 or unit_cost<0:raise AgricultureError('Girdi adı, miktarı ve birim maliyeti geçerli olmalıdır.')
        item=c.execute('SELECT * FROM agri_input_catalog WHERE lower(name)=lower(?)',(name,)).fetchone()
        if item:
            input_id=item['id'];unit=item['unit']
        else:
            c.execute('INSERT INTO agri_input_catalog(name,category,unit,created_at) VALUES(?,?,?,?)',(name,category,unit,created));input_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        amount=round(qty*unit_cost,2);tx_date=f.get('tx_date') or date.today().isoformat();desc=f'{name} girdi alımı · {qty:g} {unit} × {unit_cost:g} TL'
        if rid:
            old=c.execute("SELECT * FROM agri_input_transactions WHERE id=? AND tx_type='Giriş'",(rid,)).fetchone()
            if not old:raise AgricultureError('Girdi alımı bulunamadı.')
            remaining=input_balance(c,old['input_id'])-float(old['quantity'])+(qty if input_id==old['input_id'] else 0)
            if remaining < -0.0001:raise AgricultureError('Yeni miktar kullanılan stoktan az olamaz.')
            finance_id=old['finance_id']
            if not finance_id or not c.execute('SELECT 1 FROM agri_finance WHERE id=?',(finance_id,)).fetchone():
                c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,source_type,source_id,created_at) VALUES(?,'Gider',?,?,?,?, 'input_purchase',?,?)""",(tx_date,category,amount,desc,f.get('payment_method') or 'Nakit',rid,created));finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            else:c.execute("""UPDATE agri_finance SET tx_date=?,tx_type='Gider',category=?,amount=?,description=?,payment_method=?,source_type='input_purchase',source_id=? WHERE id=?""",(tx_date,category,amount,desc,f.get('payment_method') or 'Nakit',rid,finance_id))
            c.execute('UPDATE agri_input_transactions SET input_id=?,tx_date=?,quantity=?,unit_cost=?,supplier=?,lot_no=?,notes=?,finance_id=? WHERE id=?',(input_id,tx_date,qty,unit_cost,f.get('supplier') or '',f.get('lot_no') or '',f.get('notes') or '',finance_id,rid))
            return '/agriculture/inputs','Girdi alımı, stok ve finans gideri güncellendi.','Tarım girdi alımını güncelledi',desc
        c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,source_type,created_at) VALUES(?,'Gider',?,?,?,?, 'input_purchase',?)""",(tx_date,category,amount,desc,f.get('payment_method') or 'Nakit',created));finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        c.execute("""INSERT INTO agri_input_transactions(input_id,tx_date,tx_type,quantity,unit_cost,supplier,lot_no,notes,finance_id,source_type,created_at) VALUES(?,?,'Giriş',?,?,?,?,?,?, 'purchase',?)""",(input_id,tx_date,qty,unit_cost,f.get('supplier') or '',f.get('lot_no') or '',f.get('notes') or '',finance_id,created));tx_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        c.execute('UPDATE agri_finance SET source_id=? WHERE id=?',(tx_id,finance_id))
        return '/agriculture/inputs','Girdi stoğa alındı ve Tarım Finans gideri oluşturuldu.','Tarım girdisi satın aldı',desc

    if path=="/agriculture/input/delete":
        rid=as_int(f,'id');row=c.execute("SELECT t.*,i.name FROM agri_input_transactions t JOIN agri_input_catalog i ON i.id=t.input_id WHERE t.id=? AND t.tx_type='Giriş'",(rid,)).fetchone()
        if not row:raise AgricultureError('Girdi alımı bulunamadı.')
        if input_balance(c,row['input_id'])-float(row['quantity']) < -0.0001:raise AgricultureError('Bu alımın bir kısmı tarlada kullanılmış. Stok eksiye düşeceği için alım silinemez.')
        if row['finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(row['finance_id'],))
        c.execute('DELETE FROM agri_input_transactions WHERE id=?',(rid,))
        return '/agriculture/inputs','Girdi alımı ve bağlı Tarım Finans gideri geri alındı.','Tarım girdi alımını sildi',row['name']

    if path=="/agriculture/operation/save":
        rid=as_int(f,'id',0);old=c.execute('SELECT * FROM agri_operations WHERE id=?',(rid,)).fetchone() if rid else None
        if rid and not old:raise AgricultureError('Tarla işlemi bulunamadı.')
        season_id=as_int(f,'season_id');season=_field_and_season(c,season_id)
        if season['status']=='Kapandı' and not (old and int(old['season_id'])==season_id):raise AgricultureError('Kapalı sezona yeni işlem eklenemez.')
        area=as_float(f,'area_da');fuel_l=as_float(f,'fuel_liters');fuel_price=as_float(f,'fuel_unit_price');labor=as_float(f,'labor_cost');contractor=as_float(f,'contractor_cost');other=as_float(f,'other_cost')
        base_cost=round(fuel_l*fuel_price+labor+contractor+other,2);op_type=str(f.get('operation_type') or 'Diğer');op_date=f.get('operation_date') or date.today().isoformat()
        input_id=as_int(f,'input_id',0);input_qty=as_float(f,'input_quantity')
        old_input=c.execute('SELECT * FROM agri_operation_inputs WHERE operation_id=?',(rid,)).fetchone() if rid else None
        if input_id or input_qty:
            item=c.execute('SELECT * FROM agri_input_catalog WHERE id=? AND active=1',(input_id,)).fetchone()
            if not item or input_qty<=0:raise AgricultureError('Girdi seçildiğinde 0’dan büyük kullanım miktarı girilmelidir.')
            available=input_balance(c,input_id)+(float(old_input['quantity']) if old_input and old_input['input_id']==input_id else 0)
            if input_qty>available+0.0001:raise AgricultureError(f'{item["name"]} stoğu yetersiz. Mevcut: {available:g} {item["unit"]}, gereken: {input_qty:g} {item["unit"]}.')
        if rid:
            c.execute("DELETE FROM agri_input_transactions WHERE source_type='operation' AND source_id=?",(rid,));c.execute('DELETE FROM agri_operation_inputs WHERE operation_id=?',(rid,))
            if old['finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(old['finance_id'],))
        finance_id=None
        if base_cost>0:
            desc=f'{season["field_name"]} · {season["crop_name"]} · {op_type}'
            c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,season_id,source_type,created_at) VALUES(?,'Gider','Tarla İşlemi',?,?,?,?,?,'operation',?)""",(op_date,base_cost,desc,f.get('payment_method') or 'Nakit',season['field_id'],season_id,created));finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        if rid:
            c.execute('UPDATE agri_operations SET season_id=?,operation_date=?,operation_type=?,area_da=?,fuel_liters=?,fuel_unit_price=?,labor_cost=?,contractor_cost=?,other_cost=?,total_cost=?,finance_id=?,notes=? WHERE id=?',(season_id,op_date,op_type,area,fuel_l,fuel_price,labor,contractor,other,base_cost,finance_id,f.get('notes') or '',rid));op_id=rid
        else:
            c.execute("""INSERT INTO agri_operations(season_id,operation_date,operation_type,area_da,fuel_liters,fuel_unit_price,labor_cost,contractor_cost,other_cost,total_cost,finance_id,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",(season_id,op_date,op_type,area,fuel_l,fuel_price,labor,contractor,other,base_cost,finance_id,f.get('notes') or '',created));op_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        if finance_id:c.execute('UPDATE agri_finance SET source_id=? WHERE id=?',(op_id,finance_id))
        if input_id or input_qty:
            item=c.execute('SELECT * FROM agri_input_catalog WHERE id=? AND active=1',(input_id,)).fetchone()
            if not item or input_qty<=0:raise AgricultureError('Girdi seçildiğinde 0’dan büyük kullanım miktarı girilmelidir.')
            balance=input_balance(c,input_id)
            if input_qty>balance+0.0001:raise AgricultureError(f'{item["name"]} stoğu yetersiz. Mevcut: {balance:g} {item["unit"]}, gereken: {input_qty:g} {item["unit"]}.')
            unit_cost=input_average_cost(c,input_id)
            c.execute("""INSERT INTO agri_input_transactions(input_id,tx_date,tx_type,quantity,unit_cost,notes,source_type,source_id,created_at) VALUES(?,?,'Çıkış',?,?,?,'operation',?,?)""",(input_id,op_date,input_qty,unit_cost,f'{season["field_name"]} · {op_type}',op_id,created));stock_tx_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            c.execute('INSERT INTO agri_operation_inputs(operation_id,input_id,quantity,unit_cost,stock_tx_id,created_at) VALUES(?,?,?,?,?,?)',(op_id,input_id,input_qty,unit_cost,stock_tx_id,created))
        return '/agriculture/operations','Tarla işlemi, maliyeti ve varsa girdi tüketimi güncellendi.' if rid else 'Tarla işlemi, maliyeti ve varsa girdi tüketimi kaydedildi.','Tarla işlemini güncelledi' if rid else 'Tarla işlemi kaydetti',f'{season["field_name"]} · {op_type}'

    if path=="/agriculture/operation/delete":
        rid=as_int(f,'id');row=c.execute('SELECT * FROM agri_operations WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('Tarla işlemi bulunamadı.')
        c.execute("DELETE FROM agri_input_transactions WHERE source_type='operation' AND source_id=?",(rid,));c.execute('DELETE FROM agri_operation_inputs WHERE operation_id=?',(rid,))
        if row['finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(row['finance_id'],))
        c.execute('DELETE FROM agri_operations WHERE id=?',(rid,))
        return '/agriculture/operations','Tarla işlemi, bağlı girdi çıkışı ve finans gideri geri alındı.','Tarla işlemini sildi',str(rid)

    if path=="/agriculture/harvest/save":
        rid=as_int(f,'id',0);season_id=as_int(f,'season_id');season=_field_and_season(c,season_id);qty=as_float(f,'quantity_kg');product=str(f.get('product_name') or '').strip()
        if qty<=0 or not product:raise AgricultureError('Mahsul adı ve 0’dan büyük miktar zorunludur.')
        harvest_date=f.get('harvest_date') or date.today().isoformat()
        price=as_float(f,'estimated_market_price');values=(season_id,harvest_date,product,qty,as_float(f,'moisture_pct'),f.get('quality') or '',f.get('warehouse') or '',price,f.get('notes') or '')
        if rid:
            old=c.execute('SELECT * FROM agri_harvest_lots WHERE id=?',(rid,)).fetchone()
            if not old:raise AgricultureError('Hasat lotu bulunamadı.')
            outputs=float(old['quantity_kg'])-harvest_balance(c,rid)
            if qty+0.0001<outputs:raise AgricultureError(f'Yeni hasat miktarı yapılmış {outputs:g} kg çıkıştan az olamaz.')
            if int(old['season_id'])!=season_id and outputs>0.0001:raise AgricultureError('Satış veya transfer yapılmış hasadın üretim sezonu değiştirilemez.')
            c.execute('UPDATE agri_harvest_lots SET season_id=?,harvest_date=?,product_name=?,quantity_kg=?,moisture_pct=?,quality=?,warehouse=?,estimated_market_price=?,notes=? WHERE id=?',(*values,rid));lot_id=rid
            entry=c.execute("SELECT id FROM agri_product_transactions WHERE harvest_lot_id=? AND tx_type='Giriş' ORDER BY id LIMIT 1",(rid,)).fetchone()
            if entry:c.execute("UPDATE agri_product_transactions SET tx_date=?,quantity_kg=?,unit_price=?,source_type='harvest',source_id=?,notes=? WHERE id=?",(harvest_date,qty,price,rid,f'{season["field_name"]} hasadı',entry['id']))
            else:c.execute("""INSERT INTO agri_product_transactions(harvest_lot_id,tx_date,tx_type,quantity_kg,unit_price,source_type,source_id,notes,created_at) VALUES(?,?,'Giriş',?,?,'harvest',?,?,?)""",(rid,harvest_date,qty,price,rid,f'{season["field_name"]} hasadı',created))
        else:
            c.execute("""INSERT INTO agri_harvest_lots(season_id,harvest_date,product_name,quantity_kg,moisture_pct,quality,warehouse,estimated_market_price,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",(*values,created));lot_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            c.execute("""INSERT INTO agri_product_transactions(harvest_lot_id,tx_date,tx_type,quantity_kg,unit_price,source_type,source_id,notes,created_at) VALUES(?,?,'Giriş',?,?,'harvest',?,?,?)""",(lot_id,harvest_date,qty,price,lot_id,f'{season["field_name"]} hasadı',created))
        c.execute("UPDATE agri_seasons SET status='Hasat Tamamlandı' WHERE id=?",(season_id,))
        return '/agriculture/harvests','Hasat mahsul stoğuna alındı; nakit gelir oluşturulmadı.','Hasat kaydetti',f'{product} · {qty:g} kg'

    if path=="/agriculture/harvest/delete":
        rid=as_int(f,'id');row=c.execute('SELECT * FROM agri_harvest_lots WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('Hasat lotu bulunamadı.')
        exits=c.execute("SELECT COUNT(*) n FROM agri_product_transactions WHERE harvest_lot_id=? AND tx_type<>'Giriş'",(rid,)).fetchone()['n']
        if exits:raise AgricultureError('Bu hasat lotundan satış veya transfer yapılmış. Önce bağlı çıkışları geri alın.')
        c.execute('DELETE FROM agri_product_transactions WHERE harvest_lot_id=?',(rid,));c.execute('DELETE FROM agri_harvest_lots WHERE id=?',(rid,))
        return '/agriculture/harvests','Hasat kaydı silindi.','Hasat kaydını sildi',row['product_name']

    if path in ("/agriculture/sale/save","/agriculture/transfer/save"):
        rid=as_int(f,'id',0);is_sale=path.endswith('/sale/save')
        old=c.execute('SELECT * FROM agri_sales WHERE id=?',(rid,)).fetchone() if rid and is_sale else c.execute('SELECT * FROM agri_internal_transfers WHERE id=?',(rid,)).fetchone() if rid else None
        if rid and not old:raise AgricultureError('Satış kaydı bulunamadı.' if is_sale else 'İç transfer bulunamadı.')
        lot_id=as_int(f,'harvest_lot_id');lot=c.execute("""SELECT l.*,s.field_id,s.id season_id,fld.name field_name FROM agri_harvest_lots l JOIN agri_seasons s ON s.id=l.season_id JOIN agri_fields fld ON fld.id=s.field_id WHERE l.id=?""",(lot_id,)).fetchone()
        if not lot:raise AgricultureError('Mahsul lotu bulunamadı.')
        qty=as_float(f,'quantity_kg');unit_price=as_float(f,'unit_price')
        if qty<=0 or unit_price<=0:raise AgricultureError('Miktar ve birim fiyat 0’dan büyük olmalıdır.')
        old_product_tx=None
        if old:
            old_product_tx=c.execute('SELECT * FROM agri_product_transactions WHERE id=?',(old['stock_tx_id'] if is_sale else old['product_stock_tx_id'],)).fetchone()
        restorable=float(old_product_tx['quantity_kg'] or 0) if old_product_tx and int(old_product_tx['harvest_lot_id'])==lot_id else 0.0
        available=harvest_balance(c,lot_id)+restorable
        if qty>available+0.0001:raise AgricultureError(f'Mahsul stoğu yetersiz. Mevcut {available:g} kg, istenen {qty:g} kg.')
        amount=round(qty*unit_price,2)
        if is_sale:
            tx_date=f.get('sale_date') or date.today().isoformat();payment=f.get('payment_method') or 'Nakit';desc=f'{lot["product_name"]} dış satışı · {qty:g} kg × {unit_price:g} TL'
            if not rid:
                c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,season_id,source_type,created_at) VALUES(?,'Gelir','Mahsul Satışı',?,?,?,?,?,'sale',?)""",(tx_date,amount,desc,payment,lot['field_id'],lot['season_id'],created));finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
                c.execute("""INSERT INTO agri_product_transactions(harvest_lot_id,tx_date,tx_type,quantity_kg,unit_price,source_type,notes,created_at) VALUES(?,?,'Satış',?,?,'sale',?,?)""",(lot_id,tx_date,qty,unit_price,desc,created));stock_tx_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
                c.execute("""INSERT INTO agri_sales(harvest_lot_id,sale_date,quantity_kg,unit_price,buyer,payment_method,finance_id,stock_tx_id,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",(lot_id,tx_date,qty,unit_price,f.get('buyer') or '',payment,finance_id,stock_tx_id,f.get('notes') or '',created));rid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            else:
                finance_id=old['finance_id'];stock_tx_id=old['stock_tx_id']
                if not finance_id or not c.execute('SELECT 1 FROM agri_finance WHERE id=?',(finance_id,)).fetchone():
                    c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,season_id,source_type,source_id,created_at) VALUES(?,'Gelir','Mahsul Satışı',?,?,?,?,?,'sale',?,?)""",(tx_date,amount,desc,payment,lot['field_id'],lot['season_id'],rid,created));finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
                else:c.execute("""UPDATE agri_finance SET tx_date=?,tx_type='Gelir',category='Mahsul Satışı',amount=?,description=?,payment_method=?,field_id=?,season_id=?,source_type='sale',source_id=? WHERE id=?""",(tx_date,amount,desc,payment,lot['field_id'],lot['season_id'],rid,finance_id))
                if not stock_tx_id or not c.execute('SELECT 1 FROM agri_product_transactions WHERE id=?',(stock_tx_id,)).fetchone():
                    c.execute("""INSERT INTO agri_product_transactions(harvest_lot_id,tx_date,tx_type,quantity_kg,unit_price,source_type,source_id,notes,created_at) VALUES(?,?,'Satış',?,?,'sale',?,?,?)""",(lot_id,tx_date,qty,unit_price,rid,desc,created));stock_tx_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
                else:c.execute("""UPDATE agri_product_transactions SET harvest_lot_id=?,tx_date=?,tx_type='Satış',quantity_kg=?,unit_price=?,source_type='sale',source_id=?,notes=? WHERE id=?""",(lot_id,tx_date,qty,unit_price,rid,desc,stock_tx_id))
                c.execute("""UPDATE agri_sales SET harvest_lot_id=?,sale_date=?,quantity_kg=?,unit_price=?,buyer=?,payment_method=?,finance_id=?,stock_tx_id=?,notes=? WHERE id=?""",(lot_id,tx_date,qty,unit_price,f.get('buyer') or '',payment,finance_id,stock_tx_id,f.get('notes') or '',rid))
            c.execute('UPDATE agri_finance SET source_id=? WHERE id=?',(rid,finance_id));c.execute('UPDATE agri_product_transactions SET source_id=? WHERE id=?',(rid,stock_tx_id))
            return '/agriculture/transfers','Dış satış, Tarım Finans geliri ve mahsul stok çıkışı güncellendi.' if old else 'Dış satış geliri ve mahsul stok çıkışı kaydedildi.','Mahsul satışını güncelledi' if old else 'Mahsul satışı kaydetti',desc

        tx_date=f.get('transfer_date') or date.today().isoformat();feed_id=as_int(f,'feed_id');feed=c.execute('SELECT * FROM feed_catalog WHERE id=? AND active=1',(feed_id,)).fetchone()
        if not feed:raise AgricultureError('Hedef yem kataloğu kaydı bulunamadı.')
        old_feed_tx=c.execute('SELECT * FROM feed_stock_transactions WHERE id=?',(old['feed_stock_tx_id'],)).fetchone() if old and old['feed_stock_tx_id'] else None
        if old_feed_tx:
            old_feed_id=int(old_feed_tx['feed_id']);old_feed_qty=float(old_feed_tx['quantity_kg'] or 0)
            if old_feed_id==feed_id:
                projected=feed_stock_balance(c,feed_id)-old_feed_qty+qty
            else:
                projected=feed_stock_balance(c,old_feed_id)-old_feed_qty
            if projected < -0.0001:raise AgricultureError('Bu iç transfer yem stoğunda kullanılmış. Miktar azaltılamaz veya hedef yem değiştirilemez.')
        desc=f'{lot["product_name"]} hayvancılığa iç transfer · {qty:g} kg × {unit_price:g} TL · hedef yem: {feed["name"]}'
        if not rid:
            c.execute("""INSERT INTO agri_internal_transfers(harvest_lot_id,transfer_date,quantity_kg,unit_price,feed_id,notes,created_at) VALUES(?,?,?,?,?,?,?)""",(lot_id,tx_date,qty,unit_price,feed_id,f.get('notes') or '',created));rid=c.execute('SELECT last_insert_rowid()').fetchone()[0]
            agri_finance_id=livestock_finance_id=feed_stock_id=feed_price_id=product_tx_id=None
        else:
            agri_finance_id=old['agri_finance_id'];livestock_finance_id=old['livestock_finance_id'];feed_stock_id=old['feed_stock_tx_id'];feed_price_id=old['feed_price_id'];product_tx_id=old['product_stock_tx_id']
        if not agri_finance_id or not c.execute('SELECT 1 FROM agri_finance WHERE id=?',(agri_finance_id,)).fetchone():
            c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,season_id,source_type,source_id,internal_transfer_id,created_at) VALUES(?,'Gelir','Hayvancılığa İç Transfer',? ,?,'İç Transfer',?,?,'internal_transfer',?,?,?)""",(tx_date,amount,desc,lot['field_id'],lot['season_id'],rid,rid,created));agri_finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        else:c.execute("""UPDATE agri_finance SET tx_date=?,tx_type='Gelir',category='Hayvancılığa İç Transfer',amount=?,description=?,payment_method='İç Transfer',field_id=?,season_id=?,source_type='internal_transfer',source_id=?,internal_transfer_id=? WHERE id=?""",(tx_date,amount,desc,lot['field_id'],lot['season_id'],rid,rid,agri_finance_id))
        if not livestock_finance_id or not c.execute('SELECT 1 FROM finance WHERE id=?',(livestock_finance_id,)).fetchone():
            c.execute("""INSERT INTO finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) VALUES(?,'Gider','Yem',?,?,'İç Transfer',NULL,?,'AGRI_INTERNAL')""",(tx_date,amount,desc,created));livestock_finance_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        else:c.execute("""UPDATE finance SET tx_date=?,tx_type='Gider',category='Yem',amount=?,description=?,payment_method='İç Transfer',animal_id=NULL,animal_status_action='AGRI_INTERNAL' WHERE id=?""",(tx_date,amount,desc,livestock_finance_id))
        if not feed_stock_id or not c.execute('SELECT 1 FROM feed_stock_transactions WHERE id=?',(feed_stock_id,)).fetchone():
            c.execute("""INSERT INTO feed_stock_transactions(feed_id,tx_date,tx_type,quantity_kg,unit_price,notes) VALUES(?,?,'Giriş',?,?,?)""",(feed_id,tx_date,qty,unit_price,'Tarım modülü iç transferinden otomatik stok girişi'));feed_stock_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        else:c.execute("""UPDATE feed_stock_transactions SET feed_id=?,tx_date=?,tx_type='Giriş',quantity_kg=?,unit_price=?,notes=? WHERE id=?""",(feed_id,tx_date,qty,unit_price,'Tarım modülü iç transferinden otomatik stok girişi',feed_stock_id))
        if not feed_price_id or not c.execute('SELECT 1 FROM feed_prices WHERE id=?',(feed_price_id,)).fetchone():
            c.execute("INSERT INTO feed_prices(feed_id,effective_date,price_per_kg,notes) VALUES(?,?,?,'Tarım iç transfer fiyatı')",(feed_id,tx_date,unit_price));feed_price_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        else:c.execute("UPDATE feed_prices SET feed_id=?,effective_date=?,price_per_kg=?,notes='Tarım iç transfer fiyatı' WHERE id=?",(feed_id,tx_date,unit_price,feed_price_id))
        link=c.execute('SELECT id FROM feed_finance_links WHERE finance_id=? OR stock_tx_id=? LIMIT 1',(livestock_finance_id,feed_stock_id)).fetchone()
        if link:c.execute('UPDATE feed_finance_links SET feed_id=?,stock_tx_id=?,finance_id=?,quantity_kg=?,unit_price=? WHERE id=?',(feed_id,feed_stock_id,livestock_finance_id,qty,unit_price,link['id']))
        else:c.execute('INSERT INTO feed_finance_links(feed_id,stock_tx_id,finance_id,quantity_kg,unit_price,created_at) VALUES(?,?,?,?,?,?)',(feed_id,feed_stock_id,livestock_finance_id,qty,unit_price,created))
        if not product_tx_id or not c.execute('SELECT 1 FROM agri_product_transactions WHERE id=?',(product_tx_id,)).fetchone():
            c.execute("""INSERT INTO agri_product_transactions(harvest_lot_id,tx_date,tx_type,quantity_kg,unit_price,source_type,source_id,notes,created_at) VALUES(?,?,'İç Transfer',?,?,'internal_transfer',?,?,?)""",(lot_id,tx_date,qty,unit_price,rid,desc,created));product_tx_id=c.execute('SELECT last_insert_rowid()').fetchone()[0]
        else:c.execute("""UPDATE agri_product_transactions SET harvest_lot_id=?,tx_date=?,tx_type='İç Transfer',quantity_kg=?,unit_price=?,source_type='internal_transfer',source_id=?,notes=? WHERE id=?""",(lot_id,tx_date,qty,unit_price,rid,desc,product_tx_id))
        c.execute("""UPDATE agri_internal_transfers SET harvest_lot_id=?,transfer_date=?,quantity_kg=?,unit_price=?,feed_id=?,agri_finance_id=?,livestock_finance_id=?,feed_stock_tx_id=?,feed_price_id=?,product_stock_tx_id=?,notes=? WHERE id=?""",(lot_id,tx_date,qty,unit_price,feed_id,agri_finance_id,livestock_finance_id,feed_stock_id,feed_price_id,product_tx_id,f.get('notes') or '',rid))
        return '/agriculture/transfers','İç transfer ve bağlı tarım geliri, hayvancılık gideri ile stok hareketleri güncellendi.' if old else 'İç transfer tamamlandı: tarım geliri, hayvancılık yem gideri ve yem stoğu birlikte oluşturuldu.','İç transferi güncelledi' if old else 'Hayvancılığa iç transfer yaptı',desc

    if path=="/agriculture/sale/delete":
        rid=as_int(f,'id');row=c.execute('SELECT * FROM agri_sales WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('Satış kaydı bulunamadı.')
        if row['finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(row['finance_id'],))
        if row['stock_tx_id']:c.execute('DELETE FROM agri_product_transactions WHERE id=?',(row['stock_tx_id'],))
        c.execute('DELETE FROM agri_sales WHERE id=?',(rid,))
        return '/agriculture/transfers','Dış satış ve stok çıkışı geri alındı.','Mahsul satışını geri aldı',str(rid)

    if path=="/agriculture/transfer/delete":
        rid=as_int(f,'id');row=c.execute('SELECT * FROM agri_internal_transfers WHERE id=?',(rid,)).fetchone()
        if not row:raise AgricultureError('İç transfer bulunamadı.')
        stock_row=c.execute('SELECT * FROM feed_stock_transactions WHERE id=?',(row['feed_stock_tx_id'],)).fetchone() if row['feed_stock_tx_id'] else None
        if stock_row and feed_stock_balance(c,stock_row['feed_id'])-float(stock_row['quantity_kg'] or 0) < -0.0001:raise AgricultureError('Bu transferle giren yem stoğu kullanılmış. Önce bağlı yem tüketimlerini düzeltin.')
        if row['agri_finance_id']:c.execute('DELETE FROM agri_finance WHERE id=?',(row['agri_finance_id'],))
        if row['livestock_finance_id']:
            c.execute('DELETE FROM feed_finance_links WHERE finance_id=?',(row['livestock_finance_id'],));c.execute('DELETE FROM finance WHERE id=?',(row['livestock_finance_id'],))
        if row['feed_stock_tx_id']:c.execute('DELETE FROM feed_stock_transactions WHERE id=?',(row['feed_stock_tx_id'],))
        if row['feed_price_id']:c.execute('DELETE FROM feed_prices WHERE id=?',(row['feed_price_id'],))
        if row['product_stock_tx_id']:c.execute('DELETE FROM agri_product_transactions WHERE id=?',(row['product_stock_tx_id'],))
        c.execute('DELETE FROM agri_internal_transfers WHERE id=?',(rid,))
        return '/agriculture/transfers','İç transferin tarım, hayvancılık ve stok hareketleri birlikte geri alındı.','İç transferi geri aldı',str(rid)

    if path=="/agriculture/finance/save":
        rid=as_int(f,'id',0);amount=as_float(f,'amount');tx_type=f.get('tx_type') or 'Gider'
        if amount<=0 or tx_type not in ('Gelir','Gider'):raise AgricultureError('Finans tutarı ve işlem türü geçersiz.')
        field_id=as_int(f,'field_id',0) or None;season_id=as_int(f,'season_id',0) or None
        if season_id:
            season=_field_and_season(c,season_id);field_id=season['field_id']
        values=(f.get('tx_date') or date.today().isoformat(),tx_type,f.get('category') or 'Diğer',amount,f.get('description') or '',f.get('payment_method') or 'Nakit',field_id,season_id)
        if rid:
            row=c.execute("SELECT id FROM agri_finance WHERE id=? AND COALESCE(source_type,'')=''",(rid,)).fetchone()
            if not row:raise AgricultureError('Otomatik veya bulunamayan kayıt buradan düzenlenemez; kaynak işlemden değiştirilmelidir.')
            c.execute('UPDATE agri_finance SET tx_date=?,tx_type=?,category=?,amount=?,description=?,payment_method=?,field_id=?,season_id=? WHERE id=?',(*values,rid))
        else:c.execute("""INSERT INTO agri_finance(tx_date,tx_type,category,amount,description,payment_method,field_id,season_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)""",(*values,created))
        return '/agriculture/finance','Tarım finans kaydı güncellendi.' if rid else 'Tarım finans kaydı oluşturuldu.','Tarım finans kaydını güncelledi' if rid else 'Tarım finans kaydı oluşturdu',f'{tx_type} · {money(amount)}'

    if path=="/agriculture/finance/delete":
        rid=as_int(f,'id');row=c.execute("SELECT * FROM agri_finance WHERE id=? AND COALESCE(source_type,'')=''",(rid,)).fetchone()
        if not row:raise AgricultureError('Otomatik veya bulunamayan kayıt buradan silinemez; kaynak işlemden geri alınmalıdır.')
        c.execute('DELETE FROM agri_finance WHERE id=?',(rid,))
        return '/agriculture/finance','Tarım finans kaydı silindi.','Tarım finans kaydını sildi',str(rid)
    return None
