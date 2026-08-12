import os, sqlite3, hashlib, secrets, urllib.parse, json, csv, io, shutil, socket, threading, webbrowser, zipfile, tempfile, hmac, time, gc
from email.parser import BytesParser
from email.policy import default
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http import cookies
from datetime import datetime, date, timedelta
from pathlib import Path

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
APP_VERSION='3.5.4'
APP_CHANNEL='Stable'
APP_LABEL='ENTERPRISE V3.5.4 FİNANS + ÖSTRUS DURUMU'

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

@media(max-width:650px){.profile{grid-template-columns:1fr}.photo{width:100%;height:220px}}@media(max-width:900px){.menu-toggle{display:inline-block}.side{transform:translateX(-105%);transition:transform .2s ease;width:260px;box-shadow:8px 0 24px #0003}.side.mobile-open{transform:translateX(0)}.main{margin-left:0;padding-top:18px}.grid{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}}@media(max-width:560px){.grid,.form{grid-template-columns:1fr}.main{padding:12px}.top{padding:0 12px}.brand{font-size:17px}}




.finance-toolbar{display:flex;gap:10px;align-items:end;flex-wrap:wrap}
.finance-toolbar label{display:flex;flex-direction:column;gap:5px;font-weight:700}
.finance-table-wrap{overflow-x:auto;border-radius:14px}
.finance-table{width:100%;border-collapse:collapse;min-width:900px}
.finance-table th{white-space:nowrap;background:#edf5ef}
.finance-table td{vertical-align:middle}
.finance-table .finance-actions{display:flex;gap:6px;align-items:center;white-space:nowrap}
.finance-table .finance-actions form{margin:0}
.finance-table .btn{padding:8px 12px}
.dashboard-editbar{display:flex;justify-content:flex-end;margin:10px 0 14px}
.dashboard-slot{position:relative}
.dashboard-slot-editor{margin-top:8px;padding:10px;border:1px dashed #9cb8a5;border-radius:12px;background:#f7fbf8}
.dashboard-slot-editor form{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0}
.dashboard-slot-editor select{min-width:190px}
.dashboard-empty-slot{min-height:145px;border:2px dashed #9cb8a5;border-radius:18px;display:flex;align-items:center;justify-content:center;background:#f7fbf8;color:#176b3a;font-size:34px;font-weight:800}
.dashboard-empty-slot small{display:block;font-size:14px;color:#6d8074;margin-top:6px}
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
.metric-icon{font-size:24px;display:block;margin-bottom:8px}.metric small{display:block;margin-top:5px;color:var(--mut);font-size:12px;font-weight:600}.metric.green{border-left-color:#2c9660}.metric.purple{border-left-color:#7b5cc7}.metric.teal{border-left-color:#178c91}.cost-visual{display:grid;grid-template-columns:.9fr 1.1fr;gap:18px;align-items:center}.donut{width:190px;height:190px;border-radius:50%;margin:auto;position:relative;background:conic-gradient(var(--blue) 0 var(--purchase-pct),var(--orange) var(--purchase-pct) 100%)}.donut:after{content:"";position:absolute;inset:31px;background:var(--card);border-radius:50%}.donut-center{position:absolute;inset:0;display:flex;z-index:2;align-items:center;justify-content:center;flex-direction:column;text-align:center}.donut-center b{font-size:20px}.legend-row{display:grid;grid-template-columns:14px 1fr auto;gap:8px;align-items:center;margin:11px 0}.legend-dot{width:12px;height:12px;border-radius:4px}.dot-blue{background:var(--blue)}.dot-orange{background:var(--orange)}.progress-list{display:grid;gap:12px}.progress-item{display:grid;gap:5px}.progress-head{display:flex;justify-content:space-between;gap:10px;font-size:13px}.progress-track{height:11px;background:#e8eee9;border-radius:99px;overflow:hidden}.progress-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--g2),var(--blue))}.dashboard-section-title{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:22px 0 10px}.dashboard-section-title h2{margin:0}.dashboard-section-title span{color:var(--mut);font-size:13px}@media(max-width:760px){.cost-visual{grid-template-columns:1fr}.donut{width:165px;height:165px}}

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
'''

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def is_pregnant_value(value):
    normalized=str(value or "").strip().lower()
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
        CREATE TABLE IF NOT EXISTS finance(id INTEGER PRIMARY KEY, tx_date TEXT NOT NULL, tx_type TEXT NOT NULL, category TEXT NOT NULL, amount REAL NOT NULL, description TEXT, payment_method TEXT, animal_id INTEGER, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS backups(id INTEGER PRIMARY KEY, filename TEXT, created_at TEXT, size_bytes INTEGER);
        CREATE TABLE IF NOT EXISTS weights(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, measure_date TEXT NOT NULL, weight REAL NOT NULL, notes TEXT);
        CREATE TABLE IF NOT EXISTS milk(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, measure_date TEXT NOT NULL, liters REAL NOT NULL, notes TEXT);
        CREATE TABLE IF NOT EXISTS animal_photos(id INTEGER PRIMARY KEY, animal_id INTEGER NOT NULL, filename TEXT NOT NULL, created_at TEXT NOT NULL, caption TEXT);
        CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY, username TEXT, action TEXT, detail TEXT, created_at TEXT, ip_address TEXT);
        CREATE TABLE IF NOT EXISTS settings(setting_key TEXT PRIMARY KEY, setting_value TEXT);
        ''')
        user_cols={r[1] for r in c.execute('pragma table_info(users)').fetchall()}
        for col,typ in [('full_name','TEXT'),('active','INTEGER DEFAULT 1'),('last_login','TEXT'),('password_changed_at','TEXT')]:
            if col not in user_cols:c.execute(f'ALTER TABLE users ADD COLUMN {col} {typ}')
        c.execute("update users set active=1 where active is null")
        c.execute("update users set full_name=username where full_name is null or trim(full_name)=''")
        c.execute("insert or ignore into settings(setting_key,setting_value) values('male_min_daily_gain','1.0')")
        c.execute("insert or ignore into settings(setting_key,setting_value) values('male_warning_ratio','0.90')")
        calf_cols={r[1] for r in c.execute('pragma table_info(calves)').fetchall()}
        if 'promoted_animal_id' not in calf_cols:c.execute('ALTER TABLE calves ADD COLUMN promoted_animal_id INTEGER')
        if 'promoted_at' not in calf_cols:c.execute('ALTER TABLE calves ADD COLUMN promoted_at TEXT')
        cols={r[1] for r in c.execute('pragma table_info(animals)').fetchall()}
        for col,typ in [('paddock','TEXT'),('photo_url','TEXT'),('sold_price','REAL DEFAULT 0'),('status',"TEXT DEFAULT 'Aktif'"),('exit_date','TEXT'),('exit_reason','TEXT'),('purchase_date','TEXT'),('purchase_price','REAL DEFAULT 0'),('purchase_weight','REAL DEFAULT 0'),('daily_feed_cost','REAL DEFAULT 0'),('daily_care_cost','REAL DEFAULT 0'),('target_sale_price','REAL DEFAULT 0')]:
            if col not in cols:c.execute(f'ALTER TABLE animals ADD COLUMN {col} {typ}')
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

def fmt_date(v):
    if not v:return ''
    try:return datetime.strptime(str(v)[:10],'%Y-%m-%d').strftime('%d/%m/%Y')
    except Exception:return str(v)

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

def animal_cost_values(a):
    purchase=float(a['purchase_price'] or 0) if 'purchase_price' in a.keys() else 0.0
    feed=float(a['daily_feed_cost'] or 0) if 'daily_feed_cost' in a.keys() else 0.0
    care=float(a['daily_care_cost'] or 0) if 'daily_care_cost' in a.keys() else 0.0
    start=(a['purchase_date'] if 'purchase_date' in a.keys() else '') or (a['birth_date'] if 'birth_date' in a.keys() else '')
    # Hayvan sürüden çıktıysa maliyet o tarihte donar; aktifse bugüne kadar yürür.
    status=str(a['status'] or 'Aktif') if 'status' in a.keys() else 'Aktif'
    exit_date=(a['exit_date'] if 'exit_date' in a.keys() else '') or ''
    try:
        start_date=date.fromisoformat(start)
        end_date=date.today()
        if status!='Aktif' and exit_date:
            end_date=min(date.today(),date.fromisoformat(exit_date))
        days=max(0,(end_date-start_date).days)
    except Exception:
        days=0
    daily=feed+care
    accumulated=days*daily
    return days,daily,accumulated,purchase+accumulated


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
    """10 ayını dolduran buzağıları cinsiyetine göre hayvan listesine geçirir."""
    with db() as c:
        rows=c.execute("select * from calves where promoted_animal_id is null and birth_date is not null and birth_date<>''").fetchall()
        for calf in rows:
            if months_old(calf['birth_date']) < 10:
                continue
            existing=c.execute('select id from animals where tag=?',(calf['tag'],)).fetchone()
            if existing:
                aid=existing['id']
            else:
                cur=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes,paddock,photo_url,sold_price,status) values(?,?,?,?,?,?,?,?,?,?)',
                    (calf['tag'],'',calf['gender'] or '', '', calf['birth_date'], calf['notes'] or '', '', '', 0, 'Aktif'))
                aid=cur.lastrowid
            c.execute('update calves set promoted_animal_id=?, promoted_at=? where id=?',(aid,datetime.now().isoformat(timespec='seconds'),calf['id']))

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
        ('🐂 Besi',[('Besi Performansı','/performance')]),
        ('🩺 Üreme & Sağlık',[('Kızgınlık Takibi','/estrus'),('Tohumlama','/inseminations'),('Sağlık','/health')]),
        ('💰 Finans',[('Finans','/finance'),('Raporlar','/reports')]),
        ('🗄️ Veri & Sistem',[('Veri Aktarımı','/data'),('💾 Yedekleme Merkezi','/backups')]),
        ('⚙️ Yönetim',[('🔐 Şifremi Değiştir','/password-change')]+([('🏡 Çiftlik Profili','/farm-profile'),('👥 Kullanıcı Yönetimi','/users'),('📜 İşlem Günlüğü','/audit-log')] if role=='admin' else []))
    ]
    nav=nav_link('🏠 Dashboard','/')
    for label,items in groups:
        active=any(path==url or (url=='/performance' and path.startswith('/performance')) for _,url in items)
        children=''.join(nav_link(name,url) for name,url in items)
        nav+=f'<details class="nav-group {"open-group" if active else ""}" {"open" if active else ""}><summary>{label}</summary><div class="nav-children">{children}</div></details>'
    fl=f'<div class="flash">{h(flash)}</div>' if flash else ''
    return f"""<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><style>{CSS}</style></head><body><div class="top"><div class="top-left"><button class="menu-toggle" id="menuToggle" aria-label="Menüyü aç">☰</button><a class="brand" href="/" title="Ana Sayfa">🐄 ÇiftlikPro</a></div><div class="top-user"><span class="ver">{APP_LABEL}</span> &nbsp; {h(display)} · <a href="/logout">Çıkış</a></div></div><div class="layout"><aside class="side" id="sideMenu">{nav}</aside><main class="main">{fl}{body}</main></div><script>
(function(){{
 const btn=document.getElementById("menuToggle"),side=document.getElementById("sideMenu");
 if(btn&&side){{btn.addEventListener("click",function(){{side.classList.toggle("mobile-open");}});side.querySelectorAll("a").forEach(function(a){{a.addEventListener("click",function(){{side.classList.remove("mobile-open");}});}});}}
 document.querySelectorAll(".nav-group").forEach(function(d){{d.addEventListener("toggle",function(){{if(!d.open)return;document.querySelectorAll(".nav-group").forEach(function(o){{if(o!==d)o.open=false;}});}});}});
 const c=document.getElementById("financeCategory"),a=document.getElementById("financeAnimal"),w=document.getElementById("statusWarning"),bulk=document.getElementById("bulkAnimalIds");if(c&&a&&w){{function x(){{const r=c.value==="Hayvan Satışı"||c.value==="Kesim Geliri";w.style.display=r?"block":"none";a.required=r&&!bulk;}}c.addEventListener("change",x);x();}}
}})();
function toggleAnimalFields(){{
 var type=document.getElementById('recordType');if(!type)return;var calf=type.value==='Buzağı';
 document.querySelectorAll('.calf-only').forEach(function(e){{e.style.display=calf?'block':'none';}});
 document.querySelectorAll('.adult-only').forEach(function(e){{e.style.display=calf?'none':'block';}});
 var badge=document.getElementById('recordTypeBadge');if(badge)badge.textContent=type.options[type.selectedIndex].text;
}}
function liveTableFilter(inputId,tableId,emptyId){{
 var input=document.getElementById(inputId),table=document.getElementById(tableId),empty=document.getElementById(emptyId);if(!input||!table)return;
 input.addEventListener('input',function(){{var q=(input.value||'').toLocaleLowerCase('tr-TR').trim(),visible=0;table.querySelectorAll('tbody tr.data-row').forEach(function(row){{var ok=!q||row.textContent.toLocaleLowerCase('tr-TR').includes(q);row.style.display=ok?'':'none';if(ok)visible++;}});if(empty)empty.style.display=visible?'none':'block';}});
}}
async function optimizePhotoFile(file,status,text,bar){{
 if(!file||!file.type||!file.type.startsWith('image/'))return file;
 const maxSide=1600,quality=.78;
 if(text)text.textContent='Fotoğraf hazırlanıyor…';if(status)status.classList.add('on');if(bar)bar.style.width='8%';
 try{{
   const bitmap=await createImageBitmap(file);
   let w=bitmap.width,h=bitmap.height,scale=Math.min(1,maxSide/Math.max(w,h));w=Math.max(1,Math.round(w*scale));h=Math.max(1,Math.round(h*scale));
   const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;const ctx=canvas.getContext('2d');ctx.drawImage(bitmap,0,0,w,h);if(bitmap.close)bitmap.close();
   if(bar)bar.style.width='22%';
   const blob=await new Promise(function(resolve){{canvas.toBlob(resolve,'image/jpeg',quality);}});
   if(!blob)throw new Error('Fotoğraf dönüştürülemedi');
   const base=(file.name||'hayvan').replace(/[.][^.]+$/,'');
   return new File([blob],base+'.jpg',{{type:'image/jpeg',lastModified:Date.now()}});
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
document.addEventListener('DOMContentLoaded',bindSmartPhotoForms);
</script></body></html>"""

def clean_text(v):
    if v is None:return ''
    t=str(v).strip()
    return '' if t.lower() in ('undefined','null','none') else t

def create_backup(label='manuel'):
    BACKUPS.mkdir(exist_ok=True);ts=datetime.now().strftime('%Y%m%d_%H%M%S')
    name=f'CiftlikPro_Backup_{label}_{ts}.zip';dst=BACKUPS/name;temp_db=BACKUPS/f'.snapshot_{ts}.db'
    with db() as src, sqlite3.connect(temp_db) as out:src.backup(out)
    manifest={'product':APP_NAME,'version':APP_VERSION,'created_at':datetime.now().isoformat(timespec='seconds'),'database':'ciftlik.db','includes_uploads':True,'label':label}
    try:
        with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(temp_db,'ciftlik.db');z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2))
            if UPLOADS.exists():
                for fp in UPLOADS.rglob('*'):
                    if fp.is_file():z.write(fp,'uploads/'+str(fp.relative_to(UPLOADS)).replace('\\','/'))
    finally:
        # Windows'ta SQLite/antivirüs dosya tanıtıcısını kısa süre açık tutabilir.
        # Yedek başarıyla oluştuysa geçici snapshot temizleme hatası uygulamayı durdurmamalı.
        gc.collect()
        for attempt in range(12):
            try:
                if temp_db.exists():
                    temp_db.unlink()
                break
            except PermissionError:
                if attempt == 11:
                    try:
                        stale = temp_db.with_name(temp_db.name + '.delete-later')
                        if stale.exists(): stale.unlink()
                        temp_db.replace(stale)
                    except Exception:
                        pass
                else:
                    time.sleep(0.25)
            except FileNotFoundError:
                break
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
        b=s.encode('utf-8'); self.send_response(status); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(b)))
        for k,v in (headers or []):self.send_header(k,v)
        self.end_headers(); self.wfile.write(b)
    def redirect(self,url,msg=''):
        if msg:url += ('&' if '?' in url else '?')+'msg='+urllib.parse.quote(msg)
        self.send_response(303);self.send_header('Location',url);self.end_headers()
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
        if path=='/login':
            return self.send_html(f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>{CSS}</style></head><body><div class="login"><h1>🐄 ÇiftlikPro</h1><p class="mut">{h(APP_LABEL)} • Güvenli Yedekleme ve Kullanıcı Yönetimi</p>{'<div class="flash err">'+h(msg)+'</div>' if msg else ''}<form method="post"><label>Kullanıcı adı</label><input name="username" required><label>Şifre</label><input type="password" name="password" required><button class="btn">Giriş Yap</button></form></div></body></html>''')
        if path.startswith('/uploads/'):
            name=os.path.basename(path.split('/uploads/',1)[1]); fp=UPLOADS/name
            if not fp.exists(): return self.send_html('Fotoğraf bulunamadı',404)
            ext=fp.suffix.lower(); ctype={'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp','gif':'image/gif'}.get(ext.lstrip('.'),'application/octet-stream')
            b=fp.read_bytes(); self.send_response(200); self.send_header('Content-Type',ctype); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        if path=='/logout':
            sid=self.parse_cookie(); SESSIONS.pop(sid,None); self.send_response(303);self.send_header('Set-Cookie','sid=; Max-Age=0; Path=/');self.send_header('Location','/login');self.end_headers();return
        if not self.require():return
        u=self.user()['username']
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
        if path=='/users':
            if not self.require_admin():return
            with db() as c:rows=c.execute('select id,username,full_name,role,active,last_login from users order by username').fetchall()
            trs=''.join(f'''<tr><td>{h(r["full_name"])}</td><td>{h(r["username"])}</td><td>{'Yönetici' if r["role"]=='admin' else 'Personel'}</td><td>{'Aktif' if r["active"] else 'Pasif'}</td><td>{h(r["last_login"]) or '-'}</td><td><a class="btn alt" href="/users/edit?id={r["id"]}">Düzenle</a></td></tr>''' for r in rows)
            body=f'''<h1>Kullanıcı Yönetimi</h1><div class="two"><div class="card"><h2>Yeni Kullanıcı</h2><form method="post" action="/users/create" class="form"><label>Ad Soyad<input name="full_name" required></label><label>Kullanıcı Adı<input name="username" required></label><label>Şifre<input type="password" name="password" minlength="8" required></label><label>Rol<select name="role"><option value="personel">Personel</option><option value="admin">Yönetici</option></select></label><div class="full"><button class="btn">Kullanıcı Oluştur</button></div></form></div><div class="card"><h2>Güvenlik</h2><p class="mut">Şifreler PBKDF2-SHA256 ile saklanır. Son aktif yönetici pasifleştirilemez.</p></div></div><div class="card" style="margin-top:14px"><table><tr><th>Ad Soyad</th><th>Kullanıcı</th><th>Rol</th><th>Durum</th><th>Son Giriş</th><th>İşlem</th></tr>{trs}</table></div>'''
            return self.send_html(page('Kullanıcı Yönetimi',body,'/users',u,msg))
        if path=='/users/edit':
            if not self.require_admin():return
            uid=q.get('id',[''])[0]
            with db() as c:r=c.execute('select * from users where id=?',(uid,)).fetchone()
            if not r:return self.send_html('Kullanıcı bulunamadı',404)
            body=f'''<h1>Kullanıcı Düzenle</h1><div class="card"><form method="post" action="/users/update" class="form"><input type="hidden" name="id" value="{r["id"]}"><label>Ad Soyad<input name="full_name" value="{h(r["full_name"])}" required></label><label>Rol<select name="role"><option value="personel" {'selected' if r["role"]=='personel' else ''}>Personel</option><option value="admin" {'selected' if r["role"]=='admin' else ''}>Yönetici</option></select></label><label>Durum<select name="active"><option value="1" {'selected' if r["active"] else ''}>Aktif</option><option value="0" {'selected' if not r["active"] else ''}>Pasif</option></select></label><label>Yeni Şifre<input type="password" name="new_password" minlength="8"></label><div class="full"><button class="btn">Kaydet</button> <a class="btn alt" href="/users">İptal</a></div></form></div>'''
            return self.send_html(page('Kullanıcı Düzenle',body,'/users',u,msg))
        if path=='/audit-log':
            if not self.require_admin():return
            with db() as c:rows=c.execute('select * from audit_log order by id desc limit 300').fetchall()
            trs=''.join(f'<tr><td>{h(r["created_at"])}</td><td>{h(r["username"])}</td><td>{h(r["action"])}</td><td>{h(r["detail"])}</td><td>{h(r["ip_address"])}</td></tr>' for r in rows) or '<tr><td colspan=5>Kayıt yok.</td></tr>'
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
                health_rows=c.execute("select h.next_date,a.id,a.tag,h.kind,h.product from health h left join animals a on a.id=h.animal_id where h.next_date between ? and ? order by h.next_date limit 8",(date.today().isoformat(),(date.today()+timedelta(days=30)).isoformat())).fetchall()
                pregnancy_vaccines=pregnancy_vaccine_tasks(c,horizon_days=7)
                estrus_dash_rows=c.execute("select e.*,a.tag,a.nickname from estrus_records e join animals a on a.id=e.animal_id where a.gender='Dişi' and coalesce(a.status,'Aktif')='Aktif' order by e.estrus_date desc,e.id desc").fetchall()
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
                if cycle and cycle['end']>=today and cycle['start']<=today+timedelta(days=14):
                    estrus_upcoming.append((cycle['start'],cycle['center'],cycle['end'],er,cycle['cycle_no']))
            estrus_upcoming.sort(key=lambda x:x[1])
            estrus_dashboard_cards=[]
            for es,ec,ee,er,cycle_no in estrus_upcoming[:8]:
                in_window=es<=today<=ee
                if in_window:
                    action=f'''<form method="post" action="/estrus-inseminate" onsubmit="return confirm('Bu hayvan bugün tohumlandı olarak Tohumlama kayıtlarına aktarılsın mı?')"><input type="hidden" name="estrus_id" value="{er['id']}"><button class="btn orange">🌱 Bugün Tohumlandı</button></form>'''
                else:
                    action=f'''<a class="btn orange" href="/inseminations?animal={er['animal_id']}&estrus={er['id']}">🌱 Tohumlamaya Gönder</a>'''
                estrus_dashboard_cards.append(f'''<div class="alertitem {'estrus-window-now' if in_window else 'estrus-window-next'}"><b>🌸 <a class="taglink" href="/animal?id={er['animal_id']}">{h(er['tag'])} {h(er['nickname'])}</a></b><br><span class="mut">{fmt_date(es.isoformat())} – {fmt_date(ee.isoformat())} · En olası {fmt_date(ec.isoformat())}</span><div class="estrus-actions">{action}<form method="post" action="/estrus-skip" onsubmit="return confirm('Bu östrus dönemi atlandı olarak işaretlenecek. Emin misiniz?')"><input type="hidden" name="estrus_id" value="{er['id']}"><input type="hidden" name="cycle_no" value="{cycle_no}"><input type="hidden" name="return_to" value="/"><button class="btn alt">⏭️ Bu Östrusu Atla</button></form><a class="btn alt" href="/estrus">Kızgınlık Takibi</a></div></div>''')
            estrus_dashboard_html=''.join(estrus_dashboard_cards) or '<p class="mut">Önümüzdeki 14 gün için beklenen kızgınlık yok.</p>'
            net=total_inc-total_exp; maxv=max([max(x[1],x[2]) for x in months]+[1])
            bars=''.join(f'<div class="mini-col"><b title="Gelir {money(i)}" style="height:{max(2,int(i/maxv*100))}%"></b><i title="Gider {money(e)}" style="height:{max(2,int(e/maxv*100))}%"></i><span>{h(m)}</span></div>' for m,i,e in months)
            due_html=''.join(f'<div class="alertitem">🐄 <a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])} {h(r["nickname"])}</a><br><span class="mut">Tahmini doğum: {h(r["due_date"])}</span></div>' for r in due_rows) or '<p class="mut">45 gün içinde beklenen doğum yok.</p>'
            health_html=''.join(f'<div class="alertitem">💉 {h(r["tag"] or "Genel")} · {h(r["kind"])}<br><span class="mut">{h(r["product"])} — {h(r["next_date"])}</span></div>' for r in health_rows) or '<p class="mut">30 gün içinde planlanan sağlık işlemi yok.</p>'
            def vaccine_task_html(t):
                if t['overdue']:
                    label=f"GECİKTİ · {abs(t['days_left'])} gün"; style='border-left-color:#c8392b;background:#fff1f0'
                elif t['today']:
                    label='BUGÜN YAPILMALI'; style='border-left-color:#e27b1f;background:#fff6e8'
                else:
                    label=f"{t['days_left']} gün kaldı"; style='border-left-color:#e2a21f;background:#fff9e8'
                return f'<div class="alertitem" style="{style}"><b>💉 {h(t["tag"])} · {t["month"]}. Ay Gebelik Aşısı</b><br><span class="mut">Planlanan: {h(t["task_date"])} · {label}</span><form method="post" action="/pregnancy-vaccine/done" class="actions" style="margin-top:8px"><input type="hidden" name="animal_id" value="{t["animal_id"]}"><input type="hidden" name="insemination_id" value="{t["insemination_id"]}"><input type="hidden" name="month" value="{t["month"]}"><input type="hidden" name="return_to" value="/"><button class="btn">✅ Aşı Yapıldı</button><a class="btn alt" href="/animal?id={t["animal_id"]}">Hayvanı Aç</a></form></div>'
            pregnancy_vaccine_html=''.join(vaccine_task_html(t) for t in pregnancy_vaccines) or '<p class="mut">7 gün içinde 7./8. ay gebelik aşısı görevi yok.</p>'
            target_profit_text=money(male_target_profit) if male_target_profit is not None else '—'
            target_profit_class='red' if male_target_profit is not None and male_target_profit<0 else 'green'
            target_profit_color='#c8392b' if male_target_profit is not None and male_target_profit<0 else '#176b3a'
            performance_warning_html=''.join(f'<div class="alertitem" style="border-left-color:#c8392b">⚠️ <a class="taglink" href="/animal?id={r[0]["id"]}">{h(r[0]["tag"])} {h(r[0]["nickname"])}</a><br><span class="mut">{r[1]["daily"]:.3f} kg/gün · Hedef {min_daily_gain:.2f} kg/gün</span></div>' for r in low_performance[:8]) or '<p class="mut">Kritik seviyede düşük kilo artışı olan erkek yok.</p>'
            dash_cards={
                'active_total':f'<a class="card stat metric green summary-link" href="/animals"><span class="metric-icon">🐄</span>Toplam Aktif Hayvan<b>{active_total}</b><small>Dişi hayvanları aç →</small></a>',
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
            option_html=''.join(f'<option value="{h(k)}">{h(label)}</option>' for k,label in DASHBOARD_CARD_OPTIONS)
            dash_slots=[]
            for slot,key in enumerate(dash_layout):
                card=dash_cards.get(key,'')
                if not card:
                    card='<div class="dashboard-empty-slot"><div>＋<small>Bu yuvaya kart ekle</small></div></div>'
                if edit_dashboard:
                    selected_opts=''.join(f'<option value="{h(k)}" {"selected" if k==key else ""}>{h(label)}</option>' for k,label in DASHBOARD_CARD_OPTIONS)
                    editor=f'''<div class="dashboard-slot-editor"><form method="post" action="/dashboard-layout"><input type="hidden" name="slot" value="{slot}"><select name="card_key"><option value="">＋ Boş bırak</option>{selected_opts}</select><button class="btn">Uygula</button></form></div>'''
                else:
                    editor=''
                dash_slots.append(f'<div class="dashboard-slot">{card}{editor}</div>')
            dashboard_summary_html=''.join(dash_slots)
            dashboard_logo=(f'<img class="farm-hero-logo" src="{h(profile.get("farm_logo"))}" alt="Çiftlik logosu">' if profile.get('farm_logo') else '')
            body=f'''<div class="hero"><div class="farm-hero">{dashboard_logo}<div><h1>{h(farm_name)}</h1><div>ÇiftlikPro · Bugünün sürü, sağlık ve finans görünümü</div></div></div><div><a class="btn orange" href="/backup/create">💾 Hemen Yedek Al</a></div></div>
            <div class="dashboard-editbar"><a class="btn alt" href="/{'?' if edit_dashboard else '?edit=1'}">{'✅ Düzenlemeyi Bitir' if edit_dashboard else '⚙️ Dashboard’u Düzenle'}</a></div>
            <div class="dashboard-section-title"><h2>Dashboard Kartlarım</h2><span>{'Her yuvada göstermek istediğiniz kartı seçin' if edit_dashboard else 'Size özel hızlı görünüm'}</span></div>
            <div class="grid summary-grid">{dashboard_summary_html}</div>
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
                return f'<tr><td><a class="taglink" href="/animal?id={r["id"]}">{h(r["tag"])}</a><br><span class="mut">{h(r["nickname"])}</span></td><td>{badge}</td><td>{h(start)}</td><td>{h(end)}</td><td><b>{days} gün</b>{note}</td><td>{money(purchase)}</td><td>{money(operating)}</td><td><b>{money(total)}</b></td></tr>'
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
        if path=='/performance':
            status_filter=(q.get('status',[''])[0] or '').strip()
            scope=(q.get('scope',['all'])[0] or 'all').strip()
            if scope not in ('all','active','cut'): scope='all'
            purchase_start=(q.get('purchase_start',[''])[0] or '').strip()
            purchase_end=(q.get('purchase_end',[''])[0] or '').strip()
            cut_start=(q.get('cut_start',[''])[0] or '').strip()
            cut_end=(q.get('cut_end',[''])[0] or '').strip()
            with db() as c:
                males_rows=c.execute("select * from animals where gender='Erkek' and coalesce(status,'Aktif') in ('Aktif','Kesildi') order by tag").fetchall()
                selected=[]
                for ar in males_rows:
                    st=str(ar['status'] or 'Aktif')
                    if scope=='active' and st!='Aktif': continue
                    if scope=='cut' and st!='Kesildi': continue
                    pd=(ar['purchase_date'] or '') if 'purchase_date' in ar.keys() else ''
                    ed=(ar['exit_date'] or '') if 'exit_date' in ar.keys() else ''
                    if purchase_start and (not pd or pd<purchase_start): continue
                    if purchase_end and (not pd or pd>purchase_end): continue
                    if cut_start and (st!='Kesildi' or not ed or ed<cut_start): continue
                    if cut_end and (st!='Kesildi' or not ed or ed>cut_end): continue
                    perf=male_weight_performance(ar['id'],c)
                    if status_filter and perf['status']!=status_filter: continue
                    selected.append((ar,perf))
                detail=[]
                for ar,perf in selected:
                    wr=c.execute("select measure_date,weight from weights where animal_id=? order by measure_date,id",(ar['id'],)).fetchall()
                    first=wr[0] if wr else None; last=wr[-1] if wr else None
                    total_gain=(float(last['weight'])-float(first['weight'])) if first and last and len(wr)>=2 else None
                    days,daily,operating,total_cost=animal_cost_values(ar)
                    kg_cost=(operating/total_gain) if total_gain is not None and total_gain>0 else None
                    detail.append((ar,perf,days,operating,total_cost,total_gain,kg_cost,first,last))
            active_count=sum(1 for ar,*_ in detail if str(ar['status'] or 'Aktif')=='Aktif')
            cut_count=sum(1 for ar,*_ in detail if str(ar['status'] or '')=='Kesildi')
            purchase_total=sum(float(ar['purchase_price'] or 0) for ar,*_ in detail)
            operating_total=sum(x[3] for x in detail)
            total_cost=sum(x[4] for x in detail)
            daily_vals=[perf['daily'] for _,perf,*_ in detail if perf.get('daily') is not None]
            avg_daily=(sum(daily_vals)/len(daily_vals)) if daily_vals else None
            kg_cost_vals=[x[6] for x in detail if x[6] is not None]
            avg_kg_cost=(sum(kg_cost_vals)/len(kg_cost_vals)) if kg_cost_vals else None
            labels={'good':('Hedefte','status-good'),'watch':('Takip','status-watch'),'low':('Düşük','status-low'),'none':('Veri Yetersiz','status-none')}
            trs=''
            for ar,perf,days,operating,current_cost,total_gain,kg_cost,first,last in detail:
                label,cls=labels[perf['status']]
                st=str(ar['status'] or 'Aktif')
                pd=h(ar['purchase_date'] or '-'); ed=h(ar['exit_date'] or '-') if st=='Kesildi' else 'Devam ediyor'
                gain_text=(f'{total_gain:+.1f} kg' if total_gain is not None else '-')
                daily_text=(f"{perf['daily']:.3f} kg/gün" if perf.get('daily') is not None else '-')
                kgcost_text=(money(kg_cost)+'/kg' if kg_cost is not None else '-')
                trs+=f"""<tr><td><a class="taglink" href="/animal?id={ar["id"]}">{h(ar["tag"])}</a></td><td>{h(ar["nickname"])}</td><td>{st}</td><td>{pd}</td><td>{ed}</td><td>{days}</td><td>{gain_text}</td><td>{daily_text}</td><td>{money(operating)}</td><td>{kgcost_text}</td><td>{money(current_cost)}</td><td><span class="perf-badge {cls}">{label}</span></td></tr>"""
            trs=trs or '<tr><td colspan="12">Seçilen tarih ve filtrelerde hayvan bulunamadı.</td></tr>'
            avg_daily_text=f'{avg_daily:.3f} kg/gün' if avg_daily is not None else '—'
            avg_kg_text=(money(avg_kg_cost)+'/kg') if avg_kg_cost is not None else '—'
            body=f"""<div class="actions"><h1 style="margin-right:auto">🐂 Besi Analiz Merkezi</h1><a class="btn alt" href="/performance-settings">⚙️ Performans Eşiği</a></div>
            <div class="card"><h2>Analiz Aralığı</h2><form method="get" action="/performance" class="form">
            <label>Hayvan Durumu<select name="scope"><option value="all" {'selected' if scope=='all' else ''}>Aktif + Kesilen</option><option value="active" {'selected' if scope=='active' else ''}>Sadece Aktif</option><option value="cut" {'selected' if scope=='cut' else ''}>Sadece Kesilen</option></select></label>
            <label>Alım Tarihi Başlangıç<input type="date" name="purchase_start" value="{h(purchase_start)}"></label><label>Alım Tarihi Bitiş<input type="date" name="purchase_end" value="{h(purchase_end)}"></label>
            <label>Kesim Tarihi Başlangıç<input type="date" name="cut_start" value="{h(cut_start)}"></label><label>Kesim Tarihi Bitiş<input type="date" name="cut_end" value="{h(cut_end)}"></label>
            <label>Performans<select name="status"><option value="">Tümü</option><option value="good" {'selected' if status_filter=='good' else ''}>Hedefte</option><option value="watch" {'selected' if status_filter=='watch' else ''}>Takip</option><option value="low" {'selected' if status_filter=='low' else ''}>Düşük</option><option value="none" {'selected' if status_filter=='none' else ''}>Veri Yetersiz</option></select></label>
            <button class="btn blue">Raporla</button><a class="btn alt" href="/performance">Filtreleri Temizle</a></form></div>
            <div class="grid" style="margin-top:14px"><div class="card stat metric blue">Seçilen Hayvan<b>{len(detail)}</b><small>{active_count} aktif · {cut_count} kesilen</small></div><div class="card stat metric green">Gerçekleşmiş Maliyet<b>{money(total_cost)}</b><small>Alış {money(purchase_total)} · Yem/Bakım {money(operating_total)}</small></div><div class="card stat metric orange">Ort. Günlük Artış<b>{avg_daily_text}</b><small>Son iki tartısı olan hayvanlar</small></div><div class="card stat metric purple">Ort. 1 kg Artış Maliyeti<b>{avg_kg_text}</b><small>Tartı verisi yeterli hayvanlar</small></div></div>
            <div class="card" style="margin-top:14px"><h2>Hayvan Bazında Analiz</h2><p class="mut">Kesilen hayvanın maliyeti kesim tarihinde donar. 1 kg artış maliyeti, ilk-son tartı farkına karşı oluşan yem/bakım giderini gösterir.</p><div style="overflow:auto"><table class="performance-table"><tr><th>Küpe</th><th>Takma Ad</th><th>Durum</th><th>Alım</th><th>Kesim</th><th>Maliyet Günü</th><th>Toplam Kilo Artışı</th><th>Son Dönem Günlük</th><th>Yem/Bakım</th><th>1 kg Artış Maliyeti</th><th>Toplam Maliyet</th><th>Performans</th></tr>{trs}</table></div></div>"""
            return self.send_html(page('Besi Analiz Merkezi',body,path,u,msg))
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
            body=f'''<h1>Buzağı Düzenle</h1><div class="card"><form method="post" action="/calf-edit" class="form"><input type="hidden" name="id" value="{rec["id"]}"><label>Buzağı Küpesi<input name="tag" required value="{h(rec["tag"])}"></label><label>Anne<select name="mother_id" required>{opts}</select></label><label>Baba Küpesi<input name="father_tag" value="{h(rec["father_tag"])}"></label><label>Doğum Tarihi<input type="date" name="birth_date" required value="{h(rec["birth_date"])}"></label><label>Cinsiyet<select name="gender"><option value="Dişi" {'selected' if rec["gender"]=='Dişi' else ''}>Dişi</option><option value="Erkek" {'selected' if rec["gender"]=='Erkek' else ''}>Erkek</option></select></label><label class="full">Not<textarea name="notes">{h(rec["notes"])}</textarea></label><div class="full"><button class="btn">Buzağıyı Güncelle</button> <a class="btn alt" href="/calves">İptal</a></div></form></div>'''
            return self.send_html(page('Buzağı Düzenle',body,'/calves',u,msg))
        if path=='/animal-add':
            with db() as c:
                mothers=c.execute("select tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                breeds=[r[0] for r in c.execute("select distinct breed from animals where trim(coalesce(breed,''))<>'' order by breed").fetchall()]
                paddocks=[r[0] for r in c.execute("select distinct paddock from animals where trim(coalesce(paddock,''))<>'' order by paddock").fetchall()]
            mother_options=''.join(f'<option value="{h(r["tag"])}">{h(r["nickname"])}</option>' for r in mothers)
            breed_options=''.join(f'<option value="{h(x)}">' for x in breeds)
            paddock_options=''.join(f'<option value="{h(x)}">' for x in paddocks)
            body=f'''<div class="pro-form-head"><div><h1>Hayvan Ekle</h1><div class="mut">Tek formdan dişi, erkek veya buzağı kaydı oluşturun.</div></div><span id="recordTypeBadge" class="type-chip">Dişi Hayvan</span></div><div class="card"><form method="post" action="/animal-add" enctype="multipart/form-data" class="form" data-smart-photo-form="1"><label>Kayıt Türü<select id="recordType" name="record_type" required onchange="toggleAnimalFields()"><option value="Dişi">Dişi Hayvan</option><option value="Erkek">Erkek Hayvan</option><option value="Buzağı">Buzağı</option></select></label><label>Küpe No<input name="tag" required autocomplete="off"></label><label>Takma Ad<input name="nickname"></label><label class="adult-only">Irk<input name="breed" list="breedOptions"><datalist id="breedOptions">{breed_options}</datalist></label><label>Doğum Tarihi<input type="date" name="birth_date"></label><label class="adult-only">Padok / Ahır<input name="paddock" list="paddockOptions"><datalist id="paddockOptions">{paddock_options}</datalist></label><label class="adult-only">Fotoğraf Yükle / Kameradan veya Galeriden Seç<input type="file" name="photo_file" accept="image/*"><span class="camera-note">Telefonda kamera veya galeriden seçim yapabilirsiniz. Büyük fotoğraflar otomatik küçültülür.</span><div class="photo-upload-status" data-upload-status><span data-upload-text>Fotoğraf hazırlanıyor…</span><div class="upload-progress"><div class="upload-progress-bar" data-upload-bar></div></div></div></label><label class="male-only" style="display:none">Alış Tarihi<input type="date" name="purchase_date"></label><label class="male-only" style="display:none">Alış Fiyatı (TL)<input type="number" min="0" step="0.01" name="purchase_price"></label><label class="male-only" style="display:none">Alış Kilosu (kg)<input type="number" min="0" step="0.1" name="purchase_weight"></label><label class="male-only" style="display:none">Günlük Yem/Rasyon (TL)<input type="number" min="0" step="0.01" name="daily_feed_cost"></label><label class="male-only" style="display:none">Günlük Bakım (TL)<input type="number" min="0" step="0.01" name="daily_care_cost"></label><label class="male-only" style="display:none">Hedef Satış Fiyatı (TL)<input type="number" min="0" step="0.01" name="target_sale_price"></label><label class="calf-only" style="display:none">Buzağı Cinsiyeti<select name="calf_gender"><option>Dişi</option><option>Erkek</option></select></label><label class="calf-only" style="display:none">Anne Küpesi<input name="mother_tag" list="motherTagOptions"><datalist id="motherTagOptions">{mother_options}</datalist></label><label class="calf-only" style="display:none">Baba Küpesi<input name="father_tag"></label><label class="full">Not<textarea name="notes"></textarea></label><div class="full"><button class="btn">Kaydı Oluştur</button> <a class="btn alt" href="/">İptal</a></div></form></div><script>document.addEventListener('DOMContentLoaded',function(){{toggleAnimalFields();}});</script>'''
            return self.send_html(page('Hayvan Ekle',body,'/animal-add',u,msg))

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
                f'<td>{h(r["exit_date"])}</td><td>{h(r["exit_reason"])}</td><td>{money(r["sold_price"])}</td></tr>'
                for r in rows
            ) or '<tr><td colspan=7>Kayıt yok.</td></tr>'
            body=f'<h1>{title}</h1><div class="card"><p class="mut">Bu hayvanların geçmiş kayıtları silinmez; yalnızca aktif sürü listesinden çıkarılır.</p><table><tr><th>Küpe</th><th>Takma Ad</th><th>Cinsiyet</th><th>Irk</th><th>Çıkış Tarihi</th><th>Neden</th><th>Satış/Kesim Tutarı</th></tr>{trs}</table></div>'
            return self.send_html(page(title,body,path,u,msg))
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
            preg=(latest['pregnancy_result'] if latest else 'Kayıt yok'); due=(latest['due_date'] if latest else '')
            cls='pos' if preg=='Pozitif' else 'neg' if preg=='Negatif' else ''
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
            target_profit=float(a['target_sale_price'] or 0)-current_cost if float(a['target_sale_price'] or 0)>0 else None
            period_perf=male_weight_performance(aid) if a['gender']=='Erkek' else None
            perf_labels={'good':('Hedefte / Üstünde','status-good'),'watch':('Takip Edilmeli','status-watch'),'low':('Düşük Artış','status-low'),'none':('Veri Yetersiz','status-none')}
            perf_label,perf_class=perf_labels[period_perf['status']] if period_perf else ('','')
            chart_html=weight_chart_svg(list(reversed(weights))) if a['gender']=='Erkek' else ''
            purchase_summary=(f'<div class="costbox"><h3>Canlı Anlık Maliyet ve Performans</h3><div class="quick-metrics"><span class="pill">Alış Fiyatı<br><b>{money(a["purchase_price"])}</b></span><span class="pill">Bizde Kaldığı Süre<br><b>{stay_days} gün</b></span><span class="pill">Birikmiş Yem + Bakım<br><b>{money(accumulated_cost)}</b></span><span class="pill">Anlık Toplam Maliyet<br><b>{money(current_cost)}</b></span><span class="pill">Toplam Kilo Artışı<br><b>{(str(round(weight_gain,1))+" kg") if weight_gain is not None else "-"}</b></span><span class="pill">Günlük Kilo Artışı<br><b>{(str(round(daily_gain,3))+" kg/gün") if daily_gain is not None else "-"}</b></span><span class="pill">Hedef Satış<br><b>{money(a["target_sale_price"]) if float(a["target_sale_price"] or 0)>0 else "-"}</b></span><span class="pill">Hedef Kâr<br><b>{money(target_profit) if target_profit is not None else "-"}</b></span></div><p class="mut">Günlük yem/rasyon: {money(a["daily_feed_cost"])} · Günlük bakım: {money(a["daily_care_cost"])} · Günlük toplam: {money(daily_cost)}</p></div>') if a['gender']=='Erkek' else ''
            sale_box=(f'<div class="card" style="margin-top:14px"><h2>Erkek Hayvan Satışı</h2><p class="mut">Satış kaydı oluşturulduğunda hayvan Satılan Hayvanlar arşivine alınır ve net kâr otomatik hesaplanır.</p><form method="post" action="/animal/sale" class="form" onsubmit="return confirm(\'Bu hayvanı satıldı olarak işaretlemek istediğinize emin misiniz?\')"><input type="hidden" name="animal_id" value="{aid}"><label>Satış Tarihi<input type="date" name="sale_date" required value="{date.today().isoformat()}"></label><label>Satış Fiyatı (TL)<input type="number" name="sale_price" min="0" step="0.01" required value="{h(a["target_sale_price"])}"></label><label>Satış Kilosu (kg)<input type="number" name="sale_weight" min="0" step="0.1" value="{h(latest_weight)}"></label><label>Alıcı / Açıklama<input name="description"></label><div class="full"><button class="btn orange">Satışı Tamamla</button></div></form></div>') if a['gender']=='Erkek' and a['status']=='Aktif' else ''
            photo=f'<img class="photo" src="{h(a["photo_url"])}">' if a['photo_url'] else '<div class="photo">🐄</div>'
            gallery=''.join(f'<figure><img src="/uploads/{h(r["filename"])}"><figcaption>{h(r["caption"])}<br>{h(r["created_at"])}</figcaption></figure>' for r in photos) or '<p class="mut">Henüz fotoğraf yüklenmedi.</p>'
            itr=''.join(f'<tr><td>{r["attempt"]}</td><td>{h(r["insemination_date"])}</td><td>{h(r["pregnancy_result"])}</td><td>{h(r["due_date"])}</td></tr>' for r in ins) or '<tr><td colspan=4>Kayıt yok</td></tr>'
            htr=''.join(f'<tr><td>{h(r["applied_date"])}</td><td>{h(r["kind"])}</td><td>{h(r["product"])}</td><td>{money(r["cost"])}</td></tr>' for r in health) or '<tr><td colspan=4>Kayıt yok</td></tr>'
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
                wrows.append(f'<tr><td>{h(r["measure_date"])}</td><td>{r["weight"]} kg</td><td>{gain_txt}</td><td>{daily_txt}</td><td>{monthly_txt}</td><td>{h(r["notes"])}</td></tr>')
            wtr=''.join(reversed(wrows)) or '<tr><td colspan=6>Kayıt yok</td></tr>'
            mtr=''.join(f'<tr><td>{h(r["measure_date"])}</td><td>{r["liters"]} L</td><td>{h(r["notes"])}</td></tr>' for r in milk) or '<tr><td colspan=3>Kayıt yok</td></tr>'
            ctr=''.join(f'<tr><td>{h(r["tag"])}</td><td>{h(r["birth_date"])}</td><td>{h(r["gender"])}</td></tr>' for r in calves) or '<tr><td colspan=3>Kayıt yok</td></tr>'
            back='/males' if a['gender']=='Erkek' else '/animals'; edit_url='/animal-edit?id='+str(aid)
            body=f'''<div class="actions"><a class="btn alt" href="{back}">← Hayvanlara Dön</a><a class="btn" href="{edit_url}">Bilgileri Düzenle</a><a class="btn blue" href="/animal/print?id={aid}">Kimlik Kartını Yazdır</a></div><div class="card profile">{photo}<div><h1>{h(a['tag'])}</h1><h2>{h(a['nickname'])}</h2><span class="pill">{h(a['gender'])}</span><span class="pill">{h(a['breed'])}</span><span class="pill">Padok: {h(a['paddock']) or '-'}</span><span class="pill">Durum: {h(a['status'])}</span><p class="preg {cls}">Gebelik: {h(preg)} {('· Tahmini doğum '+h(due)) if due else ''}</p><div class="quick-metrics"><span class="pill">Yaş<br><b>{age_text(a['birth_date'])}</b></span><span class="pill">Son Kilo<br><b>{(str(latest_weight)+' kg') if latest_weight is not None else '-'}</b></span><span class="pill">Son Süt<br><b>{(str(latest_milk)+' L') if latest_milk is not None else '-'}</b></span><span class="pill">Net Değer<br><b>{money(net_value)}</b></span></div><p>Toplam masraf: <b>{money(total_cost)}</b> · Buzağı: <b>{len(calves)}</b></p>{purchase_summary}<p>{h(a['notes'])}</p></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>Tohumlama ve Gebelik</h2><table><tr><th>Deneme</th><th>Tarih</th><th>Sonuç</th><th>Tahmini Doğum</th></tr>{itr}</table></div><div class="card"><h2>Buzağıları</h2><table><tr><th>Küpe</th><th>Doğum</th><th>Cinsiyet</th></tr>{ctr}</table></div></div><div class="two" style="margin-top:14px"><div class="card"><h2>{'Aylık Tartım ve Besi Performansı' if a['gender']=='Erkek' else 'Kilo Geçmişi'}</h2>{(f'<div class="costbox"><span class="perf-badge {perf_class}">{perf_label}</span><div class="quick-metrics"><span class="pill">Son Dönem Artışı<br><b>{period_perf["gain"]:+.1f} kg</b></span><span class="pill">Tartım Aralığı<br><b>{period_perf["days"]} gün</b></span><span class="pill">Günlük Artış<br><b>{period_perf["daily"]:.3f} kg/gün</b></span><span class="pill">30 Günlük Tahmin<br><b>{period_perf["monthly"]:.1f} kg</b></span></div></div>' if period_perf and period_perf['daily'] is not None else '<p class="mut">Performans hesabı için en az iki tartım girin.</p>') if a['gender']=='Erkek' else ''}<form method="post" action="/animal/weight" class="actions"><input type="hidden" name="animal_id" value="{aid}"><input type="date" name="measure_date" required value="{date.today().isoformat()}"><input type="number" step="0.1" name="weight" placeholder="kg" required><input name="notes" placeholder="Not"><button class="btn">Tartım Ekle</button></form>{chart_html}<table style="margin-top:12px"><tr><th>Tarih</th><th>Kilo</th><th>Fark</th><th>Günlük Artış</th><th>30 Günlük</th><th>Not</th></tr>{wtr}</table></div><div class="card"><h2>Süt Verimi</h2><form method="post" action="/animal/milk" class="actions"><input type="hidden" name="animal_id" value="{aid}"><input type="date" name="measure_date" required value="{date.today().isoformat()}"><input type="number" step="0.1" name="liters" placeholder="Litre" required><input name="notes" placeholder="Not"><button class="btn">Ekle</button></form><table><tr><th>Tarih</th><th>Litre</th><th>Not</th></tr>{mtr}</table></div></div>{sale_box}<div class="card" style="margin-top:14px"><h2>Fotoğraf Galerisi</h2><form method="post" action="/animal/photo" enctype="multipart/form-data" class="uploadbox"><input type="hidden" name="animal_id" value="{aid}"><label>Fotoğraf seç veya telefondan çek<input type="file" name="photo_file" accept="image/*" required></label><input name="caption" placeholder="Açıklama (isteğe bağlı)"><button class="btn">Fotoğrafı Yükle</button><div class="camera-note">Mobil tarayıcıda arka kamera açılır. Fotoğraflar uygulama klasöründeki uploads dizininde saklanır; bu klasörü de düzenli kopyalayın.</div></form><div class="gallery" style="margin-top:14px">{gallery}</div></div><div class="card" style="margin-top:14px"><h2>Sağlık Geçmişi</h2><table><tr><th>Tarih</th><th>Tür</th><th>İşlem</th><th>Maliyet</th></tr>{htr}</table></div>'''
            return self.send_html(page('Hayvan Kartı',body,'/animals',u,msg))
        if path=='/animal/print':
            aid=q.get('id',[''])[0]
            with db() as c:a=c.execute('select * from animals where id=?',(aid,)).fetchone(); ins=c.execute('select * from inseminations where animal_id=? order by attempt',(aid,)).fetchall()
            if not a:return self.send_html('Hayvan bulunamadı',404)
            latest=ins[-1] if ins else None
            return self.send_html(f'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><title>ÇiftlikPro Hayvan Kartı</title><style>body{{font-family:Arial;padding:30px}}.box{{border:2px solid #176b3a;border-radius:16px;padding:24px;max-width:700px}}h1{{color:#176b3a}}table{{width:100%;border-collapse:collapse}}td{{padding:8px;border-bottom:1px solid #ddd}}@media print{{button{{display:none}}}}</style></head><body><button onclick="print()">Yazdır / PDF Kaydet</button><div class="box"><h1>🐄 ÇiftlikPro Hayvan Kimlik Kartı</h1><table><tr><td>Küpe</td><td><b>{h(a['tag'])}</b></td></tr><tr><td>Takma Ad</td><td>{h(a['nickname'])}</td></tr><tr><td>Cinsiyet / Irk</td><td>{h(a['gender'])} / {h(a['breed'])}</td></tr><tr><td>Doğum / Yaş</td><td>{h(a['birth_date'])} / {age_text(a['birth_date'])}</td></tr><tr><td>Padok</td><td>{h(a['paddock'])}</td></tr><tr><td>Gebelik</td><td>{h(latest['pregnancy_result'] if latest else 'Kayıt yok')}</td></tr><tr><td>Tahmini Doğum</td><td>{h(latest['due_date'] if latest else '')}</td></tr><tr><td>Not</td><td>{h(a['notes'])}</td></tr></table></div></body></html>''')
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
            promoted=''
            if calf['promoted_animal_id']:
                promoted=f'<p class="flash">Bu kayıt 10 ayını doldurduğu için hayvan listesine aktarıldı. <a class="taglink" href="/animal?id={calf["promoted_animal_id"]}">Yeni hayvan kartını aç</a></p>'
            icon='🐮' if calf['gender']=='Dişi' else '🐂'
            body=f'''<div class="actions"><a class="btn alt" href="/calves">← Buzağılara Dön</a><a class="btn" href="/calf-edit?id={cid}">Düzenle</a></div>{promoted}<div class="card profile"><div class="photo">{icon}</div><div><h1>{h(calf['tag'])}</h1><span class="pill">{h(calf['gender'])}</span><span class="pill">Yaş: {age_text(calf['birth_date'])}</span><p>Doğum tarihi: <b>{h(calf['birth_date'])}</b></p><p>Anne: <a class="taglink" href="/animal?id={calf['mother_id']}">{h(calf['mother_tag'])} {h(calf['mother_name'])}</a></p><p>Baba: <b>{h(calf['father_tag']) or '-'}</b></p><p>{h(calf['notes'])}</p></div></div>'''
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
                females=c.execute("select id,tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                rows=c.execute("select e.*,a.tag,a.nickname from estrus_records e join animals a on a.id=e.animal_id order by e.estrus_date desc,e.id desc").fetchall()
                latest={}
                for r in rows:
                    if r['animal_id'] not in latest: latest[r['animal_id']]=r
            today=date.today(); upcoming=[]
            with db() as c:
                for aid,r in latest.items():
                    cycle=next_estrus_cycle(c,r,today)
                    if cycle and cycle['end']>=today and cycle['start']<=today+timedelta(days=14):
                        upcoming.append((cycle['start'],cycle['center'],cycle['end'],r,cycle['cycle_no']))
            upcoming.sort(key=lambda x:x[1])
            opts=''.join(f'<option value="{r["id"]}">{h(r["tag"])}{(" · "+h(r["nickname"])) if r["nickname"] else ""}</option>' for r in females)
            cards=[]
            for a,center,e,r,cycle_no in upcoming:
                color='#e27b1f' if a<=today<=e else '#238a50'
                if a<=today<=e:
                    action=f'''<form method="post" action="/estrus-inseminate" onsubmit="return confirm('Bu hayvan bugün tohumlandı olarak Tohumlama kayıtlarına aktarılsın mı?')"><input type="hidden" name="estrus_id" value="{r['id']}"><button class="btn orange">🌱 Bugün Tohumlandı</button></form>'''
                else:
                    action=f'''<a class="btn orange" href="/inseminations?animal={r['animal_id']}&estrus={r['id']}">🌱 Tohumlamaya Gönder</a><span class="mut" style="align-self:center">Pencere {fmt_date(a.isoformat())} tarihinde başlıyor</span>'''
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
            <div class="two"><div class="card"><h2>Yeni Kızgınlık Kaydı</h2><form method="post" action="/estrus" class="form" onsubmit="var b=this.querySelector('button[type=submit]');if(b.disabled)return false;b.disabled=true;b.textContent='Kaydediliyor…';return true;"><label>Dişi Hayvan<select name="animal_id" required><option value="">Seçin</option>{opts}</select></label><label>Kızgınlık Tarihi<input type="date" name="estrus_date" max="{today.isoformat()}" value="{today.isoformat()}" required></label><label class="full">Gözlenen Belirtiler<input name="signs" placeholder="Örn. üzerine atlamaya izin verme, huzursuzluk, şeffaf akıntı"></label><label class="full">Not<textarea name="notes" rows="3" placeholder="Ek gözlemler..."></textarea></label><div class="full"><button class="btn">💾 Kızgınlığı Kaydet</button></div></form></div><div class="card"><h2>📅 Yaklaşan Kızgınlıklar</h2>{cards_html}</div></div>
            <div class="card" style="margin-top:14px"><h2>Kızgınlık Geçmişi</h2><div style="overflow:auto"><table class="estrus-table"><tr><th>Hayvan</th><th>Gözlem Tarihi</th><th>Belirtiler</th><th>18–24 Gün Penceresi</th><th>21. Gün</th><th>Not</th><th>İşlem</th></tr>{history_html}</table></div></div>'''
            return self.send_html(page('Kızgınlık Takibi',body,'/estrus',u,msg))
        if path=='/inseminations':
            aid=q.get('animal',[''])[0]
            estrus_id=q.get('estrus',[''])[0]
            with db() as c:
                females=c.execute("select id,tag,nickname from animals where gender='Dişi' and coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                all_rows=c.execute('''select i.*,a.tag,a.nickname from inseminations i join animals a on a.id=i.animal_id order by a.tag,i.attempt,i.insemination_date''').fetchall()
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
                if is_pregnant_value(result):badge='<span class="status-badge status-preg">Gebe</span>'
                elif result.strip().lower()=='negatif':badge='<span class="status-badge status-neg">Gebe Değil</span>'
                elif result.strip().lower()=='bekleniyor':badge='<span class="status-badge status-wait">Kontrol Bekliyor</span>'
                else:badge='<span class="status-badge status-unknown">Belirsiz</span>'
                hist=[]
                for rec in reversed(records):
                    rr=str(rec['pregnancy_result'] or 'Belirsiz')
                    if is_pregnant_value(rr):rb='<span class="status-badge status-preg">Gebe</span>'
                    elif rr.strip().lower()=='negatif':rb='<span class="status-badge status-neg">Gebe Değil</span>'
                    elif rr.strip().lower()=='bekleniyor':rb='<span class="status-badge status-wait">Kontrol Bekliyor</span>'
                    else:rb='<span class="status-badge status-unknown">Belirsiz</span>'
                    hist.append(f'''<tr><td>{rec["attempt"]}. deneme</td><td>{h(fmt_date(rec["insemination_date"]))}</td><td>{rb}</td><td>{h(fmt_date(rec["due_date"])) or '—'}</td><td><div class="row-actions"><a class="btn alt compact-btn" href="/insemination-edit?id={rec['id']}">✏️ Düzenle</a><form method="post" action="/insemination-delete" class="inline-form" onsubmit="return confirm('Bu tohumlama kaydı silinsin mi?')"><input type="hidden" name="id" value="{rec['id']}"><button class="btn red compact-btn">Sil</button></form></div></td></tr>''')
                history=''.join(hist)
                latest_rows.append(f'''<tr class="data-row"><td><a class="taglink" href="/animal?id={animal_id}">{h(latest['tag'])}</a><div class="mut">{h(latest['nickname'])}</div></td><td>{latest['attempt']}. Deneme</td><td>{h(fmt_date(latest['insemination_date']))}</td><td>{badge}</td><td>{h(fmt_date(latest['due_date'])) or '—'}</td><td><details><summary>Geçmiş ({len(records)})</summary><div style="overflow:auto"><table class="insem-history"><tr><th>Deneme</th><th>Tarih</th><th>Sonuç</th><th>Tahmini Doğum</th><th>İşlem</th></tr>{history}</table></div></details></td></tr>''')
            table_rows=''.join(latest_rows)
            estrus_info=''
            if estrus_context:
                try:
                    ed=date.fromisoformat(estrus_context['estrus_date']); es=ed+timedelta(days=18); ee=ed+timedelta(days=24)
                    estrus_info=f'<div class="flash">🌸 Bu hayvan Kızgınlık Takibi ekranından gönderildi. Beklenen pencere: <b>{fmt_date(es.isoformat())} – {fmt_date(ee.isoformat())}</b>. Tohumlama gerçekleştiğinde tarihi seçip kaydedin.</div>'
                except Exception:
                    estrus_info='<div class="flash">🌸 Bu hayvan Kızgınlık Takibi ekranından gönderildi.</div>'
            body=f'''<div class="insem-head"><div><h1>🐄 Üreme Takip Merkezi</h1><div class="mut">Tohumlama kayıtlarını hayvan bazında yönetin, gebelik sonucunu güncelleyin.</div></div><div class="insem-search"><input id="inseminationLiveSearch" type="search" placeholder="Küpe veya takma ad yazın..." autocomplete="off"><button type="button" class="btn alt live-clear" onclick="document.getElementById('inseminationLiveSearch').value='';document.getElementById('inseminationLiveSearch').dispatchEvent(new Event('input'))">Temizle</button></div></div>
            {estrus_info}
            <div class="grid insem-stats"><div class="card stat metric blue">Kontrol Bekleyen<b>{waiting}</b><small>Son kaydı sonuç bekleyen</small></div><div class="card stat metric green">Gebe<b>{pregnant}</b><small>Son sonucu pozitif olan</small></div><div class="card stat metric orange">3. Denemede<b>{third_attempt}</b><small>Yakın takip gereken</small></div><div class="card stat metric purple">Bu Ay Tohumlanan<b>{this_month}</b><small>{date.today().strftime('%m/%Y')}</small></div></div>
            <div class="card"><h2>Yeni Tohumlama</h2><form id="inseminationForm" method="post" action="/inseminations" class="form"><input type="hidden" name="estrus_id" value="{h(estrus_id if estrus_context else '')}"><label>Dişi Hayvan<div class="animal-picker"><input id="inseminationAnimalSearch" value="{h(selected_label)}" placeholder="Küpe veya takma ad yazın..." autocomplete="off" inputmode="search" required><div id="inseminationAnimalSuggestions" class="animal-suggestions" role="listbox" aria-label="Eşleşen dişi hayvanlar"></div></div><datalist id="inseminationAnimalOptions">{picker_options}</datalist><input type="hidden" id="inseminationAnimalId" name="animal_id" value="{h(aid if selected else '')}"><div class="animal-picker-note">Küpe veya takma ad yazın; eşleşen hayvanlar anında aşağıda görünür.</div></label><label>Deneme<div id="attemptPreview" class="attempt-preview">{(str(next_attempts[selected['id']])+'. Deneme') if selected else 'Hayvan seçildiğinde otomatik belirlenecek'}</div></label><label>Tohumlama Tarihi<input id="inseminationDate" type="date" name="insemination_date" required max="{date.today().isoformat()}"><div id="futureWarning" class="future-warning">Gelecek tarihli tohumlama kaydı girilemez.</div></label><label>İlk Durum<div class="attempt-preview">Kontrol Bekliyor</div><input type="hidden" name="pregnancy_result" value="Bekleniyor"></label><div class="full"><button class="btn">💾 Tohumlamayı Kaydet</button></div></form></div>
            <div class="card" style="margin-top:14px"><h2>Hayvan Bazında Tohumlama Geçmişi</h2><p class="mut">Her hayvan tek satırda gösterilir. “Geçmiş” bağlantısından tüm denemeleri açabilir ve kayıtları düzenleyebilirsiniz.</p><div id="insemEmpty" class="insem-empty">Eşleşen kayıt bulunamadı.</div><div style="overflow:auto"><table id="inseminationLiveTable" class="insem-table"><thead><tr><th>Hayvan</th><th>Son Deneme</th><th>Son Tohumlama</th><th>Durum</th><th>Tahmini Doğum</th><th>Geçmiş / İşlem</th></tr></thead><tbody>{table_rows}</tbody></table></div></div>
            <script>
            document.addEventListener('DOMContentLoaded',function(){{
              liveTableFilter('inseminationLiveSearch','inseminationLiveTable','insemEmpty');
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
        if path=='/health':
            with db() as c: animals=c.execute('select id,tag,nickname from animals order by tag').fetchall(); rows=c.execute('select h.*,a.tag from health h left join animals a on a.id=h.animal_id order by applied_date desc').fetchall()
            opts=''.join(f'<option value="{a["id"]}">{h(a["tag"])} - {h(a["nickname"])}</option>' for a in animals); trs=''.join(f'<tr><td>{h(r["tag"])}</td><td>{h(r["kind"])}</td><td>{h(r["product"])}</td><td>{h(r["applied_date"])}</td><td>{h(r["next_date"])}</td><td>{money(r["cost"])}</td></tr>' for r in rows)
            body=f'''<h1>Sağlık</h1><div class="card"><form method="post" class="form"><label>Hayvan<select name="animal_id">{opts}</select></label><label>Tür<select name="kind"><option>Aşı</option><option>İlaç</option><option>Muayene</option></select></label><label>Ürün/İşlem<input name="product" required></label><label>Uygulama Tarihi<input type="date" name="applied_date" required></label><label>Sonraki Tarih<input type="date" name="next_date"></label><label>Maliyet<input type="number" step="0.01" name="cost" value="0"></label><label class="full">Not<textarea name="notes"></textarea></label><div class="full"><button class="btn">Kaydet</button></div></form></div><div class="card" style="margin-top:14px"><table><tr><th>Küpe</th><th>Tür</th><th>Ürün</th><th>Tarih</th><th>Sonraki</th><th>Maliyet</th></tr>{trs}</table></div>'''
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
            categories=['Süt Satışı','Hayvan Satışı','Kesim Geliri','Buzağı Satışı','Destekleme','Yem','Veteriner','İlaç','Aşı','Saman','Elektrik','Yakıt','İşçilik','Diğer']
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
            sql='select f.*,a.tag from finance f left join animals a on a.id=f.animal_id where tx_date between ? and ?'; args=[start,end]
            if typ: sql+=' and tx_type=?'; args.append(typ)
            if category: sql+=' and category=?'; args.append(category)
            sql+=' order by tx_date desc,id desc'
            with db() as c:
                animals=c.execute("select id,tag,nickname from animals where coalesce(status,'Aktif')='Aktif' order by tag").fetchall()
                categories=c.execute("select distinct category from finance where coalesce(category,'')<>'' order by category").fetchall()
                rows=c.execute(sql,args).fetchall()
                inc=sum(float(r['amount'] or 0) for r in rows if r['tx_type']=='Gelir'); exp=sum(float(r['amount'] or 0) for r in rows if r['tx_type']=='Gider')
            opts=''.join(f'<option value="{a["id"]}">{h(a["tag"])} - {h(a["nickname"])}</option>' for a in animals)
            bulk_cards=''.join(f'''<label class="bulk-row" data-search="{h((str(a["tag"])+" "+str(a["nickname"] or "")).lower())}"><input type="checkbox" class="bulk-check" value="{a["id"]}" onchange="syncBulkSelection()"><span class="tag">🐄 {h(a["tag"])}</span><span class="nick">{h(a["nickname"]) or "Takma ad yok"}</span></label>''' for a in animals)
            category_opts=''.join(f'<option value="{h(r["category"])}" {"selected" if category==r["category"] else ""}>{h(r["category"])}</option>' for r in categories)
            trs=''.join(
                '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td><b>{7}</b></td><td><div class="finance-actions"><a class="btn alt" href="/finance/edit?id={8}">Düzenle</a><form method="post" action="/finance/delete" onsubmit="return confirm(\'Bu finans kaydı silinsin mi?\')"><input type="hidden" name="id" value="{8}"><button class="btn danger">Sil</button></form></div></td></tr>'.format(
                    fmt_date(r["tx_date"]),h(r["tx_type"]),h(r["category"]),h(r["description"]),h(r["tag"]),h(r["animal_status_action"]) or "-",h(r["payment_method"]),money(r["amount"]),r["id"]
                ) for r in rows
            )
            body=f'''<h1>Finans</h1><div class="grid"><div class="card stat">Gelir<b>{money(inc)}</b></div><div class="card stat">Gider<b>{money(exp)}</b></div><div class="card stat">Net<b>{money(inc-exp)}</b></div></div><div class="card" style="margin-top:14px"><h2>Yeni Kayıt</h2><form method="post" class="form" id="financeCreateForm">
<label>Tarih<input type="date" name="tx_date" required value="{date.today().isoformat()}"></label>
<label>Tür<select name="tx_type" id="tx"><option>Gelir</option><option>Gider</option></select></label>
<label>Kategori<select name="category" id="financeCategory"><option>Süt Satışı</option><option>Hayvan Satışı</option><option>Kesim Geliri</option><option>Buzağı Satışı</option><option>Destekleme</option><option>Yem</option><option>Veteriner</option><option>İlaç</option><option>Aşı</option><option>Saman</option><option>Elektrik</option><option>Yakıt</option><option>İşçilik</option><option>Diğer</option></select></label>
<label>Toplam Tutar<input type="number" step="0.01" min="0.01" name="amount" id="financeAmount" required></label>
<label>Ödeme Yöntemi<select name="payment_method"><option>Nakit</option><option>Banka</option><option>Kredi Kartı</option><option>Vadeli</option></select></label>
<label id="singleAnimalLabel">İlgili Hayvan<select name="animal_id" id="financeAnimal"><option value="">Yok</option>{opts}</select></label>
<input type="hidden" name="animal_ids" id="bulkAnimalIds" value="">
<div class="full bulk-animal-box" id="bulkAnimalBox"><div class="bulk-picker"><div class="bulk-picker-head"><div><h3 style="margin:0">🐄 İlgili Hayvanlar</h3><div class="mut">İlgili hayvanları seçin.</div></div><input class="bulk-search" id="bulkSearch" placeholder="Küpe veya takma ad ara…" oninput="filterBulkAnimals()"></div><div class="bulk-list" id="bulkList">{bulk_cards}</div><div class="bulk-summary"><span class="pill">Seçilen <b id="bulkCount">0</b> hayvan</span><span class="pill"><span id="bulkShareLabel">Hayvan Başı</span> <b id="bulkShare">₺0,00</b></span><button type="button" class="btn alt" onclick="clearBulkAnimals()">Seçimi Temizle</button></div><div class="bulk-selected-preview" id="bulkSelectedPreview">Henüz hayvan seçilmedi.</div></div></div>
<label class="full">Açıklama<input name="description"></label>
<div class="full" id="statusWarning" style="display:none;padding:12px;border-radius:10px;background:#fff3cd;color:#664d03"><b>Uyarı:</b> Seçilen hayvanlar işlem türüne göre aktif sürüden çıkarılır; geçmiş bilgileri silinmez. Toplam tutar seçilen hayvan sayısına göre otomatik dağıtılır.</div>
<div class="full finance-savebar"><button type="submit" class="btn" id="financeSubmitBtn">💾 Finans Kaydını Kaydet</button><span class="mut" id="financeSaveHint"></span></div></form></div><div class="card" style="margin-top:14px"><form method="get" class="finance-toolbar"><label>Başlangıç<input type="date" name="start" value="{h(start)}"></label><label>Bitiş<input type="date" name="end" value="{h(end)}"></label><label>Tür<select name="type"><option value="">Gelir + Gider</option><option {'selected' if typ=='Gelir' else ''}>Gelir</option><option {'selected' if typ=='Gider' else ''}>Gider</option></select></label><label>Kategori<select name="category"><option value="">Tüm Kategoriler</option>{category_opts}</select></label><button class="btn alt">Filtrele</button><a class="btn alt" href="/finance">Temizle</a><a class="btn blue" href="/finance/export?start={urllib.parse.quote(start)}&end={urllib.parse.quote(end)}&type={urllib.parse.quote(typ)}&category={urllib.parse.quote(category)}">CSV İndir</a></form><div class="finance-table-wrap"><table class="finance-table"><tr><th>Tarih</th><th>Tür</th><th>Kategori</th><th>Açıklama</th><th>Hayvan</th><th>Durum</th><th>Ödeme</th><th>Tutar</th><th>İşlem</th></tr>{trs}</table></div></div>'''
            body += f'''<script>
            function isBulkFinance(){{
              const t=document.getElementById('tx').value;
              const c=document.getElementById('financeCategory').value;
              return t==='Gelir' && (c==='Hayvan Satışı' || c==='Kesim Geliri');
            }}
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
            function refreshBulkFinance(){{
              const on=isBulkFinance();
              document.getElementById('bulkAnimalBox').style.display=on?'block':'none';
              document.getElementById('singleAnimalLabel').style.display=on?'none':'block';
              document.getElementById('financeAnimal').required=false;
              document.getElementById('statusWarning').style.display=on?'block':'none';
              syncBulkSelection();
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
            document.getElementById('financeAmount').addEventListener('input',syncBulkSelection);
            document.getElementById('financeCreateForm').addEventListener('submit',function(e){{
              syncBulkSelection();
              if(isBulkFinance()) document.getElementById('financeAnimal').required=false;
              if(isBulkFinance() && selectedChecks().length===0){{
                e.preventDefault();
                alert('Hayvan satışı veya kesim geliri için en az bir hayvan seçmelisiniz.');
              }}
            }});
            refreshBulkFinance();
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
            with db() as c:rows=c.execute('select * from backups order by created_at desc limit 100').fetchall()
            trs=''.join(f'<tr><td>{h(r["created_at"])}</td><td>{h(r["filename"])}</td><td>{(r["size_bytes"] or 0)//1024} KB</td><td><a class="btn blue" href="/backup/download?file={urllib.parse.quote(r["filename"])}">İndir</a> <a class="btn red" href="/backup/delete?file={urllib.parse.quote(r["filename"])}">Sil</a></td></tr>' for r in rows) or '<tr><td colspan=4>Henüz yedek yok.</td></tr>'
            body=f'''<h1>Yedekleme Merkezi</h1><div class="two"><div class="card"><h2>Tam Yedek Al</h2><p>Veritabanı, fotoğraflar ve sürüm bilgisi tek ZIP dosyasında saklanır.</p><a class="btn orange" href="/backup/create">Şimdi Yedek Al</a></div><div class="card"><h2>Yedeği Geri Yükle</h2><form method="post" action="/backup/restore" enctype="multipart/form-data"><input type="file" name="backup_file" accept=".zip" required><label style="display:block;margin:12px 0"><input type="checkbox" name="confirm_restore" value="yes" required> Mevcut verilerin değiştirileceğini kabul ediyorum.</label><button class="btn red">Yedeği Geri Yükle</button></form></div></div><div class="card" style="margin-top:14px"><h2>Yedek Geçmişi</h2><table><tr><th>Tarih</th><th>Dosya</th><th>Boyut</th><th>İşlem</th></tr>{trs}</table></div>'''
            return self.send_html(page('Yedekleme Merkezi',body,'/backups',u,msg))
        if path=='/backup/create':
            if not self.require_admin():return
            name=create_backup('manuel');audit(u,'Yedek oluşturdu',name,self.client_ip());return self.redirect('/backups','Tam yedek oluşturuldu.')
        if path=='/backup/download':
            if not self.require_admin():return
            name=os.path.basename(q.get('file',[''])[0]);fp=BACKUPS/name
            if not fp.exists():return self.send_html('Dosya bulunamadı',404)
            b=fp.read_bytes();self.send_response(200);self.send_header('Content-Type','application/zip');self.send_header('Content-Disposition',f'attachment; filename="{name}"');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
        if path=='/backup/delete':
            if not self.require_admin():return
            name=os.path.basename(q.get('file',[''])[0]);fp=BACKUPS/name
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
        if path=='/login':
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
                with db() as c:c.execute('insert into users(username,password,role,full_name,active,password_changed_at) values(?,?,?,?,1,?)',(uname,password_hash(password),role,f.get('full_name',''),datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            except sqlite3.IntegrityError:return self.redirect('/users','Bu kullanıcı adı zaten kullanılıyor.')
            audit(username,'Kullanıcı oluşturdu',uname+' · '+role,self.client_ip());return self.redirect('/users','Kullanıcı oluşturuldu.')
        if path=='/users/update':
            if not self.require_admin():return
            uid=int(f.get('id') or 0);role=f.get('role','personel');active=1 if f.get('active')=='1' else 0
            with db() as c:r=c.execute('select * from users where id=?',(uid,)).fetchone()
            if not r:return self.redirect('/users','Kullanıcı bulunamadı.')
            if r['role']=='admin' and r['active'] and (role!='admin' or not active) and active_admin_count()<=1:return self.redirect('/users/edit?id='+str(uid),'Son aktif yönetici değiştirilemez.')
            with db() as c:
                c.execute('update users set full_name=?,role=?,active=? where id=?',(f.get('full_name',''),role,active,uid))
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
                        name=f"animal_edit_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"
                        (UPLOADS/name).write_bytes(upload['content'])
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
                    duplicate=c.execute('select id from calves where tag=? and id<>?',(tag,cid)).fetchone()
                    animal_duplicate=c.execute('select id from animals where tag=?',(tag,)).fetchone()
                    if duplicate or animal_duplicate:return self.redirect('/calf-edit?id='+cid,'Bu küpe numarası başka bir kayıtta kullanılıyor.')
                    c.execute('update calves set tag=?,mother_id=?,father_tag=?,birth_date=?,gender=?,notes=? where id=?',
                              (tag,f.get('mother_id'),f.get('father_tag',''),f.get('birth_date',''),f.get('gender','Dişi'),f.get('notes',''),cid))
                audit(username,'Buzağı düzenledi',tag,self.client_ip())
                return self.redirect('/calves','Buzağı başarıyla güncellendi.')
            except sqlite3.IntegrityError:
                return self.redirect('/calf-edit?id='+cid,'Bu küpe numarası zaten kullanılıyor.')
            except Exception as exc:
                return self.redirect('/calf-edit?id='+cid,'Güncelleme hatası: '+str(exc))
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
                            name=f"animal_new_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}";(UPLOADS/name).write_bytes(upload['content']);photo_url='/uploads/'+name
                        cur=c.execute('insert into animals(tag,nickname,gender,breed,birth_date,notes,paddock,photo_url,sold_price,status,purchase_date,purchase_price,purchase_weight,daily_feed_cost,daily_care_cost,target_sale_price) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(tag,f.get('nickname',''),kind,f.get('breed',''),f.get('birth_date',''),f.get('notes',''),f.get('paddock',''),photo_url,0,'Aktif',f.get('purchase_date','') if kind=='Erkek' else '',float(f.get('purchase_price') or 0) if kind=='Erkek' else 0,float(f.get('purchase_weight') or 0) if kind=='Erkek' else 0,float(f.get('daily_feed_cost') or 0) if kind=='Erkek' else 0,float(f.get('daily_care_cost') or 0) if kind=='Erkek' else 0,float(f.get('target_sale_price') or 0) if kind=='Erkek' else 0))
                        aid=cur.lastrowid
                        if photo_url:c.execute('insert into animal_photos(animal_id,filename,created_at,caption) values(?,?,?,?)',(aid,photo_url.split('/uploads/',1)[1],datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'Profil fotoğrafı'))
                        return self.redirect('/animals' if kind=='Dişi' else '/males',kind+' hayvan başarıyla kaydedildi.')
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
        if path=='/animal/photo':
            try:
                upload=f.get('photo_file'); aid=f.get('animal_id','')
                if not upload or not isinstance(upload,dict): return self.redirect('/animal?id='+aid,'Fotoğraf seçilmedi.')
                ext=Path(upload['filename']).suffix.lower()
                if ext not in ('.jpg','.jpeg','.png','.webp','.gif'): return self.redirect('/animal?id='+aid,'Desteklenmeyen fotoğraf biçimi.')
                if len(upload['content'])>10*1024*1024: return self.redirect('/animal?id='+aid,'Fotoğraf 10 MB sınırını aşıyor.')
                name=f"animal_{aid}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"; (UPLOADS/name).write_bytes(upload['content'])
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
                        name=f"animal_new_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}{ext}"; (UPLOADS/name).write_bytes(upload['content']); photo_url='/uploads/'+name
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
                if path=='/health':
                    c.execute('insert into health(animal_id,kind,product,applied_date,next_date,cost,notes) values(?,?,?,?,?,?,?)',(f.get('animal_id'),f['kind'],f['product'],f['applied_date'],f.get('next_date'),float(f.get('cost') or 0),f.get('notes')))
                    if float(f.get('cost') or 0)>0:c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at) values(?,?,?,?,?,?,?,?)',(f['applied_date'],'Gider',f['kind'],float(f['cost']),f['product'],'Nakit',f.get('animal_id'),datetime.now().isoformat()))
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
                    recalculate_animal_exit_status(c,old_animal_id)
                    if animal_id!=old_animal_id:recalculate_animal_exit_status(c,animal_id)
                    return self.redirect('/finance','Finans kaydı güncellendi.')
                if path=='/finance/delete':
                    record_id=int(f['id'])
                    old=c.execute('select * from finance where id=?',(record_id,)).fetchone()
                    if not old:return self.redirect('/finance','Finans kaydı bulunamadı.')
                    animal_id=old['animal_id']
                    c.execute('delete from finance where id=?',(record_id,))
                    recalculate_animal_exit_status(c,animal_id)
                    return self.redirect('/finance','Finans kaydı silindi. Hayvan durumu yeniden hesaplandı.')
                if path=='/finance':
                    category=f['category']; tx_type=f.get('tx_type','Gelir')
                    action='Satıldı' if category=='Hayvan Satışı' else 'Kesildi' if category=='Kesim Geliri' else ''
                    amount=round(float(f['amount']),2)
                    if amount<=0:return self.redirect('/finance','Tutar 0’dan büyük olmalıdır.')
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
                    c.execute('insert into finance(tx_date,tx_type,category,amount,description,payment_method,animal_id,created_at,animal_status_action) values(?,?,?,?,?,?,?,?,?)',(f['tx_date'],tx_type,category,amount,f.get('description'),f.get('payment_method'),animal_id,datetime.now().isoformat(),action))
                    if action:c.execute('update animals set status=?,exit_date=?,exit_reason=?,sold_price=? where id=?',(action,f['tx_date'],category,amount,animal_id))
                    return self.redirect('/finance','Finans kaydı eklendi.' + (' Hayvan aktif sürüden çıkarıldı.' if action else ''))
        except sqlite3.IntegrityError as e:return self.redirect(path,'Aynı küpe numarası daha önce kaydedilmiş olabilir.')
        except Exception as e:return self.redirect(path,'Hata: '+str(e))

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));ip=s.getsockname()[0];s.close();return ip
    except:return '127.0.0.1'

if __name__=='__main__':
    init_db(); ensure_archive_schema(); promote_mature_calves(); daily_backup(); print(f'Yerel: http://127.0.0.1:{PORT}/login');print(f'Ağ: http://{local_ip()}:{PORT}/login');ThreadingHTTPServer(('0.0.0.0',PORT),App).serve_forever()
