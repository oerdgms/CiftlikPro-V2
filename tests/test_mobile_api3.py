from pathlib import Path
s=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
def test_build(): assert "MOBILE_API_BUILD='MobileAPI4-PaddockParity'" in s or "MOBILE_API_BUILD='MobileAPI5-HerdParity-Write1'" in s or "MOBILE_API_BUILD='MobileAPI6-HealthWrite'" in s
def test_task_fields():
    assert "t.task||t.title" in s and "t.subject||t.animal_tag" in s and "t.detail" in s
def test_no_raw_json_detail(): assert 'JSON.stringify(j,null,2)' not in s
def test_paddock_detail(): assert "path.startswith('/api/v1/paddocks/')" in s
def test_tr_date(): assert "p[2]+'/'+p[1]+'/'+p[0]" in s
