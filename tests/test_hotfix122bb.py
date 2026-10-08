import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import server

class Hotfix122BBTests(unittest.TestCase):
    def test_sunar_2128_exists_and_label_values_are_preserved(self):
        server.init_db()
        with server.db() as con:
            row=con.execute("select * from feed_catalog where name='SUNAR 21.28 TAMAMLAYICI SÜT YEMİ' and active=1").fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row['category'],'Ticari Karma Yem')
        self.assertAlmostEqual(row['label_cp_pct_as_fed'],21.0,places=2)
        self.assertAlmostEqual(row['label_me_kcal_kg_as_fed'],2800.0,places=1)
        self.assertAlmostEqual(row['label_crude_fiber_pct_as_fed'],8.64,places=2)
        self.assertAlmostEqual(row['label_fat_pct_as_fed'],3.10,places=2)
        self.assertAlmostEqual(row['label_ash_pct_as_fed'],6.60,places=2)
        self.assertAlmostEqual(row['label_sodium_pct_as_fed'],0.32,places=2)
        self.assertAlmostEqual(row['cp_pct'],23.769,places=3)
        self.assertAlmostEqual(row['me_mcal_kg'],3.169,places=3)
        self.assertIn('referans',row['source'])
        self.assertEqual(server.APP_VERSION,'3.9.23 DEV4 Hotfix1.22bs')

if __name__=='__main__': unittest.main()
