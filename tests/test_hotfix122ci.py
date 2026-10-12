import io
import json
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from test_reports_import import server


class IsolatedCIData(unittest.TestCase):
    maxDiff=700
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.paths = patch.multiple(server, DATA_ROOT=self.root, DB=self.root/'ciftlik.db',
                                    BACKUPS=self.root/'backups', UPLOADS=self.root/'uploads',
                                    _ARCHIVE_SCHEMA_READY=False)
        self.paths.start()
        server.init_db()

    def tearDown(self):
        self.paths.stop()
        self.temp.cleanup()

    def animal(self, tag='TRCI000001', status='Aktif', purchase=45000):
        with server.db() as con:
            return con.execute("""insert into animals(
                tag,gender,status,purchase_date,purchase_price,daily_feed_cost)
                values(?,'Dişi',?,?,?,100)""",
                (tag, status, (date.today()-timedelta(days=10)).isoformat(), purchase)).lastrowid

    def finance(self, animal_id=None, calf_id=None, category='Diğer', amount=200,
                tx_type='Gider', payment='Nakit', action='', tx_date=None):
        day = tx_date or date.today().isoformat()
        with server.db() as con:
            return con.execute("""insert into finance(
                tx_date,tx_type,category,amount,animal_id,calf_id,payment_method,
                animal_status_action,created_at,payment_status,paid_date,paid_amount,due_date)
                values(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (day, tx_type, category, amount, animal_id, calf_id, payment, action,
                 datetime.now().isoformat(), 'Bekliyor' if payment=='Vadeli' else 'Ödendi',
                 '' if payment=='Vadeli' else day, 0 if payment=='Vadeli' else amount,
                 day if payment=='Vadeli' else '')).lastrowid


class FinanceIntegrityCITests(IsolatedCIData):
    def setUp(self):
        super().setUp()
        self.session = 'ci-integrity'
        server.SESSIONS[self.session] = {'username':'admin','role':'admin'}
        self.license = patch.object(server, 'license_status', return_value=(True, {}, ''))
        self.license.start()
        self.http = server.QuietThreadingHTTPServer(('127.0.0.1', 0), server.App)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.license.stop()
        server.SESSIONS.pop(self.session, None)
        super().tearDown()

    def request(self, path, form=None, payload=None, content_type=None):
        body = urllib.parse.urlencode(form).encode() if form is not None else payload
        headers = {'Cookie':f'sid={self.session}'}
        if content_type:
            headers['Content-Type'] = content_type
        req = urllib.request.Request(f'http://127.0.0.1:{self.http.server_port}{path}',
                                     data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode(), response.geturl()

    def test_archive_and_card_include_health_once_and_other_expenses(self):
        aid = self.animal(status='Satıldı')
        day = date.today().isoformat()
        with server.db() as con:
            con.execute("update animals set exit_date=?,sold_price=65000 where id=?", (day, aid))
        self.finance(aid, category='Hayvan Alımı', amount=45000)
        self.finance(aid, category='Hayvan Satışı', amount=65000, tx_type='Gelir', action='Satıldı')
        medical = self.finance(aid, category='İlaç', amount=500)
        self.finance(aid, category='Diğer', amount=200)
        with server.db() as con:
            con.execute("insert into health(animal_id,kind,applied_date,cost,finance_id) values(?,'İlaç',?,500,?)", (aid, day, medical))
            con.execute("insert into health(animal_id,kind,applied_date,cost) values(?,'Aşı',?,100)", (aid, day))
        card, _ = self.request(f'/animal?id={aid}')
        archive, _ = self.request('/archive/sold')
        self.assertIn('₺18.200,00', card)
        self.assertIn('₺18.200,00', archive)
        self.assertIn('₺46.800,00', archive)

    def test_deleting_unrelated_expense_does_not_reactivate_lost_animal(self):
        aid = self.animal(status='Öldü')
        with server.db() as con:
            con.execute("insert into animal_losses(subject_type,animal_id,event_date,event_type,created_at) values('animal',?,?,'Öldü',?)",
                        (aid, date.today().isoformat(), datetime.now().isoformat()))
        fid = self.finance(aid)
        self.request('/finance/delete', {'id':fid})
        with server.db() as con:
            self.assertEqual(con.execute('select status from animals where id=?',(aid,)).fetchone()[0], 'Öldü')

    def test_backdated_sale_confirmation_matches_archive_cost_at_exit(self):
        aid = self.animal()
        sale_day = (date.today()-timedelta(days=3)).isoformat()
        html, _ = self.request('/animal/sale', {'animal_id':aid, 'sale_price':'65000', 'sale_date':sale_day})
        self.assertIn('Satış tamamlandı. Net kâr/zarar: ₺19.300,00', html)
        self.assertIn('₺45.700,00', html)

    def test_payment_undo_and_immediate_repay_keep_one_finance_record(self):
        fid = self.finance(payment='Vadeli', category='Yem')
        payload = {'id':fid, 'paid_date':date.today().isoformat()}
        self.request('/finance/mark-paid', payload)
        self.request('/finance/unmark-paid', {'id':fid})
        self.request('/finance/mark-paid', payload)
        with server.db() as con:
            row = con.execute('select payment_status,paid_amount from finance where id=?',(fid,)).fetchone()
            self.assertEqual(row['payment_status'], 'Ödendi')
            self.assertEqual(row['paid_amount'], 200)
            self.assertEqual(con.execute('select count(*) from finance').fetchone()[0], 1)

    def test_paid_finance_amount_edit_updates_paid_amount(self):
        fid = self.finance(payment='Vadeli')
        self.request('/finance/mark-paid', {'id':fid, 'paid_date':date.today().isoformat()})
        self.request('/finance/edit', {'id':fid,'tx_date':date.today().isoformat(),
            'tx_type':'Gider','category':'Diğer','amount':'250','payment_method':'Vadeli',
            'due_date':date.today().isoformat()})
        with server.db() as con:
            row = con.execute('select amount,paid_amount,payment_status from finance where id=?',(fid,)).fetchone()
            self.assertEqual(row['amount'], 250)
            self.assertEqual(row['paid_amount'], 250)
            self.assertEqual(row['payment_status'], 'Ödendi')

    def test_concurrent_payment_submits_write_one_completion_audit(self):
        fid=self.finance(payment='Vadeli')
        form={'id':fid,'paid_date':date.today().isoformat()}
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(lambda _:self.request('/finance/mark-paid',form),range(2)))
        self.assertEqual(len(results),2)
        with server.db() as con:
            count=con.execute("select count(*) from audit_log where action='Vadeli ödeme ödendi' and detail like ?",(f'Finans #{fid} · %',)).fetchone()[0]
        self.assertEqual(count,1)

    def test_multi_calf_sale_cents_edit_and_partial_undo(self):
        mother = self.animal()
        with server.db() as con:
            ids = [con.execute("insert into calves(tag,mother_id,birth_date,gender,status) values(?,?,?,'Dişi','Aktif')",
                 (f'TRCI00CALF{i}',mother,date.today().isoformat())).lastrowid for i in range(3)]
        form = {'tx_date':date.today().isoformat(),'tx_type':'Gelir','category':'Buzağı Satışı',
                'amount':'1.000,01','payment_method':'Nakit','calf_ids':','.join(map(str,ids))}
        self.request('/finance', form)
        self.request('/finance', form)
        with server.db() as con:
            sales = con.execute("select * from finance where category='Buzağı Satışı' order by calf_id").fetchall()
            self.assertEqual(len(sales), 3)
            self.assertEqual(sum(round(r['amount']*100) for r in sales), 100001)
        self.request('/finance/edit', {'id':sales[0]['id'],'tx_date':date.today().isoformat(),
            'tx_type':'Gelir','category':'Buzağı Satışı','amount':'400','payment_method':'Nakit','calf_id':ids[0]})
        self.request('/finance/delete', {'id':sales[1]['id']})
        with server.db() as con:
            states = [con.execute('select status,sold_price from calves where id=?',(cid,)).fetchone() for cid in ids]
        self.assertEqual([r['status'] for r in states], ['Satıldı','Aktif','Satıldı'])
        self.assertEqual(states[0]['sold_price'],400)
        self.assertEqual(states[1]['sold_price'],0)
        with server.db() as con:
            self.assertEqual(con.execute('select paid_amount from finance where id=?',(sales[0]['id'],)).fetchone()[0],400)

    def test_shared_milk_income_is_allocated_without_duplication(self):
        ids = [self.animal(tag=f'TRCIMILK{i}', purchase=0) for i in range(3)]
        fid = self.finance(category='Süt Satışı',amount=300.01,tx_type='Gelir')
        with server.db() as con:
            for aid in ids:
                con.execute('insert into finance_animals(finance_id,animal_id,relation_type) values(?,?,?)',(fid,aid,'Süt'))
        html, _ = self.request(f'/animal?id={ids[0]}')
        self.assertIn('Gelir<br><b>₺100,01</b>', html)
        with server.db() as con:
            allocated=[server.animal_financial_summary(con,con.execute('select * from animals where id=?',(aid,)).fetchone())['income'] for aid in ids]
        self.assertEqual(sum(server.financial_cents(x) for x in allocated),30001)

    def test_archived_cost_ignores_later_health_and_matches_displayed_cents(self):
        aid=self.animal(status='Satıldı')
        end=(date.today()-timedelta(days=3)).isoformat()
        with server.db() as con:
            con.execute('update animals set exit_date=?,sold_price=65000,daily_feed_cost=100.005 where id=?',(end,aid))
            con.execute("insert into health(animal_id,kind,applied_date,cost) values(?,'Aşı',?,400)",(aid,date.today().isoformat()))
            row=con.execute('select * from animals where id=?',(aid,)).fetchone()
            summary=server.animal_financial_summary(con,row)
        self.assertEqual(summary['expense'],45000)
        self.assertEqual(server.financial_cents(summary['net_profit']),
                         server.financial_cents(summary['income'])-server.financial_cents(summary['expense'])-server.financial_cents(summary['operating']))

    def test_blank_purchase_date_uses_linked_purchase_transaction_for_cost_start(self):
        aid=self.animal()
        purchase=(date.today()-timedelta(days=4)).isoformat()
        with server.db() as con:con.execute("update animals set purchase_date='',birth_date='' where id=?",(aid,))
        self.finance(aid,category='Hayvan Alımı',amount=45000,tx_date=purchase)
        with server.db() as con:
            summary=server.animal_financial_summary(con,con.execute('select * from animals where id=?',(aid,)).fetchone())
        self.assertEqual(summary['operating'],400)

    def test_calf_card_and_archive_include_health_and_internal_cost_once(self):
        mother=self.animal()
        with server.db() as con:
            cid=con.execute("""insert into calves(tag,mother_id,birth_date,gender,status,purchase_price,exit_date,sold_price)
                values('TRCISOLD',?,?,'Dişi','Satıldı',1000,?,5000)""",
                (mother,date.today().isoformat(),date.today().isoformat())).lastrowid
            con.execute("insert into calf_internal_costs(calf_id,cost_date,cost_type,amount,created_at) values(?,?,'Süt',300,?)",(cid,date.today().isoformat(),datetime.now().isoformat()))
        fid=self.finance(calf_id=cid,category='İlaç',amount=200)
        with server.db() as con:
            con.execute("insert into health(calf_id,kind,applied_date,cost,finance_id) values(?,'İlaç',?,200,?)",(cid,date.today().isoformat(),fid))
        card,_=self.request(f'/calf?id={cid}')
        archive,_=self.request('/archive/sold')
        self.assertTrue('₺3.500,00' in card)
        self.assertTrue('₺3.500,00' in archive)

    def test_real_qr_and_datamatrix_images_open_animal_card(self):
        if server.zxingcpp is None:
            self.fail('Gerçek QR/2D testi için zxing-cpp kurulmalıdır.')
        aid = self.animal()
        for fmt in (server.zxingcpp.BarcodeFormat.QRCode, server.zxingcpp.BarcodeFormat.DataMatrix):
            with self.subTest(format=fmt):
                image=server.zxingcpp.write_barcode(fmt,'TRCI000001',width=240,height=240)
                pixels=memoryview(image)
                png=io.BytesIO();Image.frombytes('L',(pixels.shape[1],pixels.shape[0]),pixels.tobytes()).save(png,format='PNG')
                boundary='CiftlikProCIRealCode'
                payload=(f'--{boundary}\r\nContent-Disposition: form-data; name="code_image"; filename="scan.png"\r\nContent-Type: image/png\r\n\r\n'.encode()+
                         png.getvalue()+f'\r\n--{boundary}--\r\n'.encode())
                _, url = self.request('/animal-code-scan',payload=payload,content_type=f'multipart/form-data; boundary={boundary}')
                self.assertIn(f'/animal?id={aid}',url)

    def test_sold_archive_search_finds_adults_and_calves_by_tag(self):
        aid=self.animal('TRCISOLD001',status='Satıldı')
        with server.db() as con:
            con.execute("insert into calves(tag,nickname,mother_id,birth_date,gender,status,sold_price) values('TRCICALF002','Sarı Buzağı',?,?,'Dişi','Satıldı',5000)",(aid,date.today().isoformat()))
        html,_=self.request('/archive/sold?q=SOLD001')
        self.assertTrue('TRCISOLD001' in html)
        self.assertTrue('TRCICALF002' not in html)
        self.assertTrue('1 / 2 kayıt' in html)
        calf,_=self.request('/archive/sold?q=sari')
        self.assertTrue('TRCICALF002' in calf)
        self.assertTrue('TRCISOLD001' not in calf)

    def test_slaughter_archive_search_accepts_turkish_text_and_display_date(self):
        aid=self.animal('TRCICUT',status='Kesildi')
        with server.db() as con:
            con.execute("update animals set nickname='Sarı Kesimlik',paddock='SA7',exit_date='2026-09-05' where id=?",(aid,))
        for query in ('sari','SA7','05/09/2026'):
            with self.subTest(query=query):
                html,_=self.request('/archive/slaughtered?q='+urllib.parse.quote(query))
                self.assertTrue('TRCICUT' in html)
                self.assertTrue('1 / 1 kayıt' in html)

    def test_lost_archive_search_matches_cause_and_keeps_record_actions(self):
        aid=self.animal('TRCILOST',status='Öldü')
        with server.db() as con:
            con.execute("insert into animal_losses(subject_type,animal_id,event_date,event_type,cause,created_at) values('animal',?,?,'Öldü','Şüpheli neden',?)",(aid,date.today().isoformat(),datetime.now().isoformat()))
        html,_=self.request('/archive/lost?q=supheli')
        self.assertTrue('TRCILOST' in html)
        self.assertTrue('action="/loss-delete"' in html)
        self.assertTrue('href="/loss-edit?' in html)

    def test_archive_no_match_and_clear_return_correct_counts(self):
        self.animal('TRCICLEAR',status='Satıldı')
        html,_=self.request('/archive/sold?q=no-such-animal')
        self.assertTrue('0 / 1 kayıt' in html)
        self.assertTrue('Aramayla eşleşen kayıt bulunamadı.' in html)
        self.assertTrue('TRCICLEAR' not in html)
        cleared,_=self.request('/archive/sold?q=')
        self.assertTrue('1 / 1 kayıt' in cleared)
        self.assertTrue('TRCICLEAR' in cleared)
        self.assertTrue('id="archiveSearchClear"' in cleared)


class BackupIntegrityCITests(IsolatedCIData):
    def test_same_second_backups_have_distinct_names_and_contents(self):
        aid = self.animal()
        fixed=datetime(2026,10,12,9,30,0)
        with patch.object(server,'datetime') as clock:
            clock.now.return_value=fixed
            one=server.create_backup()
            with server.db() as con:con.execute("update animals set nickname='İkinci' where id=?",(aid,))
            two=server.create_backup()
        self.assertNotEqual(one,two)
        self.assertTrue((server.BACKUPS/one).exists())
        self.assertTrue((server.BACKUPS/two).exists())

    def test_full_backup_restores_finance_and_photos(self):
        aid=self.animal()
        self.finance(aid)
        (server.UPLOADS/'animal.webp').write_bytes(b'original-photo')
        name=server.create_backup()
        with server.db() as con:con.execute("update animals set nickname='Değişti' where id=?",(aid,))
        (server.UPLOADS/'animal.webp').write_bytes(b'changed-photo')
        emergency, manifest=server.restore_backup_zip(server.BACKUPS/name)
        self.assertTrue((server.BACKUPS/emergency).exists())
        self.assertEqual(manifest['version'],server.APP_VERSION)
        with server.db() as con:
            self.assertIsNone(con.execute('select nickname from animals where id=?',(aid,)).fetchone()[0])
            self.assertEqual(con.execute('select count(*) from finance').fetchone()[0],1)
            self.assertEqual(con.execute('pragma quick_check').fetchone()[0],'ok')
        self.assertEqual((server.UPLOADS/'animal.webp').read_bytes(),b'original-photo')

    def test_full_empty_photo_backup_removes_later_photos(self):
        self.animal()
        name=server.create_backup()
        (server.UPLOADS/'added-later.webp').write_bytes(b'not-in-backup')
        server.restore_backup_zip(server.BACKUPS/name)
        self.assertFalse((server.UPLOADS/'added-later.webp').exists())

    def test_non_ciftlik_database_is_rejected_before_current_data_changes(self):
        aid=self.animal()
        unrelated=self.root/'unrelated.db'
        con=sqlite3.connect(unrelated);con.execute('create table notes(body text)');con.commit();con.close()
        packed=self.root/'unrelated.zip'
        with zipfile.ZipFile(packed,'w') as z:z.write(unrelated,'ciftlik.db')
        ok, _, _=server.validate_backup_zip(packed)
        self.assertFalse(ok)
        with self.assertRaises(ValueError):server.restore_backup_zip(packed)
        with server.db() as con:self.assertIsNotNone(con.execute('select id from animals where id=?',(aid,)).fetchone())

    def test_configured_daily_backup_runs_once_at_selected_location(self):
        external=self.root/'external'
        server.set_setting_value('backup_directory',str(external))
        server.daily_backup();server.daily_backup()
        self.assertEqual(len(list(external.glob('CiftlikPro_Backup_otomatik_*.zip'))),1)
        with server.db() as con:
            self.assertEqual(con.execute("select count(*) from backups where filename like 'CiftlikPro_Backup_otomatik_%'").fetchone()[0],1)

    def test_migration_failure_restores_previous_database_and_photos(self):
        aid=self.animal()
        (server.UPLOADS/'animal.webp').write_bytes(b'saved-photo')
        name=server.create_backup()
        with server.db() as con:con.execute("update animals set nickname='Before Restore' where id=?",(aid,))
        (server.UPLOADS/'animal.webp').write_bytes(b'current-photo')
        with patch.object(server,'init_db',side_effect=RuntimeError('migration failed')):
            with self.assertRaises(RuntimeError):server.restore_backup_zip(server.BACKUPS/name)
        with server.db() as con:
            self.assertEqual(con.execute('select nickname from animals where id=?',(aid,)).fetchone()[0],'Before Restore')
        self.assertEqual((server.UPLOADS/'animal.webp').read_bytes(),b'current-photo')

    def test_corrupt_and_windows_traversal_backups_are_rejected(self):
        broken=self.root/'broken.zip';broken.write_bytes(b'not-a-zip')
        self.assertFalse(server.validate_backup_zip(broken)[0])
        name=server.create_backup()
        unsafe=self.root/'unsafe.zip'
        with zipfile.ZipFile(server.BACKUPS/name) as original,zipfile.ZipFile(unsafe,'w') as modified:
            for item in original.infolist():modified.writestr(item,original.read(item.filename))
            modified.writestr('..'+chr(92)+'outside.txt',b'unsafe')
        self.assertFalse(server.validate_backup_zip(unsafe)[0])

    def test_legacy_database_backup_upgrades_idempotently_and_preserves_photos(self):
        old=self.root/'legacy.db';con=sqlite3.connect(old)
        con.executescript('''
            create table animals(id integer primary key,tag text unique not null,gender text not null,nickname text,breed text,birth_date text,notes text);
            create table finance(id integer primary key,tx_date text not null,tx_type text not null,category text not null,amount real not null,description text,payment_method text,animal_id integer,created_at text not null);
            create table users(id integer primary key,username text unique,password text,role text default 'admin');
            insert into users values(1,'legacy','keep-hash','admin');
            insert into animals(id,tag,gender) values(1,'TRCILEGACY','Dişi');
            insert into finance values(1,'2026-07-27','Gelir','Hayvan Alımı',45000,'legacy','Nakit',1,'2026-07-27');
        ''');con.commit();con.close()
        name=self.root/'legacy.zip'
        with zipfile.ZipFile(name,'w') as z:z.write(old,'ciftlik.db')
        (server.UPLOADS/'existing.webp').write_bytes(b'preserve-for-db-only-backup')
        server.restore_backup_zip(name);server.init_db();server.init_db()
        with server.db() as con:
            self.assertEqual(con.execute('select tx_type from finance where id=1').fetchone()[0],'Gider')
            self.assertEqual(con.execute('select count(*) from animals').fetchone()[0],1)
            self.assertEqual(con.execute("select password from users where username='legacy'").fetchone()[0],'keep-hash')
            self.assertEqual(con.execute('pragma quick_check').fetchone()[0],'ok')
        self.assertEqual((server.UPLOADS/'existing.webp').read_bytes(),b'preserve-for-db-only-backup')


if __name__ == '__main__':
    unittest.main()
