"""Standalone report controls retain enterprise boundaries and PDF exports."""
from html.parser import HTMLParser
import unittest
from urllib.parse import urlsplit, parse_qs
import test_multi_farm as mf

class Links(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.hrefs.append(dict(attrs).get('href',''))

class ReportNavigation260Tests(unittest.TestCase):
    setUp=mf.MultiFarmTests.setUp
    request=mf.MultiFarmTests.request
    create=mf.MultiFarmTests.create
    def test_report_returns_keep_selected_farm_filters_and_pdf(self):
        farm=self.create();fid=farm['id']
        status,_,body=self.request('/reproduction-center/print?stage=pregnant&search=TR1&farm='+fid)
        self.assertEqual(status,200)
        text=body.decode();parser=Links();parser.feed(text)
        local=[urlsplit(h) for h in parser.hrefs if h.startswith('/')]
        for path in ('/','/reports','/reproduction-center','/reproduction-center.pdf'):
            link=next(u for u in local if u.path==path)
            self.assertEqual(parse_qs(link.query)['farm'],[fid])
            if path.startswith('/reproduction-center'):
                self.assertEqual(parse_qs(link.query)['stage'],['pregnant'])
                self.assertEqual(parse_qs(link.query)['search'],['TR1'])
        self.assertIn('window.print()',text)
        self.assertIn('@media print{.actions{display:none}',text)
        status,headers,pdf=self.request('/reproduction-center.pdf?stage=pregnant&farm='+fid)
        self.assertEqual(status,200);self.assertTrue(pdf.startswith(b'%PDF'))
    def test_report_and_return_destinations_reject_other_farms_without_access(self):
        farm=self.create();fid=farm['id']
        for path in ('/reproduction-center/print?stage=all&','/reports?','/?'):
            self.assertEqual(self.request(path+'farm='+fid,sid='farm-staff')[0],403)

if __name__=='__main__':unittest.main()
