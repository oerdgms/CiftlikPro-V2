import unittest
from pathlib import Path

class MobileAPI8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
    def test_build_and_routes(self):
        self.assertIn("MOBILE_API_BUILD='MobileAPI8-FieldActions'",self.src)
        for route in ("/api/v1/notes","/api/v1/reproduction","/api/v1/paddocks/health"):
            self.assertIn(route,self.src)
    def test_mobile_actions_exist(self):
        for fn in ('reproForm','saveRepro','noteForm','saveNote','paddockHealthForm','savePaddockHealth'):
            self.assertIn('function '+fn,self.src)
    def test_parity_guards_preserved(self):
        self.assertIn("ca.promoted_animal_id is null",self.src)
        self.assertIn("paddock_population(int(row['id']),con)",self.src)
    def test_reproduction_rules(self):
        self.assertIn("if attempt>3",self.src)
        self.assertIn("timedelta(days=280)",self.src)
        self.assertIn("is_currently_pregnant(c,aid)",self.src)

if __name__=='__main__':unittest.main()
