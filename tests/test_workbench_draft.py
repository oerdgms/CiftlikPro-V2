import threading
import unittest
import urllib.request
import urllib.parse
from unittest.mock import patch
from test_reports_import import server

class WorkbenchDraftTests(unittest.TestCase):
    def test_add_feed_keeps_existing_database_amounts_and_renders_draft_support(self):
        server.init_db()
        with server.db() as c:
            feeds=[r[0] for r in c.execute('select id from feed_catalog where active=1 order by id limit 3')]
            rid=c.execute("insert into rations(name,target_group,notes,active,created_at) values('Draft HTTP test','Besi','',1,'2026-10-01')").lastrowid
            iid=c.execute('insert into ration_items(ration_id,feed_id,kg_per_head_day) values(?,?,1)',(rid,feeds[0])).lastrowid
        server.SESSIONS['draft-http']={'username':'admin','role':'admin'}
        http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=http.serve_forever,daemon=True).start()
        def request(path,data=None):
            req=urllib.request.Request(f'http://127.0.0.1:{http.server_port}'+path,data=urllib.parse.urlencode(data).encode() if data else None,headers={'Cookie':'sid=draft-http'})
            return urllib.request.urlopen(req,timeout=20).read().decode()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                html=request('/ration/item',{'ration_id':rid,'feed_id':feeds[2],'kg_per_head_day':.5,'keep_feed_add_open':'1'})
                self.assertIn('cp-workbench-add-draft:',html)
                self.assertIn('data-draft-user="admin"',html)
                self.assertIn(f'data-feed-id="{feeds[0]}"',html)
                with server.db() as c:self.assertEqual(c.execute('select kg_per_head_day from ration_items where id=?',(iid,)).fetchone()[0],1)
                request('/ration/items-bulk',{'ration_id':rid,'item_'+str(iid):2.75,'lock_'+str(iid):1})
                with server.db() as c:
                    row=c.execute('select kg_per_head_day,locked from ration_items where id=?',(iid,)).fetchone()
                    self.assertEqual(tuple(row),(2.75,1))
        finally:
            http.shutdown();http.server_close();server.SESSIONS.pop('draft-http',None)
            with server.db() as c:
                c.execute('delete from ration_items where ration_id=?',(rid,));c.execute('delete from rations where id=?',(rid,))
