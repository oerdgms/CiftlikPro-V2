# AppEdition 2.0.46 Doğrulama

Tam regresyon: 492 test, 265,300 saniye, OK. Altı yeni hazır reçete yaşam döngüsü testi dahil.

Yeni kapsam: sıfır veritabanında dört reçetenin yalnız bir kez oluşması; dört rasyonun HTTP ile silinmesi ve iki yeniden başlatmada geri gelmemesi; ad/miktar/KM oranı/kilit ve miktar geçmişinin korunması; eski sürümde silinmiş kayıtların izleme tablosu olmadan da yeniden eklenmemesi; mevcut hazır reçetelerin güncellemede ezilmemesi; aktif padok koruması ve geçmiş padok atamasında arşivleme.

Chromium 390 px mobil görünümde dört Faz rasyonunun gerçek Sil düğmesi ve onay iletişim kutusuyla silinmesi, ardından sayfa yenilemede yokluğunun korunması geçti. JavaScript hatası yok. Kalıcılık ayrıca yukarıdaki yeniden başlatma testleriyle doğrulandı.

2.0.45 ile karşılaştırmada server.py içindeki mevcut fonksiyon/sınıf tanımlarından yalnız init_db değişti. Solver ve silme korumaları birebir korundu. Sürüm eşleme ve Python sözdizimi kontrolü geçti. Kaynak özeti yalnız init_db için güncellendi.

Kullanıcının işletme verilerine erişilmedi; geçici test veritabanları kullanıldı. Fiziksel iPhone/Android testi ve Windows EXE derlemesi yapılmadı. EXE yerine tam kaynak paketi sağlandı.
