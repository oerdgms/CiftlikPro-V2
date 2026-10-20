# App Edition 2.0.10 doğrulama — 20/10/2026

## 2.0.10 düzenlemesi

Mobil Rasyon Detayı ekranındaki KM, GCAA, HP ve NDF kartlarında bulunan durum rozetleri önceki `top:8px` konumundan `top:5px` konumuna alındı. Değişiklik yalnız bu dört karta, mobil genişliğe ve rozet konumuna uygulanır. Kart boyutları, metinler, bilimsel hedefler, solver ve masaüstü görünümü değişmez.

## Korunan 2.0.9 düzenlemeleri

Telefon ekranında Üreme Merkezi durum filtresi üç dar sütuna bölündüğü için `Gebelik Kontrolü`, `Boş / İşlem Bekleyen` ve `Doğuma Yaklaşan` başlıkları sayaçlara ve yan kutulara taşıyordu.

2.0.9’da filtre HTML’i yalnız sunum katmanında başlık ve sayaç sütunlarına ayrıldı. Mobil CSS iki sütunlu grid, ayrı 28 px sayaç alanı, satır sarma ve tam satır `Tümü` düğmesi kullanır. Enterprise `/reproduction-center` işleyicisi değiştirilmedi; 2.0.10 bu yapıyı aynen korur.

## Pencere denetimi

Aşağıdaki mobil pencere grupları ekran yüksekliği, güvenli alan, kapatma düğmesi ve içerik kaydırması açısından ortak kurallara bağlandı:

1. Hızlı işlem alt sayfası
2. Irk seçimi ve QR/2D kamera sayfası
3. Dashboard kart seçimi
4. Sağlık, finans, rasyon, ilaç/veteriner ve yem işlemi çekmeceleri
5. Padok taşıma penceresi
6. Yem faturası önizlemesi
7. Hızlı gebelik sonucu penceresi
8. Hızlı yem ekleme ve fotoğraf büyütme pencereleri (mevcut güvenli alan kuralları korunarak kontrol edildi)

Tam ekran çekmeceleri `100dvh` kullanır. Alt işlem alanları `safe-area-inset-bottom`, başlıklar `safe-area-inset-top` değerini hesaba katar. Uzun içerik ana sayfayı veya pencere genişliğini büyütmez; ilgili pencerenin gövdesinde kayar. Kapatma düğmeleri en az 44 × 44 px’tir.

## Otomatik doğrulama

- `python3 -m py_compile app/server.py app/mobile_ui.py app/dashboard_performance.py app/agriculture.py app/desktop_launcher.py`: başarılı.
- `node --check app/mobile_assets/mobile.js`: başarılı.
- `python3 -m unittest discover -s tests`: **354 test başarılı**, 189,352 saniye.
- Gerçek QR ve Data Matrix görüntü testi `zxing-cpp 2.3.0` ile geçti.
- 2.0.10 özel testi, dört kart seçicisini ve rozetlerin 3 px yukarı alınan kesin konumunu doğrular. Önceki sürüm/önbellek, filtre başlığı-sayaç, pencere viewport/kaydırma, hızlı sonuç penceresi ve CSS bütünlük kontrolleri de geçti.
- Üreme Merkezi HTTP regresyonu, gerçek sayfa çıktısında üç uzun başlığın `repro-tab-label` alanına dönüştürüldüğünü doğrular.
- Enterprise çekirdek koruma testi geçti. Korunan kayıt işleyicileri ve solver fonksiyonlarının AST özetleri 2.0.8 tabanıyla aynıdır.

## Sürüm ve paketleme

- Enterprise çekirdeği: `3.9.23 DEV4 Hotfix1.22cr` (değişmedi)
- Mobil katman: `AppEdition2.0.10-RationBadgeAlignment`
- Mobil kaynak önbelleği: `2.0.10`
- Windows kurulum hedefi: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_10_Setup.exe`

Bu çalışma ortamında gerçek Windows EXE kurulumu ile fiziksel iPhone/Android cihazı çalıştırılmadı. Otomatik test ve statik responsive denetim başarılıdır; 3 px hizanın saha cihazındaki son görsel kontrolü kurulumdan sonra yapılmalıdır. 2.0.8 performans doğrulaması `docs/history/DOGRULAMA_APP_EDITION_2_0_8.md` içinde korunur.
