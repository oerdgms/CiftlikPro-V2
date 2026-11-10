# AppEdition 2.0.58

2.0.57 üzerine geliştirilmiştir. Mevcut işletme verileri, fotoğraflar, rasyon ve finans hesapları korunur. Çekirdek server.py, önceki paketin dosyasıyla bayt düzeyinde aynıdır.

## İşletme girişi

- İzinli girişte şifre yalnız bir kez doğrulanır. İzin reddi, yanlış şifre, pasif hesap ve lisans kontrolleri korunur.
- Ortak hesapların işletme veritabanına kopyası değişiklik imzasıyla kontrol edilir. Eşzamanlı eşitlemeler sıraya alınır. Fotoğraf istekleri bu işlemi başlatmaz.
- Yetki ve pasiflik bilgileri her HTTP isteğinde ana hesaptan okunur. İstekler arasında oturum yetkisi önbelleğe alınmaz.
- API oturumu açılırken hesap kopyası zorunlu doğrulanır. Yedek geri yüklemesi eşitleme imzalarını temizler.
- Giriş hatası boş yanıt yerine seçili işletme korunarak açıklamalı giriş formuna döner. Şifre URL'ye konulmaz ve giriş isteği otomatik tekrarlanmaz.
- GET sayfası yanıt başlıklarından önce hata verirse okunabilir yeniden deneme ekranı döner. Veritabanı kilidinde 503 ve no-store kullanılır. Ayrıntılı hata sunucu günlüğüne yazılır.

## Giriş görünümü

- Mobil işletme, kullanıcı adı ve şifre alanları 44 px. Yazı boyutu 16 px korunur.
- Güncelleme/ana ekrana ekleme erişimi 36 px yüksekliğinde küçük bir bağlantıdır. Güncelleme penceresinin işlevleri korunmuştur.
- Alanlar alt bölümde toplanır, arka plan fotoğrafı daha görünür kalır. Küçük ekranlarda da alanlar sığar.
- Otomatik odak kaldırılmıştır. Kullanıcı giriş sırasında İşletme açılıyor mesajını görür. Tarayıcı geri dönüşünde giriş düğmesi tekrar açılır.

## Bağlantı ve buton taraması

- İşlem günlüğündeki Ayarlara Dön, İşletme Ayarları sayfasına gider. Eski /settings adresi de doğru sayfaya yönlendirilir.
- Mobil menüde Ayarlar ile aynı hedefi tekrarlayan İşletme Bilgileri bağlantısı yerine tek İşletmeler / Değiştir bağlantısı bulunur.
- Rapor merkezinin üstündeki yinelenen Hızlı PDF kısayolu kaldırılmıştır. Rapor bölümündeki PDF, Excel ve önizleme işlemleri korunur.
- Kayıt ekleme, düzenleme, silme, filtreleme, yedekleme ve rapor dışa aktarma işlemleri topluca kaldırılmamıştır.

## Çalıştırma

Çalışan eski sunucuyu kapatın. Mevcut veri ve işletme klasörlerini değiştirmeden bu paketin KAYNAKTAN_CALISTIR.bat dosyasını çalıştırın. Telefon uygulamasında Uygulama ve güncellemeler bölümünden güncellemeyi kontrol edin. Bu paket kaynak dağıtımıdır; Windows EXE derlenmemiştir.
