import threading
import time
import unittest
import urllib.parse
import urllib.request
from datetime import date
from unittest.mock import patch

from test_reports_import import server


class Hotfix122BJTests(unittest.TestCase):
    def setUp(self):
        server.init_db()
        self.supplier='BJ Test '+str(time.time_ns())[-10:]
        with server.db() as con:
            self.finance_id=con.execute(
                '''insert into finance(
                    tx_date,tx_type,category,amount,description,payment_method,
                    created_at,due_date,payment_status,paid_date,paid_amount,supplier
                ) values(?,?,?,?,?,?,?,?,?,?,?,?)''',
                (
                    date.today().isoformat(),'Gider','Hayvan Alımı',12345.67,
                    'Dashboard hızlı ödeme testi','Vadeli',
                    time.strftime('%Y-%m-%dT%H:%M:%S'),date.today().isoformat(),
                    'Bekliyor','',0,self.supplier,
                ),
            ).lastrowid

    def tearDown(self):
        with server.db() as con:
            con.execute('delete from audit_log where detail like ?',('%Finans #'+str(self.finance_id)+'%',))
            con.execute('delete from finance where id=?',(self.finance_id,))

    def _get(self,path,session):
        request=urllib.request.Request(
            f'http://127.0.0.1:{self.http.server_port}{path}',
            headers={'Cookie':f'sid={session}'},
        )
        with urllib.request.urlopen(request,timeout=20) as response:
            return response.read().decode(),response.geturl()

    def test_dashboard_and_edit_screen_offer_payment_actions(self):
        session='hotfix122bj-ui'
        server.SESSIONS[session]={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()
        try:
            with patch.object(server,'license_status',return_value=(True,{},'')):
                dashboard,_=self._get('/',session)
                edit,_=self._get(f'/finance/edit?id={self.finance_id}',session)
            self.assertIn(f'/finance/edit?id={self.finance_id}#payment-status',dashboard)
            self.assertIn('class="v122bj-pay-btn"',dashboard)
            self.assertIn('name="return_to" value="/"',dashboard)
            self.assertIn('id="payment-status"',edit)
            self.assertIn('Ödeme bekliyor',edit)
            self.assertIn('name="paid_date"',edit)
            self.assertIn('Ödendi Olarak İşaretle',edit)
            self.assertIn('hotfix122bj-dashboard-payment',dashboard)
        finally:
            self.http.shutdown()
            self.http.server_close()
            server.SESSIONS.pop(session,None)

    def test_dashboard_quick_payment_returns_home_and_is_idempotent(self):
        session='hotfix122bj-post'
        server.SESSIONS[session]={'username':'admin','role':'admin'}
        self.http=server.QuietThreadingHTTPServer(('127.0.0.1',0),server.App)
        threading.Thread(target=self.http.serve_forever,daemon=True).start()
        try:
            payload=urllib.parse.urlencode({
                'id':self.finance_id,
                'paid_date':date.today().isoformat(),
                'return_to':'/',
            }).encode()
            request=urllib.request.Request(
                f'http://127.0.0.1:{self.http.server_port}/finance/mark-paid',
                data=payload,
                method='POST',
                headers={
                    'Cookie':f'sid={session}',
                    'Content-Type':'application/x-www-form-urlencoded',
                },
            )
            with patch.object(server,'license_status',return_value=(True,{},'')):
                with urllib.request.urlopen(request,timeout=20) as response:
                    html=response.read().decode()
                    self.assertRegex(response.geturl(),r'/\?msg=')
                # Mobil tarayıcı aynı POST'u yinelerse ikinci finans/audit hareketi oluşmamalı.
                retry=urllib.request.Request(
                    f'http://127.0.0.1:{self.http.server_port}/finance/mark-paid',
                    data=payload,
                    method='POST',
                    headers={
                        'Cookie':f'sid={session}',
                        'Content-Type':'application/x-www-form-urlencoded',
                    },
                )
                with urllib.request.urlopen(retry,timeout=20) as response:
                    response.read()
            self.assertIn('Vadeli ödeme ödendi olarak kapatıldı.',html)
            with server.db() as con:
                row=con.execute(
                    'select payment_status,paid_date,paid_amount from finance where id=?',
                    (self.finance_id,),
                ).fetchone()
                audit_count=con.execute(
                    "select count(*) from audit_log where action='Vadeli ödeme ödendi' and detail like ?",
                    ('%Finans #'+str(self.finance_id)+'%',),
                ).fetchone()[0]
            self.assertEqual(row['payment_status'],'Ödendi')
            self.assertEqual(row['paid_date'],date.today().isoformat())
            self.assertAlmostEqual(float(row['paid_amount']),12345.67)
            self.assertEqual(audit_count,1)
        finally:
            self.http.shutdown()
            self.http.server_close()
            server.SESSIONS.pop(session,None)

    def test_release_version_is_122bj(self):
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22cd')
        self.assertEqual(server.APP_LABEL,'v3.9.23 DEV4 Hotfix1.22cd')


if __name__=='__main__':
    unittest.main()
