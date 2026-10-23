# App Edition 2.0.33a — GitHub Test Düzeltmesi

23/10/2026. Temel: 2.0.33 Canlı Metin Arama tam kaynak paketi.

## Hatanın nedeni

GitHub'da 434 testten biri, Sürü Özeti içinde `/dairy-status` bağlantısını bekliyordu. Bu bağlantı, istenen yeni ana sayfa düzeninde kaldırılmıştı. Uygulamanın ürettiği yeni özet doğruydu; test eski tasarımı doğrulamaya devam ediyordu.

## Düzeltme

`tests/test_interface_parity.py` yeni tasarıma uyarlandı. Manuel olarak sağmal belirlenen 12 hayvanın hem mobil hem masaüstü özetine aynı sayıyla yansıdığı ve erkek sayısının doğru olduğu kontrolleri korunur. Her iki Sağmal kartının `/all-animals?group=lactating` filtresini açması ve kaldırılan Laktasyon Belirle kısayolunun özetlerde bulunmaması doğrulanır.

Mevcut HTTP kontrolü, ana sayfadaki yazılı Ana Sayfayı Düzenle düğmesini ve düzenleyici bağlantısını da kontrol eder. Test kaldırılmadı, atlanmadı; yeni istenen davranışa göre güncellendi.

Uygulamanın `app/` kaynakları, kayıt işlemleri, veritabanı, sürü hesaplamaları, kurulum tanımı ve GitHub Actions akışı 2.0.33 ile birebir aynıdır. Bu nedenle derleme ve Windows çıktı adı 2.0.33 olarak kalır.

## Kurulum

1. ZIP içindeki tam kaynakları GitHub deposuna aktarın; `tests/test_interface_parity.py` dosyasının da güncellendiğinden emin olun.
2. Yeni kaynakla Actions → CiftlikPro Windows Kurulum → Run workflow çalıştırın.
3. Üretilen `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_33_Setup.exe` dosyasını kurun.

Önceki başarısız çalışmayı yeniden denemek eski kaynakları kullanabilir. Önce güncellenen kaynakları depoya aktarın. ZIP hazır EXE içermez.

## Doğrulama

- Eski paketle bildirilen hata yeniden üretildi: 13 arayüz testinden yalnız eski `/dairy-status` beklentisi başarısız oldu.
- Düzeltilen 13 arayüz testi geçti. Ardından GitHub'daki `python -m unittest discover -s tests` komutuyla 434 testin tamamı geçti.
- Tam taramada mevcut gerçek QR / DataMatrix görüntü testi de çalıştı; test atlanmadı. Python 3.12 ve mevcut requirements kapsamındaki zxing-cpp 2.3.0 kullanıldı.
- Bütün `app/` dosyaları, Windows paketleme tanımları ve GitHub Actions akışı 2.0.33 ile bayt düzeyinde aynı kaldı.
- Windows EXE bu ortamda derlenmedi; yeni kaynakla mevcut GitHub Actions akışından oluşturulur.
