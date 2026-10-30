# AppEdition 2.0.48 Doğrulama

Yerleşim değişikliği: yeniden hesaplama alanı masaüstü Hayvan Profili başlığı ve özetinin altına, mobilde profil bilgilerinin altına taşındı. Form kopyalanmadı; mevcut düğüm taşındı. Yerleşim gözlemcisi profil bulunduğunda kapanır; sürekli DOM taşıması yapmaz.

30 ilgili test geçti (test_app_edition ve test_ration_recalculation), 37,284 saniye, OK. Chromium'da 320, 390, 412 ve 1366 pikselde tek formun doğru profil altında görünmesi ve alanın ekrana sığması kontrol edildi. Mobilde gerçek yeniden hesaplama, önizleme ve aynı rasyona uygulama akışı da geçti. JavaScript hatası gözlenmedi. Masaüstü ve mobil ekranlar görsel olarak incelendi.

server.py ve ration_recalculation.py, 2.0.47 ile byte düzeyinde aynı. Önceki 499 testlik genel tarama 2.0.47'ye aittir; bu yerleşim değişikliğinde 30 ilgili test çalıştırıldı. Sürüm eşleme ve JavaScript sözdizimi kontrolü geçti. Fiziksel telefon denemesi ve Windows EXE derlemesi yapılmadı. Mevcut veri klasörü korunarak kaynaktan çalıştırılır.
