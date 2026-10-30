"""Selected beef dry matter percentage must reach persistence, solver and live UI."""
import json
import sqlite3
import tempfile
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
from unittest.mock import patch

import test_app_edition as app_tests
server = app_tests.server


class DryMatterRateTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get

    def post(self, path, fields):
        req = urllib.request.Request(self.base + path,
            data=urllib.parse.urlencode(fields).encode(),
            headers={'Cookie': 'sid=app-edition-test'})
        with urllib.request.urlopen(req, timeout=60) as response:
            return response.read().decode(), response.url

    def ration(self, name='DM test', rate=2.5, milk=False):
        with server.db() as c:
            rid = c.execute('insert into rations(name,target_group,created_at,target_weight_kg,ration_type,target_dm_pct_bw) values(?,?,?,?,?,?)',
                (name, 'Sağmal' if milk else 'Besi', '2026-10-29', 400, 'Süt' if milk else 'Besi', rate)).lastrowid
            fid = c.execute('select id from feed_catalog where active=1 limit 1').fetchone()[0]
            c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)', (rid, fid, 3.25))
        return rid, fid

    def test_default_is_two_point_five_for_all_weights_and_profiles(self):
        for weight in (150, 200, 250, 350, 400, 500, 900):
            for profile in ('Besi Erkek', 'Düve', 'Genel Büyüyen Sığır'):
                t = server.ration_requirement_targets(weight, 1.3, profile)
                self.assertEqual(t['dmi_pct_bw'], 2.5)
                self.assertAlmostEqual(t['dmi_kg'], weight * .025)
                for density in (.8, 1.6, 2.5):
                    self.assertAlmostEqual(server._predicted_dmi_for_metrics({'nem_density': density}, t), weight * .025)

    def test_custom_percentage_is_not_clamped_to_old_dynamic_bounds(self):
        for pct in (1.7, 2.2, 2.7, 3.6):
            t = server.ration_requirement_targets(400, dm_pct_bw=pct)
            self.assertAlmostEqual(t['dmi_kg'], 4 * pct)
            self.assertAlmostEqual(server._predicted_dmi_for_metrics({'nem_density': 2.2}, t), 4 * pct)
        self.assertEqual(server.beef_dm_percentage('2,75'), 2.75)
        for bad in ('nan', 'inf', '-inf', 'abc', 0, -2, 101):
            with self.assertRaises(ValueError):
                server.beef_dm_percentage(bad)

    def test_existing_database_migration_keeps_quantities_and_custom_rate(self):
        rid, _ = self.ration()
        with server.db() as c:
            c.execute('alter table rations drop column target_dm_pct_bw')
        server.init_db()
        with server.db() as c:
            rr = c.execute('select * from rations where id=?', (rid,)).fetchone()
            self.assertEqual(rr['target_dm_pct_bw'], 2.5)
            self.assertEqual(c.execute('select kg_per_head_day from ration_items where ration_id=?', (rid,)).fetchone()[0], 3.25)
            c.execute('update rations set target_dm_pct_bw=2.75 where id=?', (rid,))
        server.init_db()
        with server.db() as c:
            self.assertEqual(c.execute('select target_dm_pct_bw from rations where id=?', (rid,)).fetchone()[0], 2.75)

    def test_rate_save_reloads_same_target_without_changing_feed_items(self):
        rid, fid = self.ration()
        text, url = self.post('/ration/dm-rate', {'ration_id': rid, 'target_dm_pct_bw': '2,70'})
        self.assertIn('/ration-workbench?', url)
        self.assertIn('value="2.70"', text)
        self.assertIn('10.80 kg KM/gün', text)
        with server.db() as c:
            self.assertEqual(c.execute('select target_dm_pct_bw from rations where id=?', (rid,)).fetchone()[0], 2.7)
            self.assertEqual(c.execute('select kg_per_head_day from ration_items where ration_id=? and feed_id=?', (rid, fid)).fetchone()[0], 3.25)
        for invalid in ('0', '-1', 'NaN', '101'):
            self.post('/ration/dm-rate', {'ration_id': rid, 'target_dm_pct_bw': invalid})
        with server.db() as c:
            self.assertEqual(c.execute('select target_dm_pct_bw from rations where id=?', (rid,)).fetchone()[0], 2.7)

    def test_saved_rate_and_feeds_prefill_solve_drawer(self):
        rid, fid = self.ration(rate=2.8)
        text, url = self.post('/ration/dm-rate', {'ration_id': rid, 'target_dm_pct_bw': '2.8', 'solve': '1'})
        self.assertIn('basis=' + str(rid), url)
        from html.parser import HTMLParser
        class BasisParser(HTMLParser):
            active = False
            payload = ''
            def handle_starttag(self, tag, attrs):
                self.active = tag == 'script' and dict(attrs).get('id') == 'cpDmSolveBasis'
            def handle_data(self, data):
                if self.active: self.payload += data
        parser = BasisParser(); parser.feed(text)
        basis = json.loads(parser.payload)
        self.assertEqual(basis['target_dm_pct_bw'], 2.8)
        self.assertEqual(basis['target_weight_kg'], 400)
        self.assertEqual(basis['feed_ids'], [str(fid)])

    def test_full_target_form_persists_rate_and_milk_is_independent(self):
        rid, _ = self.ration()
        self.post('/ration/target', {'ration_id': rid, 'ration_type': 'Besi', 'target_weight_kg': 250,
            'target_adg_kg': 1.3, 'target_dm_pct_bw': 2.8})
        with server.db() as c:
            rr = c.execute('select * from rations where id=?', (rid,)).fetchone()
            self.assertEqual(server.ration_targets_for_record(rr)['dmi_kg'], 7)
        milk_id, _ = self.ration('DM milk', milk=True)
        with server.db() as c:
            before = server.ration_targets_for_record(c.execute('select * from rations where id=?', (milk_id,)).fetchone())
        self.post('/ration/dm-rate', {'ration_id': milk_id, 'target_dm_pct_bw': 4})
        with server.db() as c:
            rr = c.execute('select * from rations where id=?', (milk_id,)).fetchone()
            self.assertEqual(rr['target_dm_pct_bw'], 2.5)
            self.assertEqual(server.ration_targets_for_record(rr), before)

    def test_solve_endpoint_passes_and_saves_selected_percentage(self):
        with server.db() as c:
            ids = [r[0] for r in c.execute('select id from feed_catalog where active=1 limit 2')]
        captured = []
        def fake_solve(feeds, w, adg, animal, age, phase, pct):
            captured.append(pct)
            return ([1, 2], {}, [(0, 10), (0, 10)]), server.ration_requirement_targets(w, adg, animal, age, phase, pct), ''
        with patch.object(server, 'solve_smart_ration', side_effect=fake_solve):
            _, url = self.post('/ration/solve', {'ration_type': 'Besi', 'target_weight_kg': 400,
                'target_adg_kg': 1.3, 'target_dm_pct_bw': '2.80', **{'feed_' + str(fid): 1 for fid in ids}})
        self.assertEqual(captured, [2.8])
        with server.db() as c:
            rr = c.execute("select * from rations where name like 'Akıllı Çözüm%' order by id desc limit 1").fetchone()
            self.assertEqual(rr['target_dm_pct_bw'], 2.8)
            self.assertAlmostEqual(server.ration_targets_for_record(rr)['dmi_kg'], 11.2)

    def test_protein_summary_matches_solver_with_legacy_catalog_values(self):
        rid, _ = self.ration()
        with server.db() as c:
            feed = c.execute("select * from feed_catalog where name='SUNAR 15.26 GELİŞTİRME BESİ YEMİ'").fetchone()
            c.execute('delete from ration_items where ration_id=?', (rid,))
            c.execute('update feed_catalog set cp_pct=99 where id=?', (feed['id'],))
            c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,?)', (rid, feed['id'], 4))
            feed = c.execute('select * from feed_catalog where id=?', (feed['id'],)).fetchone()
            summary = server.ration_summary(rid, c)
        metrics = server.smart_ration_metrics([feed], [4])
        self.assertAlmostEqual(summary['cp_pct_dm'], metrics['cp_pct_dm'])
        self.assertAlmostEqual(summary['cp_kg'], metrics['cp_kg'])
        self.assertAlmostEqual(summary['cp_kg'], 4 * float(feed['dm_pct']) / 100 * 16.978 / 100)

    def test_rate_change_does_not_invent_new_animal_protein_requirement(self):
        standard = server.ration_requirement_targets(400, 1.3, dm_pct_bw=2.5)
        custom = server.ration_requirement_targets(400, 1.3, dm_pct_bw=2.8)
        self.assertEqual(standard['mp_req_g'], custom['mp_req_g'])
        self.assertEqual(standard['cp_pct'], custom['cp_pct'])
        self.assertGreater(custom['dmi_kg'] * custom['cp_pct'] / 100, standard['dmi_kg'] * standard['cp_pct'] / 100)


if __name__ == '__main__':
    unittest.main()
