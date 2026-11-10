# 2.0.59 doğrulaması — 5 Kasım 2026

## Otomatik kontroller

- Tam keşif: 563 test, 561 ilk çalıştırmada geçti. İki başlangıç başarısızlığı aşağıda açıklandı ve ikisi de yeniden çalıştırılarak geçti.
- Çekirdek kaynak anlık görüntüsü: yalnız bu sürümde bilinçli değiştirilen `sync_daily_paddock_feed_stock` fonksiyonunun SHA-256 referansı güncellendi. Mevcut diğer işleyici ve solver referansları korundu; karşılaştırma testi yeniden geçti.
- QR/DataMatrix testi: ilk süreçte eksik zxing-cpp bağımlılığı nedeniyle çalışmadı. Paket requirements.txt dosyasındaki sürüm aralığına uygun zxing-cpp kuruldu; gerçek QR ve DataMatrix görüntüsü testi yeniden geçti.
- Yeni 5 regresyon: değişmeyen tüketimde sıfır yazma ve sıfır maliyet yeniden oluşturma; hayvan sayısı değişince anında güncelleme; değiştirilmiş stok hareketini onarma; son giriş zamanı değişince sıfır eşitleme/şifre-rol-aktiflik değişince aktarım; sade menü ve tüm modül yollarının korunması; zaman ölçümünün hata sonrası temizlenmesi. (İlk maddeler aynı test içinde birlikte doğrulanır.)
- Sürüm eşitleme kontrolü geçti: release_info, RELEASE.json, PWA önbellek adı, installer ve Windows workflow aynı sürümde.

## Tarayıcı

Chromium 153 üzerinde 320, 390, 820 ve 1366 piksel genişliklerde giriş/ana sayfa kontrol edildi. Üç mobil genişlikte 6 bağlantılı menü açıldı; Tüm Modüller üzerinden Besi Performansı ekranına geçildi. JavaScript hatası ve son kontrol ekranlarında yatay belge taşması görülmedi. Mobil menü ekran görüntüleri çalışma sırasında görsel olarak kontrol edildi; dağıtım paketine eklenmedi. Bu testler fiziksel iOS/Android veya Windows testinin yerine geçmez.

## Karşılaştırma

`tests/performance_259_benchmark.json`: 2.0.58 ZIP'indeki eski fonksiyon ile yeni fonksiyon aynı yapay SQLite verisi üzerinde beşer kez çalıştırıldı. Tek padok/tek yem/181 günlük stok girişiyle değişmeyen tüketimde eski sürüm her çağrıda 364 satır, yeni sürüm sıfır satır değiştirdi. Miktarlar ve maliyetler mevcut stok regresyonlarıyla doğrulandı. Ortam süreleri müşteri bilgisayarına genellenemez.

İlgili tarayıcı sonuçları `tests/mobile_259_browser_results.json` dosyasındadır. Kullanıcı veritabanı bu pakete dahil değildir. Besin kataloğu değerleri ve solver formülleri değiştirilmedi. EXE derlenmedi.
