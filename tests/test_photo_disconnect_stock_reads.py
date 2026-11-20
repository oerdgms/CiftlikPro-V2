"""Aborted photo delivery and fresh, bounded stock reconciliation reads."""
import http.client
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock
from PIL import Image
import test_app_edition as fixture
import test_performance_259 as stock_tests
import multi_farm

server=fixture.server

class PhotoDisconnectTests(unittest.TestCase):
    setUp=fixture.AppEditionTests.setUp
    tearDown=fixture.AppEditionTests.tearDown
    get=fixture.AppEditionTests.get

    def test_aborted_photo_body_is_not_logged_as_application_failure(self):
        original=server.App.end_headers
        with tempfile.TemporaryDirectory() as folder, patch.object(server,'UPLOADS',Path(folder)):
            Image.new('RGB',(320,240),'green').save(Path(folder)/'cow.jpg')
            for failure in (ConnectionAbortedError(10053,'aborted'),ConnectionResetError('reset'),BrokenPipeError('closed')):
                def abort_body(handler):
                    original(handler)
                    if handler.path.startswith('/photo-preview'):
                        stream=Mock(wraps=handler.wfile)
                        stream.write.side_effect=failure
                        handler.wfile=stream
                with patch.object(server.App,'end_headers',abort_body), patch.object(multi_farm.logging,'exception') as logged:
                    with self.assertRaises(http.client.IncompleteRead):
                        self.get('/photo-preview?name=cow.jpg',False)
                    logged.assert_not_called()
                self.assertEqual(self.get('/photo-preview?name=cow.jpg',False)[0],200)

    def test_real_photo_bug_still_logs_and_returns_error(self):
        import photo_delivery
        with patch.object(photo_delivery,'preview_bytes',side_effect=RuntimeError('unexpected test failure')),patch.object(multi_farm.logging,'exception') as logged:
            from urllib.error import HTTPError
            with self.assertRaises(HTTPError) as caught:self.get('/photo-preview?name=cow.jpg',False)
            self.assertEqual(caught.exception.code,500)
            logged.assert_called_once()

class StockBatchReadsTests(unittest.TestCase):
    setUp=fixture.AppEditionTests.setUp
    tearDown=fixture.AppEditionTests.tearDown
    seed_stock=stock_tests.Performance259Tests.seed_stock

    def test_shared_recipe_updates_without_per_transaction_selects(self):
        with server.db() as c:
            # The fixture starts without animals; seed_stock assigns this adult.
            c.execute("insert into animals(tag,gender,status) values('BATCH-A','Erkek','Aktif')")
            feed,pad,day=self.seed_stock(c)
            rid=c.execute('select ration_id from paddock_rations where paddock_id=?',(pad,)).fetchone()[0]
            for n in range(12):
                fid=c.execute("insert into feed_catalog(name,category,active) values(?,'Kesif Yemler',1)",('Batch-'+str(n),)).lastrowid
                c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,1)',(rid,fid))
                server.record_ration_item_history(c,rid,fid,1,day,'Batch test')
            server.sync_daily_paddock_feed_stock(c,day)
            self.assertEqual(c.execute('select count(*) from paddock_feed_consumptions').fetchone()[0],13)
            queries=[];before=c.total_changes;c.set_trace_callback(queries.append)
            result=server.sync_daily_paddock_feed_stock(c,day)
            c.set_trace_callback(None)
            self.assertEqual(result['created']+result['updated']+result['removed'],0)
            self.assertEqual(c.total_changes,before)
            self.assertLess(len([q for q in queries if q.lstrip().lower().startswith('select')]),15)
            selects=[q for q in queries if q.lstrip().lower().startswith('select')]
            self.assertLess(len(selects),16)
            c.execute("insert into calves(tag,mother_id,gender,birth_date,status,paddock_id) values('BATCH-C',0,'Dişi',?,'Aktif',?)",(day,pad))
            server.sync_daily_paddock_feed_stock(c,day)
            self.assertEqual(c.execute('select animal_count from paddock_feed_consumptions where feed_id=?',(feed,)).fetchone()[0],2)
            c.execute("update calves set promoted_animal_id=1 where tag='BATCH-C'")
            server.sync_daily_paddock_feed_stock(c,day)
            self.assertEqual(c.execute('select animal_count from paddock_feed_consumptions where feed_id=?',(feed,)).fetchone()[0],1)
