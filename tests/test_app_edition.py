import ast
import hashlib
import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.parse
from pathlib import Path
from unittest.mock import patch

from test_reports_import import server
import mobile_ui


ROOT = Path(__file__).resolve().parents[1]


class AppEditionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(server, 'DB', Path(self.temp.name)/'app.db')
        self.db_patch.start()
        server.init_db()
        self.license_patch = patch.object(server, 'license_status', return_value=(True, {}, ''))
        self.license_patch.start()
        server.SESSIONS['app-edition-test'] = {'id':1,'username':'admin','role':'admin'}
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()
        self.base = f'http://127.0.0.1:{self.http.server_port}'

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.license_patch.stop()
        self.db_patch.stop()
        server.SESSIONS.pop('app-edition-test',None)
        self.temp.cleanup()

    def get(self,path,authenticated=True):
        headers = {'Cookie':'sid=app-edition-test'} if authenticated else {}
        with urllib.request.urlopen(urllib.request.Request(self.base+path,headers=headers),timeout=20) as response:
            return response.status, response.headers, response.read(), response.url

    def seed(self,capacity=10):
        with server.db() as c:
            stamp = server.datetime.now().isoformat()
            p1 = c.execute('insert into paddocks(name,capacity,created_at) values(?,?,?)',('SA1',10,stamp)).lastrowid
            p2 = c.execute('insert into paddocks(name,capacity,created_at) values(?,?,?)',('SA2',capacity,stamp)).lastrowid
            a1 = c.execute("insert into animals(tag,gender,status,paddock_id,paddock) values('APP-A1','Dişi','Aktif',?,'SA1')",(p1,)).lastrowid
            a2 = c.execute("insert into animals(tag,gender,status,paddock_id,paddock) values('APP-A2','Erkek','Aktif',?,'SA1')",(p1,)).lastrowid
            ca = c.execute("insert into calves(tag,mother_id,gender,birth_date,status,paddock_id,paddock) values('APP-C1',?,'Dişi',?,'Aktif',?,'SA1')",(a1,server.date.today().isoformat(),p1)).lastrowid
        return p1,p2,a1,a2,ca

    def move(self,refs,target):
        with server.db() as c:
            return mobile_ui.move_subjects(vars(server),c,refs,target,'Test taşıma')

    def test_current_identity_and_assets(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22cr')
        self.assertEqual(server.APP_EDITION_BUILD,mobile_ui.BUILD)
        for path in ['/app-assets/mobile.css','/app-assets/mobile.js','/app-assets/icon.svg','/app-assets/icon-192.png','/app-assets/icon-512.png','/app-assets/login.jpg','/app-assets/offline.html','/app-service-worker.js','/app-manifest.json']:
            status,headers,data,_ = self.get(path,False)
            self.assertEqual(status,200,path)
            self.assertGreater(len(data),50,path)
        status,headers,_,_ = self.get('/app-service-worker.js',False)
        self.assertEqual(headers['Service-Worker-Allowed'],'/')

    def test_manifest_opens_normal_enterprise_address(self):
        manifest=json.loads(self.get('/app-manifest.json',False)[2])
        self.assertEqual(manifest['start_url'],'/')
        self.assertEqual(manifest['scope'],'/')
        self.assertEqual(manifest['display'],'standalone')

    def test_mobile_bookmark_migrates_to_enterprise_login(self):
        _,_,data,url=self.get('/mobile',False)
        self.assertEqual(urllib.parse.urlparse(url).path,'/login')
        self.assertIn(b'cpAppConfig',data)

    def test_login_uses_existing_form_and_password_recovery(self):
        text=self.get('/login',False)[2].decode()
        self.assertIn('name="username"',text)
        self.assertIn('name="password"',text)
        self.assertIn('/forgot-password',text)
        self.assertIn('viewport-fit=cover',text)
        self.assertIn('/app-assets/mobile.css',text)

    def test_existing_body_classes_and_form_fields_survive(self):
        source='<html><head></head><body class="herd-view-detail" data-user="1"><form method="post" action="/animal-edit"><input name="id" value="12"></form></body></html>'
        text=mobile_ui.enhance(source,'Hayvanlar','/all-animals')
        self.assertIn('class="herd-view-detail cp-app cp-route-all-animals"',text)
        self.assertIn('data-user="1"',text)
        self.assertIn('action="/animal-edit"',text)
        self.assertIn('name="id" value="12"',text)
        self.assertEqual(text.count('id="cpAppConfig"'),1)
        self.assertEqual(mobile_ui.enhance(text),text)

    def test_mobile_usability_patch_exposes_real_calf_entry_and_fitted_controls(self):
        text=self.get('/animal-add?entry=calf')[2].decode()
        config=json.loads(text.split('id="cpAppConfig">',1)[1].split('</script>',1)[0])
        self.assertEqual(config['request_url'],'/animal-add?entry=calf')
        self.assertIn('id="smartAnimalForm"',text)
        self.assertIn('/app-assets/mobile.css?v=2.0.5',text)
        self.assertIn('/app-assets/mobile.js?v=2.0.5',text)
        shell=mobile_ui.shell_markup('Hayvanlar','/all-animals','admin')
        self.assertIn('/animal-add?entry=adult',shell)
        self.assertIn('/animal-add?entry=calf',shell)
        javascript=(ROOT/'app'/'mobile_assets'/'mobile.js').read_text()
        stylesheet=(ROOT/'app'/'mobile_assets'/'mobile.css').read_text()
        self.assertIn('function animalEntry()',javascript)
        self.assertIn("10 aydan küçük olmalıdır",javascript)
        self.assertIn("if (path === '/all-animals') return setQuick(true)",javascript)
        self.assertIn('--cp-content-bottom',stylesheet)
        self.assertIn('bottom:calc(var(--cp-nav) + 8px)',stylesheet)
        self.assertIn('.v117-kpi b',stylesheet)
        self.assertIn('data-animal-panel="photos"',stylesheet)

    def test_finance_disclosure_stays_in_compact_card_header(self):
        javascript=(ROOT/'app'/'mobile_assets'/'mobile.js').read_text()
        stylesheet=(ROOT/'app'/'mobile_assets'/'mobile.css').read_text()
        self.assertIn("cells[8].classList.add('cp-finance-amount')",javascript)
        self.assertIn('cells[8].append(button)',javascript)
        self.assertIn('tr.cp-finance-record>td.cp-actions-cell{display:none!important',stylesheet)
        self.assertIn('tr.cp-finance-record.cp-row-open>td.cp-actions-cell{display:block!important',stylesheet)
        self.assertIn('min-height:72px!important',stylesheet)
        self.assertIn("ciftlikpro-app-edition-2.0.5",(ROOT/'app'/'mobile_assets'/'service-worker.js').read_text())

    def test_mobile_viewport_locks_page_drift_and_user_zoom(self):
        text=self.get('/reports?tab=finance')[2].decode()
        viewport='width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover'
        self.assertIn(f'<meta name="viewport" content="{viewport}">',text)
        self.assertEqual(text.count('name="viewport"'),1)
        no_meta=mobile_ui.enhance('<html><head></head><body></body></html>')
        self.assertIn(f'<meta name="viewport" content="{viewport}">',no_meta)
        javascript=(ROOT/'app'/'mobile_assets'/'mobile.js').read_text()
        stylesheet=(ROOT/'app'/'mobile_assets'/'mobile.css').read_text()
        self.assertIn('function lockMobileViewport()',javascript)
        self.assertIn("event.touches.length > 1",javascript)
        self.assertIn('document.documentElement.scrollLeft = 0',javascript)
        self.assertIn('overflow-x:hidden!important;overscroll-behavior-x:none!important',stylesheet)
        self.assertIn('touch-action:manipulation!important',stylesheet)
        self.assertIn('body.cp-app .finance-report-chart',stylesheet)
        self.assertIn('.password-wrap #loginPassword',stylesheet)
        self.assertIn('padding:13px 96px 13px 13px!important',stylesheet)
        self.assertIn('.cp-existing-actions .row-actions>form',stylesheet)
        self.assertIn('grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,.65fr)',stylesheet)

    def test_animal_cards_use_compact_mobile_layout_without_replacing_enterprise_forms(self):
        _,_,adult,_,calf=self.seed()
        calf_html=self.get(f'/calf?id={calf}')[2].decode()
        adult_html=self.get(f'/animal?id={adult}')[2].decode()
        javascript=(ROOT/'app'/'mobile_assets'/'mobile.js').read_text()
        stylesheet=(ROOT/'app'/'mobile_assets'/'mobile.css').read_text()
        self.assertIn('function animalCards()',javascript)
        self.assertIn("financial.className = 'cp-calf-financial'",javascript)
        self.assertIn('costboxes.forEach(box => financial.append(box))',javascript)
        self.assertIn("internalForm?.closest('.card')?.classList.add('cp-calf-internal')",javascript)
        self.assertIn('body.cp-app .cp-calf-financial .quick-metrics',stylesheet)
        self.assertIn('body.cp-app .calf-entry-grid{display:grid!important;grid-template-columns:minmax(0,1fr)!important',stylesheet)
        self.assertIn('body.cp-app.cp-animal-card-compact .animal-profile-head',stylesheet)
        self.assertIn('action="/calf/photo"',calf_html)
        self.assertIn('action="/calf/weight"',calf_html)
        self.assertIn('action="/calf-internal-cost/save"',calf_html)
        self.assertIn('data-animal-panel="finance"',adult_html)
        self.assertNotIn("fetch('/calf",javascript)

    def test_calf_entry_patch_does_not_replace_enterprise_post_route(self):
        javascript=(ROOT/'app'/'mobile_assets'/'mobile.js').read_text()
        self.assertNotIn("fetch('/animal-add'",javascript)
        self.assertNotIn('XMLHttpRequest',javascript)
        self.assertIn('name="record_type"',self.get('/animal-add?entry=calf')[2].decode())

    def test_config_and_display_escape_user_content(self):
        text=mobile_ui.enhance('<html><head></head><body></body></html>','</script><script>alert(1)</script>','/','"><svg onload=alert(2)>')
        config=text.split('id="cpAppConfig">',1)[1].split('</script>',1)[0]
        self.assertNotIn('</script>',config)
        self.assertEqual(json.loads(config)['title'],'</script><script>alert(1)</script>')
        self.assertIn('&lt;svg',text)

    def test_home_uses_same_task_rows_and_population_as_desktop(self):
        p1,p2,a1,a2,ca=self.seed()
        stamp=server.datetime.now().isoformat()
        today=server.date.today().isoformat()
        with server.db() as c:
            course=c.execute("insert into health_courses(kind,product,start_date,scope_type,created_at) values('Aşı','APP-AŞI',?,'single',?)",(today,stamp)).lastrowid
            for aid in [a1,a2]:
                c.execute('insert into health_tasks(course_id,animal_id,planned_date) values(?,?,?)',(course,aid,today))
            c.execute("insert into finance(tx_date,tx_type,category,amount,description,payment_method,due_date,payment_status,created_at) values(?,'Gider','Diğer',100,'APP-Vade','Vadeli',?,'Ödenmedi',?)",(today,today,stamp))
        source=server.dashboard_export_tasks()
        html=mobile_ui.home_markup(vars(server),'admin')
        self.assertEqual(html.count('class="cp-task cp-'),len(source))
        self.assertIn('APP-A1',html)
        self.assertIn('APP-A2',html)
        self.assertIn('/finance/edit?',html)
        self.assertIn('3</b><small>Aktif hayvan',html)

    def test_bulk_move_updates_adult_calf_counts_names_history_together(self):
        p1,p2,a1,a2,ca=self.seed()
        self.assertEqual(len(self.move([f'animal:{a1}',f'calf:{ca}'],p2)),2)
        with server.db() as c:
            self.assertEqual(server.paddock_population(p1,c),1)
            self.assertEqual(server.paddock_population(p2,c),2)
            self.assertEqual(c.execute('select paddock from animals where id=?',(a1,)).fetchone()[0],'SA2')
            self.assertEqual(c.execute('select paddock from calves where id=?',(ca,)).fetchone()[0],'SA2')
            self.assertEqual(c.execute('select count(*) from paddock_history').fetchone()[0],2)

    def test_insufficient_capacity_rolls_back_entire_selection(self):
        p1,p2,a1,a2,ca=self.seed(capacity=1)
        with self.assertRaises(ValueError):
            self.move([f'animal:{a1}',f'calf:{ca}'],p2)
        with server.db() as c:
            self.assertEqual(server.paddock_population(p1,c),3)
            self.assertEqual(server.paddock_population(p2,c),0)
            self.assertEqual(c.execute('select count(*) from paddock_history').fetchone()[0],0)

    def test_invalid_or_inactive_subject_never_causes_partial_move(self):
        p1,p2,a1,a2,ca=self.seed()
        with server.db() as c:c.execute("update animals set status='Satıldı' where id=?",(a2,))
        for refs in [[f'animal:{a1}',f'animal:{a2}'],[f'animal:{a1}','animal:999999'],['animals:1']]:
            with self.assertRaises(ValueError):self.move(refs,p2)
        with server.db() as c:
            self.assertEqual(c.execute('select paddock_id from animals where id=?',(a1,)).fetchone()[0],p1)
            self.assertEqual(c.execute('select count(*) from paddock_history').fetchone()[0],0)

    def test_promoted_calf_and_inactive_target_are_rejected(self):
        p1,p2,a1,a2,ca=self.seed()
        with server.db() as c:c.execute('update calves set promoted_animal_id=? where id=?',(a2,ca))
        with self.assertRaises(ValueError):self.move([f'calf:{ca}'],p2)
        with server.db() as c:c.execute('update paddocks set active=0 where id=?',(p2,))
        with self.assertRaises(ValueError):self.move([f'animal:{a1}'],p2)

    def test_repeated_move_is_idempotent(self):
        p1,p2,a1,a2,ca=self.seed()
        self.move([f'animal:{a1}',f'animal:{a1}'],p2)
        self.assertEqual(self.move([f'animal:{a1}'],p2),[])
        with server.db() as c:self.assertEqual(c.execute('select count(*) from paddock_history').fetchone()[0],1)

    def test_bulk_http_route_requires_session_and_uses_same_handler(self):
        p1,p2,a1,a2,ca=self.seed()
        form=urllib.parse.urlencode({'animal_refs':json.dumps([f'animal:{a1}',f'calf:{ca}']),'paddock_id':p2}).encode()
        request=urllib.request.Request(self.base+'/paddock/assign-many',data=form,headers={'Cookie':'sid=app-edition-test'})
        with urllib.request.urlopen(request,timeout=20) as response:self.assertIn('/paddocks?selected=',response.url)
        with server.db() as c:self.assertEqual(server.paddock_population(p2,c),2)
        request=urllib.request.Request(self.base+'/paddock/assign-many',data=form)
        with urllib.request.urlopen(request,timeout=20) as response:self.assertIn('/login',response.url)

    def test_existing_record_handlers_and_solver_functions_match_original(self):
        expected=json.loads((ROOT/'tests'/'enterprise_core_snapshot.json').read_text())
        tree=ast.parse((ROOT/'app'/'server.py').read_text())
        current={node.name:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest() for node in tree.body if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name!='page'}
        for name,digest in expected.items():
            self.assertEqual(current.get(name),digest,name+' changed')

    def test_windows_bundle_includes_mobile_assets_and_module(self):
        spec=(ROOT/'CiftlikPro.spec').read_text()
        self.assertIn('mobile_assets',spec)
        self.assertIn('"mobile_ui"',spec)
        workflow=(ROOT/'.github/workflows/windows-installer.yml').read_text()
        installer=(ROOT/'installer.iss').read_text()
        self.assertIn("server.APP_VERSION == '3.9.23 DEV4 Hotfix1.22cr'",workflow)
        self.assertIn('AppEdition_2_0_5_Setup.exe',workflow)
        self.assertIn('OutputBaseFilename=CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_5_Setup',installer)


if __name__=='__main__':
    unittest.main()
