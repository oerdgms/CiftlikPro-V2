# AppEdition 2.0.51 — Ortak finans ve uygulama erişimi

Temel 2.0.50; tarih 31.10.2026.

## Düzeltmeler

1. Giriş ekranı ve mobil yan menüde Uygulama ve güncellemeler bağlantısı artık
   HTML içinde hazır gelir. Modüller bağlantısı da başlangıçta görünürdür.
   JavaScript yüklenmese bile /app-install adresindeki kurulum yönergeleri açılır.
   Denetleyici hazır olduğunda aynı bağlantı mevcut yükleme/güncelleme penceresini
   açar. Mükerrer düğme oluşturulmaz.
2. İşletmeye Giriş ve Bizde Kalma, masaüstünde dişi/erkek hayvan ve buzağı
   kartlarının finans özetine de eklendi. Mobildeki ortak tarih kuralları kullanılır.
3. Mobil Kayıt ayrıntıları ve işlemler, tüm bağlı finans kayıtlarını açılabilir
   kartlarla gösterir. Tarih, tür ve tutar özet satırında; açıklama, ödeme, vade
   ve mevcut finans düzenleme bağlantısı içeridedir. Uzun açıklama tam genişliği
   kullanır. İlk beş kayıt ile masaüstü tablosunun tekrarı kaldırıldı.
   Maliyet kırılımı ayrı bir açılır bölümde gösterilir. Buzağı iç üretim formu korunur.

## Doğrulama

- 70 hedefli unittest testi / 33,496 saniye, tamamı başarılı. Geçici temel
  veritabanı başlatılarak eski statik arayüz testinin users tablosu önkoşulu sağlandı.
- Sürü kaydı, finans tarihleri, mevcut arayüz sözleşmeleri, PWA, sürüm kimliği,
  mobil hayvan işlemleri, bütün bağlı kayıtlar, HTML kaçışları, toplu kayıtlarda
  hayvana düşen pay ve düzenleme bağlantıları kontrol edildi.
- Chromium: 320, 390, 412, 820, 1024 ve 1366 pikselde 24 giriş/Modüller/hayvan/
  erkek/buzağı kontrolü; ayrıca JavaScript kapalıyken giriş bağlantısından
  yönergelere erişim: toplam 25 kontrol başarılı.
- Dar ekranda uzun açıklama tam satıra yayılıyor; tutar tek satır ve ekran içinde.
  Eski finans tablosu mobil ayrıntılar içine taşınmıyor. Sekiz test kaydının tümü
  görüntüleniyor. JavaScript hatası yok.
- 390 piksel mobil ayrıntı ve 1366 piksel masaüstü süre ekranları görsel incelendi.
- Python / JavaScript sözdizimi ve scripts/sync_release.py --check başarılı.
- app/server.py ve app/ration_recalculation.py 2.0.50 ile aynı; finans hesapları,
  solver, veri tabanı şeması ve kayıt işleyicileri değiştirilmedi.

Genel 502+ test taraması bu sürüm için yeniden çalıştırılmadı. Canlı işletme
verisine erişilmedi; fiziksel telefon ve Windows EXE testi yapılmadı.

Güncellemeden önce yedek alın. Bu paketi çiftlik bilgisayarında mevcut veri konumunu
koruyarak çalıştırın. Telefonda Uygulama ve güncellemeler → Güncellemeyi kontrol et
→ Yeni sürümü aç. PWA simgesini tekrar eklemek gerekmez. Sunucuda çalıştırılan
yeni sürümü açma düğmesi, sunucuya ZIP indirip kurmaz.
