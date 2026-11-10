import concurrent.futures
from contextlib import nullcontext
from datetime import timedelta
from html.parser import HTMLParser
import threading
import unittest
from unittest.mock import patch

import test_app_edition as app_tests
import performance_speed as speed

server = app_tests.server


class Text(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.skip=0; self.parts=[]; self.feed(html)
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip-=1
    def handle_data(self,data):
        if not self.skip:self.parts.append(data)
    def value(self):return ' '.join(' '.join(self.parts).split())


class ModulePerformanceTests(unittest.TestCase):
    setUp=app_tests.AppEditionTests.setUp
    tearDown=app_tests.AppEditionTests.tearDown
    get=app_tests.AppEditionTests.get

    def seed(self):
        start=server.date.today()-timedelta(days=120)
        with server.db() as c:
            pid=c.execute('insert into paddocks(name,capacity,created_at) values(?,?,?)',
                          ('Speed padok',100,start.isoformat())).lastrowid
            rid=c.execute('select id from rations order by id limit 1').fetchone()[0]
            c.execute('insert into paddock_rations(paddock_id,ration_id,start_date,active) values(?,?,?,1)',(pid,rid,start.isoformat()))
            fids=[r[0] for r in c.execute('select feed_id from ration_items where ration_id=?',(rid,))]
            for fid in fids:
                for days in (0,40,80):
                    c.execute('insert into feed_prices(feed_id,effective_date,price_per_kg) values(?,?,?)',
                              (fid,(start+timedelta(days=days)).isoformat(),10+days/10))
            ids=[]
            for i in range(12):
                status='Satıldı' if i==11 else 'Aktif'
                aid=c.execute('insert into animals(tag,gender,status,paddock_id,purchase_date,purchase_price,exit_date,sold_price) values(?,?,?,?,?,?,?,?)',
                              (f'SPEED{i:02}','Erkek',status,pid,start.isoformat(),45000,
                               (start+timedelta(days=100)).isoformat() if i==11 else '',65000 if i==11 else 0)).lastrowid
                ids.append(aid)
                for days,weight in ((0,250),(40,290),(80,310),(80,315)):
                    c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',
                              (aid,(start+timedelta(days=days)).isoformat(),weight,str(weight)))
        return pid,rid,fids,ids,start

    def test_bulk_weights_keep_original_rows_order_and_mutation_invalidation(self):
        _,_,_,ids,_=self.seed()
        with server.db() as c:
            expected={aid:c.execute('select measure_date,weight,notes from weights where animal_id=? order by measure_date,id',(aid,)).fetchall() for aid in ids}
            with speed.request_reads() as state:
                state['bulk_weights'] = True
                for aid in ids:
                    actual=speed.weight_rows(c,aid)
                    self.assertEqual([tuple(r) for r in expected[aid]],[tuple(r) for r in actual])
                    self.assertEqual(actual[0].keys(),['measure_date','weight','notes'])
                c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',(ids[0],server.date.today().isoformat(),400,'new'))
                self.assertEqual(speed.weight_rows(c,ids[0])[-1]['weight'],400)

    def test_financial_results_equal_uncached_with_far_fewer_queries(self):
        _,_,_,ids,_=self.seed()
        with server.db() as c:
            animals=c.execute('select * from animals order by id').fetchall()
            queries=[];c.set_trace_callback(queries.append)
            expected=[server.animal_financial_summary(c,a) for a in animals]
            before=len(queries);queries.clear()
            with speed.request_reads():
                speed.activate()
                actual=[server.animal_financial_summary(c,a) for a in animals]
            after=len(queries);c.set_trace_callback(None)
        self.assertEqual(expected,actual)
        self.assertLess(after,before*.4,(before,after))

    def test_same_connection_write_and_next_request_see_new_price_and_settings(self):
        pid,_,fids,ids,start=self.seed()
        end=server.date.today()
        with server.db() as c:
            with speed.request_reads():
                speed.activate()
                old=server.paddock_feed_cost_between(c,pid,start,end,0)[0]
                c.execute('insert into feed_prices(feed_id,effective_date,price_per_kg) values(?,?,?)',(fids[0],start.isoformat(),999))
                changed=server.paddock_feed_cost_between(c,pid,start,end,0)[0]
                self.assertGreater(changed,old)
            with speed.request_reads():
                speed.activate()
                self.assertEqual(server.paddock_feed_cost_between(c,pid,start,end,0)[0],changed)
            c.commit()
            server.setting_set('male_min_daily_gain','1.9')
            with speed.request_reads():
                speed.activate()
                self.assertEqual(server.setting_float('male_min_daily_gain',1),1.9)

    def test_workspace_filters_and_totals_match_without_read_reuse(self):
        _,_,_,ids,_=self.seed()
        for route in ('/performance','/performance?scope=all&page=2',
                      '/performance?scope=completed&profit=loss',
                      '/performance?scope=due&search=SPEED','/performance?scope=all&animal_id='+str(ids[0])):
            with patch.object(speed,'request_reads',nullcontext):
                expected=Text(self.get(route)[2].decode()).value()
            actual=Text(self.get(route)[2].decode()).value()
            self.assertEqual(expected,actual,route)

    def test_other_module_pages_and_next_get_show_updated_records(self):
        _,_,_,ids,_=self.seed()
        for route in ('/animal?id='+str(ids[0]),'/paddocks','/feeds','/rations','/ration-workbench?id=1','/reproduction-center'):
            with patch.object(speed,'request_reads',nullcontext):
                expected=Text(self.get(route)[2].decode()).value()
            self.assertEqual(expected,Text(self.get(route)[2].decode()).value(),route)
        with server.db() as c:
            c.execute('insert into weights(animal_id,measure_date,weight,notes) values(?,?,?,?)',(ids[0],server.date.today().isoformat(),432.1,'updated'))
        self.assertIn('432.1 kg',self.get('/performance?animal_id='+str(ids[0]))[2].decode())

    def test_indexes_are_idempotent_and_keep_rows(self):
        self.seed()
        with server.db() as c:before=c.execute('select count(*) from weights').fetchone()[0]
        server.init_db()
        with server.db() as c:
            names={r['name'] for r in c.execute("select name from sqlite_master where type='index'")}
            self.assertTrue(all(statement.split()[5] in names for statement in speed.INDEXES))
            self.assertEqual(c.execute('select count(*) from weights').fetchone()[0],before)

    def test_female_weights_are_not_filtered_by_beef_batch_on_other_pages(self):
        _,_,_,ids,_ = self.seed()
        with server.db() as c:
            c.execute("update animals set gender='Dişi' where id=?",(ids[0],))
            expected=server.male_weight_performance(ids[0],c)
            with speed.request_reads():
                speed.activate()
                actual=server.male_weight_performance(ids[0],c)
            self.assertEqual(expected,actual)
            self.assertEqual(len(actual['rows']),4)


class ReadScopeTests(unittest.TestCase):
    def test_exception_and_concurrent_requests_never_share_values(self):
        class Connection:total_changes=0
        c=Connection();calls=[];barrier=threading.Barrier(2)
        def original(connection,value):
            result=(threading.current_thread().name,value,len(calls));calls.append(result);return result
        read=speed._reuse('probe',original)
        def worker():
            with speed.request_reads():
                speed.activate();first=read(c,1);barrier.wait(timeout=5)
                self.assertEqual(first,read(c,1));return first
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            a,b=list(pool.map(lambda _:worker(),range(2)))
        self.assertNotEqual(a,b);self.assertEqual(len(calls),2)
        with self.assertRaises(ValueError):
            with speed.request_reads():
                speed.activate();read(c,1);raise ValueError('abort')
        read(c,1);read(c,1)
        self.assertEqual(len(calls),5)

    def test_maintenance_is_uncached_until_explicit_activation(self):
        calls=[]
        read=speed._reuse('settings',lambda key:calls.append(key) or len(calls),False)
        with speed.request_reads():
            self.assertNotEqual(read('x'),read('x'))
            speed.activate();self.assertEqual(read('x'),read('x'))
