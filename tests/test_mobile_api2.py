from pathlib import Path
S=Path(__file__).resolve().parents[1]/'app'/'server.py'
s=S.read_text(encoding='utf-8')
def test_mobile_api2_build(): assert "MOBILE_API_BUILD='MobileAPI2'" in s or "MOBILE_API_BUILD='MobileAPI3'" in s or "MOBILE_API_BUILD='MobileAPI4-PaddockParity'" in s or "MOBILE_API_BUILD='MobileAPI5-HerdParity-Write1'" in s or "MOBILE_API_BUILD='MobileAPI6-HealthWrite'" in s
def test_mobile_route(): assert "path in ('/mobile','/mobile/')" in s
def test_mobile_uses_api():
    assert "/api/v1" in s
    assert "/animals?status=Aktif&limit=250" in s
    assert "/tasks?filter=today" in s
    assert "/paddocks" in s
