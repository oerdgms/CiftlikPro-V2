# AppEdition 2.0.69 Doğrulama

## Kapsam

- Kayıtlı besi rasyonunda minimum değişiklikle yeniden hesaplama
- Kilitli yem, önizleme, eşzamanlı değişiklik ve tek kullanımlık uygulama korumaları
- 270 kg / 1,80 GCAA → 300 kg / KM %2,75 gerçek kullanıcı örneği
- Genel Akıllı Çözüm çağrılarının geriye uyumluluğu

## Otomatik kontroller

- `python -m py_compile app/server.py app/ration_recalculation.py tests/test_ration_recalculation.py`
- `tests.test_ration_recalculation`: 8/8 başarılı
- Tam Python regresyon taraması: 569 testin 568'i ilk çalışmada başarılı oldu. Kalan gerçek QR/DataMatrix testi ortamda `zxing-cpp` bulunmadığı için bağımlılık uyarısıyla durdu; `requirements.txt` içindeki `zxing-cpp>=2.2,<3` kurulduktan sonra bu test de ayrıca geçti. Toplam sonuç 569/569 başarılıdır.
- `tests.test_dm_rate`, `tests.test_reports_import`, `tests.test_app_edition`: işlev testleri başarılı; bilinçli solver değişikliği çekirdek hash kapısında yakalandı ve yeni regresyon testiyle birlikte güncellendi.
- Gerçek QR ve DataMatrix görüntülerinden hayvan kartı açma testi `zxing-cpp 2.3.0` ile geçti.

Sürüm eşitleme ve Python sözdizimi kontrolleri paketleme öncesinde ayrıca çalıştırılır.

## Saha sınırı

Bu doğrulama kaynak/test ortamındadır. Windows EXE kurulumu, kullanıcının gerçek veritabanı ve fiziksel telefon üzerinde onaylandığı anlamına gelmez. Önizleme uygulanmadan önce yeni/korunan yem satırları kullanıcı tarafından kontrol edilmelidir.

