import json
import unittest
import urllib.parse
import urllib.request
from datetime import timedelta
from unittest.mock import patch

import test_app_edition as app_tests
import ration_recalculation as recalc
server = app_tests.server


class RationRecalculationTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get

    def seed(self):
        with server.db() as c:
            rid = c.execute('select id from rations order by id limit 1').fetchone()[0]
            yesterday = (server.date.today()-timedelta(days=1)).isoformat()
            c.execute('update ration_item_history set effective_date=? where ration_id=?', (yesterday, rid))
            item = c.execute('select id from ration_items where ration_id=? order by id limit 1', (rid,)).fetchone()[0]
            c.execute('update ration_items set locked=1 where id=?', (item,))
            pid = c.execute("insert into paddocks(name,capacity,created_at) values('RECALC-PAD',10,?)", (yesterday,)).lastrowid
            c.execute('insert into paddock_rations(paddock_id,ration_id,start_date,active) values(?,?,?,1)', (pid, rid, yesterday))
        return rid

    def fake_solve(self, feeds, weight, adg, animal, age, phase, percent, fixed_quantities=None, reference_quantities=None):
        quantities = [float(f['kg_per_head_day']) if f['locked'] else float(f['kg_per_head_day'])+.1 for f in feeds]
        self.assertEqual(fixed_quantities, {int(f['id']):float(f['kg_per_head_day']) for f in feeds if f['locked']})
        self.assertEqual(reference_quantities, [float(f['kg_per_head_day']) for f in feeds])
        metrics = server.smart_ration_metrics(feeds, quantities)
        return (quantities, metrics, []), server.ration_requirement_targets(weight, adg, animal, age, phase, percent), ''

    def snapshot(self, rid):
        with server.db() as c:
            return recalc.state(vars(server), c, rid)[2]

    def prepare(self, rid):
        with patch.object(server, 'solve_smart_ration', side_effect=self.fake_solve):
            return recalc.prepare(vars(server), rid, 'admin', 450, 2.5)

    def test_preview_does_not_mutate_and_apply_keeps_ration_and_paddock(self):
        rid = self.seed(); original = self.snapshot(rid)
        yesterday = (server.date.today()-timedelta(days=1)).isoformat()
        with server.db() as c:
            old_count = c.execute('select count(*) from rations').fetchone()[0]
            previous = [(r['id'],r['kg_per_head_day']) for r in server.ration_items_on_date(c,rid,yesterday)]
            items = [tuple(r) for r in c.execute('select id,kg_per_head_day,locked from ration_items where ration_id=? order by id',(rid,))]
        token = self.prepare(rid)
        self.assertEqual(self.snapshot(rid), original)
        self.assertEqual(recalc.apply(vars(server),token,'admin'),rid)
        with server.db() as c:
            row = c.execute('select * from rations where id=?',(rid,)).fetchone()
            self.assertEqual(row['target_weight_kg'],450)
            self.assertEqual(row['target_dm_pct_bw'],2.5)
            self.assertEqual(c.execute('select count(*) from rations').fetchone()[0],old_count)
            self.assertIsNotNone(c.execute('select 1 from paddock_rations where ration_id=? and active=1',(rid,)).fetchone())
            self.assertEqual([(r['id'],r['kg_per_head_day']) for r in server.ration_items_on_date(c,rid,yesterday)],previous)
            for iid,qty,locked in items:
                actual = c.execute('select kg_per_head_day,locked from ration_items where id=?',(iid,)).fetchone()
                self.assertAlmostEqual(actual[0],qty if locked else qty+.1)
                self.assertEqual(actual[1],locked)

    def test_stale_ration_edit_is_rejected_without_partial_update(self):
        rid=self.seed();token=self.prepare(rid)
        with server.db() as c:c.execute("update rations set name='Changed elsewhere' where id=?",(rid,))
        before=self.snapshot(rid)
        with self.assertRaisesRegex(ValueError,'değişti'):recalc.apply(vars(server),token,'admin')
        self.assertEqual(self.snapshot(rid),before)

    def test_changed_feed_data_invalidates_preview(self):
        rid=self.seed();token=self.prepare(rid)
        with server.db() as c:
            fid=c.execute('select feed_id from ration_items where ration_id=? limit 1',(rid,)).fetchone()[0]
            c.execute('update feed_catalog set dm_pct=dm_pct-1 where id=?',(fid,))
        with self.assertRaisesRegex(ValueError,'değişti'):recalc.apply(vars(server),token,'admin')

    def test_preview_is_owner_scoped_expires_and_cannot_be_applied_twice(self):
        rid=self.seed();token=self.prepare(rid)
        with self.assertRaises(ValueError):recalc.apply(vars(server),token,'someone-else')
        recalc.apply(vars(server),token,'admin')
        with self.assertRaises(ValueError):recalc.apply(vars(server),token,'admin')
        token=self.prepare(rid)
        with server.db() as c:c.execute('update ration_recalc_previews set created_at=? where token=?',((server.datetime.now()-timedelta(hours=1)).isoformat(),token))
        with self.assertRaises(ValueError):recalc.apply(vars(server),token,'admin')

    def test_failed_solver_invalid_weight_and_milk_leave_record_unchanged(self):
        rid=self.seed();before=self.snapshot(rid)
        for weight in (149,901,'NaN'):
            with self.assertRaises(ValueError):recalc.prepare(vars(server),rid,'admin',weight,2.5)
        with patch.object(server,'solve_smart_ration',return_value=(None,{},'No feasible solution')):
            with self.assertRaisesRegex(ValueError,'No feasible'):recalc.prepare(vars(server),rid,'admin',450,2.5)
        self.assertEqual(self.snapshot(rid),before)
        with server.db() as c:c.execute("update rations set ration_type='Süt' where id=?",(rid,))
        with self.assertRaises(ValueError):recalc.prepare(vars(server),rid,'admin',450,2.5)

    def post(self,path,fields):
        req=urllib.request.Request(self.base+path,data=urllib.parse.urlencode(fields).encode(),headers={'Cookie':'sid=app-edition-test'})
        with urllib.request.urlopen(req,timeout=30) as response:return response.read().decode(),response.url

    def test_http_preview_and_apply_return_to_same_ration(self):
        rid=self.seed()
        old_name = 'Akıllı Çözüm 270kg 1.80 GCAA 1211-103000'
        new_name = 'Akıllı Çözüm 450kg 1.80 GCAA 1211-103000'
        with server.db() as c:
            c.execute('update rations set name=?, target_weight_kg=270 where id=?', (old_name,rid))
        with patch.object(server,'solve_smart_ration',side_effect=self.fake_solve):
            text,url=self.post('/ration/recalculate',{'ration_id':rid,'target_weight_kg':450,'target_dm_pct_bw':2.5})
        self.assertIn('/ration/recalculate-preview?',url)
        self.assertIn('Aynı Rasyona Uygula',text)
        self.assertIn('Yeni rasyon adı: <strong>'+new_name+'</strong>',text)
        with server.db() as c:
            self.assertEqual(c.execute('select name from rations where id=?',(rid,)).fetchone()[0], old_name)
        token=urllib.parse.parse_qs(urllib.parse.urlparse(url).query)['token'][0]
        _,url=self.post('/ration/recalculate-apply',{'token':token})
        self.assertIn('/ration-workbench?id='+str(rid),url)
        with server.db() as c:
            self.assertEqual(c.execute('select name from rations where id=?',(rid,)).fetchone()[0], new_name)
        self.assertEqual(self.get('/ration/recalculate-preview?token='+token,False)[3].split('?')[0],self.base+'/login')

    def test_duplicate_proposed_name_is_disambiguated_without_overwriting(self):
        rid = self.seed()
        with server.db() as c:
            c.execute("update rations set name='Padok A 270–350 kg', target_weight_kg=270 where id=?", (rid,))
            other = c.execute("insert into rations(name,created_at) values('Padok A 270–350 kg · Hedef 450 kg',datetime('now'))").lastrowid
        token = self.prepare(rid)
        recalc.apply(vars(server),token,'admin')
        with server.db() as c:
            self.assertEqual(c.execute('select name from rations where id=?',(rid,)).fetchone()[0],
                             'Padok A 270–350 kg · Hedef 450 kg (2)')
            self.assertEqual(c.execute('select name from rations where id=?',(other,)).fetchone()[0],
                             'Padok A 270–350 kg · Hedef 450 kg')

    def test_real_solver_preserves_locked_precision_and_rejects_out_of_bounds(self):
        names=['ARPA SAMANI','ARPA EZMESİ','BUĞDAY EZMESİ',"YONCA KURU OTU, KM'de %17-19 HP, %40-44 NDF",'MISIR SİLAJI, %29-33 KM','SUNAR 15.26 GELİŞTİRME BESİ YEMİ']
        with server.db() as c:feeds=[c.execute('select * from feed_catalog where name=?',(name,)).fetchone() for name in names]
        locked={feeds[1]['id']:1.234}
        solved,_,message=server.solve_smart_ration(feeds,400,1.3,'Besi Erkek',14,'Otomatik',2.5,fixed_quantities=locked)
        self.assertIsNotNone(solved,message)
        self.assertEqual(solved[0][1],1.234)
        solved,_,message=server.solve_smart_ration(feeds,400,1.3,'Besi Erkek',14,'Otomatik',2.5,fixed_quantities={feeds[-1]['id']:99})
        self.assertIsNone(solved)
        self.assertIn('Kilitli yem',message)

    def test_recalculation_prefers_small_changes_for_270_to_300_kg_example(self):
        names=['ARPA EZMESİ','ARPA SAMANI','BUĞDAY EZMESİ','MISIR PULU (FLAKED)',
               'MISIR SİLAJI, %29-33 KM','SUNAR 15.26 GELİŞTİRME BESİ YEMİ',
               'SUNAR BUZAĞI BÜYÜTME ÖZEL DÖNEM YEMİ',
               "YONCA KURU OTU, KM'de %19-21 HP, %37-40 NDF"]
        current=[.68,.50,.66,.52,2.91,.41,4.16,2.20]
        with server.db() as c:
            feeds=[c.execute('select * from feed_catalog where name=?',(name,)).fetchone() for name in names]
        self.assertTrue(all(feeds))
        solved,targets,message=server.solve_smart_ration(
            feeds,300,1.80,'Besi Erkek',0,'Otomatik',2.75,
            reference_quantities=current)
        self.assertIsNotNone(solved,message)
        quantities,metrics,_=solved
        changed=sum(abs(a-b)>=.04 for a,b in zip(quantities,current))
        total_change=sum(abs(a-b) for a,b in zip(quantities,current))
        self.assertLessEqual(changed,4,quantities)
        self.assertGreaterEqual(sum(abs(a-b)<1e-9 for a,b in zip(quantities,current)),4,quantities)
        self.assertLess(total_change,4.0,quantities)
        self.assertAlmostEqual(metrics['dm_kg'],targets['dmi_kg'],delta=targets['dmi_kg']*.035)
        self.assertGreaterEqual(metrics['achievable_adg_kg'],1.7995)
        self.assertGreaterEqual(metrics['roughage_pct_dm'],targets['roughage_min']-.05)
        self.assertLessEqual(metrics['roughage_pct_dm'],targets['roughage_max']+.05)
        self.assertIn('mevcut rasyona en az müdahale',metrics['solver_engine'])


if __name__=='__main__':unittest.main()
