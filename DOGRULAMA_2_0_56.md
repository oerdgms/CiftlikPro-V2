# 2.0.56 doğrulama — 01.11.2026

Temel: 2.0.55.

- Hedefli son test koşusu: 61 test / 51,841 saniye, tamamı başarılı. Giriş, çoklu işletme, Enterprise arayüz/çekirdek snapshot, PWA, pilot yeniden bağlanma ve fotoğraf önizleme testleri dahil.
- Yeni giriş testleri: herkese açık alanda yalnız işletme adlarının ve kaçışlı metinlerin bulunması; seçili işletmeyle oturum/hatırlama çerezi oluşturma; doğru şifre fakat yetkisiz işletmede oturum oluşturmama; izin verildikten sonra giriş; hatalı şifrede seçimi koruma; geçersiz işletme/pasif hesap; eski alan olmadan ilk işletmeye giriş; lisansın zorunlu kalması.
- İlk hedefli koşuda eski testte sabit 2.0.55 varlık metni vardı; sürüm bilgisi ortak release_info.VERSION üzerinden kontrol edilecek şekilde güncellendi. Son koşu geçti.
- Chromium: 320 / 390 / 412 / 820 / 1366 px genişlikte giriş alanları, işletme seçimi, şifre düğmesinin kutu içinde kalması, PWA bağlantısı ve taşma kontrolü başarılı. JavaScript hatası yok.
- Tam fotoğrafın yanıtı bilerek bekletildi: DOM yüklenirken işletme alanı ve giriş düğmesi kullanılabilir kaldı. Küçük fotoğrafın göründüğü ilk kare yerel olarak gözle incelendi. Tam fotoğrafın resource timing başlatıcısı link/preload, başlangıç yaklaşık 15 ms. Tam fotoğraf açılması için ağ süresinin sıfır olduğu iddia edilmez.
- Tarayıcı akışları: seçilen ikinci işletmeye doğrudan giriş; son başarılı seçimin sonraki giriş ekranında korunması; doğru personel şifresiyle yetkisiz üçüncü işletmede oturum çerezi oluşturulmaması; JavaScript kapalıyken izinli işletmeye giriş.
- server.py ve Enterprise çekirdek kaynak snapshotları 2.0.55 ile aynı. Veritabanı şeması ve iş hesapları değiştirilmedi. Tam genel test paketi tekrar çalıştırılmadı.
- Sürüm eşitleme, Python sözdizimi ve ZIP CRC kontrolü yapıldı. Windows EXE veya fiziksel iOS/Android testi yapılmadı. İşletim sisteminin PWA açılış ekranı bu sayfa düzenlemesinin dışındadır.
