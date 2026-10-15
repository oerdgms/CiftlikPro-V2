# App Edition 2.0.7 — 15/10/2026 mobil rasyon ve rapor düzeltmesi

Temel: AppEdition 2.0.6 tam paketi. Normal giriş adresi ve 8953 portu aynıdır.

| Ekran görüntüsündeki sorun | Değişiklik |
|---|---|
| Rasyon miktarı kesiliyor, düğmeler sıkışıyor | Yem adı ve miktar ayrı satırlar; geniş miktar alanı ve 44 px düğmeler. Genel form dolgusu ve sayı alanının yerel okları miktar alanından ayrıldı. |
| Kilit simgesi yem görselinin üstünde | Aynı kilit düğmesi yem adının yanında ayrı bir alanda. |
| Kilit açılmasına rağmen yeni miktar kaydolmuyor | Formun satır dışında tuttuğu gizli kilit alanı, düğmenin durumu ile eşitlenir. Kilit açılıp miktar kaydedilebilir; yeniden kilitlenebilir. |
| Silme simgesi çift görünüyor | Tek çizim; düğmenin mevcut işleyicisi korunur. |
| Yem Ekle / Kaydet çubuğu alt menü arkasında | Gerçek işlem çubuğu sınıfı menü ve güvenli alan yüksekliğine göre hizalanır. |
| Raporlar sola kayıyor | Sekmeler ve form alanları esnek sütunlara alındı; tarih alanlarının doğal minimum genişliği ve ek yatay kırpma taşıyıcıları giderildi. |
| Uygulanan rapor filtreleri adresten kayboluyor | Tarih aralığı ve hayvan filtreleri mobil rapor açılışında ve sekme değişiminde korunur. |

2.0.6 paketindeki önceki düzeltmeler dahildir. Mobil CSS/JS önbellek anahtarı ve Windows kurulum dosyası 2.0.7 olarak güncellenmiştir. Paket kaynak kod ve GitHub Windows kurulum akışını içerir; hazır EXE/APK/IPA içermez.

Doğrulama ayrıntıları: `DOGRULAMA_APP_EDITION_2_0.md`. Gerçek iPhone/Safari cihazı bu ortamda çalıştırılmamıştır; rapordaki iPhone odak/kaydırma davranışının son kontrolü cihazda yapılmalıdır.
