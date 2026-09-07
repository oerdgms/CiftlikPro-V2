import sqlite3
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import agriculture as agri  # noqa: E402


class AgricultureModuleTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(":memory:")
        self.con.row_factory = sqlite3.Row
        self.con.executescript(
            """
            CREATE TABLE finance(
                id INTEGER PRIMARY KEY, tx_date TEXT, tx_type TEXT, category TEXT,
                amount REAL, description TEXT, payment_method TEXT, animal_id INTEGER,
                created_at TEXT, animal_status_action TEXT DEFAULT ''
            );
            CREATE TABLE feed_catalog(id INTEGER PRIMARY KEY,name TEXT,active INTEGER DEFAULT 1);
            CREATE TABLE feed_stock_transactions(
                id INTEGER PRIMARY KEY,feed_id INTEGER,tx_date TEXT,tx_type TEXT,
                quantity_kg REAL,unit_price REAL,notes TEXT
            );
            CREATE TABLE feed_prices(
                id INTEGER PRIMARY KEY,feed_id INTEGER,effective_date TEXT,
                price_per_kg REAL,notes TEXT
            );
            CREATE TABLE feed_finance_links(
                id INTEGER PRIMARY KEY,feed_id INTEGER,stock_tx_id INTEGER UNIQUE,
                finance_id INTEGER UNIQUE,quantity_kg REAL,unit_price REAL,created_at TEXT
            );
            """
        )
        agri.init_schema(self.con)
        self.con.execute("INSERT INTO feed_catalog(name,active) VALUES('ARPA EZMESİ',1)")

    def tearDown(self):
        self.con.close()

    def _create_season(self):
        agri.handle_post(self.con, "/agriculture/field/save", {
            "name": "PINARBAŞI", "ownership_type": "Kiralık", "area_da": "100",
            "rent_amount": "50000", "rent_payment_date": "2026-01-01", "post_rent": "yes",
        })
        field_id = self.con.execute("SELECT id FROM agri_fields").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/season/save", {
            "field_id": str(field_id), "season_year": "2026", "crop_name": "Arpa",
            "cultivated_area_da": "100", "status": "Devam Ediyor",
        })
        return self.con.execute("SELECT id FROM agri_seasons").fetchone()[0]

    def test_inputs_are_financed_once_and_allocated_to_season(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/input/purchase", {
            "name": "DAP", "category": "Gübre", "unit": "kg", "quantity": "2000",
            "unit_cost": "30", "tx_date": "2026-03-01", "payment_method": "Banka",
        })
        input_id = self.con.execute("SELECT id FROM agri_input_catalog").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/operation/save", {
            "season_id": str(season_id), "operation_date": "2026-03-15",
            "operation_type": "Taban Gübreleme", "area_da": "100",
            "fuel_liters": "100", "fuel_unit_price": "50", "labor_cost": "2000",
            "input_id": str(input_id), "input_quantity": "1500",
        })
        self.assertEqual(agri.input_balance(self.con, input_id), 500)
        purchase_expenses = self.con.execute(
            "SELECT COUNT(*) FROM agri_finance WHERE source_type='input_purchase'"
        ).fetchone()[0]
        self.assertEqual(purchase_expenses, 1)
        self.assertEqual(agri.season_cost(self.con, season_id), 102000)

    def test_harvest_is_stock_not_income(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/harvest/save", {
            "season_id": str(season_id), "harvest_date": "2026-08-01",
            "product_name": "Arpa", "quantity_kg": "50000", "estimated_market_price": "12",
        })
        lot_id = self.con.execute("SELECT id FROM agri_harvest_lots").fetchone()[0]
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 50000)
        harvest_income = self.con.execute(
            "SELECT COUNT(*) FROM agri_finance WHERE tx_type='Gelir'"
        ).fetchone()[0]
        self.assertEqual(harvest_income, 0)

    def test_internal_transfer_creates_three_linked_movements_and_rolls_back(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/harvest/save", {
            "season_id": str(season_id), "harvest_date": "2026-08-01",
            "product_name": "Arpa", "quantity_kg": "50000", "estimated_market_price": "12",
        })
        lot_id = self.con.execute("SELECT id FROM agri_harvest_lots").fetchone()[0]
        feed_id = self.con.execute("SELECT id FROM feed_catalog").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/transfer/save", {
            "harvest_lot_id": str(lot_id), "transfer_date": "2026-08-10",
            "quantity_kg": "10000", "unit_price": "12", "feed_id": str(feed_id),
        })
        transfer = self.con.execute("SELECT * FROM agri_internal_transfers").fetchone()
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 40000)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM agri_finance WHERE category='Hayvancılığa İç Transfer'").fetchone()[0], 1)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM finance WHERE animal_status_action='AGRI_INTERNAL'").fetchone()[0], 1)
        self.assertEqual(self.con.execute("SELECT SUM(quantity_kg) FROM feed_stock_transactions").fetchone()[0], 10000)
        agri.handle_post(self.con, "/agriculture/transfer/delete", {"id": str(transfer["id"])})
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 50000)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM finance").fetchone()[0], 0)
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM feed_stock_transactions").fetchone()[0], 0)

    def test_overdrawn_product_stock_is_blocked(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/harvest/save", {
            "season_id": str(season_id), "harvest_date": "2026-08-01",
            "product_name": "Arpa", "quantity_kg": "100", "estimated_market_price": "12",
        })
        lot_id = self.con.execute("SELECT id FROM agri_harvest_lots").fetchone()[0]
        feed_id = self.con.execute("SELECT id FROM feed_catalog").fetchone()[0]
        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/transfer/save", {
                "harvest_lot_id": str(lot_id), "quantity_kg": "101",
                "unit_price": "12", "feed_id": str(feed_id),
            })

    def test_all_agriculture_pages_render(self):
        for path in agri.AGRI_PATHS:
            title, body = agri.render_get(self.con, path, {})
            self.assertTrue(title)
            self.assertIn("Tarım & Ziraat Yönetimi", body)

        _, transfer_body = agri.render_get(self.con, "/agriculture/transfers", {})
        self.assertIn('id="agriTransferLot"', transfer_body)
        self.assertIn('id="agriTransferPrice"', transfer_body)
        self.assertIn('id="agriTransferFeed"', transfer_body)
        self.assertIn('id="agriSaleLot"', transfer_body)

        _, report_body = agri.render_get(
            self.con, "/agriculture/reports", {"year": ["geçersiz"]}
        )
        self.assertIn("Tarım Raporları", report_body)


if __name__ == "__main__":
    unittest.main()
