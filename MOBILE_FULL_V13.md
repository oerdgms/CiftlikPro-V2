# MobileFull V13 — Enterprise Parity / Shared Logic

V13'ün amacı mobil için ikinci bir iş mantığı üretmek değil, mevcut ÇiftlikPro Enterprise kurallarını mobil arayüze sunmaktır.

## Ortak kaynak eşlemesi

| Mobil ekran | Enterprise ortak kaynak |
|---|---|
| Ana Sayfa / Bugünün İşleri | `dashboard_export_tasks()` → `health_plan_entries()` + bekleyen vadeli finans kayıtları |
| Sağlık Merkezi | `health_export_tasks()` / `health_plan_entries()` |
| Sağlık planı | `health_courses`, `health_tasks`, `create_health_course_tasks()` |
| Yem & Stok | `current_daily_feed_use()` + stok hareketleri + ortak `feed_stock_state()` |
| Gebelik sayısı | `active_pregnancy_records()` / `_api_animal_summary()` |
| Padok nüfusu | `paddock_population()` |
| Hayvan maliyeti | `animal_financial_summary()` |
| Finans kayıtları | mevcut `finance` tablosu ve normalize/bağlı kayıt kuralları |
| Rasyon | mevcut `rations`, `ration_items`, `paddock_rations`; solver değiştirilmedi |

## V13 değişiklikleri

- Mobil ana sayfa artık sağlık-only `/tasks` yerine Enterprise Dashboard iş kaynağı `/api/v1/dashboard/tasks` kullanır.
- Böylece sağlık kurs/doz görevleri ve bekleyen vadeli ödemeler aynı Dashboard kaynağından gelir.
- Yem stok durumu tek `feed_stock_state()` fonksiyonuna taşındı. Masaüstü Yem Kataloğu ve mobil aynı sınıflandırmayı kullanır.
- Mobil Yem & Stok API'si `stock_state` döndürür; mobil JavaScript yeniden stok kuralı hesaplamaz.
- V12'nin ortadaki `+`, alt menü düzeni ve yatay taşma koruması korunmuştur.
- Enterprise çekirdek sürümü değiştirilmemiştir: V3.9.23 DEV4 Hotfix1.22cr.
