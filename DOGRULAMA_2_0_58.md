# 2.0.58 doğrulama

- Giriş, çoklu işletme, izin reddi, hesap eşitleme, API girişi ve uygulama sözleşmeleri: 49 test geçti.
- Genel taramada 558 test çalıştırıldı. İlk taramada üç dosya yolu kontrolü paket kökü dışında çalıştırıldığı için hata verdi; ilgili dört arşiv testi paket kökünde yeniden çalıştırıldı ve geçti. Sonuçta 557 test doğrulandı. Bir gerçek QR/2D görüntü testi, bu çalışma ortamında zxing-cpp bulunmadığı için doğrulanamadı. Bu test atlanmış veya başarılı gösterilmiş değildir. Bağımlılık mevcut requirements.txt dosyasında yer alır; QR kodu bu sürümde değiştirilmemiştir.
- Aynı hesapların tekrar işletme tablosuna okunmaması, eşzamanlı değişikliğin bir kez uygulanması ve API oturumu öncesi zorunlu kontrol doğrulandı.
- Veritabanı kilidi enjekte edildi: GET isteği 503 ve yeniden deneme ekranı döndü, kilit kalkınca aynı sayfa açıldı. Giriş POST hatası seçili işletmeyi koruyarak forma döndü; şifre URL'ye yazılmadı.
- Kaynak çekirdeği server.py önceki 2.0.57 ile aynıdır. Kayıt işleyicileri ve solver fonksiyonlarının koruma testi geçti.
- Geçici Deneme işletmesinde 59 farklı adresin 104 bağlantı/sorgu varyasyonu tarandı. Son taramada HTTP hata hedefi veya olmayan yerel çapa bulunmadı. Bağlantılar istekle kontrol edildi; kayıt değiştiren formlar topluca çalıştırılmadı.
- Chromium: 320×640, 390×844, 412×915, 820×1180 ve 1366×768 boyutlarında işletme seçimi, kullanıcı/şifre alanları, güncelleme penceresi ve giriş test edildi. JavaScript sayfa hatası görülmedi.
- Aynı tarayıcı testinde hayvan/buzağı, rasyon, ayarlar, raporlar ve veri ekranları açıldı; görünen düğmeler incelendi.
- Yerel testte girişten Deneme ana sayfasının hazırlanmasına kadar yaklaşık 0,73–0,78 saniye ölçüldü. Ölçüm küçük geçici veritabanı ve yerel ağ içindir, Tailscale/telefon saha ölçümü değildir.
- Fiziksel Windows, iOS ve Android cihazlarda çalıştırma bu ortamda yapılmadı. Windows EXE derlenmedi. Kaynak dağıtımı ve sürüm eşleştirmesi kontrol edildi.
