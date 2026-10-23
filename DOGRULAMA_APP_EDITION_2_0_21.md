# App Edition 2.0.21 — Doğrulama

Tarih: 22/10/2026. Referans: gönderilen 12 ekranlı mobil tasarım.

## Tamamlanan kontroller

- Python regresyon paketi: **366/366 test başarılı**.
- Rasyon taslağı JavaScript testleri: başarılı (taslak korunumu, kilitler, sıfırlama, aynı yem güncellemesi, reddedilen güncelleme, rasyon yalıtımı ve depolama hatası).
- Sağlık ajandası JavaScript testleri: başarılı (tarih/sıra, filtre, kontroller, görünüm ve kullanıcı tercihi yalıtımı).
- Yeni Python/JavaScript kaynakları: sözdizimi kontrolü başarılı.
- Tarayıcı: Linux üzerinde başsız Chromium, mobil/touch görünümü.
- Ekran genişlikleri: **320, 360, 390, 430, 768, 900, 1024 ve 1366 piksel**. Ana sayfa, hayvan listesi, hayvan detayı, buzağı detayı, ekleme ve modüller sayfalarında yatay taşma görülmedi.
- 1024 ve 1366 pikselde yeni mobil içerikler gizli, masaüstü Enterprise görünümü ve padok filtresi korunuyor.
- Mobil ana sayfa, yan menü ve + hızlı işlem paneli açma/kapatma: başarılı.
- Canlı arama, tüm kayıtlarda arama, durum filtreleri ve sayfalama: başarılı.
- Hayvan sekmeleri, üst özete geri dönüş ve işlem menüsü: başarılı.
- Özgün Enterprise formuyla tartım kaydetme ve kartta tekrar okuma: başarılı.
- Sağlık planında doğru hayvanın önceden seçilmesi: başarılı.
- Padok taşıma penceresinde doğru hayvanın işaretlenmesi ve taşıma sonrası yeni padokta okunması: başarılı.
- Fotoğraf yükleme ve galeriden tekrar okuma: başarılı.
- Doğum eyleminden anne / buzağı / çiftlikte doğum bilgilerinin hazırlanması: başarılı.
- Mobil formdan erkek hayvan kaydı ve listede tekrar arama: başarılı.
- Tarayıcı işlem testlerinde JavaScript sayfa hatası: **0**.
- Yeni bilgi kartlarında ücretler, gebelik ve sağlık bilgileri gerçek Enterprise kayıtlarından gelir; HTML kullanıcı içerikleri kaçışlanır.
- Çekirdek karşılaştırması: app/server.py içindeki tek değişiklik mobil yapı kimliğidir. Kayıt, finans, stok ve solver fonksiyonlarının kaynak koruma testleri geçti.

## Paketleme

- PyInstaller yeni mobile_reference modülünü ve iki yeni statik dosyayı içerir.
- Actions sözdizimi ve kaynak/EXE smoke listeleri yeni modül ve dosyalara güncellendi.
- Windows kurulum hedefi: CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_21_Setup.exe.
- ZIP kişisel veri, test veritabanı, deneme sunucusu, tarayıcı bağımlılığı veya derlenmiş Python önbelleği içermez.
- Bu ortamda Windows EXE derlemesi ve fiziksel iPhone/Android cihaz testi yapılmadı. Windows EXE, paketteki mevcut GitHub Actions akışıyla üretilir.
