from pathlib import Path
S=(Path(__file__).parents[1]/'app'/'server.py').read_text(encoding='utf-8')
def test_build(): assert "MOBILE_API_BUILD='MobileAPI6-HealthWrite'" in S
def test_health_post(): assert "if path=='/api/v1/health':" in S and "Mobil sağlık kaydı" in S
def test_health_ui(): assert '＋ Sağlık Kaydı' in S and 'saveHealth' in S
def test_task_lock(): assert '_taskBusy' in S and 'if(_taskBusy)return' in S
