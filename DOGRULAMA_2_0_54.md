# 2.0.54 — Hedef kartı rozet hizası

31.10.2026; temel sürüm 2.0.53.

Yalnız mobil hedef kartı durum rozetlerinin CSS kuralı değiştirildi: top 5→2 px, right 8→11 px, yatay iç boşluk 6→2 px. Sabit 64 px yerine başlık alanını koruyan genişlik sınırı kullanılır. Uzun metin gerektiğinde sarılır; üç noktayla kesilmez.

320, 360, 390, 412 ve 820 px mobil genişliklerinde Yüksek %21 / Yeterli / Hedef altı %1,9 / Aralıkta etiketleriyle gerçek rasyon ekranı kontrol edildi: yatay taşma, kart dışına çıkma ve başlıkla çakışma yok. 1366 px masaüstü rasyon ekranı da açıldı. JavaScript hatası görülmedi.

Server.py ve bütün hesaplama kodları 2.0.53 ile birebir aynı. Sürüm, önbellek ve Windows paketleme kimlikleri 2.0.54 olarak eşitlendi. Bu küçük görsel değişiklik için tam test paketi tekrar çalıştırılmadı. Kaynak pakettir; EXE derlenmedi. Fiziksel telefon testi yapılmadı.

Bilgisayarda yeni kaynak sürümü çalıştırdıktan sonra telefondan Uygulama ve güncellemeler ile güncellemeyi kontrol edip yenileyin.
