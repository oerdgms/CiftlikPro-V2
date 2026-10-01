# Hotfix1.22ah - Yem eklerken taslak koruma

Rasyon çalışma masasında miktar ve kilit değişiklikleri yaptıktan sonra Yem Ekle ile başka bir yem ekleyebilirsiniz. Sayfa döndüğünde diğer satırlardaki miktar ve kilit taslağı geri gelir; bunları uygulamak için Kaydet gerekir. Aynı yemi seçerseniz çalışma masasında yazdığınız miktar yem ekleme alanına gelir. Bu yemin ekleme alanında onaylanan yeni miktarı korunur. Geri Al mevcut kaydedilmiş miktar ve kilitlere döner.

Taslak yalnız bu sekmede, kullanıcı ve rasyon bazında, yem ekleme dönüşü için tutulur. Başka rasyona taşınmaz. Tarayıcı taslak depolamasını engellerse veri kaybına karşı yem ekleme durdurulur ve önce Kaydet önerilir.

1.22ag günlük görev PDF / Yazdır özelliği korunur. Solver fonksiyonları, hedefler, bilimsel hesaplar ve stok tüketimi değiştirilmedi.

Doğrulama: mevcut 136 Python testi; ek HTTP rasyon ekleme/kaydetme testi; Node ile gerçek taslak betiğinde miktar, kilit, sıfır miktar, aynı yem güncelleme, reddedilen güncelleme, rasyon ayrımı ve depolama hatası senaryoları. Tam tarayıcı görsel testi bu ortamda yapılamadı. Kullanıcı ortamındaki kurulum henüz doğrulanmadı.
