# App Edition 2.0.7 doğrulama — 15/10/2026

## Kaynak ve kapsam

AppEdition 2.0.6 tam paketi üzerine uygulanmıştır. Yeni kod mobil sunum katmanındadır. `server.py` içinde yalnız AppEdition build etiketi değiştirilmiştir.

- 274 üst seviye fonksiyon/sınıf tanımı önceki paketteki tanımlarla AST olarak aynıdır.
- `server.py`, build etiketi normalleştirildiğinde önceki dosyayla birebir aynıdır.
- Solver, sağlık, finans, stok, üreme ve diğer kayıt işleyicileri değiştirilmemiştir. Veritabanı şeması aynıdır.
- Tarım modülü, masaüstü başlatıcı, yem/ilaç katalogları, gereksinimler ve PyInstaller tanımı önceki paketle birebir aynıdır.
- Mobil kaynakların önbellek anahtarları, kurulum dosyasının adı ve bunları doğrulayan mevcut testlerin sürüm beklentileri 2.0.7 olarak güncellenmiştir.

## Tarayıcı doğrulaması

Chromium 153 üzerinde toplam **431 kontrol başarılı**; JavaScript hatası görülmedi.

| CSS piksel ölçüsü | Sonuç |
|---|---|
| 320 × 720 | Başarılı |
| 360 × 800 | Başarılı |
| 390 × 844 | Başarılı |
| 412 × 915 | Başarılı |
| 820 × 1180 | Başarılı |
| 900 × 1000 | Başarılı |
| 844 × 390, yatay | Başarılı |
| 1024 × 900, masaüstü | Başarılı |
| 1366 × 900, masaüstü | Başarılı |

Mobil kontroller altı kayıtlı yem içeren gerçek Enterprise rasyonu üzerinde yapıldı. Yem adları, eksi/artı, miktar, kilit ve silme düğmelerinin yatay sınırları denetlendi. Tüm rasyon işlem düğmeleri en az 44 × 44 px; miktar alanı en az 16 px yazı boyutundadır. İki basamaklı ve `1234.56` gibi uzun miktarlar için metnin alanın kullanılabilir genişliğine sığdığı ölçüldü. Silmede tek SVG simgesi vardır; eski CSS ikinci simgeyi basmaz.

Yem Ekle / Kaydet çubuğunun alt menünün üstünde kalması, sayfa sonundaki yemin ulaşılabilirliği ve ekleme penceresinin başlık/menü arasına sığması denetlendi. Güvenli alan yüksekliği ayrıca CSS değişkenleriyle taklit edilerek kontrol edildi; bu bir gerçek iPhone güvenli alan testi değildir.

Yalnız geçici test veritabanında şu gerçek işlemler yapıldı:

1. Kilit açıldı; eksi/artı mevcut miktar alanını değiştirdi.
2. Doğrudan miktar girişi ve silme düğmesinin mevcut sıfırlama işleyicisi çalıştı.
3. Kilit açıkken `2.55` miktarı mevcut Enterprise POST formuyla kaydedildi; yeniden yüklemede `2.55` ve açık kilit görüldü.
4. Yeniden kilitleme ayrı kaydedildi; yükleme sonrasında kilit durumu korundu.
5. Geri Al, miktarı, salt okunur durumunu ve gizli kilit kayıt alanını geri getirdi.
6. Raporun tarih aralığı gerçek form üzerinden gönderildi. Tarihler yenileme ve sekme değişiminden sonra adreste korundu.
7. Finans, hayvan ve içe aktarma sekmeleri açıldı. Tarih alanlarına odaklanıp çıkıldığında sayfa ve iç taşıyıcılar yatay kaymadı.
8. Geniş kategori tablosu kendi kutusunda kaydırıldı; belge yatay kaymadı. Mevcut CSV çıktı adresi başarılı yanıt verdi.
9. Rapor menüsü ve kart sınırları kontrol edildi. Masaüstünde mobil menü ve mobil silme dönüşümü çalışmadı.

## JavaScript ve kaynak kontrolleri

- `python3 -m unittest discover -s tests`: **342 test başarılı**, 177,444 saniye. Mevcut 219 tanımlık Enterprise çekirdek koruma testi de dahildir.
- Gerçek QR ve DataMatrix görseliyle hayvan kartına ulaşma testleri, projenin gerektirdiği `zxing-cpp 2.3.0` test ortamına kurularak başarılı çalıştırıldı.
- Mobil JavaScript ve service worker sözdizimi kontrolü: başarılı.
- Python modüllerinin derleme kontrolü: başarılı.
- Mevcut `test_workbench_draft.js`: taslak miktar/kilit koruması, sıfırla çıkarma, aynı yem güncellemesi, ret ve depolama hatası senaryoları başarılı.
- Mevcut `test_health_agenda.js`: tarih sırası, filtre, kayıt kontrolleri ve görünüm seçimi senaryoları başarılı.

## Ortam sınırları

Kullanıcının rasyon ekranındaki miktar kırpılması ve menü arkasında kalan işlem çubuğu başlangıçta Chromium üzerinde tekrar oluşturuldu. Kullanıcının iPhone rapor ekranındaki sola kayma Chromium üzerinde birebir oluşmadı. Rapor taşıyıcıları ve yerel tarih alanlarının genişlikleri düzeltildikten sonra yukarıdaki odak, taşma ve gönderim kontrolleri yapıldı.

Gerçek iPhone/Safari, Android cihazı ve Windows EXE kurulumu bu ortamda çalıştırılmadı. ZIP tam kaynak ve GitHub Windows kurulum akışını içerir; hazır EXE/APK/IPA içermez. Önceki sürümün doğrulama raporu `docs/history/DOGRULAMA_APP_EDITION_2_0_6.md` içinde korunmuştur.
