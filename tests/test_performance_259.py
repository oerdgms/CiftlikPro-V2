"""No-write page refreshes, shared credential freshness and simple navigation."""
import unittest
from unittest.mock import patch
import test_multi_farm as mf
import multi_farm
import mobile_ui
import request_diagnostics

server = mf.server


class Performance259Tests(unittest.TestCase):
    setUp = mf.MultiFarmTests.setUp
    request = mf.MultiFarmTests.request
    create = mf.MultiFarmTests.create

    def seed_stock(self, c):
        day = server.date.today().isoformat()
        feed = c.execute("insert into feed_catalog(name,category,dm_pct,cp_pct,active) values('259 Feed','Kesif Yemler',90,15,1)").lastrowid
        ration = c.execute("insert into rations(name,target_group,active,created_at) values('259 Ration','Besi',1,?)", (day,)).lastrowid
        c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,2)', (ration,feed))
        server.record_ration_item_history(c,ration,feed,2,day,'Test')
        pad = c.execute("insert into paddocks(name,code,type,capacity,active,created_at,updated_at) values('259 Pad','259','Besi',20,1,?,?)", (day,day)).lastrowid
        c.execute("update animals set paddock_id=?,paddock='259 Pad'", (pad,))
        c.execute('insert into paddock_rations(paddock_id,ration_id,start_date,active) values(?,?,?,1)', (pad,ration,day))
        c.execute("insert into feed_stock_transactions(feed_id,tx_date,tx_type,quantity_kg,unit_price) values(?,?,'Giriş',100,10)", (feed,day))
        return feed,pad,day

    def test_refresh_does_not_write_or_rebuild_and_population_change_is_immediate(self):
        with server.db() as c:
            feed,pad,day = self.seed_stock(c)
            self.assertEqual(server.sync_daily_paddock_feed_stock(c,day)['created'],1)
            before = c.total_changes
            with patch.object(server,'rebuild_feed_cost_history',wraps=server.rebuild_feed_cost_history) as rebuild:
                again = server.sync_daily_paddock_feed_stock(c,day)
                self.assertEqual(c.total_changes,before)
                rebuild.assert_not_called()
            self.assertEqual(again['quantity_kg'],2)
            c.execute("insert into animals(tag,gender,status,paddock_id) values('259-NEW','Erkek','Aktif',?)", (pad,))
            self.assertEqual(server.sync_daily_paddock_feed_stock(c,day)['updated'],1)
            self.assertEqual(server.feed_stock_kg(feed,c),96)

    def test_edited_stock_transaction_is_repaired_even_if_population_is_unchanged(self):
        with server.db() as c:
            feed,pad,day = self.seed_stock(c)
            server.sync_daily_paddock_feed_stock(c,day)
            c.execute("update feed_stock_transactions set quantity_kg=50 where feed_id=? and tx_type='Tüketim'", (feed,))
            server.sync_daily_paddock_feed_stock(c,day)
            self.assertEqual(server.feed_stock_kg(feed,c),98)
            self.assertEqual(c.execute('select stock_qty_kg from feed_cost_history where feed_id=? order by effective_date desc limit 1',(feed,)).fetchone()[0],98)

    def test_login_timestamp_does_not_mirror_but_password_role_and_active_do(self):
        farm = self.create()
        with patch.object(multi_farm.Registry,'_write_accounts',autospec=True,side_effect=multi_farm.Registry._write_accounts) as write:
            for n in range(3):
                with server.db() as c:c.execute('update users set last_login=?', (str(n),))
                self.registry.sync_accounts(farm)
            write.assert_not_called()
            for column,value in [('password','changed-hash'),('role','viewer'),('active',0)]:
                with server.db() as c:c.execute('update users set '+column+'=? where username=\'staff\'', (value,))
                self.registry.sync_accounts(farm)
                with multi_farm.scope(farm), server.db() as c:
                    self.assertEqual(c.execute('select '+column+' from users where username=\'staff\'').fetchone()[0],value)
            self.assertEqual(write.call_count,3)

    def test_simple_menu_and_all_modules_remain_accessible(self):
        text = mobile_ui.shell_markup('Hayvanlar','/all-animals','admin',
                {'name':'Admin','initials':'A','license_ok':True,'license_note':''})
        self.assertIn('Tüm Modüller',text)
        self.assertIn('İşler ve Hatırlatmalar',text)
        self.assertIn('href="/?app_view=modules"',text)
        import desktop_views
        modules = desktop_views.modules_markup(mobile_ui.icon)
        for path in ('/performance','/rations','/feeds','/health','/finance','/reproduction-center'):
            self.assertIn('href="'+path+'"',modules)

    def test_stage_timings_reset_on_exception(self):
        state = {}
        token = request_diagnostics._timings.set(state)
        def fail():raise ValueError('test')
        try:
            with self.assertRaises(ValueError):request_diagnostics.measured('stage',fail)()
            self.assertEqual(state['stage'][1],1)
        finally:request_diagnostics._timings.reset(token)
        self.assertIsNone(request_diagnostics._timings.get())


if __name__ == '__main__':unittest.main()
