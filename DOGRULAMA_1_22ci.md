# ÇiftlikPro 1.22ci doğrulama notu — 12/10/2026

1.22ch EXE üretimi ve kurulumu kullanıcı tarafından başarılı olarak bildirildi. Bu paket, o kurulu sürümün üzerine finans tutarlılığı ve yedek güvenliği düzeltmelerini içerir.

## Kontrol kapsamı

Kontroller ayrı test veritabanlarında yapıldı. Kullanıcının çalışan veritabanı bu kontrollerde kullanılmadı.

| Alan | Doğrulanan davranış |
|---|---|
| Hayvan/arşiv maliyeti | Alış, bağlantılı sağlık gideri ve diğer giderler bir kez düşer; net ve maliyet kart/arşivde eşleşir. |
| Buzağı maliyeti | Sağlık ve iç üretim kalemleri buzağı kartı/arşiv netine katılır. |
| Geri tarihli satış | Satış onayı ve arşiv, çıkış tarihindeki aynı maliyeti gösterir. |
| Arşiv araması | Satılan yetişkin/buzağı, kesilen ve ölen/kayıp kayıtlar küpe, takma ad, padok, Türkçe metin, tarih ve nedenle filtrelenir. Arama sonucu sayısı, boş sonuç ve temizleme kontrol edilir. |
| Alış tarihi boş kayıt | Bağlı alış hareketinin tarihi varsa maliyet başlangıcı olarak kullanılabilir. |
| Toplu satış | Üç buzağıya 1.000,01 TL kuruş kaybetmeden dağıtılır; tekrar gönderim çift kayıt oluşturmaz. Bir satışı düzeltme/geri alma diğerlerini bozmaz. |
| Ödeme | Ödendi, geri al ve hemen yeniden ödendi çalışır; iki eşzamanlı gönderim bir tamamlama üretir. Tutar değişikliği ödeme tutarına yansır. |
| Ölüm/kayıp | İlgisiz finans giderini silme hayvanı aktif yapmaz. |
| Süt geliri | 300,01 TL üç hayvana dağıtılır; toplam paylar tam olarak 300,01 TL'dir. |
| Tam yedek | Finans, hayvan ve fotoğraf dosyaları birlikte geri yüklenir. Boş fotoğraf klasörünün durumu da geri yüklenir. |
| Yedek adı | Aynı anda alınan iki yedek birbirini ezmez. |
| Yedek doğrulama | Bozuk ZIP, Windows yol taşması ve başka uygulamanın SQLite dosyası kabul edilmez. |
| Geri dönüş | Şema güncellemesinde hata oluşursa yedek yüklemeden önceki DB/fotoğraflar korunur. |
| Eski yedek | Eski ÇiftlikPro şeması güncellenir; iki kez init_db kayıt çoğaltmaz. Fotoğrafsız eski DB yedeği mevcut fotoğrafları korur. |
| Harici klasör | Günlük yedek, seçili klasörde bir kez oluşur. |
| QR/2D | requirements.txt ile uyumlu zxing-cpp 2.3.0 ile gerçek QR ve Data Matrix PNG görsellerinden hayvan kartı açılır. |
| Ekran kodu | Dashboard, sürü, finans, üreme, satış arşivi, hayvan, buzağı ve yedekleme ekranı HTTP 200 verir; 166 inline JavaScript bloğu sözdizimi kontrolünden geçer. |
| Kaynaktan açılış | Sunucu açılır, lisans ekranı HTTP 200 verir ve ilk otomatik yedek oluşur. |
| Windows yapılandırması | Kurulum AppId'si, veri konumu ve kurulum öncesi DB yedek kuralı korunur; kaynak/Setup/test sürümleri 1.22ci olarak eşleşir. |

## Sınırlar ve sıradaki saha kontrolü

- 1.22ci için Windows EXE derlemesi ve kurulum bu ortamda çalıştırılmadı. Kullanıcının kurulu olduğu doğrulanan sürümü 1.22ch'dir.
- Görsel tarayıcı kontrolü tamamlanamadı: test tarayıcısının indirme çıktısı bozuk/eksikti. Gerçek mobil/masaüstü yerleşimi bu notta doğrulanmış kabul edilmez.
- iPhone kamera izni, fiziksel küpe etiketi/netlik koşulları ve kullanıcının gerçek hayvan/finans toplamları saha kontrolünü bekler.
- Yeni paketi kurmadan önce uygulamanın Yedekleme Merkezi'nden tam yedek alın. Kurulum sonrasında aynı hayvanın kart ve satış arşivindeki gider/maliyet/net değerlerini karşılaştırın.

## Sonuç

- Nihai Python regresyon taraması: **278/278 başarılı**, 161,121 saniye.
- Yeni finans/yedek/arşiv senaryoları: **24/24 başarılı**.
- Üç Python giriş dosyasının derleme kontrolü başarılı.
- Sağlık ajandası ve rasyon taslağı JavaScript testleri başarılı.
- 8 ekran HTTP 200, 166 inline JavaScript bloğunun sözdizimi geçerli. Bu kontrol görsel yerleşim testi değildir.

## Test komutları

```
python -m py_compile app/server.py app/agriculture.py app/desktop_launcher.py
python -m unittest discover -s tests
node tests/test_health_agenda.js
node tests/test_workbench_draft.js
```
