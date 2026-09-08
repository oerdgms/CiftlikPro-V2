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

    def _create_harvest(self, quantity="100", price="5"):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/harvest/save", {
            "season_id": str(season_id), "harvest_date": "2026-08-01",
            "product_name": "Arpa", "quantity_kg": quantity,
            "estimated_market_price": price,
        })
        lot_id = self.con.execute("SELECT id FROM agri_harvest_lots").fetchone()[0]
        return season_id, lot_id

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

    def test_input_and_operation_edits_reconcile_stock_and_finance(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/input/purchase", {
            "name": "DAP", "category": "Gübre", "unit": "kg", "quantity": "100",
            "unit_cost": "10", "tx_date": "2026-03-01", "payment_method": "Banka",
        })
        purchase = self.con.execute("SELECT * FROM agri_input_transactions WHERE tx_type='Giriş'").fetchone()
        agri.handle_post(self.con, "/agriculture/operation/save", {
            "season_id": str(season_id), "operation_date": "2026-03-15",
            "operation_type": "Taban Gübreleme", "labor_cost": "100",
            "input_id": str(purchase["input_id"]), "input_quantity": "30",
        })
        operation = self.con.execute("SELECT * FROM agri_operations").fetchone()

        agri.handle_post(self.con, "/agriculture/input/purchase", {
            "id": str(purchase["id"]), "name": "DAP", "category": "Gübre",
            "unit": "kg", "quantity": "120", "unit_cost": "12",
            "tx_date": "2026-03-02", "payment_method": "Vadeli",
        })
        self.assertEqual(agri.input_balance(self.con, purchase["input_id"]), 90)
        purchase_finance = self.con.execute(
            "SELECT * FROM agri_finance WHERE source_type='input_purchase'"
        ).fetchone()
        self.assertEqual(purchase_finance["amount"], 1440)
        self.assertEqual(purchase_finance["payment_method"], "Vadeli")

        agri.handle_post(self.con, "/agriculture/operation/save", {
            "id": str(operation["id"]), "season_id": str(season_id),
            "operation_date": "2026-03-16", "operation_type": "Üst Gübreleme",
            "labor_cost": "200", "input_id": str(purchase["input_id"]),
            "input_quantity": "20", "payment_method": "Nakit",
        })
        self.assertEqual(agri.input_balance(self.con, purchase["input_id"]), 100)
        self.assertEqual(self.con.execute(
            "SELECT amount FROM agri_finance WHERE source_type='operation'"
        ).fetchone()[0], 200)
        self.assertEqual(self.con.execute(
            "SELECT COUNT(*) FROM agri_finance WHERE source_type='operation'"
        ).fetchone()[0], 1)

        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/input/purchase", {
                "id": str(purchase["id"]), "name": "DAP", "category": "Gübre",
                "unit": "kg", "quantity": "10", "unit_cost": "12",
            })

    def test_harvest_and_sale_edits_reconcile_stock_and_finance(self):
        season_id, lot_id = self._create_harvest("100", "5")
        agri.handle_post(self.con, "/agriculture/harvest/save", {
            "id": str(lot_id), "season_id": str(season_id),
            "harvest_date": "2026-08-02", "product_name": "Arpa",
            "quantity_kg": "120", "estimated_market_price": "6",
        })
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 120)

        agri.handle_post(self.con, "/agriculture/sale/save", {
            "harvest_lot_id": str(lot_id), "sale_date": "2026-08-10",
            "quantity_kg": "20", "unit_price": "5", "buyer": "İlk Alıcı",
        })
        sale = self.con.execute("SELECT * FROM agri_sales").fetchone()
        agri.handle_post(self.con, "/agriculture/sale/save", {
            "id": str(sale["id"]), "harvest_lot_id": str(lot_id),
            "sale_date": "2026-08-11", "quantity_kg": "30",
            "unit_price": "6", "buyer": "Yeni Alıcı", "payment_method": "Banka",
        })
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 90)
        self.assertEqual(self.con.execute(
            "SELECT amount FROM agri_finance WHERE source_type='sale'"
        ).fetchone()[0], 180)
        self.assertEqual(self.con.execute(
            "SELECT COUNT(*) FROM agri_product_transactions WHERE tx_type='Satış'"
        ).fetchone()[0], 1)

        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/harvest/save", {
                "id": str(lot_id), "season_id": str(season_id),
                "product_name": "Arpa", "quantity_kg": "29",
            })
        agri.handle_post(self.con, "/agriculture/sale/delete", {"id": str(sale["id"])})
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 120)

    def test_internal_transfer_edit_keeps_all_linked_ledgers_in_sync(self):
        _, lot_id = self._create_harvest("100", "5")
        feed_id = self.con.execute("SELECT id FROM feed_catalog").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/transfer/save", {
            "harvest_lot_id": str(lot_id), "transfer_date": "2026-08-10",
            "quantity_kg": "20", "unit_price": "5", "feed_id": str(feed_id),
        })
        transfer = self.con.execute("SELECT * FROM agri_internal_transfers").fetchone()
        agri.handle_post(self.con, "/agriculture/transfer/save", {
            "id": str(transfer["id"]), "harvest_lot_id": str(lot_id),
            "transfer_date": "2026-08-11", "quantity_kg": "30",
            "unit_price": "6", "feed_id": str(feed_id), "notes": "Düzeltildi",
        })
        transfer = self.con.execute("SELECT * FROM agri_internal_transfers").fetchone()
        self.assertEqual(agri.harvest_balance(self.con, lot_id), 70)
        self.assertEqual(agri.feed_stock_balance(self.con, feed_id), 30)
        self.assertEqual(self.con.execute(
            "SELECT amount FROM agri_finance WHERE id=?", (transfer["agri_finance_id"],)
        ).fetchone()[0], 180)
        self.assertEqual(self.con.execute(
            "SELECT amount FROM finance WHERE id=?", (transfer["livestock_finance_id"],)
        ).fetchone()[0], 180)
        self.assertEqual(self.con.execute(
            "SELECT quantity_kg FROM feed_finance_links WHERE finance_id=?",
            (transfer["livestock_finance_id"],)
        ).fetchone()[0], 30)
        self.assertEqual(self.con.execute(
            "SELECT price_per_kg FROM feed_prices WHERE id=?", (transfer["feed_price_id"],)
        ).fetchone()[0], 6)

        self.con.execute(
            "INSERT INTO feed_stock_transactions(feed_id,tx_date,tx_type,quantity_kg,unit_price,notes) VALUES(?,?,'Tüketim',25,0,'test')",
            (feed_id, "2026-08-12"),
        )
        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/transfer/save", {
                "id": str(transfer["id"]), "harvest_lot_id": str(lot_id),
                "quantity_kg": "20", "unit_price": "6", "feed_id": str(feed_id),
            })
        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/transfer/delete", {"id": str(transfer["id"])})

    def test_manual_finance_edit_delete_and_automatic_record_protection(self):
        season_id = self._create_season()
        agri.handle_post(self.con, "/agriculture/finance/save", {
            "tx_date": "2026-04-01", "tx_type": "Gider", "category": "Elektrik",
            "amount": "500", "description": "Sulama elektriği",
            "season_id": str(season_id), "payment_method": "Banka",
        })
        manual = self.con.execute(
            "SELECT * FROM agri_finance WHERE COALESCE(source_type,'')=''"
        ).fetchone()
        agri.handle_post(self.con, "/agriculture/finance/save", {
            "id": str(manual["id"]), "tx_date": "2026-04-02", "tx_type": "Gider",
            "category": "Sulama", "amount": "750", "description": "Düzeltildi",
            "season_id": str(season_id), "payment_method": "Vadeli",
        })
        updated = self.con.execute("SELECT * FROM agri_finance WHERE id=?", (manual["id"],)).fetchone()
        self.assertEqual(updated["amount"], 750)
        self.assertEqual(updated["category"], "Sulama")
        automatic = self.con.execute(
            "SELECT id FROM agri_finance WHERE source_type='field_rent'"
        ).fetchone()[0]
        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/finance/save", {
                "id": str(automatic), "tx_type": "Gider", "amount": "1",
            })
        agri.handle_post(self.con, "/agriculture/finance/delete", {"id": str(manual["id"])})
        self.assertIsNone(self.con.execute("SELECT 1 FROM agri_finance WHERE id=?", (manual["id"],)).fetchone())

    def test_field_and_season_edits_and_guarded_deletes(self):
        agri.handle_post(self.con, "/agriculture/field/save", {
            "name": "DENEME", "ownership_type": "Özmal", "area_da": "50",
        })
        field_id = self.con.execute("SELECT id FROM agri_fields").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/field/save", {
            "id": str(field_id), "name": "DENEME 2", "ownership_type": "Özmal",
            "area_da": "60", "water_type": "Sulu",
        })
        field = self.con.execute("SELECT * FROM agri_fields WHERE id=?", (field_id,)).fetchone()
        self.assertEqual(field["name"], "DENEME 2")
        self.assertEqual(field["area_da"], 60)

        agri.handle_post(self.con, "/agriculture/season/save", {
            "field_id": str(field_id), "season_year": "2026", "crop_name": "Arpa",
            "cultivated_area_da": "50", "status": "Planlandı",
        })
        season_id = self.con.execute("SELECT id FROM agri_seasons").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/season/save", {
            "id": str(season_id), "field_id": str(field_id), "season_year": "2026",
            "crop_name": "Buğday", "cultivated_area_da": "55",
            "status": "Devam Ediyor",
        })
        season = self.con.execute("SELECT * FROM agri_seasons WHERE id=?", (season_id,)).fetchone()
        self.assertEqual(season["crop_name"], "Buğday")
        self.assertEqual(season["cultivated_area_da"], 55)
        with self.assertRaises(agri.AgricultureError):
            agri.handle_post(self.con, "/agriculture/field/delete", {"id": str(field_id)})
        agri.handle_post(self.con, "/agriculture/season/delete", {"id": str(season_id)})
        agri.handle_post(self.con, "/agriculture/field/delete", {"id": str(field_id)})
        self.assertEqual(self.con.execute("SELECT COUNT(*) FROM agri_fields").fetchone()[0], 0)

    def test_all_record_lists_expose_edit_and_delete_actions(self):
        season_id, lot_id = self._create_harvest("100", "5")
        agri.handle_post(self.con, "/agriculture/input/purchase", {
            "name": "Üre", "category": "Gübre", "unit": "kg",
            "quantity": "50", "unit_cost": "10",
        })
        input_id = self.con.execute("SELECT id FROM agri_input_catalog").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/operation/save", {
            "season_id": str(season_id), "operation_type": "Üst Gübreleme",
            "input_id": str(input_id), "input_quantity": "10",
        })
        agri.handle_post(self.con, "/agriculture/sale/save", {
            "harvest_lot_id": str(lot_id), "quantity_kg": "10",
            "unit_price": "5", "buyer": "Alıcı",
        })
        feed_id = self.con.execute("SELECT id FROM feed_catalog").fetchone()[0]
        agri.handle_post(self.con, "/agriculture/transfer/save", {
            "harvest_lot_id": str(lot_id), "quantity_kg": "10",
            "unit_price": "5", "feed_id": str(feed_id),
        })
        agri.handle_post(self.con, "/agriculture/finance/save", {
            "tx_type": "Gider", "category": "Diğer", "amount": "25",
        })
        expected = {
            "/agriculture/fields": ("?edit=", "/agriculture/field/delete"),
            "/agriculture/seasons": ("?edit=", "/agriculture/season/delete"),
            "/agriculture/operations": ("?edit=", "/agriculture/operation/delete"),
            "/agriculture/inputs": ("?edit=", "/agriculture/input/delete"),
            "/agriculture/harvests": ("?edit=", "/agriculture/harvest/delete"),
            "/agriculture/transfers": ("?edit_transfer=", "?edit_sale="),
            "/agriculture/finance": ("?edit=", "/agriculture/finance/delete"),
        }
        for path, markers in expected.items():
            _, body = agri.render_get(self.con, path, {})
            for marker in markers:
                self.assertIn(marker, body, path)

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
