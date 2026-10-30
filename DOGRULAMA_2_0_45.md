# AppEdition 2.0.45 Doğrulama

- Tam regresyon: 486 test, 266,002 saniye, OK. Dokuz yeni KM/protein testi dahildir.
- Yeni test kapsamı: tüm ağırlıklarda %2,50 varsayılanı, özel yüzdenin korunması, eski veritabanına veri kaybetmeden alan ekleme, ayrı rasyon tercihi, hatalı sayıları reddetme, yüzdeyi çözüm motoruna ve yeni kayda aktarma, süt hesabını koruma ve eski katalog HP verisinde özet/solver eşitliği.
- Chromium: 320, 390, 412 ve 1366 pikselde 12 kayıt/önizleme/çözüm geçişi kontrolü geçti. Yatay taşma veya JavaScript hatası gözlenmedi. KM hedefi yem miktarı taslağında sabit kaldı; günlük HP gramı canlı değişti.
- Gerçek solver denemesi: aynı altı yemle 400 kg, 1,30 kg/gün artış hedefi; %2,50 için hedef 10,00 kg KM, bulunan 9,656 kg; %2,70 için hedef 10,80 kg KM, bulunan 10,420 kg. İlk sonuç feasible, ikinci limited. Mevcut toleranslar ve açık sapma uyarıları korunur.
- Sürüm eşleme kontrolü, Python kaynak ayrıştırma ve yeni JavaScript sözdizimi kontrolü geçti.
- İş kuralları için kaynak özeti yalnız istekte değiştirilen 11 tanımda güncellendi. Kalan çekirdek tanımlar için önceki karşılaştırma korunur.

Fiziksel iPhone/Android ve Windows EXE denemesi yapılmadı. Tarayıcı kontrolleri benzetilmiş ekran genişliklerindedir. Testlerde geçici veritabanları kullanıldı; kullanıcının işletme verilerine erişilmedi.

Protein referans kontrolü: NASEM 2016 Chapter 20 errata 20-1/20-2 tablolarında MP gereksinimi ile diyet HP değerlendirmesi ayrı büyüklüklerdir. Bu sürüm tam RDP/RUP veya MP arzı modeli eklemez. Yapılan düzeltme HP arzı hesabının özet, canlı ekran ve solverde tutarlı olmasıdır.
