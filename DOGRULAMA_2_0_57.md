# 2.0.57 doğrulama — 01.11.2026

- İlk incelemede paylaşılan üç sayfalık PDF'nin metin çıkarım uzunlukları 0/0/0 bulundu. İlk sayfa render edilip yerel olarak incelendi. Belge tarama olduğu için mevcut dijital PDF ayrıştırıcısı tarafından okunamaz.
- Önceki sürümde aynı dosyayla yerel HTTP denemesi 303 hata yönlendirmesi döndürdü. Bu yerel denemede sunucu çökmesi görülmedi; fiziksel Safari/Tailscale bağlantı kesintisi birebir tekrar üretildiği iddia edilmez. Mobilde import anchor bağlantısının rapor giriş ekranına dönmesi doğrulandı.
- Son geniş hedefli koşu: 180 test / 113,329 saniye, tamamı başarılı. İçe aktarma, çoklu işletme, raporlar/ayrıştırıcılar, Enterprise çekirdek snapshot ve arayüz eşliği dahil.
- Son önizleme kaydırma/tarih düzeni ve metin PDF kontrolünden sonra 6 içe aktarma testi / 6,220 saniye, tamamı başarılı. CSV okuma/önizleme/ayrı onay/işletme ayrımı/mükerrer tekrar; taranmış PDF için JSON ve native HTML hata; hatalı/boş dosya; yetki ve başka işletmede önizleme reddi; metin içeren PDF'yi okuyup onay öncesi kayıt eklememe sınandı.
- Tarayıcı: 320 / 390 / 412 / 820 / 1366 px genişliklerinde Veri Aktarımı ve raporlardan dosya seçme ekranına geçiş — beş genişlikte başarılı. Yatay taşma veya JavaScript hatası yok.
- Paylaşılan gerçek taranmış PDF ile aynı pencerede OCR açıklaması, seçilen dosyanın korunması, düğmenin tekrar kullanılabilmesi ve yeni pencere açılmaması kontrol edildi. Bu PDF'den kayıt eklenmedi.
- Sentetik CSV'deki iki kayıt önce önizlendi; ayrı onaydan sonra yalnız seçili ek işletmeye eklendi. İlk işletmeye geçildiğinde bu kayıtlar yoktu. JavaScript kapalıyken aynı taranmış PDF boş sayfa yerine hata/yeniden seçme ekranı gösterdi. Önizlemede üst işletme alanı ve sayfa başlangıcı görünür kaldı.
- server.py değişikliği yalnız yeni sunum/istek modülünü kuran ekleme; çekirdek kaynak snapshotları değişmedi. Son onay mevcut aktarım/yedekleme işleyicisini kullanır. Yem kataloğu değişmedi.
- Python ve JavaScript sözdizimi, sürüm eşitleme ve ZIP CRC kontrolü yapıldı. Tam genel tarama tekrar yapılmadı. Windows EXE/fiziksel iOS/Android testi yapılmadı. OCR özelliği bu sürümde yoktur.

Mobil Raporlar giriş ekranına da doğrudan Hayvan İçe Aktarma kartı eklendi; dosya seçme ekranını açması beş genişlikteki son tarayıcı kontrolünde doğrulandı.
