# AppEdition 2.0.49 — PWA doğrulaması

Tarih: 31.10.2026. Temel: 2.0.48.

## Değişiklikler

- Kurulum rehberi girişte, Modüller altında ve mobil yan menüde erişilebilir.
- Android tarayıcı yükleme isteği, iOS paylaşım yönergesi ve standalone durumu.
- HTTPS gerekliliği ve Tailscale Serve kurulum belgesi.
- Ayrı maskable Android ve 180×180 Apple simgeleri, aynı manifest kimliği/kapsamı.
- Altı saniye süreli kullanıcı başlatmalı sürüm kontrolü; açık form otomatik yenilenmez.
- Mevcut bağlantı kesilmesi ekranı korunur; takılan gezinme isteği sekiz saniyede
  bağlantı ekranına düşer. POST istekleri service worker tarafından işlenmez.
- Önbellekte yalnız bağlantı ekranı ve dört herkese açık simge tutulur.

## Sonuçlar

- Genel unittest taraması: 502 test / 266,017 saniye. 501 test geçti;
  gerçek QR/DataMatrix testi test ortamındaki eksik `zxing-cpp` nedeniyle başarısızdı.
  Zaten requirements içinde olan 2.3.0 bağımlılığı kurulduktan sonra bu test
  tek başına tekrar çalıştırıldı ve 0,780 saniyede geçti. Tam tarama ikinci kez çalıştırılmadı.
- Son paketleme değişikliğinden sonra PWA HTTP/simge ve sürüm kontrolleri:
  8 test / 2,527 saniye, tamamı başarılı.
- Chromium otomasyonu: 320, 390, 412, 820 ve 1366 pikselde 25 sayfa/kurulum
  arayüzü kontrolü; dar ekranda kurulum penceresi yatay taşmıyor.
- 10 PWA akış kontrolü başarılı: 2.0.48 worker güncellemesi ve eski önbellek
  temizliği sırasında formun korunması; yükleme isteğinin tek kullanımı;
  güncellemede iptal/onay; süre aşımı; bağlantı kesilmesi/başarısız yeniden deneme;
  tekrar bağlanmada sayfa/filtre ve oturum denetimi; iOS/standalone/HTTP yönergeleri.
- Tarayıcı JavaScript hatası yok. Kurulum penceresi görsel olarak incelendi.
- Python/JavaScript sözdizimi ve `scripts/sync_release.py --check` başarılı.
- `app/server.py`, `app/ration_recalculation.py`, `dm-rate.js` ve `dm-rate.css`
  2.0.48 ile bayt düzeyinde aynı. İş kuralları ve rasyon motoru değiştirilmedi.

## Sınırlar

Testler geçici veritabanları üzerinde yapıldı. Canlı işletme verisine erişilmedi.
iOS, standalone ve güvensiz bağlantı yönergeleri platform özellikleri taklit edilerek
kontrol edildi; gerçek iPhone/Android yüklemesi ve işletmenin HTTPS/Tailscale
erişimi henüz doğrulanmadı. Windows EXE üretilmedi.

Kullanım için PWA_KURULUM.md dosyasını izleyin. Normal HTTP IP erişimi çalışmaya
devam eder; tam PWA/çevrimdışı bağlantı ekranı için HTTPS gerekir.
