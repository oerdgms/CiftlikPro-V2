import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook


TEST_DATA = tempfile.TemporaryDirectory(prefix="ciftlikpro-report-test-")
os.environ["CIFTLIKPRO_DATA_DIR"] = TEST_DATA.name
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import server  # noqa: E402


class ReportImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.init_db()

    def test_official_pdf_row_parser(self):
        text = "TR380001234567 1 SIĞIR Simental DİŞİ 20/05/2021 TR380009876543 26/10/2021"
        rows = server._official_pdf_rows(text)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["tag"], "TR380001234567")
        self.assertEqual(rows[0]["gender"], "DİŞİ")

    def test_xlsx_parse_prepare_and_export(self):
        wb = Workbook(); ws = wb.active
        ws.append(["KÜPE NO", "SÜRÜ NO", "TÜR", "IRK", "CİNSİYET", "DOĞUM TARİHİ", "ANA NO", "GELİŞ TARİHİ"])
        ws.append(["TR580000000101", 1, "SIĞIR", "Simental", "DİŞİ", "01/01/2020", "", "01/02/2020"])
        ws.append(["TR580000000102", 1, "SIĞIR", "Simental", "ERKEK", "01/08/2026", "TR580000000101", "02/08/2026"])
        data = io.BytesIO(); wb.save(data); wb.close()

        raw = server.parse_animal_import_file("hayvanlar.xlsx", data.getvalue())
        prepared = server.prepare_animal_import("hayvanlar.xlsx", raw)
        self.assertEqual(len(prepared), 2)
        self.assertTrue(all(row["valid"] for row in prepared))
        self.assertEqual(prepared[1]["record_type"], "Buzağı")

        export = server.animal_report_xlsx([], {"farm_name": "Test Çiftliği", "business_no": "TR1"})
        check = load_workbook(io.BytesIO(export), read_only=True)
        self.assertEqual(check.active["A1"].value, "Test Çiftliği · Tüm Hayvanlar Raporu")
        check.close()

    def test_report_combines_active_adults_and_calves(self):
        with server.db() as con:
            mother_id = con.execute(
                "insert into animals(tag,nickname,gender,breed,birth_date,notes,status) values(?,?,?,?,?,?,'Aktif')",
                ("TR580000000201", "Anne", "Dişi", "Simental", "2020-01-01", ""),
            ).lastrowid
            con.execute(
                "insert into calves(tag,mother_id,father_tag,birth_date,gender,notes,breed) values(?,?,?,?,?,?,?)",
                ("TR580000000202", mother_id, "", "2026-08-01", "Erkek", "", "Simental"),
            )
        rows = server.animal_report_rows()
        tags = {row["tag"] for row in rows}
        self.assertIn("TR580000000201", tags)
        self.assertIn("TR580000000202", tags)


if __name__ == "__main__":
    unittest.main()
