"""Search behavior across the complete herd, independent of viewport/page size."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode

from test_reports_import import server
import mobile_reference
import text_search


class TextSearchTests(unittest.TestCase):
    def test_turkish_case_and_plain_keyboard_match(self):
        for query in ('çiğ', 'CIG', 'SARI İNCİ', 'inci sari', 'mavi takip'):
            self.assertTrue(text_search.matches(query, 'SARI PADOK', 'İnci ÇİĞDEM', 'MAVİ TAKİP'), query)
        self.assertFalse(text_search.matches('olmayan', 'İnci ÇİĞDEM'))

    def test_partial_numbers_words_and_empty_query(self):
        self.assertTrue(text_search.matches('6333', 'TR6333333'))
        self.assertTrue(text_search.matches('pad ci', 'Sarı Padok', 'Çiğdem'))
        self.assertTrue(text_search.matches('', None))
        self.assertFalse(text_search.matches('6333 eksik', 'TR6333333'))

    def test_query_text_is_not_sql_or_a_regular_expression(self):
        self.assertFalse(text_search.matches("' OR 1=1 --", 'Çiğdem'))
        self.assertFalse(text_search.matches('.*beklenen', 'Başka kayıt'))


class HerdTextSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db_patch=patch.object(server,'DB',Path(self.temp.name)/'search.db')
        self.db_patch.start();server.init_db()
        with server.db() as c:
            for index in range(35):
                c.execute("insert into animals(tag,nickname,gender,status) values(?,?,'Dişi','Aktif')",(f'AA{index:04}',f'Deneme {index}'))
            self.target=c.execute("insert into animals(tag,nickname,gender,paddock,notes,status) values('TR6333333','İnci ÇİĞDEM','Dişi','SARI PADOK','MAVİ TAKİP','Aktif')").lastrowid

    def tearDown(self):
        self.db_patch.stop();self.temp.cleanup()

    def test_search_is_applied_before_pagination_with_other_filters(self):
        for term in ('6333333','inci','CIGDEM','sari cig','mavi takip'):
            view=mobile_reference.herd_selection(vars(server),'/all-animals?'+urlencode({'q':term,'kind':'female','paddock':'SARI PADOK','per_page':15}))
            self.assertEqual([r['id'] for r in view['selected']],[self.target],term)
            self.assertEqual(view['pages'],1)
        view=mobile_reference.herd_selection(vars(server),'/all-animals?q=6333333&kind=male')
        self.assertEqual(view['selected'],[])

    def test_sql_search_is_read_only_and_uses_the_same_matching(self):
        with server.db() as c:
            changes=c.total_changes
            rows=c.execute('select id from animals where cp_search(?,tag,nickname,paddock,notes)=1',('cig sari',)).fetchall()
            self.assertEqual([r['id'] for r in rows],[self.target])
            self.assertEqual(c.total_changes,changes)
            self.assertEqual(c.execute('select count(*) from animals where cp_search(?,tag,nickname)=1',("' OR 1=1 --",)).fetchone()[0],0)
