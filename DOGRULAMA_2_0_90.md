# 2.0.90 — Doğum kaydında iç üretim değeri

- Doğum Yaptı penceresi ve Yeni Hayvan > Çiftlikte Doğdu ekranında isteğe bağlı Doğum / İç Üretim Değeri (₺) alanı bulunur.
- Sıfır veya boş tutar maliyet kaydı oluşturmaz. Sonradan buzağı kartından eklenebilir.
- Pozitif tutar doğum tarihiyle, 1 adet üzerinden mevcut Doğum Maliyeti türünde saklanır; mevcut kayıtlarla uyumluluk için veri türü adı değiştirilmez.
- Buzağı ve iç maliyet aynı veritabanı işleminde oluşturulur. Sonraki adım hata verirse ikisi de geri alınır.
- Anne üretim katkısı mevcut hesaplama üzerinden buzağı maliyetinden türetilir; kasa/finans defterine nakit gelir veya gider yazılmaz.
- Sonradan tutar değiştirildiğinde tek doğum maliyeti güncellenir. Aynı küpeyle tekrar kayıt ikinci buzağı veya maliyet oluşturmaz.
- Negatif, geçersiz veya sonsuz tutarlar reddedilir. Pozitif değer yalnız çiftlikte doğan buzağılara kaydedilebilir.

Doğrulama: yeni kayıt + anne maliyetine yansıma + nakit oluşturmama, boş değer + sonradan giriş, tutar düzenleme + tekrar kayıt koruması, geçersiz tutarların kayıt oluşturmaması ve hata durumunda birlikte geri alma HTTP/veritabanı testleriyle kontrol edildi. Oluşturulan formun JavaScript sözdizimi ve sürüm dosyalarının eşitliği de kontrol edildi.

Test sonucu: Tam taramada 581 testin 580’i geçti (303,7 sn). Barkod kütüphanesi yüklenmeden başlatılan süreçteki tek bağımlılık hatası, kurulum tamamlandıktan sonra ilgili gerçek QR/DataMatrix testi yeniden çalıştırılarak giderildi; tekrar test başarılı (0,7 sn). Toplam 581 testin tamamı bu iki çalıştırmada doğrulandı. Gerçek Windows EXE derlemesi veya fiziksel iOS cihaz testi bu ortamda yapılmadı.
