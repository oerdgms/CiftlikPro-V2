# 2.0.42 → 2.1 Mobil Pilot Kontrolü

28/10/2026. Temel: kullanıcının stabil 2.0.41 sürümü. 2.0.42 pilot hazırlığıdır; 2.1 kararlı onayı değildir. Aşağıdaki fiziksel cihaz denemeleri henüz yapılmamıştır.

Kurulum öncesi mevcut yedekleme merkezinden bir yedek alın. Güncel 2.0.41 kurulumunu ve kaynak paketini geri dönüş için saklayın. Saha testinde deneme hayvanı/kayıtları kullanın; gerçek finans ve stok verisini gelişigüzel değiştirmeyin.

| Deneme | Beklenen sonuç | iPhone | Android | Windows |
|---|---|---|---|---|
| 2.0.41'den güncelleme | Kaynak/EXE `/app-build.json` sürümü 2.0.42; mevcut veri korunur | Bekliyor | Bekliyor | Bekliyor |
| Ana ekran simgesinden açma | Aynı işletme adresi ve mevcut oturum/giriş akışı açılır | Bekliyor | Bekliyor | — |
| Hayvan ve buzağı ekleme | Doğru tür, yaş, padok ve sayaç; masaüstü/telefon aynı kaydı görür | Bekliyor | Bekliyor | Bekliyor |
| Fotoğraf kamera/galeri | Doğru hayvana yüklenir; form ekrana sığar | Bekliyor | Bekliyor | Bekliyor |
| Sağlık ve çoklu uygulama | Seçilen hedefler/dozlar doğru; ilgili giderler tek işlem olarak tutarlı görünür | Bekliyor | Bekliyor | Bekliyor |
| Finans kayıt/düzenle | Türkçe tutar, ödeme/vade, hayvan bağlantısı doğru; mükerrer kayıt yok | Bekliyor | Bekliyor | Bekliyor |
| Padok taşıma | Kapasite, hayvan listesi, geçmiş ve sayaçlar aynı sonucu verir | Bekliyor | Bekliyor | Bekliyor |
| Rasyon/bilimsel panel | 2.0.41 yerleşimi korunur; aç/kapat, miktar değişimi ve kaydetme çalışır | Bekliyor | Bekliyor | Bekliyor |
| Süt sabah/akşam | Değişen hayvanlar doğru kaydedilir; toplam/ortalamalar tutarlı | Bekliyor | Bekliyor | Bekliyor |
| Kaydırma, klavye, çift dokunma | Titreme/yan kayma yok; son düğme ve kapatma alanı erişilebilir | Bekliyor | Bekliyor | Bekliyor |
| Wi-Fi/VPN kesip yeniden açma | Uygun bağlantı ekranı; yeniden deneme çalışır, filtreli sayfaya dönülür | Bekliyor | Bekliyor | Bekliyor |
| Açık form sırasında güncelleme | Otomatik zorunlu yenileme yok; taslak kendiliğinden silinmez | Bekliyor | Bekliyor | Bekliyor |
| Sunucuyu yeniden başlatma | Uygulama erişimi geri gelir; kayıtlar korunur, tekrar giriş gerekirse açıkça görülür | Bekliyor | Bekliyor | Bekliyor |

HTTPS/ana ekran kurulumu ve service worker desteği gerçek erişim adresinde ayrıca kontrol edilmelidir. Yerel/VPN HTTP üzerinden canlı uygulama çalışabilir; bu, çevrimdışı ekranın her cihazda etkin olduğu anlamına gelmez. Bu paket HTTPS veya Tailscale kurulumunu değiştirmez.

Bağlantı yokken yeni kayıt kuyruğu yoktur. Sunucuya ulaşılamayan bir kaydın gönderimini körlemesine tekrarlamayın; bağlantı geri geldiğinde kayıt listesini kontrol edin.

2.1'e kabul: Windows derlemesi ve bu tablodaki kritik veri akışları başarılı; veri kaybı/mükerrer kayıt yok; iPhone ve Android'de açılış, güncelleme, kaydırma ve yeniden bağlanma doğrulanmış olmalı. Sonuçları cihaz/model, erişim şekli (LAN/VPN/HTTPS), tarih ve gözlenen hata ile kaydedin.
