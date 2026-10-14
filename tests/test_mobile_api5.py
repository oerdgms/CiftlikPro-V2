from pathlib import Path
S=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
def test_build(): assert "MOBILE_API_BUILD='MobileAPI5-HerdParity-Write1'" in S or "MOBILE_API_BUILD='MobileAPI6-HealthWrite'" in S
def test_active_herd_includes_calves():
    assert "ca.promoted_animal_id is null" in S and "item['source']='animal'" in S and "'source':'calf'" in S
def test_mobile_write_endpoint(): assert "path=='/api/v1/tasks/complete'" in S
def test_duplicate_guard(): assert "status='İşleniyor'" in S and "status='Tamamlandı'" in S
def test_mobile_button(): assert '✓ Uygulandı' in S
