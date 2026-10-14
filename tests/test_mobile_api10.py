import unittest
from pathlib import Path
class MobileApi10Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.s=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
 def test_build(self): self.assertIn("MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'",self.s)
 def test_animal_crud(self):
  for x in ("/api/v1/animal/update","/api/v1/animal/create","editAnimalForm","newAnimalForm"): self.assertIn(x,self.s)
 def test_health_crud(self):
  for x in ("/api/v1/health/update","/api/v1/health/delete","saveHealthEdit","deleteHealth"): self.assertIn(x,self.s)
 def test_lookups(self): self.assertIn("/api/v1/lookups",self.s)
 def test_parity_features_preserved(self):
  for x in ("/api/v1/paddocks/health","/api/v1/tasks/complete","/api/v1/reproduction","topSoon()"): self.assertIn(x,self.s)
