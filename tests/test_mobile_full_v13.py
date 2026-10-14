from pathlib import Path
S=(Path(__file__).resolve().parents[1]/'app'/'server.py').read_text(encoding='utf-8')

def test_v13_identity_and_core_version_unchanged():
    assert "MOBILE_API_BUILD='MobileFullV13-EnterpriseParity-SharedLogic'" in S
    assert "APP_VERSION='3.9.23 DEV4 Hotfix1.22cr'" in S

def test_dashboard_mobile_uses_enterprise_dashboard_source():
    assert "path=='/api/v1/dashboard/tasks'" in S
    assert "api('/dashboard/tasks?filter=today')" in S
    assert "rows=list(health_plan_entries(c,horizon_days=30))" in S

def test_feed_state_is_shared_not_recomputed_in_mobile_js():
    assert 'def feed_stock_state(stock, daily_use):' in S
    assert "'stock_state':feed_stock_state" in S
    assert "data-stock-state=" in S
    assert "mode==='low'&&state==='low'" in S
    assert 'stock<=daily*7' not in S

def test_v12_center_quick_action_is_preserved():
    assert 'id="globalFab"' in S
    assert 'data-v="animals"' in S and 'data-v="tasks"' in S and 'data-v="modules"' in S
