"""Bootstrap recipes behave like ordinary user-owned rations after creation."""
import unittest
import urllib.parse
import urllib.request

import test_app_edition as app_tests
server = app_tests.server


class PhaseRecipeLifecycleTests(unittest.TestCase):
    setUp = app_tests.AppEditionTests.setUp
    tearDown = app_tests.AppEditionTests.tearDown
    get = app_tests.AppEditionTests.get

    def phases(self):
        with server.db() as c:
            return c.execute("select * from rations where name like 'ÇiftlikPro Faz %' order by id").fetchall()

    def delete(self, rid):
        req = urllib.request.Request(self.base + '/ration/delete',
            data=urllib.parse.urlencode({'ration_id': rid}).encode(),
            headers={'Cookie': 'sid=app-edition-test'})
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode(), response.url

    def test_fresh_database_gets_four_recipes_once(self):
        before = [(row['id'], row['name']) for row in self.phases()]
        self.assertEqual(len(before), 4)
        server.init_db(); server.init_db()
        self.assertEqual([(row['id'], row['name']) for row in self.phases()], before)
        with server.db() as c:
            self.assertEqual(c.execute('select count(*) from ration_template_state').fetchone()[0], 4)

    def test_all_four_can_be_deleted_and_stay_deleted_after_restart(self):
        ids = [row['id'] for row in self.phases()]
        for rid in ids:
            text, _ = self.delete(rid)
            self.assertIn('Rasyon silindi.', text)
        server.init_db(); server.init_db()
        self.assertEqual(self.phases(), [])
        with server.db() as c:
            for rid in ids:
                self.assertIsNone(c.execute('select 1 from rations where id=?', (rid,)).fetchone())
                self.assertIsNone(c.execute('select 1 from ration_items where ration_id=?', (rid,)).fetchone())
                self.assertIsNone(c.execute('select 1 from ration_item_history where ration_id=?', (rid,)).fetchone())

    def test_bootstrap_never_resets_edited_quantities_or_renamed_recipes(self):
        rid = self.phases()[0]['id']
        with server.db() as c:
            iid = c.execute('select id from ration_items where ration_id=? limit 1', (rid,)).fetchone()[0]
            c.execute('update ration_items set kg_per_head_day=0.77,locked=1 where id=?', (iid,))
            c.execute("update rations set name='Benim Fazım',target_dm_pct_bw=2.8 where id=?", (rid,))
            history = c.execute('select * from ration_item_history where ration_id=? order by id', (rid,)).fetchall()
        server.init_db()
        with server.db() as c:
            item = c.execute('select * from ration_items where id=?', (iid,)).fetchone()
            self.assertEqual(item['kg_per_head_day'], .77)
            self.assertEqual(item['locked'], 1)
            self.assertEqual(c.execute('select target_dm_pct_bw from rations where id=?', (rid,)).fetchone()[0], 2.8)
            self.assertEqual([tuple(x) for x in c.execute('select * from ration_item_history where ration_id=? order by id', (rid,))], [tuple(x) for x in history])
            self.assertEqual(c.execute('select count(*) from rations').fetchone()[0], 4)

    def test_upgrade_preserves_deleted_recipes_even_without_prior_tracking(self):
        with server.db() as c:
            c.execute('drop table ration_template_state')
            c.execute('delete from ration_item_history')
            c.execute('delete from ration_items')
            c.execute('delete from rations')
        server.init_db()
        self.assertEqual(self.phases(), [])

    def test_upgrade_does_not_overwrite_existing_template_contents(self):
        rid = self.phases()[0]['id']
        with server.db() as c:
            c.execute('drop table ration_template_state')
            c.execute('update ration_items set kg_per_head_day=0.61 where ration_id=?', (rid,))
        server.init_db()
        with server.db() as c:
            self.assertTrue(all(row[0] == .61 for row in c.execute('select kg_per_head_day from ration_items where ration_id=?', (rid,))))

    def test_active_paddock_blocks_delete_and_past_assignment_archives(self):
        rid = self.phases()[0]['id']
        today = server.date.today().isoformat()
        with server.db() as c:
            pid = c.execute("insert into paddocks(name,capacity,created_at) values('PHASE-PAD',10,?)", (today,)).lastrowid
            c.execute('insert into paddock_rations(paddock_id,ration_id,start_date,active) values(?,?,?,1)', (pid, rid, today))
        text, _ = self.delete(rid)
        self.assertIn('Önce padok atamasını kaldırın', text)
        with server.db() as c:
            self.assertEqual(c.execute('select active from rations where id=?', (rid,)).fetchone()[0], 1)
            c.execute('update paddock_rations set active=0 where ration_id=?', (rid,))
            c.execute("delete from request_dedupe")
        text, _ = self.delete(rid)
        self.assertIn('arşivlendi', text)
        server.init_db()
        with server.db() as c:
            self.assertEqual(c.execute('select active from rations where id=?', (rid,)).fetchone()[0], 0)
            self.assertIsNotNone(c.execute('select 1 from ration_items where ration_id=?', (rid,)).fetchone())
            self.assertIsNotNone(c.execute('select 1 from paddock_rations where ration_id=?', (rid,)).fetchone())


if __name__ == '__main__':
    unittest.main()
