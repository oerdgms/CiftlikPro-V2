import os, sqlite3, hashlib, secrets, urllib.parse, json, csv, io, shutil, socket, threading, webbrowser, zipfile, tempfile, hmac, time, gc, base64, uuid, smtplib, ssl
from email.parser import BytesParser
from email.message import EmailMessage
from email.policy import default
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http import cookies
from datetime import datetime, date, timedelta
from pathlib import Path
from PIL import Image, ImageOps
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

PROGRAM_DIR=Path(__file__).resolve().parent
DEFAULT_DATA_ROOT=Path(os.environ.get('LOCALAPPDATA') or Path.home())/'CiftlikPro'
DATA_ROOT=Path(os.environ.get('CIFTLIKPRO_DATA_DIR') or DEFAULT_DATA_ROOT)
DATA_ROOT.mkdir(parents=True,exist_ok=True)
DB=DATA_ROOT/'ciftlik.db'
BACKUPS=DATA_ROOT/'backups'
UPLOADS=DATA_ROOT/'uploads'
PORT=8953
SESSIONS={}

APP_NAME='ÇiftlikPro Enterprise'
APP_VERSION='3.9.20'
APP_CHANNEL='DEV'
APP_LABEL='ENTERPRISE V3.9.20 HOTFIX 2 · AKILLI TEDAVİ + TOPLU AŞI'

LICENSE_FILE=DATA_ROOT/'ciftlikpro.license'
LICENSE_PUBLIC_KEY_B64='Z9rGVotpzHR7eNxdVtFX3ztjrxhzhSYBHweob5EYqHE='

def device_id():
    parts=[]
    if os.name=='nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SOFTWARE\Microsoft\Cryptography') as k:
                parts.append(str(winreg.QueryValueEx(k,'MachineGuid')[0]))
        except Exception: pass
    if not parts:
        parts.extend([socket.gethostname(),str(uuid.getnode())])
    digest=hashlib.sha256(('|'.join(parts)+'|CiftlikPro').encode('utf-8')).hexdigest().upper()
    return 'CF-'+digest[:4]+'-'+digest[4:8]+'-'+digest[8:12]+'-'+digest[12:16]

def license_payload_bytes(payload):
    return json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')

def license_doc_to_key(doc):
    import zlib
    raw=json.dumps(doc,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    packed=zlib.compress(raw,9)
    text=base64.b32encode(packed).decode("ascii").rstrip("=")
    return "CFP-"+"-".join(text[i:i+5] for i in range(0,len(text),5))

def _device_id_from_raw(raw8):
    hx=raw8.hex().upper()
    return 'CF-'+hx[0:4]+'-'+hx[4:8]+'-'+hx[8:12]+'-'+hx[12:16]

def _license_date(value):
    if not value:return ''
    return (date(2020,1,1)+timedelta(days=int(value)-1)).isoformat()

def license_key_to_bytes(key):
    import zlib,struct,re
    raw_key=str(key or '').upper().strip()
    if raw_key.startswith('CFS-'):
        clean=re.sub(r'[^A-Z2-7]','',raw_key[4:])
        if not clean:raise ValueError('Lisans anahtarı boş.')
        clean+='='*((8-len(clean)%8)%8)
        blob=base64.b32decode(clean,casefold=True)
        if len(blob)<78 or blob[0]!=1:raise ValueError('Kısa lisans anahtarı biçimi geçersiz.')
        owner_len=blob[13]
        if len(blob)!=(14+owner_len+64):raise ValueError('Kısa lisans anahtarı eksik veya bozuk.')
        issued_days,expires_days=struct.unpack('>HH',blob[9:13])
        payload={
            'product':'CiftlikPro Enterprise',
            'licensee':blob[14:14+owner_len].decode('utf-8'),
            'device_id':_device_id_from_raw(blob[1:9]),
            'license_type':'Süresiz' if not expires_days else 'Süreli',
            'issued_on':_license_date(issued_days),
            'expires_on':_license_date(expires_days),
        }
        doc={'payload':payload,'signature':base64.b64encode(blob[14+owner_len:]).decode('ascii')}
        return json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    clean=raw_key
    if clean.startswith('CFP-'):clean=clean[4:]
    clean=re.sub(r'[^A-Z2-7]','',clean)
    if not clean:raise ValueError('Lisans anahtarı boş.')
    clean+='='*((8-len(clean)%8)%8)
    return zlib.decompress(base64.b32decode(clean,casefold=True))

def validate_license_bytes(raw=None):
    try:
        if raw is None:
            if not LICENSE_FILE.exists(): return False,None,'Lisans dosyası bulunamadı.'
            raw=LICENSE_FILE.read_bytes()
        doc=json.loads(raw.decode('utf-8'))
        payload=doc.get('payload') or {}
        signature=base64.b64decode(doc.get('signature',''),validate=True)
        Ed25519PublicKey.from_public_bytes(base64.b64decode(LICENSE_PUBLIC_KEY_B64)).verify(signature,license_payload_bytes(payload))
        if payload.get('product')!='CiftlikPro Enterprise': return False,payload,'Bu lisans farklı bir ürün için.'
        if str(payload.get('device_id','')).upper()!=device_id().upper(): return False,payload,'Lisans bu bilgisayara ait değil.'
        expires=str(payload.get('expires_on') or '').strip()
        if expires and date.today()>date.fromisoformat(expires): return False,payload,'Lisans süresi dolmuş.'
        return True,payload,'Aktif'
    except InvalidSignature:return False,None,'Lisans imzası geçersiz.'
    except Exception as exc:return False,None,'Lisans doğrulanamadı: '+str(exc)

def license_status():
    return validate_license_bytes()


CSS='''
:root{--g:#176b3a;--g2:#228b4f;--bg:#f3f6f4;--card:#fff;--txt:#203127;--mut:#6b7b70;--red:#c8392b;--orange:#e58c16;--blue:#2e6fc2}
*{box-sizing:border-box}body{margin:0;font-family:Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--txt)}
a{text-decoration:none;color:inherit}.top{height:64px;background:linear-gradient(90deg,var(--g),var(--g2));color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 20px;position:fixed;top:0;left:0;right:0;z-index:30}.brand{font-weight:800;font-size:20px}.ver{font-size:12px;background:#ffffff2b;padding:6px 10px;border-radius:20px}.layout{display:block;min-height:100vh;padding-top:64px}.side{position:fixed;top:64px;left:0;bottom:0;width:220px;background:#153d28;color:#e9fff1;padding:18px 12px;overflow-y:auto;z-index:20}.side a{display:block;padding:12px;border-radius:10px;margin:5px 0}.side a:hover,.side a.on{background:#ffffff18}.main{margin-left:220px;padding:22px;min-height:calc(100vh - 64px)}.grid{display:grid;grid-template-columns:repeat(4,minmax(170px,1fr));gap:14px}.card{background:var(--card);border-radius:16px;padding:18px;box-shadow:0 4px 18px #14271b12}.stat b{font-size:27px;display:block;margin-top:8px}.mut{color:var(--mut)}.actions{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}.btn{display:inline-block;border:0;border-radius:10px;padding:10px 14px;cursor:pointer;background:var(--g);color:#fff;font-weight:700}.btn.alt{background:#eef4ef;color:var(--g)}.btn.red{background:var(--red)}.btn.blue{background:var(--blue)}.btn.orange{background:var(--orange)}.inline-form{display:inline}.costbox{background:#f7fbf8;border:1px solid #d8e7dc;border-radius:14px;padding:14px;margin-top:12px}
table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden}th,td{padding:11px;border-bottom:1px solid #e7ece8;text-align:left;font-size:14px}th{background:#edf5ef}.form{display:grid;grid-template-columns:repeat(2,minmax(180px,1fr));gap:12px}.form label{font-size:13px;font-weight:700}.form input,.form select,.form textarea{width:100%;padding:10px;border:1px solid #cfd9d1;border-radius:9px;margin-top:5px}.full{grid-column:1/-1}.flash{padding:12px;border-radius:10px;background:#e8f7ec;color:#175f34;margin-bottom:14px}.err{background:#fdebea;color:#a52d25}.login{max-width:420px;margin:9vh auto;background:#fff;padding:28px;border-radius:18px;box-shadow:0 10px 35px #1a3b2720}.login h1{margin-top:0}.login input{width:100%;padding:12px;margin:7px 0 14px;border:1px solid #ccd7cf;border-radius:10px}.chart{display:flex;align-items:end;gap:8px;height:190px;padding-top:16px}.bar{flex:1;background:linear-gradient(#2c9660,#176b3a);border-radius:8px 8px 0 0;min-width:18px;position:relative}.bar span{position:absolute;bottom:-24px;font-size:11px;width:100%;text-align:center}.bar i{position:absolute;top:-20px;font-style:normal;font-size:10px;width:100%;text-align:center}.two{display:grid;grid-template-columns:1.2fr .8fr;gap:14px}.taglink{font-weight:800;color:var(--g);text-decoration:underline}.profile{display:grid;grid-template-columns:180px 1fr;gap:18px}.photo{width:180px;height:180px;border-radius:16px;object-fit:cover;background:#e8efe9;display:flex;align-items:center;justify-content:center;font-size:54px}.pill{display:inline-block;padding:6px 10px;border-radius:20px;background:#eaf4ed;margin:3px;font-size:13px}.preg{font-weight:800}.preg.pos{color:var(--g)}.preg.neg{color:var(--red)}.hero{background:linear-gradient(135deg,#123f29,#238a50);color:white;border-radius:20px;padding:24px;margin-bottom:16px;display:flex;justify-content:space-between;gap:16px;align-items:center}.hero h1{margin:0 0 6px}.metric{border-left:5px solid var(--g)}.metric.red{border-left-color:var(--red)}.metric.blue{border-left-color:var(--blue)}.metric.orange{border-left-color:var(--orange)}.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}.gallery figure{margin:0;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 3px 14px #0001}.gallery img{width:100%;height:150px;object-fit:cover;display:block}.gallery figcaption{padding:8px;font-size:12px}.alertlist{display:grid;gap:8px}.alertitem{padding:10px;border-radius:10px;background:#f3f7f4;border-left:4px solid var(--g)}.mini-chart{display:flex;align-items:end;gap:10px;height:180px;padding:20px 5px 28px}.mini-col{flex:1;display:flex;gap:3px;align-items:end;height:100%;position:relative}.mini-col b{flex:1;border-radius:6px 6px 0 0;background:#2c9660;min-height:2px}.mini-col i{flex:1;border-radius:6px 6px 0 0;background:#d95b4e;min-height:2px}.mini-col span{position:absolute;bottom:-22px;width:100%;text-align:center;font-size:11px}.uploadbox{border:2px dashed #b8c9bd;border-radius:14px;padding:14px;background:#f9fbf9}.camera-note{font-size:12px;color:var(--mut)}.photo-upload-status{display:none;margin-top:8px;padding:10px;border-radius:10px;background:#eef5ef;font-size:12px}.photo-upload-status.on{display:block}.photo-upload-status.error{background:#fdebea;color:#a52d25}.upload-progress{height:9px;background:#dbe6dd;border-radius:99px;overflow:hidden;margin-top:7px}.upload-progress-bar{height:100%;width:0;background:linear-gradient(90deg,var(--g2),var(--blue));transition:width .15s ease}.btn[disabled]{opacity:.62;cursor:not-allowed}
.side .nav-home{font-weight:800}.nav-group{margin:5px 0}.nav-group summary{list-style:none;cursor:pointer;padding:12px;border-radius:10px;font-weight:800;display:flex;align-items:center;justify-content:space-between;user-select:none}.nav-group summary::-webkit-details-marker{display:none}.nav-group summary:hover,.nav-group.open-group summary{background:#ffffff10}.nav-group summary:after{content:"›";font-size:20px;transition:transform .18s ease}.nav-group[open] summary:after{transform:rotate(90deg)}.nav-children{padding:2px 0 4px 10px;border-left:1px solid #ffffff22;margin-left:13px}.side .nav-children a{padding:9px 11px;margin:2px 0;font-size:13px}.menu-toggle{display:none;border:0;background:#ffffff22;color:#fff;border-radius:9px;padding:8px 11px;font-size:20px;cursor:pointer}.top-left{display:flex;align-items:center;gap:10px}

.estrus-decision-badge{display:inline-block;padding:8px 11px;border-radius:12px;font-weight:800;margin:0 7px 7px 0;line-height:1.25}
.estrus-decision-badge small{font-weight:600;opacity:.8}
.estrus-skipped{background:#f1ecff;color:#6542a6}
.estrus-done{background:#e7f6eb;color:#176b3a}


.sortable-insem th{white-space:nowrap}
.sort-head{appearance:none;border:0;background:transparent;color:inherit;font:inherit;font-weight:800;padding:8px 4px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.sort-head span{color:#718278;font-size:13px}
.sort-head:hover{color:#08783e}
.sort-head.active{color:#08783e}
.sort-head.active span{color:#08783e}

.license-shell{max-width:760px;margin:55px auto;padding:18px}.license-card{background:#fff;border-radius:22px;padding:28px;box-shadow:0 12px 38px #183c2820;border:1px solid #dfe9e2}
.device-code{font-family:Consolas,monospace;font-size:20px;font-weight:800;letter-spacing:1px;background:#eef6f0;padding:14px;border-radius:12px;word-break:break-all}
.license-ok{display:inline-block;background:#e7f6eb;color:#176b3a;padding:7px 11px;border-radius:999px;font-weight:800}.license-bad{display:inline-block;background:#fff0ee;color:#a92f24;padding:7px 11px;border-radius:999px;font-weight:800}

@media(max-width:760px){.sort-head{padding:6px 2px;font-size:12px;white-space:normal;text-align:left}.sort-head span{font-size:11px}}

@media(max-width:650px){.profile{grid-template-columns:1fr}.photo{width:100%;height:220px}}
/* V3.7.6 Besi Kârlılık */
.perf-hero{background:linear-gradient(135deg,#173f2b,#245f3e);color:#fff;border-radius:24px;padding:24px 26px;display:flex;align-items:center;justify-content:space-between;gap:18px;box-shadow:0 14px 34px rgba(22,72,45,.16)}
.perf-hero h1{margin:0 0 6px;font-size:28px}.perf-hero p{margin:0;color:#dcece2}.perf-hero .btn{background:#fff;color:#18492f}
.perf-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}.perf-tab{display:inline-flex;padding:10px 15px;border-radius:999px;background:#edf4ef;color:#355747;font-weight:800;text-decoration:none;border:1px solid #dce8df}.perf-tab.active{background:#1f6b42;color:#fff;border-color:#1f6b42}
/* V3.9.15 unified ration workspace */
.target-workspace{margin-top:10px}.target-controlbar{display:flex;align-items:flex-end;gap:10px;justify-content:space-between;flex-wrap:wrap;padding:8px 10px;background:#fff;border:1px solid #dce8df;border-radius:12px}.target-controlbar .target-head{min-width:190px}.target-controlbar .target-head h3{margin:0;font-size:16px}.target-controlbar .target-context{margin-top:2px;font-size:12px}.target-controlbar .target-form{display:flex;align-items:flex-end;gap:7px;flex:1;justify-content:flex-end;flex-wrap:wrap}.target-controlbar .target-form label{font-size:11px;min-width:110px}.target-controlbar .target-form input,.target-controlbar .target-form select{padding:6px 8px;min-height:34px}.target-compare-sticky{position:sticky;top:8px;z-index:18;margin-top:8px;padding:7px 8px;background:rgba(248,251,249,.97);backdrop-filter:blur(7px);border:1px solid #bcd8c5;border-radius:12px;box-shadow:0 5px 18px rgba(28,76,49,.08)}.target-compare-title{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 2px 5px;font-size:12px}.target-compare-title span{color:#617269}.nutri-mini-grid{grid-template-columns:repeat(8,minmax(92px,1fr))!important;gap:5px!important}.nutri-mini{padding:6px 7px!important;min-height:64px!important}.nutri-mini span{font-size:10px!important}.nutri-mini b{font-size:16px!important;margin-top:1px!important}.nutri-mini small,.nutri-mini i,.nutri-mini em{font-size:9.5px!important;line-height:1.15!important}.compact-changebar{margin:4px 0 6px!important;padding:0 2px}.ration-workbench-table th,.ration-workbench-table td{padding:6px 7px!important}.ration-workbench-table{font-size:12px}.ration-workbench-table tbody tr:nth-child(even){background:#f4f8f5}.ration-workbench-table tbody tr:nth-child(odd){background:#fff}.ration-workbench-table tbody tr:hover{background:#eaf5ee}.quick-feed-card:not([open]){display:none}.quick-feed-card[open]{display:block;position:fixed;z-index:80;left:max(12px,calc(50% - 430px));right:max(12px,calc(50% - 430px));top:8vh;max-height:84vh;overflow:auto;margin:0!important;box-shadow:0 24px 70px rgba(0,0,0,.28);border:1px solid #b9d7c3!important}.quick-feed-card[open]::before{content:'';position:fixed;inset:0;background:rgba(17,35,25,.38);z-index:-1}.quick-feed-head{position:sticky;top:0;background:#fff;z-index:2;padding:4px 0}.ration-savebar{padding:7px!important}.ration-picker-grid{gap:8px!important}.ration-picker-card{min-height:88px!important;padding:10px 12px!important}
@media(max-width:1100px){.nutri-mini-grid{grid-template-columns:repeat(4,minmax(100px,1fr))!important}.target-compare-sticky{top:4px}.target-controlbar{align-items:stretch}.target-controlbar .target-form{justify-content:flex-start}}
@media(max-width:650px){.nutri-mini-grid{grid-template-columns:repeat(2,minmax(110px,1fr))!important}.target-compare-title span{display:none}.target-controlbar .target-form label{min-width:calc(50% - 6px);flex:1}.target-compare-sticky{padding:6px}.nutri-mini{min-height:58px!important}.quick-feed-card[open]{left:8px;right:8px;top:4vh;max-height:92vh}}
.ration-stepper{display:flex;align-items:center;gap:6px;white-space:nowrap}.ration-qty{width:92px;padding:8px;border:1px solid #bfd0c4;border-radius:9px;text-align:center;font-weight:800}.ration-savebar{position:sticky;bottom:8px;background:#fffffff2;padding:10px;text-align:right;border-top:1px solid #e1ebe4;z-index:9}#ration-workbench{scroll-margin-top:82px}.ration-section-collapse details>summary{cursor:pointer;font-weight:800}.ration-live{position:sticky;top:42px;z-index:7;background:#f8fbf9;border:1px solid #cfe3d5;border-radius:12px;padding:10px;margin:10px 0}.ration-live-grid{display:grid;grid-template-columns:repeat(7,minmax(100px,1fr));gap:8px}.ration-live-metric{background:#fff;border:1px solid #e0e8e2;border-radius:9px;padding:8px}.ration-live-metric span{display:block;color:#607067;font-size:12px}.ration-live-metric b{display:block;margin-top:3px}.ration-live-metric small{display:block;margin-top:2px}.ration-dirty{outline:2px solid #f0a126;background:#fff9ec}.ration-changebar{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:8px}.ration-dirty-text{font-weight:800;color:#9a5b00}@media(max-width:1000px){.ration-live-grid{grid-template-columns:repeat(2,minmax(120px,1fr))}.ration-live{position:static}}
.perf-filter-card{border:1px solid #dce8df;background:linear-gradient(180deg,#fff,#f8fbf9)}.perf-filter-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}.perf-filter-head h2{margin:0}
.perf-filter-grid{display:grid;grid-template-columns:1.2fr repeat(3,1fr);gap:10px;align-items:end}.perf-filter-grid label{display:flex;flex-direction:column;gap:5px;font-weight:800;font-size:13px}.perf-filter-actions{display:flex;gap:8px}
.perf-summary{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-top:14px}.perf-summary small{display:block;margin-top:7px;color:#6d8075}.perf-table-wrap{overflow:auto;border:1px solid #e1e9e4;border-radius:16px}.performance-table{min-width:1450px;margin:0}.performance-table th{position:sticky;top:0;background:#edf5ef;z-index:1;white-space:nowrap}.performance-table td{white-space:nowrap}.performance-table tbody tr:hover{background:#f7fbf8}
.profit-pill{display:inline-flex;padding:6px 10px;border-radius:999px;font-weight:900}.profit-pill.good{background:#e5f6eb;color:#14723d}.profit-pill.bad{background:#fff0ed;color:#b33a2e}.profit-pill.wait{background:#eef2f0;color:#65756d}
@media(max-width:1100px){.perf-filter-grid{grid-template-columns:repeat(2,1fr)}.perf-summary{grid-template-columns:repeat(2,1fr)}}@media(max-width:650px){.perf-hero{padding:19px;align-items:flex-start;flex-direction:column}.perf-filter-grid{grid-template-columns:1fr}.perf-summary{grid-template-columns:1fr 1fr}.perf-summary .card:last-child{grid-column:1/-1}.perf-tabs{overflow-x:auto;flex-wrap:nowrap}.perf-tab{white-space:nowrap}}
@media(max-width:900px){.menu-toggle{display:inline-block}.side{transform:translateX(-105%);transition:transform .2s ease;width:260px;box-shadow:8px 0 24px #0003}.side.mobile-open{transform:translateX(0)}.main{margin-left:0;padding-top:18px}.grid{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}}@media(max-width:560px){.grid,.form{grid-template-columns:1fr}.main{padding:12px}.top{padding:0 12px}.brand{font-size:17px}}




.finance-toolbar{display:flex;gap:10px;align-items:end;flex-wrap:wrap}
.finance-toolbar label{display:flex;flex-direction:column;gap:5px;font-weight:700}
.finance-table-wrap{overflow-x:auto;border-radius:14px}
.finance-table{width:100%;border-collapse:collapse;min-width:900px}
.finance-table th{white-space:nowrap;background:#edf5ef}
.finance-table td{vertical-align:middle}
.finance-table .finance-actions{display:flex;gap:6px;align-items:center;white-space:nowrap}
.finance-table .finance-actions form{margin:0}
.finance-table .btn{padding:8px 12px}
.dashboard-editbar{display:flex;justify-content:flex-end;gap:10px;margin:10px 0 14px}
.dashboard-slot{position:relative;min-width:0}
.dashboard-slot.editing{padding-top:0}
.dashboard-slot.editing>.summary-link{outline:2px dashed #83ad90;outline-offset:3px}
.dashboard-slot-plus{position:absolute;right:-7px;top:-9px;z-index:4;width:34px;height:34px;border-radius:50%;border:3px solid #fff;background:#167a43;color:#fff;font-size:23px;line-height:27px;font-weight:900;cursor:pointer;box-shadow:0 4px 12px #173b2828;display:flex;align-items:center;justify-content:center}
.dashboard-slot-plus:hover{transform:scale(1.08);background:#0f6838}
.dashboard-empty-slot{min-height:145px;border:2px dashed #91b59c;border-radius:18px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#f8fcf9,#edf7f0);color:#176b3a;cursor:pointer;transition:.18s}
.dashboard-empty-slot:hover{border-color:#176b3a;background:#eaf7ee;transform:translateY(-2px)}
.dashboard-empty-slot .plus-icon{width:52px;height:52px;border-radius:50%;background:#176b3a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:35px;margin:0 auto 8px;box-shadow:0 7px 18px #176b3a2c}
.dashboard-empty-slot small{display:block;font-size:14px;color:#607869;font-weight:700;text-align:center}
.dashboard-picker-backdrop{display:none;position:fixed;inset:0;background:#10271b8c;z-index:100;align-items:center;justify-content:center;padding:18px;backdrop-filter:blur(3px)}
.dashboard-picker-backdrop.open{display:flex}
.dashboard-picker{width:min(760px,96vw);max-height:88vh;overflow:auto;background:#fff;border-radius:24px;padding:22px;box-shadow:0 25px 80px #07150d55}
.dashboard-picker-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;margin-bottom:16px}
.dashboard-picker-head h2{margin:0;color:#173c29}.dashboard-picker-head p{margin:4px 0 0;color:#718276}
.dashboard-picker-close{border:0;background:#edf4ef;width:42px;height:42px;border-radius:50%;font-size:22px;cursor:pointer}
.dashboard-card-gallery{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:11px}
.dashboard-card-choice{display:flex;align-items:center;gap:12px;text-align:left;border:2px solid #e0eae3;background:#fbfdfb;border-radius:16px;padding:14px;cursor:pointer;font:inherit;color:#183a29}
.dashboard-card-choice:hover,.dashboard-card-choice.active{border-color:#248952;background:#eaf7ee;transform:translateY(-1px)}
.dashboard-card-choice .choice-icon{width:44px;height:44px;border-radius:13px;background:#edf6ef;display:flex;align-items:center;justify-content:center;font-size:24px}
.dashboard-card-choice b{display:block}.dashboard-card-choice small{color:#6f8174}
.dashboard-picker-footer{display:flex;gap:9px;justify-content:space-between;align-items:center;margin-top:16px;flex-wrap:wrap}
@media(max-width:600px){.dashboard-card-gallery{grid-template-columns:1fr}.dashboard-picker{padding:16px;border-radius:18px}.dashboard-slot-plus{right:-3px;top:-6px}}
@media(max-width:700px){
 .finance-toolbar{align-items:stretch}.finance-toolbar>*{width:100%}.finance-toolbar input,.finance-toolbar select,.finance-toolbar .btn{width:100%}
 .finance-table{min-width:760px}
}

.bulk-animal-box{display:none}
.bulk-picker{border:1px solid #d8e5dc;border-radius:16px;background:#fbfdfb;padding:14px}
.bulk-picker-head{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:10px}
.bulk-search{max-width:420px;width:100%}
.bulk-list{max-height:300px;overflow:auto;border:1px solid #dfe9e2;border-radius:12px;background:white}
.bulk-row{display:grid;grid-template-columns:34px minmax(130px,1fr) minmax(110px,1fr);gap:10px;align-items:center;padding:10px 12px;border-bottom:1px solid #edf2ee;cursor:pointer}
.bulk-row:last-child{border-bottom:0}.bulk-row:hover{background:#f5faf6}.bulk-row.selected{background:#eaf7ee}
.bulk-row input{width:20px;height:20px}.bulk-row .tag{font-weight:800;color:#176b3a}.bulk-row .nick{color:#6d8074;font-size:13px}
.bulk-summary{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:12px}
.bulk-summary .pill{background:#edf6ef;padding:9px 12px;border-radius:999px}
.bulk-selected-preview{font-size:13px;color:#5f7466;margin-top:8px}
.finance-savebar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.finance-savebar .btn{min-width:180px}

.farm-profile-head{display:flex;gap:18px;align-items:center;flex-wrap:wrap}
.farm-logo-preview{width:120px;height:120px;border-radius:18px;object-fit:contain;background:#f4f7f5;border:1px solid #dbe5de;padding:8px}
.farm-logo-placeholder{width:120px;height:120px;border-radius:18px;background:#eaf4ed;display:flex;align-items:center;justify-content:center;font-size:50px}
.farm-hero{display:flex;align-items:center;gap:16px}.farm-hero-logo{width:76px;height:76px;border-radius:16px;object-fit:contain;background:#ffffff18;padding:5px}
@media(max-width:560px){.farm-hero{align-items:flex-start}.farm-hero-logo{width:58px;height:58px}}

.pro-form-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.type-chip{padding:7px 11px;border-radius:999px;background:#eaf4ed;color:var(--g);font-weight:800}
.livebox{display:flex;gap:8px;align-items:center;margin:12px 0}
.livebox input{flex:1;max-width:540px;padding:11px;border:1px solid #cfd9d1;border-radius:10px}
.empty-state{display:none;padding:16px;text-align:center;color:var(--mut)}
.quick-metrics{display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;margin-top:12px}
.quick-metrics .pill{display:block;text-align:center;padding:12px}
@media(max-width:700px){.quick-metrics{grid-template-columns:repeat(2,1fr)}}

.summary-link{display:block;transition:transform .15s ease,box-shadow .15s ease}.summary-link:hover{transform:translateY(-2px);box-shadow:0 8px 24px #14271b20}.summary-link:focus{outline:2px solid var(--g2);outline-offset:2px}.summary-grid{grid-template-columns:repeat(6,minmax(145px,1fr))}.summary-grid .card{padding:15px}.summary-grid .stat b{font-size:24px}.summary-grid .metric-icon{font-size:21px;margin-bottom:6px}@media(max-width:1250px){.summary-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:700px){.summary-grid{grid-template-columns:repeat(2,1fr)}}
.metric-icon{font-size:24px;display:block;margin-bottom:8px}.metric small{display:block;margin-top:5px;color:var(--mut);font-size:12px;font-weight:600}.metric.green{border-left-color:#2c9660}.metric.purple{border-left-color:#7b5cc7}.metric.teal{border-left-color:#178c91}.cost-visual{display:grid;grid-template-columns:.9fr 1.1fr;gap:18px;align-items:center}.donut{width:190px;height:190px;border-radius:50%;margin:auto;position:relative;background:conic-gradient(var(--blue) 0 var(--purchase-pct),var(--orange) var(--purchase-pct) 100%)}.donut:after{content:"";position:absolute;inset:31px;background:var(--card);border-radius:50%}.donut-center{position:absolute;inset:0;display:flex;z-index:2;align-items:center;justify-content:center;flex-direction:column;text-align:center}.donut-center b{font-size:20px}.legend-row{display:grid;grid-template-columns:14px 1fr auto;gap:8px;align-items:center;margin:11px 0}.legend-dot{width:12px;height:12px;border-radius:4px}.dot-blue{background:var(--blue)}.dot-orange{background:var(--orange)}.progress-list{display:grid;gap:12px}.progress-item{display:grid;gap:5px}.progress-head{display:flex;justify-content:space-between;gap:10px;font-size:13px}.progress-track{height:11px;background:#e8eee9;border-radius:99px;overflow:hidden}.progress-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--g2),var(--blue))}.health-group{border:1px solid #dfe9e2;border-radius:14px;margin:10px 0;background:#fbfdfb;overflow:hidden}.health-group summary{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:14px 16px;cursor:pointer;list-style:none}.health-group summary::-webkit-details-marker{display:none}.health-group[open] summary{background:#eef7f0;border-bottom:1px solid #dfe9e2}.dash-fold{margin-top:14px}.dash-fold>summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:15px 18px;background:#fff;border:1px solid #e0e9e2;border-radius:15px;font-size:18px;font-weight:900;color:#183c2a;box-shadow:0 3px 12px #173b2810}.dash-fold>summary::-webkit-details-marker{display:none}.dash-fold[open]>summary{border-radius:15px 15px 0 0}.dash-fold-content{padding:14px;background:#f8fbf9;border:1px solid #e0e9e2;border-top:0;border-radius:0 0 15px 15px}.dashboard-section-title{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:22px 0 10px}.dashboard-section-title h2{margin:0}.dashboard-section-title span{color:var(--mut);font-size:13px}@media(max-width:760px){.cost-visual{grid-template-columns:1fr}.donut{width:165px;height:165px}}

.performance-card{border-left:5px solid var(--blue)}.status-good{color:#176b3a;background:#e8f7ec}.status-watch{color:#8a5a00;background:#fff4d6}.status-low{color:#a52d25;background:#fdebea}.status-none{color:var(--mut);background:#f0f3f1}.perf-badge{display:inline-block;padding:6px 10px;border-radius:999px;font-weight:800;font-size:12px}.weight-chart{width:100%;height:240px;border-radius:14px;background:linear-gradient(180deg,#f7fbf8,#fff);border:1px solid #e0e9e2}.weight-chart text{font-family:Segoe UI,Arial,sans-serif;font-size:11px;fill:#6b7b70}.weight-chart .axis{stroke:#bccac0;stroke-width:1}.weight-chart .gridline{stroke:#e2e9e4;stroke-width:1}.weight-chart .trend{fill:none;stroke:var(--blue);stroke-width:4;stroke-linecap:round;stroke-linejoin:round}.weight-chart .point{fill:var(--g);stroke:#fff;stroke-width:3}.warning-panel{border-left:5px solid var(--red);background:#fff7f6}.performance-table tr.low-row td{background:#fff3f2}.performance-table tr.watch-row td{background:#fff9e8}.performance-table tr.good-row td{background:#f2fbf5}.setting-box{background:#f7fbf8;border:1px solid #d8e7dc;border-radius:14px;padding:16px}
.insem-head{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap}.insem-head h1{margin-bottom:4px}.insem-search{display:flex;gap:8px;align-items:center;min-width:min(100%,460px)}.insem-search input{flex:1;padding:11px;border:1px solid #cfd9d1;border-radius:10px}.insem-stats{grid-template-columns:repeat(4,minmax(150px,1fr));margin:14px 0}.insem-table details summary{cursor:pointer;color:var(--g);font-weight:800}.insem-history{margin:10px 0 2px;background:#f8fbf9;border-radius:10px}.status-badge{display:inline-block;padding:5px 9px;border-radius:999px;font-weight:800;font-size:12px}.status-preg{background:#e8f7ec;color:#176b3a}.status-wait{background:#eaf2ff;color:#2e6fc2}.status-neg{background:#fdebea;color:#a52d25}.status-unknown{background:#fff4d6;color:#8a5a00}.animal-picker-note{font-size:12px;color:var(--mut);margin-top:5px}.attempt-preview{display:flex;align-items:center;min-height:42px;padding:10px;border:1px solid #cfd9d1;border-radius:9px;margin-top:5px;background:#f7fbf8;font-weight:800}.future-warning{font-size:12px;color:var(--red);display:none;margin-top:5px}.row-actions{display:flex;gap:6px;flex-wrap:wrap}.compact-btn{padding:7px 10px;font-size:12px}.insem-empty{display:none;padding:18px;text-align:center;color:var(--mut)}.animal-picker{position:relative}.animal-suggestions{display:none;position:absolute;left:0;right:0;top:100%;z-index:60;background:#fff;border:1px solid #cfd9d1;border-radius:10px;box-shadow:0 10px 26px #14271b24;max-height:260px;overflow-y:auto;margin-top:4px}.animal-suggestions.open{display:block}.animal-suggestion{display:block;width:100%;border:0;background:#fff;text-align:left;padding:11px 12px;cursor:pointer;border-bottom:1px solid #edf1ee;color:var(--txt)}.animal-suggestion:last-child{border-bottom:0}.animal-suggestion:hover,.animal-suggestion:focus{background:#edf7f0;outline:none}.animal-suggestion b{display:block;color:var(--g)}.animal-suggestion span{font-size:12px;color:var(--mut)}
@media(max-width:800px){.insem-stats{grid-template-columns:repeat(2,1fr)}.insem-search{min-width:100%}.insem-head{align-items:stretch}.insem-search .btn{flex:0 0 auto}}
@media(max-width:560px){.top-user{font-size:12px;max-width:46vw;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ver{display:none}.card{padding:14px;border-radius:13px}.btn{min-height:44px;padding:11px 13px}.form input,.form select,.form textarea,.livebox input,.insem-search input{min-height:44px;font-size:16px}.insem-stats{grid-template-columns:1fr 1fr;gap:8px}.insem-stats .card{padding:12px}.insem-stats .stat b{font-size:22px}.insem-head h1{font-size:25px}.insem-search{flex-direction:column;align-items:stretch}.insem-search .btn{width:100%}.animal-suggestions{max-height:220px}.row-actions .btn{width:100%;text-align:center}.row-actions .inline-form{width:100%}.row-actions .inline-form .btn{width:100%}table{min-width:620px}.insem-table{min-width:680px}.insem-history{min-width:650px}.card{overflow-x:auto}.animal-picker{overflow:visible}.login{margin:4vh 12px;padding:20px}.actions>input,.actions>select,.actions>label{max-width:100%}.actions{align-items:stretch}.actions .btn{flex:1 1 auto}}


/* V3.1.9 — gerçek mobil arayüz */
.business-summary-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
.mobile-animal-table .inline-form{display:inline-block}
@media(max-width:700px){
  .top{height:58px;padding:0 12px}.layout{padding-top:58px}.side{top:58px}.main{padding:14px 12px 24px}
  .top-left{gap:8px}.menu-toggle{font-size:22px;padding:9px 12px;border-radius:12px}.brand{font-size:22px}.top-user{font-size:13px;max-width:42vw}
  h1{font-size:30px;line-height:1.08;margin:16px 0 18px}h2{font-size:21px}.card{padding:14px;border-radius:18px}
  .livebox{gap:8px;margin:8px 0 14px}.livebox input{max-width:none;width:100%;min-width:0;height:46px;font-size:16px;padding:10px 42px 10px 13px}.live-clear{padding:10px 12px;min-height:46px}
  .business-summary-grid{grid-template-columns:1fr 1fr!important;gap:10px}.business-summary-grid .card{min-width:0;padding:13px}.business-summary-grid .card:last-child{grid-column:1/-1}.business-summary-grid .stat{font-size:13px}.business-summary-grid .stat b{font-size:23px;line-height:1.08;overflow-wrap:anywhere}
  .summary-grid{grid-template-columns:1fr 1fr;gap:10px}.summary-grid .card{padding:12px}.summary-grid .stat b{font-size:22px}
  .actions{gap:8px}.actions .btn{flex:1 1 auto;text-align:center}
  .card:has(> .mobile-animal-table){padding:8px;background:transparent;box-shadow:none;overflow:visible}
  .mobile-animal-table,.mobile-animal-table tbody,.mobile-animal-table tr,.mobile-animal-table td{display:block;width:100%!important;min-width:0!important}
  .mobile-animal-table{background:transparent;min-width:0!important}.mobile-animal-table thead{display:none}
  .mobile-animal-table tr.data-row{background:#fff;border:1px solid #e2ebe5;border-radius:16px;margin:0 0 10px;padding:14px;box-shadow:0 3px 13px #14271b0d}
  .mobile-animal-table tr.data-row td{border:0;padding:4px 0;font-size:14px;display:grid;grid-template-columns:104px 1fr;gap:10px;align-items:center}
  .mobile-animal-table tr.data-row td:before{font-size:12px;font-weight:800;color:var(--mut)}
  .mobile-animal-table .taglink{font-size:18px}.mobile-animal-table .btn{min-height:40px;padding:9px 11px;font-size:13px}
  .mobile-animal-table tr.data-row td:last-child{display:flex;gap:7px;flex-wrap:wrap;padding-top:10px;margin-top:6px;border-top:1px solid #edf1ee}
  .mobile-animal-table tr.data-row td:last-child:before{display:none}.mobile-animal-table tr.data-row td:last-child .btn{flex:1 1 auto;text-align:center}.mobile-animal-table tr.data-row td:last-child .inline-form{flex:0 0 auto}.mobile-animal-table tr.data-row td:last-child .inline-form .btn{width:auto}
  .all-animal-table td:nth-child(1):before{content:'Küpe'}.all-animal-table td:nth-child(2):before{content:'Takma Ad'}.all-animal-table td:nth-child(3):before{content:'Tür'}.all-animal-table td:nth-child(4):before{content:'Irk'}.all-animal-table td:nth-child(5):before{content:'Padok'}.all-animal-table td:nth-child(6):before{content:'Yaş'}
    .female-table td:nth-child(1):before{content:'Küpe'}.female-table td:nth-child(2):before{content:'Takma Ad'}.female-table td:nth-child(3):before{content:'Cinsiyet'}.female-table td:nth-child(4):before{content:'Irk'}.female-table td:nth-child(5):before{content:'Padok'}.female-table td:nth-child(6):before{content:'Yaş'}
  .male-table td:nth-child(1):before{content:'Küpe'}.male-table td:nth-child(2):before{content:'Takma Ad'}.male-table td:nth-child(3):before{content:'Irk'}.male-table td:nth-child(4):before{content:'Padok'}.male-table td:nth-child(5):before{content:'Bizde Kalma'}.male-table td:nth-child(6):before{content:'Alış'}.male-table td:nth-child(7):before{content:'Anlık Maliyet'}.male-table td:nth-child(8):before{content:'Hedef Kâr'}
  .calf-table td:nth-child(1):before{content:'Küpe'}.calf-table td:nth-child(2):before{content:'Anne'}.calf-table td:nth-child(3):before{content:'Baba'}.calf-table td:nth-child(4):before{content:'Doğum'}.calf-table td:nth-child(5):before{content:'Yaş'}.calf-table td:nth-child(6):before{content:'Cinsiyet'}
  .insem-head{gap:12px}.insem-head h1{font-size:28px}.insem-search{width:100%;flex-direction:row}.insem-search input{min-width:0;width:100%}.insem-search .live-clear{width:auto!important;flex:0 0 auto}
  .insem-stats{grid-template-columns:1fr 1fr!important;gap:9px}.insem-stats .card{min-width:0;padding:12px}.insem-stats .stat{font-size:13px}.insem-stats .stat b{font-size:22px}.insem-stats small{font-size:11px}
  .insem-table,.insem-table tbody,.insem-table tr.data-row,.insem-table tr.data-row>td{display:block;width:100%;min-width:0!important}.insem-table{background:transparent}.insem-table>thead{display:none}
  .insem-table tr.data-row{background:#fff;border:1px solid #e1ebe4;border-radius:16px;margin-bottom:10px;padding:14px;box-shadow:0 3px 13px #14271b0d}
  .insem-table tr.data-row>td{border:0;padding:5px 0;display:grid;grid-template-columns:112px 1fr;gap:9px;align-items:center}
  .insem-table tr.data-row>td:before{font-size:12px;font-weight:800;color:var(--mut)}
  .insem-table tr.data-row>td:nth-child(1):before{content:'Hayvan'}.insem-table tr.data-row>td:nth-child(2):before{content:'Son Deneme'}.insem-table tr.data-row>td:nth-child(3):before{content:'Tohumlama'}.insem-table tr.data-row>td:nth-child(4):before{content:'Durum'}.insem-table tr.data-row>td:nth-child(5):before{content:'Tahmini Doğum'}.insem-table tr.data-row>td:nth-child(6){display:block;border-top:1px solid #edf1ee;margin-top:7px;padding-top:10px}.insem-table tr.data-row>td:nth-child(6):before{display:none}
  .insem-table details summary{padding:8px 0;font-weight:800;color:var(--g)}.insem-history{min-width:570px!important}
}

.estrus-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}.estrus-actions form{margin:0}.estrus-window-now{background:#fff6e8;border-left-color:#e27b1f}.estrus-window-next{background:#f3f7f4;border-left-color:#238a50}
@media(max-width:700px){
  .estrus-table,.estrus-table tbody,.estrus-table tr.data-row,.estrus-table tr.data-row>td{display:block;width:100%;min-width:0!important}.estrus-table{background:transparent}.estrus-table>thead{display:none}
  .estrus-table tr.data-row{background:#fff;border:1px solid #e1ebe4;border-radius:16px;margin-bottom:10px;padding:14px;box-shadow:0 3px 13px #14271b0d}
  .estrus-table tr.data-row>td{border:0;padding:5px 0;display:grid;grid-template-columns:112px 1fr;gap:9px;align-items:start}
  .estrus-table tr.data-row>td:before{font-size:12px;font-weight:800;color:var(--mut)}
  .estrus-table tr.data-row>td:nth-child(1):before{content:'Hayvan'}.estrus-table tr.data-row>td:nth-child(2):before{content:'Gözlem'}.estrus-table tr.data-row>td:nth-child(3):before{content:'Belirtiler'}.estrus-table tr.data-row>td:nth-child(4):before{content:'Pencere'}.estrus-table tr.data-row>td:nth-child(5):before{content:'21. Gün'}.estrus-table tr.data-row>td:nth-child(6):before{content:'Not'}
  .estrus-table tr.data-row>td:last-child{display:flex;gap:7px;flex-wrap:wrap;border-top:1px solid #edf1ee;margin-top:7px;padding-top:10px}.estrus-table tr.data-row>td:last-child:before{display:none}
}

@media(max-width:430px){
  .brand{font-size:20px}.top-user{font-size:12px}.main{padding-left:10px;padding-right:10px}h1{font-size:28px}
  .live-clear{font-size:0;width:46px!important}.live-clear:after{content:'×';font-size:24px;line-height:1}
  .business-summary-grid .stat b{font-size:21px}.mobile-animal-table tr.data-row td{grid-template-columns:92px 1fr}
}

/* V3.7.6 Görsel Standartlar */
.btn{min-height:40px;border-radius:11px;padding:9px 14px;display:inline-flex;align-items:center;justify-content:center;gap:6px;line-height:1.15;text-decoration:none;transition:transform .12s ease,filter .12s ease,box-shadow .12s ease}
.btn:hover{filter:brightness(.97);box-shadow:0 5px 14px rgba(20,70,43,.10)}
.btn:active{transform:translateY(1px)}
.btn.red,.btn.danger{background:#d83a2e;color:#fff}.btn.secondary{background:#eef4ef;color:#176b3a}.compact-btn{min-height:34px;padding:7px 10px;border-radius:9px}
.row-actions,.finance-actions,.actions{gap:8px;align-items:center;flex-wrap:wrap}.inline-form{margin:0}
.finance-primary-actions{display:flex;align-items:center;gap:14px;margin:14px 0 18px;flex-wrap:wrap}.finance-new-btn{font-size:15px;padding:13px 20px;border-radius:12px;box-shadow:0 8px 20px rgba(15,112,61,.18)}
.finance-drawer-backdrop{position:fixed;inset:0;background:rgba(13,38,26,.38);backdrop-filter:blur(2px);z-index:1090;display:none}.finance-drawer-backdrop.open{display:block}.finance-drawer{position:fixed;top:0;right:0;height:100vh;width:min(760px,94vw);background:#f5f8f6;z-index:1100;transform:translateX(105%);transition:transform .22s ease;box-shadow:-20px 0 50px rgba(12,45,28,.20);display:flex;flex-direction:column}.finance-drawer.open{transform:translateX(0)}.finance-drawer-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;padding:22px 24px 17px;background:#fff;border-bottom:1px solid #dce8df;position:sticky;top:0;z-index:2}.finance-drawer-close{width:42px;height:42px;border:0;border-radius:50%;font-size:29px;background:#eaf3ed;color:#145b34;cursor:pointer}.finance-drawer-body{padding:18px 20px 35px;overflow:auto}.finance-entry-card{margin:0!important;box-shadow:none!important}.finance-drawer .bulk-list{max-height:310px;overflow:auto}
@media(max-width:700px){.finance-primary-actions{position:sticky;top:62px;z-index:15;background:#f4f7f5;padding:8px 0;margin:5px 0 12px}.finance-new-btn{width:100%}.finance-primary-actions .mut{display:none}.finance-drawer{width:100vw}.finance-drawer-head{padding:16px}.finance-drawer-body{padding:12px 12px 28px}.finance-drawer .bulk-list{max-height:42vh}}
.finance-filter-card{background:linear-gradient(180deg,#fff,#f8fbf9);border:1px solid #dce8df}
.finance-filter-title{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:14px}.finance-filter-title h2{margin:0 0 3px}
.filter-count-pill{display:inline-flex;padding:7px 11px;border-radius:999px;background:#edf5ef;color:#315943;font-weight:800;white-space:nowrap}
.finance-toolbar-modern{display:grid;grid-template-columns:1fr 1fr .9fr 1.15fr auto;gap:10px;align-items:end}
.finance-toolbar-modern label{display:flex;flex-direction:column;gap:5px;font-size:13px;font-weight:800}.finance-toolbar-modern label>span{color:#415f50}
.finance-toolbar-modern input,.finance-toolbar-modern select{min-height:42px;border:1px solid #ccd9d0;border-radius:10px;background:#fff;padding:8px 10px}
.finance-filter-actions{display:flex;gap:7px;align-items:center;white-space:nowrap}.export-btn{background:#2f74c7;color:#fff}
@media(max-width:1100px){.finance-toolbar-modern{grid-template-columns:repeat(2,minmax(0,1fr))}.finance-filter-actions{grid-column:1/-1}}
@media(max-width:600px){.finance-filter-title{align-items:flex-start;flex-direction:column}.finance-toolbar-modern{grid-template-columns:1fr}.finance-filter-actions{grid-column:auto;display:grid;grid-template-columns:1fr 1fr}.finance-filter-actions .export-btn{grid-column:1/-1}.btn{min-height:44px}}
'''

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def is_pregnant_value(value):
    normalized=str(value or "").strip().lower()
    if normalized.startswith("gebe (satın alındığında"):
        return True
    return normalized in {
        "pozitif","gebe","evet","yes","true","1","olumlu",
        "gebelik pozitif","pozitif (gebe)","pregnant"
    }


def recalculate_animal_exit_status(con, animal_id):
    if not animal_id:
        return
    row=con.execute(
        """select animal_status_action,tx_date,category,amount
           from finance
           where animal_id=? and animal_status_action in ('Satıldı','Kesildi')
           order by tx_date desc,id desc limit 1""",
        (animal_id,)
    ).fetchone()
    if row:
        con.execute(
            "update animals set status=?,exit_date=?,exit_reason=?,sold_price=? where id=?",
            (row["animal_status_action"],row["tx_date"],row["category"],row["amount"],animal_id)
        )
    else:
        con.execute(
            "update animals set status='Aktif',exit_date='',exit_reason='',sold_price=0 where id=?",
            (animal_id,)
        )

def ensure_archive_schema():
    with db() as c:
        cols={r[1] for r in c.execute("pragma table_info(animals)").fetchall()}
        for col,typ in [
            ("status","TEXT DEFAULT 'Aktif'"),
            ("exit_date","TEXT DEFAULT ''"),
            ("exit_reason","TEXT DEFAULT ''"),
            ("sold_price","REAL DEFAULT 0")
        ]:
            if col not in cols:
                c.execute(f"ALTER TABLE animals ADD COLUMN {col} {typ}")
        fcols={r[1] for r in c.execute("pragma table_info(finance)").fetchall()}
        if "animal_status_action" not in fcols:
            c.execute("ALTER TABLE finance ADD COLUMN animal_status_action TEXT DEFAULT ''")
        c.execute("update animals set status='Aktif' where status is null or trim(status)=''")




def next_estrus_cycle(con, rec, today=None):
    today=today or date.today()
    try: observed=date.fromisoformat(rec['estrus_date'])
    except Exception: return None
    cycle=1
    while cycle<=24:
        d=con.execute("select decision from estrus_decisions where estrus_id=? and cycle_no=?",(rec['id'],cycle)).fetchone()
        if not d:
            center=observed+timedelta(days=21*cycle)
            return {'cycle_no':cycle,'start':center-timedelta(days=3),'center':center,'end':center+timedelta(days=3)}
        if str(d['decision'])=='Atlandı':
            cycle+=1
            continue
        return None
    return None

def password_hash(password):
    salt=secrets.token_bytes(16); rounds=240000
    digest=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),salt,rounds)
    return f'pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}'

def password_verify(password,stored):
    stored=str(stored or '')
    if stored.startswith('pbkdf2_sha256$'):
        try:
            _,rounds,salt_hex,digest_hex=stored.split('$',3)
            candidate=hashlib.pbkdf2_hmac('sha256',password.encode('utf-8'),bytes.fromhex(salt_hex),int(rounds)).hex()
            return hmac.compare_digest(candidate,digest_hex)
        except Exception:return False
    return hmac.compare_digest(hashlib.sha256(('farm-v05'+password).encode()).hexdigest(),stored)

def audit(username,action,detail='',ip_address=''):
    try:
        with db() as c:c.execute('insert into audit_log(username,action,detail,created_at,ip_address) values(?,?,?,?,?)',(username or 'sistem',action,detail,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),ip_address or ''))
    except Exception:pass


def setting_get(key,default=''):
    try:
        with db() as c:
            r=c.execute('select setting_value from settings where setting_key=?',(key,)).fetchone()
        return (r['setting_value'] if r else default) or default
    except Exception:
        return default

def setting_set(key,value):
    with db() as c:
        c.execute("""insert into settings(setting_key,setting_value) values(?,?)
                     on conflict(setting_key) do update set setting_value=excluded.setting_value""",(key,str(value or '')))

def smtp_config():
    return {
        'host':setting_get('smtp_host','smtp.gmail.com'),
        'port':int(setting_get('smtp_port','587') or 587),
        'username':setting_get('smtp_username',''),
        'password':setting_get('smtp_password',''),
        'sender':setting_get('smtp_sender','') or setting_get('smtp_username',''),
        'security':setting_get('smtp_security','starttls') or 'starttls',
    }

def send_reset_email(to_email,full_name,code):
    cfg=smtp_config()
    if not cfg['host'] or not cfg['sender']:
        raise RuntimeError('E-posta sunucusu ayarları tamamlanmamış.')
    msg=EmailMessage();msg['Subject']='ÇiftlikPro şifre sıfırlama kodu';msg['From']=cfg['sender'];msg['To']=to_email
    display=(full_name or 'ÇiftlikPro kullanıcısı').strip()
    msg.set_content(f"Merhaba {display},\n\nÇiftlikPro şifre sıfırlama doğrulama kodunuz:\n\n{code}\n\nBu kod 5 dakika geçerlidir ve yalnızca bir kez kullanılabilir.\nBu işlemi siz başlatmadıysanız bu e-postayı dikkate almayın.\n\nÇiftlikPro Enterprise")
    context=ssl.create_default_context()
    if cfg['security']=='ssl':
        with smtplib.SMTP_SSL(cfg['host'],cfg['port'],timeout=20,context=context) as server:
            if cfg['username']:server.login(cfg['username'],cfg['password'])
            server.send_message(msg)
    else:
        with smtplib.SMTP(cfg['host'],cfg['port'],timeout=20) as server:
            server.ehlo()
            if cfg['security']=='starttls':server.starttls(context=context);server.ehlo()
            if cfg['username']:server.login(cfg['username'],cfg['password'])
            server.send_message(msg)

def reset_code_hash(salt,code):return hashlib.sha256((str(salt)+'|'+str(code)).encode('utf-8')).hexdigest()
def reset_token_hash(token):return hashlib.sha256(str(token).encode('utf-8')).hexdigest()

def finance_request_fingerprint(username,form):
    keys=('tx_date','tx_type','category','amount','description','payment_method','animal_id','animal_ids','milk_animal_ids')
    payload='|'.join(str(form.get(k,'')).strip() for k in keys)
    return hashlib.sha256((str(username)+'|'+payload).encode('utf-8')).hexdigest()

def claim_request_once(con,fingerprint,ttl_seconds=15):
    cutoff=(datetime.now()-timedelta(seconds=ttl_seconds)).isoformat(timespec='seconds')
    con.execute('delete from request_dedupe where created_at<?',(cutoff,))
    try:
        con.execute('insert into request_dedupe(fingerprint,created_at) values(?,?)',
                    (fingerprint,datetime.now().isoformat(timespec='seconds')))
        return True
    except sqlite3.IntegrityError:
        return False


def active_admin_count():
    with db() as c:return c.execute("select count(*) from users where role='admin' and active=1").fetchone()[0]

def init_db():
    BACKUPS.mkdir(exist_ok=True)
    UPLOADS.mkdir(exist_ok=True)
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT DEFAULT 'admin');
        CREATE TABLE IF NOT EXISTS animals(id INTEGER PRIMARY KEY, tag TEXT UNIQUE NOT NULL, nickname TEXT, gender TEXT NOT NULL, breed TEXT, birth_date TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS inseminations(id INTEGER PRIMARY KEY, animal_id INTEGER, attempt INTEGER, insemination_date TEXT, pregnancy_result TEXT, due_date TEXT, UNIQUE(animal_id,attempt));
        CREATE TABLE IF NOT EXISTS estrus_records(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, estrus_date TEXT NOT NULL, signs TEXT, notes TEXT, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS estrus_decisions(id INTEGER PRIMARY KEY, estrus_id INTEGER NOT NULL, cycle_no INTEGER NOT NULL, decision TEXT NOT NULL, decision_date TEXT NOT NULL, insemination_id INTEGER, notes TEXT, UNIQUE(estrus_id,cycle_no));
        CREATE TABLE IF NOT EXISTS calves(id INTEGER PRIMARY KEY, tag TEXT UNIQUE NOT NULL, mother_id INTEGER NOT NULL, father_tag TEXT, birth_date TEXT NOT NULL, gender TEXT, notes TEXT);
        CREATE TABLE IF NOT EXISTS health(id INTEGER PRIMARY KEY, animal_id INTEGER, kind TEXT, product TEXT, applied_date TEXT, next_date TEXT, cost REAL DEFAULT 0, notes TEXT);
        CREATE TABLE IF NOT EXISTS health_courses(id INTEGER PRIMARY KEY,kind TEXT NOT NULL,product TEXT NOT NULL,scope_type TEXT NOT NULL DEFAULT 'single',paddock_id INTEGER,start_date TEXT NOT NULL,treatment_days INTEGER DEFAULT 1,times_per_day INTEGER DEFAULT 1,dose_count INTEGER DEFAULT 1,interval_days INTEGER DEFAULT 0,cost_per_application REAL DEFAULT 0,notes TEXT,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS health_tasks(id INTEGER PRIMARY KEY,course_id INTEGER NOT NULL,animal_id INTEGER,calf_id INTEGER,planned_date TEXT NOT NULL,dose_no INTEGER DEFAULT 1,dose_total INTEGER DEFAULT 1,day_no INTEGER DEFAULT 1,day_total INTEGER DEFAULT 1,application_no INTEGER DEFAULT 1,applications_per_day INTEGER DEFAULT 1,status TEXT DEFAULT 'Bekliyor',completed_date TEXT,cost REAL DEFAULT 0,notes TEXT);
        CREATE INDEX IF NOT EXISTS idx_health_tasks_due ON health_tasks(status,planned_date,course_id);
        CREATE TABLE IF NOT EXISTS finance(id INTEGER PRIMARY KEY, tx_date TEXT NOT NULL, tx_type TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL, description TEXT, payment_method TEXT, animal_id INTEGER, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY, filename TEXT, created_at TEXT, size_bytes INTEGER);
        CREATE TABLE IF NOT EXISTS weights(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, measure_date TEXT NOT NULL, weight REAL NOT NULL, notes TEXT);
        CREATE TABLE IF NOT EXISTS milk(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, measure_date TEXT NOT NULL, liters REAL NOT NULL, notes TEXT);
        CREATE TABLE IF NOT EXISTS animal_photos(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, filename TEXT NOT NULL, created_at TEXT NOT NULL, caption TEXT);
        CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY, username TEXT, action TEXT, detail TEXT, created_at TEXT, ip_address TEXT);
        CREATE TABLE IF NOT EXISTS settings(setting_key TEXT PRIMARY KEY, setting_value TEXT);
        CREATE TABLE IF NOT EXISTS paddocks(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,code TEXT,type TEXT,capacity INTEGER DEFAULT 0,notes TEXT,active INTEGER DEFAULT 1,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS paddock_history(id INTEGER PRIMARY KEY,animal_source TEXT NOT NULL,animal_id INTEGER NOT NULL,from_paddock_id INTEGER,to_paddock_id INTEGER,moved_at TEXT NOT NULL,notes TEXT);
        CREATE TABLE IF NOT EXISTS feed_catalog(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,category TEXT,dm_pct REAL DEFAULT 0,ndf_pct REAL DEFAULT 0,cp_pct REAL DEFAULT 0,tdn_pct REAL DEFAULT 0,me_mcal_kg REAL DEFAULT 0,nem_mcal_kg REAL DEFAULT 0,neg_mcal_kg REAL DEFAULT 0,starch_pct REAL DEFAULT 0,fat_pct REAL DEFAULT 0,ash_pct REAL DEFAULT 0,ca_pct REAL DEFAULT 0,p_pct REAL DEFAULT 0,mg_pct REAL DEFAULT 0,k_pct REAL DEFAULT 0,na_pct REAL DEFAULT 0,s_pct REAL DEFAULT 0,source TEXT,active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS feed_prices(id INTEGER PRIMARY KEY,feed_id INTEGER NOT NULL,effective_date TEXT NOT NULL,price_per_kg REAL NOT NULL,notes TEXT);
        CREATE TABLE IF NOT EXISTS feed_stock_transactions(id INTEGER PRIMARY KEY,feed_id INTEGER NOT NULL,tx_date TEXT NOT NULL,tx_type TEXT NOT NULL,quantity_kg REAL NOT NULL,unit_price REAL DEFAULT 0,notes TEXT);
        CREATE TABLE IF NOT EXISTS rations(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,target_group TEXT,notes TEXT,active INTEGER DEFAULT 1,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS ration_items(id INTEGER PRIMARY KEY,ration_id INTEGER NOT NULL,feed_id INTEGER NOT NULL,kg_per_head_day REAL NOT NULL,UNIQUE(ration_id,feed_id));
        CREATE TABLE IF NOT EXISTS ration_item_history(id INTEGER PRIMARY KEY,ration_id INTEGER NOT NULL,feed_id INTEGER NOT NULL,effective_date TEXT NOT NULL,kg_per_head_day REAL NOT NULL,created_at TEXT NOT NULL,notes TEXT);
        CREATE INDEX IF NOT EXISTS idx_ration_item_history_lookup ON ration_item_history(ration_id,feed_id,effective_date,id);
        CREATE TABLE IF NOT EXISTS paddock_rations(id INTEGER PRIMARY KEY,paddock_id INTEGER NOT NULL,ration_id INTEGER NOT NULL,start_date TEXT NOT NULL,end_date TEXT,active INTEGER DEFAULT 1,notes TEXT);
        ''')
        user_cols={r[1] for r in c.execute('pragma table_info(users)').fetchall()}
        for col,typ in [('full_name','TEXT'),('active','INTEGER DEFAULT 1'),('last_login','TEXT'),('password_changed_at','TEXT'),('recovery_email','TEXT')]:
            if col not in user_cols:c.execute(f'ALTER TABLE users ADD COLUMN {col} {typ}')
        c.execute("update users set active=1 where active is null")
        c.execute("update users set full_name=username where full_name is null or trim(full_name)=''")
        c.execute("insert or ignore into settings(setting_key,setting_value) values('male_min_daily_gain','1.0')")
        c.execute("insert or ignore into settings(setting_key,setting_value) values('male_warning_ratio','0.90')")
        ration_cols={r[1] for r in c.execute('pragma table_info(rations)').fetchall()}
        for col,typ in [('target_weight_kg','REAL DEFAULT 450'),('target_adg_kg','REAL DEFAULT 1.3'),('animal_type',"TEXT DEFAULT 'Besi Erkek'"),('ration_type',"TEXT DEFAULT 'Besi'"),('target_milk_l','REAL DEFAULT 25'),('milk_fat_pct','REAL DEFAULT 3.8'),('milk_protein_pct','REAL DEFAULT 3.2')]:
            if col not in ration_cols:c.execute(f'ALTER TABLE rations ADD COLUMN {col} {typ}')
        # Rasyon miktar geçmişi: mevcut rasyonları başlangıç revizyonu olarak koru.
        # Böylece padoka atama tarihinden sonraki maliyetler ilerideki rasyon değişiklikleriyle geriye dönük bozulmaz.
        for ri in c.execute('''select ri.ration_id,ri.feed_id,ri.kg_per_head_day,r.created_at
                               from ration_items ri join rations r on r.id=ri.ration_id''').fetchall():
            exists=c.execute('select 1 from ration_item_history where ration_id=? and feed_id=? limit 1',(ri['ration_id'],ri['feed_id'])).fetchone()
            if not exists:
                eff=str(ri['created_at'] or date.today().isoformat())[:10]
                c.execute('insert into ration_item_history(ration_id,feed_id,effective_date,kg_per_head_day,created_at,notes) values(?,?,?,?,?,?)',
                          (ri['ration_id'],ri['feed_id'],eff,float(ri['kg_per_head_day'] or 0),datetime.now().isoformat(timespec='seconds'),'V3.9.8 maliyet entegrasyonu başlangıç revizyonu'))
        c.execute("""CREATE TABLE IF NOT EXISTS password_reset_codes(
            id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,code_hash TEXT NOT NULL,salt TEXT NOT NULL,expires_at TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,used INTEGER DEFAULT 0,reset_token_hash TEXT,reset_token_expires TEXT,created_at TEXT NOT NULL,ip_address TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS finance_animals(
            finance_id INTEGER NOT NULL,animal_id INTEGER NOT NULL,relation_type TEXT DEFAULT 'İlgili',PRIMARY KEY(finance_id,animal_id))""")
        for k,v in [('smtp_host','smtp.gmail.com'),('smtp_port','587'),('smtp_security','starttls'),('smtp_username',''),('smtp_password',''),('smtp_sender','')]:
            c.execute("insert or ignore into settings(setting_key,setting_value) values(?,?)",(k,v))
        c.execute("""CREATE TABLE IF NOT EXISTS request_dedupe(
            fingerprint TEXT PRIMARY KEY,
            created_at TEXT NOT NULL
        )""")

        health_cols={r[1] for r in c.execute('pragma table_info(health)').fetchall()}
        if 'calf_id' not in health_cols:c.execute('ALTER TABLE health ADD COLUMN calf_id INTEGER')
        calf_cols={r[1] for r in c.execute('pragma table_info(calves)').fetchall()}
        if 'promoted_animal_id' not in calf_cols:c.execute('ALTER TABLE calves ADD COLUMN promoted_animal_id INTEGER')
        if 'promoted_at' not in calf_cols:c.execute('ALTER TABLE calves ADD COLUMN promoted_at TEXT')
        for col,typ in [('nickname','TEXT'),('breed','TEXT'),('paddock','TEXT'),('photo_url','TEXT'),('purchase_date','TEXT'),('purchase_price','REAL DEFAULT 0'),('purchase_payment_method',"TEXT DEFAULT 'Nakit'")]:
            if col not in calf_cols:c.execute(f'ALTER TABLE calves ADD COLUMN {col} {typ}')
        c.execute("CREATE TABLE IF NOT EXISTS calf_weights(id INTEGER PRIMARY KEY,calf_id INTEGER NOT NULL,measure_date TEXT NOT NULL,weight REAL NOT NULL,notes TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS calf_photos(id INTEGER PRIMARY KEY,calf_id INTEGER NOT NULL,filename TEXT NOT NULL,created_at TEXT NOT NULL,caption TEXT)")
        cols={r[1] for r in c.execute('pragma table_info(animals)').fetchall()}
        for col,typ in [('paddock','TEXT'),('photo_url','TEXT'),('sold_price','REAL DEFAULT 0'),('status',"TEXT DEFAULT 'Aktif'"),('exit_date','TEXT'),('exit_reason','TEXT'),('purchase_date','TEXT'),('purchase_price','REAL DEFAULT 0'),('purchase_weight','REAL DEFAULT 0'),('daily_feed_cost','REAL DEFAULT 0'),('daily_care_cost','REAL DEFAULT 0'),('target_sale_price','REAL DEFAULT 0'),('pregnancy_source','TEXT DEFAULT \'\''),('pregnancy_age_months_at_entry','REAL DEFAULT 0'),('pregnancy_entry_date','TEXT DEFAULT \'\'')]:
            if col not in cols:c.execute(f'ALTER TABLE animals ADD COLUMN {col} {typ}')
        # V3.9.0 Padok + Yem/Rasyon veri modeli
        calf_cols={r[1] for r in c.execute('pragma table_info(calves)').fetchall()}
        if 'paddock_id' not in calf_cols:c.execute('ALTER TABLE calves ADD COLUMN paddock_id INTEGER')
        animal_cols={r[1] for r in c.execute('pragma table_info(animals)').fetchall()}
        if 'paddock_id' not in animal_cols:c.execute('ALTER TABLE animals ADD COLUMN paddock_id INTEGER')
        # Eski serbest metin padokları kaybetmeden gerçek padok kayıtlarına dönüştür.
        legacy_names=set()
        for rr in c.execute("select distinct trim(coalesce(paddock,'')) p from animals where trim(coalesce(paddock,''))<>''").fetchall(): legacy_names.add(rr['p'])
        for rr in c.execute("select distinct trim(coalesce(paddock,'')) p from calves where trim(coalesce(paddock,''))<>''").fetchall(): legacy_names.add(rr['p'])
        for name in sorted(legacy_names):
            c.execute('insert or ignore into paddocks(name,code,type,capacity,notes,active,created_at) values(?,?,?,?,?,?,?)',(name,'','Genel',0,'V3.8.x serbest metin padok kaydından aktarıldı',1,datetime.now().isoformat(timespec='seconds')))
        c.execute("update animals set paddock_id=(select id from paddocks where paddocks.name=trim(animals.paddock)) where paddock_id is null and trim(coalesce(paddock,''))<>''")
        c.execute("update calves set paddock_id=(select id from paddocks where paddocks.name=trim(calves.paddock)) where paddock_id is null and trim(coalesce(paddock,''))<>''")
        # Besi_V5.02.xlsm'den yalnız besin referans verilerini ilk kurulumda yükle; fiyatlar özellikle taşınmaz.
        if c.execute('select count(*) from feed_catalog').fetchone()[0]==0:
            catalog_file=PROGRAM_DIR/'feed_catalog.json'
            if catalog_file.exists():
                try:
                    for x in json.loads(catalog_file.read_text(encoding='utf-8')):
                        c.execute('''insert or ignore into feed_catalog(name,category,dm_pct,ndf_pct,cp_pct,tdn_pct,me_mcal_kg,nem_mcal_kg,neg_mcal_kg,starch_pct,fat_pct,ash_pct,ca_pct,p_pct,mg_pct,k_pct,na_pct,s_pct,source,active) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)''',
                                  (x.get('name',''),x.get('category',''),x.get('dm_pct',0),x.get('ndf_pct',0),x.get('cp_pct',0),x.get('tdn_pct',0),x.get('me_mcal_kg',0),x.get('nem_mcal_kg',0),x.get('neg_mcal_kg',0),x.get('starch_pct',0),x.get('fat_pct',0),x.get('ash_pct',0),x.get('ca_pct',0),x.get('p_pct',0),x.get('mg_pct',0),x.get('k_pct',0),x.get('na_pct',0),x.get('s_pct',0),x.get('source','')))
                except Exception as exc:
                    print('Yem kataloğu yüklenemedi:',exc)
        # V3.9.16: NASEM ile birebir eşleştirilebilen temel yemleri mevcut kurulumlarda da güncelle.
        # Kullanıcının daha önce elle/laboratuvar analiziyle değiştirdiği kayıtları ezmemek için yalnız eski Besi_V5.02 kaynaklı satırlar güncellenir.
        try:
            catalog_file=PROGRAM_DIR/'feed_catalog.json'
            if catalog_file.exists():
                modern_names={'ARPA, AĞIR','ARPA, HAFİF','ARPA SİLAJI','BUĞDAY, ÖĞÜTÜLMÜŞ','BUĞDAY SAMANI','MISIR SİLAJI, %33-40 KM'}
                for x in json.loads(catalog_file.read_text(encoding='utf-8')):
                    if x.get('name') not in modern_names: continue
                    c.execute('''update feed_catalog set category=?,dm_pct=?,ndf_pct=?,cp_pct=?,tdn_pct=?,me_mcal_kg=?,nem_mcal_kg=?,neg_mcal_kg=?,starch_pct=?,fat_pct=?,ash_pct=?,ca_pct=?,p_pct=?,mg_pct=?,k_pct=?,na_pct=?,s_pct=?,source=? where name=? and (source is null or source='' or source like 'Besi_V5.02%')''',
                              (x.get('category',''),x.get('dm_pct',0),x.get('ndf_pct',0),x.get('cp_pct',0),x.get('tdn_pct',0),x.get('me_mcal_kg',0),x.get('nem_mcal_kg',0),x.get('neg_mcal_kg',0),x.get('starch_pct',0),x.get('fat_pct',0),x.get('ash_pct',0),x.get('ca_pct',0),x.get('p_pct',0),x.get('mg_pct',0),x.get('k_pct',0),x.get('na_pct',0),x.get('s_pct',0),x.get('source',''),x.get('name','')))
        except Exception as exc:
            print('NASEM yem kataloğu güncellemesi uygulanamadı:',exc)
        # V3.9.18: ÇiftlikPro 4 Fazlı Besi reçeteleri.
        # Reçeteler mevcut yem kataloğundaki kayıtları kullanır; besin değerlerini kopyalamaz.
        # Böylece kullanıcı bir yemin KM/HP/NDF/ME vb. değerini düzenlediğinde rasyon hesabı anında yeni değeri kullanır.
        try:
            def _feed_key(txt):
                txt=(txt or '').strip().upper()
                tr=str.maketrans({'İ':'I','Ş':'S','Ğ':'G','Ü':'U','Ö':'O','Ç':'C'})
                return ' '.join(txt.translate(tr).replace('_',' ').replace('-',' ').split())

            active_feeds=c.execute("select id,name from feed_catalog where active=1 order by id").fetchall()
            keyed=[(r['id'],r['name'],_feed_key(r['name'])) for r in active_feeds]

            def _pick_feed(*aliases):
                alias_keys=[_feed_key(a) for a in aliases if a]
                for ak in alias_keys:
                    for fid,name,k in keyed:
                        if k==ak:return fid,name
                for ak in alias_keys:
                    toks=[t for t in ak.split() if len(t)>1]
                    for fid,name,k in keyed:
                        if toks and all(t in k for t in toks):return fid,name
                return None,None

            feed_refs={
                'straw':_pick_feed('ARPA SAMANI'),
                'barley':_pick_feed('ARPA EZMESİ','ARPA EZMESI','ARPA, AĞIR','ARPA, HAFİF'),
                'wheat':_pick_feed('BUĞDAY EZMESİ','BUGDAY EZMESI','BUĞDAY, ÖĞÜTÜLMÜŞ'),
                'alfalfa':_pick_feed('YONCA',"YONCA KURU OTU, KM'de %17-19 HP, %40-44 NDF","YONCA KURU OTU, KM'de %15-17 HP, %44-48 NDF"),
                'cob_silage':_pick_feed('MISIR KOÇANI SİLAJI','MISIR KOCANI SILAJI'),
                'beef15':_pick_feed('15 PROTEİN 2650 ME BESİ YEMİ','15 PROTEIN 2650 ME BESI YEMI','%15 BESİ YEMİ','15 BESİ YEMİ'),
                'dairy19':_pick_feed('19 PROTEİN 2750 ME SÜT YEMİ','19 PROTEIN 2750 ME SUT YEMI','%19 SÜT YEMİ','19 SÜT YEMİ'),
            }

            phase_recipes=[
                ('ÇiftlikPro Faz 1 · 250–350 kg Büyütme','250–350 kg · Büyütme',300,1.00,
                 {'straw':1.20,'barley':2.00,'wheat':0.30,'alfalfa':1.50,'cob_silage':4.00,'beef15':1.00,'dairy19':0.50},
                 'Hazır başlangıç reçetesi · hedef CAA yaklaşık 0,9–1,1 kg/gün. Kaba yem ve protein ağırlıklı büyütme fazı.'),
                ('ÇiftlikPro Faz 2 · 350–450 kg Geliştirme','350–450 kg · Geliştirme',400,1.20,
                 {'straw':1.20,'barley':3.50,'wheat':0.50,'alfalfa':1.40,'cob_silage':4.50,'beef15':1.40,'dairy19':0.30},
                 'Hazır başlangıç reçetesi · hedef CAA yaklaşık 1,1–1,3 kg/gün. Enerji kademeli yükseltilir.'),
                ('ÇiftlikPro Faz 3 · 450–550 kg Yoğun Besi','450–550 kg · Yoğun Besi',500,1.50,
                 {'straw':1.00,'barley':6.50,'wheat':1.00,'alfalfa':1.00,'cob_silage':4.00,'beef15':2.00,'dairy19':0.00},
                 'Hazır başlangıç reçetesi · hedef CAA yaklaşık 1,4–1,5 kg/gün. Buğday 1,0 kg/gün üst sınırında tutulur.'),
                ('ÇiftlikPro Faz 4 · 550 kg+ Bitirme','550 kg+ · Bitirme',600,1.35,
                 {'straw':0.80,'barley':8.00,'wheat':1.00,'alfalfa':1.00,'cob_silage':5.00,'beef15':2.00,'dairy19':0.00},
                 'Hazır başlangıç reçetesi · hedef CAA yaklaşık 1,2–1,5 kg/gün. Ekonomik bitirme ve yüksek enerji yoğunluğu hedeflenir.'),
            ]

            now_iso=datetime.now().isoformat(timespec='seconds')
            for rname,target_group,target_w,target_adg,items,rnote in phase_recipes:
                rr=c.execute('select id from rations where name=?',(rname,)).fetchone()
                if rr:
                    oldnote=c.execute('select notes from rations where id=?',(rr['id'],)).fetchone()
                    if oldnote and 'Hazır başlangıç reçetesi' in str(oldnote['notes'] or ''):
                        rid=int(rr['id'])
                        c.execute('delete from ration_items where ration_id=?',(rid,))
                        c.execute('update rations set target_group=?,target_weight_kg=?,target_adg_kg=?,notes=? where id=?',(target_group,float(target_w),float(target_adg),rnote+' V3.9.19 dengelenmiş hazır reçete · NASEM ortalama yem değerleri esaslıdır.',rid))
                        for key,kg in items.items():
                            fid,_fname=feed_refs[key]
                            if fid and float(kg)>0:
                                c.execute('insert or replace into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)',(rid,fid,float(kg)))
                                c.execute('insert into ration_item_history(ration_id,feed_id,effective_date,kg_per_head_day,created_at,notes) values(?,?,?,?,?,?)',(rid,fid,date.today().isoformat(),float(kg),now_iso,'V3.9.19 dengelenmiş hazır 4 faz reçetesi'))
                        continue
                    continue  # Kullanıcının kendi reçetesini/değiştirdiği kaydı ezme.
                missing=[]
                for key in items:
                    if not feed_refs[key][0]:missing.append(key)
                note=rnote+' Besin hesapları doğrudan aktif Yem Kataloğu değerlerinden yapılır.'
                if missing:
                    labels={'straw':'Arpa samanı','barley':'Arpa ezmesi','wheat':'Buğday ezmesi','alfalfa':'Yonca','cob_silage':'Mısır koçanı silajı','beef15':'%15 / 2650 ME besi yemi','dairy19':'%19 / 2750 ME süt yemi'}
                    note+=' Eksik katalog eşleşmesi: '+', '.join(labels[x] for x in missing)+'. Bu yemleri katalogda ekledikten sonra reçeteye manuel ekleyebilirsiniz.'
                cur=c.execute('''insert into rations(name,target_group,notes,active,created_at,target_weight_kg,target_adg_kg,animal_type,ration_type,target_milk_l,milk_fat_pct,milk_protein_pct)
                                 values(?,?,?,1,?,?,?,?,?,?,?,?)''',
                              (rname,target_group,note,now_iso,float(target_w),float(target_adg),'Besi Erkek','Besi',25,3.8,3.2))
                rid=cur.lastrowid
                for key,kg in items.items():
                    fid,_fname=feed_refs[key]
                    if not fid or float(kg)<=0:continue
                    c.execute('insert or ignore into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)',(rid,fid,float(kg)))
                    c.execute('insert into ration_item_history(ration_id,feed_id,effective_date,kg_per_head_day,created_at,notes) values(?,?,?,?,?,?)',
                              (rid,fid,date.today().isoformat(),float(kg),now_iso,'V3.9.18 hazır 4 fazlı besi reçetesi başlangıç değeri'))
        except Exception as exc:
            print('4 fazlı hazır besi reçeteleri oluşturulamadı:',exc)

        finance_cols={r[1] for r in c.execute('pragma table_info(finance)').fetchall()}
        if 'animal_status_action' not in finance_cols:c.execute("ALTER TABLE finance ADD COLUMN animal_status_action TEXT DEFAULT ''")
        n=c.execute('select count(*) from users').fetchone()[0]
        if not n:
            c.execute('insert into users(username,password,role,full_name,active,password_changed_at) values(?,?,?,?,?,?)',('admin',password_hash('admin123'),'admin','Yönetici',1,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


FARM_PROFILE_KEYS = (
    'farm_name','owner_name','phone','email','province','district','address',
    'business_no','tax_or_tc','vet_name','vet_phone','vet_email','notes','farm_logo'
)

def farm_profile():
    profile={k:'' for k in FARM_PROFILE_KEYS}
    try:
        with db() as c:
            rows=c.execute("select setting_key,setting_value from settings").fetchall()
        for r in rows:
            if r['setting_key'] in profile:
                profile[r['setting_key']]=r['setting_value'] or ''
    except Exception:
        pass
    return profile

def farm_display_name(profile=None):
    p=profile or farm_profile()
    return (p.get('farm_name') or '').strip() or 'ÇiftlikPro'


DASHBOARD_CARD_OPTIONS = [
    ('active_total','🐄 Toplam Aktif Hayvan'),
    ('female','🐮 Dişi Hayvan'),
    ('male','🐂 Erkek Hayvan'),
    ('pregnant','🤰 Gebe Hayvan'),
    ('calves','🐮 Buzağı'),
    ('due','📅 Yaklaşan Doğum'),
    ('estrus','🌸 Yaklaşan Kızgınlık'),
    ('income','📥 Toplam Gelir'),
    ('expense','📤 Toplam Gider'),
    ('net','⚖️ Net Durum'),
]
DASHBOARD_DEFAULT_LAYOUT=['active_total','female','male','pregnant','calves','due','estrus','']

def dashboard_layout(username):
    key='dashboard_layout_'+str(username)
    try:
        with db() as c:
            r=c.execute("select setting_value from settings where setting_key=?",(key,)).fetchone()
        if r and r['setting_value']:
            vals=(r['setting_value'].split(',')+['']*8)[:8]
            valid={x[0] for x in DASHBOARD_CARD_OPTIONS}
            return [v if v in valid else '' for v in vals]
    except Exception:
        pass
    return DASHBOARD_DEFAULT_LAYOUT[:]

def h(s):
    return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def money(v):
    return f"₺{float(v or 0):,.2f}".replace(',','X').replace('.',',').replace('X','.')

# Kullanıcıya gösterilen tarihler GG/AA/YYYY; form/veritabanı ISO kalır.
def fmt_date(v):
    if not v:return ''
    try:return datetime.strptime(str(v)[:10],'%Y-%m-%d').strftime('%d/%m/%Y')
    except Exception:return str(v)

def fmt_datetime(v):
    if not v:return ''
    try:
        x=str(v).replace('T',' ')
        d=datetime.fromisoformat(x)
        return d.strftime('%d/%m/%Y %H:%M')
    except Exception:
        return fmt_date(v)

def current_pregnancy_record(c, animal_id):
    latest=c.execute("select * from inseminations where animal_id=? order by insemination_date desc,id desc limit 1",(animal_id,)).fetchone()
    if not latest or not is_pregnant_value(latest['pregnancy_result']): return None
    ins_date=(latest['insemination_date'] or '').strip()
    if ins_date and c.execute("select id from calves where mother_id=? and birth_date>=? order by birth_date desc,id desc limit 1",(animal_id,ins_date)).fetchone(): return None
    return latest

def is_currently_pregnant(c, animal_id):
    return current_pregnancy_record(c,animal_id) is not None

def age_text(d):
    if not d:return '-'
    try:
        b=date.fromisoformat(d); days=(date.today()-b).days
        if days<60:return f'{days} gün'
        if days<730:return f'{days//30} ay'
        return f'{days//365} yıl {(days%365)//30} ay'
    except:return '-'

def months_old(d):
    try:
        b=date.fromisoformat(d); t=date.today()
        return (t.year-b.year)*12 + t.month-b.month - (1 if t.day < b.day else 0)
    except:return -1

def record_ration_item_history(c, ration_id, feed_id, kg_per_head_day, effective_date=None, notes='Rasyon düzenleme'):
    # Bir rasyon kaleminin tarihli durumunu saklar; kg=0 silinmiş kalemdir.
    eff=(effective_date or date.today().isoformat())[:10]
    kg=max(0.0,float(kg_per_head_day or 0))
    # Aynı gün aynı yem için son durum yeterlidir; geçmiş günleri değiştirmeyiz.
    c.execute('insert into ration_item_history(ration_id,feed_id,effective_date,kg_per_head_day,created_at,notes) values(?,?,?,?,?,?)',
              (int(ration_id),int(feed_id),eff,kg,datetime.now().isoformat(timespec='seconds'),notes))


def ration_items_on_date(c, ration_id, on_date):
    d=str(on_date)[:10]
    return c.execute('''select h.feed_id,h.kg_per_head_day,f.*
        from ration_item_history h
        join feed_catalog f on f.id=h.feed_id
        where h.ration_id=? and h.effective_date<=?
          and h.id=(select h2.id from ration_item_history h2
                    where h2.ration_id=h.ration_id and h2.feed_id=h.feed_id and h2.effective_date<=?
                    order by h2.effective_date desc,h2.id desc limit 1)
          and h.kg_per_head_day>0
        order by f.name''',(ration_id,d,d)).fetchall()


def ration_cost_on_date(c, ration_id, on_date):
    d=str(on_date)[:10]
    total=0.0
    for r in ration_items_on_date(c,ration_id,d):
        total += float(r['kg_per_head_day'] or 0) * current_feed_price(r['feed_id'],c,d)
    return total


def ration_cost_between(c, ration_id, start_day, end_day):
    # [start_day,end_day) aralığındaki tarihsel rasyon yem maliyetini hesaplar.
    if end_day<=start_day:return 0.0
    s0=start_day.isoformat(); e0=end_day.isoformat()
    # Rasyon miktarı veya ilgili yem fiyatı değiştiği gün yeni maliyet dönemi başlar.
    feed_ids=[int(r['feed_id']) for r in c.execute('select distinct feed_id from ration_item_history where ration_id=?',(ration_id,)).fetchall()]
    bounds={start_day,end_day}
    for r in c.execute('select distinct effective_date from ration_item_history where ration_id=? and effective_date>? and effective_date<?',(ration_id,s0,e0)).fetchall():
        try:bounds.add(date.fromisoformat(r['effective_date'][:10]))
        except Exception:pass
    if feed_ids:
        ph=','.join('?'*len(feed_ids))
        rows=c.execute(f'select distinct effective_date from feed_prices where feed_id in ({ph}) and effective_date>? and effective_date<?',(*feed_ids,s0,e0)).fetchall()
        for r in rows:
            try:bounds.add(date.fromisoformat(r['effective_date'][:10]))
            except Exception:pass
    pts=sorted(bounds); total=0.0
    for a,b in zip(pts,pts[1:]):
        days=max(0,(b-a).days)
        if days: total += days*ration_cost_on_date(c,ration_id,a.isoformat())
    return total


def animal_paddock_intervals(c, a, start_day, end_day):
    # Hayvanın [start,end) dönemindeki padoklarını tarih aralıkları halinde döndürür.
    aid=int(a['id']); current_pid=a['paddock_id'] if 'paddock_id' in a.keys() else None
    rows=c.execute("select * from paddock_history where animal_source='animal' and animal_id=? order by moved_at,id",(aid,)).fetchall()
    # Başlangıç günündeki padoku bul.
    pid=current_pid
    before=[]; after=[]
    for r in rows:
        try:md=date.fromisoformat(str(r['moved_at'])[:10])
        except Exception:continue
        if md<=start_day: before.append((md,r))
        else: after.append((md,r))
    if before:
        pid=before[-1][1]['to_paddock_id']
    elif after:
        # İlk kayıt, hareket öncesindeki padoku da biliyor.
        pid=after[0][1]['from_paddock_id']
    intervals=[]; cur=start_day
    for md,r in after:
        if md>=end_day:break
        if md>cur:intervals.append((cur,md,pid))
        pid=r['to_paddock_id'];cur=max(cur,md)
    if cur<end_day:intervals.append((cur,end_day,pid))
    return intervals


def paddock_feed_cost_between(c, paddock_id, start_day, end_day, manual_daily_feed):
    # Padokta rasyon tanımlı dönemlerde rasyon, boşluklarda manuel sabit maliyet kullanılır.
    if end_day<=start_day:return 0.0,0,0
    if not paddock_id:
        days=(end_day-start_day).days
        return days*manual_daily_feed,0,days
    rows=c.execute('''select * from paddock_rations
        where paddock_id=? and start_date<? and (end_date is null or end_date='' or end_date>=?)
        order by start_date,id''',(paddock_id,end_day.isoformat(),start_day.isoformat())).fetchall()
    total=0.0;ration_days=0;manual_days=0;cur=start_day
    for pr in rows:
        try:rs=max(start_day,date.fromisoformat(pr['start_date'][:10]))
        except Exception:continue
        try:re=min(end_day,date.fromisoformat(pr['end_date'][:10])+timedelta(days=1)) if pr['end_date'] else end_day
        except Exception:re=end_day
        if re<=rs:continue
        if rs>cur:
            d=(rs-cur).days;total+=d*manual_daily_feed;manual_days+=d
        seg_start=max(cur,rs)
        if re>seg_start:
            d=(re-seg_start).days
            total+=ration_cost_between(c,int(pr['ration_id']),seg_start,re);ration_days+=d
            cur=max(cur,re)
        if cur>=end_day:break
    if cur<end_day:
        d=(end_day-cur).days;total+=d*manual_daily_feed;manual_days+=d
    return total,ration_days,manual_days


def animal_current_feed_context(a, con=None, on_date=None):
    own=con is None;c=con or db().__enter__()
    try:
        manual=float(a['daily_feed_cost'] or 0) if 'daily_feed_cost' in a.keys() else 0.0
        pid=a['paddock_id'] if 'paddock_id' in a.keys() else None
        d=(on_date or date.today().isoformat())[:10]
        if pid:
            pr=c.execute('''select pr.*,r.name ration_name from paddock_rations pr join rations r on r.id=pr.ration_id
                where pr.paddock_id=? and pr.start_date<=? and (pr.end_date is null or pr.end_date='' or pr.end_date>=?)
                order by pr.start_date desc,pr.id desc limit 1''',(pid,d,d)).fetchone()
            if pr:
                return {'feed_cost':ration_cost_on_date(c,int(pr['ration_id']),d),'source':'ration','ration_name':pr['ration_name'],'start_date':pr['start_date'],'paddock_id':pid}
        return {'feed_cost':manual,'source':'manual','ration_name':'','start_date':'','paddock_id':pid}
    finally:
        if own:c.close()


def animal_cost_values(a, con=None):
    purchase=float(a['purchase_price'] or 0) if 'purchase_price' in a.keys() else 0.0
    manual_feed=float(a['daily_feed_cost'] or 0) if 'daily_feed_cost' in a.keys() else 0.0
    care=float(a['daily_care_cost'] or 0) if 'daily_care_cost' in a.keys() else 0.0
    start=(a['purchase_date'] if 'purchase_date' in a.keys() else '') or (a['birth_date'] if 'birth_date' in a.keys() else '')
    status=str(a['status'] or 'Aktif') if 'status' in a.keys() else 'Aktif'
    exit_date=(a['exit_date'] if 'exit_date' in a.keys() else '') or ''
    try:
        start_date=date.fromisoformat(start);end_date=date.today()
        if status!='Aktif' and exit_date:end_date=min(date.today(),date.fromisoformat(exit_date))
        days=max(0,(end_date-start_date).days)
    except Exception:
        days=0;start_date=end_date=date.today()
    own=con is None;c=con or db().__enter__()
    try:
        feed_acc=0.0
        for a0,b0,pid in animal_paddock_intervals(c,a,start_date,end_date):
            part,_,_=paddock_feed_cost_between(c,pid,a0,b0,manual_feed);feed_acc+=part
        accumulated=feed_acc + days*care
        ctx=animal_current_feed_context(a,c,end_date.isoformat())
        daily=float(ctx['feed_cost'])+care
        return days,daily,accumulated,purchase+accumulated
    finally:
        if own:c.close()


def pregnancy_vaccine_tasks(con, animal_id=None, horizon_days=7):
    # Aktif gebelikler için 7. ve 8. ay aşı görevlerini üretir.
    params=[]
    where="a.gender='Dişi' and coalesce(a.status,'Aktif')='Aktif'"
    if animal_id is not None:
        where+=' and a.id=?'; params.append(animal_id)
    rows=con.execute(f'''select i.*,a.tag,a.nickname,a.status
        from inseminations i join animals a on a.id=i.animal_id
        where {where}
        order by i.animal_id,i.insemination_date desc,i.id desc''',params).fetchall()
    latest_by_animal={}
    for r in rows:
        if r['animal_id'] not in latest_by_animal:
            latest_by_animal[r['animal_id']]=r
    today=date.today(); horizon=today+timedelta(days=horizon_days)
    tasks=[]
    for r in latest_by_animal.values():
        if not is_pregnant_value(r['pregnancy_result']):
            continue
        try:
            insemination_day=date.fromisoformat(r['insemination_date'])
            due_day=date.fromisoformat(r['due_date']) if r['due_date'] else insemination_day+timedelta(days=280)
        except Exception:
            continue
        if due_day < today:
            continue
        for month,offset in ((7,210),(8,240)):
            task_day=insemination_day+timedelta(days=offset)
            if task_day>horizon:
                continue
            token=f'GEBELIK_ASI|{r["id"]}|{month}'
            done=con.execute("select 1 from health where animal_id=? and notes like ? limit 1",(r['animal_id'],token+'%')).fetchone()
            if done:
                continue
            days_left=(task_day-today).days
            tasks.append({'animal_id':r['animal_id'],'insemination_id':r['id'],'tag':r['tag'],'nickname':r['nickname'],'month':month,'task_date':task_day.isoformat(),'days_left':days_left,'token':token,'overdue':days_left<0,'today':days_left==0})
    return sorted(tasks,key=lambda x:(x['task_date'],x['tag']))


def setting_float(key, default):
    try:
        with db() as c:
            row=c.execute('select setting_value from settings where setting_key=?',(key,)).fetchone()
        return float(row['setting_value']) if row and row['setting_value'] not in (None,'') else float(default)
    except Exception:
        return float(default)


def current_feed_price(feed_id, con=None, on_date=None):
    own=con is None
    c=con or db().__enter__()
    try:
        d=(on_date or date.today().isoformat())[:10]
        r=c.execute("select price_per_kg from feed_prices where feed_id=? and effective_date<=? order by effective_date desc,id desc limit 1",(feed_id,d)).fetchone()
        return float(r['price_per_kg'] or 0) if r else 0.0
    finally:
        if own:c.close()

def feed_stock_kg(feed_id, con=None):
    own=con is None
    c=con or db().__enter__()
    try:
        r=c.execute("select coalesce(sum(case when tx_type in ('Giriş','Sayım +') then quantity_kg when tx_type in ('Çıkış','Tüketim','Sayım -') then -quantity_kg else 0 end),0) qty from feed_stock_transactions where feed_id=?",(feed_id,)).fetchone()
        return float(r['qty'] or 0)
    finally:
        if own:c.close()

def feed_group(feed):
    """Rasyon kaba/kesif oranı için pratik yem grubu sınıflaması.
    Mineral/katkılar oran hesabına dahil edilmez. Katalog kategorileri eski Excel'de
    tek tip geldiği için isim + NDF tabanlı güvenli bir ön sınıflama kullanılır.
    """
    name=str(feed['name'] or '').upper()
    ndf=float(feed['ndf_pct'] or 0)
    additive_words=('TUZ','FOSFAT','KİREÇ','KIREC','PREMİKS','PREMIKS','MİNERAL','MINERAL','SODYUM BİKARBONAT','SODYUM BIKARBONAT','AMONYUM','ÜRE','URE')
    if any(w in name for w in additive_words): return 'Katkı'
    rough_words=('SAMAN','SİLAJ','SILAJ','KURU OT','YONCA','MERA','ÇAYIR','OTU','HASIL','FİĞ','FIG','ÇİM','CIM')
    concentrate_words=('YEMİ','YEMI','KÜSPE','KUSPE','SOYA','KANOLA','AYÇİÇEĞİ','AYCICEGI','ARPA,','MISIR,','MISIR DANE','MISIR KIRMA','BUĞDAY,','BUGDAY,','KEPEK','MELAS','FLAKED','PULU')
    if any(w in name for w in rough_words): return 'Kaba'
    if any(w in name for w in concentrate_words): return 'Kesif'
    return 'Kaba' if ndf>=35 else 'Kesif'

def ration_summary(ration_id, con=None):
    own=con is None
    c=con or db().__enter__()
    try:
        sql="""select ri.id item_id,ri.kg_per_head_day,f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price
                 from ration_items ri join feed_catalog f on f.id=ri.feed_id where ri.ration_id=? order by f.name"""
        rows=c.execute(sql,(date.today().isoformat(),ration_id)).fetchall()
        out={'as_fed_kg':0.0,'dm_kg':0.0,'cp_kg':0.0,'ndf_kg':0.0,'tdn_kg':0.0,'me_mcal':0.0,'ca_g':0.0,'p_g':0.0,'cost':0.0,'roughage_dm_kg':0.0,'concentrate_dm_kg':0.0,'additive_dm_kg':0.0,'items':rows}
        for r in rows:
            kg=float(r['kg_per_head_day'] or 0); dm=kg*float(r['dm_pct'] or 0)/100.0
            out['as_fed_kg']+=kg; out['dm_kg']+=dm
            out['cp_kg']+=dm*float(r['cp_pct'] or 0)/100.0
            out['ndf_kg']+=dm*float(r['ndf_pct'] or 0)/100.0
            out['tdn_kg']+=dm*float(r['tdn_pct'] or 0)/100.0
            out['me_mcal']+=dm*float(r['me_mcal_kg'] or 0)
            out['ca_g']+=dm*float(r['ca_pct'] or 0)*10.0
            out['p_g']+=dm*float(r['p_pct'] or 0)*10.0
            out['cost']+=kg*float(r['price'] or 0)
            grp=feed_group(r)
            if grp=='Kaba': out['roughage_dm_kg']+=dm
            elif grp=='Kesif': out['concentrate_dm_kg']+=dm
            else: out['additive_dm_kg']+=dm
        out['cp_pct_dm']=(out['cp_kg']/out['dm_kg']*100) if out['dm_kg'] else 0.0
        out['ndf_pct_dm']=(out['ndf_kg']/out['dm_kg']*100) if out['dm_kg'] else 0.0
        out['me_per_kg_dm']=(out['me_mcal']/out['dm_kg']) if out['dm_kg'] else 0.0
        rc_dm=out['roughage_dm_kg']+out['concentrate_dm_kg']
        out['roughage_pct_dm']=(out['roughage_dm_kg']/rc_dm*100) if rc_dm else 0.0
        out['concentrate_pct_dm']=(out['concentrate_dm_kg']/rc_dm*100) if rc_dm else 0.0
        return out
    finally:
        if own:c.close()

def ration_requirement_targets(weight_kg=450.0, target_adg=1.3, animal_type='Besi Erkek'):
    w=max(150.0,min(float(weight_kg or 450),900.0)); adg=max(0.2,min(float(target_adg or 1.3),2.2))
    dmi_pct=max(2.0,min(2.8,2.55-0.00055*(w-400)+0.10*(adg-1.0))); dmi_kg=w*dmi_pct/100.0
    cp_pct=max(9.0,min(15.0,10.2+2.2*(adg-1.0)+0.002*(500-w)))
    tdn_pct=max(60.0,min(78.0,66.0+8.0*(adg-0.8)-0.004*(w-450))); me_mcal_kg=tdn_pct*0.03615
    ca_pct=max(0.30,min(0.70,0.42+0.10*(adg-1.0))); p_pct=max(0.20,min(0.40,0.24+0.05*(adg-1.0)))
    rough_target=max(30.0,min(60.0,50.0-15.0*(adg-1.0))); rough_min=max(25.0,rough_target-10.0); rough_max=min(65.0,rough_target+10.0)
    return {'mode':'Besi','weight_kg':w,'adg':adg,'dmi_pct_bw':dmi_pct,'dmi_kg':dmi_kg,'cp_pct':cp_pct,'tdn_pct':tdn_pct,'me_mcal_kg':me_mcal_kg,'me_mcal_day':me_mcal_kg*dmi_kg,'ca_g':dmi_kg*ca_pct*10,'p_g':dmi_kg*p_pct*10,'ca_pct':ca_pct,'p_pct':p_pct,'ndf_min':25.0,'ndf_max':40.0,'roughage_min':rough_min,'roughage_max':rough_max}

def dairy_requirement_targets(weight_kg=650.0, target_milk_l=25.0, milk_fat_pct=3.8, milk_protein_pct=3.2):
    """Sağmal inek için kolay kullanımlı ön değerlendirme hedefi; reçete değildir."""
    w=max(350.0,min(float(weight_kg or 650),900.0)); milk=max(0.0,min(float(target_milk_l or 25),70.0))
    fat=max(2.5,min(float(milk_fat_pct or 3.8),6.5)); prot=max(2.5,min(float(milk_protein_pct or 3.2),5.0))
    dmi_kg=max(w*0.020,min(w*0.045,w*0.025+milk*0.30))
    lactose=4.8; milk_nel=0.0929*fat+0.0563*prot+0.0395*lactose; maintenance_nel=0.080*(w**0.75)
    me_day=(maintenance_nel+milk*milk_nel)/0.64
    cp_pct=max(15.0,min(18.5,14.5+milk*0.08)); ca_pct=max(0.60,min(0.90,0.62+milk*0.004)); p_pct=max(0.34,min(0.46,0.34+milk*0.0022))
    rough_target=max(45.0,min(60.0,55.0-0.5*max(0.0,milk-20.0))); rough_min=max(40.0,rough_target-7.5); rough_max=min(65.0,rough_target+7.5)
    return {'mode':'Süt','weight_kg':w,'milk_l':milk,'milk_fat_pct':fat,'milk_protein_pct':prot,'dmi_pct_bw':dmi_kg/w*100,'dmi_kg':dmi_kg,'cp_pct':cp_pct,'me_mcal_day':me_day,'me_mcal_kg':me_day/max(dmi_kg,.01),'ca_g':dmi_kg*ca_pct*10,'p_g':dmi_kg*p_pct*10,'ca_pct':ca_pct,'p_pct':p_pct,'ndf_min':28.0,'ndf_max':34.0,'roughage_min':rough_min,'roughage_max':rough_max}

def ration_targets_for_record(rr):
    typ=(rr['ration_type'] if 'ration_type' in rr.keys() and rr['ration_type'] else 'Besi').strip()
    if typ.lower().startswith(('süt','sut')):
        return dairy_requirement_targets(rr['target_weight_kg'],rr['target_milk_l'],rr['milk_fat_pct'],rr['milk_protein_pct'])
    return ration_requirement_targets(rr['target_weight_kg'],rr['target_adg_kg'],rr['animal_type'])

def is_real_protein_feed(feed):
    """Gerçek yem proteini ile NPN/mineral eşdeğerlerini ayırır.
    Protein önerisi için yalnız besleyici yem hammaddeleri kullanılır.
    """
    name=str(feed['name'] or '').upper()
    cp=float(feed['cp_pct'] or 0); me=float(feed['me_mcal_kg'] or 0); tdn=float(feed['tdn_pct'] or 0); ash=float(feed['ash_pct'] or 0) if 'ash_pct' in feed.keys() else 0.0
    blocked=('AMONYUM','ÜRE','URE','BİÜRE','BIURE','NPN','FOSFAT','KİREÇ','KIREC','TUZ','SODYUM BİKARBONAT','SODYUM BIKARBONAT')
    if any(x in name for x in blocked): return False
    # %100'ün üstündeki HP değerleri çoğunlukla NPN protein eşdeğeridir.
    if cp<=0 or cp>70: return False
    if me<=0 and tdn<=0: return False
    if ash>=35: return False
    return True

def nutrient_status(actual,target,tol=0.05):
    if target<=0:return ('-', 'mut')
    ratio=actual/target
    if ratio < 1-tol:return (f'⚠️ Eksik %{(1-ratio)*100:.0f}','red')
    if ratio > 1+tol:return (f'⬆️ Fazla %{(ratio-1)*100:.0f}','orange')
    return ('✅ Uygun','preg pos')

def ration_requirement_panel(rr,sm):
    t=ration_targets_for_record(rr)
    cp_s,cp_c=nutrient_status(sm['cp_pct_dm'],t['cp_pct']); me_s,me_c=nutrient_status(sm['me_mcal'],t['me_mcal_day'],0.08); dm_s,dm_c=nutrient_status(sm['dm_kg'],t['dmi_kg'],0.10); ca_s,ca_c=nutrient_status(sm['ca_g'],t['ca_g'],0.10); p_s,p_c=nutrient_status(sm['p_g'],t['p_g'],0.10)
    ndf=sm['ndf_pct_dm']; ndf_s='✅ Uygun' if t['ndf_min']<=ndf<=t['ndf_max'] else ('⚠️ Düşük' if ndf<t['ndf_min'] else '⚠️ Yüksek')
    rough=sm.get('roughage_pct_dm',0); conc=sm.get('concentrate_pct_dm',0); rc_s='✅ Uygun' if t['roughage_min']<=rough<=t['roughage_max'] else ('⚠️ Kaba yem düşük' if rough<t['roughage_min'] else '⚠️ Kaba yem yüksek')
    if t['mode']=='Süt':
        form_fields=f"""<input type='hidden' name='ration_type' value='Süt'><label>Canlı Ağırlık (kg)<input type='number' min='350' max='900' step='1' name='target_weight_kg' value='{t['weight_kg']:.0f}'></label><label>Hedef Süt (L/gün)<input type='number' min='0' max='70' step='0.5' name='target_milk_l' value='{t['milk_l']:.1f}'></label><details class='target-more'><summary>🥛 Gelişmiş</summary><div class='target-more-grid'><label>Süt Yağı %<input type='number' min='2.5' max='6.5' step='0.1' name='milk_fat_pct' value='{t['milk_fat_pct']:.1f}'></label><label>Süt Proteini %<input type='number' min='2.5' max='5' step='0.1' name='milk_protein_pct' value='{t['milk_protein_pct']:.1f}'></label></div></details>"""
        title='🥛 Akıllı Süt Rasyonu Hedefi'; ctx=f"<div class='target-context compact'><b>{t['weight_kg']:.0f} kg</b> · hedef <b>{t['milk_l']:.1f} L/gün süt</b></div>"
    else:
        at=h(rr['animal_type'] or 'Besi Erkek')
        form_fields=f"""<input type='hidden' name='ration_type' value='Besi'><label>Canlı Ağırlık (kg)<input type='number' min='150' max='900' step='1' name='target_weight_kg' value='{t['weight_kg']:.0f}'></label><label>Hedef Artış (kg/gün)<input type='number' min='0.2' max='2.2' step='0.05' name='target_adg_kg' value='{t['adg']:.2f}'></label><label>Hayvan Tipi<input name='animal_type' value='{at}'></label>"""
        title='🎯 Akıllı Besi Rasyonu Hedefi'; ctx=f"<div class='target-context compact'><b>{t['weight_kg']:.0f} kg</b> · hedef <b>{t['adg']:.2f} kg/gün artış</b></div>"
    def diff_text(actual,target,unit='',digits=1):
        if not target:return ''
        d=float(actual)-float(target); pct=d/float(target)*100; sign='+' if d>0 else ''
        return f"{sign}{d:.{digits}f}{unit} ({sign}{pct:.0f}%)"
    def box(key,label,current,target,status,diff=''):
        cls='ok' if 'Uygun' in status else 'warn'
        return f"<div class='nutri-mini {cls}' id='target-mini-{key}'><span>{label}</span><b id='target-mini-{key}-current'>{current}</b><small>{target}</small><i class='nutri-diff' id='target-mini-{key}-diff'>{diff}</i><em id='target-mini-{key}-status'>{status}</em></div>"
    mini=''.join([
        box('dm','KM',f"{sm['dm_kg']:.2f} kg",f"Hedef {t['dmi_kg']:.2f}",dm_s,diff_text(sm['dm_kg'],t['dmi_kg'],' kg',2)),
        box('cp','HP',f"%{sm['cp_pct_dm']:.1f}",f"Hedef %{t['cp_pct']:.1f}",cp_s,diff_text(sm['cp_pct_dm'],t['cp_pct'],' puan',1)),
        box('me','ME',f"{sm['me_mcal']:.1f}",f"Hedef {t['me_mcal_day']:.1f} Mcal",me_s,diff_text(sm['me_mcal'],t['me_mcal_day'],' Mcal',1)),
        box('ndf','NDF',f"%{ndf:.1f}",f"Hedef %{t['ndf_min']:.0f}–{t['ndf_max']:.0f}",ndf_s,'Aralık içi' if t['ndf_min']<=ndf<=t['ndf_max'] else ('Alt sınırın altında' if ndf<t['ndf_min'] else 'Üst sınırın üzerinde')),
        box('ca','Ca',f"{sm['ca_g']:.0f} g",f"Hedef {t['ca_g']:.0f} g",ca_s,diff_text(sm['ca_g'],t['ca_g'],' g',0)),
        box('p','P',f"{sm['p_g']:.0f} g",f"Hedef {t['p_g']:.0f} g",p_s,diff_text(sm['p_g'],t['p_g'],' g',0)),
        box('rc','Kaba/Kesif',f"%{rough:.0f} / %{conc:.0f}",f"Kaba %{t['roughage_min']:.0f}–{t['roughage_max']:.0f}",rc_s,'Aralık içi' if t['roughage_min']<=rough<=t['roughage_max'] else ('Kaba yem düşük' if rough<t['roughage_min'] else 'Kaba yem yüksek')),
        box('cost','Maliyet',money(sm['cost']),f"Kaydedilmiş {money(sm['cost'])}",'💰 Canlı','Değişiklik yok'),
    ])
    detail=f"""<details class='nutri-detail'><summary>📋 Besin detaylarını göster</summary><div class='table-compact-wrap'><table class='ration-target-table compact-table zebra'><thead><tr><th>Besin</th><th>Hedef</th><th>Mevcut</th><th>Durum</th></tr></thead><tbody><tr><td>Kuru Madde</td><td>{t['dmi_kg']:.2f} kg/gün</td><td>{sm['dm_kg']:.2f} kg</td><td>{dm_s}</td></tr><tr><td>Ham Protein</td><td>%{t['cp_pct']:.1f} KM</td><td>%{sm['cp_pct_dm']:.1f} KM</td><td>{cp_s}</td></tr><tr><td>Metabolik Enerji</td><td>{t['me_mcal_day']:.1f} Mcal/gün</td><td>{sm['me_mcal']:.1f} Mcal</td><td>{me_s}</td></tr><tr><td>NDF</td><td>%{t['ndf_min']:.0f}–{t['ndf_max']:.0f}</td><td>%{ndf:.1f}</td><td>{ndf_s}</td></tr><tr><td>Kalsiyum</td><td>{t['ca_g']:.0f} g</td><td>{sm['ca_g']:.0f} g</td><td>{ca_s}</td></tr><tr><td>Fosfor</td><td>{t['p_g']:.0f} g</td><td>{sm['p_g']:.0f} g</td><td>{p_s}</td></tr><tr><td>Kaba/Kesif</td><td>Kaba %{t['roughage_min']:.0f}–{t['roughage_max']:.0f}</td><td>%{rough:.0f} / %{conc:.0f}</td><td>{rc_s}</td></tr></tbody></table></div></details>"""
    return f"""<div class='target-workspace'><div class='target-controlbar'><div class='target-head'><h3>{title}</h3>{ctx}</div><form method='post' action='/ration/target' class='target-form'><input type='hidden' name='ration_id' value='{rr['id']}'>{form_fields}<button class='btn blue compact-target-btn'>Güncelle</button></form></div><div class='target-compare-sticky'><div class='target-compare-title'><b>🎯 Hedef ↔ Mevcut</b><span id='target-live-note'>Çalışma masasıyla canlı bağlı</span></div><div class='nutri-mini-grid'>{mini}</div></div></div>"""

def ration_smart_recommendations(rr, sm, con=None, limit=6):
    """Katalogdaki yemleri mevcut besin açıklarını iyileştirme potansiyeline göre sıralar.
    Bu bir karar-destek simülasyonudur; reçete değildir."""
    own=con is None; c=con or db().__enter__()
    try:
        t=ration_targets_for_record(rr)
        deficits={
            'dm':max(0,t['dmi_kg']-sm['dm_kg'])/max(t['dmi_kg'],.01),
            'cp':max(0,t['cp_pct']-sm['cp_pct_dm'])/max(t['cp_pct'],.01),
            'me':max(0,t['me_mcal_day']-sm['me_mcal'])/max(t['me_mcal_day'],.01),
            'ca':max(0,t['ca_g']-sm['ca_g'])/max(t['ca_g'],.01),
            'p':max(0,t['p_g']-sm['p_g'])/max(t['p_g'],.01),
        }
        rows=c.execute("""select f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price from feed_catalog f where f.active=1""",(date.today().isoformat(),)).fetchall()
        out=[]
        for f in rows:
            dm=float(f['dm_pct'] or 0)/100; cp=float(f['cp_pct'] or 0)/100; ndf=float(f['ndf_pct'] or 0)/100; me=float(f['me_mcal_kg'] or 0); ca=float(f['ca_pct'] or 0); ph=float(f['p_pct'] or 0)
            if dm<=0: continue
            # 1 kg yaş yem katkısının açık kapatma yönündeki göreli puanı
            protein_factor=(dm*cp*5 if is_real_protein_feed(f) else 0.0)
            score=(deficits['dm']*dm + deficits['cp']*protein_factor + deficits['me']*dm*me/3 + deficits['ca']*dm*ca/1.0 + deficits['p']*dm*ph/0.6)
            # NDF zaten yüksekse yüksek-NDF yemleri; protein zaten fazlaysa çok proteinli yemleri geri it
            if sm['ndf_pct_dm']>t['ndf_max'] and float(f['ndf_pct'] or 0)>40: score*=0.55
            if sm['cp_pct_dm']>t['cp_pct']*1.05 and float(f['cp_pct'] or 0)>18: score*=0.60
            if score<=0: continue
            price=float(f['price'] or 0); value=score/(1+(price/20 if price>0 else .15))
            reasons=[]
            if deficits['me']>.03 and me>=2.3: reasons.append('enerji')
            if deficits['cp']>.03 and is_real_protein_feed(f) and float(f['cp_pct'] or 0)>=14: reasons.append('protein')
            if deficits['dm']>.05: reasons.append('kuru madde')
            if deficits['ca']>.05 and ca>=.5: reasons.append('kalsiyum')
            if deficits['p']>.05 and ph>=.3: reasons.append('fosfor')
            out.append((value,f,', '.join(reasons) or 'denge'))
        out.sort(key=lambda x:x[0],reverse=True)
        return out[:limit]
    finally:
        if own:c.close()

def ration_balance_error(targets, sm):
    """Rasyonu hedefe uzaklığına göre puanlar. Daha düşük daha iyidir.
    Bu skor reçete değildir; öneri sıralamasında karar desteği için kullanılır."""
    def rel(actual, target):
        return abs(float(actual)-float(target))/max(abs(float(target)), 0.01)
    score=0.0
    score += rel(sm.get('dm_kg',0), targets['dmi_kg'])*1.10
    score += rel(sm.get('cp_pct_dm',0), targets['cp_pct'])*1.20
    score += rel(sm.get('me_mcal',0), targets['me_mcal_day'])*1.45
    score += rel(sm.get('ca_g',0), targets['ca_g'])*0.65
    score += rel(sm.get('p_g',0), targets['p_g'])*0.65
    ndf=float(sm.get('ndf_pct_dm',0) or 0)
    if ndf < targets['ndf_min']:
        score += (targets['ndf_min']-ndf)/max(targets['ndf_min'],1)*1.10
    elif ndf > targets['ndf_max']:
        score += (ndf-targets['ndf_max'])/max(targets['ndf_max'],1)*1.10
    rough=float(sm.get('roughage_pct_dm',0) or 0)
    if rough < targets.get('roughage_min',0):
        score += (targets['roughage_min']-rough)/max(targets['roughage_min'],1)*0.90
    elif rough > targets.get('roughage_max',100):
        score += (rough-targets['roughage_max'])/max(targets['roughage_max'],1)*0.90
    return score

def ration_reduction_recommendations(rr, sm, con=None, limit=6):
    """Mevcut rasyondaki fazlalıkları azaltmaya yardımcı olabilecek yem/miktarları sıralar."""
    own=con is None; c=con or db().__enter__()
    try:
        t=ration_targets_for_record(rr)
        base_err=ration_balance_error(t,sm); out=[]
        for it in sm['items']:
            current=float(it['kg_per_head_day'] or 0)
            if current <= 0.05: continue
            best=None
            for step in (0.25,0.50,1.00):
                delta=-min(step,current)
                if current+delta < -0.001: continue
                ss=ration_simulated_summary(rr['id'],it['id'] if False else it['id'],delta,c)
                err=ration_balance_error(t,ss); improve=base_err-err
                if improve <= 0.0005: continue
                reasons=[]
                if sm['cp_pct_dm']>t['cp_pct']*1.05 and float(it['cp_pct'] or 0)>=t['cp_pct']: reasons.append('proteini düşürür')
                if sm['ca_g']>t['ca_g']*1.10 and float(it['ca_pct'] or 0)>=0.35: reasons.append('kalsiyumu düşürür')
                if sm['p_g']>t['p_g']*1.10 and float(it['p_pct'] or 0)>=0.25: reasons.append('fosforu düşürür')
                if sm['ndf_pct_dm']>t['ndf_max'] and float(it['ndf_pct'] or 0)>t['ndf_max']: reasons.append('NDF yükünü azaltır')
                # Bir değeri düzeltirken enerji/KM açığını büyütüyorsa cezalandır.
                warnings=[]
                if ss['me_mcal'] < t['me_mcal_day']*0.92: warnings.append('enerji düşebilir')
                if ss['dm_kg'] < t['dmi_kg']*0.90: warnings.append('KM düşebilir')
                candidate=(improve, it, delta, ', '.join(reasons) or 'genel dengeyi iyileştirir', ', '.join(warnings), ss)
                if best is None or candidate[0]>best[0]: best=candidate
            if best: out.append(best)
        out.sort(key=lambda x:x[0],reverse=True)
        return out[:limit]
    finally:
        if own:c.close()

def ration_addition_recommendations(rr, sm, con=None, limit=30):
    """Tüm katalogdaki yemleri +0.50 kg simülasyonuyla değerlendirir ve hedefe yaklaştıranları sıralar."""
    own=con is None; c=con or db().__enter__()
    try:
        t=ration_targets_for_record(rr)
        base_err=ration_balance_error(t,sm)
        rows=c.execute("""select f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price,
            coalesce((select sum(case when st.tx_type in ('Giriş','Sayım +') then st.quantity_kg when st.tx_type in ('Çıkış','Tüketim','Sayım -') then -st.quantity_kg else 0 end) from feed_stock_transactions st where st.feed_id=f.id),0) stock
            from feed_catalog f where f.active=1""",(date.today().isoformat(),)).fetchall()
        out=[]
        for f in rows:
            if float(f['dm_pct'] or 0)<=0: continue
            ss=ration_simulated_summary(rr['id'],f['id'],0.50,c)
            err=ration_balance_error(t,ss); improve=base_err-err
            # HP açığı varsa gerçek protein hammaddelerini ayrıca hedefe göre puanla.
            # Böylece enerji zaten yüksek olsa bile soya/kanola/ayçiçeği gibi kaynaklar
            # çözüm adayı olarak görülebilir; NPN/mineral ürünleri protein diye önerilmez.
            targeted=0.0
            cp_gap=max(0.0,t['cp_pct']-sm['cp_pct_dm'])
            if cp_gap>0.15 and is_real_protein_feed(f):
                cp_gain=max(0.0,ss['cp_pct_dm']-sm['cp_pct_dm'])
                targeted += min(cp_gain/max(cp_gap,0.01),1.5)*0.90
                if sm['me_mcal']>t['me_mcal_day']*1.05 and ss['me_mcal']>sm['me_mcal']:
                    targeted -= ((ss['me_mcal']-sm['me_mcal'])/max(t['me_mcal_day'],0.1))*0.45
            rank_score=improve+targeted
            if rank_score<=0.0005: continue
            reasons=[]
            if sm['me_mcal']<t['me_mcal_day']*0.98 and ss['me_mcal']>sm['me_mcal']: reasons.append('enerji açığını azaltır')
            if sm['cp_pct_dm']<t['cp_pct']*0.98 and is_real_protein_feed(f) and ss['cp_pct_dm']>sm['cp_pct_dm']+0.03: reasons.append('protein açığını azaltır')
            if sm['dm_kg']<t['dmi_kg']*0.95 and ss['dm_kg']>sm['dm_kg']: reasons.append('KM desteği')
            if sm['ca_g']<t['ca_g']*0.95 and ss['ca_g']>sm['ca_g']: reasons.append('Ca desteği')
            if sm['p_g']<t['p_g']*0.95 and ss['p_g']>sm['p_g']: reasons.append('P desteği')
            warnings=[]
            if sm['cp_pct_dm']>t['cp_pct']*1.05 and ss['cp_pct_dm']>sm['cp_pct_dm']+0.05: warnings.append('proteini artırır')
            if sm['ca_g']>t['ca_g']*1.10 and ss['ca_g']>sm['ca_g']+1: warnings.append('Ca fazlasını artırır')
            if sm['p_g']>t['p_g']*1.10 and ss['p_g']>sm['p_g']+1: warnings.append('P fazlasını artırır')
            out.append((rank_score,f,', '.join(reasons) or 'genel dengeyi iyileştirir',', '.join(warnings),ss))
        # Önce denge katkısı; aynı katkıda fiyatı bilinen ve daha ucuz olan öne gelsin.
        out.sort(key=lambda x:(x[0], 1 if float(x[1]['price'] or 0)>0 else 0, -float(x[1]['price'] or 999999)),reverse=True)
        return out[:limit]
    finally:
        if own:c.close()

def ration_simulated_multi_summary(ration_id, changes, con=None):
    """Birden fazla yem değişikliğini kaydetmeden aynı rasyon üzerinde birlikte simüle eder."""
    own=con is None; c=con or db().__enter__()
    try:
        base=ration_summary(ration_id,c)
        out={k:v for k,v in base.items() if k!='items'}; out['items']=base['items']
        for feed_id,delta_kg in changes:
            f=c.execute("""select f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price from feed_catalog f where f.id=?""",(date.today().isoformat(),int(feed_id))).fetchone()
            if not f: continue
            kg=float(delta_kg or 0); dm=kg*float(f['dm_pct'] or 0)/100
            out['as_fed_kg']+=kg; out['dm_kg']+=dm; out['cp_kg']+=dm*float(f['cp_pct'] or 0)/100; out['ndf_kg']+=dm*float(f['ndf_pct'] or 0)/100; out['tdn_kg']+=dm*float(f['tdn_pct'] or 0)/100; out['me_mcal']+=dm*float(f['me_mcal_kg'] or 0); out['ca_g']+=dm*float(f['ca_pct'] or 0)*10; out['p_g']+=dm*float(f['p_pct'] or 0)*10; out['cost']+=kg*float(f['price'] or 0)
            grp=feed_group(f)
            if grp=='Kaba': out['roughage_dm_kg']=out.get('roughage_dm_kg',0)+dm
            elif grp=='Kesif': out['concentrate_dm_kg']=out.get('concentrate_dm_kg',0)+dm
            else: out['additive_dm_kg']=out.get('additive_dm_kg',0)+dm
        for key in ('as_fed_kg','dm_kg','cp_kg','ndf_kg','me_mcal','ca_g','p_g','cost','roughage_dm_kg','concentrate_dm_kg'):
            if key in out: out[key]=max(0.0,float(out[key] or 0))
        out['cp_pct_dm']=out['cp_kg']/out['dm_kg']*100 if out['dm_kg'] else 0; out['ndf_pct_dm']=out['ndf_kg']/out['dm_kg']*100 if out['dm_kg'] else 0; out['me_per_kg_dm']=out['me_mcal']/out['dm_kg'] if out['dm_kg'] else 0
        rc=out.get('roughage_dm_kg',0)+out.get('concentrate_dm_kg',0); out['roughage_pct_dm']=out.get('roughage_dm_kg',0)/rc*100 if rc else 0; out['concentrate_pct_dm']=out.get('concentrate_dm_kg',0)/rc*100 if rc else 0
        return out
    finally:
        if own:c.close()

def ration_effect_text(targets,before,after,max_items=3):
    """Öneriyi ölçülebilir ve kısa bir dille açıklar."""
    impacts=[]
    metrics=[('HP',before['cp_pct_dm'],after['cp_pct_dm'],targets['cp_pct'],'%{:.1f}'),('Enerji',before['me_mcal'],after['me_mcal'],targets['me_mcal_day'],'{:.1f} Mcal'),('KM',before['dm_kg'],after['dm_kg'],targets['dmi_kg'],'{:.2f} kg'),('Ca',before['ca_g'],after['ca_g'],targets['ca_g'],'{:.0f} g'),('P',before['p_g'],after['p_g'],targets['p_g'],'{:.0f} g')]
    for name,b,a,t,fmt in metrics:
        if t<=0: continue
        gain=abs(b-t)/t-abs(a-t)/t
        if gain>0.01: impacts.append((gain,f"{name} {fmt.format(b)} → {fmt.format(a)}"))
    def add_range(name,b,a,lo,hi,fmt):
        def dist(x): return (lo-x)/max(lo,1) if x<lo else (x-hi)/max(hi,1) if x>hi else 0
        gain=dist(b)-dist(a)
        if gain>0.01: impacts.append((gain,f"{name} {fmt.format(b)} → {fmt.format(a)}"))
    add_range('NDF',before['ndf_pct_dm'],after['ndf_pct_dm'],targets['ndf_min'],targets['ndf_max'],'%{:.1f}')
    add_range('Kaba',before.get('roughage_pct_dm',0),after.get('roughage_pct_dm',0),targets.get('roughage_min',0),targets.get('roughage_max',100),'%{:.0f}')
    impacts.sort(key=lambda x:x[0],reverse=True)
    return ' · '.join(x[1] for x in impacts[:max_items]) or 'Genel denge hedefe yaklaşıyor'

def ration_combined_recommendations(rr, sm, reductions, additions, limit=5):
    """Azalt + ekle çiftlerini gerçek birlikte simülasyonla puanlar."""
    t=ration_targets_for_record(rr); base_err=ration_balance_error(t,sm); out=[]
    for red in reductions[:5]:
        for add in additions[:12]:
            if int(red[1]['id'])==int(add[1]['id']): continue
            ss=ration_simulated_multi_summary(rr['id'],[(red[1]['id'],red[2]),(add[1]['id'],0.50)])
            improve=base_err-ration_balance_error(t,ss)
            if improve<=0.0005: continue
            effect=ration_effect_text(t,sm,ss,3)
            out.append((improve,red,add,ss,effect))
    out.sort(key=lambda x:(x[0],-float(x[3].get('cost',999999))),reverse=True)
    return out[:limit]

def ration_simulated_summary(ration_id, feed_id, delta_kg, con=None):
    own=con is None; c=con or db().__enter__()
    try:
        base=ration_summary(ration_id,c); out={k:v for k,v in base.items() if k!='items'}; out['items']=base['items']
        f=c.execute("""select f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price from feed_catalog f where f.id=?""",(date.today().isoformat(),feed_id)).fetchone()
        if not f:return base
        kg=float(delta_kg); dm=kg*float(f['dm_pct'] or 0)/100
        out['as_fed_kg']+=kg; out['dm_kg']+=dm; out['cp_kg']+=dm*float(f['cp_pct'] or 0)/100; out['ndf_kg']+=dm*float(f['ndf_pct'] or 0)/100; out['tdn_kg']+=dm*float(f['tdn_pct'] or 0)/100; out['me_mcal']+=dm*float(f['me_mcal_kg'] or 0); out['ca_g']+=dm*float(f['ca_pct'] or 0)*10; out['p_g']+=dm*float(f['p_pct'] or 0)*10; out['cost']+=kg*float(f['price'] or 0)
        grp=feed_group(f)
        if grp=='Kaba': out['roughage_dm_kg']=out.get('roughage_dm_kg',0)+dm
        elif grp=='Kesif': out['concentrate_dm_kg']=out.get('concentrate_dm_kg',0)+dm
        else: out['additive_dm_kg']=out.get('additive_dm_kg',0)+dm
        out['cp_pct_dm']=out['cp_kg']/out['dm_kg']*100 if out['dm_kg'] else 0; out['ndf_pct_dm']=out['ndf_kg']/out['dm_kg']*100 if out['dm_kg'] else 0; out['me_per_kg_dm']=out['me_mcal']/out['dm_kg'] if out['dm_kg'] else 0
        rc=out.get('roughage_dm_kg',0)+out.get('concentrate_dm_kg',0); out['roughage_pct_dm']=out.get('roughage_dm_kg',0)/rc*100 if rc else 0; out['concentrate_pct_dm']=out.get('concentrate_dm_kg',0)/rc*100 if rc else 0
        return out
    finally:
        if own:c.close()

def paddock_population(paddock_id, con=None):
    own=con is None
    c=con or db().__enter__()
    try:
        adults=c.execute("select count(*) n from animals where paddock_id=? and coalesce(status,'Aktif')='Aktif'",(paddock_id,)).fetchone()['n']
        calves=c.execute("select count(*) n from calves where paddock_id=? and promoted_animal_id is null",(paddock_id,)).fetchone()['n']
        return int(adults or 0)+int(calves or 0)
    finally:
        if own:c.close()

def sync_paddock_text(c, source, animal_id, paddock_id):
    name=''
    if paddock_id:
        r=c.execute('select name from paddocks where id=?',(paddock_id,)).fetchone(); name=r['name'] if r else ''
    table='animals' if source=='animal' else 'calves'
    c.execute(f'update {table} set paddock_id=?,paddock=? where id=?',(paddock_id or None,name,animal_id))

def male_weight_performance(animal_id, con=None):
    own=con is None
    c=con or db()
    try:
        rows=c.execute('select measure_date,weight,notes from weights where animal_id=? order by measure_date,id',(animal_id,)).fetchall()
        if len(rows)<2:
            return {'rows':rows,'gain':None,'days':0,'daily':None,'monthly':None,'status':'none'}
        prev,last=rows[-2],rows[-1]
        try: days=(date.fromisoformat(last['measure_date'])-date.fromisoformat(prev['measure_date'])).days
        except Exception: days=0
        gain=float(last['weight'])-float(prev['weight'])
        daily=gain/days if days>0 else None
        monthly=daily*30 if daily is not None else None
        target=setting_float('male_min_daily_gain',1.0)
        warn_ratio=setting_float('male_warning_ratio',0.90)
        if daily is None: status='none'
        elif daily < target*warn_ratio: status='low'
        elif daily < target: status='watch'
        else: status='good'
        return {'rows':rows,'previous':prev,'latest':last,'gain':gain,'days':days,'daily':daily,'monthly':monthly,'target':target,'status':status}
    finally:
        if own:c.close()

def weight_chart_svg(rows):
    if len(rows)<2:return '<p class="mut">Grafik için en az iki tartım kaydı gerekir.</p>'
    data=[]
    for r in rows:
        try:data.append((date.fromisoformat(r['measure_date']),float(r['weight'])))
        except Exception:pass
    if len(data)<2:return '<p class="mut">Geçerli tarih ve kilo verisi yetersiz.</p>'
    w,hgt,pad=720,240,42
    minv=min(v for _,v in data);maxv=max(v for _,v in data)
    if maxv==minv:maxv=minv+1
    span=max(1,(data[-1][0]-data[0][0]).days)
    pts=[]
    for d,v in data:
        x=pad+((d-data[0][0]).days/span)*(w-2*pad)
        y=hgt-pad-((v-minv)/(maxv-minv))*(hgt-2*pad)
        pts.append((x,y,d,v))
    poly=' '.join(f'{x:.1f},{y:.1f}' for x,y,_,_ in pts)
    grid=''.join(f'<line class="gridline" x1="{pad}" y1="{pad+i*(hgt-2*pad)/4:.1f}" x2="{w-pad}" y2="{pad+i*(hgt-2*pad)/4:.1f}"/>' for i in range(5))
    dots=''.join(f'<circle class="point" cx="{x:.1f}" cy="{y:.1f}" r="6"><title>{d.isoformat()} · {v:.1f} kg</title></circle>' for x,y,d,v in pts)
    labels=f'<text x="{pad}" y="{hgt-10}">{data[0][0].strftime("%d.%m.%Y")}</text><text x="{w-pad}" y="{hgt-10}" text-anchor="end">{data[-1][0].strftime("%d.%m.%Y")}</text><text x="8" y="{pad+4}">{maxv:.1f} kg</text><text x="8" y="{hgt-pad+4}">{minv:.1f} kg</text>'
    return f'<svg class="weight-chart" viewBox="0 0 {w} {hgt}" role="img" aria-label="Kilo gelişim grafiği">{grid}<line class="axis" x1="{pad}" y1="{hgt-pad}" x2="{w-pad}" y2="{hgt-pad}"/><polyline class="trend" points="{poly}"/>{dots}{labels}</svg>'

def promote_mature_calves():
    """10 ayını dolduran buzağıları yetişkin karta geçirir; geçmiş kayıtları korur."""
    with db() as c:
        rows=c.execute("select * from calves where promoted_animal_id is null and birth_date is not null and birth_date<>''").fetchall()
        for calf in rows:
            if months_old(calf['birth_date']) < 10: continue
            existing=c.execute('select id from animals where tag=?',(calf['tag'],)).fetchone()
            if existing: aid=existing['id']
            else:
                cur=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes,paddock,photo_url,sold_price,status,purchase_date,purchase_price) values(?,?,?,?,?,?,?,?,?,?,?,?)',
                    (calf['tag'],calf['nickname'] or '',calf['gender'] or '',calf['breed'] or '',calf['birth_date'],calf['notes'] or '',calf['paddock'] or '',calf['photo_url'] or '',0,'Aktif',calf['purchase_date'] or '',float(calf['purchase_price'] or 0)))
                aid=cur.lastrowid
            c.execute('update health set animal_id=?,calf_id=null where calf_id=?',(aid,calf['id']))
            for w in c.execute('select * from calf_weights where calf_id=? order by measure_date,id',(calf['id'],)).fetchall():
                if not c.execute('select 1 from weights where animal_id=? and measure_date=?',(aid,w['measure_date'])).fetchone():
                    c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',(aid,w['measure_date'],w['weight'],w['notes']))
            for ph in c.execute('select * from calf_photos where calf_id=? order by id',(calf['id'],)).fetchall():
                if not c.execute('select 1 from animal_photos where animal_id=? and filename=?',(aid,ph['filename'])).fetchone():
                    c.execute('insert into animal_photos(animal_id,filename,created_at,caption) values(?,?,?,?)',(aid,ph['filename'],ph['created_at'],ph['caption']))
            c.execute('update calves set promoted_animal_id=?,promoted_at=? where id=?',(aid,datetime.now().isoformat(timespec='seconds'),calf['id']))


NAV=[('Dashboard','/'),('📈 Besi Performansı','/performance'),('➕ Hayvan Ekle','/animal-add'),('Dişi Hayvanlar','/animals'),('Erkek Hayvanlar','/males'),('Satılan Hayvanlar','/archive/sold'),('Kesilen Hayvanlar','/archive/slaughtered'),('Buzağılar','/calves'),('Kızgınlık Takibi','/estrus'),('Tohumlama','/inseminations'),('Sağlık','/health'),('Finans','/finance'),('Raporlar','/reports'),('Veri Aktarımı','/data'),('💾 Yedekleme Merkezi','/backups'),('🔐 Şifremi Değiştir','/password-change')]
ADMIN_NAV=[('👥 Kullanıcı Yönetimi','/users'),('📜 İşlem Günlüğü','/audit-log')]

def page(title,body,path='/',user='admin',flash=''):
    try:
        with db() as c:account=c.execute('select role,full_name from users where username=?',(user,)).fetchone()
        role=account['role'] if account else 'personel';display=account['full_name'] if account and account['full_name'] else user
    except Exception:role='personel';display=user
    def nav_link(name,url):
        return f'<a class="{"on" if path==url else ""}" href="{url}">{name}</a>'
    groups=[
        ('🐄 Hayvanlar',[('Dişi Hayvanlar','/animals'),('Erkek Hayvanlar','/males'),('Buzağılar','/calves'),('Kesilen Hayvanlar','/archive/slaughtered'),('Satılan Hayvanlar','/archive/sold'),('➕ Hayvan Ekle','/animal-add')]),
        ('🐂 Besi',[('🏠 Padok Yönetimi','/paddocks'),('🌾 Yem Kataloğu','/feeds'),('🥣 Rasyon Yönetimi','/rations'),('Besi Performansı','/performance')]),
        ('🩺 Üreme & Sağlık',[('Kızgınlık Takibi','/estrus'),('Tohumlama','/inseminations'),('Sağlık','/health')]),
        ('💰 Finans',[('Finans','/finance'),('Raporlar','/reports')]),
        ('🗄️ Veri & Sistem',[('Veri Aktarımı','/data'),('💾 Yedekleme Merkezi','/backups')]),
        ('⚙️ Yönetim',[('🔐 Şifremi Değiştir','/password-change')]+([('🏡 Çiftlik Profili','/farm-profile'),('🔐 Lisans Bilgileri','/license-info'),('👥 Kullanıcı Yönetimi','/users'),('📜 İşlem Günlüğü','/audit-log')] if role=='admin' else []))
    ]
    nav=nav_link('🏠 Dashboard','/')
    for label,items in groups:
        active=any(path==url or (url=='/performance' and path.startswith('/performance')) for _,url in items)
        children=''.join(nav_link(name,url) for name,url in items)
        nav+=f'<details class="nav-group {"open-group" if active else ""}" {"open" if active else ""}><summary>{label}</summary><div class="nav-children">{children}</div></details>'
    fl=f'<div class="flash">{h(flash)}</div>' if flash else ''
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><style>{CSS}
/* V3.7.8 Finance Drawer Hotfix */
#financeDrawerBackdrop.finance-drawer-backdrop{{position:fixed!important;inset:0!important;z-index:2090!important;display:none!important;background:rgba(9,34,22,.42)!important;backdrop-filter:blur(2px)}}
#financeDrawerBackdrop.finance-drawer-backdrop.open{{display:block!important}}
#financeDrawer.finance-drawer{{position:fixed!important;top:0!important;right:0!important;bottom:0!important;left:auto!important;width:min(760px,94vw)!important;height:100dvh!important;max-width:none!important;margin:0!important;padding:0!important;z-index:2100!important;display:flex!important;flex-direction:column!important;background:#f5f8f6!important;border:0!important;border-radius:0!important;box-shadow:-22px 0 55px rgba(12,45,28,.24)!important;transform:translateX(105%)!important;visibility:hidden!important;pointer-events:none!important;transition:transform .24s ease,visibility 0s linear .24s!important;overflow:hidden!important}}
#financeDrawer.finance-drawer.open{{transform:translateX(0)!important;visibility:visible!important;pointer-events:auto!important;transition:transform .24s ease!important}}
#financeDrawer .finance-drawer-head{{display:flex!important;align-items:flex-start!important;justify-content:space-between!important;gap:16px!important;padding:22px 24px 17px!important;flex:0 0 auto!important;background:#fff!important;border-bottom:1px solid #dce8df!important}}
#financeDrawer .finance-drawer-close{{appearance:none!important;display:grid!important;place-items:center!important;width:42px!important;height:42px!important;min-width:42px!important;padding:0!important;margin:0!important;border:0!important;border-radius:50%!important;background:#e8f3ec!important;color:#126c3b!important;font:700 28px/1 Arial,sans-serif!important;cursor:pointer!important}}
#financeDrawer .finance-drawer-body{{flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;padding:18px 20px 36px!important}}
#financeDrawer .finance-entry-card{{margin:0!important;width:100%!important;box-sizing:border-box!important}}
#financeDrawer .bulk-list{{max-height:310px!important;overflow-y:auto!important}}
@media(max-width:700px){{#financeDrawer.finance-drawer{{width:100vw!important;max-width:100vw!important}}#financeDrawer .finance-drawer-head{{padding:16px!important}}#financeDrawer .finance-drawer-body{{padding:12px 12px 28px!important}}#financeDrawer .bulk-list{{max-height:42vh!important}}}}

.ration-new-collapsed>details>summary{{cursor:pointer}}.target-context{{background:#f4faf6;border:1px solid #d8e9dd;border-radius:10px;padding:10px 12px;margin-bottom:12px}}.smart-solution-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:12px}}.smart-solution{{border:1px solid #dce8df;background:#f8fbf9;border-radius:12px;padding:12px}}.smart-solution b{{display:block;color:#164f31}}.smart-solution small{{display:block;margin-top:4px;font-weight:700}}.smart-solution p{{margin:8px 0;font-size:13px}}.ration-section-collapse>details>summary,details>summary{{cursor:pointer}}@media(max-width:900px){{.smart-solution-grid{{grid-template-columns:1fr}}}}

.quick-feed-card:not([open]){{padding:11px 14px}}.quick-feed-card[open]{{position:fixed;z-index:95;left:max(210px,8vw);right:4vw;top:58px;bottom:4vh;background:#fff;overflow:auto;padding:14px 16px!important;border-radius:16px!important;box-shadow:0 24px 70px rgba(0,0,0,.28)!important}}.quick-feed-card[open]::before{{content:'';position:fixed;inset:0;background:rgba(8,38,23,.38);z-index:-1}}.quick-feed-card[open] .quick-feed-head{{position:sticky;top:-14px;z-index:3;background:#fff;padding:10px 0;border-bottom:1px solid #e2ece5}}.quick-feed-card[open] .quick-feed-results{{max-height:42vh}}.quick-feed-card:not([open]) .quick-feed-head{{min-height:28px}}.quick-feed-card:not([open]) .quick-feed-head .mut{{font-size:12px}}@media(max-width:820px){{.quick-feed-card[open]{{left:8px;right:8px;top:48px;bottom:8px}}}}.quick-feed-card{{padding:16px}}.quick-feed-head,.quick-feed-selected{{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}}.quick-feed-tools{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}}.quick-feed-tools>input{{flex:1;min-width:280px;padding:11px 13px;border:1px solid #cbd8cf;border-radius:10px}}.quick-feed-shortcuts{{display:flex;gap:6px;flex-wrap:wrap}}.quick-feed-results{{margin-top:10px;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;max-height:290px;overflow:auto}}.quick-feed-result{{border:1px solid #dce8df;background:#fff;border-radius:10px;padding:10px 12px;text-align:left;display:flex;justify-content:space-between;gap:12px;cursor:pointer;color:inherit}}.quick-feed-result:hover,.quick-feed-result.selected{{border-color:#23824a;background:#f0f8f3}}.quick-feed-result span{{display:flex;flex-direction:column;gap:3px}}.quick-feed-result small{{color:#66736b}}.quick-feed-side{{text-align:right;white-space:nowrap}}.quick-feed-selected{{margin-top:12px;padding:11px;background:#f6faf7;border:1px solid #dce8df;border-radius:10px}}.quick-feed-selected>div:first-child{{display:flex;flex-direction:column}}.quick-feed-selected .ration-stepper input{{width:92px}}@media(max-width:760px){{.quick-feed-results{{grid-template-columns:1fr}}.quick-feed-tools>input{{min-width:100%}}.quick-feed-selected{{align-items:stretch}}.quick-feed-selected .ration-stepper{{justify-content:center}}.quick-feed-selected .btn{{justify-content:center}}}}
.target-card{{padding:14px 16px}}.target-head{{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap}}.target-head h3{{margin:0}}.target-context.compact{{margin:0;padding:7px 10px;font-size:13px}}.target-form{{display:grid;grid-template-columns:repeat(3,minmax(140px,1fr)) auto;gap:8px;align-items:end;margin-top:10px}}.target-form label{{font-size:12px}}.target-form input,.target-form select{{padding:7px 9px}}.compact-target-btn{{height:36px}}.target-more{{grid-column:auto}}.target-more summary{{font-size:12px;font-weight:700;padding:8px}}.target-more-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px}}.nutri-mini-grid{{display:grid;grid-template-columns:repeat(7,minmax(96px,1fr));gap:6px;margin-top:8px}}.nutri-mini{{border:1px solid #dce8df;border-radius:10px;padding:7px 8px;background:#fbfdfb;min-width:0}}.nutri-mini span{{display:block;font-size:11px;color:#587064}}.nutri-mini b{{display:block;font-size:15px;line-height:1.15;margin:2px 0}}.nutri-mini small{{display:block;font-size:11px;color:#3f5148;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.nutri-mini em{{display:block;font-style:normal;font-size:10px;font-weight:700;margin-top:3px}}.nutri-diff{{display:block;font-style:normal;font-size:10px;font-weight:800;margin-top:4px;color:#607067}}.nutri-mini.warn .nutri-diff{{color:#bf4d32}}.target-live-note{{margin-top:7px;padding:7px 9px;border-radius:8px;background:#eef8f1;color:#2d6242;font-size:11px;font-weight:700}}.nutri-mini.ok{{border-left:3px solid #27a45e}}.nutri-mini.ok em{{color:#17733d}}.nutri-mini.warn{{border-left:3px solid #e6a11a;background:#fffdf7}}.nutri-mini.warn em{{color:#a96700}}.nutri-detail{{margin-top:8px}}.nutri-detail summary{{font-size:12px;color:#345b47}}.compact-note{{margin:7px 0 0;font-size:11px}}.table-compact-wrap{{overflow:auto;margin-top:7px}}.compact-table th,.compact-table td{{font-size:13px!important}}.ration-workbench-table th,.ration-workbench-table td,.smart-tech-table th,.smart-tech-table td{{padding:5px 7px;font-size:12px;vertical-align:middle}}.zebra tbody tr:nth-child(even),.ration-workbench-table tbody tr:nth-child(even),.smart-tech-table tbody tr:nth-child(even){{background:#f1f8f3}}.zebra tbody tr:nth-child(odd),.ration-workbench-table tbody tr:nth-child(odd),.smart-tech-table tbody tr:nth-child(odd){{background:#fff}}.ration-workbench-table tbody tr:hover,.smart-tech-table tbody tr:hover{{background:#e4f2e9}}.ration-workbench-table th:nth-child(1){{width:32%}}.ration-workbench-table th:nth-child(2){{width:22%}}.ration-workbench-table .ration-stepper{{gap:4px}}.ration-workbench-table .ration-qty{{width:72px;padding:6px}}.ration-live-grid{{display:none!important}}.ration-live{{position:static!important;padding:6px 8px!important;margin:5px 0!important;background:#f8fbf9!important}}.ration-live-metric{{padding:7px 8px!important}}.smart-solution{{padding:10px}}.smart-solution .effect{{font-size:11px;color:#456859;background:#eef7f1;border-radius:7px;padding:6px 7px;margin:7px 0}}.combo-apply{{margin-top:7px}}.smart-solution-grid{{gap:8px}}.ration-section-collapse{{padding:12px 14px}}.smart-tech-table th,.smart-tech-table td{{white-space:normal}}.ration-savebar{{margin-top:7px}}.ration-page-steps{{margin-bottom:8px}}
@media(max-width:1250px){{.nutri-mini-grid{{grid-template-columns:repeat(4,minmax(110px,1fr))}}.target-form{{grid-template-columns:repeat(2,minmax(150px,1fr)) auto}}.ration-workbench-table th,.ration-workbench-table td{{padding:5px 6px;font-size:11.5px}}}}
@media(max-width:820px){{.nutri-mini-grid{{grid-template-columns:repeat(2,minmax(120px,1fr))}}.target-form{{grid-template-columns:1fr}}.target-more{{grid-column:1}}.compact-target-btn{{width:100%}}.ration-workbench-table th:nth-child(3),.ration-workbench-table td:nth-child(3),.ration-workbench-table th:nth-child(4),.ration-workbench-table td:nth-child(4),.ration-workbench-table th:nth-child(5),.ration-workbench-table td:nth-child(5){{display:none}}}}
/* V3.9.15 - hedef çalışma masasıyla birlikte görünür */
.target-card{{padding-bottom:8px}}.nutri-mini-grid{{grid-template-columns:repeat(8,minmax(108px,1fr));position:sticky;top:48px;z-index:18;background:#f4f7f5;padding:7px;border:1px solid #cfe3d5;border-radius:12px;box-shadow:0 6px 18px rgba(24,73,46,.08)}}.nutri-mini{{padding:6px 7px}}.nutri-mini b{{font-size:16px}}.nutri-mini small{{font-weight:900;color:#203c2d}}.target-live-note{{display:none}}#ration-workbench{{margin-top:8px!important}}.workbench-head{{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}}.workbench-actions{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.quick-feed-card:not([open]){{display:none}}.quick-feed-card[open]{{display:block}}
@media(max-width:1350px){{.nutri-mini-grid{{grid-template-columns:repeat(4,minmax(120px,1fr));position:static}}}}
@media(max-width:820px){{.nutri-mini-grid{{grid-template-columns:repeat(2,minmax(120px,1fr));position:static}}.workbench-actions{{width:100%}}.workbench-actions .btn{{flex:1}}}}
/* V3.9.18 - Rasyon sayfası kompakt üst alan */
.ration-page-title{{margin:8px 0 4px!important;font-size:25px!important;line-height:1.05}}.ration-page-subtitle{{margin:0 0 6px!important;font-size:13px}}.ration-page-steps{{display:flex;gap:10px;flex-wrap:wrap;margin:3px 0 8px!important;font-size:12px;color:#486457}}.ration-new-collapsed{{padding:8px 12px!important;margin-bottom:8px}}.ration-new-collapsed>details>summary{{display:flex;align-items:center;gap:7px;min-height:30px}}.ration-new-collapsed>details>summary h2{{font-size:18px!important;line-height:1.1}}.ration-new-collapsed>details>summary .mut{{font-size:11px!important;margin-left:2px!important}}.ration-create-grid{{gap:8px!important;margin-top:8px!important}}.ration-create-grid>.card{{padding:10px!important}}@media(max-width:700px){{.ration-page-title{{font-size:23px!important}}.ration-new-collapsed>details>summary{{flex-wrap:wrap}}}}
.ration-picker-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,235px));gap:10px;margin-top:10px}}.ration-picker-card{{display:block;min-height:0;padding:12px 14px!important;border:1px solid #dce8df!important;text-decoration:none}}.ration-picker-card.active{{border:2px solid #176b3a!important;padding:11px 13px!important}}.ration-picker-head{{display:flex;align-items:center;justify-content:space-between;gap:8px}}.ration-picker-head h3{{margin:0;font-size:17px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.ration-picker-type{{font-size:12px;color:#60766a;white-space:nowrap}}.ration-picker-main{{display:flex;align-items:center;gap:6px;margin-top:8px;font-size:14px}}.ration-picker-ratio{{margin-top:5px;font-size:12px;color:#526b5e}}@media(max-width:700px){{.ration-picker-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.ration-picker-card{{padding:10px!important}}.ration-picker-main{{font-size:13px;flex-wrap:wrap}}}}@media(max-width:430px){{.ration-picker-grid{{grid-template-columns:1fr}}}}</style></head><body><div class="top"><div class="top-left"><button class="menu-toggle" id="menuToggle" aria-label="Menüyü aç">☰</button><a class="brand" href="/" title="Ana Sayfa">🐄 ÇiftlikPro</a></div><div class="top-user"><span class="ver">{APP_LABEL}</span> &nbsp; {h(display)} · <a href="/logout">Çıkış</a></div></div><div class="layout"><aside class="side" id="sideMenu">{nav}</aside><main class="main">{fl}{body}</main></div><script>
(function(){{
 const btn=document.getElementById("menuToggle"),side=document.getElementById("sideMenu");
 if(btn&&side){{btn.addEventListener("click",function(){{side.classList.toggle("mobile-open");}});side.querySelectorAll("a").forEach(function(a){{a.addEventListener("click",function(){{side.classList.remove("mobile-open");}});}});}}
 document.querySelectorAll(".nav-group").forEach(function(d){{d.addEventListener("toggle",function(){{if(!d.open)return;document.querySelectorAll(".nav-group").forEach(function(o){{if(o!==d)o.open=false;}});}});}});
 const c=document.getElementById("financeCategory"),a=document.getElementById("financeAnimal"),w=document.getElementById("statusWarning"),bulk=document.getElementById("bulkAnimalIds");if(c&&a&&w){{function x(){{const r=c.value==="Hayvan Satışı"||c.value==="Kesim Geliri";w.style.display=r?"block":"none";a.required=r&&!bulk;}}c.addEventListener("change",x);x();}}
}})();
function copyDeviceSimple(id,btn){{
 var el=document.getElementById(id);if(!el)return;var v=(el.innerText||el.textContent||'').trim();
 var ta=document.createElement('textarea');ta.value=v;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();
 try{{document.execCommand('copy');var old=btn.innerText;btn.innerText='✓ Kopyalandı';setTimeout(function(){{btn.innerText=old}},1400)}}
 catch(e){{window.prompt('Cihaz Kimliğini kopyalayın:',v)}}
 document.body.removeChild(ta);
}}
function toggleAnimalFields(){{
 var type=document.getElementById('recordType');if(!type)return;var calf=type.value==='Buzağı';
 document.querySelectorAll('.calf-only').forEach(function(e){{e.style.display=calf?'block':'none';}});
 document.querySelectorAll('.adult-only').forEach(function(e){{e.style.display=calf?'none':'block';}});
 document.querySelectorAll('.female-pregnancy').forEach(function(e){{e.style.display=type.value==='Dişi'?'block':'none';}});
 var badge=document.getElementById('recordTypeBadge');if(badge)badge.textContent=type.options[type.selectedIndex].text;
 toggleEntryPregnancy();
}}
function toggleEntryPregnancy(){{
 var type=document.getElementById('recordType'),status=document.getElementById('entryPregnancyStatus'),mode=document.getElementById('pregnancyInfoMode');
 if(!type||!status)return;var pregnant=type.value==='Dişi'&&status.value==='Gebe',age=pregnant&&mode&&mode.value==='age';
 ['pregnancyInfoModeLabel','pregnancyEntryDateLabel','pregnancyEntryHint'].forEach(function(id){{var e=document.getElementById(id);if(e)e.style.display=pregnant?'block':'none';}});
 var kd=document.getElementById('knownInseminationLabel'),ag=document.getElementById('pregnancyAgeLabel');
 if(kd)kd.style.display=pregnant&&!age?'block':'none';if(ag)ag.style.display=age?'block':'none';
}}
function liveTableFilter(inputId,tableId,emptyId){{
 var input=document.getElementById(inputId),table=document.getElementById(tableId),empty=document.getElementById(emptyId);if(!input||!table)return;
 input.addEventListener('input',function(){{var q=(input.value||'').toLocaleLowerCase('tr-TR').trim(),visible=0;table.querySelectorAll('tbody tr.data-row').forEach(function(row){{var ok=!q||row.textContent.toLocaleLowerCase('tr-TR').includes(q);row.style.display=ok?'':'none';if(ok)visible++;}});if(empty)empty.style.display=visible?'none':'block';}});
}}
async function optimizePhotoFile(file,status,text,bar){{
 if(!file||!file.type||!file.type.startsWith('image/'))return file;
 const maxSide=1024,quality=.58;
 if(text)text.textContent='Fotoğraf hazırlanıyor…';if(status)status.classList.add('on');if(bar)bar.style.width='8%';
 try{{
   const bitmap=await createImageBitmap(file);
   let w=bitmap.width,h=bitmap.height,scale=Math.min(1,maxSide/Math.max(w,h));w=Math.max(1,Math.round(w*scale));h=Math.max(1,Math.round(h*scale));
   const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;const ctx=canvas.getContext('2d');ctx.drawImage(bitmap,0,0,w,h);if(bitmap.close)bitmap.close();
   if(bar)bar.style.width='22%';
   const blob=await new Promise(function(resolve){{canvas.toBlob(resolve,'image/webp',quality);}});
   if(!blob)throw new Error('Fotoğraf dönüştürülemedi');
   const base=(file.name||'hayvan').replace(/[.][^.]+$/,'');
   return new File([blob],base+'.webp',{{type:'image/webp',lastModified:Date.now()}});
 }}catch(err){{
   console.warn('Fotoğraf optimizasyonu atlandı:',err);return file;
 }}
}}
function bindSmartPhotoForms(){{
 document.querySelectorAll('form[data-smart-photo-form="1"]').forEach(function(form){{
   if(form.dataset.smartBound==='1')return;form.dataset.smartBound='1';
   const input=form.querySelector('input[type="file"][name="photo_file"]'),btn=form.querySelector('button[type="submit"],button:not([type])'),status=form.querySelector('[data-upload-status]'),text=form.querySelector('[data-upload-text]'),bar=form.querySelector('[data-upload-bar]');
   if(input)input.addEventListener('change',function(){{if(status){{status.classList.remove('error');status.classList.add('on');}}if(text){{const f=input.files&&input.files[0];text.textContent=f?'Seçildi: '+f.name+' · Kaydederken otomatik küçültülecek.':'Fotoğraf hazırlanıyor…';}}if(bar)bar.style.width='0';}});
   form.addEventListener('submit',async function(ev){{
     ev.preventDefault();if(form.dataset.submitting==='1')return;if(!form.checkValidity()){{form.reportValidity();return;}}
     form.dataset.submitting='1';if(btn){{btn.disabled=true;btn.dataset.oldText=btn.textContent;btn.textContent='Kaydediliyor…';}}
     if(status){{status.classList.remove('error');status.classList.add('on');}}if(bar)bar.style.width='3%';
     try{{
       let chosen=input&&input.files&&input.files[0];
       if(chosen){{const optimized=await optimizePhotoFile(chosen,status,text,bar);if(optimized!==chosen){{const dt=new DataTransfer();dt.items.add(optimized);input.files=dt.files;chosen=optimized;}}if(text)text.textContent='Fotoğraf yükleniyor…';}}
       else {{if(text)text.textContent='Değişiklikler kaydediliyor…';if(bar)bar.style.width='25%';}}
       const xhr=new XMLHttpRequest();xhr.open((form.method||'POST').toUpperCase(),form.action,true);
       xhr.upload.onprogress=function(e){{if(e.lengthComputable&&bar){{const pct=Math.max(25,Math.min(95,Math.round(e.loaded/e.total*100)));bar.style.width=pct+'%';if(text)text.textContent='Yükleniyor… %'+pct;}}}};
       xhr.onerror=function(){{fail('Sunucuya ulaşılamadı. Mobil internet / VPN bağlantısını kontrol edip tekrar deneyin.');}};
       xhr.ontimeout=function(){{fail('Yükleme zaman aşımına uğradı. Bağlantıyı kontrol edip tekrar deneyin.');}};xhr.timeout=120000;
       xhr.onload=function(){{if(xhr.status>=200&&xhr.status<400){{if(bar)bar.style.width='100%';if(text)text.textContent='Kaydedildi.';window.location.href=xhr.responseURL||form.action;}}else fail('Kaydetme başarısız oldu (HTTP '+xhr.status+'). Tekrar deneyin.');}};
       function fail(message){{form.dataset.submitting='0';if(btn){{btn.disabled=false;btn.textContent=btn.dataset.oldText||'Kaydet';}}if(status){{status.classList.add('error');status.classList.add('on');}}if(text)text.textContent=message;if(bar)bar.style.width='0';}}
       xhr.send(new FormData(form));
     }}catch(err){{form.dataset.submitting='0';if(btn){{btn.disabled=false;btn.textContent=btn.dataset.oldText||'Kaydet';}}if(status){{status.classList.add('error');status.classList.add('on');}}if(text)text.textContent='Fotoğraf hazırlanırken hata oluştu. Başka bir fotoğraf seçip tekrar deneyin.';if(bar)bar.style.width='0';console.error(err);}}
   }});
 }});
}}

function moneyRaw(v){{
  v=String(v||'').trim().replace(/[₺\\s]/g,'');
  if(!v)return '';
  const comma=v.indexOf(',');
  const whole=(comma>=0?v.slice(0,comma):v).replace(/\\D/g,'')||'0';
  const dec=comma>=0?v.slice(comma+1).replace(/\\D/g,'').slice(0,2):'';
  return whole+(comma>=0&&dec!==''?'.'+dec:'');
}}
function moneyGroupDigits(digits){{
  digits=String(digits||'').replace(/\\D/g,'').replace(/^0+(?=\\d)/,'');
  if(!digits)return '';
  return digits.replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,'.');
}}
function bindSmartMoney(){{
  const names=new Set(['amount','cost','purchase_price','sale_price','sold_price','target_sale_price','daily_feed_cost','daily_care_cost']);
  document.querySelectorAll('input[name]').forEach(function(el){{
    if(!names.has(el.name)||el.dataset.moneyBound==='1')return;
    el.dataset.moneyBound='1';
    el.type='text';
    el.inputMode='numeric';
    el.autocomplete='off';
    el.classList.add('smart-money');

    // Existing database value -> Turkish display.
    if(el.value){{
      const initial=String(el.value).trim().replace(',', '.');
      const n=Number(initial);
      if(Number.isFinite(n)){{
        const fixed=Math.round(n*100)/100;
        const parts=String(fixed).split('.');
        const whole=moneyGroupDigits(parts[0]);
        const dec=(parts[1]||'').replace(/\\D/g,'').slice(0,2);
        el.value=whole+(dec?','+dec:'');
      }}
    }}

    // IMPORTANT: while typing, only digits are accepted as the lira amount.
    // The dots visible in the field are presentation only.
    el.addEventListener('input',function(){{
      const raw=el.value;
      const digits=raw.replace(/\\D/g,'');
      el.value=moneyGroupDigits(digits);
      try{{el.setSelectionRange(el.value.length,el.value.length);}}catch(e){{}}
    }});

    // Prevent punctuation typed by mobile/desktop keyboard from changing meaning.
    el.addEventListener('beforeinput',function(ev){{
      if(ev.data==='.'||ev.data===','){{
        ev.preventDefault();
      }}
    }});
  }});

  document.querySelectorAll('form').forEach(function(form){{
    if(form.dataset.moneySubmitBound==='1')return;
    form.dataset.moneySubmitBound='1';
    form.addEventListener('submit',function(){{
      form.querySelectorAll('input.smart-money').forEach(function(el){{
        el.value=String(el.value||'').replace(/\\D/g,'');
      }});
    }},true);
  }});
}}
document.addEventListener('DOMContentLoaded',bindSmartMoney);

document.addEventListener('DOMContentLoaded',bindSmartPhotoForms);
</script></body></html>"""


PHOTO_MAX_SIDE=1024
PHOTO_WEBP_QUALITY=58
PHOTO_JPEG_QUALITY=56

def format_bytes(n):
    n=float(n or 0)
    for unit in ('B','KB','MB','GB'):
        if n<1024 or unit=='GB':
            return f'{n:.1f} {unit}' if unit!='B' else f'{int(n)} B'
        n/=1024

def get_setting(key,default=''):
    try:
        with db() as c:
            r=c.execute('select setting_value from settings where setting_key=?',(key,)).fetchone()
        return (r['setting_value'] if r else default) or default
    except Exception:
        return default

def set_setting_value(key,value):
    with db() as c:
        c.execute('insert or replace into settings(setting_key,setting_value) values(?,?)',(key,str(value or '')))

def configured_backup_dir():
    raw=(get_setting('backup_directory','') or '').strip()
    if not raw:return BACKUPS
    try:
        path=Path(os.path.expandvars(os.path.expanduser(raw)))
        path.mkdir(parents=True,exist_ok=True)
        probe=path/'.ciftlikpro_probe.tmp'
        probe.write_text('ok',encoding='utf-8')
        probe.unlink()
        return path
    except Exception:
        return BACKUPS

def uploads_storage_stats():
    total=count=0
    if UPLOADS.exists():
        for fp in UPLOADS.rglob('*'):
            if fp.is_file():
                try:
                    total+=fp.stat().st_size;count+=1
                except OSError:pass
    db_size=DB.stat().st_size if DB.exists() else 0
    return {'db_bytes':db_size,'upload_bytes':total,'upload_count':count,'total_bytes':db_size+total}

def optimized_webp_bytes(content):
    with Image.open(io.BytesIO(content)) as im:
        im=ImageOps.exif_transpose(im)
        if getattr(im,'is_animated',False):
            try:im.seek(0)
            except Exception:pass
        if im.mode not in ('RGB','RGBA'):im=im.convert('RGB')
        im.thumbnail((PHOTO_MAX_SIDE,PHOTO_MAX_SIDE),Image.Resampling.LANCZOS)
        out=io.BytesIO()
        im.save(out,'WEBP',quality=PHOTO_WEBP_QUALITY,method=6)
        return out.getvalue()

def save_optimized_upload(prefix,upload):
    content=upload.get('content') if isinstance(upload,dict) else None
    if not content:raise ValueError('Fotoğraf içeriği boş.')
    if len(content)>15*1024*1024:raise ValueError('Fotoğraf 15 MB sınırını aşıyor.')
    data=optimized_webp_bytes(content)
    name=f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.webp"
    UPLOADS.mkdir(parents=True,exist_ok=True)
    (UPLOADS/name).write_bytes(data)
    return name

def optimize_existing_uploads():
    if not UPLOADS.exists():return {'count':0,'saved':0,'before':0,'after':0}
    before=after=count=0
    for fp in list(UPLOADS.rglob('*')):
        if not fp.is_file() or fp.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):continue
        old_size=fp.stat().st_size;before+=old_size
        tmp=fp.with_name(fp.name+'.optimize-tmp')
        try:
            with Image.open(fp) as im:
                im=ImageOps.exif_transpose(im)
                im.thumbnail((PHOTO_MAX_SIDE,PHOTO_MAX_SIDE),Image.Resampling.LANCZOS)
                ext=fp.suffix.lower()
                if ext in ('.jpg','.jpeg'):
                    if im.mode!='RGB':im=im.convert('RGB')
                    im.save(tmp,'JPEG',quality=PHOTO_JPEG_QUALITY,optimize=True,progressive=True)
                elif ext=='.webp':
                    if im.mode not in ('RGB','RGBA'):im=im.convert('RGB')
                    im.save(tmp,'WEBP',quality=PHOTO_WEBP_QUALITY,method=6)
                else:
                    if im.mode not in ('RGB','RGBA'):im=im.convert('RGBA')
                    im.save(tmp,'PNG',optimize=True,compress_level=9)
            new_size=tmp.stat().st_size
            if new_size<old_size:
                os.replace(tmp,fp);after+=new_size;count+=1
            else:
                tmp.unlink(missing_ok=True);after+=old_size
        except Exception:
            tmp.unlink(missing_ok=True);after+=old_size
    return {'count':count,'saved':max(0,before-after),'before':before,'after':after}

def clean_text(v):
    if v is None:return ''
    t=str(v).strip()
    return '' if t.lower() in ('undefined','null','none') else t

def create_backup(label='manuel'):
    target_dir=configured_backup_dir()
    target_dir.mkdir(parents=True,exist_ok=True)
    ts=datetime.now().strftime('%Y%m%d_%H%M%S')
    name=f'CiftlikPro_Backup_{label}_{ts}.zip'
    dst=target_dir/name
    temp_db=DATA_ROOT/f'.snapshot_{ts}.db'
    with db() as src, sqlite3.connect(temp_db) as out:src.backup(out)
    manifest={'product':APP_NAME,'version':APP_VERSION,'created_at':datetime.now().isoformat(timespec='seconds'),'database':'ciftlik.db','includes_uploads':True,'label':label,'backup_directory':str(target_dir)}
    try:
        with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(temp_db,'ciftlik.db')
            z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
            if UPLOADS.exists():
                for fp in UPLOADS.rglob('*'):
                    if fp.is_file():z.write(fp,'uploads/'+str(fp.relative_to(UPLOADS)).replace('\\','/'))
    finally:
        gc.collect()
        for attempt in range(12):
            try:
                if temp_db.exists():temp_db.unlink()
                break
            except PermissionError:
                if attempt<11:time.sleep(.25)
            except FileNotFoundError:break
    with db() as c:c.execute('insert into backups(filename,created_at,size_bytes) values(?,?,?)',(name,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),dst.stat().st_size))
    return name

def validate_backup_zip(zip_path):
    with zipfile.ZipFile(zip_path,'r') as z:
        names=set(z.namelist())
        if 'ciftlik.db' not in names:return False,'Yedekte ciftlik.db bulunamadı.',None
        for name in names:
            p=Path(name)
            if name.startswith('/') or '..' in p.parts:return False,'Güvensiz ZIP yolu tespit edildi.',None
        manifest={}
        if 'manifest.json' in names:
            try:manifest=json.loads(z.read('manifest.json').decode('utf-8'))
            except Exception:return False,'manifest.json okunamadı.',None
        with tempfile.TemporaryDirectory() as td:
            db_copy=Path(td)/'ciftlik.db';db_copy.write_bytes(z.read('ciftlik.db'))
            try:
                with sqlite3.connect(db_copy) as c:
                    if c.execute('pragma quick_check').fetchone()[0]!='ok':return False,'Yedek veritabanı bozuk.',None
            except Exception as exc:return False,'Yedek veritabanı açılamadı: '+str(exc),None
    return True,'Yedek geçerli.',manifest

def restore_backup_zip(zip_path):
    ok,message,manifest=validate_backup_zip(zip_path)
    if not ok:raise ValueError(message)
    emergency=create_backup('EmergencyBeforeRestore')
    with tempfile.TemporaryDirectory() as td:
        target=Path(td)
        with zipfile.ZipFile(zip_path,'r') as z:z.extractall(target)
        staged=DB.with_suffix('.restore.tmp');shutil.copy2(target/'ciftlik.db',staged);os.replace(staged,DB)
        restored=target/'uploads'
        if restored.exists():
            shutil.rmtree(UPLOADS,ignore_errors=True);shutil.copytree(restored,UPLOADS)
        else:UPLOADS.mkdir(exist_ok=True)
    init_db();return emergency,manifest

def daily_backup():
    BACKUPS.mkdir(exist_ok=True);today=date.today().strftime('%Y%m%d')
    if not any(BACKUPS.glob(f'CiftlikPro_Backup_otomatik_{today}_*.zip')):create_backup('otomatik')
    files=sorted(BACKUPS.glob('CiftlikPro_Backup_otomatik_*.zip'),key=lambda x:x.stat().st_mtime,reverse=True)
    for fp in files[30:]:
        try:fp.unlink()
        except:pass


def export_payload():
    with db() as c:
        return {'format':'ciftlik-suru-takip-v06','exportDate':datetime.now().isoformat(),'animals':[dict(r) for r in c.execute('select * from animals order by id')],'inseminations':[dict(r) for r in c.execute('select * from inseminations order by animal_id,attempt')],'estrus_records':[dict(r) for r in c.execute('select * from estrus_records order by animal_id,estrus_date')],'calves':[dict(r) for r in c.execute('select * from calves order by id')],'health':[dict(r) for r in c.execute('select * from health order by id')],'finance':[dict(r) for r in c.execute('select * from finance order by id')],'weights':[dict(r) for r in c.execute('select * from weights order by id')],'milk':[dict(r) for r in c.execute('select * from milk order by id')]}

def import_payload(payload,strategy='skip'):
    stats={'animals':0,'animals_updated':0,'inseminations':0,'calves':0,'finance':0,'health':0,'skipped':0,'errors':[]}
    animals=payload.get('herdData',payload.get('animals',[])) if isinstance(payload,dict) else []
    calf_data=payload.get('calfData',payload.get('calves',[])) if isinstance(payload,dict) else []
    finance_data=payload.get('financeData',payload.get('finance',[])) if isinstance(payload,dict) else []
    native_insems=payload.get('inseminations',[]) if isinstance(payload,dict) else []
    health_data=payload.get('health',[]) if isinstance(payload,dict) else []
    with db() as c:
        for a in animals:
            try:
                tag=clean_text(a.get('tagId',a.get('tag')))
                if not tag:stats['skipped']+=1;continue
                nickname=clean_text(a.get('description',a.get('nickname')))
                gender=clean_text(a.get('gender')) or 'Dişi'
                existing=c.execute('select id from animals where tag=?',(tag,)).fetchone()
                if existing:
                    aid=existing['id']
                    if strategy=='update':
                        c.execute('update animals set nickname=coalesce(nullif(?,''),nickname),gender=coalesce(nullif(?,''),gender),breed=coalesce(nullif(?,''),breed),birth_date=coalesce(nullif(?,''),birth_date),notes=coalesce(nullif(?,''),notes) where id=?',(nickname,gender,clean_text(a.get('breed')),clean_text(a.get('birth_date',a.get('birthDate'))),clean_text(a.get('notes')),aid));stats['animals_updated']+=1
                    else:stats['skipped']+=1
                else:
                    aid=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes) values(?,?,?,?,?,?)',(tag,nickname,gender,clean_text(a.get('breed')),clean_text(a.get('birth_date',a.get('birthDate'))),clean_text(a.get('notes')))).lastrowid;stats['animals']+=1
                dates=[a.get('toh1'),a.get('toh2'),a.get('toh3')]
                latest=next((clean_text(x) for x in reversed(dates) if clean_text(x)),'')
                for i,d in enumerate(dates,1):
                    d=clean_text(d)
                    if not d:continue
                    result='Pozitif' if bool(a.get('isPregnant')) and d==latest else 'Belirsiz'
                    due=(date.fromisoformat(d)+timedelta(days=280)).isoformat() if result=='Pozitif' else ''
                    c.execute('insert or replace into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',(aid,i,d,result,due));stats['inseminations']+=1
            except Exception as e:stats['errors'].append(f'Hayvan: {e}')
        for ins in native_insems:
            try:
                aid=ins.get('animal_id')
                if not aid and clean_text(ins.get('tag')):
                    r=c.execute('select id from animals where tag=?',(clean_text(ins.get('tag')),)).fetchone();aid=r['id'] if r else None
                if not aid:stats['skipped']+=1;continue
                c.execute('insert or replace into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',(aid,ins.get('attempt',1),ins.get('insemination_date',''),ins.get('pregnancy_result','Belirsiz'),ins.get('due_date','')));stats['inseminations']+=1
            except Exception as e:stats['errors'].append(f'Tohumlama: {e}')
        for calf in calf_data:
            try:
                tag=clean_text(calf.get('tagId',calf.get('tag')));mtag=clean_text(calf.get('motherTagId',calf.get('mother_tag')))
                mother=c.execute("select id from animals where tag=? and gender='Dişi'",(mtag,)).fetchone()
                if not tag or not mother or c.execute('select 1 from calves where tag=?',(tag,)).fetchone():stats['skipped']+=1;continue
                c.execute('insert into calves(tag,mother_id,father_tag,birth_date,gender,notes) values(?,?,?,?,?,?)',(tag,mother['id'],clean_text(calf.get('fatherTagId',calf.get('father_tag'))),clean_text(calf.get('birthDate',calf.get('birth_date'))),clean_text(calf.get('gender')),clean_text(calf.get('notes'))));stats['calves']+=1
            except Exception as e:stats['errors'].append(f'Buzağı: {e}')
        for f in finance_data:
            try:
                typ='Gelir' if clean_text(f.get('type',f.get('tx_type'))).lower()=='gelir' else 'Gider';tag=clean_text(f.get('tagId',f.get('tag')));aid=None
                if tag and tag!='-':
                    r=c.execute('select id from animals where tag=?',(tag,)).fetchone();aid=r['id'] if r else None
                c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at) values(?,?,?,?,?,?,?,?)',(clean_text(f.get('date',f.get('tx_date'))),typ,clean_text(f.get('category')) or 'Diğer',float(f.get('amount') or 0),clean_text(f.get('description')),clean_text(f.get('payment_method')) or 'Belirtilmedi',aid,datetime.now().isoformat()));stats['finance']+=1
            except Exception as e:stats['errors'].append(f'Finans: {e}')
        for x in health_data:
            try:c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(x.get('animal_id'),x.get('kind'),x.get('product'),x.get('applied_date'),x.get('next_date'),float(x.get('cost') or 0),x.get('notes')));stats['health']+=1
            except Exception as e:stats['errors'].append(f'Sağlık: {e}')
    return stats

class App(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def parse_cookie(self):
        c=cookies.SimpleCookie(self.headers.get('Cookie')); return c.get('sid').value if c.get('sid') else None
    def user(self): return SESSIONS.get(self.parse_cookie())
    def send_html(self,s,status=200,headers=None):
        b=s.encode('utf-8')
        try:
            self.send_response(status); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(b)))
            for k,v in (headers or []):self.send_header(k,v)
            self.end_headers(); self.wfile.write(b)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            # Tarayıcı yenileme/geri/sekme kapatma sırasında isteği iptal edebilir.
            # Bu durum uygulama hatası değildir; DEV konsoluna traceback basma.
            return
        except OSError as e:
            if getattr(e,'winerror',None) in (10053,10054): return
            raise
    def redirect(self,url,msg=''):
        # Mesaj query string'e, varsa #anchor'dan ÖNCE eklenmeli.
        # Aksi halde /rations?id=1%23... gibi bozuk URL oluşup sayfayı düşürebilir.
        base, sep, frag = url.partition('#')
        if msg:
            base += ('&' if '?' in base else '?')+'msg='+urllib.parse.quote(msg)
        target = base + (('#'+frag) if sep else '')
        self.send_response(303);self.send_header('Location',target);self.end_headers()
    def form(self):
        n=int(self.headers.get('Content-Length','0')); return {k:v[0] for k,v in urllib.parse.parse_qs(self.rfile.read(n).decode()).items()}
    def post_data(self):
        ctype=self.headers.get('Content-Type','')
        if ctype.startswith('multipart/form-data'):
            n=int(self.headers.get('Content-Length','0')); body=self.rfile.read(n)
            raw=(f'Content-Type: {ctype}\r\nMIME-Version: 1.0\r\n\r\n').encode()+body
            msg=BytesParser(policy=default).parsebytes(raw); data={}
            for part in msg.iter_parts():
                name=part.get_param('name',header='content-disposition'); filename=part.get_filename(); content=part.get_payload(decode=True) or b''
                if filename:data[name]={'filename':filename,'content':content}
                else:data[name]=content.decode(part.get_content_charset() or 'utf-8')
            return data
        return self.form()
    def require(self):
        if not self.user(): self.redirect('/login'); return False
        return True
    def is_admin(self):return bool(self.user() and self.user().get('role')=='admin')
    def require_admin(self):
        if not self.require():return False
        if not self.is_admin():self.redirect('/','Bu bölüm yalnızca yöneticilere açıktır.');return False
        return True
    def client_ip(self):return self.client_address[0] if self.client_address else ''
    def do_GET(self):
        ensure_archive_schema()
        p=urllib.parse.urlparse(self.path); path=p.path; q=urllib.parse.parse_qs(p.query); msg=q.get('msg',[''])[0]
        lic_ok,lic_payload,lic_msg=license_status()
        if path=='/license':
            payload=lic_payload or {}
            flash_html=('<div class="activation-alert">'+h(msg)+'</div>') if msg else ''
            status_class='license-ok' if lic_ok else 'license-bad'
            status_text='🟢 Lisans Aktif' if lic_ok else '🔴 Lisans Gerekli'
            active_details=''
            if lic_ok:
                exp=payload.get('expires_on') or 'Süresiz'
                if exp!='Süresiz': exp=fmt_date(exp)
                active_details='<div class="activation-details"><div><span>Lisans Sahibi</span><b>'+h(payload.get('licensee') or '-')+'</b></div><div><span>Lisans Türü</span><b>'+h(payload.get('license_type') or '-')+'</b></div><div><span>Geçerlilik</span><b>'+h(exp)+'</b></div></div><a class="activation-continue" href="/login">ÇiftlikPro\'ya Devam →</a>'
            upload_section='' if lic_ok else '''<form class="activation-form" method="post" action="/license-key-activate">
              <label class="device-label" for="license_key">Lisans Anahtarı</label>
              <textarea id="license_key" name="license_key" class="license-key-input" rows="4" placeholder="CFP-XXXXX-XXXXX-XXXXX-..." required></textarea>
              <button class="activation-submit" type="submit">🔓 ÇiftlikPro'yu Etkinleştir</button></form>
              <details class="file-fallback"><summary>Gelişmiş: .license dosyasıyla etkinleştir</summary>
              <form class="activation-form fallback-form" method="post" action="/license-activate" enctype="multipart/form-data">
              <label class="activation-upload" for="license_file"><span class="upload-icon">📄</span><span><b>Lisans dosyanızı seçin</b><small>Yedek aktivasyon yöntemi</small></span><span class="upload-button">Dosya Seç</span></label>
              <input id="license_file" type="file" name="license_file" accept=".license,application/json" required hidden><div id="selected-license" class="selected-license">Henüz dosya seçilmedi</div>
              <button class="activation-submit secondary-submit" type="submit">Dosyayla Etkinleştir</button></form></details>'''
            html='''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ÇiftlikPro Aktivasyon</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,"Segoe UI",Arial,sans-serif;background:linear-gradient(145deg,#eef5f0 0%,#f8faf9 55%,#e7f1eb 100%);color:#173426;min-height:100vh}
.activation-page{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:28px 16px}.activation-card{width:min(760px,100%);background:#fff;border:1px solid #dce9e0;border-radius:28px;box-shadow:0 24px 70px rgba(17,73,43,.14);overflow:hidden}
.activation-head{background:linear-gradient(135deg,#105b35,#18824a);padding:30px 34px;color:#fff}.activation-brand{display:flex;align-items:center;gap:11px;font-weight:800;font-size:19px}.activation-brand span:first-child{font-size:27px}
.activation-head h1{font-size:34px;line-height:1.1;margin:28px 0 8px}.activation-head p{margin:0;color:#dcefe4;font-size:15px}.activation-body{padding:32px 34px 34px}
.activation-status{display:inline-flex;padding:8px 13px;border-radius:999px;font-weight:800;font-size:14px;margin-bottom:22px}.license-ok{background:#e5f6eb;color:#14723d}.license-bad{background:#fff0ed;color:#ad3529}
.activation-alert{padding:13px 15px;border-radius:12px;background:#fff4dc;color:#7c5600;border:1px solid #f2d797;margin-bottom:18px}.device-label{font-size:13px;color:#698075;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px}
.device-row{display:flex;gap:10px}.device-code{flex:1;background:#f0f7f2;border:1px solid #cfe2d5;border-radius:14px;padding:15px 17px;font:800 18px Consolas,monospace;letter-spacing:.7px;color:#145c36;overflow-wrap:anywhere}
.copy-btn{border:0;border-radius:14px;background:#e6f2e9;color:#176a3c;font-weight:800;padding:0 18px;cursor:pointer}.activation-help{color:#65786d;font-size:14px;line-height:1.55;margin:12px 0 24px}
.activation-upload{display:flex;align-items:center;gap:14px;border:2px dashed #b8d4c0;background:#f8fbf9;border-radius:18px;padding:18px;cursor:pointer}.upload-icon{font-size:28px}.activation-upload b,.activation-upload small{display:block}.activation-upload small{color:#77887f;margin-top:3px}.upload-button{margin-left:auto;background:#e4f1e8;color:#16693b;padding:9px 12px;border-radius:10px;font-weight:800}
.license-key-input{width:100%;resize:vertical;min-height:105px;border:1px solid #bfd5c6;border-radius:14px;background:#f8fbf9;padding:15px;font:700 14px Consolas,monospace;color:#174d31;outline:none;margin:0 0 14px}.selected-license{font-size:13px;color:#718177;margin:8px 2px 14px}.file-fallback{margin-top:18px;border-top:1px solid #e4ece7;padding-top:16px}.file-fallback summary{cursor:pointer;font-weight:700;color:#65786d}.fallback-form{margin-top:14px}.secondary-submit{background:#557267}.activation-submit,.activation-continue{width:100%;border:0;border-radius:14px;background:linear-gradient(135deg,#14763f,#199151);color:#fff;font-weight:800;font-size:16px;padding:15px 18px;cursor:pointer;text-decoration:none;display:block;text-align:center}
.activation-details{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:22px 0}.activation-details div{background:#f3f8f5;border-radius:13px;padding:13px}.activation-details span{display:block;color:#708278;font-size:12px}.activation-foot{text-align:center;color:#829087;font-size:12px;margin-top:22px}
@media(max-width:600px){.activation-page{padding:0}.activation-card{min-height:100vh;border-radius:0}.activation-head{padding:26px 22px}.activation-head h1{font-size:29px}.activation-body{padding:26px 22px}.device-row{display:block}.copy-btn{width:100%;padding:12px;margin-top:8px}.activation-details{grid-template-columns:1fr}}
</style></head><body><main class="activation-page"><section class="activation-card"><header class="activation-head"><div class="activation-brand"><span>🐄</span><span>ÇiftlikPro Enterprise</span></div><h1>🔐 Lisans Aktivasyonu</h1><p>Bu bilgisayarı güvenli bir ÇiftlikPro lisansıyla etkinleştirin.</p></header><div class="activation-body">'''
            html+=flash_html+'<div class="activation-status '+status_class+'">'+status_text+'</div><div class="device-label">Bu Bilgisayarın Cihaz Kimliği</div><div class="device-row"><div id="device-code" class="device-code">'+h(device_id())+'</div><button class="copy-btn" type="button" onclick="copyDevice()">Kopyala</button></div><p class="activation-help">Bu cihaz kodunu lisans yöneticisine iletin. Size verilen <b>CFP lisans anahtarını</b> aşağıdaki alana yapıştırın.</p>'+active_details+upload_section
            html+='''<div class="activation-foot">ÇiftlikPro Enterprise · Cihaza bağlı dijital lisans koruması</div></div></section></main>
<script>
function copyDevice(){var t=document.getElementById("device-code").innerText;navigator.clipboard.writeText(t).then(function(){var b=document.querySelector(".copy-btn");b.innerText="Kopyalandı ✓";setTimeout(function(){b.innerText="Kopyala"},1600)})}
var f=document.getElementById("license_file");if(f){f.addEventListener("change",function(){document.getElementById("selected-license").innerText=f.files.length?"Seçilen dosya: "+f.files[0].name:"Henüz dosya seçilmedi"})}
</script></body></html>'''
            return self.send_html(html)
        if not lic_ok and path not in ('/license','/license-activate','/license-key-activate'):
            return self.redirect('/license',lic_msg)
        if path=='/login':
            login_msg=('<div class="flash err">'+h(msg)+'</div>') if msg else ''
            return self.send_html(f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ÇiftlikPro Enterprise · Giriş</title><style>{CSS}
            body{{min-height:100vh;margin:0;background:radial-gradient(circle at 15% 15%,#2f8b5b 0,#153d2a 38%,#0c261a 100%);display:grid;place-items:center;padding:24px;box-sizing:border-box}}
            .login-shell{{width:min(980px,100%);display:grid;grid-template-columns:1.05fr .95fr;background:#fff;border-radius:30px;overflow:hidden;box-shadow:0 30px 90px #06170f70}}
            .login-visual{{padding:54px;background:linear-gradient(145deg,#174a31,#23784b);color:#fff;display:flex;flex-direction:column;justify-content:space-between;min-height:510px}}
            .login-logo{{font-size:36px;font-weight:950;letter-spacing:-1px}}.login-visual h1{{font-size:42px;line-height:1.05;margin:24px 0 14px}}.login-visual p{{color:#dcece2;font-size:17px;line-height:1.6;max-width:430px}}.login-pills{{display:flex;flex-wrap:wrap;gap:8px}}.login-pills span{{padding:8px 11px;border-radius:999px;background:#ffffff17;border:1px solid #ffffff24;font-size:13px;font-weight:800}}
            .login-panel{{padding:54px 48px;display:flex;flex-direction:column;justify-content:center}}.login-panel h2{{font-size:30px;margin:0 0 8px;color:#173c29}}.login-sub{{color:#718276;margin-bottom:26px}}.login-version{{display:inline-flex;align-self:flex-start;background:#eef6f0;color:#557064;border-radius:999px;padding:7px 11px;font-weight:800;font-size:12px;margin-bottom:22px}}.login-form label{{display:block;font-size:13px;font-weight:850;margin:12px 0 6px;color:#263b30}}.login-form input{{width:100%;box-sizing:border-box;font-size:16px;padding:14px;border:1px solid #cfdcd2;border-radius:12px;background:#fbfdfb}}.password-wrap{{position:relative}}.password-wrap input{{padding-right:96px}}.password-toggle{{position:absolute;right:7px;top:50%;transform:translateY(-50%);border:0;background:#edf5ef;color:#176b3a;border-radius:9px;padding:8px 10px;font-weight:800;cursor:pointer}}.login-submit{{width:100%;margin-top:20px;min-height:50px;font-size:16px;border-radius:12px}}.forgot{{display:block;text-align:center;margin-top:16px;color:#176b3a;font-weight:800;text-decoration:none}}
            @media(max-width:760px){{body{{padding:8px;min-height:100dvh;align-items:start}}.login-shell{{grid-template-columns:1fr;border-radius:22px;margin:0 auto}}.login-visual{{min-height:auto;padding:20px 22px 18px}}.login-logo{{font-size:31px}}.login-visual h1{{font-size:28px;line-height:1.04;margin:12px 0 8px}}.login-visual p{{font-size:13.5px;line-height:1.45;margin:0 0 13px}}.login-pills{{gap:6px}}.login-pills span{{padding:6px 9px;font-size:11.5px}}.login-panel{{padding:22px 20px 24px}}.login-version{{margin-bottom:14px;padding:6px 9px;font-size:11px}}.login-panel h2{{font-size:27px}}.login-sub{{margin-bottom:17px;font-size:14px}}.login-form label{{margin:9px 0 5px}}.login-form input{{padding:12px;min-height:46px}}.password-wrap input{{padding-right:92px}}.password-toggle{{padding:7px 9px}}.login-submit{{margin-top:16px;min-height:48px}}.forgot{{margin-top:12px;padding-bottom:max(2px,env(safe-area-inset-bottom))}}}}
            </style></head><body><div class="login-shell"><section class="login-visual"><div><div class="login-logo">🐄 ÇiftlikPro</div><h1>Çiftliğinizin kontrol merkezi.</h1><p>Sürü, üreme, sağlık, besi ve finans yönetimini tek yerde güvenle takip edin.</p></div><div class="login-pills"><span>🐄 Sürü Yönetimi</span><span>💉 Sağlık</span><span>🌸 Üreme</span><span>📈 Besi</span><span>₺ Finans</span></div></section><section class="login-panel"><div class="login-version">ÇiftlikPro Enterprise • V{APP_VERSION}</div><h2>Hoş geldiniz</h2><div class="login-sub">Devam etmek için hesabınızla giriş yapın.</div>{login_msg}<form method="post" class="login-form"><label>Kullanıcı adı</label><input name="username" autocomplete="username" required autofocus><label>Şifre</label><div class="password-wrap"><input id="loginPassword" type="password" name="password" autocomplete="current-password" required><button class="password-toggle" type="button" onclick="toggleLoginPassword(this)">👁 Göster</button></div><button class="btn login-submit">Giriş Yap →</button><a class="forgot" href="/forgot-password">🔑 Şifremi Unuttum</a></form></section></div><script>function toggleLoginPassword(btn){{var p=document.getElementById('loginPassword');var show=p.type==='password';p.type=show?'text':'password';btn.textContent=show?'🙈 Gizle':'👁 Göster';}}</script></body></html>''')
        if path=='/forgot-password':
            step=(q.get('step',['request'])[0] or 'request');rid=(q.get('id',[''])[0] or '');token=(q.get('token',[''])[0] or '')
            notice=f'<div class="flash">{h(msg)}</div>' if msg else ''
            base_style='''<style>
            body{background:linear-gradient(145deg,#eef5f0,#f9fbfa);min-height:100vh}.reset-shell{max-width:520px;margin:6vh auto;background:#fff;border:1px solid #dce8df;border-radius:24px;padding:28px;box-shadow:0 18px 48px rgba(22,72,45,.11)}
            .reset-brand{font-size:27px;font-weight:900;color:#183c2a;margin-bottom:5px}.reset-sub{color:#6c7f73;margin-bottom:22px}.reset-shell label{display:block;font-weight:800;font-size:13px;margin-top:12px}.reset-shell input{width:100%;padding:13px;border:1px solid #cbd9cf;border-radius:10px;margin-top:5px;font-size:16px}.reset-actions{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap}.reset-actions .btn{flex:1}.code-box{text-align:center;letter-spacing:8px;font:900 24px Consolas,monospace}@media(max-width:600px){.reset-shell{margin:3vh 14px;padding:23px 20px}}</style>'''
            if step=='verify' and rid:
                content=f'''<div class="reset-brand">📧 Doğrulama Kodu</div><div class="reset-sub">E-postanıza gönderilen 6 haneli kodu girin. Kod 5 dakika geçerlidir.</div>{notice}<form method="post" action="/forgot-verify"><input type="hidden" name="reset_id" value="{h(rid)}"><label>6 Haneli Kod<input class="code-box" name="code" inputmode="numeric" pattern="[0-9]{{6}}" maxlength="6" autocomplete="one-time-code" required></label><div class="reset-actions"><button class="btn">Kodu Doğrula</button><a class="btn alt" href="/forgot-password">Başa Dön</a></div></form>'''
            elif step=='reset' and rid and token:
                content=f'''<div class="reset-brand">🔐 Yeni Şifre Belirle</div><div class="reset-sub">Doğrulama tamamlandı. Yeni şifrenizi oluşturun.</div>{notice}<form method="post" action="/forgot-reset"><input type="hidden" name="reset_id" value="{h(rid)}"><input type="hidden" name="token" value="{h(token)}"><label>Yeni Şifre<input type="password" name="password" minlength="8" required></label><label>Yeni Şifre Tekrar<input type="password" name="password_confirm" minlength="8" required></label><div class="reset-actions"><button class="btn">Şifreyi Değiştir</button></div></form>'''
            else:
                content=f'''<div class="reset-brand">🔑 Şifremi Unuttum</div><div class="reset-sub">Kullanıcı adınızı veya hesabınıza kayıtlı kurtarma e-postasını girin.</div>{notice}<form method="post" action="/forgot-password"><label>Kullanıcı Adı / Kurtarma E-postası<input name="identifier" autocomplete="username" required></label><div class="reset-actions"><button class="btn">📧 Kod Gönder</button><a class="btn alt" href="/login">Girişe Dön</a></div></form><p class="mut" style="margin-top:16px">Kod, kullanıcı hesabına tanımlı kurtarma e-postasına gönderilir.</p>'''
            return self.send_html(f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ÇiftlikPro Şifre Kurtarma</title><style>{CSS}</style>{base_style}</head><body><div class="reset-shell">🐄 <b>ÇiftlikPro Enterprise</b><hr style="border:0;border-top:1px solid #e6eee8;margin:16px 0">{content}</div></body></html>''')
        if path.startswith('/uploads/'):
            name=os.path.basename(path.split('/uploads/',1)[1]); fp=UPLOADS/name
            if not fp.exists(): return self.send_html('Fotoğraf bulunamadı',404)
            ext=fp.suffix.lower(); ctype={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp','gif':'image/gif'}.get(ext.lstrip('.'),'application/octet-stream')
            b=fp.read_bytes(); self.send_response(200); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        if path=='/logout':
            sid=self.parse_cookie(); SESSIONS.pop(sid,None); self.send_response(303);self.send_header('Set-Cookie','sid=; Max-Age=0; Path=/');self.send_header('Location','/login');self.end_headers();return
        if not self.require():return
        u=self.user()['username']
        if path=='/license-info':
            if not self.require_admin():return
            ok,payload,status=license_status();payload=payload or {}
            exp=payload.get('expires_on') or 'Süresiz'
            if exp!='Süresiz': exp=fmt_date(exp)
            badge_class='license-info-ok' if ok else 'license-info-bad'
            badge_text='🟢 Lisans Aktif' if ok else '🔴 Lisans Geçersiz'
            body=f'''<style>
.license-info-card{{background:#fff;border:1px solid #dfeae3;border-radius:22px;padding:26px;box-shadow:0 12px 35px rgba(20,80,48,.07)}}
.license-info-status{{display:inline-flex;padding:9px 14px;border-radius:999px;font-weight:800;margin-bottom:20px}}
.license-info-ok{{background:#e5f6eb;color:#14723d}}.license-info-bad{{background:#fff0ed;color:#ad3529}}
.license-info-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
.license-info-item{{background:#f5f9f6;border:1px solid #e2ece5;border-radius:14px;padding:15px}}
.license-info-item span{{display:block;color:#6d8075;font-size:12px;margin-bottom:5px;font-weight:700}}
.license-info-item b{{font-size:15px;color:#173b27;overflow-wrap:anywhere}}
.device-info{{grid-column:1/-1}}.device-row-info{{display:flex;align-items:center;gap:10px}}
.device-row-info b{{flex:1;font-family:Consolas,monospace}}
.copy-license-device{{border:0;border-radius:10px;background:#e2f1e7;color:#17683c;font-weight:800;padding:9px 13px;cursor:pointer}}
.license-note{{margin-top:18px;color:#6c7d73;line-height:1.55}}
@media(max-width:650px){{.license-info-grid{{grid-template-columns:1fr}}.device-info{{grid-column:auto}}.device-row-info{{align-items:stretch;flex-direction:column}}}}
</style>
<h1>🔐 Lisans Bilgileri</h1><div class="license-info-card">
<div class="license-info-status {badge_class}">{badge_text}</div>
<div class="license-info-grid">
<div class="license-info-item"><span>Lisans Sahibi</span><b>{h(payload.get('licensee') or '-')}</b></div>
<div class="license-info-item"><span>Ürün</span><b>{h(payload.get('product') or APP_NAME)}</b></div>
<div class="license-info-item"><span>Lisans Türü</span><b>{h(payload.get('license_type') or '-')}</b></div>
<div class="license-info-item"><span>Geçerlilik</span><b>{h(exp)}</b></div>
<div class="license-info-item device-info"><span>Cihaz Kimliği</span><div class="device-row-info"><b id="license-device-id">{h(device_id())}</b><button type="button" class="copy-license-device" onclick="copyLicenseDevice()">Kopyala</button></div></div>
<div class="license-info-item"><span>Durum</span><b>{h(status)}</b></div>
</div><div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px"><a class="btn" href="/license-test">🧪 Lisans Aktivasyonunu Test Et</a><a class="btn secondary" href="/license-change">🔄 Lisansı Değiştir</a></div><p class="license-note">Lisans bu bilgisayarın cihaz kimliğine ve dijital imzaya bağlıdır. Lisans verisinde yapılan yetkisiz değişiklikler dijital imzayı geçersiz kılar.</p></div>
<script>function copyLicenseDevice(){{var e=document.getElementById("license-device-id");if(!e)return;navigator.clipboard.writeText(e.innerText).then(function(){{var b=document.querySelector(".copy-license-device");b.innerText="Kopyalandı ✓";setTimeout(function(){{b.innerText="Kopyala"}},1500)}})}}</script>'''
            return self.send_html(page('Lisans Bilgileri',body,'/license-info',u,msg))
        if path=='/license-test':
            if not self.require_admin():return
            body=f'''<h1>🧪 Lisans Aktivasyon Testi</h1><div class="card"><p class="mut">Bu ekran yeni CFP anahtarını doğrular; mevcut aktif lisansınızı değiştirmez.</p><div class="kv"><div><b>Cihaz Kimliği</b><span><code id="testDeviceId">{h(device_id())}</code> <button type="button" class="btn alt compact-btn" onclick="copyDeviceSimple('testDeviceId',this)">📋 Kopyala</button></span></div></div><form method="post" action="/license-test" class="form" style="margin-top:18px"><label class="full">Test Edilecek Lisans Anahtarı<textarea name="license_key" rows="5" placeholder="CFP-XXXXX-XXXXX-..." required></textarea></label><div class="full"><button class="btn">🧪 Anahtarı Doğrula</button> <a class="btn secondary" href="/license-info">Geri Dön</a></div></form></div>'''
            return self.send_html(page('Lisans Aktivasyon Testi',body,'/license-info',u,msg))
        if path=='/license-change':
            if not self.require_admin():return
            body=f'''<h1>🔄 Lisansı Değiştir</h1><div class="card"><div class="flash" style="background:#fff4dc;color:#7c5600">Bu işlem doğrulanan yeni lisansı mevcut aktif lisansın yerine kaydeder.</div><div class="kv"><div><b>Cihaz Kimliği</b><span><code id="changeDeviceId">{h(device_id())}</code> <button type="button" class="btn alt compact-btn" onclick="copyDeviceSimple('changeDeviceId',this)">📋 Kopyala</button></span></div></div><form method="post" action="/license-change" class="form" style="margin-top:18px"><label class="full">Yeni Lisans Anahtarı<textarea name="license_key" rows="5" placeholder="CFP-XXXXX-XXXXX-..." required></textarea></label><label class="full" style="display:flex;gap:8px;align-items:center"><input type="checkbox" name="confirm_change" value="yes" required style="width:auto"> Mevcut lisansın yeni lisansla değiştirileceğini onaylıyorum.</label><div class="full"><button class="btn">🔄 Yeni Lisansı Etkinleştir</button> <a class="btn secondary" href="/license-info">İptal</a></div></form></div>'''
            return self.send_html(page('Lisansı Değiştir',body,'/license-info',u,msg))
        if path=='/password-change':
            body='''<h1>Şifremi Değiştir</h1><div class="card"><form method="post" action="/password-change" class="form"><label>Mevcut Şifre<input type="password" name="current_password" required></label><label>Yeni Şifre<input type="password" name="new_password" minlength="8" required></label><label>Yeni Şifre Tekrar<input type="password" name="new_password_confirm" minlength="8" required></label><div class="full"><button class="btn">Şifreyi Değiştir</button></div></form></div>'''
            return self.send_html(page('Şifremi Değiştir',body,'/password-change',u,msg))
        if path=='/farm-profile':
            if not self.require_admin():return
            p=farm_profile()
            logo=p.get('farm_logo','')
            logo_html=(f'<img class="farm-logo-preview" src="{h(logo)}" alt="Çiftlik logosu">' if logo else '<div class="farm-logo-placeholder">🏡</div>')
            body=f'''<h1>🏡 Çiftlik Profili / İşletme Tanımları</h1>
            <div class="card"><div class="farm-profile-head">{logo_html}<div><h2 style="margin:0 0 6px">{h(farm_display_name(p))}</h2><p class="mut" style="margin:0">Bu bilgiler Dashboard ve rapor başlıklarında kullanılacaktır.</p></div></div></div>
            <div class="card" style="margin-top:14px"><form method="post" action="/farm-profile" enctype="multipart/form-data" class="form">
            <label>Çiftlik / İşletme Adı<input name="farm_name" value="{h(p.get('farm_name'))}" placeholder="Örn. Erdoğmuş Çiftliği"></label>
            <label>İşletme Sahibi<input name="owner_name" value="{h(p.get('owner_name'))}"></label>
            <label>Telefon<input name="phone" value="{h(p.get('phone'))}" inputmode="tel"></label>
            <label>E-posta<input type="email" name="email" value="{h(p.get('email'))}"></label>
            <label>İl<input name="province" value="{h(p.get('province'))}"></label>
            <label>İlçe<input name="district" value="{h(p.get('district'))}"></label>
            <label>İşletme Numarası<input name="business_no" value="{h(p.get('business_no'))}"></label>
            <label>Vergi / TC (isteğe bağlı)<input name="tax_or_tc" value="{h(p.get('tax_or_tc'))}"></label>
            <label class="full">Adres<textarea name="address" rows="3">{h(p.get('address'))}</textarea></label>
            <div class="full"><h2 style="margin:8px 0 0">Veteriner İletişim Bilgileri</h2></div>
            <label>Veteriner Adı<input name="vet_name" value="{h(p.get('vet_name'))}"></label>
            <label>Veteriner Telefonu<input name="vet_phone" value="{h(p.get('vet_phone'))}" inputmode="tel"></label>
            <label>Veteriner E-posta<input type="email" name="vet_email" value="{h(p.get('vet_email'))}"></label>
            <label>Çiftlik Logosu<input type="file" name="farm_logo_file" accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"><span class="camera-note">JPG, PNG veya WebP · En fazla 5 MB</span></label>
            <label class="full">Notlar<textarea name="notes" rows="4">{h(p.get('notes'))}</textarea></label>
            <label class="full" style="display:flex;flex-direction:row;align-items:center;gap:8px"><input type="checkbox" name="remove_logo" value="1" style="width:auto"> Mevcut logoyu kaldır</label>
            <div class="full"><button class="btn">💾 Çiftlik Profilini Kaydet</button></div>
            </form></div>'''
            return self.send_html(page('Çiftlik Profili',body,'/farm-profile',u,msg))
        if path=='/smtp-settings':
            if not self.require_admin():return
            cfg=smtp_config();sec=cfg['security']
            body=f'''<h1>📧 E-posta / Şifre Kurtarma Ayarları</h1><div class="two"><div class="card"><h2>SMTP Ayarları</h2><form method="post" action="/smtp-settings" class="form"><label>SMTP Sunucusu<input name="smtp_host" value="{h(cfg['host'])}" required></label><label>Port<input type="number" name="smtp_port" value="{cfg['port']}" required></label><label>Güvenlik<select name="smtp_security"><option value="starttls" {'selected' if sec=='starttls' else ''}>STARTTLS</option><option value="ssl" {'selected' if sec=='ssl' else ''}>SSL/TLS</option><option value="none" {'selected' if sec=='none' else ''}>Yok</option></select></label><label>SMTP Kullanıcı<input name="smtp_username" value="{h(cfg['username'])}"></label><label>Gönderen E-posta<input type="email" name="smtp_sender" value="{h(cfg['sender'])}" required></label><label>SMTP / Uygulama Şifresi<input type="password" name="smtp_password" placeholder="Değiştirmeyecekseniz boş bırakın"></label><div class="full"><button class="btn">💾 Ayarları Kaydet</button></div></form></div><div class="card"><h2>Test E-postası</h2><p class="mut">Sağlayıcınız iki aşamalı doğrulama kullanıyorsa normal hesap şifresi yerine uygulama şifresi kullanın.</p><form method="post" action="/smtp-settings" class="form"><input type="hidden" name="action" value="test"><label class="full">Test Adresi<input type="email" name="test_email" required></label><div class="full"><button class="btn blue">📨 Test E-postası Gönder</button></div></form></div></div>'''
            return self.send_html(page('E-posta Ayarları',body,'/users',u,msg))
        if path=='/users':
            if not self.require_admin():return
            with db() as c:rows=c.execute('select id,username,full_name,recovery_email,role,active,last_login from users order by username').fetchall()
            trs=''.join(f'''<tr><td>{h(r["full_name"])}</td><td>{h(r["username"])}</td><td>{h(r["recovery_email"]) or '-'}</td><td>{'Yönetici' if r["role"]=='admin' else 'Personel'}</td><td>{'Aktif' if r["active"] else 'Pasif'}</td><td>{fmt_datetime(r["last_login"]) if r["last_login"] else '-'}</td><td><a class="btn alt" href="/users/edit?id={r["id"]}">Düzenle</a></td></tr>''' for r in rows)
            body=f'''<h1>Kullanıcı Yönetimi</h1><div class="two"><div class="card"><h2>Yeni Kullanıcı</h2><form method="post" action="/users/create" class="form"><label>Ad Soyad<input name="full_name" required></label><label>Kullanıcı Adı<input name="username" required></label><label>Kurtarma E-postası<input type="email" name="recovery_email" required></label><label>Şifre<input type="password" name="password" minlength="8" required></label><label>Rol<select name="role"><option value="personel">Personel</option><option value="admin">Yönetici</option></select></label><div class="full"><button class="btn">Kullanıcı Oluştur</button></div></form></div><div class="card"><h2>Güvenlik</h2><p class="mut">Şifreler PBKDF2-SHA256 ile saklanır. Şifre kurtarma kodları 5 dakika geçerli ve tek kullanımlıktır.</p><a class="btn alt" href="/smtp-settings">📧 E-posta Ayarları</a></div></div><div class="card" style="margin-top:14px"><table><tr><th>Ad Soyad</th><th>Kullanıcı</th><th>Kurtarma E-postası</th><th>Rol</th><th>Durum</th><th>Son Giriş</th><th>İşlem</th></tr>{trs}</table></div>'''
            return self.send_html(page('Kullanıcı Yönetimi',body,'/users',u,msg))
        if path=='/users/edit':
            if not self.require_admin():return
            uid=q.get('id',[''])[0]
            with db() as c:r=c.execute('select * from users where id=?',(uid,)).fetchone()
            if not r:return self.send_html('Kullanıcı bulunamadı',404)
            body=f'''<h1>Kullanıcı Düzenle</h1><div class="card"><form method="post" action="/users/update" class="form"><input type="hidden" name="id" value="{r["id"]}"><label>Ad Soyad<input name="full_name" value="{h(r["full_name"])}" required></label><label>Kurtarma E-postası<input type="email" name="recovery_email" value="{h(r["recovery_email"])}" required></label><label>Rol<select name="role"><option value="personel" {'selected' if r["role"]=='personel' else ''}>Personel</option><option value="admin" {'selected' if r["role"]=='admin' else ''}>Yönetici</option></select></label><label>Durum<select name="active"><option value="1" {'selected' if r["active"] else ''}>Aktif</option><option value="0" {'selected' if not r["active"] else ''}>Pasif</option></select></label><label>Yeni Şifre<input type="password" name="new_password" minlength="8"></label><div class="full"><button class="btn">Kaydet</button> <a class="btn alt" href="/users">İptal</a></div></form></div>'''
            return self.send_html(page('Kullanıcı Düzenle',body,'/users',u,msg))
        if path=='/audit-log':
            if not self.require_admin():return
            with db() as c:rows=c.execute('select * from audit_log order by id desc limit 300').fetchall()
            trs=''.join(f'<tr><td>{fmt_datetime(r["created_at"])}</td><td>{h(r["username"])}</td><td>{h(r["action"])}</td><td>{h(r["detail"])}</td><td>{h(r["ip_address"])}</td></tr>' for r in rows) or '<tr><td colspan=5>Kayıt yok.</td></tr>'
            body=f'''<h1>İşlem Günlüğü</h1><div class="card"><table><tr><th>Tarih</th><th>Kullanıcı</th><th>İşlem</th><th>Detay</th><th>IP</th></tr>{trs}</table></div>'''
            return self.send_html(page('İşlem Günlüğü',body,'/audit-log',u,msg))
        promote_mature_calves()
        if path=='/':
            profile=farm_profile()
            farm_name=farm_display_name(profile)
            edit_dashboard=(q.get('edit',['0'])[0]=='1')
            dash_layout=dashboard_layout(u)
            with db() as c:
                animals=c.execute("select count(*) from animals where gender='Dişi' and status='Aktif'").fetchone()[0]
                males=c.execute("select count(*) from animals where gender='Erkek' and status='Aktif'").fetchone()[0]
                calves=c.execute('select count(*) from calves where promoted_animal_id is null').fetchone()[0]
                total_inc=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gelir'").fetchone()[0]
                total_exp=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gider'").fetchone()[0]
                pregnant=c.execute("select count(distinct animal_id) from inseminations where pregnancy_result='Pozitif'").fetchone()[0]
                active_total=animals+males+calves
                active_male_records=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif')='Aktif'").fetchall()
                # Gerçekleşmiş besi maliyetinde kesilen hayvanlar kaybolmaz; maliyetleri kesim tarihinde donar.
                male_cost_records=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif') in ('Aktif','Kesildi')").fetchall()
                male_purchase_total=sum(float(r['purchase_price'] or 0) for r in male_cost_records)
                male_operating_cost=sum(animal_cost_values(r)[2] for r in male_cost_records)
                male_current_cost=male_purchase_total+male_operating_cost
                slaughtered_male_records=[r for r in male_cost_records if str(r['status'] or '')=='Kesildi']
                active_male_count=len(active_male_records)
                slaughtered_male_count=len(slaughtered_male_records)
                active_male_cost=sum(animal_cost_values(r)[3] for r in active_male_records)
                slaughtered_male_cost=sum(animal_cost_values(r)[3] for r in slaughtered_male_records)
                active_male_purchase=sum(float(r['purchase_price'] or 0) for r in active_male_records)
                slaughtered_male_purchase=sum(float(r['purchase_price'] or 0) for r in slaughtered_male_records)
                active_male_operating=sum(animal_cost_values(r)[2] for r in active_male_records)
                slaughtered_male_operating=sum(animal_cost_values(r)[2] for r in slaughtered_male_records)
                targeted_males=[r for r in active_male_records if float(r['target_sale_price'] or 0)>0]
                male_target_sales=sum(float(r['target_sale_price'] or 0) for r in targeted_males)
                male_target_cost=sum(animal_cost_values(r)[3] for r in targeted_males)
                male_target_profit=male_target_sales-male_target_cost if targeted_males else None
                min_daily_gain=setting_float('male_min_daily_gain',1.0)
                male_performance=[]
                for mr in active_male_records:
                    perf=male_weight_performance(mr['id'],c)
                    if perf['daily'] is not None: male_performance.append((mr,perf))
                low_performance=[x for x in male_performance if x[1]['status']=='low']
                watch_performance=[x for x in male_performance if x[1]['status']=='watch']
                due_rows=c.execute("select i.due_date,a.id,a.tag,a.nickname from inseminations i join animals a on a.id=i.animal_id where i.pregnancy_result='Pozitif' and i.due_date between ? and ? order by i.due_date limit 8",(date.today().isoformat(),(date.today()+timedelta(days=45)).isoformat())).fetchall()
                health_rows=c.execute("select h.id,h.next_date,h.kind,h.product,h.notes,h.animal_id,h.calf_id,a.id as adult_id,a.tag as animal_tag,ca.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves ca on ca.id=h.calf_id where coalesce(h.next_date,'')<>'' and h.next_date<=? order by h.next_date limit 10",((date.today()+timedelta(days=30)).isoformat(),)).fetchall()
                pregnancy_vaccines=pregnancy_vaccine_tasks(c,horizon_days=7)
                estrus_dash_all=c.execute("select e.*,a.tag,a.nickname from estrus_records e join animals a on a.id=e.animal_id where a.gender='Dişi' and coalesce(a.status,'Aktif')='Aktif' order by e.estrus_date desc,e.id desc").fetchall()
                estrus_dash_rows=[r for r in estrus_dash_all if not is_currently_pregnant(c,r['animal_id'])]
                months=[]
                for n in range(5,-1,-1):
                    d=(date.today().replace(day=1)-timedelta(days=n*31)).replace(day=1); key=d.strftime('%Y-%m')
                    inc=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gelir' and substr(tx_date,1,7)=?",(key,)).fetchone()[0]
                    exp=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gider' and substr(tx_date,1,7)=?",(key,)).fetchone()[0]
                    months.append((d.strftime('%m/%y'),inc,exp))
            estrus_latest={}
            for er in estrus_dash_rows:
                if er['animal_id'] not in estrus_latest: estrus_latest[er['animal_id']]=er
            estrus_upcoming=[]; today=date.today()
            for er in estrus_latest.values():
                cycle=next_estrus_cycle(c,er,today)
                if cycle and cycle['end']>=today and cycle['start']<=today+timedelta(days=30):
                    estrus_upcoming.append((cycle['start'],cycle['center'],cycle['end'],er,cycle['cycle_no']))
            estrus_upcoming.sort(key=lambda x:x[1])
            estrus_dashboard_cards=[]
            for es,ec,ee,er,cycle_no in estrus_upcoming[:8]:
                in_window=es<=today<=ee
                if in_window:
                    action=f'''<form method="post" action="/estrus-inseminate" onsubmit="return confirm('Bu hayvan bugün tohumlandı olarak Tohumlama kayıtlarına aktarılsın mı?')"><input type="hidden" name="estrus_id" value="{er['id']}"><button class="btn orange">🌱 Bugün Tohumlandı</button></form>'''
                else:
                    action=f'''<form method="post" action="/estrus-send" onsubmit="return confirm('Bu hayvan Tohumlama Takibi ekranına gönderilsin mi? Ana sayfadaki bu kızgınlık kartı kapanacaktır.')"><input type="hidden" name="estrus_id" value="{er['id']}"><input type="hidden" name="cycle_no" value="{cycle_no}"><button class="btn orange">🌱 Tohumlamaya Gönder</button></form>'''
                estrus_dashboard_cards.append(f'''<div class="alertitem {'estrus-window-now' if in_window else 'estrus-window-next'}"><b>🌸 <a class="taglink" href="/animal?id={er['animal_id']}">{h(er['tag'])} {h(er['nickname'])}</a></b><br><span class="mut">{fmt_date(es.isoformat())} – {fmt_date(ee.isoformat())} · En olası {fmt_date(ec.isoformat())}</span><div class="estrus-actions">{action}<form method="post" action="/estrus-skip" onsubmit="return confirm('Bu östrus dönemi atlandı olarak işaretlenecek. Emin misiniz?')"><input type="hidden" name="estrus_id" value="{er['id']}"><input type="hidden" name="cycle_no" value="{cycle_no}"><input type="hidden" name="return_to" value="/"><button class="btn alt">⏭️ Bu Östrusu Atla</button></form><a class="btn alt" href="/estrus">Kızgınlık Takibi</a></div></div>''')
            estrus_dashboard_html=''.join(estrus_dashboard_cards) or '<p class="mut">Önümüzdeki 30 gün için beklenen kızgınlık yok.</p>'
            net=total_inc-total_exp; maxv=max([max(x[1],x[2]) for x in months]+[1])
            bars=''.join(f'<div class="mini-col"><b title="Gelir {money(i)}" style="height:{max(2,int(i/maxv*100))}%"></b><i title="Gider {money(e)}" style="height:{max(2,int(e/maxv*100))}%"></i><span>{h(m)}</span></div>' for m,i,e in months)
            due_html=''.join(f'<div class="alertitem">🐄 <a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])} {h(r["nickname"])}</a><br><span class="mut">Tahmini doğum: {fmt_date(r["due_date"])}</span></div>' for r in due_rows) or '<p class="mut">45 gün içinde beklenen doğum yok.</p>'
            def health_task_html(r):
                tag=r["animal_tag"] or r["calf_tag"] or "Genel"
                try:days=(date.fromisoformat(r["next_date"])-date.today()).days
                except:days=9999
                if days<0:label=f'GECİKTİ · {abs(days)} gün';style='border-left-color:#c8392b;background:#fff1f0'
                elif days==0:label='BUGÜN';style='border-left-color:#e27b1f;background:#fff6e8'
                elif days<=3:label=f'{days} gün kaldı';style='border-left-color:#e27b1f;background:#fff6e8'
                else:label=f'{days} gün kaldı';style='border-left-color:#e2a21f;background:#fff9e8'
                action=''
                if str(r["kind"] or '')=='Aşı' and 'IKINCI_DOZ_PLAN' in str(r["notes"] or ''):
                    action=f'<form method="post" action="/health/second-dose-done" class="actions" style="margin-top:8px"><input type="hidden" name="source_id" value="{r["id"]}"><input type="hidden" name="return_to" value="/"><button class="btn">✅ 2. Doz Yapıldı</button><a class="btn alt" href="/health">Sağlığı Aç</a></form>'
                return f'<div class="alertitem" style="{style}"><b>💉 {h(tag)} · {h(r["kind"])}</b><br><span class="mut">{h(r["product"])} · {fmt_date(r["next_date"])} · {label}</span>{action}</div>'
            health_html=''.join(health_task_html(r) for r in health_rows) or '<p class="mut">30 gün içinde planlanan/geciken sağlık işlemi yok.</p>'
            def vaccine_task_html(t):
                if t['overdue']:
                    label=f"GECİKTİ · {abs(t['days_left'])} gün"; style='border-left-color:#c8392b;background:#fff1f0'
                elif t['today']:
                    label='BUGÜN YAPILMALI'; style='border-left-color:#e27b1f;background:#fff6e8'
                else:
                    label=f"{t['days_left']} gün kaldı"; style='border-left-color:#e2a21f;background:#fff9e8'
                return f'<div class="alertitem" style="{style}"><b>💉 {h(t["tag"])} · {t["month"]}. Ay Gebelik Aşısı</b><br><span class="mut">Planlanan: {fmt_date(t["task_date"])} · {label}</span><form method="post" action="/pregnancy-vaccine/done" class="actions" style="margin-top:8px"><input type="hidden" name="animal_id" value="{t["animal_id"]}"><input type="hidden" name="insemination_id" value="{t["insemination_id"]}"><input type="hidden" name="month" value="{t["month"]}"><input type="hidden" name="return_to" value="/"><button class="btn">✅ Aşı Yapıldı</button><a class="btn alt" href="/animal?id={t["animal_id"]}">Hayvanı Aç</a></form></div>'
            pregnancy_vaccine_html=''.join(vaccine_task_html(t) for t in pregnancy_vaccines) or '<p class="mut">7 gün içinde 7./8. ay gebelik aşısı görevi yok.</p>'
            target_profit_text=money(male_target_profit) if male_target_profit is not None else '—'
            target_profit_class='red' if male_target_profit is not None and male_target_profit<0 else 'green'
            target_profit_color='#c8392b' if male_target_profit is not None and male_target_profit<0 else '#176b3a'
            performance_warning_html=''.join(f'<div class="alertitem" style="border-left-color:#c8392b">⚠️ <a class="taglink" href="/animal?id={r[0]["id"]}">{h(r[0]["tag"])} {h(r[0]["nickname"])}</a><br><span class="mut">{r[1]["daily"]:.3f} kg/gün · Hedef {min_daily_gain:.2f} kg/gün</span></div>' for r in low_performance[:8]) or '<p class="mut">Kritik seviyede düşük kilo artışı olan erkek yok.</p>'
            dash_cards={
                'active_total':f'<a class="card stat metric green summary-link" href="/all-animals"><span class="metric-icon">🐄</span>Toplam Aktif Hayvan<b>{active_total}</b><small>Tüm hayvanları aç →</small></a>',
                'female':f'<a class="card stat metric green summary-link" href="/animals"><span class="metric-icon">🐮</span>Dişi Hayvan<b>{animals}</b><small>Listeyi aç →</small></a>',
                'male':f'<a class="card stat metric blue summary-link" href="/males"><span class="metric-icon">🐂</span>Erkek Hayvan<b>{males}</b><small>Listeyi aç →</small></a>',
                'pregnant':f'<a class="card stat metric orange summary-link" href="/inseminations"><span class="metric-icon">🤰</span>Gebe Hayvan<b>{pregnant}</b><small>Gebelikleri aç →</small></a>',
                'calves':f'<a class="card stat metric teal summary-link" href="/calves"><span class="metric-icon">🐮</span>Buzağı<b>{calves}</b><small>Listeyi aç →</small></a>',
                'due':f'<a class="card stat metric purple summary-link" href="#approaching-births"><span class="metric-icon">📅</span>Yaklaşan Doğum<b>{len(due_rows)}</b><small>Detaya git ↓</small></a>',
                'estrus':f'<a class="card stat metric green summary-link" href="#approaching-estrus"><span class="metric-icon">🌸</span>Yaklaşan Kızgınlık<b>{len(estrus_upcoming)}</b><small>Detaya git ↓</small></a>',
                'income':f'<a class="card stat metric green summary-link" href="/finance?type=Gelir"><span class="metric-icon">📥</span>Toplam Gelir<b>{money(total_inc)}</b><small>Gelirleri aç →</small></a>',
                'expense':f'<a class="card stat metric red summary-link" href="/finance?type=Gider"><span class="metric-icon">📤</span>Toplam Gider<b>{money(total_exp)}</b><small>Giderleri aç →</small></a>',
                'net':f'<a class="card stat metric {"red" if net<0 else "green"} summary-link" href="/finance"><span class="metric-icon">⚖️</span>Net Durum<b>{money(net)}</b><small>Finansı aç →</small></a>',
            }
            card_meta={
                'active_total':('🐄','Toplam Aktif Hayvan','Sürüdeki toplam aktif kayıt'),
                'female':('🐮','Dişi Hayvan','Aktif dişi hayvan sayısı'),
                'male':('🐂','Erkek Hayvan','Aktif erkek hayvan sayısı'),
                'pregnant':('🤰','Gebe Hayvan','Pozitif gebelik kayıtları'),
                'calves':('🐮','Buzağı','Aktif buzağı kayıtları'),
                'due':('📅','Yaklaşan Doğum','Yaklaşan doğum sayısı'),
                'estrus':('🌸','Yaklaşan Kızgınlık','Takip penceresindeki hayvanlar'),
                'income':('📥','Toplam Gelir','Tüm gelirlerin toplamı'),
                'expense':('📤','Toplam Gider','Tüm giderlerin toplamı'),
                'net':('⚖️','Net Durum','Gelir eksi gider'),
            }
            dash_slots=[]
            for slot,key in enumerate(dash_layout):
                card=dash_cards.get(key,'')
                if edit_dashboard:
                    if card:
                        card=card+f'<button type="button" class="dashboard-slot-plus" title="Bu kartı değiştir" onclick="openDashboardPicker({slot},\'{h(key)}\')">+</button>'
                    else:
                        card=f'''<div class="dashboard-empty-slot" onclick="openDashboardPicker({slot},'')"><div><div class="plus-icon">+</div><small>Bu yuvaya kart ekle</small></div></div>'''
                    cls='dashboard-slot editing'
                else:
                    if not card: continue
                    cls='dashboard-slot'
                dash_slots.append(f'<div class="{cls}">{card}</div>')
            dashboard_summary_html=''.join(dash_slots)
            gallery_choices=''.join(f'''<button type="button" class="dashboard-card-choice" data-key="{h(k)}" onclick="chooseDashboardCard('{h(k)}')"><span class="choice-icon">{card_meta[k][0]}</span><span><b>{h(card_meta[k][1])}</b><small>{h(card_meta[k][2])}</small></span></button>''' for k,_ in DASHBOARD_CARD_OPTIONS)
            dashboard_picker_html=f'''<div class="dashboard-picker-backdrop" id="dashboardPicker" onclick="if(event.target===this)closeDashboardPicker()"><div class="dashboard-picker"><div class="dashboard-picker-head"><div><h2>Dashboard Kartı Seç</h2><p>Seçtiğiniz kart bu yuvaya anında yerleşir.</p></div><button type="button" class="dashboard-picker-close" onclick="closeDashboardPicker()">×</button></div><div class="dashboard-card-gallery">{gallery_choices}</div><div class="dashboard-picker-footer"><button type="button" class="btn red" onclick="chooseDashboardCard('')">Yuvayı Boşalt</button><span class="mut">Daha sonra tekrar ekleyebilirsiniz.</span></div><form id="dashboardPickerForm" method="post" action="/dashboard-layout"><input type="hidden" name="slot" id="dashboardPickerSlot"><input type="hidden" name="card_key" id="dashboardPickerKey"></form></div></div><script>function openDashboardPicker(slot,current){{document.getElementById('dashboardPickerSlot').value=slot;document.getElementById('dashboardPicker').classList.add('open');document.querySelectorAll('.dashboard-card-choice').forEach(function(b){{b.classList.toggle('active',b.dataset.key===current);}});}}function closeDashboardPicker(){{document.getElementById('dashboardPicker').classList.remove('open');}}function chooseDashboardCard(key){{document.getElementById('dashboardPickerKey').value=key;document.getElementById('dashboardPickerForm').submit();}}document.addEventListener('keydown',function(e){{if(e.key==='Escape')closeDashboardPicker();}});</script>'''
            dashboard_logo=(f'<img class="farm-hero-logo" src="{h(profile.get("farm_logo"))}" alt="Çiftlik logosu">' if profile.get('farm_logo') else '')
            body=f'''<div class="hero"><div class="farm-hero">{dashboard_logo}<div><h1>{h(farm_name)}</h1><div>ÇiftlikPro · Bugünün sürü, sağlık ve finans görünümü</div></div></div><div><a class="btn orange" href="/backup/create">💾 Hemen Yedek Al</a></div></div>
            <div class="dashboard-editbar"><a class="btn alt" href="/{'?' if edit_dashboard else '?edit=1'}">{'✅ Düzenlemeyi Bitir' if edit_dashboard else '⚙️ Dashboard’u Düzenle'}</a></div>
            <div class="dashboard-section-title"><h2>Dashboard Kartlarım</h2><span>{'Kartın üzerindeki + işaretine dokunarak değiştirebilirsiniz' if edit_dashboard else 'Size özel hızlı görünüm'}</span></div>
            <div class="grid summary-grid">{dashboard_summary_html}</div>{dashboard_picker_html if edit_dashboard else ''}
            <div class="dashboard-section-title" id="approaching-estrus"><h2>🌸 Yaklaşan Kızgınlıklar</h2><span>Son kızgınlık kaydına göre 18–24 günlük takip penceresi</span></div><div class="card"><div class="alertlist">{estrus_dashboard_html}</div></div>
            <div class="card" style="display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap;margin-top:16px"><div><h2 style="margin:0 0 6px">🐂 Besi Performansı</h2><p class="mut" style="margin:0">Aktif ve kesilen erkekleri; alım tarihi, kesim tarihi, kilo performansı ve gerçekleşmiş maliyete göre inceleyin.</p></div><a class="btn blue" href="/performance">Besi Analizine Git →</a></div>
            <div class="dashboard-section-title"><h2>🚨 Gebelik Aşı Alarmı</h2><span>7. ve 8. ay aşıları yapılana kadar uyarı devam eder</span></div><div class="card"><div class="alertlist">{pregnancy_vaccine_html}</div></div>
            <div class="dashboard-section-title"><h2>Finans Özeti</h2><span>Gelir ve giderlerin genel görünümü</span></div><div class="grid"><div class="card stat metric green"><span class="metric-icon">📥</span>Toplam Gelir<b style="color:#176b3a">{money(total_inc)}</b></div><div class="card stat metric red"><span class="metric-icon">📤</span>Toplam Gider<b style="color:#c8392b">{money(total_exp)}</b></div><div class="card stat metric {'red' if net<0 else 'green'}"><span class="metric-icon">⚖️</span>Net Durum<b style="color:{'#c8392b' if net<0 else '#176b3a'}">{money(net)}</b></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>Son 6 Ay Finans Eğilimi</h2><div class="mut">Yeşil: gelir · Kırmızı: gider</div><div class="mini-chart">{bars}</div></div><div class="card"><h2>Hızlı İşlemler</h2><p class="mut">Detaylı finans hareketleri Finans bölümünde tutulur.</p><div class="actions"><a class="btn blue" href="/finance">Finans Kaydı</a><a class="btn alt" href="/health">Sağlık Kaydı</a><a class="btn alt" href="/reports">Finans Raporları</a></div></div></div><div class="two" style="margin-top:14px"><div class="card" id="approaching-births"><h2>Yaklaşan Doğumlar</h2><div class="alertlist">{due_html}</div></div><div class="card"><h2>Yaklaşan Aşı / Sağlık</h2><div class="alertlist">{health_html}</div></div></div>'''
            with db() as c:
                month_key=date.today().strftime('%Y-%m')
                month_milk_income=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gelir' and category in ('Süt Satışı','Süt Geliri') and substr(tx_date,1,7)=?",(month_key,)).fetchone()[0]
                month_cut_income=c.execute("select coalesce(sum(amount),0) from finance where tx_type='Gelir' and category='Kesim Geliri' and substr(tx_date,1,7)=?",(month_key,)).fetchone()[0]
                recent_weights=c.execute("select count(*) from weights where measure_date>=?",((date.today()-timedelta(days=30)).isoformat(),)).fetchone()[0]
            body += f'''<div class="card" style="margin-top:14px"><h2>İşletme Özeti</h2><div class="grid business-summary-grid"><div class="card stat metric blue">Bu Ay Süt Geliri<b>{money(month_milk_income)}</b></div><div class="card stat metric green">Bu Ay Kesim Geliri<b>{money(month_cut_income)}</b></div><div class="card stat metric orange">30 Günlük Kilo Kaydı<b>{recent_weights}</b></div></div><div class="actions"><a class="btn" href="/animal-add">+ Hayvan Ekle</a><a class="btn alt" href="/reports">Raporları Aç</a></div></div>'''
            # V3.9.20: Dashboard uzunluğunu azaltan açılır/kapanır bölümler.
            fold_js='''<script>(function(){var titles=[].slice.call(document.querySelectorAll('.dashboard-section-title'));titles.forEach(function(t,i){if(i===0)return;var key='cp_dash_section_'+i;var saved=localStorage.getItem(key);var open=saved===null?(i<3):saved==='1';var nodes=[];for(var n=t.nextElementSibling;n&&!(n.classList&&n.classList.contains('dashboard-section-title'));n=n.nextElementSibling)nodes.push(n);t.style.cursor='pointer';var hint=t.querySelector('span');if(hint)hint.dataset.original=hint.textContent;function paint(){nodes.forEach(function(x){x.style.display=open?'':'none'});if(hint)hint.textContent=(open?'▲ ':'▼ ')+(hint.dataset.original||'');}t.addEventListener('click',function(){open=!open;localStorage.setItem(key,open?'1':'0');paint()});paint();});})();</script>'''
            # Büyük dashboard bloklarını başlıklarına göre istemci tarafında kompaktlaştır.
            body += fold_js
            return self.send_html(page('Profesyonel Dashboard',body,'/',u,msg))

        if path=='/cost-details':
            search=(q.get('search',[''])[0] or '').strip()
            status=(q.get('status',['all'])[0] or 'all').lower()
            if status not in ('all','active','cut'): status='all'
            try: per_page=int(q.get('per_page',['20'])[0])
            except: per_page=20
            if per_page not in (10,20,50): per_page=20
            try: page_no=max(1,int(q.get('page',['1'])[0]))
            except: page_no=1
            with db() as c:
                all_cost_rows=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif') in ('Aktif','Kesildi') order by tag").fetchall()
            filtered=[]
            needle=search.casefold()
            for r in all_cost_rows:
                rs=str(r['status'] or 'Aktif')
                if status=='active' and rs!='Aktif': continue
                if status=='cut' and rs!='Kesildi': continue
                hay=(str(r['tag'] or '')+' '+str(r['nickname'] or '')).casefold()
                if needle and needle not in hay: continue
                filtered.append(r)
            total_count=len(filtered)
            total_pages=max(1,(total_count+per_page-1)//per_page)
            if page_no>total_pages: page_no=total_pages
            offset=(page_no-1)*per_page
            shown=filtered[offset:offset+per_page]
            def cost_detail_tr(r):
                days,daily,operating,total=animal_cost_values(r)
                purchase=float(r['purchase_price'] or 0)
                start=r['purchase_date'] or r['birth_date'] or '-'
                is_cut=str(r['status'] or '')=='Kesildi'
                end=(r['exit_date'] or '-') if is_cut else 'Bugün'
                badge='<span class="perf-badge status-low">Kesildi</span>' if is_cut else '<span class="perf-badge status-good">Aktif</span>'
                note='<br><span class="mut">Kesim tarihinde donduruldu</span>' if is_cut else ''
                return f'<tr><td><a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])}</a><br><span class="mut">{h(r["nickname"])}</span></td><td>{badge}</td><td>{fmt_date(start)}</td><td>{fmt_date(end)}</td><td><b>{days} gün</b>{note}</td><td>{money(purchase)}</td><td>{money(operating)}</td><td><b>{money(total)}</b></td></tr>'
            detail_rows=''.join(cost_detail_tr(r) for r in shown) or '<tr><td colspan="8">Bu filtreye uygun hayvan bulunamadı.</td></tr>'
            active_rows=[r for r in filtered if str(r['status'] or '')=='Aktif']
            cut_rows=[r for r in filtered if str(r['status'] or '')=='Kesildi']
            purchase_sum=sum(float(r['purchase_price'] or 0) for r in filtered)
            operating_sum=sum(animal_cost_values(r)[2] for r in filtered)
            total_sum=sum(animal_cost_values(r)[3] for r in filtered)
            def page_url(n):
                return '/cost-details?'+urllib.parse.urlencode({'search':search,'status':status,'per_page':per_page,'page':n})
            pager=[]
            if page_no>1: pager.append(f'<a class="btn alt" href="{h(page_url(page_no-1))}">← Önceki</a>')
            pager.append(f'<span class="pill">Sayfa <b>{page_no}</b> / {total_pages}</span>')
            if page_no<total_pages: pager.append(f'<a class="btn alt" href="{h(page_url(page_no+1))}">Sonraki →</a>')
            status_options=''.join(f'<option value="{v}" {"selected" if status==v else ""}>{label}</option>' for v,label in [('all','Tümü'),('active','Sadece Aktif'),('cut','Sadece Kesilen')])
            per_options=''.join(f'<option value="{n}" {"selected" if per_page==n else ""}>{n} kayıt</option>' for n in (10,20,50))
            body=f'''<div class="hero"><div><h1>🐂 Erkek Hayvan Maliyet Detayı</h1><div>Dashboard kısa kalır; bütün maliyet kaynaklarını burada inceleyebilirsiniz.</div></div><div><a class="btn alt" href="/">← Dashboard</a></div></div>
            <div class="grid"><div class="card stat metric blue"><span class="metric-icon">🐂</span>Aktif Erkek<b>{len(active_rows)}</b></div><div class="card stat metric red"><span class="metric-icon">🥩</span>Kesilen Erkek<b>{len(cut_rows)}</b></div><div class="card stat metric orange"><span class="metric-icon">🌾</span>Yem + Bakım<b>{money(operating_sum)}</b></div><div class="card stat metric green"><span class="metric-icon">💰</span>Filtre Toplamı<b>{money(total_sum)}</b><small>Alış {money(purchase_sum)}</small></div></div>
            <div class="card" style="margin-top:14px"><form method="get" action="/cost-details" class="actions"><input name="search" value="{h(search)}" placeholder="Küpe veya takma ad ara" style="min-width:240px"><select name="status">{status_options}</select><select name="per_page">{per_options}</select><button class="btn">Filtrele</button><a class="btn alt" href="/cost-details">Temizle</a></form><p class="mut">{total_count} kayıt bulundu. Kesilen hayvanın maliyet günü kesim tarihinde durur; aktif hayvanın maliyeti bugüne kadar devam eder.</p></div>
            <div class="card" style="margin-top:14px"><div style="overflow-x:auto"><table><tr><th>Küpe</th><th>Durum</th><th>Başlangıç</th><th>Maliyet Bitişi</th><th>Maliyet Günü</th><th>Alış</th><th>Yem + Bakım</th><th>Toplam</th></tr>{detail_rows}</table></div><div class="actions" style="justify-content:center;margin-top:16px">{''.join(pager)}</div></div>'''
            return self.send_html(page('Maliyet Detayı',body,'',u,msg))

        if path=='/performance-settings':
            target=setting_float('male_min_daily_gain',1.0); ratio=setting_float('male_warning_ratio',0.90)
            body=f"""<h1>Besi Performans Ayarları</h1><div class="card setting-box"><form method="post" action="/performance-settings" class="form"><label>Minimum Günlük Canlı Ağırlık Artışı (kg/gün)<input type="number" min="0.01" step="0.01" name="male_min_daily_gain" value="{target:.2f}" required></label><label>Sarı Uyarı Başlangıcı (% hedef)<input type="number" min="1" max="100" step="1" name="warning_percent" value="{ratio*100:.0f}" required></label><div class="full"><p class="mut">Örnek: hedef 1,00 kg/gün ve sarı sınır %90 ise; 0,90-0,99 sarı, 0,90 altı kırmızı olur.</p><button class="btn">Ayarları Kaydet</button> <a class="btn alt" href="/performance">İptal</a></div></form></div>"""
            return self.send_html(page('Besi Performans Ayarları',body,path,u,msg))
        if path=='/paddocks':
            with db() as c:
                paddocks=c.execute("select * from paddocks where active=1 order by name").fetchall()
                rations=c.execute("select id,name from rations where active=1 order by name").fetchall()
                adults=c.execute("select id,tag,nickname,gender,paddock_id from animals where coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                calves=c.execute("select id,tag,nickname,gender,paddock_id from calves where promoted_animal_id is null order by tag").fetchall()
                rows=[]
                for pd in paddocks:
                    pop=paddock_population(pd['id'],c)
                    ar=c.execute("select pr.*,r.name ration_name from paddock_rations pr join rations r on r.id=pr.ration_id where pr.paddock_id=? and pr.active=1 and (pr.end_date is null or pr.end_date='') order by pr.id desc limit 1",(pd['id'],)).fetchone()
                    sm=ration_summary(ar['ration_id'],c) if ar else None
                    cap=int(pd['capacity'] or 0); doluluk=(pop/cap*100) if cap else 0
                    rows.append(f'''<tr><td><b>{h(pd['name'])}</b><div class="mut">{h(pd['code']) or '-'}</div></td><td>{h(pd['type']) or 'Genel'}</td><td>{pop}{('/'+str(cap)) if cap else ''}</td><td>{f'{doluluk:.0f}%' if cap else '-'}</td><td>{h(ar['ration_name']) if ar else '-'}</td><td>{(money(sm['cost'])+'/baş/gün · '+money(sm['cost']*pop)+'/padok/gün') if sm else '-'}</td><td>{h(pd['notes']) or '-'}</td></tr>''')
                pd_opts=''.join(f'<option value="{x["id"]}">{h(x["name"])}</option>' for x in paddocks)
                ration_opts=''.join(f'<option value="{x["id"]}">{h(x["name"])}</option>' for x in rations)
                animal_opts=''.join(f'<option value="animal:{x["id"]}">🐄 {h(x["tag"])} · {h(x["nickname"])} · {h(x["gender"])}</option>' for x in adults)+''.join(f'<option value="calf:{x["id"]}">🐮 {h(x["tag"])} · {h(x["nickname"])} · Buzağı</option>' for x in calves)
            body=f'''<h1>🏠 Padok Yönetimi</h1><p class="mut">Hayvanları padoklara yerleştirin; rasyonu padoka bağlayınca günlük yem ihtiyacı ve maliyet otomatik hesaplanır.</p>
            <div class="two"><div class="card"><h2>➕ Yeni Padok</h2><form method="post" action="/paddock/create" class="form"><label>Padok Adı<input name="name" required placeholder="Besi B-01"></label><label>Kod<input name="code" placeholder="B01"></label><label>Tür<select name="type"><option>Genel</option><option>Besi</option><option>Dişi</option><option>Buzağı</option><option>Doğum</option><option>Karantina</option></select></label><label>Kapasite<input type="number" min="0" name="capacity" value="0"></label><label class="full">Not<textarea name="notes"></textarea></label><div class="full"><button class="btn">Padoku Kaydet</button></div></form></div>
            <div class="card"><h2>🐄 Hayvanı Padoka Ata</h2><form method="post" action="/paddock/assign" class="form"><label class="full">Hayvan<select name="animal_ref" required><option value="">Seçin</option>{animal_opts}</select></label><label class="full">Padok<select name="paddock_id"><option value="">Padoksuz</option>{pd_opts}</select></label><label class="full">Taşıma Notu<input name="notes" placeholder="Grup değişimi"></label><div class="full"><button class="btn blue">Padoka Ata / Taşı</button></div></form></div></div>
            <div class="card" style="margin-top:14px"><h2>🥣 Padoka Rasyon Ata</h2><form method="post" action="/ration/assign" class="form"><label>Padok<select name="paddock_id" required><option value="">Seçin</option>{pd_opts}</select></label><label>Rasyon<select name="ration_id" required><option value="">Seçin</option>{ration_opts}</select></label><label>Başlangıç<input type="date" name="start_date" value="{date.today().isoformat()}" required></label><label>Not<input name="notes"></label><div class="full"><button class="btn orange">Rasyonu Padoka Ata</button> <a class="btn alt" href="/rations">Rasyon Yönetimi →</a></div></form></div>
            <div class="card" style="margin-top:14px;overflow:auto"><h2>Padoklar</h2><table><tr><th>Padok</th><th>Tür</th><th>Hayvan</th><th>Doluluk</th><th>Aktif Rasyon</th><th>Yem Maliyeti</th><th>Not</th></tr>{''.join(rows) if rows else '<tr><td colspan="7">Henüz padok tanımlanmadı.</td></tr>'}</table></div>'''
            return self.send_html(page('Padok Yönetimi',body,'/paddocks',u,msg))
        if path=='/feeds':
            search=(q.get('q',[''])[0] or '').strip()
            with db() as c:
                params=[]; where='where f.active=1'
                if search: where+=' and (f.name like ? or f.category like ?)';params=[f'%{search}%',f'%{search}%']
                feeds=c.execute(f'''select f.*,coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price,
                    coalesce((select sum(case when st.tx_type in ('Giriş','Sayım +') then st.quantity_kg when st.tx_type in ('Çıkış','Tüketim','Sayım -') then -st.quantity_kg else 0 end) from feed_stock_transactions st where st.feed_id=f.id),0) stock
                    from feed_catalog f {where} order by f.category,f.name limit 250''',[date.today().isoformat()]+params).fetchall()
                allfeeds=c.execute("select id,name from feed_catalog where active=1 order by name").fetchall()
                daily_use={}
                active_pr=c.execute("select paddock_id,ration_id from paddock_rations where active=1 and (end_date is null or end_date='')").fetchall()
                for pr in active_pr:
                    pop=paddock_population(pr['paddock_id'],c)
                    for it in c.execute("select feed_id,kg_per_head_day from ration_items where ration_id=?",(pr['ration_id'],)).fetchall():
                        daily_use[it['feed_id']]=daily_use.get(it['feed_id'],0.0)+pop*float(it['kg_per_head_day'] or 0)
                opts=''.join(f'<option value="{x["id"]}">{h(x["name"])}</option>' for x in allfeeds)
                trs=''.join(f'''<tr><td><b>{h(r['name'])}</b><div class="mut">{h(r['category'])}</div><small class="mut">{h(r['source']) or '-'}</small></td><td>{float(r['dm_pct'] or 0):.1f}</td><td>{float(r['cp_pct'] or 0):.1f}</td><td>{float(r['ndf_pct'] or 0):.1f}</td><td>{float(r['me_mcal_kg'] or 0):.2f}</td><td>{float(r['ca_pct'] or 0):.2f}</td><td>{float(r['p_pct'] or 0):.2f}</td><td><b>{money(r['price'])}/kg</b></td><td>{float(r['stock'] or 0):,.1f} kg</td><td>{daily_use.get(r['id'],0):,.1f} kg</td><td>{(f"{float(r['stock'] or 0)/daily_use.get(r['id'],1):.0f} gün" if daily_use.get(r['id'],0)>0 else '-')}</td><td><div class="actions" style="flex-wrap:nowrap"><a class="btn alt compact-btn" href="/feed-edit?id={r['id']}">✏️ Düzenle</a><form method="post" action="/feed/delete" style="margin:0" onsubmit="return confirm('Bu yemi katalogdan kaldırmak istediğinize emin misiniz? Geçmiş rasyon ve fiyat kayıtları korunur.')"><input type="hidden" name="feed_id" value="{r['id']}"><button class="btn red compact-btn">🗑 Sil</button></form></div></td></tr>''' for r in feeds)
            body=f'''<h1>🌾 Yem Kataloğu & Stok</h1><p class="mut">Besin değerleri NASEM 2016 Beef + NASEM 2021 Dairy ile karşılaştırmalı güncelleniyor. Tam eşleşmeyen özel yemlerde mevcut referans korunur; kendi laboratuvar analizinizi Düzenle ile girebilirsiniz. Eski fiyatlar aktarılmadı.</p>
            <div class="grid"><div class="card stat metric"><span>Yem Kataloğu</span><b>{len(allfeeds)}</b></div><div class="card stat metric blue"><span>Gösterilen</span><b>{len(feeds)}</b></div><div class="card stat metric orange"><span>Fiyat Mantığı</span><b>Geçmişli</b><small>Her tarih kendi fiyatını korur</small></div></div>
            <div class="two" style="margin-top:14px"><div class="card"><h2>💰 Güncel Fiyat Gir</h2><form method="post" action="/feed/price" class="form"><label class="full">Yem<select name="feed_id" required><option value="">Seçin</option>{opts}</select></label><label>Tarih<input type="date" name="effective_date" value="{date.today().isoformat()}" required></label><label>₺ / kg<input type="number" step="0.0001" min="0" name="price_per_kg" required></label><label class="full">Not<input name="notes" placeholder="Tedarikçi / alım notu"></label><div class="full"><button class="btn">Fiyatı Kaydet</button></div></form></div>
            <div class="card"><h2>📦 Stok Hareketi</h2><form method="post" action="/feed/stock" class="form"><label class="full">Yem<select name="feed_id" required><option value="">Seçin</option>{opts}</select></label><label>Tür<select name="tx_type"><option>Giriş</option><option>Çıkış</option><option>Tüketim</option><option>Sayım +</option><option>Sayım -</option></select></label><label>Miktar (kg)<input type="number" step="0.1" min="0.01" name="quantity_kg" required></label><label>Tarih<input type="date" name="tx_date" value="{date.today().isoformat()}" required></label><label>Alış ₺/kg<input type="number" step="0.0001" min="0" name="unit_price" value="0"></label><label class="full">Not<input name="notes"></label><div class="full"><button class="btn blue">Stok Hareketini Kaydet</button></div></form></div></div>
            <div class="card" style="margin-top:14px"><details><summary><b>➕ Katalogda olmayan özel yem ekle</b></summary><form method="post" action="/feed/create" class="form" style="margin-top:14px"><label>Yem Adı<input name="name" required></label><label>Kategori<input name="category" value="Özel Yem"></label><label>KM %<input type="number" step="0.01" name="dm_pct"></label><label>HP % KM<input type="number" step="0.01" name="cp_pct"></label><label>NDF % KM<input type="number" step="0.01" name="ndf_pct"></label><label>ME Mcal/kg KM<input type="number" step="0.001" name="me_mcal_kg"></label><label>Ca % KM<input type="number" step="0.001" name="ca_pct"></label><label>P % KM<input type="number" step="0.001" name="p_pct"></label><div class="full"><button class="btn">Özel Yemi Ekle</button></div></form></details></div>
            <div class="card" style="margin-top:14px;overflow:auto"><form class="actions"><input name="q" value="{h(search)}" placeholder="Yem ara..."><button class="btn alt">🔎 Ara</button><a class="btn alt" href="/feeds">Temizle</a></form><table><tr><th>Yem</th><th>KM%</th><th>HP%</th><th>NDF%</th><th>ME</th><th>Ca%</th><th>P%</th><th>Fiyat</th><th>Stok</th><th>Günlük Kullanım</th><th>Tahmini Yeterlilik</th><th>İşlem</th></tr>{trs or '<tr><td colspan="12">Kayıt bulunamadı.</td></tr>'}</table></div>'''
            return self.send_html(page('Yem Kataloğu',body,'/feeds',u,msg))
        if path=='/feed-edit':
            try: fid=int((q.get('id',['0'])[0] or 0))
            except: fid=0
            with db() as c: feed=c.execute('select * from feed_catalog where id=? and active=1',(fid,)).fetchone()
            if not feed:return self.redirect('/feeds','Yem bulunamadı.')
            def fv(k,dec=3):
                try:return f"{float(feed[k] or 0):.{dec}f}"
                except:return '0'
            body=f'''<div class="pro-form-head"><div><h1>✏️ Yemi Düzenle</h1><div class="mut">Sistem kataloğundaki veya sizin eklediğiniz yemin besin değerlerini güncelleyebilirsiniz.</div></div><a class="btn alt" href="/feeds">← Yem Kataloğu</a></div>
            <div class="card"><form method="post" action="/feed/edit" class="form">
            <input type="hidden" name="feed_id" value="{fid}"><label>Yem Adı<input name="name" value="{h(feed['name'])}" required></label><label>Kategori<input name="category" value="{h(feed['category'])}"></label>
            <label>KM %<input type="number" step="0.01" name="dm_pct" value="{fv('dm_pct',2)}"></label><label>HP % KM<input type="number" step="0.01" name="cp_pct" value="{fv('cp_pct',2)}"></label><label>NDF % KM<input type="number" step="0.01" name="ndf_pct" value="{fv('ndf_pct',2)}"></label><label>TDN % KM<input type="number" step="0.01" name="tdn_pct" value="{fv('tdn_pct',2)}"></label>
            <label>ME Mcal/kg KM<input type="number" step="0.001" name="me_mcal_kg" value="{fv('me_mcal_kg')}"></label><label>NEm Mcal/kg KM<input type="number" step="0.001" name="nem_mcal_kg" value="{fv('nem_mcal_kg')}"></label><label>NEg Mcal/kg KM<input type="number" step="0.001" name="neg_mcal_kg" value="{fv('neg_mcal_kg')}"></label>
            <label>Nişasta % KM<input type="number" step="0.01" name="starch_pct" value="{fv('starch_pct',2)}"></label><label>Yağ % KM<input type="number" step="0.01" name="fat_pct" value="{fv('fat_pct',2)}"></label><label>Kül % KM<input type="number" step="0.01" name="ash_pct" value="{fv('ash_pct',2)}"></label>
            <label>Ca % KM<input type="number" step="0.001" name="ca_pct" value="{fv('ca_pct')}"></label><label>P % KM<input type="number" step="0.001" name="p_pct" value="{fv('p_pct')}"></label><label>Mg % KM<input type="number" step="0.001" name="mg_pct" value="{fv('mg_pct')}"></label><label>K % KM<input type="number" step="0.001" name="k_pct" value="{fv('k_pct')}"></label><label>Na % KM<input type="number" step="0.001" name="na_pct" value="{fv('na_pct')}"></label><label>S % KM<input type="number" step="0.001" name="s_pct" value="{fv('s_pct')}"></label>
            <label class="full">Kaynak / Referans<input name="source" value="{h(feed['source'])}" placeholder="NASEM 2016 / NASEM 2021 / Laboratuvar analizi / Kullanıcı girişi"></label>
            <div class="full"><button class="btn">Değişiklikleri Kaydet</button> <a class="btn alt" href="/feeds">İptal</a></div></form></div>'''
            return self.send_html(page('Yemi Düzenle',body,'/feeds',u,msg))
        if path=='/rations':
            selected=int((q.get('id',['0'])[0] or 0))
            with db() as c:
                rations=c.execute("select * from rations where active=1 order by name").fetchall()
                feeds=c.execute("""select f.id,f.name,f.category,f.dm_pct,f.cp_pct,f.ndf_pct,f.me_mcal_kg,f.ca_pct,f.p_pct, coalesce((select fp.price_per_kg from feed_prices fp where fp.feed_id=f.id and fp.effective_date<=? order by fp.effective_date desc,fp.id desc limit 1),0) price, coalesce((select sum(case when st.tx_type in ('Giriş','Sayım +') then st.quantity_kg when st.tx_type in ('Çıkış','Tüketim','Sayım -') then -st.quantity_kg else 0 end) from feed_stock_transactions st where st.feed_id=f.id),0) stock from feed_catalog f where f.active=1 order by f.name""",(date.today().isoformat(),)).fetchall()
                paddocks=c.execute("select id,name from paddocks where active=1 order by name").fetchall()
                cards=[]
                for r in rations:
                    sm=ration_summary(r['id'],c)
                    cards.append(f'''<a class="card ration-picker-card{' active' if selected==r['id'] else ''}" href="/rations?id={r['id']}"><div class="ration-picker-head"><h3>🥣 {h(r['name'])}</h3><span class="ration-picker-type">{('🥛 Süt' if ('ration_type' in r.keys() and (r['ration_type'] or '').startswith('Süt')) else '🥩 Besi')}</span></div><div class="ration-picker-main"><b>{sm['as_fed_kg']:.2f} kg</b><span>·</span><b>{money(sm['cost'])}/gün</b></div><div class="ration-picker-ratio">🌾 K/K <b>%{sm['roughage_pct_dm']:.0f} / %{sm['concentrate_pct_dm']:.0f}</b></div></a>''')
                detail=''
                if selected:
                    rr=c.execute("select * from rations where id=?",(selected,)).fetchone()
                    if rr:
                        sm=ration_summary(selected,c)
                        item_rows=''.join(f'''<tr class="ration-row" data-dm="{float(x['dm_pct'] or 0):.8f}" data-cp="{float(x['cp_pct'] or 0):.8f}" data-ndf="{float(x['ndf_pct'] or 0):.8f}" data-me="{float(x['me_mcal_kg'] or 0):.8f}" data-ca="{float(x['ca_pct'] or 0):.8f}" data-p="{float(x['p_pct'] or 0):.8f}" data-price="{float(x['price'] or 0):.8f}" data-group="{feed_group(x)}"><td><b>{h(x['name'])}</b></td><td><div class="ration-stepper"><button type="button" class="btn alt compact-btn qty-step" data-delta="-0.10">−</button><input class="ration-qty" type="number" min="0" step="0.01" name="item_{x['item_id']}" value="{float(x['kg_per_head_day']):.2f}" data-original="{float(x['kg_per_head_day']):.2f}"><button type="button" class="btn alt compact-btn qty-step" data-delta="0.10">+</button></div><small class="qty-delta mut"></small></td><td>{float(x['dm_pct'] or 0):.1f}%</td><td>{float(x['cp_pct'] or 0):.1f}%</td><td>{float(x['ndf_pct'] or 0):.1f}%</td><td>{money(x['price'])}/kg</td><td class="row-daily">{money(float(x['kg_per_head_day'])*float(x['price'] or 0))}</td><td><button type="button" class="btn red compact-btn qty-zero">Çıkar</button></td></tr>''' for x in sm['items']) or '<tr><td colspan="8">Henüz yem eklenmedi.</td></tr>'
                        feed_opts=''.join(f'<option value="{x["id"]}">{h(x["name"])}</option>' for x in feeds)
                        current_feed_qty={int(x['id']):float(x['kg_per_head_day'] or 0) for x in sm['items']}
                        quick_feed_rows=[]
                        for x in feeds:
                            fid=int(x['id']); price=float(x['price'] or 0); stock=float(x['stock'] or 0); cur=current_feed_qty.get(fid,0.0)
                            meta=f"{h(x['category'] or 'Yem')} · KM %{float(x['dm_pct'] or 0):.1f} · HP %{float(x['cp_pct'] or 0):.1f} · NDF %{float(x['ndf_pct'] or 0):.1f}"
                            price_txt=(money(price)+'/kg') if price>0 else 'Fiyat girilmemiş'
                            stock_txt=(f"{stock:,.0f} kg stok" if stock>0 else 'Stok bilinmiyor')
                            in_ration=(f" · Rasyonda {cur:.2f} kg" if cur>0 else '')
                            search_key=h((str(x['name'])+' '+str(x['category'] or '')).casefold())
                            quick_feed_rows.append(f"""<button type='button' class='quick-feed-result' data-feed-id='{fid}' data-feed-name='{h(x['name'])}' data-current='{cur:.2f}' data-search='{search_key}'><span><b>{h(x['name'])}</b><small>{meta}</small></span><span class='quick-feed-side'><b>{price_txt}</b><small>{stock_txt}{in_ration}</small></span></button>""")
                        quick_feed_html=''.join(quick_feed_rows)
                        pd_opts=''.join(f'<option value="{x["id"]}">{h(x["name"])}</option>' for x in paddocks)
                        add_recs=ration_addition_recommendations(rr,sm,c,30)
                        reduce_recs=ration_reduction_recommendations(rr,sm,c,8)
                        combo_recs=ration_combined_recommendations(rr,sm,reduce_recs,add_recs,5)
                        def price_label(fx):
                            return (money(fx['price'])+'/kg') if float(fx['price'] or 0)>0 else '<span class="mut">Fiyat girilmemiş</span>'
                        targets=ration_targets_for_record(rr)
                        add_top_html=''.join(f'''<tr><td><b>{h(fx['name'])}</b><div class="mut">{h(fx['category'])}</div></td><td><b>{h(ration_effect_text(targets,sm,ss,2))}</b><div class="mut">{h(reason)}</div>{('<div class="orange">⚠ '+h(warn)+'</div>') if warn else ''}</td><td>{price_label(fx)}</td><td>{(f"{float(fx['stock'] or 0):,.0f} kg" if float(fx['stock'] or 0)>0 else '<span class="mut">Stok yok/bilinmiyor</span>')}</td><td><a class="btn alt compact-btn" href="/rations?id={selected}&sim_feed={fx['id']}&sim_delta=0.50#smart-balance">+0,50 kg Simüle Et</a></td></tr>''' for score,fx,reason,warn,ss in add_recs[:8]) or '<tr><td colspan="5">Mevcut rasyonu belirgin biçimde iyileştiren ek yem adayı bulunmadı.</td></tr>'
                        add_all_html=''.join(f'''<tr><td><b>{h(fx['name'])}</b><div class="mut">{h(fx['category'])}</div></td><td>{h(ration_effect_text(targets,sm,ss,2))}</td><td>{price_label(fx)}</td><td>{(f"{float(fx['stock'] or 0):,.0f} kg" if float(fx['stock'] or 0)>0 else '-')}</td><td><a class="btn alt compact-btn" href="/rations?id={selected}&sim_feed={fx['id']}&sim_delta=0.50#smart-balance">Simüle Et</a></td></tr>''' for score,fx,reason,warn,ss in add_recs)
                        reduce_html=''.join(f'''<tr><td><b>{h(fx['name'])}</b></td><td><b>{delta:.2f} kg</b></td><td><b>{h(ration_effect_text(targets,sm,ss,2))}</b><div class="mut">{h(reason)}</div>{('<div class="orange">⚠ '+h(warn)+'</div>') if warn else ''}</td><td>{money(ss['cost'])}/baş/gün</td><td><a class="btn alt compact-btn" href="/rations?id={selected}&sim_feed={fx['id']}&sim_delta={delta:.2f}#smart-balance">Simüle Et</a></td></tr>''' for score,fx,delta,reason,warn,ss in reduce_recs) or '<tr><td colspan="5">Azaltılması genel dengeyi iyileştiren belirgin bir mevcut yem bulunmadı.</td></tr>'
                        combo_html=''.join(f'''<tr><td><b>{h(red[1]['name'])}</b> {red[2]:.2f} kg</td><td><b>{h(add[1]['name'])}</b> +0,50 kg</td><td>{h(effect)}</td><td><form method="post" action="/ration/apply-combo"><input type="hidden" name="ration_id" value="{selected}"><input type="hidden" name="red_feed_id" value="{red[1]['id']}"><input type="hidden" name="red_delta" value="{red[2]:.2f}"><input type="hidden" name="add_feed_id" value="{add[1]['id']}"><input type="hidden" name="add_delta" value="0.50"><button class="btn blue compact-btn">Birlikte Uygula</button></form></td></tr>''' for score,red,add,combo_ss,effect in combo_recs) or '<tr><td colspan="4">Şimdilik anlamlı bir azalt + ekle kombinasyonu bulunmadı.</td></tr>'
                        quick_solutions=[]
                        if reduce_recs:
                            score,fx,delta,reason,warn,ss=reduce_recs[0]
                            quick_solutions.append(f'''<div class="smart-solution"><div><b>✂️ Fazlalığı Azalt</b><small>{h(fx['name'])} {delta:.2f} kg</small></div><div class="effect">{h(ration_effect_text(targets,sm,ss,3))}</div><p>{h(reason)}</p><a class="btn alt compact-btn" href="/rations?id={selected}&sim_feed={fx['id']}&sim_delta={delta:.2f}#ration-workbench">Çalışma Masasında Dene</a></div>''')
                        if add_recs:
                            score,fx,reason,warn,ss=add_recs[0]
                            quick_solutions.append(f'''<div class="smart-solution"><div><b>➕ Eksik Tamamla</b><small>{h(fx['name'])} +0,50 kg</small></div><div class="effect">{h(ration_effect_text(targets,sm,ss,3))}</div><p>{h(reason)}</p><a class="btn alt compact-btn" href="/rations?id={selected}&sim_feed={fx['id']}&sim_delta=0.50#ration-workbench">Çalışma Masasında Dene</a></div>''')
                        if combo_recs:
                            score,red,add,combo_ss,effect=combo_recs[0]
                            quick_solutions.append(f'''<div class="smart-solution"><div><b>⚖️ Kombine Dengele</b><small>{h(red[1]['name'])} {red[2]:.2f} kg · {h(add[1]['name'])} +0,50 kg</small></div><div class="effect">{h(effect)}</div><p>Maliyet: {money(sm['cost'])} → <b>{money(combo_ss['cost'])}</b>/baş/gün</p><form class="combo-apply" method="post" action="/ration/apply-combo"><input type="hidden" name="ration_id" value="{selected}"><input type="hidden" name="red_feed_id" value="{red[1]['id']}"><input type="hidden" name="red_delta" value="{red[2]:.2f}"><input type="hidden" name="add_feed_id" value="{add[1]['id']}"><input type="hidden" name="add_delta" value="0.50"><button class="btn blue compact-btn">✅ İkisini Birlikte Uygula</button></form></div>''')
                        quick_solutions_html=''.join(quick_solutions) or '<div class="mut">Rasyon hedef aralıklara yakın; belirgin bir düzeltme önerisi oluşmadı.</div>'
                        sim_html=''
                        try: sim_feed=int((q.get('sim_feed',['0'])[0] or 0));sim_delta=float((q.get('sim_delta',['0.5'])[0] or .5))
                        except: sim_feed=0;sim_delta=.5
                        if sim_feed:
                            sf=c.execute('select name from feed_catalog where id=?',(sim_feed,)).fetchone();ss=ration_simulated_summary(selected,sim_feed,sim_delta,c)
                            if sf: sim_html=f'''<div class="card" style="margin-top:14px;border:2px solid #2f78d0"><h3>🧪 Kaydetmeden Simülasyon: +{sim_delta:.2f} kg {h(sf['name'])}</h3><div class="grid"><div class="card stat">KM<b>{sm['dm_kg']:.2f} → {ss['dm_kg']:.2f}</b></div><div class="card stat">HP<b>%{sm['cp_pct_dm']:.1f} → %{ss['cp_pct_dm']:.1f}</b></div><div class="card stat">ME<b>{sm['me_mcal']:.1f} → {ss['me_mcal']:.1f}</b></div><div class="card stat">NDF<b>%{sm['ndf_pct_dm']:.1f} → %{ss['ndf_pct_dm']:.1f}</b></div><div class="card stat">Kaba/Kesif<b>%{sm['roughage_pct_dm']:.0f}/%{sm['concentrate_pct_dm']:.0f} → %{ss['roughage_pct_dm']:.0f}/%{ss['concentrate_pct_dm']:.0f}</b></div><div class="card stat metric orange">Maliyet<b>{money(sm['cost'])} → {money(ss['cost'])}</b></div></div><div class="actions"><form method="post" action="/ration/apply-suggestion"><input type="hidden" name="ration_id" value="{selected}"><input type="hidden" name="feed_id" value="{sim_feed}"><input type="hidden" name="delta" value="{sim_delta}"><button class="btn blue">✅ Bu Değişikliği Uygula</button></form><a class="btn alt" href="/rations?id={selected}">↩ Vazgeç</a></div></div>'''
                        detail=f'''<div class="card" style="margin-top:14px"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap"><div><h2 style="margin:0">🥣 {h(rr['name'])}</h2><span class="mut">Hedef ↔ mevcut → çalışma masası → yem ekle → akıllı çözüm</span></div><details><summary><b>✏️ Rasyon Bilgileri</b></summary><form method="post" action="/ration/edit" class="form" style="margin-top:12px"><input type="hidden" name="ration_id" value="{selected}"><label>Rasyon Adı<input name="name" value="{h(rr['name'])}" required></label><label>Hedef Grup<input name="target_group" value="{h(rr['target_group'])}"></label><label class="full">Not<input name="notes" value="{h(rr['notes'])}"></label><div class="full"><button class="btn">Değişiklikleri Kaydet</button></div></form><form method="post" action="/ration/delete" style="margin-top:10px" onsubmit="return confirm('Bu rasyonu silmek istediğinize emin misiniz?');"><input type="hidden" name="ration_id" value="{selected}"><button class="btn red compact-btn">🗑 Rasyonu Sil</button></form></details></div>
                        {ration_requirement_panel(rr,sm)}
                        <div id="ration-workbench" class="card" style="margin-top:14px"><div class="workbench-head"><div><h3 style="margin:0">🌾 Rasyon Çalışma Masası</h3><span class="mut">Miktarı yazın veya −/+ kullanın. Hedef ↔ mevcut değerler üstte canlı güncellenir.</span></div><div class="workbench-actions"><button type="button" class="btn" onclick="document.getElementById('quick-feed-add').open=true;setTimeout(()=>document.getElementById('quick-feed-search')?.focus(),80)">➕ Yem Ekle</button></div></div><form method="post" action="/ration/items-bulk" id="ration-bulk-form"><input type="hidden" name="ration_id" value="{selected}"><div class="ration-changebar compact-changebar"><span id="dirty-status" class="mut">Kaydedilmiş rasyon gösteriliyor.</span><button type="button" id="ration-reset" class="btn alt compact-btn" style="display:none">↩ Değişiklikleri Geri Al</button></div><div style="overflow:auto;margin-top:8px"><table class="ration-workbench-table"><thead><tr><th>Yem</th><th>Miktar kg/baş/gün</th><th>KM</th><th>HP</th><th>NDF</th><th>₺/kg</th><th>Günlük</th><th></th></tr></thead><tbody>{item_rows}</tbody></table></div><div class="ration-savebar"><button class="btn blue" id="ration-save" disabled>💾 Değişiklikleri Kaydet</button></div></form></div><script>(()=>{{const form=document.getElementById('ration-bulk-form');if(!form)return;const scrollKey='cp-ration-scroll';const rows=[...form.querySelectorAll('.ration-row')],save=document.getElementById('ration-save'),reset=document.getElementById('ration-reset'),status=document.getElementById('dirty-status');const base={{asfed:{sm['as_fed_kg']:.8f},dm:{sm['dm_kg']:.8f},cp:{sm['cp_pct_dm']:.8f},me:{sm['me_mcal']:.8f},ndf:{sm['ndf_pct_dm']:.8f},ca:{sm['ca_g']:.8f},p:{sm['p_g']:.8f},cost:{sm['cost']:.8f},rough:{sm['roughage_pct_dm']:.8f},conc:{sm['concentrate_pct_dm']:.8f}}};const targetsLive={{dm:{targets['dmi_kg']:.8f},cp:{targets['cp_pct']:.8f},me:{targets['me_mcal_day']:.8f},ndfMin:{targets['ndf_min']:.8f},ndfMax:{targets['ndf_max']:.8f},ca:{targets['ca_g']:.8f},p:{targets['p_g']:.8f},roughMin:{targets['roughage_min']:.8f},roughMax:{targets['roughage_max']:.8f}}};const setText=(id,v)=>{{const e=document.getElementById(id);if(e)e.textContent=v;}};function targetStatus(actual,target,tol){{const r=target?actual/target:1;if(r<1-tol)return '⚠️ Eksik %'+((1-r)*100).toFixed(0);if(r>1+tol)return '⬆️ Fazla %'+((r-1)*100).toFixed(0);return '✅ Uygun';}}function liveDiff(actual,target,unit,digits){{if(!target)return '—';const d=actual-target,p=d/target*100,sg=d>0?'+':'';return sg+d.toFixed(digits)+unit+' ('+sg+p.toFixed(0)+'%)';}}function updateTargetCard(key,current,status,diff){{setText('target-mini-'+key+'-current',current);setText('target-mini-'+key+'-status',status);setText('target-mini-'+key+'-diff',diff);const b=document.getElementById('target-mini-'+key);if(b){{b.classList.toggle('ok',status.indexOf('Uygun')>=0);b.classList.toggle('warn',status.indexOf('Uygun')<0);}}}}function updateTargetCards(dm,cp,me,ndf,ca,p,rough,conc,changed){{const ts=targetsLive;const dmS=targetStatus(dm,ts.dm,.10),cpS=targetStatus(cp,ts.cp,.05),meS=targetStatus(me,ts.me,.08),caS=targetStatus(ca,ts.ca,.10),pS=targetStatus(p,ts.p,.10),ndfS=(ndf>=ts.ndfMin&&ndf<=ts.ndfMax)?'✅ Uygun':(ndf<ts.ndfMin?'⚠️ Düşük':'⚠️ Yüksek'),rcS=(rough>=ts.roughMin&&rough<=ts.roughMax)?'✅ Uygun':(rough<ts.roughMin?'⚠️ Kaba yem düşük':'⚠️ Kaba yem yüksek');updateTargetCard('dm',dm.toFixed(2)+' kg',dmS,liveDiff(dm,ts.dm,' kg',2));updateTargetCard('cp','%'+cp.toFixed(1),cpS,liveDiff(cp,ts.cp,' puan',1));updateTargetCard('me',me.toFixed(1),meS,liveDiff(me,ts.me,' Mcal',1));updateTargetCard('ndf','%'+ndf.toFixed(1),ndfS,ndfS.indexOf('Uygun')>=0?'Aralık içi':(ndf<ts.ndfMin?'Alt sınırın altında':'Üst sınırın üzerinde'));updateTargetCard('ca',ca.toFixed(0)+' g',caS,liveDiff(ca,ts.ca,' g',0));updateTargetCard('p',p.toFixed(0)+' g',pS,liveDiff(p,ts.p,' g',0));updateTargetCard('rc','%'+rough.toFixed(0)+' / %'+conc.toFixed(0),rcS,rcS.indexOf('Uygun')>=0?'Aralık içi':(rough<ts.roughMin?'Kaba yem düşük':'Kaba yem yüksek'));const note=document.getElementById('target-live-note');if(note)note.textContent=changed?'🟡 Kaydedilmemiş taslak canlı analiz ediliyor. Hedef kartları çalışma masasıyla birlikte değişiyor.':'🌾 Çalışma masası ile canlı bağlı: miktar değiştikçe bu kartlar anında güncellenir.';}}const trMoney=n=>'₺'+n.toLocaleString('tr-TR',{{minimumFractionDigits:2,maximumFractionDigits:2}});const delta=(id,n,b,suffix='')=>{{const e=document.getElementById(id),d=n-b;e.textContent=Math.abs(d)<0.005?'':((d>0?'+':'')+d.toFixed(2)+suffix);e.style.color=d>0?'#17733d':d<0?'#b33a2b':''}};function calc(){{let asfed=0,dm=0,cpkg=0,ndfkg=0,me=0,ca=0,p=0,cost=0,roughdm=0,concdm=0,changed=0;rows.forEach(r=>{{const i=r.querySelector('.ration-qty'),kg=Math.max(0,parseFloat((i.value||'0').replace(',','.'))||0),orig=parseFloat(i.dataset.original||0),dmp=parseFloat(r.dataset.dm||0),dmkg=kg*dmp/100;asfed+=kg;dm+=dmkg;cpkg+=dmkg*parseFloat(r.dataset.cp||0)/100;ndfkg+=dmkg*parseFloat(r.dataset.ndf||0)/100;me+=dmkg*parseFloat(r.dataset.me||0);ca+=dmkg*parseFloat(r.dataset.ca||0)*10;p+=dmkg*parseFloat(r.dataset.p||0)*10;cost+=kg*parseFloat(r.dataset.price||0);if(r.dataset.group==='Kaba')roughdm+=dmkg;else if(r.dataset.group==='Kesif')concdm+=dmkg;const ch=Math.abs(kg-orig)>.0005;i.classList.toggle('ration-dirty',ch);r.querySelector('.qty-delta').textContent=ch?((kg-orig>0?'+':'')+(kg-orig).toFixed(2)+' kg'):'';if(ch)changed++;r.querySelector('.row-daily').textContent=trMoney(kg*parseFloat(r.dataset.price||0));}});const cp=dm?cpkg/dm*100:0,ndf=dm?ndfkg/dm*100:0,rcdm=roughdm+concdm,rough=rcdm?roughdm/rcdm*100:0,conc=rcdm?concdm/rcdm*100:0;const dc=cost-base.cost;updateTargetCards(dm,cp,me,ndf,ca,p,rough,conc,changed);setText('target-mini-cost-current',trMoney(cost));setText('target-mini-cost-diff',Math.abs(cost-base.cost)<.005?'Değişiklik yok':((cost-base.cost>0?'+':'')+trMoney(cost-base.cost)));setText('target-mini-cost-status',cost<=base.cost?'💰 Maliyet düştü':'💰 Maliyet arttı');save.disabled=changed===0;reset.style.display=changed?'inline-flex':'none';status.className=changed?'ration-dirty-text':'mut';status.textContent=changed?('● '+changed+' yem kaleminde kaydedilmemiş değişiklik var'):'Kaydedilmiş rasyon gösteriliyor.';}}rows.forEach(r=>{{const i=r.querySelector('.ration-qty');i.addEventListener('input',calc);r.querySelectorAll('.qty-step').forEach(b=>b.onclick=(e)=>{{e.preventDefault();const y=window.scrollY;i.value=Math.max(0,(parseFloat(i.value)||0)+parseFloat(b.dataset.delta)).toFixed(2);calc();requestAnimationFrame(()=>window.scrollTo(0,y));}});r.querySelector('.qty-zero').onclick=(e)=>{{e.preventDefault();const y=window.scrollY;i.value='0.00';calc();requestAnimationFrame(()=>window.scrollTo(0,y));}};}});reset.onclick=()=>{{rows.forEach(r=>{{const i=r.querySelector('.ration-qty');i.value=parseFloat(i.dataset.original||0).toFixed(2);}});calc();}};form.addEventListener('submit',()=>sessionStorage.setItem(scrollKey,String(window.scrollY)));const saved=sessionStorage.getItem(scrollKey);if(saved!==null){{sessionStorage.removeItem(scrollKey);requestAnimationFrame(()=>window.scrollTo(0,parseFloat(saved)||0));}}calc();}})();</script>
                        <details id='quick-feed-add' class='card quick-feed-card' style='margin-top:14px;border:1px solid #cfe3d5' {('open' if q.get('feedadd',['0'])[0]=='1' else '')}><summary class='quick-feed-head' style='cursor:pointer'><div><h3 style='display:inline;margin:0'>➕ Rasyona Yem Ekle</h3><span class='mut' style='margin-left:8px'>Yem ekleyeceğiniz zaman açın</span></div><span class='pill'>{('🥛 Süt' if ('ration_type' in rr.keys() and (rr['ration_type'] or '').lower().startswith(('süt','sut'))) else '🥩 Besi')}</span></summary><div class='quick-feed-body'><div class='quick-feed-tools'><input id='quick-feed-search' type='search' placeholder='🔎 Yem ara: mısır, arpa, yonca, süt yemi...' autocomplete='off'><div class='quick-feed-shortcuts'><button type='button' class='btn alt compact-btn quick-filter' data-filter=''>Tümü</button><button type='button' class='btn alt compact-btn quick-filter' data-filter='mısır'>Mısır</button><button type='button' class='btn alt compact-btn quick-filter' data-filter='arpa'>Arpa</button><button type='button' class='btn alt compact-btn quick-filter' data-filter='yonca'>Yonca</button></div></div><div id='quick-feed-results' class='quick-feed-results'>{quick_feed_html}</div><form method='post' action='/ration/item' id='quick-feed-form' class='quick-feed-selected'><input type='hidden' name='ration_id' value='{selected}'><input type='hidden' name='keep_feed_add_open' value='1'><input type='hidden' name='feed_id' id='quick-feed-id' required><div><span class='mut'>Seçilen Yem</span><b id='quick-feed-name'>Önce yukarıdan yem seçin</b></div><div class='ration-stepper'><button type='button' class='btn alt compact-btn' id='quick-feed-minus'>−</button><input id='quick-feed-qty' type='number' step='0.01' min='0.01' name='kg_per_head_day' value='0.50' required><button type='button' class='btn alt compact-btn' id='quick-feed-plus'>+</button></div><button class='btn' id='quick-feed-submit' disabled>➕ Rasyona Ekle / Güncelle</button></form><div style='display:flex;justify-content:flex-end;margin-top:10px'><button type='button' class='btn alt compact-btn' id='quick-feed-close'>✕ Yem Ekleme Alanını Kapat</button></div></div></details><script>(()=>{{const box=document.getElementById('quick-feed-add');if(!box)return;const search=document.getElementById('quick-feed-search'),results=[...box.querySelectorAll('.quick-feed-result')],fid=document.getElementById('quick-feed-id'),fname=document.getElementById('quick-feed-name'),qty=document.getElementById('quick-feed-qty'),submit=document.getElementById('quick-feed-submit');const norm=v=>(v||'').toLocaleLowerCase('tr-TR').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/ı/g,'i').replace(/ş/g,'s').replace(/ğ/g,'g').replace(/ü/g,'u').replace(/ö/g,'o').replace(/ç/g,'c');function filter(){{const q=norm(search.value.trim());let shown=0;results.forEach(r=>{{const ok=!q||norm(r.dataset.search).includes(q);const vis=ok&&shown<12;r.style.display=vis?'flex':'none';if(vis)shown++;}});}}search.addEventListener('input',filter);box.querySelectorAll('.quick-filter').forEach(b=>b.onclick=()=>{{search.value=b.dataset.filter||'';filter();search.focus();}});results.forEach(r=>r.onclick=()=>{{results.forEach(x=>x.classList.remove('selected'));r.classList.add('selected');fid.value=r.dataset.feedId;fname.textContent=r.dataset.feedName;const cur=parseFloat(r.dataset.current||0);qty.value=(cur>0?cur:0.50).toFixed(2);submit.disabled=false;}});document.getElementById('quick-feed-minus').onclick=()=>qty.value=Math.max(.01,(parseFloat(qty.value)||.5)-.10).toFixed(2);document.getElementById('quick-feed-plus').onclick=()=>qty.value=Math.max(.01,(parseFloat(qty.value)||.5)+.10).toFixed(2);document.getElementById('quick-feed-close').onclick=()=>{{box.open=false;history.replaceState(null,'',location.pathname+'?id={selected}#ration-workbench');}};box.addEventListener('toggle',()=>{{if(box.open)setTimeout(()=>search.focus(),50);}});filter();}})();</script>
                        
                        {sim_html}
                        <div id="smart-balance" class="card ration-section-collapse" style="margin-top:14px;border:1px solid #d8e4ff"><div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><div><h3 style="margin:0">🧠 Akıllı Dengeleme</h3><span class="mut">Hedef kartları çalışma masasıyla canlı bağlıdır. Akıllı çözüm önerileri kaydettiğiniz son rasyona göre yenilenir.</span></div></div><div class="smart-solution-grid">{quick_solutions_html}</div><details style="margin-top:12px"><summary><b>🔬 Tüm önerileri ve teknik analizi göster</b></summary><div style="margin-top:12px"><h3>✂️ Fazlalıkları Azaltmak İçin</h3><div style="overflow:auto"><table class="smart-tech-table"><tr><th>Mevcut Yem</th><th>Deneme</th><th>Beklenen Etki</th><th>Yeni Maliyet</th><th></th></tr>{reduce_html}</table></div><h3 style="margin-top:18px">➕ Eksikleri Tamamlamak İçin</h3><div style="overflow:auto"><table class="smart-tech-table"><tr><th>Yem</th><th>Beklenen Etki</th><th>Fiyat</th><th>Stok</th><th></th></tr>{add_top_html}</table></div><details style="margin-top:12px"><summary><b>📚 Tüm uygun yem adayları ({len(add_recs)})</b></summary><div style="overflow:auto;margin-top:8px"><table class="smart-tech-table"><tr><th>Yem</th><th>Beklenen Etki</th><th>Fiyat</th><th>Stok</th><th></th></tr>{add_all_html}</table></div></details><h3 style="margin-top:18px">⚖️ Kombine Dengeleme Fikirleri</h3><div style="overflow:auto"><table class="smart-tech-table"><tr><th>Azalt</th><th>Ekle</th><th>Beklenen Etki</th><th></th></tr>{combo_html}</table></div></div></details></div>
                        <div class="costbox"><b>Not:</b> ÇiftlikPro bu ekranda rasyonun besin içeriği ve maliyetini analiz eder. Nihai rasyon uygunluğu hayvanın canlı ağırlığı, yaş, sağlık ve hedef performansına göre veteriner/zooteknist tarafından değerlendirilmelidir.</div>
                        <details class="card" style="margin-top:14px"><summary><b>🏠 Padoka Ata</b></summary><form method="post" action="/ration/assign" class="actions" style="margin-top:12px"><input type="hidden" name="ration_id" value="{selected}"><select name="paddock_id" required><option value="">Padok seçin</option>{pd_opts}</select><input type="date" name="start_date" value="{date.today().isoformat()}" required><button class="btn orange">Padoka Ata</button></form></details></div>'''
            body=f'''<h1 class="ration-page-title">🥣 Rasyon Yönetimi</h1><p class="mut ration-page-subtitle">Rasyon miktar, besin değeri ve gerçek yem fiyatlarını tek hesapta birleştirir.</p><div class="ration-page-steps"><span>1️⃣ Hedefi belirle</span><span>2️⃣ Yemleri düzenle</span><span>3️⃣ Dengeyi kontrol et</span></div><div class="card ration-new-collapsed"><details><summary><h2 style="display:inline;margin:0">➕ Yeni Rasyon Oluştur</h2><span class="mut" style="margin-left:8px">Yeni rasyon gerektiğinde açın</span></summary><div class="ration-create-grid" style="margin-top:14px"><details class="card"><summary><b>🥩 Besi Rasyonu Oluştur</b></summary><form method="post" action="/ration/create" class="form" style="margin-top:12px"><input type="hidden" name="ration_type" value="Besi"><input type="hidden" name="target_group" value="Besi"><label>Rasyon Adı<input name="name" required placeholder="Besi 500 kg"></label><label>Ortalama Canlı Ağırlık (kg)<input type="number" min="150" max="900" step="1" name="target_weight_kg" value="450"></label><label>Hedef Günlük Artış (kg/gün)<input type="number" min="0.2" max="2.2" step="0.05" name="target_adg_kg" value="1.30"></label><label>Hayvan Tipi<select name="animal_type"><option>Besi Erkek</option><option>Düve</option><option>Genel Büyüyen Sığır</option></select></label><label class="full">Not<input name="notes"></label><div class="full"><button class="btn">Besi Rasyonunu Oluştur</button></div></form></details><details class="card"><summary><b>🥛 Süt Rasyonu Oluştur</b></summary><form method="post" action="/ration/create" class="form" style="margin-top:12px"><input type="hidden" name="ration_type" value="Süt"><input type="hidden" name="target_group" value="Sağmal"><input type="hidden" name="animal_type" value="Sağmal İnek"><label>Rasyon Adı<input name="name" required placeholder="Süt 25 L"></label><label>Ortalama Canlı Ağırlık (kg)<input type="number" min="350" max="900" step="1" name="target_weight_kg" value="650"></label><label>Hedef Süt (L/gün)<input type="number" min="0" max="70" step="0.5" name="target_milk_l" value="25"></label><label class="full">Not<input name="notes"></label><div class="full"><button class="btn blue">Süt Rasyonunu Oluştur</button></div></form></details></div></details></div><div class="ration-picker-grid">{''.join(cards) if cards else '<div class="card">Henüz rasyon oluşturulmadı.</div>'}</div>{detail}'''
            return self.send_html(page('Rasyon Yönetimi',body,'/rations',u,msg))
        if path=='/performance':
            status_filter=(q.get('status',[''])[0] or '').strip();scope=(q.get('scope',['all'])[0] or 'all').strip();search=(q.get('search',[''])[0] or '').strip()
            if scope not in ('all','active','completed'):scope='all'
            purchase_start=(q.get('purchase_start',[''])[0] or '').strip();purchase_end=(q.get('purchase_end',[''])[0] or '').strip();exit_start=(q.get('exit_start',[''])[0] or '').strip();exit_end=(q.get('exit_end',[''])[0] or '').strip();profit_filter=(q.get('profit',[''])[0] or '').strip()
            if profit_filter not in ('','profit','loss','pending'):profit_filter=''
            detail=[]
            with db() as c:
                rows=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif') in ('Aktif','Kesildi','Satıldı') order by tag").fetchall()
                for ar in rows:
                    st=str(ar['status'] or 'Aktif');completed=st in ('Kesildi','Satıldı');hay=(str(ar['tag'] or '')+' '+str(ar['nickname'] or '')+' '+str(ar['breed'] or '')).casefold()
                    if scope=='active' and st!='Aktif':continue
                    if scope=='completed' and not completed:continue
                    if search and search.casefold() not in hay:continue
                    pd=ar['purchase_date'] or '';ed=ar['exit_date'] or ''
                    if purchase_start and (not pd or pd<purchase_start):continue
                    if purchase_end and (not pd or pd>purchase_end):continue
                    if exit_start and (not completed or not ed or ed<exit_start):continue
                    if exit_end and (not completed or not ed or ed>exit_end):continue
                    perf=male_weight_performance(ar['id'],c)
                    if status_filter and perf['status']!=status_filter:continue
                    days,daily,operating,total_cost=animal_cost_values(ar)
                    revenue=float(c.execute("select coalesce(sum(amount),0) from finance where animal_id=? and tx_type='Gelir' and category in ('Kesim Geliri','Hayvan Satışı')",(ar['id'],)).fetchone()[0] or 0)
                    if completed and revenue<=0 and float(ar['sold_price'] or 0)>0:revenue=float(ar['sold_price'] or 0)
                    net_profit=(revenue-total_cost) if completed and revenue>0 else None;profit_pct=((net_profit/total_cost)*100) if net_profit is not None and total_cost>0 else None
                    if profit_filter=='profit' and not(net_profit is not None and net_profit>0):continue
                    if profit_filter=='loss' and not(net_profit is not None and net_profit<0):continue
                    if profit_filter=='pending' and net_profit is not None:continue
                    wr=c.execute('select measure_date,weight from weights where animal_id=? order by measure_date,id',(ar['id'],)).fetchall();first=wr[0] if wr else None;last=wr[-1] if wr else None
                    gain=(float(last['weight'])-float(first['weight'])) if first and last and len(wr)>=2 else None
                    detail.append((ar,perf,days,operating,total_cost,gain,revenue,net_profit,profit_pct))
            active_count=sum(1 for x in detail if str(x[0]['status'] or '')=='Aktif');completed_count=len(detail)-active_count
            purchase_total=sum(float(x[0]['purchase_price'] or 0) for x in detail);operating_total=sum(x[3] for x in detail);total_cost=sum(x[4] for x in detail)
            realized_revenue=sum(x[6] for x in detail if x[7] is not None);realized_cost=sum(x[4] for x in detail if x[7] is not None);realized_profit=sum(x[7] for x in detail if x[7] is not None);margin=((realized_profit/realized_cost)*100) if realized_cost>0 else None
            daily_vals=[x[1]['daily'] for x in detail if x[1].get('daily') is not None];avg_daily=(sum(daily_vals)/len(daily_vals)) if daily_vals else None
            labels={'good':('Hedefte','status-good'),'watch':('Takip','status-watch'),'low':('Düşük','status-low'),'none':('Veri Yetersiz','status-none')};trs=''
            for ar,perf,days,operating,cost,gain,revenue,profit,pct in detail:
                st=str(ar['status'] or 'Aktif');completed=st in ('Kesildi','Satıldı');label,cls=labels[perf['status']];daily_text=f"{perf['daily']:.3f} kg/gün" if perf.get('daily') is not None else '-';gain_text=f'{gain:+.1f} kg' if gain is not None else '-'
                if profit is None:profit_html='<span class="profit-pill wait">Henüz gerçekleşmedi</span>';pct_text='—'
                else:profit_html=f'<span class="profit-pill {"good" if profit>=0 else "bad"}">{"+" if profit>0 else ""}{money(profit)}</span>';pct_text=f'{pct:+.1f}%' if pct is not None else '—'
                rev=money(revenue) if completed and revenue>0 else ('Gelir bekleniyor' if completed else '—');ed=fmt_date(ar['exit_date'] or '-') if completed else 'Devam ediyor'
                trs+=f'<tr><td><a class="taglink" href="/animal?id={ar["id"]}">{h(ar["tag"])}</a><br><span class="mut">{h(ar["nickname"])}</span></td><td>{h(st)}</td><td>{fmt_date(ar["purchase_date"] or "-")}</td><td>{ed}</td><td>{days} gün</td><td>{gain_text}<br><span class="mut">{daily_text}</span></td><td>{money(float(ar["purchase_price"] or 0))}</td><td>{money(operating)}</td><td><b>{money(cost)}</b></td><td><b>{rev}</b></td><td>{profit_html}</td><td><b>{pct_text}</b></td><td><span class="perf-badge {cls}">{label}</span></td></tr>'
            trs=trs or '<tr><td colspan="13">Seçilen filtrelerde hayvan bulunamadı.</td></tr>';margin_text=f'{margin:+.1f}%' if margin is not None else '—';avg_text=f'{avg_daily:.3f} kg/gün' if avg_daily is not None else '—';net_cls='green' if realized_profit>=0 else 'red'
            body=f'''<div class="perf-hero"><div><h1>🐂 Besi Performansı & Kârlılık Merkezi</h1><p>Canlı ağırlık performansı, gerçek maliyet ve satış/kesim gelirini tek ekranda karşılaştırın.</p></div><a class="btn" href="/performance-settings">⚙️ Performans Eşiği</a></div>
            <div class="perf-tabs"><a class="perf-tab {'active' if scope=='all' else ''}" href="/performance?scope=all">📊 Tümü</a><a class="perf-tab {'active' if scope=='active' else ''}" href="/performance?scope=active">🐂 Aktif Besi</a><a class="perf-tab {'active' if scope=='completed' else ''}" href="/performance?scope=completed">💰 Tamamlanan Besiler</a></div>
            <div class="card perf-filter-card"><div class="perf-filter-head"><div><h2>🔎 Akıllı Filtreler</h2><span class="mut">Küpe, tarih, performans ve kârlılık durumuna göre daraltın.</span></div><a class="btn alt" href="/performance">Tümünü Temizle</a></div><form method="get" class="perf-filter-grid"><input type="hidden" name="scope" value="{h(scope)}"><label>Küpe / Hayvan Ara<input name="search" value="{h(search)}" placeholder="Küpe, takma ad veya ırk"></label><label>Alım Başlangıç<input type="date" name="purchase_start" value="{h(purchase_start)}"></label><label>Alım Bitiş<input type="date" name="purchase_end" value="{h(purchase_end)}"></label><label>Çıkış Başlangıç<input type="date" name="exit_start" value="{h(exit_start)}"></label><label>Çıkış Bitiş<input type="date" name="exit_end" value="{h(exit_end)}"></label><label>Performans<select name="status"><option value="">Tümü</option><option value="good" {'selected' if status_filter=='good' else ''}>Hedefte</option><option value="watch" {'selected' if status_filter=='watch' else ''}>Takip</option><option value="low" {'selected' if status_filter=='low' else ''}>Düşük</option><option value="none" {'selected' if status_filter=='none' else ''}>Veri Yetersiz</option></select></label><label>Kârlılık<select name="profit"><option value="">Tümü</option><option value="profit" {'selected' if profit_filter=='profit' else ''}>Kârlı</option><option value="loss" {'selected' if profit_filter=='loss' else ''}>Zararda</option><option value="pending" {'selected' if profit_filter=='pending' else ''}>Henüz Gerçekleşmedi</option></select></label><div class="perf-filter-actions"><button class="btn blue">Filtrele</button><a class="btn alt" href="/performance?scope={h(scope)}">Sıfırla</a></div></form></div>
            <div class="perf-summary"><div class="card stat metric blue">Seçilen Hayvan<b>{len(detail)}</b><small>{active_count} aktif · {completed_count} tamamlanan</small></div><div class="card stat metric orange">Toplam Maliyet<b>{money(total_cost)}</b><small>Alış {money(purchase_total)} · Yem/Bakım {money(operating_total)}</small></div><div class="card stat metric green">Gerçekleşen Gelir<b>{money(realized_revenue)}</b><small>Kesim + hayvan satış gelirleri</small></div><div class="card stat metric {net_cls}">Gerçekleşen Net Kâr<b>{money(realized_profit)}</b><small>Geliri kayıtlı tamamlanan hayvanlar</small></div><div class="card stat metric purple">Gerçekleşen Kâr Oranı<b>{margin_text}</b><small>Maliyet üzerinden · Ort. artış {avg_text}</small></div></div>
            <div class="card" style="margin-top:14px"><h2>Hayvan Bazında Kârlılık Analizi</h2><p class="mut">Kesilen/satılan hayvanın maliyeti çıkış tarihinde donar. Finansta hayvana dağıtılan Kesim Geliri / Hayvan Satışı otomatik eşleşir.</p><div class="perf-table-wrap"><table class="performance-table"><thead><tr><th>Hayvan</th><th>Durum</th><th>Alım</th><th>Çıkış</th><th>Besi Süresi</th><th>Kilo Performansı</th><th>Alış Maliyeti</th><th>Yem + Bakım</th><th>Toplam Maliyet</th><th>Gerçekleşen Gelir</th><th>Net Kâr/Zarar</th><th>Kâr %</th><th>Besi Performansı</th></tr></thead><tbody>{trs}</tbody></table></div></div>'''
            return self.send_html(page('Besi Performansı & Kârlılık',body,path,u,msg))
        if path=='/animal-edit':
            aid=q.get('id',[''])[0]
            with db() as c:
                rec=c.execute('select * from animals where id=?',(aid,)).fetchone()
            if not rec:return self.send_html('Hayvan bulunamadı',404)
            cancel='/animals' if rec['gender']=='Dişi' else '/males'
            body=f'''<h1>Hayvan Düzenle</h1><div class="card"><form method="post" action="/animal-edit" enctype="multipart/form-data" class="form" data-smart-photo-form="1"><input type="hidden" name="id" value="{rec["id"]}"><label>Küpe No<input name="tag" required value="{h(rec["tag"])}"></label><label>Takma Ad<input name="nickname" value="{h(rec["nickname"])}"></label><label>Cinsiyet<select name="gender"><option value="Dişi" {'selected' if rec["gender"]=='Dişi' else ''}>Dişi</option><option value="Erkek" {'selected' if rec["gender"]=='Erkek' else ''}>Erkek</option></select></label><label>Irk<input name="breed" value="{h(rec["breed"])}"></label><label>Doğum Tarihi<input type="date" name="birth_date" value="{h(rec["birth_date"])}"></label><label>Padok / Ahır<input name="paddock" value="{h(rec["paddock"])}"></label><label>Fotoğrafı Değiştir<input type="file" name="photo_file" accept="image/*"><span class="camera-note">Telefonda kamera veya galeriden seçim yapabilirsiniz. Büyük fotoğraflar otomatik küçültülür.</span><div class="photo-upload-status" data-upload-status><span data-upload-text>Fotoğraf hazırlanıyor…</span><div class="upload-progress"><div class="upload-progress-bar" data-upload-bar></div></div></div></label><input type="hidden" name="photo_url" value="{h(rec["photo_url"])}"><label>Durum<select name="status"><option value="Aktif" {'selected' if rec["status"]=='Aktif' else ''}>Aktif</option><option value="Satıldı" {'selected' if rec["status"]=='Satıldı' else ''}>Satıldı</option><option value="Kesildi" {'selected' if rec["status"]=='Kesildi' else ''}>Kesildi</option></select></label><label>Satış Fiyatı<input type="number" step="0.01" name="sold_price" value="{h(rec["sold_price"])}"></label><label>Alış Tarihi<input type="date" name="purchase_date" value="{h(rec["purchase_date"])}"></label><label>Alış Fiyatı (TL)<input type="number" min="0" step="0.01" name="purchase_price" value="{h(rec["purchase_price"])}"></label><label>Alış Kilosu (kg)<input type="number" min="0" step="0.1" name="purchase_weight" value="{h(rec["purchase_weight"])}"></label><label>Günlük Yem/Rasyon (TL)<input type="number" min="0" step="0.01" name="daily_feed_cost" value="{h(rec["daily_feed_cost"])}"></label><label>Günlük Bakım (TL)<input type="number" min="0" step="0.01" name="daily_care_cost" value="{h(rec["daily_care_cost"])}"></label><label>Hedef Satış Fiyatı (TL)<input type="number" min="0" step="0.01" name="target_sale_price" value="{h(rec["target_sale_price"])}"></label><label class="full">Not<textarea name="notes">{h(rec["notes"])}</textarea></label><div class="full"><button class="btn">Değişiklikleri Kaydet</button> <a class="btn alt" href="{cancel}">İptal</a></div></form></div>'''
            return self.send_html(page('Hayvan Düzenle',body,cancel,u,msg))
        if path=='/calf-edit':
            cid=q.get('id',[''])[0]
            with db() as c:
                rec=c.execute('select * from calves where id=?',(cid,)).fetchone()
                mothers=c.execute("select id,tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
            if not rec:return self.send_html('Buzağı bulunamadı',404)
            opts=''.join(f'<option value="{m["id"]}" {"selected" if rec["mother_id"]==m["id"] else ""}>{h(m["tag"])} - {h(m["nickname"])}</option>' for m in mothers)
            body=f'''<h1>Buzağı Düzenle</h1><div class="card"><form method="post" action="/calf-edit" enctype="multipart/form-data" class="form" data-smart-photo-form="1">
            <input type="hidden" name="id" value="{rec["id"]}"><input type="hidden" name="photo_url" value="{h(rec["photo_url"])}">
            <label>Buzağı Küpesi<input name="tag" required value="{h(rec["tag"])}"></label><label>Takma Ad<input name="nickname" value="{h(rec["nickname"])}"></label>
            <label>Anne<select name="mother_id" required>{opts}</select></label><label>Baba Küpesi<input name="father_tag" value="{h(rec["father_tag"])}"></label>
            <label>Doğum Tarihi<input type="date" name="birth_date" required value="{h(rec["birth_date"])}"></label>
            <label>Cinsiyet<select name="gender"><option value="Dişi" {'selected' if rec["gender"]=='Dişi' else ''}>Dişi</option><option value="Erkek" {'selected' if rec["gender"]=='Erkek' else ''}>Erkek</option></select></label>
            <label>Irk<input name="breed" value="{h(rec["breed"])}"></label><label>Padok / Ahır<input name="paddock" value="{h(rec["paddock"])}"></label>
            <label>Alış Tarihi<input type="date" name="purchase_date" value="{h(rec["purchase_date"])}"></label><label>Alış Fiyatı (TL)<input type="number" step="0.01" min="0" name="purchase_price" value="{float(rec["purchase_price"] or 0)}"></label>
            <label>Alış Ödeme Yöntemi<select name="purchase_payment_method"><option {"selected" if rec["purchase_payment_method"]=="Nakit" else ""}>Nakit</option><option {"selected" if rec["purchase_payment_method"]=="Banka" else ""}>Banka</option><option {"selected" if rec["purchase_payment_method"]=="Kredi Kartı" else ""}>Kredi Kartı</option><option {"selected" if rec["purchase_payment_method"]=="Vadeli" else ""}>Vadeli</option></select></label>
            <label>Fotoğraf Yükle<input type="file" name="photo_file" accept="image/*"></label>
            <label class="full">Not<textarea name="notes">{h(rec["notes"])}</textarea></label>
            <div class="full"><button class="btn">Buzağıyı Güncelle</button> <a class="btn alt" href="/calf?id={cid}">İptal</a></div></form></div>'''
            return self.send_html(page('Buzağı Düzenle',body,'/calves',u,msg))
        if path=='/animal-add':
            with db() as c:
                mothers=c.execute("select tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                breeds=[r[0] for r in c.execute("select distinct breed from animals where trim(coalesce(breed,''))<>'' order by breed").fetchall()]
                paddocks=[r[0] for r in c.execute("select distinct paddock from animals where trim(coalesce(paddock,''))<>'' order by paddock").fetchall()]
            mother_options=''.join(f'<option value="{h(r["tag"])}">{h(r["nickname"])}</option>' for r in mothers)
            breed_options=''.join(f'<option value="{h(x)}">' for x in breeds)
            paddock_options=''.join(f'<option value="{h(x)}">' for x in paddocks)
            body=f'''<div class="pro-form-head"><div><h1>Hayvan Ekle</h1><div class="mut">Tek formdan dişi, erkek veya buzağı kaydı oluşturun.</div></div><span id="recordTypeBadge" class="type-chip">Dişi Hayvan</span></div><div class="card"><form method="post" action="/animal-add" enctype="multipart/form-data" class="form" data-smart-photo-form="1"><label>Kayıt Türü<select id="recordType" name="record_type" required onchange="toggleAnimalFields()"><option value="Dişi">Dişi Hayvan</option><option value="Erkek">Erkek Hayvan</option><option value="Buzağı">Buzağı</option></select></label><label>Küpe No<input name="tag" required autocomplete="off"></label><label>Takma Ad<input name="nickname"></label><label class="adult-only">Irk<input name="breed" list="breedOptions"><datalist id="breedOptions">{breed_options}</datalist></label><label>Doğum Tarihi<input type="date" name="birth_date"></label><label class="adult-only">Padok / Ahır<input name="paddock" list="paddockOptions"><datalist id="paddockOptions">{paddock_options}</datalist></label><label class="adult-only">Fotoğraf Yükle / Kameradan veya Galeriden Seç<input type="file" name="photo_file" accept="image/*"><span class="camera-note">Telefonda kamera veya galeriden seçim yapabilirsiniz. Büyük fotoğraflar otomatik küçültülür.</span><div class="photo-upload-status" data-upload-status><span data-upload-text>Fotoğraf hazırlanıyor…</span><div class="upload-progress"><div class="upload-progress-bar" data-upload-bar></div></div></div></label><label class="adult-only">Alış Tarihi<input type="date" name="purchase_date"></label><label class="adult-only">Alış Fiyatı (TL)<input type="number" min="0" step="0.01" name="purchase_price"></label><label class="adult-only">Alış Ödeme Yöntemi<select name="purchase_payment_method"><option>Nakit</option><option>Banka</option><option>Kredi Kartı</option><option>Vadeli</option></select></label><label class="male-only" style="display:none">Alış Kilosu (kg)<input type="number" min="0" step="0.1" name="purchase_weight"></label><label class="male-only" style="display:none">Günlük Yem/Rasyon (TL)<input type="number" min="0" step="0.01" name="daily_feed_cost"></label><label class="male-only" style="display:none">Günlük Bakım (TL)<input type="number" min="0" step="0.01" name="daily_care_cost"></label><label class="male-only" style="display:none">Hedef Satış Fiyatı (TL)<input type="number" min="0" step="0.01" name="target_sale_price"></label><div class="female-pregnancy full" id="femalePregnancyBox"><div class="card" style="background:#f7fbf8;border:1px solid #d7eadc"><h3 style="margin-top:0">🤰 Üreme Durumu</h3><div class="form"><label>Hayvanın Durumu<select id="entryPregnancyStatus" name="entry_pregnancy_status" onchange="toggleEntryPregnancy()"><option value="Bos">Boş / Gebe Değil</option><option value="Gebe">Gebe</option><option value="Bilinmiyor">Bilinmiyor</option></select></label><label id="pregnancyInfoModeLabel" style="display:none">Gebelik Bilgisi<select id="pregnancyInfoMode" name="pregnancy_info_mode" onchange="toggleEntryPregnancy()"><option value="date">Son Tohumlama Tarihi Biliniyor</option><option value="age">Sadece Gebelik Yaşı Biliniyor</option></select></label><label id="knownInseminationLabel" style="display:none">Son Tohumlama Tarihi<input type="date" name="known_insemination_date"></label><label id="pregnancyAgeLabel" style="display:none">Gebelik Yaşı (Ay)<input type="number" name="pregnancy_age_months" min="1" max="9" step="0.5" placeholder="Örn. 6"></label><label id="pregnancyEntryDateLabel" style="display:none">Gebelik Bilgisinin Tarihi<input type="date" name="pregnancy_entry_date" value="{date.today().isoformat()}"></label><div class="full mut" id="pregnancyEntryHint" style="display:none">Satın alınırken gebe olduğu ayrıca kaydedilir. Yalnız gebelik ayı biliniyorsa tahmini doğum yaklaşık hesaplanır.</div></div></div></div><label class="calf-only" style="display:none">Buzağı Cinsiyeti<select name="calf_gender"><option>Dişi</option><option>Erkek</option></select></label><label class="calf-only" style="display:none">Anne Küpesi<input name="mother_tag" list="motherTagOptions"><datalist id="motherTagOptions">{mother_options}</datalist></label><label class="calf-only" style="display:none">Baba Küpesi<input name="father_tag"></label><label class="full">Not<textarea name="notes"></textarea></label><div class="full"><button class="btn">Kaydı Oluştur</button> <a class="btn alt" href="/">İptal</a></div></form></div><script>document.addEventListener('DOMContentLoaded',function(){{toggleAnimalFields();}});</script>'''
            return self.send_html(page('Hayvan Ekle',body,'/animal-add',u,msg))

        if path=='/all-animals':
            with db() as c:
                adults=c.execute("select id,tag,nickname,gender,breed,paddock,birth_date from animals where coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                calves_all=c.execute("select id,tag,nickname,gender,breed,paddock,birth_date from calves where promoted_animal_id is null order by tag").fetchall()
            paddocks=sorted({str(r['paddock'] or '').strip() for r in list(adults)+list(calves_all) if str(r['paddock'] or '').strip()},key=lambda x:x.casefold())
            combined=[]
            for r in adults:
                kind='Dişi' if r['gender']=='Dişi' else 'Erkek'
                row=f'<tr class="data-row" data-kind="{h(kind)}" data-paddock="{h(r["paddock"])}"><td><a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])}</a></td><td>{h(r["nickname"]) or "-"}</td><td>{h(kind)}</td><td>{h(r["breed"]) or "-"}</td><td>{h(r["paddock"]) or "-"}</td><td>{age_text(r["birth_date"])}</td></tr>'
                combined.append((str(r['tag'] or '').casefold(),row))
            for r in calves_all:
                row=f'<tr class="data-row" data-kind="Buzağı" data-paddock="{h(r["paddock"])}"><td><a class="taglink" href="/calf?id={r["id"]}">{h(r["tag"])}</a></td><td>{h(r["nickname"]) or "-"}</td><td>Buzağı - {h(r["gender"])}</td><td>{h(r["breed"]) or "-"}</td><td>{h(r["paddock"]) or "-"}</td><td>{age_text(r["birth_date"])}</td></tr>'
                combined.append((str(r['tag'] or '').casefold(),row))
            combined.sort(key=lambda x:x[0]); trs=''.join(x[1] for x in combined)
            paddock_options=''.join(f'<option value="{h(x)}">{h(x)}</option>' for x in paddocks)
            body=f'''<h1>🐄 Tüm Aktif Hayvanlar</h1><p class="mut">Aktif dişi, erkek ve buzağılar tek listede. Satılan ve kesilen hayvanlar gösterilmez.</p><div class="card"><div class="form" style="grid-template-columns:2fr 1fr 1fr"><label>Arama<input id="allAnimalSearch" type="search" placeholder="Küpe, takma ad, ırk veya padok yazın..." autocomplete="off"></label><label>Padok / Ahır<select id="allAnimalPaddock"><option value="">Tüm Padoklar</option>{paddock_options}</select></label><label>Tür<select id="allAnimalKind"><option value="">Tümü</option><option>Dişi</option><option>Erkek</option><option>Buzağı</option></select></label></div></div><div id="allAnimalEmpty" class="empty-state">Filtrelere uyan aktif hayvan bulunamadı.</div><div class="card"><table id="allAnimalTable" class="mobile-animal-table all-animal-table"><thead><tr><th>Küpe</th><th>Takma Ad</th><th>Tür</th><th>Irk</th><th>Padok</th><th>Yaş</th></tr></thead><tbody>{trs}</tbody></table></div><script>document.addEventListener('DOMContentLoaded',function(){{var search=document.getElementById('allAnimalSearch'),paddock=document.getElementById('allAnimalPaddock'),kind=document.getElementById('allAnimalKind'),rows=[...document.querySelectorAll('#allAnimalTable tr.data-row')],empty=document.getElementById('allAnimalEmpty');function norm(v){{return (v||'').toLocaleLowerCase('tr-TR').trim()}}function apply(){{var q=norm(search.value),p=norm(paddock.value),k=norm(kind.value),shown=0;rows.forEach(function(r){{var ok=(!q||norm(r.innerText).includes(q))&&(!p||norm(r.dataset.paddock)===p)&&(!k||norm(r.dataset.kind)===k);r.style.display=ok?'':'none';if(ok)shown++;}});empty.style.display=shown?'none':'block';}}search.addEventListener('input',apply);paddock.addEventListener('change',apply);kind.addEventListener('change',apply);apply();}});</script>'''
            return self.send_html(page('Tüm Aktif Hayvanlar',body,'/all-animals',u,msg))

        if path=='/animals':
            edit=q.get('edit',[''])[0]
            term=q.get('q',[''])[0].strip()
            with db() as c:
                if term:
                    like=f"%{term}%"
                    rows=c.execute(
                        "select * from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' and (tag like ? or nickname like ? or breed like ? or paddock like ?) order by tag",
                        (like,like,like,like)
                    ).fetchall()
                else:
                    rows=c.execute("select * from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                rec=c.execute('select * from animals where id=?',(edit,)).fetchone() if edit else None
            trs=''.join('<tr><td><a class="taglink" href="/animal?id={0}">{1}</a></td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td><a class="btn alt" href="/animal-edit?id={0}">Düzenle</a>{7}</td></tr>'.format(r['id'],h(r['tag']),h(r['nickname']),h(r['gender']),h(r['breed']),h(r['paddock']),age_text(r['birth_date']),(' <a class="btn" href="/inseminations?animal='+str(r['id'])+'">Tohumlama</a>' if r['gender']=='Dişi' else '')+' <form class="inline-form" method="post" action="/animal-delete" onsubmit="return confirm(\'Bu hayvan ve bağlı kayıtları kalıcı olarak silmek istediğinize emin misiniz?\')"><input type="hidden" name="id" value="'+str(r['id'])+'"><button class="btn red">Sil</button></form>') for r in rows)
            search_options=''.join(f'<option value="{h(r["tag"])}">{h(r["nickname"])}</option>' for r in rows)
            table_rows=trs.replace('<tr>','<tr class="data-row">')
            body=f'''<h1>Dişi Hayvanlar</h1><div class="livebox"><input id="femaleLiveSearch" type="search" placeholder="Küpe, takma ad, ırk veya padok yazın..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('femaleLiveSearch').value='';document.getElementById('femaleLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div><div id="femaleEmpty" class="empty-state">Eşleşen dişi hayvan bulunamadı.</div><div class="card"><table id="femaleLiveTable" class="mobile-animal-table female-table"><thead><tr><th>Küpe</th><th>Takma Ad</th><th>Cinsiyet</th><th>Irk</th><th>Padok</th><th>Yaş</th><th>İşlem</th></tr></thead><tbody>{table_rows}</tbody></table></div><script>document.addEventListener('DOMContentLoaded',function(){{liveTableFilter('femaleLiveSearch','femaleLiveTable','femaleEmpty');}});</script>'''
            return self.send_html(page('Hayvanlar',body,'/animals',u,msg))
        if path=='/males':
            edit=q.get('edit',[''])[0]
            term=q.get('q',[''])[0].strip()
            with db() as c:
                if term:
                    like=f"%{term}%"
                    rows=c.execute(
                        "select * from animals where gender='Erkek' and coalesce(status,'Aktif')='Aktif' and (tag like ? or nickname like ? or breed like ? or paddock like ?) order by tag",
                        (like,like,like,like)
                    ).fetchall()
                else:
                    rows=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                rec=c.execute("select * from animals where id=? and gender='Erkek'",(edit,)).fetchone() if edit else None
            male_rows=[]
            for r in rows:
                days,daily,accumulated,current=animal_cost_values(r)
                male_rows.append(f'<tr><td><a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])}</a></td><td>{h(r["nickname"])}</td><td>{h(r["breed"])}</td><td>{h(r["paddock"])}</td><td>{days} gün</td><td>{money(r["purchase_price"])}</td><td><b>{money(current)}</b></td><td>{money(float(r['target_sale_price'] or 0)-current) if float(r['target_sale_price'] or 0)>0 else '-'}</td><td><a class="btn alt" href="/animal-edit?id={r["id"]}">Düzenle</a> <form class="inline-form" method="post" action="/animal-delete" onsubmit="return confirm(\'Bu hayvan ve bağlı kayıtları kalıcı olarak silmek istediğinize emin misiniz?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></td></tr>')
            trs=''.join(male_rows) or '<tr><td colspan=8>Erkek hayvan kaydı yok</td></tr>'
            search_options=''.join(f'<option value="{h(r["tag"])}">{h(r["nickname"])}</option>' for r in rows)
            table_rows=trs.replace('<tr>','<tr class="data-row">')
            body=f'''<h1>Erkek Hayvanlar</h1><div class="livebox"><input id="maleLiveSearch" type="search" placeholder="Küpe, takma ad, ırk veya padok yazın..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('maleLiveSearch').value='';document.getElementById('maleLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div><div id="maleEmpty" class="empty-state">Eşleşen erkek hayvan bulunamadı.</div><div class="card"><p class="mut">10 ayını dolduran erkek buzağılar otomatik olarak bu listeye geçer.</p><table id="maleLiveTable" class="mobile-animal-table male-table"><thead><tr><th>Küpe</th><th>Takma Ad</th><th>Irk</th><th>Padok</th><th>Bizde Kalma</th><th>Alış</th><th>Anlık Maliyet</th><th>Hedef Kâr</th><th>İşlem</th></tr></thead><tbody>{table_rows}</tbody></table></div><script>document.addEventListener('DOMContentLoaded',function(){{liveTableFilter('maleLiveSearch','maleLiveTable','maleEmpty');}});</script>'''
            return self.send_html(page('Erkek Hayvanlar',body,'/males',u,msg))
        if path in ('/archive/sold','/archive/slaughtered'):
            status='Satıldı' if path=='/archive/sold' else 'Kesildi'
            title='Satılan Hayvanlar' if status=='Satıldı' else 'Kesilen Hayvanlar'
            with db() as c:
                rows=c.execute("select * from animals where status=? order by exit_date desc,tag",(status,)).fetchall()
            trs=''.join(
                f'<tr><td><a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])}</a></td>'
                f'<td>{h(r["nickname"])}</td><td>{h(r["gender"])}</td><td>{h(r["breed"])}</td>'
                f'<td>{fmt_date(r["exit_date"])}</td><td>{h(r["exit_reason"])}</td><td>{money(r["sold_price"])}</td></tr>'
                for r in rows
            ) or '<tr><td colspan=7>Kayıt yok.</td></tr>'
            body=f'<h1>{title}</h1><div class="card"><p class="mut">Bu hayvanların geçmiş kayıtları silinmez; yalnızca aktif sürü listesinden çıkarılır.</p><table><tr><th>Küpe</th><th>Takma Ad</th><th>Cinsiyet</th><th>Irk</th><th>Çıkış Tarihi</th><th>Neden</th><th>Satış/Kesim Tutarı</th></tr>{trs}</table></div>'
            return self.send_html(page(title,body,path,u,msg))
        if path=='/pregnancy-edit':
            aid=q.get('animal_id',[''])[0]
            with db() as c:
                a=c.execute("select * from animals where id=? and gender='Dişi'",(aid,)).fetchone()
                rec=current_pregnancy_record(c,aid) if a else None
            if not a:return self.redirect('/animals','Dişi hayvan bulunamadı.')
            if not rec:return self.redirect('/animal?id='+str(aid),'Düzenlenecek aktif gebelik kaydı bulunamadı.')
            if not str(a['pregnancy_source'] or '').startswith('Satın Alındığında Gebe'):
                return self.redirect('/animal?id='+str(aid),'Bu düzenleme ekranı dışarıdan gebe alınan hayvanlar içindir.')
            source=str(a['pregnancy_source'] or '')
            mode='date' if 'Tohumlama Tarihi' in source else 'age'
            ref=(a['pregnancy_entry_date'] or a['purchase_date'] or date.today().isoformat())
            age=float(a['pregnancy_age_months_at_entry'] or 0)
            body=f'''<div class="actions"><a class="btn alt" href="/animal?id={aid}">← Hayvan Kartına Dön</a></div><h1>🤰 Gebelik Bilgisini Düzenle</h1>
            <div class="card"><p class="mut">Dışarıdan gebe alınan hayvanın tahmini gebelik bilgisini düzeltin. Kaydedildiğinde hayvan kartı ve Tohumlama kaydı birlikte güncellenir.</p>
            <form method="post" action="/pregnancy-edit" class="form"><input type="hidden" name="animal_id" value="{aid}">
            <label>Hayvan<input value="{h(a['tag'])} · {h(a['nickname'])}" disabled></label>
            <label>Gebelik Bilgisi<select name="pregnancy_info_mode" id="pregEditMode" onchange="syncPregEditMode()"><option value="age" {'selected' if mode=='age' else ''}>Gebelik Yaşı Biliniyor</option><option value="date" {'selected' if mode=='date' else ''}>Son Tohumlama Tarihi Biliniyor</option></select></label>
            <label id="pregEditAge">Yaklaşık Gebelik Yaşı (Ay)<input type="number" min="0.5" max="9" step="0.1" name="pregnancy_age_months" value="{age if age>0 else ''}"></label>
            <label id="pregEditDate">Son Tohumlama Tarihi<input type="date" name="known_insemination_date" value="{h(rec['insemination_date'])}"></label>
            <label>Bilginin Geçerli Olduğu Tarih<input type="date" name="pregnancy_entry_date" value="{h(ref)}" required></label>
            <div class="full"><button class="btn">💾 Gebelik Bilgisini Güncelle</button></div></form></div>
            <script>function syncPregEditMode(){{const m=document.getElementById('pregEditMode').value;document.getElementById('pregEditAge').style.display=m==='age'?'block':'none';document.getElementById('pregEditDate').style.display=m==='date'?'block':'none';}}syncPregEditMode();</script>'''
            return self.send_html(page('Gebelik Bilgisini Düzenle',body,'/animals',u,msg))
        if path=='/animal':
            aid=q.get('id',[''])[0]
            with db() as c:
                a=c.execute('select * from animals where id=?',(aid,)).fetchone()
                if not a:return self.send_html('Hayvan bulunamadı',404)
                ins=c.execute('select * from inseminations where animal_id=? order by attempt',(aid,)).fetchall()
                health=c.execute('select * from health where animal_id=? order by applied_date desc',(aid,)).fetchall()
                fin=c.execute('select * from finance where animal_id=? order by tx_date desc',(aid,)).fetchall()
                weights=c.execute('select * from weights where animal_id=? order by measure_date desc',(aid,)).fetchall()
                milk=c.execute('select * from milk where animal_id=? order by measure_date desc',(aid,)).fetchall()
                calves=c.execute('select * from calves where mother_id=? order by birth_date desc',(aid,)).fetchall()
                photos=c.execute('select * from animal_photos where animal_id=? order by created_at desc',(aid,)).fetchall()
            latest=ins[-1] if ins else None
            with db() as pc:
                active_preg=current_pregnancy_record(pc,aid) if a['gender']=='Dişi' else None
            preg=(active_preg['pregnancy_result'] if active_preg else (latest['pregnancy_result'] if latest else 'Kayıt yok'))
            due=(active_preg['due_date'] if active_preg else '')
            cls='pos' if active_preg else 'neg' if str(preg).strip().lower()=='negatif' else ''
            pregnancy_panel=''
            pregnancy_line=f'<p class="preg {cls}">Gebelik: {h(preg)}{(" · Tahmini doğum "+fmt_date(due)) if due else ""}</p>'
            if active_preg and due:
                try:
                    due_day=date.fromisoformat(due);raw_days=(due_day-date.today()).days
                    start_day=date.fromisoformat(active_preg['insemination_date']) if active_preg['insemination_date'] else date.today()-timedelta(days=max(0,280-max(0,raw_days)))
                    preg_days=max(0,min(280,(date.today()-start_day).days));preg_months=min(9,preg_days/(280/9));month_text=f'{preg_months:.1f}'.replace('.',',')
                    remain_text=f'{raw_days} gün' if raw_days>=0 else f'{abs(raw_days)} gün geçti';progress=max(0,min(100,round((preg_days/280)*100)))
                    pregnancy_panel=(f'<div style="margin:18px 0;padding:16px;border:1px solid #cfe5d6;border-radius:18px;background:linear-gradient(180deg,#f7fcf8,#eef8f1)">'
                        f'<div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px"><b style="font-size:18px;color:#176b3a">🤰 Gebelik Durumu</b><span class="status-badge status-preg">Pozitif</span></div>'
                        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px"><div class="pill" style="display:block;text-align:center;padding:12px"><span class="mut">Gebelik Süresi</span><br><b style="font-size:18px">≈ {month_text} ay</b></div><div class="pill" style="display:block;text-align:center;padding:12px"><span class="mut">Doğuma Kalan</span><br><b style="font-size:18px">{remain_text}</b></div><div class="pill" style="display:block;text-align:center;padding:12px"><span class="mut">Tahmini Doğum</span><br><b style="font-size:18px">{fmt_date(due)}</b></div></div>'
                        f'<div style="margin-top:14px"><div style="display:flex;justify-content:space-between;font-size:13px;color:#667a6d"><span>Gebelik ilerlemesi</span><b>%{progress}</b></div><div style="height:10px;background:#dcebe1;border-radius:999px;overflow:hidden;margin-top:6px"><div style="height:100%;width:{progress}%;background:#238a50;border-radius:999px"></div></div></div>'
                        + (f'<div style="margin-top:14px"><a class="btn alt" href="/pregnancy-edit?animal_id={aid}">✏️ Gebelik Bilgisini Düzenle</a></div>' if str(a["pregnancy_source"] or "").startswith("Satın Alındığında Gebe") else '')
                        + '</div>')
                    pregnancy_line=''
                except Exception:pass
            total_cost=sum(r['amount'] for r in fin if r['tx_type']=='Gider')+sum(r['cost'] or 0 for r in health)
            latest_weight=weights[0]['weight'] if weights else None
            first_weight=weights[-1]['weight'] if weights else (a['purchase_weight'] or None)
            try:
                first_date=date.fromisoformat(weights[-1]['measure_date']) if weights else date.fromisoformat(a['purchase_date'])
                perf_days=max(1,(date.fromisoformat(weights[0]['measure_date'])-first_date).days) if latest_weight is not None and first_weight is not None else 0
            except Exception: perf_days=0
            weight_gain=(float(latest_weight)-float(first_weight)) if latest_weight is not None and first_weight is not None else None
            daily_gain=(weight_gain/perf_days) if weight_gain is not None and perf_days>0 else None
            latest_milk=milk[0]['liters'] if milk else None
            total_income=sum(r['amount'] for r in fin if r['tx_type']=='Gelir')
            net_value=total_income-total_cost
            stay_days,daily_cost,accumulated_cost,current_cost=animal_cost_values(a)
            feed_ctx=animal_current_feed_context(a)
            target_profit=float(a['target_sale_price'] or 0)-current_cost if float(a['target_sale_price'] or 0)>0 else None
            period_perf=male_weight_performance(aid) if a['gender']=='Erkek' else None
            perf_labels={'good':('Hedefte / Üstünde','status-good'),'watch':('Takip Edilmeli','status-watch'),'low':('Düşük Artış','status-low'),'none':('Veri Yetersiz','status-none')}
            perf_label,perf_class=perf_labels[period_perf['status']] if period_perf else ('','')
            chart_html=weight_chart_svg(list(reversed(weights))) if a['gender']=='Erkek' else ''
            purchase_summary=(f'<div class="costbox"><h3>Canlı Anlık Maliyet ve Performans</h3><div class="quick-metrics"><span class="pill">Alış Fiyatı<br><b>{money(a["purchase_price"])}</b></span><span class="pill">Bizde Kaldığı Süre<br><b>{stay_days} gün</b></span><span class="pill">Birikmiş Yem + Bakım<br><b>{money(accumulated_cost)}</b></span><span class="pill">Anlık Toplam Maliyet<br><b>{money(current_cost)}</b></span><span class="pill">Toplam Kilo Artışı<br><b>{(str(round(weight_gain,1))+" kg") if weight_gain is not None else "-"}</b></span><span class="pill">Günlük Kilo Artışı<br><b>{(str(round(daily_gain,3))+" kg/gün") if daily_gain is not None else "-"}</b></span><span class="pill">Hedef Satış<br><b>{money(a["target_sale_price"]) if float(a["target_sale_price"] or 0)>0 else "-"}</b></span><span class="pill">Hedef Kâr<br><b>{money(target_profit) if target_profit is not None else "-"}</b></span></div><p class="mut">Günlük yem/rasyon: {money(feed_ctx["feed_cost"])} · Günlük bakım: {money(a["daily_care_cost"])} · Günlük toplam: {money(daily_cost)}</p><p class="mut">{("🌾 Padok rasyonu: "+h(feed_ctx["ration_name"])+" · "+fmt_date(feed_ctx["start_date"])+" tarihinden itibaren") if feed_ctx["source"]=="ration" else "Manuel sabit yem maliyeti kullanılıyor (padokta aktif rasyon yok)."}</p></div>') if a['gender']=='Erkek' else ''
            sale_box=(f'<div class="card" style="margin-top:14px"><h2>Erkek Hayvan Satışı</h2><p class="mut">Satış kaydı oluşturulduğunda hayvan Satılan Hayvanlar arşivine alınır ve net kâr otomatik hesaplanır.</p><form method="post" action="/animal/sale" class="form" onsubmit="return confirm(\'Bu hayvanı satıldı olarak işaretlemek istediğinize emin misiniz?\')"><input type="hidden" name="animal_id" value="{aid}"><label>Satış Tarihi<input type="date" name="sale_date" required value="{date.today().isoformat()}"></label><label>Satış Fiyatı (TL)<input type="number" name="sale_price" min="0" step="0.01" required value="{h(a["target_sale_price"])}"></label><label>Satış Kilosu (kg)<input type="number" name="sale_weight" min="0" step="0.1" value="{h(latest_weight)}"></label><label>Alıcı / Açıklama<input name="description"></label><div class="full"><button class="btn orange">Satışı Tamamla</button></div></form></div>') if a['gender']=='Erkek' and a['status']=='Aktif' else ''
            photo=f'<img class="photo" src="{h(a["photo_url"])}">' if a['photo_url'] else '<div class="photo">🐄</div>'
            gallery=''.join(f'<figure><img src="/uploads/{h(r["filename"])}"><figcaption>{h(r["caption"])}<br>{fmt_datetime(r["created_at"])}</figcaption></figure>' for r in photos) or '<p class="mut">Henüz fotoğraf yüklenmedi.</p>'
            itr=''.join(f'<tr><td>{r["attempt"]}</td><td>{fmt_date(r["insemination_date"])}</td><td>{h(r["pregnancy_result"])}</td><td>{fmt_date(r["due_date"])}</td></tr>' for r in ins) or '<tr><td colspan=4>Kayıt yok</td></tr>'
            htr=''.join(f'<tr><td>{fmt_date(r["applied_date"])}</td><td>{h(r["kind"])}</td><td>{h(r["product"])}</td><td>{money(r["cost"])}</td></tr>' for r in health) or '<tr><td colspan=4>Kayıt yok</td></tr>'
            weight_chron=list(reversed(weights)); wrows=[]
            for i,r in enumerate(weight_chron):
                gain_txt=daily_txt=monthly_txt='-'
                if i>0:
                    prev=weight_chron[i-1]
                    try:
                        wd=(date.fromisoformat(r['measure_date'])-date.fromisoformat(prev['measure_date'])).days
                        wg=float(r['weight'])-float(prev['weight'])
                        gain_txt=f'{wg:+.1f} kg'
                        if wd>0:
                            dd=wg/wd;daily_txt=f'{dd:.3f} kg/gün';monthly_txt=f'{dd*30:.1f} kg'
                    except Exception:pass
                wrows.append(f'<tr><td>{fmt_date(r["measure_date"])}</td><td>{r["weight"]} kg</td><td>{gain_txt}</td><td>{daily_txt}</td><td>{monthly_txt}</td><td>{h(r["notes"])}</td></tr>')
            wtr=''.join(reversed(wrows)) or '<tr><td colspan=6>Kayıt yok</td></tr>'
            mtr=''.join(f'<tr><td>{fmt_date(r["measure_date"])}</td><td>{r["liters"]} L</td><td>{h(r["notes"])}</td></tr>' for r in milk) or '<tr><td colspan=3>Kayıt yok</td></tr>'
            ctr=''.join(f'<tr><td>{h(r["tag"])}</td><td>{fmt_date(r["birth_date"])}</td><td>{h(r["gender"])}</td></tr>' for r in calves) or '<tr><td colspan=3>Kayıt yok</td></tr>'
            back='/males' if a['gender']=='Erkek' else '/animals'; edit_url='/animal-edit?id='+str(aid)
            body=f'''<div class="actions"><a class="btn alt" href="{back}">← Hayvanlara Dön</a><a class="btn" href="{edit_url}">Bilgileri Düzenle</a><a class="btn blue" href="/animal/print?id={aid}">Kimlik Kartını Yazdır</a></div><div class="card profile">{photo}<div><h1>{h(a['tag'])}</h1><h2>{h(a['nickname'])}</h2><span class="pill">{h(a['gender'])}</span><span class="pill">{h(a['breed'])}</span><span class="pill">Padok: {h(a['paddock']) or '-'}</span><span class="pill">Durum: {h(a['status'])}</span>{pregnancy_panel}{pregnancy_line}<div class="quick-metrics"><span class="pill">Yaş<br><b>{age_text(a['birth_date'])}</b></span><span class="pill">Son Kilo<br><b>{(str(latest_weight)+' kg') if latest_weight is not None else '-'}</b></span><span class="pill">Son Süt<br><b>{(str(latest_milk)+' L') if latest_milk is not None else '-'}</b></span><span class="pill">Net Değer<br><b>{money(net_value)}</b></span></div><p>Toplam masraf: <b>{money(total_cost)}</b> · Buzağı: <b>{len(calves)}</b></p>{purchase_summary}<p>{h(a['notes'])}</p></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>Tohumlama ve Gebelik</h2><table><tr><th>Deneme</th><th>Tarih</th><th>Sonuç</th><th>Tahmini Doğum</th></tr>{itr}</table></div><div class="card"><h2>Buzağıları</h2><table><tr><th>Küpe</th><th>Doğum</th><th>Cinsiyet</th></tr>{ctr}</table></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>{'Aylık Tartım ve Besi Performansı' if a['gender']=='Erkek' else 'Kilo Geçmişi'}</h2>{(f'<div class="costbox"><span class="perf-badge {perf_class}">{perf_label}</span><div class="quick-metrics"><span class="pill">Son Dönem Artışı<br><b>{period_perf["gain"]:+.1f} kg</b></span><span class="pill">Tartım Aralığı<br><b>{period_perf["days"]} gün</b></span><span class="pill">Günlük Artış<br><b>{period_perf["daily"]:.3f} kg/gün</b></span><span class="pill">30 Günlük Tahmin<br><b>{period_perf["monthly"]:.1f} kg</b></span></div></div>' if period_perf and period_perf['daily'] is not None else '<p class="mut">Performans hesabı için en az iki tartım girin.</p>') if a['gender']=='Erkek' else ''}<form method="post" action="/animal/weight" class="actions"><input type="hidden" name="animal_id" value="{aid}"><input type="date" name="measure_date" required value="{date.today().isoformat()}"><input type="number" step="0.1" name="weight" placeholder="kg" required><input name="notes" placeholder="Not"><button class="btn">Tartım Ekle</button></form>{chart_html}<table style="margin-top:12px"><tr><th>Tarih</th><th>Kilo</th><th>Fark</th><th>Günlük Artış</th><th>30 Günlük</th><th>Not</th></tr>{wtr}</table></div><div class="card"><h2>Süt Verimi</h2><form method="post" action="/animal/milk" class="actions"><input type="hidden" name="animal_id" value="{aid}"><input type="date" name="measure_date" required value="{date.today().isoformat()}"><input type="number" step="0.1" name="liters" placeholder="Litre" required><input name="notes" placeholder="Not"><button class="btn">Ekle</button></form><table><tr><th>Tarih</th><th>Litre</th><th>Not</th></tr>{mtr}</table></div></div>{sale_box}<div class="card" style="margin-top:14px"><h2>Fotoğraf Galerisi</h2><form method="post" action="/animal/photo" enctype="multipart/form-data" class="uploadbox"><input type="hidden" name="animal_id" value="{aid}"><label>Fotoğraf seç veya telefondan çek<input type="file" name="photo_file" accept="image/*" required></label><input name="caption" placeholder="Açıklama (isteğe bağlı)"><button class="btn">Fotoğrafı Yükle</button><div class="camera-note">Mobil tarayıcıda arka kamera açılır. Fotoğraflar uygulama klasöründeki uploads dizininde saklanır; bu klasörü de düzenli kopyalayın.</div></form><div class="gallery" style="margin-top:14px">{gallery}</div></div><div class="card" style="margin-top:14px"><h2>Sağlık Geçmişi</h2><table><tr><th>Tarih</th><th>Tür</th><th>İşlem</th><th>Maliyet</th></tr>{htr}</table></div>'''
            return self.send_html(page('Hayvan Kartı',body,'/animals',u,msg))
        if path=='/animal/print':
            aid=q.get('id',[''])[0]
            with db() as c:a=c.execute('select * from animals where id=?',(aid,)).fetchone(); ins=c.execute('select * from inseminations where animal_id=? order by attempt',(aid,)).fetchall()
            if not a:return self.send_html('Hayvan bulunamadı',404)
            latest=ins[-1] if ins else None
            return self.send_html(f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>ÇiftlikPro Hayvan Kartı</title><style>body{{font-family:Arial;padding:30px}}.box{{border:2px solid #176b3a;border-radius:16px;padding:24px;max-width:700px}}h1{{color:#176b3a}}table{{width:100%;border-collapse:collapse}}td{{padding:8px;border-bottom:1px solid #ddd}}@media print{{button{{display:none}}}}</style></head><body><button onclick="print()">Yazdır / PDF Kaydet</button><div class="box"><h1>🐄 ÇiftlikPro Hayvan Kimlik Kartı</h1><table><tr><td>Küpe</td><td><b>{h(a['tag'])}</b></td></tr><tr><td>Takma Ad</td><td>{h(a['nickname'])}</td></tr><tr><td>Cinsiyet / Irk</td><td>{h(a['gender'])} / {h(a['breed'])}</td></tr><tr><td>Doğum / Yaş</td><td>{fmt_date(a['birth_date'])} / {age_text(a['birth_date'])}</td></tr><tr><td>Padok</td><td>{h(a['paddock'])}</td></tr><tr><td>Gebelik</td><td>{h(latest['pregnancy_result'] if latest else 'Kayıt yok')}</td></tr><tr><td>Tahmini Doğum</td><td>{fmt_date(latest['due_date'] if latest else '')}</td></tr><tr><td>Not</td><td>{h(a['notes'])}</td></tr></table></div></body></html>''')
        if path=='/calves':
            edit=q.get('edit',[''])[0]
            term=q.get('q',[''])[0].strip()
            with db() as c:
                mothers=c.execute("select id,tag,nickname from animals where gender='Dişi' order by tag").fetchall()
                if term:
                    like=f"%{term}%"
                    rows=c.execute(
                        '''select calves.*,animals.tag mother_tag,animals.nickname mother_name
                           from calves join animals on animals.id=calves.mother_id
                           where calves.promoted_animal_id is null and
                           (calves.tag like ? or animals.tag like ? or animals.nickname like ?)
                           order by calves.birth_date desc''',
                        (like,like,like)
                    ).fetchall()
                else:
                    rows=c.execute(
                        'select calves.*,animals.tag mother_tag,animals.nickname mother_name from calves join animals on animals.id=calves.mother_id where calves.promoted_animal_id is null order by calves.birth_date desc'
                    ).fetchall()
                rec=c.execute('select * from calves where id=?',(edit,)).fetchone() if edit else None
            opts=''.join(f'<option value="{m["id"]}" {"selected" if rec and rec["mother_id"]==m["id"] else ""}>{h(m["tag"])} - {h(m["nickname"])}</option>' for m in mothers)
            trs=''.join(f'<tr><td><a class="taglink" href="/calf?id={r["id"]}">{h(r["tag"])}</a></td><td>{h(r["mother_tag"])} {h(r["mother_name"])}</td><td>{h(r["father_tag"])}</td><td>{h(fmt_date(r["birth_date"]))}</td><td>{age_text(r["birth_date"])}</td><td>{h(r["gender"])}</td><td><a class="btn alt" href="/calf-edit?id={r["id"]}">Düzenle</a> <form class="inline-form" method="post" action="/calf-delete" onsubmit="return confirm(\'Bu buzağı kaydını kalıcı olarak silmek istediğinize emin misiniz?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></td></tr>' for r in rows)
            search_options=''.join(f'<option value="{h(r["tag"])}">{h(r["mother_tag"])}</option>' for r in rows)
            table_rows=trs.replace('<tr>','<tr class="data-row">')
            body=f'''<h1>Buzağılar</h1><div class="livebox"><input id="calfLiveSearch" type="search" placeholder="Buzağı küpesi, anne küpesi veya anne adı yazın..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('calfLiveSearch').value='';document.getElementById('calfLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div><div id="calfEmpty" class="empty-state">Eşleşen buzağı bulunamadı.</div><div class="card"><table id="calfLiveTable" class="mobile-animal-table calf-table"><thead><tr><th>Küpe</th><th>Anne</th><th>Baba</th><th>Doğum</th><th>Yaş</th><th>Cinsiyet</th><th>İşlem</th></tr></thead><tbody>{table_rows}</tbody></table></div><script>document.addEventListener('DOMContentLoaded',function(){{liveTableFilter('calfLiveSearch','calfLiveTable','calfEmpty');}});</script>'''
            return self.send_html(page('Buzağılar',body,'/calves',u,msg))
        if path=='/calf':
            cid=q.get('id',[''])[0]
            with db() as c:
                calf=c.execute('select calves.*,animals.tag mother_tag,animals.nickname mother_name from calves join animals on animals.id=calves.mother_id where calves.id=?',(cid,)).fetchone()
                if not calf:return self.send_html('Buzağı bulunamadı',404)
                health_rows=c.execute('select * from health where calf_id=? order by applied_date desc,id desc',(cid,)).fetchall()
                weight_rows=c.execute('select * from calf_weights where calf_id=? order by measure_date desc,id desc',(cid,)).fetchall()
            promoted=''
            if calf['promoted_animal_id']:promoted=f'<p class="flash">Bu kayıt 10 ayını doldurduğu için yetişkin karta aktarıldı. <a class="taglink" href="/animal?id={calf["promoted_animal_id"]}">Yeni hayvan kartını aç</a></p>'
            icon='🐮' if calf['gender']=='Dişi' else '🐂'
            photo=f'<img src="{h(calf["photo_url"])}" alt="Buzağı">' if calf['photo_url'] else icon
            last_weight=float(weight_rows[0]['weight']) if weight_rows else None
            health_html=''.join(f'<tr><td>{fmt_date(r["applied_date"])}</td><td>{h(r["kind"])}</td><td>{h(r["product"])}</td><td>{fmt_date(r["next_date"])}</td><td>{h(r["notes"])}</td></tr>' for r in health_rows) or '<tr><td colspan="5">Henüz sağlık/tedavi kaydı yok.</td></tr>'
            weight_html=''.join(f'<tr><td>{fmt_date(r["measure_date"])}</td><td><b>{float(r["weight"]):.1f} kg</b></td><td>{h(r["notes"])}</td></tr>' for r in weight_rows) or '<tr><td colspan="3">Henüz tartım kaydı yok.</td></tr>'
            body=f'''<div class="actions"><a class="btn alt" href="/calves">← Buzağılara Dön</a><a class="btn" href="/calf-edit?id={cid}">Düzenle</a></div>{promoted}
            <div class="card profile"><div class="photo">{photo}</div><div><h1>{h(calf["tag"])}</h1><span class="pill">{h(calf["gender"])}</span><span class="pill">Yaş: {age_text(calf["birth_date"])}</span>
            <p>Takma ad: <b>{h(calf["nickname"]) or "-"}</b></p><p>Irk: <b>{h(calf["breed"]) or "-"}</b> · Padok: <b>{h(calf["paddock"]) or "-"}</b></p>
            <p>Doğum tarihi: <b>{fmt_date(calf["birth_date"])}</b></p><p>Anne: <a class="taglink" href="/animal?id={calf["mother_id"]}">{h(calf["mother_tag"])} {h(calf["mother_name"])}</a></p><p>Baba: <b>{h(calf["father_tag"]) or "-"}</b></p>
            <p>Son kilo: <b>{f"{last_weight:.1f} kg" if last_weight is not None else "-"}</b></p><p>Alış: <b>{fmt_date(calf["purchase_date"]) or "-"}</b> · <b>{money(calf["purchase_price"])}</b></p><p>{h(calf["notes"])}</p></div></div>
            <div class="grid" style="margin-top:14px"><div class="card"><h2>📷 Fotoğraf</h2><form method="post" action="/calf/photo" enctype="multipart/form-data" class="form" data-smart-photo-form="1"><input type="hidden" name="calf_id" value="{cid}"><label class="full">Kamera / Galeri<input type="file" name="photo_file" accept="image/*" required></label><div class="full"><button class="btn">Fotoğrafı Yükle</button></div></form></div>
            <div class="card"><h2>⚖️ Kilo / Gelişim</h2><form method="post" action="/calf/weight" class="form"><input type="hidden" name="calf_id" value="{cid}"><label>Tarih<input type="date" name="measure_date" value="{date.today().isoformat()}" required></label><label>Kilo (kg)<input type="number" step="0.1" min="0.1" name="weight" required></label><label class="full">Not<input name="notes"></label><div class="full"><button class="btn">Tartımı Kaydet</button></div></form></div></div>
            <div class="card" style="margin-top:14px"><h2>💉 Sağlık / Tedavi Geçmişi</h2><p><a class="btn" href="/health">Sağlık Kaydı Ekle</a></p><div class="tablewrap"><table><tr><th>Tarih</th><th>Tür</th><th>Ürün/İşlem</th><th>Sonraki</th><th>Not</th></tr>{health_html}</table></div></div>
            <div class="card" style="margin-top:14px"><h2>⚖️ Kilo Geçmişi</h2><div class="tablewrap"><table><tr><th>Tarih</th><th>Kilo</th><th>Not</th></tr>{weight_html}</table></div></div>'''
            return self.send_html(page('Buzağı Kartı',body,'/calves',u,msg))
        if path=='/estrus-edit':
            eid=q.get('id',[''])[0]
            with db() as c:
                rec=c.execute("select e.*,a.tag,a.nickname from estrus_records e join animals a on a.id=e.animal_id where e.id=?",(eid,)).fetchone()
            if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
            body=f'''<h1>✏️ Kızgınlık Kaydını Düzenle</h1><div class="card"><form method="post" action="/estrus-edit" class="form"><input type="hidden" name="id" value="{rec['id']}"><label>Hayvan<input value="{h(rec['tag'])} · {h(rec['nickname'])}" disabled></label><label>Kızgınlık Tarihi<input type="date" name="estrus_date" max="{date.today().isoformat()}" value="{h(rec['estrus_date'])}" required></label><label class="full">Gözlenen Belirtiler<input name="signs" value="{h(rec['signs'])}" placeholder="Gözlenen belirtiler"></label><label class="full">Not<textarea name="notes" rows="3">{h(rec['notes'])}</textarea></label><div class="full actions"><button class="btn">💾 Değişiklikleri Kaydet</button><a class="btn alt" href="/estrus">İptal</a></div></form></div>'''
            return self.send_html(page('Kızgınlık Kaydı Düzenle',body,'/estrus',u,msg))
        if path=='/estrus':
            with db() as c:
                female_rows=c.execute("select id,tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                females=[a for a in female_rows if not is_currently_pregnant(c,a['id'])]
                rows=c.execute("select e.*,a.tag,a.nickname from estrus_records e join animals a on a.id=e.animal_id order by e.estrus_date desc,e.id desc").fetchall()
                latest={}
                for r in rows:
                    if r['animal_id'] not in latest: latest[r['animal_id']]=r
            today=date.today(); upcoming=[]
            with db() as c:
                for aid,r in latest.items():
                    if is_currently_pregnant(c,aid):continue
                    cycle=next_estrus_cycle(c,r,today)
                    if cycle and cycle['end']>=today and cycle['start']<=today+timedelta(days=30):
                        upcoming.append((cycle['start'],cycle['center'],cycle['end'],r,cycle['cycle_no']))
            upcoming.sort(key=lambda x:x[1])
            # V3.9.17: Kızgınlık seçicisinde takma adı boş hayvanlarda görünen etiket ile
            # gizli animal_id eşleşmesi aynı kaynaktan üretilir. Böylece "KÜPE · " / "KÜPE"
            # farkı nedeniyle geçerli dişinin reddedilmesi engellenir.
            estrus_picker_rows=[{'id':r['id'],'tag':str(r['tag'] or ''),'nickname':str(r['nickname'] or '')} for r in females]
            for x in estrus_picker_rows:
                x['label']=x['tag'] + ((' · '+x['nickname']) if x['nickname'] else '')
            opts=''.join(f'<option value="{h(x["label"])}"></option>' for x in estrus_picker_rows)
            estrus_picker_data=json.dumps(estrus_picker_rows,ensure_ascii=False)
            cards=[]
            for a,center,e,r,cycle_no in upcoming:
                color='#e27b1f' if a<=today<=e else '#238a50'
                if a<=today<=e:
                    action=f'''<form method="post" action="/estrus-inseminate" onsubmit="return confirm('Bu hayvan bugün tohumlandı olarak Tohumlama kayıtlarına aktarılsın mı?')"><input type="hidden" name="estrus_id" value="{r['id']}"><button class="btn orange">🌱 Bugün Tohumlandı</button></form>'''
                else:
                    action=f'''<form method="post" action="/estrus-send" onsubmit="return confirm('Bu hayvan Tohumlama Takibi ekranına gönderilsin mi? Bu kızgınlık kartı kapanacaktır.')"><input type="hidden" name="estrus_id" value="{r['id']}"><input type="hidden" name="cycle_no" value="{cycle_no}"><button class="btn orange">🌱 Tohumlamaya Gönder</button></form><span class="mut" style="align-self:center">Pencere {fmt_date(a.isoformat())} tarihinde başlıyor</span>'''
                cards.append(f'''<div class="alertitem" style="border-left-color:{color}"><b>🐄 <a class="taglink" href="/animal?id={r['animal_id']}">{h(r['tag'])} {h(r['nickname'])}</a></b><br><span class="mut">Beklenen pencere: {fmt_date(a.isoformat())} – {fmt_date(e.isoformat())} · En olası: {fmt_date(center.isoformat())}</span><div class="estrus-actions">{action}<form method="post" action="/estrus-skip" onsubmit="return confirm('Bu östrus dönemi atlandı olarak işaretlenecek. Emin misiniz?')"><input type="hidden" name="estrus_id" value="{r['id']}"><input type="hidden" name="cycle_no" value="{cycle_no}"><input type="hidden" name="return_to" value="/estrus"><button class="btn alt">⏭️ Bu Östrusu Atla</button></form><a class="btn alt" href="/estrus-edit?id={r['id']}">✏️ Düzenle</a></div></div>''')
            cards_html=''.join(cards) or '<p class="mut">Önümüzdeki 14 gün için beklenen kızgınlık kaydı yok.</p>'
            history=[]
            for r in rows:
                try:
                    d=date.fromisoformat(r['estrus_date']); center=d+timedelta(days=21); window=f'{fmt_date((d+timedelta(days=18)).isoformat())} – {fmt_date((d+timedelta(days=24)).isoformat())}'
                except Exception: center=None; window='-'
                inseminate_action=''
                decision_badge=''
                try:
                    decisions=c.execute("select cycle_no,decision,decision_date from estrus_decisions where estrus_id=? order by cycle_no desc",(r['id'],)).fetchall()
                    skipped=[x for x in decisions if str(x['decision'])=='Atlandı']
                    inseminated=[x for x in decisions if str(x['decision'])=='Tohumlandı']
                    if inseminated:
                        x=inseminated[0]
                        decision_badge=f'''<div class="estrus-decision-badge estrus-done">🌱 Tohumlandı<br><small>{fmt_date(x['decision_date'])}</small></div>'''
                    elif skipped:
                        x=skipped[0]
                        next_center=d+timedelta(days=21*(int(x['cycle_no'])+1))
                        decision_badge=f'''<div class="estrus-decision-badge estrus-skipped">⏭️ Sonraki Döngüye Ertelendi<br><small>Tahmini: {fmt_date(next_center.isoformat())}</small></div>'''
                    elif 0 <= (today-d).days <= 1:
                        inseminate_action=f'''<form method="post" action="/estrus-inseminate" class="inline-form" onsubmit="return confirm('Bu hayvan bugün tohumlandı olarak Tohumlama kayıtlarına aktarılsın mı?')"><input type="hidden" name="estrus_id" value="{r['id']}"><button class="btn orange">🌱 Bugün Tohumlandı</button></form>'''
                except Exception: pass
                history.append(f'''<tr class="data-row"><td><a class="taglink" href="/animal?id={r['animal_id']}">{h(r['tag'])} {h(r['nickname'])}</a></td><td>{fmt_date(r['estrus_date'])}</td><td>{h(r['signs']) or '-'}</td><td>{window}</td><td>{fmt_date(center.isoformat()) if center else '-'}</td><td>{h(r['notes']) or '-'}</td><td>{decision_badge}{inseminate_action}<a class="btn alt" href="/estrus-edit?id={r['id']}">✏️ Düzenle</a><form method="post" action="/estrus-delete" class="inline-form" onsubmit="return confirm('Bu kızgınlık kaydı silinsin mi?')"><input type="hidden" name="id" value="{r['id']}"><button class="btn red">Sil</button></form></td></tr>''')
            history_html=''.join(history) or '<tr><td colspan="7">Henüz kayıt yok.</td></tr>'
            body=f'''<h1>🌸 Kızgınlık Takibi</h1><p class="mut">Dişi hayvanların gözlenen kızgınlıklarını kaydedin. Sistem 18–24 günlük takip penceresini ve 21. günü merkez tahmin olarak gösterir. Tahminler gözlem planlaması içindir.</p>
            <div class="two"><div class="card"><h2>Yeni Kızgınlık Kaydı</h2><form method="post" action="/estrus" class="form" onsubmit="var b=this.querySelector('button[type=submit]');if(b.disabled)return false;b.disabled=true;b.textContent='Kaydediliyor…';return true;"><label>Dişi Hayvan<input id="estrusAnimalSearch" type="search" list="estrusAnimalOptions" placeholder="Küpe veya takma ad yazın..." autocomplete="off" required><input type="hidden" name="animal_id" id="estrusAnimalId"><datalist id="estrusAnimalOptions">{opts}</datalist><span class="mut">Gebe hayvanlar doğum ve buzağı kaydı tamamlanana kadar listelenmez.</span></label><label>Kızgınlık Tarihi<input type="date" name="estrus_date" max="{today.isoformat()}" value="{today.isoformat()}" required></label><label class="full">Gözlenen Belirtiler<input name="signs" placeholder="Örn. üzerine atlamaya izin verme, huzursuzluk, şeffaf akıntı"></label><label class="full">Not<textarea name="notes" rows="3" placeholder="Ek gözlemler..."></textarea></label><div class="full"><button class="btn">💾 Kızgınlığı Kaydet</button></div></form></div><div class="card"><h2>📅 Yaklaşan Kızgınlıklar</h2>{cards_html}</div></div>
            <div class="card" style="margin-top:14px"><h2>Kızgınlık Geçmişi</h2><div class="livebox"><input id="estrusLiveSearch" type="search" placeholder="Küpe, takma ad, belirti veya not ara..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('estrusLiveSearch').value='';document.getElementById('estrusLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div><div id="estrusEmpty" class="empty-state">Eşleşen kızgınlık kaydı bulunamadı.</div><div style="overflow:auto"><table id="estrusLiveTable" class="estrus-table"><tr><th>Hayvan</th><th>Gözlem Tarihi</th><th>Belirtiler</th><th>18–24 Gün Penceresi</th><th>21. Gün</th><th>Not</th><th>İşlem</th></tr>{history_html}</table></div></div>
            <script>const estrusPicker={estrus_picker_data};const estrusSearch=document.getElementById('estrusAnimalSearch'),estrusId=document.getElementById('estrusAnimalId');function normEstrus(v){{return (v||'').trim().toLocaleLowerCase('tr-TR');}}function syncEstrusAnimal(){{const v=normEstrus(estrusSearch.value);const m=estrusPicker.find(x=>normEstrus(x.label)===v||normEstrus(x.tag)===v);estrusId.value=m?m.id:'';}}estrusSearch.addEventListener('input',syncEstrusAnimal);estrusSearch.addEventListener('change',syncEstrusAnimal);document.addEventListener('DOMContentLoaded',function(){{syncEstrusAnimal();liveTableFilter('estrusLiveSearch','estrusLiveTable','estrusEmpty');}});</script>'''
            return self.send_html(page('Kızgınlık Takibi',body,'/estrus',u,msg))
        if path=='/inseminations':
            aid=q.get('animal',[''])[0]
            estrus_id=q.get('estrus',[''])[0]
            with db() as c:
                female_rows=c.execute("select id,tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                females=[a for a in female_rows if not is_currently_pregnant(c,a['id'])]
                all_rows=c.execute('''select i.*,a.tag,a.nickname,a.pregnancy_source from inseminations i join animals a on a.id=i.animal_id order by a.tag,i.attempt,i.insemination_date''').fetchall()
                estrus_context=c.execute('select * from estrus_records where id=? and animal_id=?',(estrus_id,aid)).fetchone() if estrus_id and aid else None
            grouped={}
            for r in all_rows:grouped.setdefault(r['animal_id'],[]).append(r)
            waiting=sum(1 for records in grouped.values() if str(records[-1]['pregnancy_result'] or '').strip().lower() in ('bekleniyor',''))
            pregnant=sum(1 for records in grouped.values() if is_pregnant_value(records[-1]['pregnancy_result']))
            third_attempt=sum(1 for records in grouped.values() if int(records[-1]['attempt'] or 0)>=3)
            month_prefix=date.today().strftime('%Y-%m')
            this_month=sum(1 for r in all_rows if str(r['insemination_date'] or '').startswith(month_prefix))
            next_attempts={a['id']:(max([int(x['attempt']) for x in grouped.get(a['id'],[])],default=0)+1) for a in females}
            selected=next((a for a in females if str(a['id'])==aid),None)
            selected_label=(f"{selected['tag']} · {selected['nickname']}" if selected else '')
            picker_options=''.join(f'<option value="{h(a["tag"])} · {h(a["nickname"])}" data-id="{a["id"]}" data-attempt="{next_attempts[a["id"]]}"></option>' for a in females)
            picker_data=json.dumps([{'id':a['id'],'tag':a['tag'] or '', 'nickname':a['nickname'] or '', 'attempt':next_attempts[a['id']]} for a in females],ensure_ascii=False)
            latest_rows=[]
            for animal_id,records in grouped.items():
                latest=records[-1]
                result=str(latest['pregnancy_result'] or 'Belirsiz')
                if is_pregnant_value(result):
                    external=str(latest['pregnancy_source'] or '').startswith('Satın Alındığında Gebe')
                    badge='<span class="status-badge status-preg">'+('Gebe · Dışarıdan Gebe' if external else 'Gebe')+'</span>'
                elif result.strip().lower()=='negatif':badge='<span class="status-badge status-neg">Gebe Değil</span>'
                elif result.strip().lower()=='bekleniyor':badge='<span class="status-badge status-wait">Kontrol Bekliyor</span>'
                else:badge='<span class="status-badge status-unknown">Belirsiz</span>'
                hist=[]
                for rec in reversed(records):
                    rr=str(rec['pregnancy_result'] or 'Belirsiz')
                    if is_pregnant_value(rr):
                        external=str(rec['pregnancy_source'] or '').startswith('Satın Alındığında Gebe')
                        rb='<span class="status-badge status-preg">'+('Gebe · Dışarıdan' if external else 'Gebe')+'</span>'
                    elif rr.strip().lower()=='negatif':rb='<span class="status-badge status-neg">Gebe Değil</span>'
                    elif rr.strip().lower()=='bekleniyor':rb='<span class="status-badge status-wait">Kontrol Bekliyor</span>'
                    else:rb='<span class="status-badge status-unknown">Belirsiz</span>'
                    hist.append(f'''<tr><td>{rec["attempt"]}. deneme</td><td>{h(fmt_date(rec["insemination_date"]))}</td><td>{rb}</td><td>{h(fmt_date(rec["due_date"])) or '—'}</td><td><div class="row-actions"><a class="btn alt compact-btn" href="/insemination-edit?id={rec['id']}">✏️ Düzenle</a><form method="post" action="/insemination-delete" class="inline-form" onsubmit="return confirm('Bu tohumlama kaydı silinsin mi?')"><input type="hidden" name="id" value="{rec['id']}"><button class="btn red compact-btn">Sil</button></form></div></td></tr>''')
                history=''.join(hist)
                status_sort=('1' if is_pregnant_value(result) else '2' if result.strip().lower()=='bekleniyor' else '3' if result.strip().lower()=='negatif' else '4')
                latest_rows.append(f'''<tr class="data-row" data-animal="{h((str(latest['tag'] or '')+' '+str(latest['nickname'] or '')).lower())}" data-attempt="{int(latest['attempt'] or 0)}" data-insem="{h(latest['insemination_date'] or '')}" data-status="{status_sort}" data-due="{h(latest['due_date'] or '')}" data-history="{len(records)}"><td><a class="taglink" href="/animal?id={animal_id}">{h(latest['tag'])}</a><div class="mut">{h(latest['nickname'])}</div></td><td>{latest['attempt']}. Deneme</td><td>{h(fmt_date(latest['insemination_date']))}</td><td>{badge}</td><td>{h(fmt_date(latest['due_date'])) or '—'}</td><td><details><summary>Geçmiş ({len(records)})</summary><div style="overflow:auto"><table class="insem-history"><tr><th>Deneme</th><th>Tarih</th><th>Sonuç</th><th>Tahmini Doğum</th><th>İşlem</th></tr>{history}</table></div></details></td></tr>''')
            table_rows=''.join(latest_rows)
            estrus_info=''
            if estrus_context:
                try:
                    ed=date.fromisoformat(estrus_context['estrus_date']); es=ed+timedelta(days=18); ee=ed+timedelta(days=24)
                    estrus_info=f'<div class="flash">🌸 Bu hayvan Kızgınlık Takibi ekranından gönderildi. Beklenen pencere: <b>{fmt_date(es.isoformat())} – {fmt_date(ee.isoformat())}</b>. Tohumlama gerçekleştiğinde tarihi seçip kaydedin.</div>'
                except Exception:
                    estrus_info='<div class="flash">🌸 Bu hayvan Kızgınlık Takibi ekranından gönderildi.</div>'
            body=f'''<div class="insem-head"><div><h1>🐄 Üreme Takip Merkezi</h1><div class="mut">Tohumlama kayıtlarını hayvan bazında yönetin, gebelik sonucunu güncelleyin.</div></div></div>
            {estrus_info}
            <div class="grid insem-stats"><div class="card stat metric blue">Kontrol Bekleyen<b>{waiting}</b><small>Son kaydı sonuç bekleyen</small></div><div class="card stat metric green">Gebe<b>{pregnant}</b><small>Son sonucu pozitif olan</small></div><div class="card stat metric orange">3. Denemede<b>{third_attempt}</b><small>Yakın takip gereken</small></div><div class="card stat metric purple">Bu Ay Tohumlanan<b>{this_month}</b><small>{date.today().strftime('%m/%Y')}</small></div></div>
            <div class="card"><h2>Yeni Tohumlama</h2><form id="inseminationForm" method="post" action="/inseminations" class="form"><input type="hidden" name="estrus_id" value="{h(estrus_id if estrus_context else '')}"><label>Dişi Hayvan<div class="animal-picker"><input id="inseminationAnimalSearch" value="{h(selected_label)}" placeholder="Küpe veya takma ad yazın..." autocomplete="off" inputmode="search" required><div id="inseminationAnimalSuggestions" class="animal-suggestions" role="listbox" aria-label="Eşleşen dişi hayvanlar"></div></div><datalist id="inseminationAnimalOptions">{picker_options}</datalist><input type="hidden" id="inseminationAnimalId" name="animal_id" value="{h(aid if selected else '')}"><div class="animal-picker-note">Küpe veya takma ad yazın; eşleşen hayvanlar anında aşağıda görünür.</div></label><label>Deneme<div id="attemptPreview" class="attempt-preview">{(str(next_attempts[selected['id']])+'. Deneme') if selected else 'Hayvan seçildiğinde otomatik belirlenecek'}</div></label><label>Tohumlama Tarihi<input id="inseminationDate" type="date" name="insemination_date" required max="{date.today().isoformat()}"><div id="futureWarning" class="future-warning">Gelecek tarihli tohumlama kaydı girilemez.</div></label><label>İlk Durum<div class="attempt-preview">Kontrol Bekliyor</div><input type="hidden" name="pregnancy_result" value="Bekleniyor"></label><div class="full"><button class="btn">💾 Tohumlamayı Kaydet</button></div></form></div>
            <div class="card" style="margin-top:14px"><h2>Hayvan Bazında Tohumlama Geçmişi</h2><p class="mut">Her hayvan tek satırda gösterilir. “Geçmiş” bağlantısından tüm denemeleri açabilir ve kayıtları düzenleyebilirsiniz.</p><div class="insem-search" style="margin:12px 0 14px"><input id="inseminationLiveSearch" type="search" placeholder="Kayıtlarda küpe veya takma ad ara..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('inseminationLiveSearch').value='';document.getElementById('inseminationLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div><div id="insemEmpty" class="insem-empty">Eşleşen kayıt bulunamadı.</div><div style="overflow:auto"><table id="inseminationLiveTable" class="insem-table sortable-insem"><thead><tr><th><button type="button" class="sort-head" data-sort="animal">Hayvan <span>↕</span></button></th><th><button type="button" class="sort-head" data-sort="attempt">Son Deneme <span>↕</span></button></th><th><button type="button" class="sort-head active" data-sort="insem" data-dir="desc">Son Tohumlama <span>↓</span></button></th><th><button type="button" class="sort-head" data-sort="status">Durum <span>↕</span></button></th><th><button type="button" class="sort-head" data-sort="due">Tahmini Doğum <span>↕</span></button></th><th><button type="button" class="sort-head" data-sort="history">Geçmiş / İşlem <span>↕</span></button></th></tr></thead><tbody>{table_rows}</tbody></table></div></div>
            <script>
            document.addEventListener('DOMContentLoaded',function(){{
              liveTableFilter('inseminationLiveSearch','inseminationLiveTable','insemEmpty');
              var sortTable=document.getElementById('inseminationLiveTable'),sortBody=sortTable.querySelector('tbody');
              function sortInsem(key,dir){{
                var rows=Array.from(sortBody.querySelectorAll('tr.data-row'));
                rows.sort(function(a,b){{
                  var av=a.dataset[key]||'',bv=b.dataset[key]||'';
                  if(key==='attempt'||key==='status'||key==='history'){{av=parseInt(av||'0');bv=parseInt(bv||'0');return dir==='asc'?av-bv:bv-av;}}
                  var cmp=av.localeCompare(bv,'tr',{{numeric:true,sensitivity:'base'}});
                  return dir==='asc'?cmp:-cmp;
                }});
                rows.forEach(function(r){{sortBody.appendChild(r);}});
              }}
              document.querySelectorAll('.sort-head').forEach(function(btn){{
                btn.addEventListener('click',function(){{
                  var key=btn.dataset.sort,dir=(btn.dataset.dir==='asc'?'desc':'asc');
                  if(!btn.dataset.dir && (key==='insem'||key==='due'||key==='attempt'||key==='history'))dir='desc';
                  document.querySelectorAll('.sort-head').forEach(function(x){{x.classList.remove('active');x.removeAttribute('data-dir');x.querySelector('span').textContent='↕';}});
                  btn.classList.add('active');btn.dataset.dir=dir;btn.querySelector('span').textContent=dir==='asc'?'↑':'↓';
                  sortInsem(key,dir);
                }});
              }});
              sortInsem('insem','desc');
              var input=document.getElementById('inseminationAnimalSearch'),hidden=document.getElementById('inseminationAnimalId'),preview=document.getElementById('attemptPreview'),form=document.getElementById('inseminationForm'),dt=document.getElementById('inseminationDate'),warn=document.getElementById('futureWarning'),suggestions=document.getElementById('inseminationAnimalSuggestions');
              var animals={picker_data};
              function norm(v){{return (v||'').toLocaleLowerCase('tr-TR').trim();}}
              function chooseAnimal(a){{input.value=a.tag+(a.nickname?' · '+a.nickname:'');hidden.value=String(a.id);preview.textContent=(parseInt(a.attempt)>3)?'3 deneme sınırına ulaşıldı':(a.attempt+'. Deneme');suggestions.classList.remove('open');suggestions.innerHTML='';}}
              function exactAnimal(){{var v=norm(input.value),found=null;animals.forEach(function(a){{var label=norm(a.tag+(a.nickname?' · '+a.nickname:''));if(v===label||v===norm(a.tag))found=a;}});return found;}}
              function renderSuggestions(){{var q=norm(input.value);hidden.value='';preview.textContent='Hayvan seçildiğinde otomatik belirlenecek';if(!q){{suggestions.classList.remove('open');suggestions.innerHTML='';return;}}var hits=animals.filter(function(a){{return norm(a.tag).indexOf(q)!==-1||norm(a.nickname).indexOf(q)!==-1||norm(a.tag+' '+a.nickname).indexOf(q)!==-1;}}).slice(0,8);if(!hits.length){{suggestions.innerHTML='<div class="animal-suggestion"><span>Eşleşen aktif dişi hayvan bulunamadı.</span></div>';suggestions.classList.add('open');return;}}suggestions.innerHTML='';hits.forEach(function(a){{var b=document.createElement('button');b.type='button';b.className='animal-suggestion';b.innerHTML='<b>'+a.tag+'</b><span>'+(a.nickname||'Takma ad yok')+' · '+a.attempt+'. deneme</span>';b.addEventListener('click',function(){{chooseAnimal(a);}});suggestions.appendChild(b);}});suggestions.classList.add('open');var exact=exactAnimal();if(exact){{hidden.value=String(exact.id);preview.textContent=(parseInt(exact.attempt)>3)?'3 deneme sınırına ulaşıldı':(exact.attempt+'. Deneme');}}}}
              function syncAnimal(){{var exact=exactAnimal();if(exact){{hidden.value=String(exact.id);preview.textContent=(parseInt(exact.attempt)>3)?'3 deneme sınırına ulaşıldı':(exact.attempt+'. Deneme');}}}}
              input.addEventListener('input',renderSuggestions);input.addEventListener('focus',renderSuggestions);input.addEventListener('change',syncAnimal);document.addEventListener('click',function(e){{if(!e.target.closest('.animal-picker'))suggestions.classList.remove('open');}});syncAnimal();
              dt.addEventListener('change',function(){{var bad=dt.value&&dt.value>'{date.today().isoformat()}';warn.style.display=bad?'block':'none';}});
              form.addEventListener('submit',function(e){{syncAnimal();if(!hidden.value){{e.preventDefault();alert('Lütfen listeden geçerli bir dişi hayvan seçin.');return;}}if(dt.value>'{date.today().isoformat()}'){{e.preventDefault();warn.style.display='block';alert('Gelecek tarihli tohumlama kaydı girilemez.');}}}});
            }});
            </script>'''
            return self.send_html(page('Üreme Takip Merkezi',body,'/inseminations',u,msg))
        if path=='/insemination-edit':
            iid=q.get('id',[''])[0]
            with db() as c:rec=c.execute('''select i.*,a.tag,a.nickname from inseminations i join animals a on a.id=i.animal_id where i.id=?''',(iid,)).fetchone()
            if not rec:return self.redirect('/inseminations','Tohumlama kaydı bulunamadı.')
            result=str(rec['pregnancy_result'] or 'Bekleniyor')
            body=f'''<div class="actions"><a class="btn alt" href="/inseminations">← Tohumlamalara Dön</a></div><h1>Tohumlama Kaydını Düzenle</h1><div class="card"><form method="post" action="/insemination-edit" class="form"><input type="hidden" name="id" value="{rec['id']}"><label>Hayvan<div class="attempt-preview">{h(rec['tag'])} · {h(rec['nickname'])}</div></label><label>Deneme<div class="attempt-preview">{rec['attempt']}. Deneme</div></label><label>Tohumlama Tarihi<input type="date" name="insemination_date" required max="{date.today().isoformat()}" value="{h(rec['insemination_date'])}"></label><label>Gebelik Sonucu<select name="pregnancy_result"><option value="Bekleniyor" {'selected' if result=='Bekleniyor' else ''}>Kontrol Bekliyor</option><option value="Pozitif" {'selected' if is_pregnant_value(result) else ''}>Gebe</option><option value="Negatif" {'selected' if result=='Negatif' else ''}>Gebe Değil</option><option value="Belirsiz" {'selected' if result=='Belirsiz' else ''}>Belirsiz</option></select></label><div class="full"><button class="btn">Değişiklikleri Kaydet</button> <a class="btn alt" href="/inseminations">İptal</a></div></form></div>'''
            return self.send_html(page('Tohumlama Düzenle',body,'/inseminations',u,msg))
        if path=='/health-edit':
            hid=q.get('id',[''])[0]
            with db() as c:
                r=c.execute("select h.*,a.tag as animal_tag,ca.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves ca on ca.id=h.calf_id where h.id=?",(hid,)).fetchone()
            if not r:return self.redirect('/health','Sağlık kaydı bulunamadı.')
            subject=r['animal_tag'] or r['calf_tag'] or '-'
            body=f'''<h1>Sağlık Kaydını Düzenle</h1><div class="card"><form method="post" action="/health-edit" class="form">
            <input type="hidden" name="id" value="{r["id"]}">
            <label>Hayvan / Buzağı<input value="{h(subject)}" disabled></label>
            <label>Tür<select name="kind"><option {"selected" if r["kind"]=="Aşı" else ""}>Aşı</option><option {"selected" if r["kind"]=="İlaç" else ""}>İlaç</option><option {"selected" if r["kind"]=="Muayene" else ""}>Muayene</option></select></label>
            <label>Ürün/İşlem<input name="product" value="{h(r["product"])}" required></label>
            <label>Uygulama Tarihi<input type="date" name="applied_date" value="{h(r["applied_date"])}" required></label>
            <label>Sonraki Tarih<input type="date" name="next_date" value="{h(r["next_date"])}"></label>
            <label>Maliyet<input type="number" step="0.01" min="0" name="cost" value="{float(r["cost"] or 0)}"></label>
            <label class="full">Not<textarea name="notes">{h(r["notes"])}</textarea></label>
            <div class="full actions"><button class="btn">Değişiklikleri Kaydet</button><a class="btn alt" href="/health">İptal</a></div>
            </form></div>'''
            return self.send_html(page('Sağlık Kaydı Düzenle',body,'/health',u,msg))
        if path=='/health':
            with db() as c:
                active_animals=c.execute("select id,tag,nickname,gender,paddock_id from animals where coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                active_calves=c.execute("select id,tag,gender,paddock_id from calves where promoted_animal_id is null order by tag").fetchall()
                paddocks=c.execute("select id,name,code from paddocks where active=1 order by name").fetchall()
                rows=c.execute("select h.*,a.tag as animal_tag,a.nickname,c.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves c on c.id=h.calf_id order by h.applied_date desc,h.id desc").fetchall()
                legacy_plans=c.execute("select h.*,a.tag as animal_tag,a.nickname,c.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves c on c.id=h.calf_id where coalesce(h.next_date,'')<>'' order by h.next_date,h.id").fetchall()
                task_rows=c.execute("""select t.*,hc.kind,hc.product,hc.scope_type,hc.paddock_id,p.name as paddock_name,a.tag as animal_tag,a.nickname,c.tag as calf_tag
                    from health_tasks t join health_courses hc on hc.id=t.course_id left join paddocks p on p.id=hc.paddock_id
                    left join animals a on a.id=t.animal_id left join calves c on c.id=t.calf_id
                    where t.status='Bekliyor' order by t.planned_date,t.course_id,t.dose_no,t.day_no,t.application_no,t.id""").fetchall()
            subject_items=[]
            for a in active_animals:
                label=str(a['tag'])+' · '+(str(a['nickname'] or '').strip() or str(a['gender'] or 'Hayvan'))
                subject_items.append(('A:'+str(a['id']),label))
            for c in active_calves: subject_items.append(('C:'+str(c['id']),str(c['tag'])+' · Buzağı · '+str(c['gender'] or '')))
            subject_items.sort(key=lambda x:x[1].casefold())
            subject_json=json.dumps([{'key':k,'label':v} for k,v in subject_items],ensure_ascii=False)
            paddock_options=''.join(f'<option value="{r["id"]}">{h(r["name"])}{(" · "+h(r["code"])) if r["code"] else ""}</option>' for r in paddocks)
            health_groups={}
            for r in rows:
                key=('A',r['animal_id']) if r['animal_id'] else ('C',r['calf_id']); tag=r['animal_tag'] or r['calf_tag'] or '-'; nickname=(r['nickname'] or '').strip() if r['animal_id'] else 'Buzağı'
                health_groups.setdefault(key,{'tag':tag,'nickname':nickname,'rows':[]})['rows'].append(r)
            group_cards=[]
            for g in health_groups.values():
                inner=''.join(f'<tr><td>{fmt_date(r["applied_date"])}</td><td>{h(r["kind"])}</td><td>{h(r["product"])}</td><td>{fmt_date(r["next_date"])}</td><td>{money(r["cost"])}</td><td><a class="btn alt" href="/health-edit?id={r["id"]}">Düzenle</a> <form method="post" action="/health-delete" class="inline-form" onsubmit="return confirm(\'Bu sağlık kaydı silinsin mi?\')"><input type="hidden" name="id" value="{r["id"]}"><button class="btn red">Sil</button></form></td></tr>' for r in g['rows'])
                latest=g['rows'][0]['applied_date'] if g['rows'] else ''
                group_cards.append(f'''<details class="health-group"><summary><span><b>🐄 {h(g['tag'])}</b> · {h(g['nickname'])}</span><span class="mut">{len(g['rows'])} kayıt · Son işlem {fmt_date(latest)} ▾</span></summary><div class="tablewrap"><table><tr><th>Tarih</th><th>Tür</th><th>Ürün/İşlem</th><th>Sonraki</th><th>Maliyet</th><th>İşlem</th></tr>{inner}</table></div></details>''')
            grouped_health_html=''.join(group_cards) or '<p class="mut">Henüz sağlık kaydı yok.</p>'
            def due_badge(due):
                try:days=(date.fromisoformat(due)-date.today()).days
                except:days=9999
                if days<0:return '🔴 '+str(abs(days))+' gün gecikti'
                if days==0:return '🟠 Bugün'
                if days<=3:return '🟠 '+str(days)+' gün kaldı'
                return '🟡 '+str(days)+' gün kaldı'
            task_groups={}
            for r in task_rows:
                key=('P',r['course_id'],r['planned_date'],r['dose_no'],r['day_no'],r['application_no']) if r['scope_type']=='paddock' else ('S',r['id'])
                task_groups.setdefault(key,[]).append(r)
            task_cards=[]
            for key,items in task_groups.items():
                r=items[0];badge=due_badge(r['planned_date'])
                detail=(f'{int(r["dose_no"] or 1)} / {int(r["dose_total"] or 1)}. doz' if r['kind']=='Aşı' else f'{int(r["day_no"] or 1)} / {int(r["day_total"] or 1)}. gün · {int(r["application_no"] or 1)} / {int(r["applications_per_day"] or 1)} uygulama')
                if r['scope_type']=='paddock':
                    title='🏠 '+str(r['paddock_name'] or 'Padok');meta=f'{len(items)} hayvan · {detail}'
                    action=f'''<form method="post" action="/health/task-batch-done"><input type="hidden" name="course_id" value="{r['course_id']}"><input type="hidden" name="planned_date" value="{h(r['planned_date'])}"><input type="hidden" name="dose_no" value="{int(r['dose_no'] or 1)}"><input type="hidden" name="day_no" value="{int(r['day_no'] or 1)}"><input type="hidden" name="application_no" value="{int(r['application_no'] or 1)}"><button class="btn">✅ {len(items)} Hayvan Yapıldı</button></form>'''
                else:
                    title='🐄 '+str(r['animal_tag'] or r['calf_tag'] or '-');meta=detail
                    action=f'''<form method="post" action="/health/task-done"><input type="hidden" name="task_id" value="{r['id']}"><button class="btn">✅ Yapıldı</button></form>'''
                task_cards.append(f'''<div class="health-plan-card"><div class="health-plan-main"><div><b>{h(title)}</b><div class="health-plan-product">{h(r['product'])}</div><div class="mut">{h(meta)} · {fmt_date(r['planned_date'])}</div></div><span class="health-due">{badge}</span></div><div class="health-plan-action">{action}</div></div>''')
            for r in legacy_plans:
                tag=r['animal_tag'] or r['calf_tag'] or '-';badge=due_badge(r['next_date'])
                action=(f'''<form method="post" action="/health/second-dose-done"><input type="hidden" name="source_id" value="{r['id']}"><input type="hidden" name="return_to" value="/health"><button class="btn">✅ 2. Doz Yapıldı</button></form>''' if str(r['kind'] or '')=='Aşı' and 'IKINCI_DOZ_PLAN' in str(r['notes'] or '') else f'''<form method="post" action="/health/plan-done"><input type="hidden" name="source_id" value="{r['id']}"><input type="hidden" name="return_to" value="/health"><button class="btn">✅ Yapıldı</button></form>''')
                task_cards.append(f'''<div class="health-plan-card"><div class="health-plan-main"><div><b>🐄 {h(tag)}</b><div class="health-plan-product">{h(r['product'])}</div><div class="mut">Eski plan · {fmt_date(r['next_date'])}</div></div><span class="health-due">{badge}</span></div><div class="health-plan-action">{action}</div></div>''')
            planned_html=''.join(task_cards) or '<p class="mut">Planlanmış sağlık işlemi yok.</p>'
            body=f'''<style>.health-mode-box{{background:#f7fbf8;border:1px solid #d7eadc;border-radius:16px;padding:14px 16px}}.health-plan-list{{display:grid;gap:10px}}.health-plan-card{{border:1px solid #dfe9e2;border-radius:15px;padding:14px;background:#fff}}.health-plan-main{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}}.health-plan-product{{font-weight:800;margin:5px 0}}.health-due{{white-space:nowrap;font-weight:800}}.health-plan-action{{margin-top:12px}}.health-plan-action form{{margin:0}}@media(max-width:700px){{.health-plan-main{{display:block}}.health-due{{display:inline-block;margin-top:8px}}.health-plan-action .btn{{width:100%}}.health-group summary{{align-items:flex-start;flex-direction:column}}}}</style><h1>Sağlık</h1>
            <div class="card"><form method="post" class="form" id="healthForm"><label>Uygulama Kapsamı<select name="scope_type" id="healthScope"><option value="single">Tek Hayvan / Buzağı</option><option value="paddock">Padok Bazında Aşılama</option></select></label><label>Tür<select name="kind" id="healthKind"><option>Aşı</option><option>İlaç</option><option>Muayene</option></select></label>
            <div class="full" id="singleSubjectBox"><label>Hayvan / Buzağı</label><div style="position:relative"><input type="search" id="healthSubjectSearch" placeholder="Küpe veya takma ad yazın…" autocomplete="off"><input type="hidden" name="subject_key" id="healthSubjectKey"><div id="healthSubjectResults" style="display:none;position:absolute;left:0;right:0;top:100%;z-index:30;background:#fff;border:1px solid #d7e4da;border-radius:12px;max-height:280px;overflow:auto;box-shadow:0 12px 28px #173b2822"></div></div><div class="mut">Aktif hayvanlar ve buzağılar listelenir.</div></div>
            <div class="full" id="paddockSubjectBox" style="display:none"><label>Padok<select name="paddock_id" id="healthPaddock"><option value="">Padok seçin…</option>{paddock_options}</select></label><div class="mut">Plan oluşturulduğu anda padoktaki aktif hayvan listesi sabitlenir. Sonradan padoka giren hayvanlar bu plana eklenmez.</div></div>
            <label>Ürün/İşlem<input name="product" required placeholder="Örn. Şap aşısı / antibiyotik"></label><label>Başlangıç / Uygulama Tarihi<input type="date" name="applied_date" id="healthAppliedDate" required value="{date.today().isoformat()}"></label>
            <div class="full health-mode-box" id="vaccinePlanBox"><div class="form"><label>Kaç Doz?<input type="number" name="dose_count" id="doseCount" min="1" max="10" value="1"></label><label>Dozlar Arası Gün<input type="number" name="dose_interval_days" id="doseInterval" min="1" max="365" value="15"></label></div><div class="mut">Örn. 3 doz / 15 gün arayla. Tüm doz tarihleri otomatik planlanır.</div></div>
            <div class="full health-mode-box" id="medicinePlanBox" style="display:none"><div class="form"><label>Tedavi Kaç Gün?<input type="number" name="treatment_days" min="1" max="60" value="5"></label><label>Günde Kaç Uygulama?<input type="number" name="times_per_day" min="1" max="6" value="1"></label></div><div class="mut">Her uygulama ayrı ayrı “Yapıldı” işaretlenir; geciken uygulamalar otomatik görünür.</div></div>
            <label id="nextDateLabel" style="display:none">Sonraki Tarih<input type="date" name="next_date" id="healthNextDate"></label><label>Uygulama Başı / Hayvan Başı Maliyet<input type="number" step="0.01" min="0" name="cost" value="0"></label><label class="full">Not<textarea name="notes"></textarea></label><div class="full"><button class="btn" id="healthSubmit">💾 Planı Oluştur</button></div></form></div>
            <div class="card" style="margin-top:14px"><h2>💉 Planlanan Aşı / Tedavi İşlemleri</h2><div class="health-plan-list">{planned_html}</div></div><div class="card" style="margin-top:14px"><h2>🩺 Hayvan Bazlı Sağlık Dosyaları</h2><p class="mut">Tamamlanan tedavi, aşı ve muayeneler hayvanın gerçek sağlık geçmişine işlenir.</p>{grouped_health_html}</div>
            <script>const healthSubjects={subject_json};const hs=document.getElementById('healthSubjectSearch'),hk=document.getElementById('healthSubjectKey'),hr=document.getElementById('healthSubjectResults');function renderHealthSubjects(){{const q=(hs.value||'').toLocaleLowerCase('tr-TR').trim();const found=healthSubjects.filter(x=>!q||x.label.toLocaleLowerCase('tr-TR').includes(q)).slice(0,40);hr.innerHTML=found.map((x,i)=>'<button type="button" data-index="'+i+'" style="display:block;width:100%;text-align:left;border:0;border-bottom:1px solid #eef3ef;background:#fff;padding:12px 14px;font:inherit;cursor:pointer">'+x.label+'</button>').join('');hr.style.display=found.length?'block':'none';hr.querySelectorAll('button').forEach(b=>b.onclick=function(){{const x=found[parseInt(this.dataset.index)];hk.value=x.key;hs.value=x.label;hr.style.display='none';}});}}hs.addEventListener('input',function(){{hk.value='';renderHealthSubjects();}});hs.addEventListener('focus',renderHealthSubjects);document.addEventListener('click',e=>{{if(!hr.contains(e.target)&&e.target!==hs)hr.style.display='none';}});const scope=document.getElementById('healthScope'),kind=document.getElementById('healthKind'),single=document.getElementById('singleSubjectBox'),paddock=document.getElementById('paddockSubjectBox'),vbox=document.getElementById('vaccinePlanBox'),mbox=document.getElementById('medicinePlanBox'),nlabel=document.getElementById('nextDateLabel'),submit=document.getElementById('healthSubmit'),doseCount=document.getElementById('doseCount'),doseInterval=document.getElementById('doseInterval');function syncHealthForm(){{if(scope.value==='paddock'&&kind.value!=='Aşı')kind.value='Aşı';single.style.display=scope.value==='single'?'block':'none';paddock.style.display=scope.value==='paddock'?'block':'none';vbox.style.display=kind.value==='Aşı'?'block':'none';mbox.style.display=kind.value==='İlaç'?'block':'none';nlabel.style.display=kind.value==='Muayene'?'block':'none';doseInterval.closest('label').style.display=(parseInt(doseCount.value||1)>1)?'block':'none';submit.textContent=(kind.value==='Muayene')?'💾 Sağlık Kaydını Kaydet':'💾 Planı Oluştur';}}scope.addEventListener('change',syncHealthForm);kind.addEventListener('change',syncHealthForm);doseCount.addEventListener('input',syncHealthForm);syncHealthForm();document.getElementById('healthForm').addEventListener('submit',function(e){{if(scope.value==='single'&&!hk.value){{e.preventDefault();alert('Lütfen listeden bir hayvan veya buzağı seçin.');hs.focus();return;}}if(scope.value==='paddock'&&!document.getElementById('healthPaddock').value){{e.preventDefault();alert('Lütfen bir padok seçin.');}}}});</script>'''
            return self.send_html(page('Sağlık',body,'/health',u,msg))
        if path=='/finance/edit':
            record_id=int(q.get('id',['0'])[0])
            with db() as c:
                r=c.execute('select f.*,a.tag,a.nickname from finance f left join animals a on a.id=f.animal_id where f.id=?',(record_id,)).fetchone()
                animals=c.execute('select id,tag,nickname,status from animals order by tag').fetchall()
            if not r:return self.redirect('/finance','Finans kaydı bulunamadı.')
            animal_options='<option value="">Hayvan seçmeden kaydet</option>'+''.join(
                '<option value="{0}" {1}>{2} · {3} · {4}</option>'.format(
                    a["id"],'selected' if r["animal_id"]==a["id"] else '',h(a["tag"]),h(a["nickname"]),h(a["status"])
                ) for a in animals
            )
            categories=['Süt Satışı','Hayvan Satışı','Kesim Geliri','Buzağı Satışı','Destekleme','Yem','Veteriner','İlaç','Aşı','Saman','Elektrik','Yakıt','İşçilik','Hayvan Alımı','Diğer']
            category_options=''.join('<option {0}>{1}</option>'.format('selected' if r["category"]==x else '',h(x)) for x in categories)
            body=f'''<h1>Finans Kaydını Düzenle</h1><div class="card"><form method="post" action="/finance/edit" class="form">
            <input type="hidden" name="id" value="{r["id"]}">
            <label>Tarih<input type="date" name="tx_date" value="{h(r["tx_date"])}" required></label>
            <label>Tür<select name="tx_type"><option {"selected" if r["tx_type"]=="Gelir" else ""}>Gelir</option><option {"selected" if r["tx_type"]=="Gider" else ""}>Gider</option></select></label>
            <label>Kategori<select name="category" id="financeCategory">{category_options}</select></label>
            <label>Tutar<input type="number" step="0.01" min="0" name="amount" value="{r["amount"]}" required></label>
            <label>Ödeme<select name="payment_method"><option {"selected" if r["payment_method"]=="Nakit" else ""}>Nakit</option><option {"selected" if r["payment_method"]=="Banka" else ""}>Banka</option><option {"selected" if r["payment_method"]=="Kredi Kartı" else ""}>Kredi Kartı</option><option {"selected" if r["payment_method"]=="Vadeli" else ""}>Vadeli</option></select></label>
            <label>İlgili Hayvan<select name="animal_id" id="financeAnimal">{animal_options}</select></label>
            <label class="full">Açıklama<input name="description" value="{h(r["description"])}"></label>
            <div class="full" id="statusWarning" style="display:none;padding:12px;border-radius:10px;background:#fff3cd;color:#664d03"><b>Uyarı:</b> Satış veya kesim seçilirse hayvan aktif sürüden çıkarılır. Kategori değiştirilirse durum yeniden hesaplanır.</div>
            <div class="full"><button class="btn">Değişiklikleri Kaydet</button> <a class="btn alt" href="/finance">İptal</a></div>
            </form></div>'''
            return self.send_html(page('Finans Düzenle',body,path,u,msg))
        if path=='/finance':
            start=q.get('start',[date.today().replace(day=1).isoformat()])[0]; end=q.get('end',[date.today().isoformat()])[0]; typ=q.get('type',[''])[0]; category=q.get('category',[''])[0]
            sql='''select f.*,a.tag,
            case when f.category='Süt Satışı'
                 then coalesce((select group_concat(a2.tag, ', ') from finance_animals fa join animals a2 on a2.id=fa.animal_id where fa.finance_id=f.id and fa.relation_type='Süt Satışı'),a.tag)
                 else a.tag end as related_tags
            from finance f left join animals a on a.id=f.animal_id where tx_date between ? and ?'''; args=[start,end]
            if typ: sql+=' and tx_type=?'; args.append(typ)
            if category: sql+=' and category=?'; args.append(category)
            sql+=' order by tx_date desc,id desc'
            with db() as c:
                animals=c.execute("select id,tag,nickname,gender from animals where coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                purchase_linked_ids={int(r['animal_id']) for r in c.execute("select distinct animal_id from finance where category='Hayvan Alımı' and animal_id is not null").fetchall()}
                milk_females=[a for a in animals if str(a['gender'] or '')=='Dişi']
                categories=c.execute("select distinct category from finance where coalesce(category,'')<>'' order by category").fetchall()
                rows=c.execute(sql,args).fetchall()
                inc=sum(float(r['amount'] or 0) for r in rows if r['tx_type']=='Gelir'); exp=sum(float(r['amount'] or 0) for r in rows if r['tx_type']=='Gider')
            opts=''.join(f'<option value="{a["id"]}">{h(a["tag"])} - {h(a["nickname"])}</option>' for a in animals)
            bulk_cards=''.join(f'''<label class="bulk-row" data-search="{h((str(a["tag"])+" "+str(a["nickname"] or "")).lower())}"><input type="checkbox" class="bulk-check" value="{a["id"]}" onchange="syncBulkSelection()"><span class="tag">🐄 {h(a["tag"])}</span><span class="nick">{h(a["nickname"]) or "Takma ad yok"}</span></label>''' for a in animals)
            milk_cards=''.join(f'''<label class="bulk-row milk-row" data-search="{h((str(a["tag"])+" "+str(a["nickname"] or "")).lower())}"><input type="checkbox" class="milk-check" value="{a["id"]}" onchange="syncMilkSelection()"><span class="tag">🥛 {h(a["tag"])}</span><span class="nick">{h(a["nickname"]) or "Takma ad yok"}</span></label>''' for a in milk_females)
            category_opts=''.join(f'<option value="{h(r["category"])}" {"selected" if category==r["category"] else ""}>{h(r["category"])}</option>' for r in categories)
            trs=''.join(
                '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td><b>{7}</b></td><td><div class="finance-actions"><a class="btn alt" href="/finance/edit?id={8}">Düzenle</a><form method="post" action="/finance/delete" onsubmit="return confirm(\'Bu finans kaydı silinsin mi?\')"><input type="hidden" name="id" value="{8}"><button class="btn danger">Sil</button></form></div></td></tr>'.format(
                    fmt_date(r["tx_date"]),h(r["tx_type"]),h(r["category"]),h(r["description"]),h(r["related_tags"]),h(r["animal_status_action"]) or "-",h(r["payment_method"]),money(r["amount"]),r["id"]
                ) for r in rows
            )
            body=f'''<h1>Finans</h1><div class="grid"><div class="card stat">Gelir<b>{money(inc)}</b></div><div class="card stat">Gider<b>{money(exp)}</b></div><div class="card stat">Net<b>{money(inc-exp)}</b></div></div><div class="finance-primary-actions"><button type="button" class="btn finance-new-btn" onclick="openFinanceDrawer()">➕ Yeni Finans Kaydı</button><span class="mut">Kayıtlar ve filtreler öncelikli görünür.</span></div><div id="financeDrawerBackdrop" class="finance-drawer-backdrop" onclick="closeFinanceDrawer(event)"></div><aside id="financeDrawer" class="finance-drawer" aria-hidden="true"><div class="finance-drawer-head"><div><span class="mut">FİNANS</span><h2 style="margin:3px 0">➕ Yeni Finans Kaydı</h2><span class="mut">Kaydı oluşturun; bitince listenize dönün.</span></div><button type="button" class="finance-drawer-close" onclick="closeFinanceDrawer()">×</button></div><div class="finance-drawer-body"><div class="card finance-entry-card"><form method="post" class="form" id="financeCreateForm">
<label>Tarih<input type="date" name="tx_date" required value="{date.today().isoformat()}"></label>
<label>Tür<select name="tx_type" id="tx"><option>Gelir</option><option>Gider</option></select></label>
<label>Kategori<select name="category" id="financeCategory"><option>Süt Satışı</option><option>Hayvan Satışı</option><option>Kesim Geliri</option><option>Buzağı Satışı</option><option>Destekleme</option><option>Yem</option><option>Veteriner</option><option>İlaç</option><option>Aşı</option><option>Saman</option><option>Elektrik</option><option>Yakıt</option><option>İşçilik</option><option>Hayvan Alımı</option><option>Diğer</option></select></label>
<label>Toplam Tutar<input type="number" step="0.01" min="0.01" name="amount" id="financeAmount" required></label>
<label>Ödeme Yöntemi<select name="payment_method"><option>Nakit</option><option>Banka</option><option>Kredi Kartı</option><option>Vadeli</option></select></label>
<label id="singleAnimalLabel">İlgili Hayvan<select name="animal_id" id="financeAnimal"><option value="">Yok</option>{opts}</select></label>
<input type="hidden" name="animal_ids" id="bulkAnimalIds" value="">
<div class="full bulk-animal-box" id="bulkAnimalBox"><div class="bulk-picker"><div class="bulk-picker-head"><div><h3 style="margin:0">🐄 İlgili Hayvanlar</h3><div class="mut">İlgili hayvanları seçin.</div></div><input class="bulk-search" id="bulkSearch" placeholder="Küpe veya takma ad ara…" oninput="filterBulkAnimals()"></div><div class="bulk-list" id="bulkList">{bulk_cards}</div><div class="bulk-summary"><span class="pill">Seçilen <b id="bulkCount">0</b> hayvan</span><span class="pill"><span id="bulkShareLabel">Hayvan Başı</span> <b id="bulkShare">₺0,00</b></span><button type="button" class="btn alt" onclick="clearBulkAnimals()">Seçimi Temizle</button></div><div class="bulk-selected-preview" id="bulkSelectedPreview">Henüz hayvan seçilmedi.</div></div></div><input type="hidden" name="milk_animal_ids" id="milkAnimalIds" value=""><div class="full bulk-animal-box" id="milkAnimalBox" style="display:none"><div class="bulk-picker"><div class="bulk-picker-head"><div><h3 style="margin:0">🥛 Süt Gelirine Dahil Dişi Hayvanlar</h3><div class="mut">Yalnızca aktif dişi hayvanlar gösterilir. Toplam süt geliri bölünmez; seçilen hayvanlar kayda ilişkilendirilir.</div></div><input class="bulk-search" id="milkSearch" placeholder="Dişi küpe veya takma ad ara…" oninput="filterMilkAnimals()"></div><div class="bulk-list" id="milkList">{milk_cards}</div><div class="bulk-summary"><span class="pill">Seçilen <b id="milkCount">0</b> dişi</span><span class="pill">Toplam gelir <b id="milkTotal">₺0,00</b></span><button type="button" class="btn alt" onclick="clearMilkAnimals()">Seçimi Temizle</button></div><div class="bulk-selected-preview" id="milkSelectedPreview">Henüz dişi hayvan seçilmedi.</div></div></div>
<label class="full">Açıklama<input name="description"></label>
<div class="full" id="statusWarning" style="display:none;padding:12px;border-radius:10px;background:#fff3cd;color:#664d03"><b>Uyarı:</b> Seçilen hayvanlar işlem türüne göre aktif sürüden çıkarılır; geçmiş bilgileri silinmez. Toplam tutar seçilen hayvan sayısına göre otomatik dağıtılır.</div>
<div class="full finance-savebar"><button type="submit" class="btn" id="financeSubmitBtn">💾 Finans Kaydını Kaydet</button><span class="mut" id="financeSaveHint"></span></div></form></div></div></aside><div class="card finance-filter-card" id="financeRecords" style="margin-top:14px"><div class="finance-filter-title"><div><h2>🔎 Finans Filtreleri</h2><span class="mut">Tarih, işlem türü ve kategoriye göre kayıtları daraltın.</span></div><span class="filter-count-pill">{len(rows)} kayıt</span></div><form method="get" class="finance-toolbar finance-toolbar-modern"><label><span>📅 Başlangıç</span><input type="date" name="start" value="{h(start)}"></label><label><span>📅 Bitiş</span><input type="date" name="end" value="{h(end)}"></label><label><span>↕️ Tür</span><select name="type"><option value="">Gelir + Gider</option><option {'selected' if typ=='Gelir' else ''}>Gelir</option><option {'selected' if typ=='Gider' else ''}>Gider</option></select></label><label><span>🏷️ Kategori</span><select name="category"><option value="">Tüm Kategoriler</option>{category_opts}</select></label><div class="finance-filter-actions"><button class="btn blue">🔎 Filtrele</button><a class="btn alt" href="/finance">↺ Temizle</a><a class="btn export-btn" href="/finance/export?start={urllib.parse.quote(start)}&end={urllib.parse.quote(end)}&type={urllib.parse.quote(typ)}&category={urllib.parse.quote(category)}">⬇ CSV</a></div></form><div class="finance-table-wrap"><table class="finance-table"><tr><th>Tarih</th><th>Tür</th><th>Kategori</th><th>Açıklama</th><th>Hayvan</th><th>Durum</th><th>Ödeme</th><th>Tutar</th><th>İşlem</th></tr>{trs}</table></div></div>'''
            body += f'''<script>
            function isBulkFinance(){{
              const t=document.getElementById('tx').value;
              const c=document.getElementById('financeCategory').value;
              return t==='Gelir' && (c==='Hayvan Satışı' || c==='Kesim Geliri');
            }}
            function isMilkFinance(){{return document.getElementById('tx').value==='Gelir' && document.getElementById('financeCategory').value==='Süt Satışı';}}
            function formatTRY(v){{return new Intl.NumberFormat('tr-TR',{{style:'currency',currency:'TRY'}}).format(v||0);}}
            function selectedChecks(){{return Array.from(document.querySelectorAll('.bulk-check:checked'));}}
            function syncBulkSelection(){{
              const checks=selectedChecks();
              checks.forEach(x=>x.closest('.bulk-row').classList.add('selected'));
              document.querySelectorAll('.bulk-check:not(:checked)').forEach(x=>x.closest('.bulk-row').classList.remove('selected'));
              document.getElementById('bulkAnimalIds').value=checks.map(x=>x.value).join(',');
              document.getElementById('bulkCount').textContent=checks.length;
              const total=parseFloat(document.getElementById('financeAmount').value||'0');
              document.getElementById('bulkShare').textContent=formatTRY(checks.length ? total/checks.length : 0);
              const shareLabel=document.getElementById('bulkShareLabel');
              if(shareLabel) shareLabel.textContent=checks.length===1?'Satış / Kesim Bedeli':'Hayvan Başı';
              const labels=checks.slice(0,5).map(x=>x.closest('.bulk-row').querySelector('.tag').textContent.trim());
              document.getElementById('bulkSelectedPreview').textContent=checks.length ? labels.join(' · ')+(checks.length>5?' · +'+(checks.length-5)+' diğer':'') : 'Henüz hayvan seçilmedi.';
              document.getElementById('financeSaveHint').textContent=(isBulkFinance()&&checks.length)
                ? (checks.length===1 ? 'Seçilen hayvana '+formatTRY(total)+' yazılacak' : checks.length+' hayvana otomatik dağıtılacak')
                : '';
            }}
            function syncMilkSelection(){{
              const checks=Array.from(document.querySelectorAll('.milk-check:checked'));
              document.querySelectorAll('.milk-row').forEach(x=>x.classList.toggle('selected',x.querySelector('.milk-check').checked));
              document.getElementById('milkAnimalIds').value=checks.map(x=>x.value).join(',');document.getElementById('milkCount').textContent=checks.length;
              document.getElementById('milkTotal').textContent=formatTRY(parseFloat(document.getElementById('financeAmount').value||'0'));
              const labels=checks.slice(0,8).map(x=>x.closest('.milk-row').querySelector('.tag').textContent.trim());
              document.getElementById('milkSelectedPreview').textContent=checks.length?labels.join(' · ')+(checks.length>8?' · +'+(checks.length-8)+' diğer':''):'Henüz dişi hayvan seçilmedi.';
              if(isMilkFinance())document.getElementById('financeSaveHint').textContent=checks.length+' dişi hayvan süt gelirine ilişkilendirilecek';
            }}
            function clearMilkAnimals(){{document.querySelectorAll('.milk-check').forEach(x=>x.checked=false);syncMilkSelection();}}
            function filterMilkAnimals(){{const q=(document.getElementById('milkSearch').value||'').toLocaleLowerCase('tr-TR').trim();document.querySelectorAll('.milk-row').forEach(row=>{{row.style.display=!q||row.dataset.search.toLocaleLowerCase('tr-TR').includes(q)?'grid':'none';}});}}
            function refreshPurchaseAnimalOptions(){{
              const category=document.getElementById('financeCategory').value;
              const select=document.getElementById('financeAnimal');
              const purchaseMode=category==='Hayvan Alımı';
              Array.from(select.options).forEach(function(opt){{
                if(!opt.value)return;
                const used=opt.dataset.purchaseLinked==='1';
                opt.hidden=purchaseMode&&used;
                opt.disabled=purchaseMode&&used;
              }});
              if(select.selectedOptions.length&&select.selectedOptions[0].disabled)select.value='';
            }}
            function refreshBulkFinance(){{
              const on=isBulkFinance(),milk=isMilkFinance();
              document.getElementById('bulkAnimalBox').style.display=on?'block':'none';document.getElementById('milkAnimalBox').style.display=milk?'block':'none';
              document.getElementById('singleAnimalLabel').style.display=(on||milk)?'none':'block';document.getElementById('financeAnimal').required=false;
              document.getElementById('statusWarning').style.display=on?'block':'none';refreshPurchaseAnimalOptions();syncBulkSelection();syncMilkSelection();
            }}
            function clearBulkAnimals(){{
              document.querySelectorAll('.bulk-check').forEach(x=>x.checked=false);
              syncBulkSelection();
            }}
            function filterBulkAnimals(){{
              const q=(document.getElementById('bulkSearch').value||'').toLocaleLowerCase('tr-TR').trim();
              document.querySelectorAll('.bulk-row').forEach(row=>{{row.style.display=!q||row.dataset.search.toLocaleLowerCase('tr-TR').includes(q)?'grid':'none';}});
            }}
            document.getElementById('tx').addEventListener('change',refreshBulkFinance);
            document.getElementById('financeCategory').addEventListener('change',refreshBulkFinance);
            document.getElementById('financeAmount').addEventListener('input',function(){{syncBulkSelection();syncMilkSelection();}});
            document.getElementById('financeCreateForm').addEventListener('submit',function(e){{
              syncBulkSelection();
              if(isBulkFinance()) document.getElementById('financeAnimal').required=false;
              if(isBulkFinance() && selectedChecks().length===0){{
                e.preventDefault();
                alert('Hayvan satışı veya kesim geliri için en az bir hayvan seçmelisiniz.');
                return false;
              }}
              if(isMilkFinance() && document.querySelectorAll('.milk-check:checked').length===0){{
                e.preventDefault();
                alert('Süt satışı için en az bir aktif dişi hayvan seçmelisiniz.');
                return false;
              }}
              if(this.dataset.submitting==='1'){{
                e.preventDefault();
                return false;
              }}
              this.dataset.submitting='1';
              const submitBtn=this.querySelector('button[type=submit]');
              if(submitBtn){{
                submitBtn.disabled=true;
                submitBtn.textContent='⏳ Kaydediliyor…';
              }}
            }});
            refreshBulkFinance();
            function setFinanceDrawer(open){{const d=document.getElementById('financeDrawer'),b=document.getElementById('financeDrawerBackdrop');if(!d||!b)return;d.classList.toggle('open',open);b.classList.toggle('open',open);d.setAttribute('aria-hidden',open?'false':'true');document.body.style.overflow=open?'hidden':'';}}
function openFinanceDrawer(){{setFinanceDrawer(true);}}
function closeFinanceDrawer(ev){{if(ev&&ev.target!==document.getElementById('financeDrawerBackdrop'))return;setFinanceDrawer(false);}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')setFinanceDrawer(false);}});
setTimeout(()=>setFinanceDrawer(false),0);
</script>'''
            return self.send_html(page('Finans',body,'/finance',u,msg))
        if path=='/reports':
            profile=farm_profile(); farm_name=farm_display_name(profile)
            start=q.get('start',[(date.today()-timedelta(days=365)).isoformat()])[0]; end=q.get('end',[date.today().isoformat()])[0]
            with db() as c:
                sums=c.execute('select tx_type,category,sum(amount) total,count(*) cnt from finance where tx_date between ? and ? group by tx_type,category order by tx_type, total desc',(start,end)).fetchall(); monthly=c.execute("select substr(tx_date,1,7) m, sum(case when tx_type='Gelir' then amount else 0 end) inc, sum(case when tx_type='Gider' then amount else 0 end) exp from finance where tx_date between ? and ? group by m order by m",(start,end)).fetchall()
            inc=sum(r['total'] for r in sums if r['tx_type']=='Gelir');exp=sum(r['total'] for r in sums if r['tx_type']=='Gider'); maxv=max([max(r['inc'],r['exp']) for r in monthly] or [1])
            bars=''.join(f'<div style="flex:1;display:flex;align-items:end;gap:2px;height:170px"><div class="bar" style="height:{max(2,r["inc"]/maxv*150)}px"><i>{int(r["inc"])}</i></div><div class="bar" style="height:{max(2,r["exp"]/maxv*150)}px;background:linear-gradient(#e76d5b,#b9382b)"><i>{int(r["exp"])}</i></div><span style="position:absolute"></span><small style="position:absolute;margin-top:175px">{h(r["m"])}</small></div>' for r in monthly)
            trs=''.join(f'<tr><td>{h(r["tx_type"])}</td><td>{h(r["category"])}</td><td>{r["cnt"]}</td><td>{money(r["total"])}</td></tr>' for r in sums)
            body=f'''<h1>{h(farm_name)} · Finans Raporları</h1><div class="card"><form class="actions"><label>Başlangıç <input type="date" name="start" value="{start}"></label><label>Bitiş <input type="date" name="end" value="{end}"></label><button class="btn">Raporla</button><a class="btn blue" href="/reports/export?start={start}&end={end}">Rapor CSV</a></form></div><div class="grid" style="margin-top:14px"><div class="card stat">Toplam Gelir<b>{money(inc)}</b></div><div class="card stat">Toplam Gider<b>{money(exp)}</b></div><div class="card stat">Net Sonuç<b>{money(inc-exp)}</b></div><div class="card stat">Gider/Gelir Oranı<b>{(exp/inc*100 if inc else 0):.1f}%</b></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>Aylık Gelir / Gider</h2><p class="mut">Yeşil: gelir · Kırmızı: gider</p><div class="chart">{bars or '<p>Kayıt yok</p>'}</div></div><div class="card"><h2>Kategori Özeti</h2><table><tr><th>Tür</th><th>Kategori</th><th>Adet</th><th>Toplam</th></tr>{trs}</table></div></div>'''
            return self.send_html(page('Raporlar',body,'/reports',u,msg))
        if path=='/data':
            body="""<h1>Veri Aktarımı</h1><div class='two'><div class='card'><h2>JSON'dan İçe Aktar</h2><p class='mut'>Eski sistem yedeklerini ve V0.6 dışa aktarımlarını destekler. İçe aktarmadan önce otomatik veritabanı yedeği alınır.</p><form method='post' action='/data/import' enctype='multipart/form-data' class='form'><label class='full'>JSON dosyası<input type='file' name='json_file' accept='.json,application/json' required></label><label>Çakışan küpeler<select name='strategy'><option value='skip'>Atla (önerilen)</option><option value='update'>Mevcut kaydı güncelle</option></select></label><div class='full'><button class='btn'>İçe Aktar</button></div></form></div><div class='card'><h2>Dışa Aktar</h2><p>Tüm hayvan, tohumlama, buzağı, sağlık ve finans kayıtlarını tek JSON dosyasına aktarır.</p><div class='actions'><a class='btn blue' href='/data/export'>JSON Yedeğini İndir</a><a class='btn alt' href='/backups'>SQLite Yedekleri</a></div><hr><p class='mut'>JSON taşınabilir veri yedeğidir. SQLite yedeği uygulamanın birebir veritabanı kopyasıdır.</p></div></div>"""
            return self.send_html(page('Veri Aktarımı',body,'/data',u,msg))
        if path=='/data/export':
            b=json.dumps(export_payload(),ensure_ascii=False,indent=2).encode('utf-8');name=f'ciftlik_json_yedek_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            self.send_response(200);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Disposition',f'attachment; filename="{name}"');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        if path=='/backups':
            if not self.require_admin():return
            target_dir=configured_backup_dir()
            raw_dir=(get_setting('backup_directory','') or '').strip()
            disk_files=[fp for fp in target_dir.glob('CiftlikPro_Backup_*.zip') if fp.is_file()]
            disk_files.sort(key=lambda x:x.stat().st_mtime,reverse=True)
            trs=''.join(
                f'<tr><td>{fmt_datetime(datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"))}</td><td>{h(fp.name)}</td><td>{format_bytes(fp.stat().st_size)}</td><td><a class="btn blue" href="/backup/download?file={urllib.parse.quote(fp.name)}">İndir</a> <form method="post" action="/backup/restore-existing" class="inline-form" onsubmit="return confirm(\'Bu yedek geri yüklensin mi?\')"><input type="hidden" name="file" value="{h(fp.name)}"><button class="btn orange">Geri Yükle</button></form> <a class="btn red" href="/backup/delete?file={urllib.parse.quote(fp.name)}" onclick="return confirm(\'Bu yedek silinsin mi?\')">Sil</a></td></tr>'
                for fp in disk_files[:100]
            ) or '<tr><td colspan=4>Seçili klasörde yedek bulunamadı.</td></tr>'
            stats=uploads_storage_stats()
            body=f'''<h1>Yedekleme Merkezi</h1>
            <div class="grid" style="margin-bottom:14px">
              <div class="card stat"><span class="mut">Veritabanı</span><b>{format_bytes(stats["db_bytes"])}</b></div>
              <div class="card stat"><span class="mut">Fotoğraflar</span><b>{format_bytes(stats["upload_bytes"])}</b><small>{stats["upload_count"]} dosya</small></div>
              <div class="card stat"><span class="mut">Toplam Veri</span><b>{format_bytes(stats["total_bytes"])}</b></div>
              <div class="card stat"><span class="mut">Yedek Klasörü</span><b style="font-size:14px;word-break:break-all">{h(str(target_dir))}</b></div>
            </div>
            <div class="two">
              <div class="card"><h2>Yedekleme Ayarları</h2>
                <form method="post" action="/backup/settings" class="form">
                  <label class="full">Yedek Klasörü<input name="backup_directory" value="{h(raw_dir or str(BACKUPS))}" placeholder="D:\\CiftlikPro_Yedekler"></label>
                  <div class="full mut">D:, harici disk veya erişilebilir ağ klasörü kullanabilirsiniz. Program yolu hatırlar.</div>
                  <div class="full"><button class="btn">Klasörü Kaydet ve Test Et</button></div>
                </form>
                <hr style="border:0;border-top:1px solid #e2ece5;margin:18px 0">
                <h3>Fotoğraf Optimizasyonu</h3>
                <p class="mut">Yeni fotoğraflar otomatik olarak 1024 px WebP biçiminde saklanır.</p>
                <form method="post" action="/photos/optimize-existing" onsubmit="return confirm('Mevcut fotoğraflar küçültülsün mü? Önce güvenlik yedeği alınacaktır.')"><button class="btn orange">Mevcut Fotoğrafları Optimize Et</button></form>
              </div>
              <div class="card"><h2>Tam Yedek Al</h2><p>Veritabanı ve fotoğraflar seçili klasörde tek ZIP dosyasında saklanır.</p><a class="btn orange" href="/backup/create">Şimdi Yedek Al</a>
                <hr style="border:0;border-top:1px solid #e2ece5;margin:18px 0">
                <h2>Dosyadan Geri Yükle</h2><form method="post" action="/backup/restore" enctype="multipart/form-data"><input type="file" name="backup_file" accept=".zip" required><label style="display:block;margin:12px 0"><input type="checkbox" name="confirm_restore" value="yes" required> Mevcut verilerin değiştirileceğini kabul ediyorum.</label><button class="btn red">Yedeği Geri Yükle</button></form>
              </div>
            </div>
            <div class="card" style="margin-top:14px"><h2>Seçili Klasördeki Yedekler</h2><div class="tablewrap"><table><tr><th>Tarih</th><th>Dosya</th><th>Boyut</th><th>İşlem</th></tr>{trs}</table></div></div>'''
            return self.send_html(page('Yedekleme Merkezi',body,'/backups',u,msg))
        if path=='/backup/create':
            if not self.require_admin():return
            name=create_backup('manuel');audit(u,'Yedek oluşturdu',name,self.client_ip());return self.redirect('/backups','Tam yedek oluşturuldu.')
        if path=='/backup/download':
            if not self.require_admin():return
            name=os.path.basename(q.get('file',[''])[0]);fp=configured_backup_dir()/name
            if not fp.exists():return self.send_html('Dosya bulunamadı',404)
            b=fp.read_bytes();self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition',f'attachment; filename="{name}"');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        if path=='/backup/delete':
            if not self.require_admin():return
            name=os.path.basename(q.get('file',[''])[0]);fp=configured_backup_dir()/name
            if fp.exists():fp.unlink()
            with db() as c:c.execute('delete from backups where filename=?',(name,))
            audit(u,'Yedek sildi',name,self.client_ip());return self.redirect('/backups','Yedek silindi.')
        if path in ('/finance/export','/reports/export'):
            start=q.get('start',['0000-01-01'])[0];end=q.get('end',['9999-12-31'])[0];typ=q.get('type',[''])[0];category=q.get('category',[''])[0]
            sql='select tx_date,tx_type,category,amount,description,payment_method from finance where tx_date between ? and ?';args=[start,end]
            if typ: sql+=' and tx_type=?'; args.append(typ)
            if category: sql+=' and category=?'; args.append(category)
            with db() as c: rows=c.execute(sql,args).fetchall()
            out=io.StringIO();w=csv.writer(out,delimiter=';');w.writerow(['Tarih','Tür','Kategori','Tutar','Açıklama','Ödeme Yöntemi']);w.writerows(rows);b=('\ufeff'+out.getvalue()).encode('utf-8')
            self.send_response(200);self.send_header('Content-Type','text/csv; charset=utf-8');self.send_header('Content-Disposition',f'attachment; filename="finans_{start}_{end}.csv"');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        self.send_html('Sayfa bulunamadı',404)
    def do_POST(self):
        ensure_archive_schema()
        path=urllib.parse.urlparse(self.path).path
        f={}
        try:
            f=self.post_data()
        except Exception as exc:
            return self.redirect('/','Form verisi okunamadı: '+str(exc))
        if path=='/license-test':
            if not self.require_admin():return
            key=(f.get('license_key') or '').strip()
            try: raw=license_key_to_bytes(key)
            except Exception:return self.redirect('/license-test','❌ Lisans anahtarı eksik, bozuk veya okunamadı. Anahtarı yeniden kopyalayıp yapıştırın.')
            ok,payload,status=validate_license_bytes(raw);payload=payload or {}
            if not ok:return self.redirect('/license-test','❌ '+str(status))
            exp=payload.get('expires_on') or 'Süresiz'
            if exp!='Süresiz':exp=fmt_date(exp)
            body=f'''<h1>🧪 Lisans Test Sonucu</h1><div class="card"><p><span class="license-ok">✅ Anahtar Geçerli</span></p><div class="kv"><div><b>Dijital İmza</b><span>✅ Doğru</span></div><div><b>Cihaz Kimliği</b><span>✅ Eşleşiyor · {h(device_id())}</span></div><div><b>Lisans Sahibi</b><span>{h(payload.get('licensee') or '-')}</span></div><div><b>Lisans Türü</b><span>{h(payload.get('license_type') or '-')}</span></div><div><b>Geçerlilik</b><span>{h(exp)}</span></div></div><p class="mut">Test başarılı. Mevcut aktif lisans değiştirilmedi.</p><a class="btn" href="/license-test">Başka Anahtar Test Et</a> <a class="btn secondary" href="/license-info">Lisans Bilgilerine Dön</a></div>'''
            return self.send_html(page('Lisans Test Sonucu',body,'/license-info',u,''))
        if path=='/license-change':
            if not self.require_admin():return
            if (f.get('confirm_change') or '')!='yes':return self.redirect('/license-change','Değişiklik için onay kutusunu işaretleyin.')
            key=(f.get('license_key') or '').strip()
            try:raw=license_key_to_bytes(key)
            except Exception:return self.redirect('/license-change','❌ Lisans anahtarı eksik, bozuk veya okunamadı. Anahtarı yeniden kopyalayıp yapıştırın.')
            ok,payload,status=validate_license_bytes(raw)
            if not ok:return self.redirect('/license-change','❌ '+str(status))
            tmp=LICENSE_FILE.with_suffix('.license.tmp');tmp.write_bytes(raw);os.replace(tmp,LICENSE_FILE)
            return self.redirect('/license-info','✅ Yeni lisans başarıyla etkinleştirildi.')
        if path=='/license-key-activate':
            key=(f.get('license_key') or '').strip()
            try: raw=license_key_to_bytes(key)
            except Exception: return self.redirect('/license','Lisans anahtarı okunamadı veya geçersiz.')
            ok,payload,status=validate_license_bytes(raw)
            if not ok:return self.redirect('/license',status)
            tmp=LICENSE_FILE.with_suffix('.license.tmp');tmp.write_bytes(raw);os.replace(tmp,LICENSE_FILE)
            return self.redirect('/login','Lisans başarıyla etkinleştirildi.')
        if path=='/license-activate':
            item=f.get('license_file')
            if not isinstance(item,dict) or not item.get('content'):
                return self.redirect('/license','Lütfen geçerli bir lisans dosyası seçin.')
            raw=item['content']
            ok,payload,status=validate_license_bytes(raw)
            if not ok:return self.redirect('/license',status)
            tmp=LICENSE_FILE.with_suffix('.license.tmp');tmp.write_bytes(raw);os.replace(tmp,LICENSE_FILE)
            return self.redirect('/login','Lisans başarıyla etkinleştirildi.')
        if path=='/forgot-password':
            identifier=(f.get('identifier') or '').strip()
            if not identifier:return self.redirect('/forgot-password','Kullanıcı adı veya e-posta girin.')
            with db() as c:user=c.execute("select * from users where active=1 and (lower(username)=lower(?) or lower(coalesce(recovery_email,''))=lower(?)) limit 1",(identifier,identifier)).fetchone()
            if not user or not (user['recovery_email'] or '').strip():return self.redirect('/forgot-password','Bu hesap için kurtarma e-postası tanımlı değil veya hesap bulunamadı.')
            with db() as c:recent=c.execute('select created_at from password_reset_codes where user_id=? order by id desc limit 1',(user['id'],)).fetchone()
            if recent:
                try:
                    if (datetime.now()-datetime.fromisoformat(recent['created_at'])).total_seconds()<60:return self.redirect('/forgot-password','Yeni kod istemeden önce 60 saniye bekleyin.')
                except Exception:pass
            code=f'{secrets.randbelow(1000000):06d}';salt=secrets.token_hex(16);expires=(datetime.now()+timedelta(minutes=5)).isoformat(timespec='seconds');created=datetime.now().isoformat(timespec='seconds')
            with db() as c:
                c.execute('insert into password_reset_codes(user_id,code_hash,salt,expires_at,attempts,used,created_at,ip_address) values(?,?,?,?,0,0,?,?)',(user['id'],reset_code_hash(salt,code),salt,expires,created,self.client_ip()));rid=c.execute('select last_insert_rowid()').fetchone()[0]
            try:send_reset_email(user['recovery_email'],user['full_name'],code)
            except Exception as exc:
                with db() as c:c.execute('update password_reset_codes set used=1 where id=?',(rid,))
                return self.redirect('/forgot-password','E-posta gönderilemedi. Yönetici SMTP ayarlarını kontrol etsin: '+str(exc))
            audit(user['username'],'Şifre sıfırlama kodu istedi','',self.client_ip());return self.redirect(f'/forgot-password?step=verify&id={rid}','Doğrulama kodu kurtarma e-postasına gönderildi.')
        if path=='/forgot-verify':
            rid=int(f.get('reset_id') or 0);code=(f.get('code') or '').strip()
            with db() as c:r=c.execute('select pr.*,u.username from password_reset_codes pr join users u on u.id=pr.user_id where pr.id=?',(rid,)).fetchone()
            if not r:return self.redirect('/forgot-password','Şifre sıfırlama isteği bulunamadı.')
            if r['used'] or int(r['attempts'] or 0)>=3:return self.redirect('/forgot-password','Bu doğrulama isteği artık kullanılamaz.')
            try:
                if datetime.now()>datetime.fromisoformat(r['expires_at']):
                    with db() as c:c.execute('update password_reset_codes set used=1 where id=?',(rid,))
                    return self.redirect('/forgot-password','Doğrulama kodunun süresi doldu. Yeni kod isteyin.')
            except Exception:return self.redirect('/forgot-password','Doğrulama isteği geçersiz.')
            if not hmac.compare_digest(reset_code_hash(r['salt'],code),r['code_hash']):
                attempts=int(r['attempts'] or 0)+1
                with db() as c:c.execute('update password_reset_codes set attempts=?,used=? where id=?',(attempts,1 if attempts>=3 else 0,rid))
                return self.redirect(f'/forgot-password?step=verify&id={rid}',f'Kod hatalı. Kalan deneme: {max(0,3-attempts)}')
            token=secrets.token_urlsafe(32);token_exp=(datetime.now()+timedelta(minutes=10)).isoformat(timespec='seconds')
            with db() as c:c.execute('update password_reset_codes set reset_token_hash=?,reset_token_expires=? where id=?',(reset_token_hash(token),token_exp,rid))
            return self.redirect(f'/forgot-password?step=reset&id={rid}&token={urllib.parse.quote(token)}','Kod doğrulandı.')
        if path=='/forgot-reset':
            rid=int(f.get('reset_id') or 0);token=f.get('token') or '';pw=f.get('password') or '';pw2=f.get('password_confirm') or ''
            if len(pw)<8:return self.redirect('/forgot-password','Yeni şifre en az 8 karakter olmalıdır.')
            if pw!=pw2:return self.redirect('/forgot-password','Yeni şifreler eşleşmiyor.')
            with db() as c:r=c.execute('select pr.*,u.username from password_reset_codes pr join users u on u.id=pr.user_id where pr.id=?',(rid,)).fetchone()
            if not r or r['used'] or not r['reset_token_hash']:return self.redirect('/forgot-password','Şifre sıfırlama bağlantısı geçersiz.')
            try:
                if datetime.now()>datetime.fromisoformat(r['reset_token_expires']):return self.redirect('/forgot-password','Şifre sıfırlama bağlantısının süresi doldu.')
            except Exception:return self.redirect('/forgot-password','Şifre sıfırlama bağlantısı geçersiz.')
            if not hmac.compare_digest(reset_token_hash(token),r['reset_token_hash']):return self.redirect('/forgot-password','Şifre sıfırlama bağlantısı geçersiz.')
            with db() as c:c.execute('update users set password=?,password_changed_at=? where id=?',(password_hash(pw),datetime.now().strftime('%Y-%m-%d %H:%M:%S'),r['user_id']));c.execute('update password_reset_codes set used=1 where id=?',(rid,))
            audit(r['username'],'Şifresini e-posta doğrulamasıyla sıfırladı','',self.client_ip());return self.redirect('/login','Şifreniz yenilendi. Yeni şifrenizle giriş yapabilirsiniz.')
        if path=='/login':
            ok,_,status=license_status()
            if not ok:return self.redirect('/license',status)
            username=(f.get('username') or '').strip()
            with db() as c:r=c.execute('select * from users where username=?',(username,)).fetchone()
            if not r or not r['active'] or not password_verify(f.get('password',''),r['password']):audit(username or 'bilinmeyen','Başarısız giriş','',self.client_ip());return self.redirect('/login','Kullanıcı adı veya şifre hatalı ya da hesap pasif.')
            if not str(r['password']).startswith('pbkdf2_sha256$'):
                with db() as c:c.execute('update users set password=?,password_changed_at=? where id=?',(password_hash(f.get('password','')),datetime.now().strftime('%Y-%m-%d %H:%M:%S'),r['id']))
            now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with db() as c:c.execute('update users set last_login=? where id=?',(now,r['id']))
            sid=secrets.token_urlsafe(24);SESSIONS[sid]={'id':r['id'],'username':r['username'],'role':r['role'],'full_name':r['full_name']};audit(r['username'],'Oturum açtı','',self.client_ip())
            self.send_response(303);self.send_header('Set-Cookie',f'sid={sid}; HttpOnly; SameSite=Lax; Path=/');self.send_header('Location','/');self.end_headers();return
        if not self.require():return
        current=self.user();username=current['username']
        if path=='/paddock/create':
            name=(f.get('name') or '').strip()
            if not name:return self.redirect('/paddocks','Padok adı zorunludur.')
            try:
                cap=max(0,int(float(f.get('capacity') or 0)))
            except Exception:cap=0
            try:
                with db() as c:c.execute('insert into paddocks(name,code,type,capacity,notes,active,created_at) values(?,?,?,?,?,1,?)',(name,(f.get('code') or '').strip(),(f.get('type') or 'Genel').strip(),cap,(f.get('notes') or '').strip(),datetime.now().isoformat(timespec='seconds')))
            except sqlite3.IntegrityError:return self.redirect('/paddocks','Bu padok adı zaten kayıtlı.')
            audit(username,'Padok oluşturdu',name,self.client_ip());return self.redirect('/paddocks','Padok oluşturuldu.')
        if path=='/paddock/assign':
            ref=(f.get('animal_ref') or '').strip();pid=int(f.get('paddock_id') or 0) or None
            if ':' not in ref:return self.redirect('/paddocks','Hayvan seçin.')
            source,raw_id=ref.split(':',1)
            if source not in ('animal','calf'):return self.redirect('/paddocks','Geçersiz hayvan türü.')
            aid=int(raw_id or 0);table='animals' if source=='animal' else 'calves'
            with db() as c:
                rec=c.execute(f'select id,tag,paddock_id from {table} where id=?',(aid,)).fetchone()
                if not rec:return self.redirect('/paddocks','Hayvan bulunamadı.')
                if pid and not c.execute('select id from paddocks where id=? and active=1',(pid,)).fetchone():return self.redirect('/paddocks','Padok bulunamadı.')
                old=rec['paddock_id'];sync_paddock_text(c,source,aid,pid)
                if old!=pid:c.execute('insert into paddock_history(animal_source,animal_id,from_paddock_id,to_paddock_id,moved_at,notes) values(?,?,?,?,?,?)',(source,aid,old,pid,datetime.now().isoformat(timespec='seconds'),(f.get('notes') or '').strip()))
            audit(username,'Hayvan padok taşıma',f'{rec["tag"]} -> {pid or "Padoksuz"}',self.client_ip());return self.redirect('/paddocks','Hayvanın padoku güncellendi.')
        if path=='/feed/create':
            name=(f.get('name') or '').strip()
            if not name:return self.redirect('/feeds','Yem adı zorunludur.')
            def num(k):
                try:return float(f.get(k) or 0)
                except:return 0.0
            try:
                with db() as c:c.execute('''insert into feed_catalog(name,category,dm_pct,ndf_pct,cp_pct,me_mcal_kg,ca_pct,p_pct,source,active) values(?,?,?,?,?,?,?,?,?,1)''',(name,(f.get('category') or 'Özel Yem').strip(),num('dm_pct'),num('ndf_pct'),num('cp_pct'),num('me_mcal_kg'),num('ca_pct'),num('p_pct'),'Kullanıcı girişi'))
            except sqlite3.IntegrityError:return self.redirect('/feeds','Bu yem zaten katalogda var.')
            audit(username,'Yem kataloğuna ekledi',name,self.client_ip());return self.redirect('/feeds','Özel yem kataloğa eklendi.')
        if path=='/feed/edit':
            try: fid=int(f.get('feed_id') or 0)
            except:return self.redirect('/feeds','Geçersiz yem kaydı.')
            name=(f.get('name') or '').strip()
            if fid<=0 or not name:return self.redirect('/feeds','Yem adı zorunludur.')
            def num(k):
                try:return float(f.get(k) or 0)
                except:return 0.0
            cols=('dm_pct','ndf_pct','cp_pct','tdn_pct','me_mcal_kg','nem_mcal_kg','neg_mcal_kg','starch_pct','fat_pct','ash_pct','ca_pct','p_pct','mg_pct','k_pct','na_pct','s_pct')
            vals=[num(k) for k in cols]
            try:
                with db() as c:
                    old=c.execute('select name from feed_catalog where id=? and active=1',(fid,)).fetchone()
                    if not old:return self.redirect('/feeds','Yem bulunamadı.')
                    c.execute('''update feed_catalog set name=?,category=?,dm_pct=?,ndf_pct=?,cp_pct=?,tdn_pct=?,me_mcal_kg=?,nem_mcal_kg=?,neg_mcal_kg=?,starch_pct=?,fat_pct=?,ash_pct=?,ca_pct=?,p_pct=?,mg_pct=?,k_pct=?,na_pct=?,s_pct=?,source=? where id=?''',(name,(f.get('category') or 'Özel Yem').strip(),*vals,(f.get('source') or 'Kullanıcı tarafından güncellendi').strip(),fid))
            except sqlite3.IntegrityError:return self.redirect('/feed-edit?id='+str(fid),'Bu yem adı başka bir kayıtta kullanılıyor.')
            audit(username,'Yem kataloğunu düzenledi',f'{old["name"]} -> {name}',self.client_ip());return self.redirect('/feeds','Yem bilgileri güncellendi.')
        if path=='/feed/delete':
            try: fid=int(f.get('feed_id') or 0)
            except:return self.redirect('/feeds','Geçersiz yem kaydı.')
            with db() as c:
                feed=c.execute('select name from feed_catalog where id=? and active=1',(fid,)).fetchone()
                if not feed:return self.redirect('/feeds','Yem bulunamadı.')
                c.execute('update feed_catalog set active=0 where id=?',(fid,))
            audit(username,'Yemi katalogdan kaldırdı',feed['name'],self.client_ip());return self.redirect('/feeds','Yem katalogdan kaldırıldı. Geçmiş rasyon/fiyat/stok kayıtları korundu.')
        if path=='/feed/price':
            try:fid=int(f.get('feed_id') or 0);price=float(f.get('price_per_kg') or 0)
            except:return self.redirect('/feeds','Yem ve fiyat bilgisi geçersiz.')
            if fid<=0 or price<0:return self.redirect('/feeds','Yem ve fiyat bilgisi geçersiz.')
            d=(f.get('effective_date') or date.today().isoformat()).strip()
            with db() as c:
                feed=c.execute('select name from feed_catalog where id=?',(fid,)).fetchone()
                if not feed:return self.redirect('/feeds','Yem bulunamadı.')
                c.execute('insert into feed_prices(feed_id,effective_date,price_per_kg,notes) values(?,?,?,?)',(fid,d,price,(f.get('notes') or '').strip()))
            audit(username,'Yem fiyatı girdi',f'{feed["name"]}: {price}',self.client_ip());return self.redirect('/feeds','Yem fiyatı kaydedildi.')
        if path=='/feed/stock':
            try:fid=int(f.get('feed_id') or 0);qty=float(f.get('quantity_kg') or 0);unit=float(f.get('unit_price') or 0)
            except:return self.redirect('/feeds','Stok bilgisi geçersiz.')
            typ=(f.get('tx_type') or 'Giriş').strip()
            if fid<=0 or qty<=0 or typ not in ('Giriş','Çıkış','Tüketim','Sayım +','Sayım -'):return self.redirect('/feeds','Stok bilgisi geçersiz.')
            d=(f.get('tx_date') or date.today().isoformat()).strip()
            with db() as c:
                feed=c.execute('select name from feed_catalog where id=?',(fid,)).fetchone()
                if not feed:return self.redirect('/feeds','Yem bulunamadı.')
                c.execute('insert into feed_stock_transactions(feed_id,tx_date,tx_type,quantity_kg,unit_price,notes) values(?,?,?,?,?,?)',(fid,d,typ,qty,unit,(f.get('notes') or '').strip()))
                if typ=='Giriş' and unit>0:c.execute('insert into feed_prices(feed_id,effective_date,price_per_kg,notes) values(?,?,?,?)',(fid,d,unit,'Stok girişinden otomatik fiyat'))
            audit(username,'Yem stok hareketi',f'{feed["name"]} {typ} {qty} kg',self.client_ip());return self.redirect('/feeds','Stok hareketi kaydedildi.')
        if path=='/ration/create':
            name=(f.get('name') or '').strip()
            if not name:return self.redirect('/rations','Rasyon adı zorunludur.')
            try:
                with db() as c:
                    rtype=(f.get('ration_type') or 'Besi').strip(); cur=c.execute('insert into rations(name,target_group,notes,active,created_at,target_weight_kg,target_adg_kg,animal_type,ration_type,target_milk_l,milk_fat_pct,milk_protein_pct) values(?,?,?,1,?,?,?,?,?,?,?,?)',(name,(f.get('target_group') or ('Sağmal' if rtype=='Süt' else 'Besi')).strip(),(f.get('notes') or '').strip(),datetime.now().isoformat(timespec='seconds'),float(f.get('target_weight_kg') or (650 if rtype=='Süt' else 450)),float(f.get('target_adg_kg') or 1.3),(f.get('animal_type') or ('Sağmal İnek' if rtype=='Süt' else 'Besi Erkek')).strip(),rtype,float(f.get('target_milk_l') or 25),3.8,3.2));rid=cur.lastrowid
            except sqlite3.IntegrityError:return self.redirect('/rations','Bu rasyon adı zaten kayıtlı.')
            audit(username,'Rasyon oluşturdu',name,self.client_ip());return self.redirect('/rations?id='+str(rid),'Rasyon oluşturuldu. Şimdi yemleri ekleyin.')
        if path=='/ration/target':
            try:
                rid=int(f.get('ration_id') or 0);rtype=(f.get('ration_type') or 'Besi').strip();w=float(f.get('target_weight_kg') or (650 if rtype=='Süt' else 450));adg=float(f.get('target_adg_kg') or 1.3);milk=float(f.get('target_milk_l') or 25);fat=float(f.get('milk_fat_pct') or 3.8);mprot=float(f.get('milk_protein_pct') or 3.2)
            except:return self.redirect('/rations','Hedef bilgileri geçersiz.')
            if rid<=0 or not (150<=w<=900):return self.redirect('/rations?id='+str(rid),'Canlı ağırlık aralık dışında.')
            if rtype=='Süt':
                if not (0<=milk<=70):return self.redirect('/rations?id='+str(rid),'Hedef süt miktarı aralık dışında.')
                with db() as c:c.execute('update rations set ration_type=?,target_weight_kg=?,target_milk_l=?,milk_fat_pct=?,milk_protein_pct=?,animal_type=? where id=?',('Süt',w,milk,fat,mprot,'Sağmal İnek',rid))
                return self.redirect('/rations?id='+str(rid),'Süt rasyonu hedefi güncellendi.')
            if not (0.2<=adg<=2.2):return self.redirect('/rations?id='+str(rid),'Hedef artış aralık dışında.')
            with db() as c:c.execute('update rations set ration_type=?,target_weight_kg=?,target_adg_kg=?,animal_type=? where id=?',('Besi',w,adg,(f.get('animal_type') or 'Besi Erkek').strip(),rid))
            return self.redirect('/rations?id='+str(rid),'Besi rasyonu hedefi güncellendi.')
        if path=='/ration/delete':
            try:rid=int(f.get('ration_id') or 0)
            except:return self.redirect('/rations','Geçersiz rasyon.')
            if rid<=0:return self.redirect('/rations','Geçersiz rasyon.')
            with db() as c:
                rr=c.execute('select name from rations where id=? and active=1',(rid,)).fetchone()
                if not rr:return self.redirect('/rations','Rasyon bulunamadı.')
                active_pd=c.execute('''select p.name from paddock_rations pr join paddocks p on p.id=pr.paddock_id where pr.ration_id=? and pr.active=1 and (pr.end_date is null or pr.end_date='' or pr.end_date>=?) order by p.name''',(rid,date.today().isoformat())).fetchall()
                if active_pd:return self.redirect('/rations','Bu rasyon aktif olarak '+', '.join(x['name'] for x in active_pd)+' padokunda kullanılıyor. Önce padok atamasını kaldırın.')
                hist=c.execute('select 1 from paddock_rations where ration_id=? limit 1',(rid,)).fetchone()
                if hist:
                    c.execute('update rations set active=0 where id=?',(rid,))
                    audit(username,'Rasyonu arşivledi',rr['name'],self.client_ip())
                    return self.redirect('/rations','Rasyon geçmiş padok kayıtları korunarak arşivlendi.')
                c.execute('delete from ration_item_history where ration_id=?',(rid,))
                c.execute('delete from ration_items where ration_id=?',(rid,))
                c.execute('delete from rations where id=?',(rid,))
            audit(username,'Rasyonu sildi',rr['name'],self.client_ip());return self.redirect('/rations','Rasyon silindi.')
        if path=='/ration/edit':
            try:rid=int(f.get('ration_id') or 0)
            except:return self.redirect('/rations','Geçersiz rasyon.')
            name=(f.get('name') or '').strip()
            if not name:return self.redirect('/rations?id='+str(rid),'Rasyon adı zorunludur.')
            with db() as c:c.execute('update rations set name=?,target_group=?,notes=? where id=?',(name,(f.get('target_group') or 'Besi').strip(),(f.get('notes') or '').strip(),rid))
            return self.redirect('/rations?id='+str(rid),'Rasyon bilgileri güncellendi.')
        if path=='/ration/items-bulk':
            try:rid=int(f.get('ration_id') or 0)
            except:return self.redirect('/rations','Geçersiz rasyon.')
            if rid<=0:return self.redirect('/rations','Geçersiz rasyon.')
            with db() as c:
                valid={int(r['id']) for r in c.execute('select id from ration_items where ration_id=?',(rid,)).fetchall()}
                for key,val in f.items():
                    if not key.startswith('item_'):continue
                    try:iid=int(key[5:]);kg=max(0.0,float(str(val).replace(',','.')))
                    except:continue
                    if iid not in valid:continue
                    item=c.execute('select feed_id from ration_items where id=? and ration_id=?',(iid,rid)).fetchone()
                    if not item:continue
                    if kg<0.001:c.execute('delete from ration_items where id=? and ration_id=?',(iid,rid))
                    else:c.execute('update ration_items set kg_per_head_day=? where id=? and ration_id=?',(round(kg,3),iid,rid))
                    record_ration_item_history(c,rid,item['feed_id'],0 if kg<0.001 else round(kg,3),notes='Çalışma masası')
            return self.redirect('/rations?id='+str(rid),'Rasyon miktarları kaydedildi.')
        if path=='/ration/item-adjust':
            try:rid=int(f.get('ration_id') or 0);iid=int(f.get('item_id') or 0);delta=float(f.get('delta') or 0)
            except:return self.redirect('/rations','Geçersiz rasyon kalemi.')
            with db() as c:
                row=c.execute('select kg_per_head_day from ration_items where id=? and ration_id=?',(iid,rid)).fetchone()
                if not row:return self.redirect('/rations?id='+str(rid),'Yem kalemi bulunamadı.')
                new=max(0,float(row['kg_per_head_day'] or 0)+delta)
                item=c.execute('select feed_id from ration_items where id=?',(iid,)).fetchone()
                if new<0.001:c.execute('delete from ration_items where id=?',(iid,))
                else:c.execute('update ration_items set kg_per_head_day=? where id=?',(round(new,3),iid))
                if item:record_ration_item_history(c,rid,item['feed_id'],0 if new<0.001 else round(new,3),notes='Hızlı miktar ayarı')
            return self.redirect('/rations?id='+str(rid),'Rasyon miktarı güncellendi.')
        if path=='/ration/apply-combo':
            try:
                rid=int(f.get('ration_id') or 0);rfid=int(f.get('red_feed_id') or 0);rd=float(f.get('red_delta') or 0);afid=int(f.get('add_feed_id') or 0);ad=float(f.get('add_delta') or 0)
            except:return self.redirect('/rations','Kombine öneri uygulanamadı.')
            if rid<=0 or rfid<=0 or afid<=0 or rd>=0 or ad<=0:return self.redirect('/rations?id='+str(rid),'Kombine öneri geçersiz.')
            with db() as c:
                row=c.execute('select id,kg_per_head_day from ration_items where ration_id=? and feed_id=?',(rid,rfid)).fetchone()
                if not row:return self.redirect('/rations?id='+str(rid),'Azaltılacak yem rasyonda bulunamadı.')
                newkg=max(0.0,float(row['kg_per_head_day'] or 0)+rd)
                if newkg<0.001:c.execute('delete from ration_items where id=?',(row['id'],))
                else:c.execute('update ration_items set kg_per_head_day=? where id=?',(round(newkg,3),row['id']))
                record_ration_item_history(c,rid,rfid,0 if newkg<0.001 else round(newkg,3),notes='Kombine akıllı dengeleme - azalt')
                addrow=c.execute('select id,kg_per_head_day from ration_items where ration_id=? and feed_id=?',(rid,afid)).fetchone()
                if addrow:
                    addkg=max(0.0,float(addrow['kg_per_head_day'] or 0)+ad);c.execute('update ration_items set kg_per_head_day=? where id=?',(round(addkg,3),addrow['id']))
                else:
                    addkg=ad;c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)',(rid,afid,round(addkg,3)))
                record_ration_item_history(c,rid,afid,round(addkg,3),notes='Kombine akıllı dengeleme - ekle')
            return self.redirect('/rations?id='+str(rid)+'#smart-balance','Kombine dengelemedeki iki değişiklik birlikte uygulandı.')
        if path=='/ration/apply-suggestion':
            try:rid=int(f.get('ration_id') or 0);fid=int(f.get('feed_id') or 0);delta=float(f.get('delta') or 0)
            except:return self.redirect('/rations','Öneri uygulanamadı.')
            if rid<=0 or fid<=0 or abs(delta)<0.001:return self.redirect('/rations?id='+str(rid),'Öneri miktarı geçersiz.')
            with db() as c:
                row=c.execute('select id,kg_per_head_day from ration_items where ration_id=? and feed_id=?',(rid,fid)).fetchone()
                if row:
                    newkg=max(0.0,float(row['kg_per_head_day'] or 0)+delta)
                    if newkg<0.001:c.execute('delete from ration_items where id=?',(row['id'],))
                    else:c.execute('update ration_items set kg_per_head_day=? where id=?',(round(newkg,3),row['id']))
                    record_ration_item_history(c,rid,fid,0 if newkg<0.001 else round(newkg,3),notes='Akıllı dengeleme önerisi')
                elif delta>0:
                    c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)',(rid,fid,round(delta,3)))
                    record_ration_item_history(c,rid,fid,round(delta,3),notes='Akıllı dengeleme önerisi')
                else:return self.redirect('/rations?id='+str(rid),'Azaltılacak yem rasyonda bulunamadı.')
            return self.redirect('/rations?id='+str(rid)+'#smart-balance','Simülasyondaki değişiklik rasyona uygulandı.')
        if path=='/ration/item':
            try:rid=int(f.get('ration_id') or 0);fid=int(f.get('feed_id') or 0);kg=float(f.get('kg_per_head_day') or 0)
            except:return self.redirect('/rations','Rasyon kalemi geçersiz.')
            if rid<=0 or fid<=0 or kg<=0:return self.redirect('/rations?id='+str(rid),'Rasyon kalemi geçersiz.')
            with db() as c:
                c.execute('''insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?) on conflict(ration_id,feed_id) do update set kg_per_head_day=excluded.kg_per_head_day''',(rid,fid,kg))
                record_ration_item_history(c,rid,fid,kg,notes='Rasyona yem ekle/güncelle')
            keep=(f.get('keep_feed_add_open') or '').strip()=='1'
            return self.redirect('/rations?id='+str(rid)+('&feedadd=1#ration-workbench' if keep else '#ration-workbench'),'Rasyon kalemi güncellendi.')
        if path=='/ration/item-delete':
            try:iid=int(f.get('id') or 0);rid=int(f.get('ration_id') or 0)
            except:return self.redirect('/rations','Geçersiz kayıt.')
            with db() as c:
                item=c.execute('select feed_id from ration_items where id=? and ration_id=?',(iid,rid)).fetchone()
                c.execute('delete from ration_items where id=?',(iid,))
                if item:record_ration_item_history(c,rid,item['feed_id'],0,notes='Yem rasyondan çıkarıldı')
            return self.redirect('/rations?id='+str(rid),'Yem rasyondan çıkarıldı.')
        if path=='/ration/assign':
            try:pid=int(f.get('paddock_id') or 0);rid=int(f.get('ration_id') or 0)
            except:return self.redirect('/paddocks','Padok ve rasyon seçin.')
            if pid<=0 or rid<=0:return self.redirect('/paddocks','Padok ve rasyon seçin.')
            start=(f.get('start_date') or date.today().isoformat()).strip()
            with db() as c:
                if not c.execute('select id from paddocks where id=? and active=1',(pid,)).fetchone():return self.redirect('/paddocks','Padok bulunamadı.')
                if not c.execute('select id from rations where id=? and active=1',(rid,)).fetchone():return self.redirect('/paddocks','Rasyon bulunamadı.')
                c.execute("update paddock_rations set active=0,end_date=? where paddock_id=? and active=1 and (end_date is null or end_date='')",((date.fromisoformat(start)-timedelta(days=1)).isoformat(),pid))
                c.execute('insert into paddock_rations(paddock_id,ration_id,start_date,end_date,active,notes) values(?,?,?,NULL,1,?)',(pid,rid,start,(f.get('notes') or '').strip()))
            audit(username,'Padoka rasyon atadı',f'Padok {pid} / Rasyon {rid}',self.client_ip());return self.redirect('/paddocks','Rasyon padoka atandı.')
        if path=='/smtp-settings':
            if not self.require_admin():return
            action=(f.get('action') or 'save').strip()
            if action=='test':
                target=(f.get('test_email') or '').strip()
                if not target:return self.redirect('/smtp-settings','Test e-posta adresi girin.')
                try:send_reset_email(target,'SMTP Test','123456');return self.redirect('/smtp-settings','✅ Test e-postası gönderildi.')
                except Exception as exc:return self.redirect('/smtp-settings','Test e-postası gönderilemedi: '+str(exc))
            setting_set('smtp_host',(f.get('smtp_host') or '').strip());setting_set('smtp_port',(f.get('smtp_port') or '587').strip());setting_set('smtp_security',(f.get('smtp_security') or 'starttls').strip());setting_set('smtp_username',(f.get('smtp_username') or '').strip());setting_set('smtp_sender',(f.get('smtp_sender') or '').strip())
            if (f.get('smtp_password') or '').strip():setting_set('smtp_password',f.get('smtp_password').strip())
            audit(username,'SMTP ayarlarını güncelledi','',self.client_ip());return self.redirect('/smtp-settings','E-posta ayarları kaydedildi.')

        if path=='/dashboard-layout':
            try: slot=int(f.get('slot','-1'))
            except Exception: slot=-1
            valid={x[0] for x in DASHBOARD_CARD_OPTIONS}
            card_key=(f.get('card_key') or '').strip()
            if slot<0 or slot>=8:return self.redirect('/?edit=1','Geçersiz Dashboard yuvası.')
            if card_key and card_key not in valid:return self.redirect('/?edit=1','Geçersiz Dashboard kartı.')
            layout=dashboard_layout(username)
            layout[slot]=card_key
            with db() as c:
                c.execute("insert into settings(setting_key,setting_value) values(?,?) on conflict(setting_key) do update set setting_value=excluded.setting_value",('dashboard_layout_'+username,','.join(layout)))
            return self.redirect('/?edit=1','Dashboard kartı güncellendi.')
        if path=='/farm-profile':
            if not self.require_admin():return
            text_keys=('farm_name','owner_name','phone','email','province','district','address','business_no','tax_or_tc','vet_name','vet_phone','vet_email','notes')
            with db() as c:
                for key in text_keys:
                    val=(f.get(key,'') or '').strip()
                    c.execute("insert into settings(setting_key,setting_value) values(?,?) on conflict(setting_key) do update set setting_value=excluded.setting_value",(key,val))
                current=c.execute("select setting_value from settings where setting_key='farm_logo'").fetchone()
                current_logo=current['setting_value'] if current else ''
                if f.get('remove_logo')=='1':
                    if current_logo.startswith('/uploads/'):
                        try:(UPLOADS/os.path.basename(current_logo)).unlink(missing_ok=True)
                        except Exception:pass
                    c.execute("insert into settings(setting_key,setting_value) values('farm_logo','') on conflict(setting_key) do update set setting_value=''")
                    current_logo=''
                upload=f.get('farm_logo_file')
                if isinstance(upload,dict) and upload.get('filename') and upload.get('content'):
                    content=upload['content']
                    if len(content)>5*1024*1024:return self.redirect('/farm-profile','Logo dosyası 5 MB sınırını aşıyor.')
                    ext=Path(upload['filename']).suffix.lower()
                    if ext not in ('.jpg','.jpeg','.png','.webp'):return self.redirect('/farm-profile','Logo yalnızca JPG, PNG veya WebP olabilir.')
                    UPLOADS.mkdir(parents=True,exist_ok=True)
                    if current_logo.startswith('/uploads/'):
                        try:(UPLOADS/os.path.basename(current_logo)).unlink(missing_ok=True)
                        except Exception:pass
                    filename='farm_logo'+('.jpg' if ext=='.jpeg' else ext)
                    (UPLOADS/filename).write_bytes(content)
                    logo_url='/uploads/'+filename
                    c.execute("insert into settings(setting_key,setting_value) values('farm_logo',?) on conflict(setting_key) do update set setting_value=excluded.setting_value",(logo_url,))
            audit(username,'Çiftlik profilini güncelledi',(f.get('farm_name') or 'ÇiftlikPro').strip(),self.client_ip())
            return self.redirect('/farm-profile','Çiftlik profili başarıyla kaydedildi.')
        if path=='/password-change':
            np=f.get('new_password','')
            if len(np)<8:return self.redirect('/password-change','Yeni şifre en az 8 karakter olmalıdır.')
            if np!=f.get('new_password_confirm',''):return self.redirect('/password-change','Yeni şifreler eşleşmiyor.')
            with db() as c:r=c.execute('select * from users where username=?',(username,)).fetchone()
            if not r or not password_verify(f.get('current_password',''),r['password']):return self.redirect('/password-change','Mevcut şifre hatalı.')
            with db() as c:c.execute('update users set password=?,password_changed_at=? where id=?',(password_hash(np),datetime.now().strftime('%Y-%m-%d %H:%M:%S'),r['id']))
            audit(username,'Şifresini değiştirdi','',self.client_ip());return self.redirect('/password-change','Şifreniz başarıyla değiştirildi.')
        if path=='/users/create':
            if not self.require_admin():return
            uname=(f.get('username') or '').strip();password=f.get('password','');role=f.get('role','personel')
            if len(password)<8:return self.redirect('/users','Şifre en az 8 karakter olmalıdır.')
            try:
                with db() as c:c.execute('insert into users(username,password,role,full_name,recovery_email,active,password_changed_at) values(?,?,?,?,?,1,?)',(uname,password_hash(password),role,f.get('full_name',''),(f.get('recovery_email') or '').strip(),datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except sqlite3.IntegrityError:return self.redirect('/users','Bu kullanıcı adı zaten kullanılıyor.')
            audit(username,'Kullanıcı oluşturdu',uname+' · '+role,self.client_ip());return self.redirect('/users','Kullanıcı oluşturuldu.')
        if path=='/users/update':
            if not self.require_admin():return
            uid=int(f.get('id') or 0);role=f.get('role','personel');active=1 if f.get('active')=='1' else 0
            with db() as c:r=c.execute('select * from users where id=?',(uid,)).fetchone()
            if not r:return self.redirect('/users','Kullanıcı bulunamadı.')
            if r['role']=='admin' and r['active'] and (role!='admin' or not active) and active_admin_count()<=1:return self.redirect('/users/edit?id='+str(uid),'Son aktif yönetici değiştirilemez.')
            with db() as c:
                c.execute('update users set full_name=?,recovery_email=?,role=?,active=? where id=?',(f.get('full_name',''),(f.get('recovery_email') or '').strip(),role,active,uid))
                if f.get('new_password'):
                    if len(f['new_password'])<8:return self.redirect('/users/edit?id='+str(uid),'Yeni şifre en az 8 karakter olmalıdır.')
                    c.execute('update users set password=?,password_changed_at=? where id=?',(password_hash(f['new_password']),datetime.now().strftime('%Y-%m-%d %H:%M:%S'),uid))
            audit(username,'Kullanıcı güncelledi',r['username'],self.client_ip());return self.redirect('/users','Kullanıcı güncellendi.')
        if path=='/backup/restore':
            if not self.require_admin():return
            upload=f.get('backup_file')
            if f.get('confirm_restore')!='yes':return self.redirect('/backups','Geri yükleme onayı verilmedi.')
            if not upload or not isinstance(upload,dict):return self.redirect('/backups','ZIP dosyası seçilmedi.')
            temp_path=BACKUPS/('.incoming_'+secrets.token_hex(8)+'.zip');temp_path.write_bytes(upload.get('content',b''))
            try:
                emergency,manifest=restore_backup_zip(temp_path);audit(username,'Yedek geri yükledi',upload.get('filename','')+' · '+emergency,self.client_ip());SESSIONS.clear();return self.redirect('/login','Yedek geri yüklendi. Yeniden giriş yapın.')
            except Exception as exc:return self.redirect('/backups','Geri yükleme başarısız: '+str(exc))
            finally:
                if temp_path.exists():temp_path.unlink()

        if path=='/animal-delete':
            if not self.require_admin():return
            aid=(f.get('id') or '').strip()
            try:
                with db() as c:
                    rec=c.execute('select tag,gender from animals where id=?',(aid,)).fetchone()
                    if not rec:return self.redirect('/','Hayvan kaydı bulunamadı.')
                    photo_rows=c.execute('select filename from animal_photos where animal_id=?',(aid,)).fetchall()
                    for table in ('inseminations','health','finance','weights','milk','animal_photos'):
                        c.execute(f'delete from {table} where animal_id=?',(aid,))
                    c.execute('delete from calves where mother_id=?',(aid,))
                    c.execute('delete from animals where id=?',(aid,))
                for pr in photo_rows:
                    fp=UPLOADS/pr['filename']
                    if fp.exists():
                        try:fp.unlink()
                        except Exception:pass
                audit(username,'Hayvan sildi',rec['tag'],self.client_ip())
                return self.redirect('/males' if rec['gender']=='Erkek' else '/animals','Hayvan ve bağlı kayıtları silindi.')
            except Exception as exc:return self.redirect('/','Silme hatası: '+str(exc))
        if path=='/calf-delete':
            if not self.require_admin():return
            cid=(f.get('id') or '').strip()
            try:
                with db() as c:
                    rec=c.execute('select tag from calves where id=?',(cid,)).fetchone()
                    if not rec:return self.redirect('/calves','Buzağı kaydı bulunamadı.')
                    c.execute('delete from health where calf_id=?',(cid,))
                    c.execute('delete from calf_weights where calf_id=?',(cid,))
                    c.execute('delete from calf_photos where calf_id=?',(cid,))
                    c.execute('delete from calves where id=?',(cid,))
                audit(username,'Buzağı sildi',rec['tag'],self.client_ip())
                return self.redirect('/calves','Buzağı kaydı silindi.')
            except Exception as exc:return self.redirect('/calves','Silme hatası: '+str(exc))

        if path=='/animal-edit':
            aid=(f.get('id') or '').strip()
            try:
                with db() as c:
                    rec=c.execute('select * from animals where id=?',(aid,)).fetchone()
                    if not rec:return self.redirect('/','Hayvan kaydı bulunamadı.')
                    tag=(f.get('tag') or '').strip()
                    duplicate=c.execute('select id from animals where tag=? and id<>?',(tag,aid)).fetchone()
                    calf_duplicate=c.execute('select id from calves where tag=?',(tag,)).fetchone()
                    if duplicate or calf_duplicate:return self.redirect('/animal-edit?id='+aid,'Bu küpe numarası başka bir kayıtta kullanılıyor.')
                    photo_url=f.get('photo_url','')
                    upload=f.get('photo_file')
                    if upload and isinstance(upload,dict) and upload.get('content'):
                        ext=Path(upload['filename']).suffix.lower()
                        if ext not in ('.jpg','.jpeg','.png','.webp','.gif'):return self.redirect('/animal-edit?id='+aid,'Desteklenmeyen fotoğraf biçimi.')
                        if len(upload['content'])>10*1024*1024:return self.redirect('/animal-edit?id='+aid,'Fotoğraf 10 MB sınırını aşıyor.')
                        name=save_optimized_upload('animal_edit',upload)
                        photo_url='/uploads/'+name
                    gender=f.get('gender') if f.get('gender') in ('Dişi','Erkek') else rec['gender']
                    c.execute('update animals set tag=?,nickname=?,gender=?,breed=?,birth_date=?,notes=?,paddock=?,photo_url=?,sold_price=?,status=?,purchase_date=?,purchase_price=?,purchase_weight=?,daily_feed_cost=?,daily_care_cost=?,target_sale_price=? where id=?',
                              (tag,f.get('nickname',''),gender,f.get('breed',''),f.get('birth_date',''),f.get('notes',''),f.get('paddock',''),photo_url,float(f.get('sold_price') or 0),f.get('status') or 'Aktif',f.get('purchase_date',''),float(f.get('purchase_price') or 0),float(f.get('purchase_weight') or 0),float(f.get('daily_feed_cost') or 0),float(f.get('daily_care_cost') or 0),float(f.get('target_sale_price') or 0),aid))
                audit(username,'Hayvan düzenledi',tag,self.client_ip())
                return self.redirect('/animals' if gender=='Dişi' else '/males','Hayvan başarıyla güncellendi.')
            except sqlite3.IntegrityError:
                return self.redirect('/animal-edit?id='+aid,'Bu küpe numarası zaten kullanılıyor.')
            except Exception as exc:
                return self.redirect('/animal-edit?id='+aid,'Güncelleme hatası: '+str(exc))
        if path=='/calf-edit':
            cid=(f.get('id') or '').strip()
            try:
                with db() as c:
                    rec=c.execute('select * from calves where id=?',(cid,)).fetchone()
                    if not rec:return self.redirect('/calves','Buzağı kaydı bulunamadı.')
                    mother=c.execute("select id from animals where id=? and gender='Dişi' and coalesce(status,'Aktif')='Aktif'",(f.get('mother_id'),)).fetchone()
                    if not mother:return self.redirect('/calf-edit?id='+cid,'Anne olarak aktif bir dişi hayvan seçilmelidir.')
                    tag=(f.get('tag') or '').strip()
                    if c.execute('select id from calves where tag=? and id<>?',(tag,cid)).fetchone() or c.execute('select id from animals where tag=?',(tag,)).fetchone():return self.redirect('/calf-edit?id='+cid,'Bu küpe numarası başka bir kayıtta kullanılıyor.')
                    photo_url=f.get('photo_url') or rec['photo_url'] or '';upload=f.get('photo_file')
                    if upload and isinstance(upload,dict) and upload.get('content'):
                        ext=Path(upload['filename']).suffix.lower()
                        if ext not in ('.jpg','.jpeg','.png','.webp','.gif'):return self.redirect('/calf-edit?id='+cid,'Desteklenmeyen fotoğraf biçimi.')
                        if len(upload['content'])>10*1024*1024:return self.redirect('/calf-edit?id='+cid,'Fotoğraf 10 MB sınırını aşıyor.')
                        name=save_optimized_upload(f'calf_{cid}',upload);photo_url='/uploads/'+name
                        c.execute('insert into calf_photos(calf_id,filename,created_at,caption) values(?,?,?,?)',(cid,name,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Profil fotoğrafı'))
                    c.execute('update calves set tag=?,nickname=?,mother_id=?,father_tag=?,birth_date=?,gender=?,breed=?,paddock=?,photo_url=?,purchase_date=?,purchase_price=?,purchase_payment_method=?,notes=? where id=?',
                        (tag,f.get('nickname',''),f.get('mother_id'),f.get('father_tag',''),f.get('birth_date',''),f.get('gender','Dişi'),f.get('breed',''),f.get('paddock',''),photo_url,f.get('purchase_date',''),float(f.get('purchase_price') or 0),f.get('purchase_payment_method') or 'Nakit',f.get('notes',''),cid))
                audit(username,'Buzağı düzenledi',tag,self.client_ip());return self.redirect('/calf?id='+cid,'Buzağı başarıyla güncellendi.')
            except sqlite3.IntegrityError:return self.redirect('/calf-edit?id='+cid,'Bu küpe numarası zaten kullanılıyor.')
            except Exception as exc:return self.redirect('/calf-edit?id='+cid,'Güncelleme hatası: '+str(exc))
        if path=='/animal-add':
            kind=(f.get('record_type') or '').strip();tag=(f.get('tag') or '').strip()
            if not tag:return self.redirect('/animal-add','Küpe numarası zorunludur.')
            try:
                with db() as c:
                    if c.execute('select 1 from animals where tag=?',(tag,)).fetchone() or c.execute('select 1 from calves where tag=?',(tag,)).fetchone():return self.redirect('/animal-add','Bu küpe numarası zaten kayıtlı.')
                    if kind in ('Dişi','Erkek'):
                        photo_url='';upload=f.get('photo_file')
                        if upload and isinstance(upload,dict) and upload.get('content'):
                            ext=Path(upload['filename']).suffix.lower()
                            if ext not in ('.jpg','.jpeg','.png','.webp','.gif'):return self.redirect('/animal-add','Desteklenmeyen fotoğraf biçimi.')
                            if len(upload['content'])>10*1024*1024:return self.redirect('/animal-add','Fotoğraf 10 MB sınırını aşıyor.')
                            name=save_optimized_upload('animal_new',upload);photo_url='/uploads/'+name
                        cur=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes,paddock,photo_url,sold_price,status,purchase_date,purchase_price,purchase_weight,daily_feed_cost,daily_care_cost,target_sale_price) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(tag,f.get('nickname',''),kind,f.get('breed',''),f.get('birth_date',''),f.get('notes',''),f.get('paddock',''),photo_url,0,'Aktif',f.get('purchase_date',''),float(f.get('purchase_price') or 0),float(f.get('purchase_weight') or 0) if kind=='Erkek' else 0,float(f.get('daily_feed_cost') or 0) if kind=='Erkek' else 0,float(f.get('daily_care_cost') or 0) if kind=='Erkek' else 0,float(f.get('target_sale_price') or 0) if kind=='Erkek' else 0))
                        aid=cur.lastrowid
                        if photo_url:c.execute('insert into animal_photos(animal_id,filename,created_at,caption) values(?,?,?,?)',(aid,photo_url.split('/uploads/',1)[1],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Profil fotoğrafı'))
                        if kind=='Dişi' and (f.get('entry_pregnancy_status') or '')=='Gebe':
                            mode=(f.get('pregnancy_info_mode') or 'date').strip()
                            entry_date=(f.get('pregnancy_entry_date') or date.today().isoformat()).strip()
                            try:ref_day=date.fromisoformat(entry_date)
                            except:ref_day=date.today();entry_date=ref_day.isoformat()
                            age_months=0.0
                            if mode=='date':
                                ins_date=(f.get('known_insemination_date') or '').strip()
                                if not ins_date:return self.redirect('/animal-add','Gebe hayvan için son tohumlama tarihini girin.')
                                try:ins_day=date.fromisoformat(ins_date)
                                except:return self.redirect('/animal-add','Tohumlama tarihi geçersiz.')
                                due=(ins_day+timedelta(days=280)).isoformat()
                                result='Gebe (Satın Alındığında · Tohumlama Tarihi Biliniyor)'
                                source='Satın Alındığında Gebe · Tohumlama Tarihi'
                            else:
                                try:age_months=float(f.get('pregnancy_age_months') or 0)
                                except:age_months=0
                                if age_months<=0 or age_months>9:return self.redirect('/animal-add','Gebelik yaşını 1-9 ay arasında girin.')
                                elapsed=round(age_months*(280/9))
                                ins_day=ref_day-timedelta(days=elapsed);ins_date=ins_day.isoformat()
                                due=(ins_day+timedelta(days=280)).isoformat()
                                result='Gebe (Satın Alındığında · Gebelik Yaşından Tahmini)'
                                source='Satın Alındığında Gebe · Yaklaşık'
                            c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',(aid,1,ins_date,result,due))
                            c.execute('update animals set pregnancy_source=?,pregnancy_age_months_at_entry=?,pregnancy_entry_date=? where id=?',(source,age_months,entry_date,aid))

                        purchase_price=float(f.get('purchase_price') or 0)
                        if purchase_price>0:
                            purchase_date=(f.get('purchase_date') or date.today().isoformat()).strip()
                            payment=(f.get('purchase_payment_method') or 'Nakit').strip()
                            desc=f'Otomatik hayvan alımı · {tag}'
                            c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',
                                      (purchase_date,'Gider','Hayvan Alımı',purchase_price,desc,payment,aid,datetime.now().isoformat(),''))
                            audit(username,'Hayvan alımı finansa otomatik işlendi',f'{tag} · {money(purchase_price)} · {payment}',self.client_ip())

                        return self.redirect('/animals' if kind=='Dişi' else '/males',kind+' hayvan başarıyla kaydedildi.'+(' Alış bedeli Finans > Hayvan Alımı giderine otomatik işlendi.' if purchase_price>0 else ''))
                    if kind=='Buzağı':
                        mt=(f.get('mother_tag') or '').strip();bd=(f.get('birth_date') or '').strip()
                        if not mt:return self.redirect('/animal-add','Buzağı kaydı için anne küpesi zorunludur.')
                        if not bd:return self.redirect('/animal-add','Buzağı kaydı için doğum tarihi zorunludur.')
                        mother=c.execute("select id from animals where tag=? and gender='Dişi' and coalesce(status,'Aktif')='Aktif'",(mt,)).fetchone()
                        if not mother:return self.redirect('/animal-add','Anne küpesi aktif dişi hayvanlarda bulunamadı.')
                        c.execute('insert into calves(tag,mother_id,father_tag,birth_date,gender,notes) values(?,?,?,?,?,?)',(tag,mother['id'],f.get('father_tag',''),bd,f.get('calf_gender','Dişi'),f.get('notes','')))
                        return self.redirect('/calves','Buzağı başarıyla kaydedildi.')
                return self.redirect('/animal-add','Geçersiz kayıt türü.')
            except sqlite3.IntegrityError:return self.redirect('/animal-add','Bu küpe numarası zaten kayıtlı.')
            except Exception as exc:return self.redirect('/animal-add','Kayıt hatası: '+str(exc))

        if path=='/backup/settings':
            if not self.require_admin():return
            raw=(f.get('backup_directory') or '').strip()
            if not raw:
                set_setting_value('backup_directory','')
                return self.redirect('/backups','Yedek klasörü varsayılan konuma döndürüldü.')
            try:
                target=Path(os.path.expandvars(os.path.expanduser(raw)))
                target.mkdir(parents=True,exist_ok=True)
                probe=target/'.ciftlikpro_write_test.tmp'
                probe.write_text('ok',encoding='utf-8');probe.unlink()
            except Exception as exc:
                return self.redirect('/backups','Yedek klasörü kullanılamıyor: '+str(exc))
            set_setting_value('backup_directory',str(target))
            audit(username,'Yedek klasörünü değiştirdi',str(target),self.client_ip())
            return self.redirect('/backups','Yedek klasörü kaydedildi ve yazma testi başarılı.')
        if path=='/backup/restore-existing':
            if not self.require_admin():return
            name=os.path.basename((f.get('file') or '').strip())
            fp=configured_backup_dir()/name
            if not fp.exists():return self.redirect('/backups','Yedek dosyası bulunamadı.')
            try:
                restore_backup_zip(fp)
                audit(username,'Klasörden yedek geri yükledi',name,self.client_ip())
                return self.redirect('/backups','Yedek başarıyla geri yüklendi.')
            except Exception as exc:
                return self.redirect('/backups','Geri yükleme hatası: '+str(exc))
        if path=='/photos/optimize-existing':
            if not self.require_admin():return
            try:
                safety=create_backup('FotoOptimizasyonOncesi')
                result=optimize_existing_uploads()
                audit(username,'Fotoğrafları optimize etti',f"{result['count']} dosya · {format_bytes(result['saved'])} kazanım",self.client_ip())
                return self.redirect('/backups',f"Optimizasyon tamamlandı: {result['count']} fotoğraf küçültüldü, {format_bytes(result['saved'])} alan kazanıldı. Güvenlik yedeği: {safety}")
            except Exception as exc:
                return self.redirect('/backups','Fotoğraf optimizasyonu başarısız: '+str(exc))
        if path=='/data/import':
            try:
                upload=f.get('json_file')
                if not upload or not isinstance(upload,dict):return self.redirect('/data','JSON dosyası seçilmedi.')
                payload=json.loads(upload['content'].decode('utf-8-sig'))
                create_backup('import_oncesi')
                stats=import_payload(payload,f.get('strategy','skip'))
                summary=f"Aktarım tamamlandı: {stats['animals']} yeni hayvan, {stats['animals_updated']} güncellenen, {stats['inseminations']} tohumlama, {stats['calves']} buzağı, {stats['finance']} finans, {stats['skipped']} atlanan"
                if stats['errors']:summary+=f", {len(stats['errors'])} hata"
                return self.redirect('/data',summary)
            except Exception as e:return self.redirect('/data','İçe aktarma hatası: '+str(e))
        if path=='/calf/photo':
            cid=(f.get('calf_id') or '').strip()
            try:
                upload=f.get('photo_file')
                if not upload or not isinstance(upload,dict):return self.redirect('/calf?id='+cid,'Fotoğraf seçilmedi.')
                ext=Path(upload['filename']).suffix.lower()
                if ext not in ('.jpg','.jpeg','.png','.webp','.gif'):return self.redirect('/calf?id='+cid,'Desteklenmeyen fotoğraf biçimi.')
                if len(upload['content'])>10*1024*1024:return self.redirect('/calf?id='+cid,'Fotoğraf 10 MB sınırını aşıyor.')
                name=save_optimized_upload(f'calf_{cid}',upload)
                with db() as c:
                    if not c.execute('select 1 from calves where id=?',(cid,)).fetchone():return self.redirect('/calves','Buzağı bulunamadı.')
                    c.execute('insert into calf_photos(calf_id,filename,created_at,caption) values(?,?,?,?)',(cid,name,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),f.get('caption','')))
                    c.execute('update calves set photo_url=? where id=?',('/uploads/'+name,cid))
                return self.redirect('/calf?id='+cid,'Fotoğraf başarıyla yüklendi.')
            except Exception as e:return self.redirect('/calf?id='+cid,'Fotoğraf yükleme hatası: '+str(e))
        if path=='/calf/weight':
            cid=(f.get('calf_id') or '').strip()
            try:
                weight=float(f.get('weight') or 0)
                if weight<=0:return self.redirect('/calf?id='+cid,'Kilo sıfırdan büyük olmalıdır.')
                with db() as c:
                    if not c.execute('select 1 from calves where id=?',(cid,)).fetchone():return self.redirect('/calves','Buzağı bulunamadı.')
                    existing=c.execute('select id from calf_weights where calf_id=? and measure_date=?',(cid,f.get('measure_date'))).fetchone()
                    if existing:c.execute('update calf_weights set weight=?,notes=? where id=?',(weight,f.get('notes',''),existing['id']))
                    else:c.execute('insert into calf_weights(calf_id,measure_date,weight,notes) values(?,?,?,?)',(cid,f.get('measure_date'),weight,f.get('notes','')))
                return self.redirect('/calf?id='+cid,'Buzağı tartımı kaydedildi.')
            except Exception as e:return self.redirect('/calf?id='+cid,'Tartım kayıt hatası: '+str(e))
        if path=='/animal/photo':
            try:
                upload=f.get('photo_file'); aid=f.get('animal_id','')
                if not upload or not isinstance(upload,dict): return self.redirect('/animal?id='+aid,'Fotoğraf seçilmedi.')
                ext=Path(upload['filename']).suffix.lower()
                if ext not in ('.jpg','.jpeg','.png','.webp','.gif'): return self.redirect('/animal?id='+aid,'Desteklenmeyen fotoğraf biçimi.')
                if len(upload['content'])>10*1024*1024: return self.redirect('/animal?id='+aid,'Fotoğraf 10 MB sınırını aşıyor.')
                name=save_optimized_upload(f'animal_{aid}',upload)
                with db() as c:
                    c.execute('insert into animal_photos(animal_id,filename,created_at,caption) values(?,?,?,?)',(aid,name,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),f.get('caption','')))
                    c.execute('update animals set photo_url=? where id=?',('/uploads/'+name,aid))
                return self.redirect('/animal?id='+aid,'Fotoğraf başarıyla yüklendi.')
            except Exception as e: return self.redirect('/animal?id='+f.get('animal_id',''),'Fotoğraf yükleme hatası: '+str(e))
        try:
            with db() as c:
                if path=='/animal/sale':
                    aid=f['animal_id']; sale_price=float(f['sale_price']); sale_date=f['sale_date']; sale_weight=float(f.get('sale_weight') or 0)
                    a=c.execute("select * from animals where id=? and gender='Erkek'",(aid,)).fetchone()
                    if not a:return self.redirect('/males','Erkek hayvan bulunamadı.')
                    if a['status']!='Aktif':return self.redirect('/animal?id='+aid,'Bu hayvan daha önce aktif sürüden çıkarılmış.')
                    days,daily,accumulated,current=animal_cost_values(a); profit=sale_price-current
                    desc=(f.get('description') or '').strip()
                    detail=f"{desc} | Satış kilosu: {sale_weight:.1f} kg | Anlık maliyet: {current:.2f} TL | Net kâr/zarar: {profit:.2f} TL"
                    c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',(sale_date,'Gelir','Hayvan Satışı',sale_price,detail,'Nakit',aid,datetime.now().isoformat(),'Satıldı'))
                    c.execute('update animals set status=?,exit_date=?,exit_reason=?,sold_price=? where id=?',('Satıldı',sale_date,'Hayvan Satışı',sale_price,aid))
                    if sale_weight>0:c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',(aid,sale_date,sale_weight,'Satış kilosu'))
                    return self.redirect('/archive/sold','Satış tamamlandı. Net kâr/zarar: '+money(profit))
                if path=='/performance-settings':
                    target=max(0.01,float(f['male_min_daily_gain'])); ratio=max(0.01,min(1.0,float(f['warning_percent'])/100.0))
                    c.execute("insert or replace into settings(setting_key,setting_value) values('male_min_daily_gain',?)",(str(target),))
                    c.execute("insert or replace into settings(setting_key,setting_value) values('male_warning_ratio',?)",(str(ratio),))
                    return self.redirect('/performance','Besi performans eşikleri güncellendi.')
                if path=='/animal/weight':
                    aid=f['animal_id']; measure=f['measure_date']; weight=float(f['weight'])
                    if weight<=0:return self.redirect('/animal?id='+aid,'Kilo sıfırdan büyük olmalıdır.')
                    existing=c.execute('select id from weights where animal_id=? and measure_date=?',(aid,measure)).fetchone()
                    if existing:c.execute('update weights set weight=?,notes=? where id=?',(weight,f.get('notes'),existing['id']));msg='Aynı tarihteki tartım güncellendi.'
                    else:c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',(aid,measure,weight,f.get('notes')));msg='Tartım kaydı eklendi.'
                    return self.redirect('/animal?id='+aid,msg)
                if path=='/animal/milk':
                    c.execute('insert into milk(animal_id,measure_date,liters,notes) values(?,?,?,?)',(f['animal_id'],f['measure_date'],float(f['liters']),f.get('notes')));return self.redirect('/animal?id='+f['animal_id'],'Süt kaydı eklendi.')
                if path in ('/animals','/males'):
                    upload=f.get('photo_file'); photo_url=f.get('photo_url','')
                    if upload and isinstance(upload,dict) and upload.get('content'):
                        ext=Path(upload['filename']).suffix.lower()
                        if ext not in ('.jpg','.jpeg','.png','.webp','.gif'): return self.redirect(path,'Desteklenmeyen fotoğraf biçimi.')
                        if len(upload['content'])>10*1024*1024: return self.redirect(path,'Fotoğraf 10 MB sınırını aşıyor.')
                        name=save_optimized_upload('animal_new',upload); photo_url='/uploads/'+name
                    vals=(f['tag'],f.get('nickname'),f['gender'],f.get('breed'),f.get('birth_date'),f.get('notes'),f.get('paddock'),photo_url,float(f.get('sold_price') or 0),f.get('status') or 'Aktif',f.get('purchase_date',''),float(f.get('purchase_price') or 0),float(f.get('purchase_weight') or 0),float(f.get('daily_feed_cost') or 0),float(f.get('daily_care_cost') or 0),float(f.get('target_sale_price') or 0))
                    if f.get('id'):
                        c.execute('update animals set tag=?,nickname=?,gender=?,breed=?,birth_date=?,notes=?,paddock=?,photo_url=?,sold_price=?,status=?,purchase_date=?,purchase_price=?,purchase_weight=?,daily_feed_cost=?,daily_care_cost=?,target_sale_price=? where id=?',vals+(f['id'],)); aid=f['id']
                    else:
                        cur=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes,paddock,photo_url,sold_price,status,purchase_date,purchase_price,purchase_weight,daily_feed_cost,daily_care_cost,target_sale_price) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',vals); aid=cur.lastrowid
                    if photo_url.startswith('/uploads/'):
                        fname=photo_url.split('/uploads/',1)[1]
                        exists=c.execute('select 1 from animal_photos where animal_id=? and filename=?',(aid,fname)).fetchone()
                        if not exists:c.execute('insert into animal_photos(animal_id,filename,created_at,caption) values(?,?,?,?)',(aid,fname,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Profil fotoğrafı'))
                    return self.redirect('/males' if path=='/males' else '/animals','Hayvan kaydedildi.')
                if path=='/calves':
                    m=c.execute("select id from animals where id=? and gender='Dişi'",(f['mother_id'],)).fetchone()
                    if not m:return self.redirect('/calves','Anne olarak yalnızca kayıtlı dişi hayvan seçilebilir.')
                    vals=(f['tag'],f['mother_id'],f.get('father_tag'),f['birth_date'],f.get('gender'),f.get('notes'))
                    if f.get('id'):c.execute('update calves set tag=?,mother_id=?,father_tag=?,birth_date=?,gender=?,notes=? where id=?',vals+(f['id'],));msg='Buzağı güncellendi.'
                    else:c.execute('insert into calves(tag,mother_id,father_tag,birth_date,gender,notes) values(?,?,?,?,?,?)',vals);msg='Buzağı kaydedildi.'
                    promote_mature_calves(); return self.redirect('/calves',msg)
                if path=='/estrus':
                    aid=f.get('animal_id',''); a=c.execute("select id,tag from animals where id=? and gender='Dişi' and coalesce(status,'Aktif')='Aktif'",(aid,)).fetchone()
                    if not a:return self.redirect('/estrus','Lütfen geçerli ve aktif bir dişi hayvan seçin.')
                    if is_currently_pregnant(c,aid):return self.redirect('/estrus',f'{a["tag"]} şu anda gebe görünüyor. Doğum ve buzağı kaydı tamamlanmadan yeni kızgınlık kaydı açılamaz.')
                    estrus_date=f.get('estrus_date','')
                    try: estrus_day=date.fromisoformat(estrus_date)
                    except Exception:return self.redirect('/estrus','Geçerli bir kızgınlık tarihi girin.')
                    if estrus_day>date.today():return self.redirect('/estrus','Gelecek tarihli kızgınlık kaydı girilemez.')
                    duplicate=c.execute('select id from estrus_records where animal_id=? and estrus_date=?',(aid,estrus_date)).fetchone()
                    if duplicate:return self.redirect('/estrus',f'{a["tag"]} için {fmt_date(estrus_date)} tarihinde zaten kızgınlık kaydı var. Yeni kayıt açılmadı; mevcut kaydı Düzenle ile değiştirebilirsiniz.')
                    c.execute('insert into estrus_records(animal_id,estrus_date,signs,notes,created_at) values(?,?,?,?,?)',(aid,estrus_date,f.get('signs',''),f.get('notes',''),datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    audit(username,'Kızgınlık kaydı eklendi',f'{a["tag"]} · {estrus_date}',self.client_ip())
                    return self.redirect('/estrus',f'{a["tag"]} için kızgınlık kaydı eklendi. Beklenen yeni pencere {fmt_date((estrus_day+timedelta(days=18)).isoformat())} – {fmt_date((estrus_day+timedelta(days=24)).isoformat())}.')
                if path=='/estrus-edit':
                    eid=f.get('id','')
                    rec=c.execute('select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where e.id=?',(eid,)).fetchone()
                    if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
                    estrus_date=f.get('estrus_date','')
                    try: estrus_day=date.fromisoformat(estrus_date)
                    except Exception:return self.redirect('/estrus-edit?id='+str(eid),'Geçerli bir kızgınlık tarihi girin.')
                    if estrus_day>date.today():return self.redirect('/estrus-edit?id='+str(eid),'Gelecek tarihli kızgınlık kaydı girilemez.')
                    duplicate=c.execute('select id from estrus_records where animal_id=? and estrus_date=? and id<>?',(rec['animal_id'],estrus_date,eid)).fetchone()
                    if duplicate:return self.redirect('/estrus-edit?id='+str(eid),f'{rec["tag"]} için {fmt_date(estrus_date)} tarihinde başka bir kızgınlık kaydı zaten var.')
                    c.execute('update estrus_records set estrus_date=?,signs=?,notes=? where id=?',(estrus_date,f.get('signs',''),f.get('notes',''),eid))
                    audit(username,'Kızgınlık kaydı güncellendi',f'{rec["tag"]} · {estrus_date}',self.client_ip())
                    return self.redirect('/estrus','Kızgınlık kaydı güncellendi.')
                if path=='/estrus-send':
                    eid=f.get('estrus_id','')
                    try: cycle_no=int(f.get('cycle_no','1'))
                    except Exception: cycle_no=1
                    rec=c.execute('select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where e.id=?',(eid,)).fetchone()
                    if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
                    if is_currently_pregnant(c,rec['animal_id']):return self.redirect('/estrus',f'{rec["tag"]} şu anda gebe görünüyor. Tohumlama takibine gönderilemedi.')
                    current_cycle=next_estrus_cycle(c,rec,date.today())
                    if not current_cycle or current_cycle['cycle_no']!=cycle_no:
                        return self.redirect('/estrus','Bu östrus dönemi daha önce sonuçlandırılmış veya artık aktif değil.')
                    c.execute("insert or replace into estrus_decisions(estrus_id,cycle_no,decision,decision_date,notes) values(?,?,?,?,?)",(eid,cycle_no,'Tohumlamaya Gönderildi',date.today().isoformat(),'Hayvan Tohumlama Takibi ekranına gönderildi; gerçek tohumlama kaydı bekleniyor.'))
                    audit(username,'Kızgınlık tohumlama takibine gönderildi',f'{rec["tag"]} · {cycle_no}. tahmini döngü',self.client_ip())
                    return self.redirect(f'/inseminations?animal={rec["animal_id"]}&estrus={rec["id"]}',f'{rec["tag"]} Tohumlama Takibi ekranına gönderildi. Kızgınlık kartı kapatıldı; tohumlama gerçekleştiğinde tarihi kaydedin.')
                if path=='/estrus-skip':
                    eid=f.get('estrus_id','')
                    try: cycle_no=int(f.get('cycle_no','1'))
                    except Exception: cycle_no=1
                    rec=c.execute('select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where e.id=?',(eid,)).fetchone()
                    if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
                    current=next_estrus_cycle(c,rec,date.today())
                    if not current or current['cycle_no']!=cycle_no:return self.redirect(f.get('return_to') or '/estrus','Bu östrus dönemi daha önce sonuçlandırılmış veya artık aktif değil.')
                    c.execute("insert or replace into estrus_decisions(estrus_id,cycle_no,decision,decision_date,notes) values(?,?,?,?,?)",(eid,cycle_no,'Atlandı',date.today().isoformat(),'Kullanıcı bu östrus dönemini atladı.'))
                    audit(username,'Östrus atlandı',f'{rec["tag"]} · {cycle_no}. tahmini döngü',self.client_ip())
                    return self.redirect(f.get('return_to') or '/estrus',f'{rec["tag"]} için bu östrus dönemi atlandı. Sonraki döngü otomatik takip edilecek.')
                if path=='/estrus-inseminate':
                    eid=f.get('estrus_id','')
                    rec=c.execute('select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where e.id=?',(eid,)).fetchone()
                    if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
                    if is_currently_pregnant(c,rec['animal_id']):return self.redirect('/estrus',f'{rec["tag"]} şu anda gebe görünüyor. Yeni tohumlama işlemi engellendi.')
                    try:
                        observed=date.fromisoformat(rec['estrus_date']); start=observed+timedelta(days=18); end=observed+timedelta(days=24)
                    except Exception:return self.redirect('/estrus','Kızgınlık tarihi geçersiz.')
                    today=date.today()
                    actual_window=observed<=today<=observed+timedelta(days=1)
                    predicted_window=start<=today<=end
                    if not (actual_window or predicted_window):return self.redirect('/estrus',f'Tohumlama aktarımı yalnızca kaydedilen kızgınlık günü/ertesi gün veya beklenen kızgınlık penceresinde ({fmt_date(start.isoformat())} – {fmt_date(end.isoformat())}) yapılabilir.')
                    same_day=c.execute('select id,attempt from inseminations where animal_id=? and insemination_date=?',(rec['animal_id'],today.isoformat())).fetchone()
                    if same_day:return self.redirect('/inseminations?animal='+str(rec['animal_id']),f'{rec["tag"]} için bugün zaten tohumlama kaydı mevcut. Mükerrer kayıt oluşturulmadı.')
                    latest=c.execute('select max(attempt) from inseminations where animal_id=?',(rec['animal_id'],)).fetchone()[0] or 0
                    attempt=int(latest)+1
                    if attempt>3:return self.redirect('/inseminations?animal='+str(rec['animal_id']),'Bu hayvan için 3 tohumlama denemesi zaten kayıtlı. Önce mevcut kayıtları düzenleyin.')
                    cur=c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',(rec['animal_id'],attempt,today.isoformat(),'Bekleniyor',''))
                    cycle_no=0 if actual_window else max(1,round((today-observed).days/21))
                    c.execute("insert or replace into estrus_decisions(estrus_id,cycle_no,decision,decision_date,insemination_id,notes) values(?,?,?,?,?,?)",(rec['id'],cycle_no,'Tohumlamaya Gönderildi',today.isoformat(),cur.lastrowid,'Kızgınlık Takibi üzerinden doğrudan aktarıldı.'))
                    audit(username,'Kızgınlıktan tohumlamaya aktarıldı',f'{rec["tag"]} · {attempt}. deneme · {today.isoformat()}',self.client_ip())
                    return self.redirect('/inseminations?animal='+str(rec['animal_id']),f'{rec["tag"]} kızgınlık takibinden {attempt}. tohumlama olarak aktarıldı. Gebelik sonucu Bekleniyor durumunda.')
                if path=='/estrus-delete':
                    rec=c.execute('select e.*,a.tag from estrus_records e join animals a on a.id=e.animal_id where e.id=?',(f.get('id',''),)).fetchone()
                    if not rec:return self.redirect('/estrus','Kızgınlık kaydı bulunamadı.')
                    c.execute('delete from estrus_records where id=?',(rec['id'],)); audit(username,'Kızgınlık kaydı silindi',f'{rec["tag"]} · {rec["estrus_date"]}',self.client_ip())
                    return self.redirect('/estrus','Kızgınlık kaydı silindi.')
                if path=='/inseminations':
                    aid=f.get('animal_id','')
                    a=c.execute("select id,tag from animals where id=? and gender='Dişi' and coalesce(status,'Aktif')='Aktif'",(aid,)).fetchone()
                    if not a:return self.redirect('/inseminations','Lütfen geçerli ve aktif bir dişi hayvan seçin.')
                    if is_currently_pregnant(c,aid):return self.redirect('/inseminations',f'{a["tag"]} şu anda gebe görünüyor. Doğum ve buzağı kaydı tamamlanmadan yeni tohumlama kaydı açılamaz.')
                    ins_date=f.get('insemination_date','')
                    try:ins_day=date.fromisoformat(ins_date)
                    except Exception:return self.redirect('/inseminations','Geçerli bir tohumlama tarihi girin.')
                    if ins_day>date.today():return self.redirect('/inseminations','Gelecek tarihli tohumlama kaydı girilemez.')
                    latest=c.execute('select max(attempt) from inseminations where animal_id=?',(aid,)).fetchone()[0] or 0
                    attempt=int(latest)+1
                    if attempt>3:return self.redirect('/inseminations?animal='+str(aid),'Bu hayvan için 3 tohumlama denemesi zaten kayıtlı. Önce mevcut kayıtları düzenleyin.')
                    cur=c.execute('insert into inseminations(animal_id,attempt,insemination_date,pregnancy_result,due_date) values(?,?,?,?,?)',(aid,attempt,ins_date,'Bekleniyor',''))
                    linked_estrus=f.get('estrus_id','')
                    if linked_estrus:
                        er=c.execute('select * from estrus_records where id=? and animal_id=?',(linked_estrus,aid)).fetchone()
                        if er:
                            cyc=next_estrus_cycle(c,er,date.fromisoformat(ins_date))
                            if cyc:c.execute("insert or replace into estrus_decisions(estrus_id,cycle_no,decision,decision_date,insemination_id,notes) values(?,?,?,?,?,?)",(er['id'],cyc['cycle_no'],'Tohumlamaya Gönderildi',ins_date,cur.lastrowid,'Tohumlama ekranından kaydedildi.'))
                    audit(username,'Tohumlama kaydı eklendi',f'{a["tag"]} · {attempt}. deneme · {ins_date}',self.client_ip())
                    return self.redirect('/inseminations?animal='+str(aid),f'{a["tag"]} için {attempt}. tohumlama kaydedildi.')
                if path=='/pregnancy-edit':
                    aid=int(f.get('animal_id') or 0)
                    a=c.execute("select * from animals where id=? and gender='Dişi'",(aid,)).fetchone()
                    if not a:return self.redirect('/animals','Dişi hayvan bulunamadı.')
                    if not str(a['pregnancy_source'] or '').startswith('Satın Alındığında Gebe'):
                        return self.redirect('/animal?id='+str(aid),'Bu işlem yalnız dışarıdan gebe alınan hayvanlar için kullanılabilir.')
                    rec=current_pregnancy_record(c,aid)
                    if not rec:return self.redirect('/animal?id='+str(aid),'Aktif gebelik kaydı bulunamadı.')
                    mode=(f.get('pregnancy_info_mode') or 'age').strip()
                    ref=(f.get('pregnancy_entry_date') or date.today().isoformat()).strip()
                    try:ref_day=date.fromisoformat(ref)
                    except:return self.redirect('/pregnancy-edit?animal_id='+str(aid),'Bilgi tarihi geçersiz.')
                    age_months=0.0
                    if mode=='date':
                        ins_date=(f.get('known_insemination_date') or '').strip()
                        try:ins_day=date.fromisoformat(ins_date)
                        except:return self.redirect('/pregnancy-edit?animal_id='+str(aid),'Son tohumlama tarihi geçersiz.')
                        if ins_day>ref_day:return self.redirect('/pregnancy-edit?animal_id='+str(aid),'Tohumlama tarihi bilgi tarihinden sonra olamaz.')
                        due=(ins_day+timedelta(days=280)).isoformat()
                        result='Gebe (Satın Alındığında · Tohumlama Tarihi Biliniyor)'
                        source='Satın Alındığında Gebe · Tohumlama Tarihi'
                    else:
                        try:age_months=float(f.get('pregnancy_age_months') or 0)
                        except:age_months=0
                        if age_months<=0 or age_months>9:return self.redirect('/pregnancy-edit?animal_id='+str(aid),'Gebelik yaşını 0,5-9 ay arasında girin.')
                        elapsed=round(age_months*(280/9));ins_day=ref_day-timedelta(days=elapsed);ins_date=ins_day.isoformat()
                        due=(ins_day+timedelta(days=280)).isoformat()
                        result='Gebe (Satın Alındığında · Gebelik Yaşından Tahmini)'
                        source='Satın Alındığında Gebe · Yaklaşık'
                    c.execute('update inseminations set insemination_date=?,pregnancy_result=?,due_date=? where id=?',(ins_date,result,due,rec['id']))
                    c.execute('update animals set pregnancy_source=?,pregnancy_age_months_at_entry=?,pregnancy_entry_date=? where id=?',(source,age_months,ref,aid))
                    audit(username,'Dışarıdan gebe hayvan bilgisini güncelledi',f'{a["tag"]} · Tahmini doğum {due}',self.client_ip())
                    return self.redirect('/animal?id='+str(aid),'Gebelik bilgisi güncellendi; hayvan kartı ve Tohumlama kaydı senkronlandı.')
                if path=='/insemination-edit':
                    iid=f.get('id','')
                    rec=c.execute('select i.*,a.tag from inseminations i join animals a on a.id=i.animal_id where i.id=?',(iid,)).fetchone()
                    if not rec:return self.redirect('/inseminations','Tohumlama kaydı bulunamadı.')
                    ins_date=f.get('insemination_date','')
                    try:ins_day=date.fromisoformat(ins_date)
                    except Exception:return self.redirect('/insemination-edit?id='+str(iid),'Geçerli bir tarih girin.')
                    if ins_day>date.today():return self.redirect('/insemination-edit?id='+str(iid),'Gelecek tarihli tohumlama kaydı girilemez.')
                    result=f.get('pregnancy_result','Bekleniyor')
                    if result not in ('Bekleniyor','Pozitif','Negatif','Belirsiz'):result='Belirsiz'
                    animal=c.execute('select pregnancy_source from animals where id=?',(rec['animal_id'],)).fetchone()
                    external=animal and str(animal['pregnancy_source'] or '').startswith('Satın Alındığında Gebe')
                    if external and result=='Pozitif':
                        result='Gebe (Satın Alındığında · Tohumlama Tarihi Biliniyor)'
                    due=(ins_day+timedelta(days=280)).isoformat() if is_pregnant_value(result) else ''
                    c.execute('update inseminations set insemination_date=?,pregnancy_result=?,due_date=? where id=?',(ins_date,result,due,iid))
                    audit(username,'Tohumlama kaydı güncellendi',f'{rec["tag"]} · {rec["attempt"]}. deneme',self.client_ip())
                    return self.redirect('/inseminations?animal='+str(rec['animal_id']),'Tohumlama kaydı güncellendi.')
                if path=='/insemination-delete':
                    iid=f.get('id','')
                    rec=c.execute('select i.*,a.tag from inseminations i join animals a on a.id=i.animal_id where i.id=?',(iid,)).fetchone()
                    if not rec:return self.redirect('/inseminations','Tohumlama kaydı bulunamadı.')
                    c.execute('delete from inseminations where id=?',(iid,))
                    remaining=c.execute('select id,attempt from inseminations where animal_id=? order by attempt,insemination_date,id',(rec['animal_id'],)).fetchall()
                    for idx,row in enumerate(remaining,1):
                        if row['attempt']!=idx:c.execute('update inseminations set attempt=? where id=?',(idx,row['id']))
                    audit(username,'Tohumlama kaydı silindi',f'{rec["tag"]} · {rec["attempt"]}. deneme',self.client_ip())
                    return self.redirect('/inseminations?animal='+str(rec['animal_id']),'Tohumlama kaydı silindi ve deneme sırası yeniden düzenlendi.')
                if path=='/pregnancy-vaccine/done':
                    aid=int(f['animal_id']); ins_id=int(f['insemination_id']); month=int(f['month'])
                    if month not in (7,8):return self.redirect('/','Geçersiz gebelik aşı görevi.')
                    ins=c.execute("select i.*,a.tag from inseminations i join animals a on a.id=i.animal_id where i.id=? and i.animal_id=?",(ins_id,aid)).fetchone()
                    if not ins or not is_pregnant_value(ins['pregnancy_result']):return self.redirect('/','Gebelik kaydı bulunamadı veya aktif değil.')
                    token=f'GEBELIK_ASI|{ins_id}|{month}'
                    existing=c.execute("select id from health where animal_id=? and notes like ? limit 1",(aid,token+'%')).fetchone()
                    if not existing:
                        product=f'{month}. Ay Gebelik Aşısı'
                        notes=token+' | Dashboard gebelik aşı alarmından tamamlandı.'
                        c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(aid,'Aşı',product,date.today().isoformat(),'',0,notes))
                        audit(username,'Gebelik aşısı yapıldı',f'{ins["tag"]} · {month}. ay',self.client_ip())
                    target=f.get('return_to') or ('/animal?id='+str(aid))
                    return self.redirect(target,f'{ins["tag"]} · {month}. ay gebelik aşısı sağlık geçmişine kaydedildi.')
                if path=='/health-edit':
                    hid=int(f.get('id') or 0)
                    old=c.execute('select * from health where id=?',(hid,)).fetchone()
                    if not old:return self.redirect('/health','Sağlık kaydı bulunamadı.')
                    c.execute('update health set kind=?,product=?,applied_date=?,next_date=?,cost=?,notes=? where id=?',
                              (f.get('kind'),f.get('product'),f.get('applied_date'),f.get('next_date') or '',float(f.get('cost') or 0),f.get('notes') or '',hid))
                    audit(username,'Sağlık kaydı düzenledi',f'#{hid} · {f.get("product")}',self.client_ip())
                    return self.redirect('/health','Sağlık kaydı güncellendi.')
                if path=='/health-delete':
                    hid=int(f.get('id') or 0)
                    old=c.execute('select * from health where id=?',(hid,)).fetchone()
                    if not old:return self.redirect('/health','Sağlık kaydı bulunamadı.')
                    c.execute('delete from health where id=?',(hid,))
                    audit(username,'Sağlık kaydı sildi',f'#{hid} · {old["product"]}',self.client_ip())
                    return self.redirect('/health','Sağlık kaydı silindi.')
                if path=='/health/plan-done':
                    source_id=int(f.get('source_id') or 0)
                    src=c.execute("select h.*,a.tag as animal_tag,ca.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves ca on ca.id=h.calf_id where h.id=?",(source_id,)).fetchone()
                    if not src:return self.redirect('/health','Planlanan sağlık kaydı bulunamadı.')
                    if not src['next_date']:return self.redirect(f.get('return_to') or '/health','Bu plan daha önce tamamlanmış.')
                    tag=src['animal_tag'] or src['calf_tag'] or '-'; actual=date.today().isoformat(); planned=src['next_date']
                    product=str(src['product'] or '')
                    if src['kind']=='Aşı' and 'IKINCI_DOZ_PLAN' in str(src['notes'] or ''): product += ' · 2. Doz'
                    notes=f'Planlanan sağlık işlemi tamamlandı | Kaynak sağlık #{source_id} | Planlanan {planned}'
                    c.execute('insert into health(animal_id,calf_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?,?)',(src['animal_id'],src['calf_id'],src['kind'],product,actual,'',0,notes))
                    c.execute("update health set next_date='',notes=coalesce(notes,'')||? where id=?",(' | Tamamlandı: '+actual,source_id))
                    audit(username,'Planlanan sağlık işlemini tamamladı',f'{tag} · {product}',self.client_ip())
                    return self.redirect(f.get('return_to') or '/health',f'{tag} · işlem {fmt_date(actual)} tarihinde yapıldı olarak kaydedildi.')
                if path=='/health/second-dose-done':
                    source_id=int(f.get('source_id') or 0)
                    src=c.execute("select h.*,a.tag as animal_tag,ca.tag as calf_tag from health h left join animals a on a.id=h.animal_id left join calves ca on ca.id=h.calf_id where h.id=?",(source_id,)).fetchone()
                    if not src:return self.redirect('/health','Planlanan aşı kaydı bulunamadı.')
                    if not src['next_date']:return self.redirect('/health','Bu ikinci doz daha önce tamamlanmış veya plan kapatılmış.')
                    if src['kind']!='Aşı' or 'IKINCI_DOZ_PLAN' not in str(src['notes'] or ''):return self.redirect('/health','Bu kayıt ikinci doz planı değil.')
                    tag=src['animal_tag'] or src['calf_tag'] or '-'
                    actual=date.today().isoformat()
                    product=str(src['product'] or '')+' · 2. Doz'
                    notes=f'2. doz tamamlandı | Kaynak sağlık #{source_id} | Planlanan {src["next_date"]}'
                    c.execute('insert into health(animal_id,calf_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?,?)',(src['animal_id'],src['calf_id'],'Aşı',product,actual,'',0,notes))
                    c.execute("update health set next_date='',notes=coalesce(notes,'')||? where id=?",(' | 2. doz tamamlandı: '+actual,source_id))
                    audit(username,'Aşı ikinci dozu tamamladı',f'{tag} · {product}',self.client_ip())
                    return self.redirect(f.get('return_to') or '/health',f'{tag} · 2. doz sağlık geçmişine kaydedildi.')
                if path=='/health/task-done':
                    tid=int(f.get('task_id') or 0)
                    t=c.execute("""select t.*,hc.kind,hc.product from health_tasks t join health_courses hc on hc.id=t.course_id where t.id=?""",(tid,)).fetchone()
                    if not t:return self.redirect('/health','Planlanan işlem bulunamadı.')
                    if t['status']!='Bekliyor':return self.redirect('/health','Bu uygulama daha önce tamamlanmış.')
                    actual=date.today().isoformat();product=str(t['product'] or '')
                    if t['kind']=='Aşı':product+=f' · {int(t["dose_no"] or 1)}. Doz'
                    elif t['kind']=='İlaç':product+=f' · Gün {int(t["day_no"] or 1)}/{int(t["day_total"] or 1)} · Uygulama {int(t["application_no"] or 1)}/{int(t["applications_per_day"] or 1)}'
                    notes=f'Planlı uygulama tamamlandı | Plan #{t["course_id"]} | Planlanan {t["planned_date"]}'
                    c.execute('insert into health(animal_id,calf_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?,?)',(t['animal_id'],t['calf_id'],t['kind'],product,actual,'',float(t['cost'] or 0),notes))
                    c.execute("update health_tasks set status='Tamamlandı',completed_date=? where id=?",(actual,tid))
                    if float(t['cost'] or 0)>0:c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at) values(?,?,?,?,?,?,?,?)',(actual,'Gider',t['kind'],float(t['cost'] or 0),product,'Nakit',t['animal_id'],datetime.now().isoformat()))
                    audit(username,'Planlı sağlık uygulaması tamamlandı',f'Görev #{tid} · {product}',self.client_ip())
                    return self.redirect('/health','Sağlık uygulaması Yapıldı olarak kaydedildi.')
                if path=='/health/task-batch-done':
                    course_id=int(f.get('course_id') or 0);planned=(f.get('planned_date') or '').strip();dose_no=int(f.get('dose_no') or 1);day_no=int(f.get('day_no') or 1);app_no=int(f.get('application_no') or 1)
                    tasks=c.execute("""select t.*,hc.kind,hc.product from health_tasks t join health_courses hc on hc.id=t.course_id where t.course_id=? and t.planned_date=? and t.dose_no=? and t.day_no=? and t.application_no=? and t.status='Bekliyor'""",(course_id,planned,dose_no,day_no,app_no)).fetchall()
                    if not tasks:return self.redirect('/health','Bu toplu uygulama daha önce tamamlanmış veya bulunamadı.')
                    actual=date.today().isoformat();count=0
                    for t in tasks:
                        product=str(t['product'] or '')
                        if t['kind']=='Aşı':product+=f' · {int(t["dose_no"] or 1)}. Doz'
                        else:product+=f' · Gün {int(t["day_no"] or 1)}/{int(t["day_total"] or 1)} · Uygulama {int(t["application_no"] or 1)}/{int(t["applications_per_day"] or 1)}'
                        notes=f'Padok bazlı plan tamamlandı | Plan #{course_id} | Planlanan {planned}'
                        c.execute('insert into health(animal_id,calf_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?,?)',(t['animal_id'],t['calf_id'],t['kind'],product,actual,'',float(t['cost'] or 0),notes))
                        c.execute("update health_tasks set status='Tamamlandı',completed_date=? where id=?",(actual,t['id']))
                        if float(t['cost'] or 0)>0:c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at) values(?,?,?,?,?,?,?,?)',(actual,'Gider',t['kind'],float(t['cost'] or 0),product,'Nakit',t['animal_id'],datetime.now().isoformat()))
                        count+=1
                    audit(username,'Padok sağlık uygulaması tamamlandı',f'Plan #{course_id} · {count} hayvan',self.client_ip())
                    return self.redirect('/health',f'{count} hayvan için uygulama Yapıldı olarak sağlık geçmişine işlendi.')
                if path=='/health':
                    scope=(f.get('scope_type') or 'single').strip();kind=(f.get('kind') or '').strip();product=(f.get('product') or '').strip();applied=(f.get('applied_date') or '').strip();notes=(f.get('notes') or '').strip()
                    if not product:return self.redirect('/health','Ürün / işlem adı zorunludur.')
                    try:date.fromisoformat(applied)
                    except:return self.redirect('/health','Uygulama tarihi geçersiz.')
                    try:cost=max(0,float(f.get('cost') or 0))
                    except:cost=0
                    targets=[];paddock_id=None
                    if scope=='paddock':
                        if kind!='Aşı':return self.redirect('/health','Padok bazlı plan şu anda yalnız aşı için kullanılabilir.')
                        try:paddock_id=int(f.get('paddock_id') or 0)
                        except:paddock_id=0
                        pd=c.execute('select id,name from paddocks where id=? and active=1',(paddock_id,)).fetchone()
                        if not pd:return self.redirect('/health','Geçerli bir padok seçin.')
                        for r in c.execute("select id,tag from animals where paddock_id=? and coalesce(status,'Aktif')='Aktif'",(paddock_id,)).fetchall():targets.append((r['id'],None,r['tag']))
                        for r in c.execute("select id,tag from calves where paddock_id=? and promoted_animal_id is null",(paddock_id,)).fetchall():targets.append((None,r['id'],r['tag']))
                        if not targets:return self.redirect('/health','Seçilen padokta aktif hayvan bulunamadı.')
                    else:
                        subject=(f.get('subject_key') or '').strip()
                        if ':' not in subject:return self.redirect('/health','Lütfen geçerli bir hayvan veya buzağı seçin.')
                        stype,sid=subject.split(':',1)
                        try:sid=int(sid)
                        except:return self.redirect('/health','Hayvan seçimi geçersiz.')
                        if stype=='A':
                            rec=c.execute("select id,tag from animals where id=? and coalesce(status,'Aktif')='Aktif'",(sid,)).fetchone()
                            if not rec:return self.redirect('/health','Seçilen hayvan aktif sürüde değil.')
                            targets=[(sid,None,rec['tag'])]
                        elif stype=='C':
                            rec=c.execute("select id,tag from calves where id=? and promoted_animal_id is null",(sid,)).fetchone()
                            if not rec:return self.redirect('/health','Seçilen buzağı aktif kayıtlarda değil.')
                            targets=[(None,sid,rec['tag'])]
                        else:return self.redirect('/health','Hayvan seçimi geçersiz.')
                    if kind in ('Aşı','İlaç'):
                        if kind=='Aşı':
                            try:dose_count=max(1,min(10,int(f.get('dose_count') or 1)))
                            except:dose_count=1
                            try:interval=max(1,min(365,int(f.get('dose_interval_days') or 15)))
                            except:interval=15
                            treatment_days=1;times_per_day=1
                        else:
                            try:treatment_days=max(1,min(60,int(f.get('treatment_days') or 1)))
                            except:treatment_days=1
                            try:times_per_day=max(1,min(6,int(f.get('times_per_day') or 1)))
                            except:times_per_day=1
                            dose_count=1;interval=0
                        cur=c.execute('''insert into health_courses(kind,product,scope_type,paddock_id,start_date,treatment_days,times_per_day,dose_count,interval_days,cost_per_application,notes,created_at) values(?,?,?,?,?,?,?,?,?,?,?,?)''',(kind,product,scope,paddock_id,applied,treatment_days,times_per_day,dose_count,interval,cost,notes,datetime.now().isoformat(timespec='seconds')))
                        course_id=cur.lastrowid;start_day=date.fromisoformat(applied);task_count=0
                        for animal_id,calf_id,tag in targets:
                            if kind=='Aşı':
                                for dn in range(1,dose_count+1):
                                    planned=(start_day+timedelta(days=(dn-1)*interval)).isoformat()
                                    c.execute('''insert into health_tasks(course_id,animal_id,calf_id,planned_date,dose_no,dose_total,day_no,day_total,application_no,applications_per_day,status,cost,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(course_id,animal_id,calf_id,planned,dn,dose_count,1,1,1,1,'Bekliyor',cost,notes));task_count+=1
                            else:
                                for day_no in range(1,treatment_days+1):
                                    planned=(start_day+timedelta(days=day_no-1)).isoformat()
                                    for app_no in range(1,times_per_day+1):
                                        c.execute('''insert into health_tasks(course_id,animal_id,calf_id,planned_date,dose_no,dose_total,day_no,day_total,application_no,applications_per_day,status,cost,notes) values(?,?,?,?,?,?,?,?,?,?,?,?,?)''',(course_id,animal_id,calf_id,planned,1,1,day_no,treatment_days,app_no,times_per_day,'Bekliyor',cost,notes));task_count+=1
                        audit(username,'Sağlık planı oluşturdu',f'{kind} · {product} · {len(targets)} hayvan · {task_count} uygulama',self.client_ip())
                        if scope=='paddock':return self.redirect('/health',f'{len(targets)} hayvan için {dose_count} dozluk padok aşı planı oluşturuldu.')
                        if kind=='Aşı':return self.redirect('/health',f'{dose_count} dozluk aşı planı oluşturuldu. Her doz Yapıldı olarak işaretlenebilir.')
                        return self.redirect('/health',f'{treatment_days} gün × günde {times_per_day} uygulamalık tedavi planı oluşturuldu.')
                    if scope!='single':return self.redirect('/health','Muayene kaydı tek hayvan üzerinden oluşturulmalıdır.')
                    animal_id,calf_id,subject_tag=targets[0];next_date=(f.get('next_date') or '').strip()
                    c.execute('insert into health(animal_id,calf_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?,?)',(animal_id,calf_id,kind,product,applied,next_date,cost,notes))
                    if cost>0:c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at) values(?,?,?,?,?,?,?,?)',(applied,'Gider',kind,cost,product,'Nakit',animal_id,datetime.now().isoformat()))
                    audit(username,'Sağlık kaydı oluşturdu',f'{subject_tag} · {kind} · {product}',self.client_ip())
                    return self.redirect('/health','Sağlık kaydı oluşturuldu.')
                if path=='/finance/edit':
                    record_id=int(f['id'])
                    old=c.execute('select * from finance where id=?',(record_id,)).fetchone()
                    if not old:return self.redirect('/finance','Finans kaydı bulunamadı.')
                    category=f['category']; animal_id=f.get('animal_id') or None
                    action='Satıldı' if category=='Hayvan Satışı' else 'Kesildi' if category=='Kesim Geliri' else ''
                    if action and not animal_id:return self.redirect(f'/finance/edit?id={record_id}','Satış veya kesim için ilgili hayvan seçilmelidir.')
                    old_animal_id=old['animal_id']
                    c.execute(
                        'update finance set tx_date=?,tx_type=?,category=?,amount=?,description=?,payment_method=?,animal_id=?,animal_status_action=? where id=?',
                        (f['tx_date'],f['tx_type'],category,float(f['amount']),f.get('description'),f.get('payment_method'),animal_id,action,record_id)
                    )
                    if category!='Süt Satışı':
                        c.execute('delete from finance_animals where finance_id=?',(record_id,))
                    recalculate_animal_exit_status(c,old_animal_id)
                    if animal_id!=old_animal_id:recalculate_animal_exit_status(c,animal_id)
                    return self.redirect('/finance','Finans kaydı güncellendi.')
                if path in ('/finance/delete','/finance-delete'):
                    record_id=int(f.get('id') or 0)
                    old=c.execute('select * from finance where id=?',(record_id,)).fetchone()
                    if not old:return self.redirect('/finance','Finans kaydı bulunamadı.')
                    animal_id=old['animal_id']
                    c.execute('delete from finance_animals where finance_id=?',(record_id,))
                    c.execute('delete from finance where id=?',(record_id,))
                    if animal_id:recalculate_animal_exit_status(c,animal_id)
                    return self.redirect('/finance','Finans kaydı silindi.')
                if path=='/finance':
                    category=f['category']; tx_type=f.get('tx_type','Gelir')
                    action='Satıldı' if category=='Hayvan Satışı' else 'Kesildi' if category=='Kesim Geliri' else ''
                    amount=round(float(f['amount']),2)
                    if amount<=0:return self.redirect('/finance','Tutar 0’dan büyük olmalıdır.')
                    milk_mode=tx_type=='Gelir' and category=='Süt Satışı'
                    if milk_mode:
                        raw_ids=[x.strip() for x in (f.get('milk_animal_ids') or '').split(',') if x.strip()];animal_ids=[]
                        for x in raw_ids:
                            try:aid=int(x)
                            except:continue
                            if aid not in animal_ids:animal_ids.append(aid)
                        if not animal_ids:return self.redirect('/finance','Süt satışı için en az bir aktif dişi hayvan seçilmelidir.')
                        placeholders=','.join('?' for _ in animal_ids);selected=c.execute(f"select id,tag,gender,status from animals where id in ({placeholders})",animal_ids).fetchall()
                        if len(selected)!=len(animal_ids):return self.redirect('/finance','Seçilen dişi hayvanlardan biri bulunamadı.')
                        if any(str(r['gender'] or '')!='Dişi' or str(r['status'] or 'Aktif')!='Aktif' for r in selected):return self.redirect('/finance','Süt satışına yalnız aktif dişi hayvanlar bağlanabilir. Sayfayı yenileyin.')
                        fingerprint=finance_request_fingerprint(username,f)
                        if not claim_request_once(c,fingerprint,15):
                            return self.redirect('/finance','⚠️ Aynı finans kaydı ikinci kez gönderildi; mükerrer kayıt engellendi.')
                        created=datetime.now().isoformat();tags=', '.join(str(r['tag']) for r in selected);desc=(f.get('description') or '').strip();relation_note=f'Süt satışı · {len(animal_ids)} dişi: {tags}'
                        c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',(f['tx_date'],tx_type,category,amount,(desc+' · ' if desc else '')+relation_note,f.get('payment_method'),None,created,''));finance_id=c.execute('select last_insert_rowid()').fetchone()[0]
                        for aid in animal_ids:c.execute('insert or ignore into finance_animals(finance_id,animal_id,relation_type) values(?,?,?)',(finance_id,aid,'Süt Satışı'))
                        audit(username,'Süt satışını dişi hayvanlara ilişkilendirdi',f'{len(animal_ids)} dişi · {money(amount)}',self.client_ip());return self.redirect('/finance',f'Süt satışı kaydedildi ve {len(animal_ids)} aktif dişi hayvana ilişkilendirildi.')
                    bulk_mode=tx_type=='Gelir' and category in ('Hayvan Satışı','Kesim Geliri')
                    if bulk_mode:
                        raw_ids=[x.strip() for x in (f.get('animal_ids') or '').split(',') if x.strip()]
                        animal_ids=[]
                        for x in raw_ids:
                            try: aid=int(x)
                            except: continue
                            if aid not in animal_ids: animal_ids.append(aid)
                        if not animal_ids:return self.redirect('/finance','Hayvan satışı veya kesim geliri için en az bir hayvan seçilmelidir.')
                        placeholders=','.join('?' for _ in animal_ids)
                        selected=c.execute(f"select id,tag,nickname,status from animals where id in ({placeholders})",animal_ids).fetchall()
                        if len(selected)!=len(animal_ids):return self.redirect('/finance','Seçilen hayvanlardan biri bulunamadı.')
                        inactive=[r for r in selected if str(r['status'] or 'Aktif')!='Aktif']
                        if inactive:return self.redirect('/finance','Seçilen hayvanlardan biri artık aktif sürüde değil. Sayfayı yenileyip tekrar deneyin.')
                        fingerprint=finance_request_fingerprint(username,f)
                        if not claim_request_once(c,fingerprint,15):
                            return self.redirect('/finance','⚠️ Aynı finans kaydı ikinci kez gönderildi; mükerrer kayıt engellendi.')
                        total_cents=int(round(amount*100)); n=len(animal_ids)
                        base=total_cents//n; remainder=total_cents-(base*n)
                        description=(f.get('description') or '').strip()
                        batch_note=f'{category}: {n} hayvan · toplam {money(amount)}'
                        created=datetime.now().isoformat()
                        for idx,aid in enumerate(animal_ids):
                            cents=base+(1 if idx<remainder else 0)
                            share=cents/100.0
                            desc=(description+' · ' if description else '')+batch_note
                            c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',(f['tx_date'],tx_type,category,share,desc,f.get('payment_method'),aid,created,action))
                            c.execute('update animals set status=?,exit_date=?,exit_reason=?,sold_price=? where id=?',(action,f['tx_date'],category,share,aid))
                        audit(username,'Finans geliri hayvanlara dağıtıldı',f'{category} · {n} hayvan · {money(amount)}',self.client_ip())
                        if n==1:
                            return self.redirect('/finance',f'{money(amount)} gelir seçilen hayvana kaydedildi.')
                        return self.redirect('/finance',f'{n} hayvana toplam {money(amount)} gelir otomatik dağıtıldı. Hayvan başı {money(amount/n)}.')
                    animal_id=f.get('animal_id') or None
                    if action and not animal_id:return self.redirect('/finance','Hayvan satışı veya kesim geliri için ilgili hayvan seçilmelidir.')
                    if category=='Hayvan Alımı' and animal_id:
                        existing_purchase=c.execute("select id from finance where category='Hayvan Alımı' and animal_id=? limit 1",(animal_id,)).fetchone()
                        if existing_purchase:return self.redirect('/finance','Bu hayvan daha önce Hayvan Alımı gideriyle ilişkilendirilmiş. İkinci alış kaydı engellendi.')
                    fingerprint=finance_request_fingerprint(username,f)
                    if not claim_request_once(c,fingerprint,15):
                        return self.redirect('/finance','⚠️ Aynı finans kaydı ikinci kez gönderildi; mükerrer kayıt engellendi.')
                    c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',(f['tx_date'],tx_type,category,amount,f.get('description'),f.get('payment_method'),animal_id,datetime.now().isoformat(),action))
                    if action:c.execute('update animals set status=?,exit_date=?,exit_reason=?,sold_price=? where id=?',(action,f['tx_date'],category,amount,animal_id))
                    return self.redirect('/finance','Finans kaydı eklendi.' + (' Hayvan aktif sürüden çıkarıldı.' if action else ''))
        except sqlite3.IntegrityError as e:return self.redirect(path,'Aynı küpe numarası daha önce kaydedilmiş olabilir.')
        except Exception as e:
            if path in ('/finance/delete','/finance-delete'):
                return self.redirect('/finance','Finans kaydı silinemedi: '+str(e))
            return self.redirect(path,'Hata: '+str(e))

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));ip=s.getsockname()[0];s.close();return ip
    except:return '127.0.0.1'

if __name__=='__main__':
    init_db(); ensure_archive_schema(); promote_mature_calves(); daily_backup(); print(f'Yerel: http://127.0.0.1:{PORT}/login');print(f'Ağ: http://{local_ip()}:{PORT}/login');ThreadingHTTPServer(('0.0.0.0',PORT),App).serve_forever()
