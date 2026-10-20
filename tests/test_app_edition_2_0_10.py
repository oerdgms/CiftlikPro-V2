import unittest
from pathlib import Path

import mobile_ui
from test_reports_import import server


ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'app' / 'mobile_assets' / 'mobile.css').read_text(encoding='utf-8')


class AppEdition210LayoutTests(unittest.TestCase):
    def test_build_and_cache_identity_are_current(self):
        self.assertEqual(mobile_ui.BUILD, 'AppEdition2.0.10-RationBadgeAlignment')
        self.assertEqual(server.APP_EDITION_BUILD, mobile_ui.BUILD)
        self.assertIn('/app-assets/mobile.css?v=2.0.10', mobile_ui.HEAD)
        self.assertIn('/app-assets/mobile.js?v=2.0.10', mobile_ui.enhance('<html><head></head><body></body></html>'))
        self.assertIn('ciftlikpro-app-edition-2.0.10', (ROOT / 'app' / 'mobile_assets' / 'service-worker.js').read_text(encoding='utf-8'))

    def test_primary_ration_status_badges_move_up_three_pixels(self):
        selector = 'body.cp-app:has(.workbench-shell) .wb2-kpi:is([data-key="dm"],[data-key="adg"],[data-key="cp"],[data-key="ndf"]) .wb2-kpi-status{top:5px!important}'
        self.assertIn(selector, CSS)
        for key in ('dm', 'adg', 'cp', 'ndf'):
            self.assertIn(f'[data-key="{key}"]', selector)

    def test_reproduction_filters_have_separate_label_and_count_columns(self):
        source = '<html><head></head><body><nav class="repro-stage-tabs"><button data-repro-filter="control">⌁ Gebelik Kontrolü <b>1</b></button><button data-repro-filter="empty">○ Boş / İşlem Bekleyen <b>4</b></button><button data-repro-filter="birth">🐮 Doğuma Yaklaşan <b>5</b></button></nav></body></html>'
        rendered = mobile_ui.enhance(source, path='/reproduction-center')
        self.assertIn('class="repro-tab-label">⌁ Gebelik Kontrolü</span> <b>', rendered)
        self.assertIn('class="repro-tab-label">○ Boş / İşlem Bekleyen</span> <b>', rendered)
        self.assertIn('class="repro-tab-label">🐮 Doğuma Yaklaşan</span> <b>', rendered)
        self.assertEqual(rendered.count('class="repro-tab-label"'), 3)
        self.assertEqual(mobile_ui.wrap_reproduction_tab_labels(rendered), rendered)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))!important', CSS)
        self.assertIn('grid-template-columns:minmax(0,1fr) 28px!important', CSS)
        self.assertIn('.repro-stage-tabs .repro-tab-label', CSS)
        self.assertIn('overflow-wrap:anywhere!important', CSS)
        self.assertNotIn('flex:1 1 29%!important', CSS)

    def test_every_enterprise_mobile_window_has_viewport_and_scroll_guards(self):
        required = (
            'body.cp-app .cp-sheet{',
            'body.cp-app .breed-sheet .sheet-panel',
            'body.cp-app .dashboard-picker{',
            'body.cp-app #financeDrawer.finance-drawer',
            'body.cp-app .section-drawer',
            'body.cp-app .ration-drawer',
            'body.cp-app .medicine-drawer',
            'body.cp-app .paddock-dialog{',
            'body.cp-app .feed-invoice-preview-card{',
            'body.cp-app .repro-status-dialog{',
            'body.cp-app .quick-feed-card[open]{',
        )
        for selector in required:
            self.assertIn(selector, CSS, selector)
        self.assertGreaterEqual(CSS.count('100dvh'), 8)
        self.assertGreaterEqual(CSS.count('env(safe-area-inset-bottom)'), 12)
        self.assertGreaterEqual(CSS.count('overscroll-behavior:contain!important'), 6)
        self.assertGreaterEqual(CSS.count('-webkit-overflow-scrolling:touch!important'), 5)

    def test_result_dialog_uses_readable_two_column_actions(self):
        self.assertIn('body.cp-app .repro-status-options{grid-template-columns:repeat(2,minmax(0,1fr))!important', CSS)
        self.assertIn('body.cp-app .repro-status-choice{min-width:0!important;min-height:74px!important', CSS)
        self.assertIn('body.cp-app .repro-status-foot{position:sticky!important', CSS)

    def test_stylesheet_is_structurally_balanced(self):
        self.assertEqual(CSS.count('{'), CSS.count('}'))
        self.assertTrue(CSS.rstrip().endswith('}'))


if __name__ == '__main__':
    unittest.main()
