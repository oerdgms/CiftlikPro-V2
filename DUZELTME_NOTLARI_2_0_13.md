# AppEdition 2.0.13 – Performance + Mobil Ana Sayfa

- Üstteki 4 özet kartı ile Bugünün İşleri arasındaki dikey boşluk 6 px azaltıldı.
- Global + butonu Yem & Stok etiketini kapatmaması için 10 px yukarı ve sağ kenara daha yakın konumlandırıldı.
- Aynı GET / isteğinde masaüstü dashboard ve App Edition mobil sunumunun tekrar çağırdığı `dashboard_export_tasks` sonucu request-scope içinde yeniden kullanılıyor. Kayıt/iş kuralı değişmedi.
- 2.0.12 dashboard indeksleri ve N+1 azaltmaları korunuyor.
- Mobil asset cache sürümü 2.0.13 yapıldı.
