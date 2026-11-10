# AppEdition 2.0.52 — Ana modüllerde hızlandırma

Temel: 2.0.51. Tarih: 31.10.2026.

## Kapsam

15 ana ekran ölçüldü: ana sayfa, Modüller, hayvan listesi, hayvan kartı, Padoklar,
Sağlık, Üreme Merkezi, Finans, finans raporu, Süt, Tarım, Yem/Stok, Rasyonlar,
rasyon çalışma masası ve Besi Performansı.

- Besi Performansı'nda tartımlar iki kez okunmaz. Erkek besi hayvanlarının
  tartımları aynı sıralama ve SQLite satır biçimi korunarak toplu okunur.
  Bu toplu okuma yalnız /performance içinde çalışır; dişi hayvanların tartımları
  diğer kartlarda eski kuralla okunur.
- Aynı sayfa açılışı boyunca aynı bağlantı/padok/rasyon/tarih aralığına ait
  maliyet okumaları ve tekrarlanan ayar/gebelik/yem fiyatı/stok okumaları yeniden
  kullanılır. Hesaplar HTTP isteği bitince silinir. POST işlemleri kapsam dışıdır.
- Eski kayıt bakımı ve günlük stok işleme tamamlanmadan okuma tekrar kullanımı
  açılmaz. Aynı bağlantıdaki veri değişikliği yeni bir okuma anahtarı oluşturur.
- Geçmiş rasyon, padok hareketi, finans, süt, kızgınlık, tedavi ve veteriner
  sorgularına 12 benzersiz olmayan indeks eklendi. Kayıtlar değiştirilmez.
- Mevcut sayfalama, filtreler, özetler, hedefler ve maliyet kuralları korunur.
  Sunucuda kaynak düzeyinde değişen işlevler yalnız App (aynı tartımı tekrar okumama
  ve bakım sonrası okuma etkinleştirme) ve male_weight_performance (aynı veriyi
  ortak okuma yordamından alma) olarak snapshot ile sınırlandırıldı.

## Ölçüm

Canlı işletme verisi kullanılmadı. Geçici veritabanında 29 erkek + 31 dişi,
125 günlük dönem ve tarihli yem fiyatlarıyla yerel HTTP ölçümü yapıldı.

| Ekran | Önceki SQL sayısı | Sonraki SQL sayısı | Azalma |
|---|---:|---:|---:|
| Besi Performansı | 10.038 | 539 | %94,6 |
| Üreme Merkezi | 410 | 199 | %51,5 |
| Hayvan kartı | 749 | 713 | %4,8 |

Diğer ekranlarda aynı veri setinde sorgu sayısı genellikle değişmedi; geçmiş
tablo indeksleri büyüyen veri kümelerinde sorgu taramasını azaltmak içindir.
Bütün ekranlar için aynı hız artışı iddia edilmez. Yerel süreler, gerçek telefon,
çiftlik bilgisayarı ve VPN ağındaki süreler değildir. Ham karşılaştırma
tests/module_performance_benchmark.json dosyasındadır.

## Testler

- Genel tarama: 519 test / 282,295 saniye. 518 başarılı; gerçek QR/DataMatrix
  testi ortamda zxing-cpp bulunmadığı için başarısızdı. requirements içinde zaten
  yer alan zxing-cpp 2.3.0 kurulduktan sonra ilgili test 0,823 saniyede geçti.
  Genel tarama ikinci kez çalıştırılmadı.
- Son kapsam düzeltmesinden sonra 28 hedefli test / 24,825 saniye: tamamı başarılı.
  Bunlar toplu tartımın yalnız Besi'de çalışması, dişi tartımlarının korunması,
  finans/maliyet eşitliği, filtre/toplam/metin eşitliği, yeni fiyat/ayar/tartımın
  sonraki istekte görünmesi, aynı bağlantıdaki değişiklik, eşzamanlı istek ayrımı,
  hata sonrasında temizlenme, indekslerin idempotansı, dashboard ve rasyon
  yeniden hesaplama kontrollerini kapsar.
- Chromium: 390 ve 1366 pikselde 15 ekran / toplam 30 kontrol başarılı.
  Besi'de hayvan açma ve tamamlanan filtreye geçiş kontrol edildi. JS hatası yok.
- scripts/sync_release.py --check ve Python sözdizimi kontrolü başarılı.
- Rasyon çözüm algoritmaları ve ration_recalculation.py değiştirilmedi.

Windows EXE üretilmedi. Gerçek telefon üzerinde hız ölçümü henüz yapılmadı.

Güncellemeden önce yedek alın. Bu kaynak paketini mevcut veri konumunu koruyarak
çiftlik bilgisayarında çalıştırın. Telefonda Uygulama ve güncellemeler →
Güncellemeyi kontrol et → Yeni sürümü aç seçin. PWA simgesi yeniden eklenmez.
