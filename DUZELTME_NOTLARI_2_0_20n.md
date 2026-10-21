# ÇiftlikPro AppEdition 2.0.20n

## Mobil Rasyon — Bilimsel Hedef konumu
- 2.0.20m stabil ilk açılış davranışı korunur.
- Mobilde tek `Bilimsel Hedef Özeti` paneli, Rasyon/Hayvan Profili bilgisinin hemen altına ve Çözüm Durumu + KM/GCAA/HP/NDF kartlarının üstüne taşındı.
- Panel ilk açılışta kapalıdır; başlığa dokununca aynı mevcut form yerinde açılır/kapanır.
- Panel klonlanmaz; mevcut DOM düğümü tek kez doğru ankora yerleştirilir.
- Masaüstü ve solver/hesaplama fonksiyonları değiştirilmedi.

## Doğrulama
- `python -m py_compile app/server.py app/mobile_ui.py`: geçti.
- `PYTHONPATH=app:tests python -m unittest tests/test_app_edition.py -q`: 23/23 geçti.
