# App Edition 2.0.8 doğrulama — 15/10/2026

## Ölçülen sorun

Kullanıcı `[PERF] Dashboard hazır` satırlarında 0,4–7,2 saniye aralığında değerler bildirdi. Bu mevcut ölçüm Dashboard gövdesini hazırlayan bölümü kapsar; bakım işlemleri, son sunum katmanları ve gzip iletimi ölçümün dışındadır.

Yerel profilde SQL execute/fetchall süreleri baskındı. Aynı açılışta ortak gebelik kaynağı iki, sağlık görevleri iki kez çalışıyor; 300 dişi için `current_pregnancy_record` 1.500 kez çağrılıyordu. Tartım ve stok sorgularındaki tekrarlı taramalar için uygun indeksler bulunmuyordu.

## Karşılaştırmalı performans testi

Önceki sürüm: teslim edilmiş AppEdition 2.0.7. Sonraki sürüm: aynı kaynağa bu performans değişikliği eklenmiş sürüm. Aynı Linux/Python/SQLite ortamında, aynı deterministik yapay veriyle ayrı geçici veritabanları kullanıldı:

- 600 yetişkin hayvan; 300 dişi ve 300 erkek.
- 100 yeni doğmuş buzağı, 900 tohumlama ve 600 eski tip sağlık kaydı.
- 12.000 tartım, 90.000 stok hareketi ve 3.000 finans kaydı.
- Beş ardışık istek; ardından dört istemciyle sekiz eşzamanlı istek. Ön ısıtma/profil isteği istatistiklere dahil edilmedi.
- Süreler oturumlu HTTP isteğinin gzip yanıt gövdesi tamamen alınıncaya kadarki süredir; tarayıcı çizimi dahil değildir.

| Ölçüm | 2.0.7 | 2.0.8 değişikliği |
|---|---:|---:|
| Tek istek ortancası | 0,662 sn | 0,120 sn |
| Eşzamanlı istek ortancası | 1,817 sn | 0,726 sn |
| Eşzamanlı istek en yüksek değeri | 2,111 sn | 0,916 sn |
| Bir açılışta `current_pregnancy_record` gerçek hesap çağrısı | 1.500 | 300 |
| Bir açılışta sağlık planı hesap çağrısı | 2 | 1 |

Süreler kullanıcının gerçek Windows bilgisayarında veya gerçek veritabanında ölçülmedi. Kullanıcıdaki 7,2 saniyenin belirli bir değere düşeceği bu deneyden garanti edilemez.

## Veri güncelliği ve güvenilirlik

12 indeks non-unique olarak mevcut şema hazırlandıktan sonra başlangıçta oluşturulur. Kayıt verileri ve eski iş kuralları korunur. İndekslerin ilk oluşturulması başlangıçta ek çalışma gerektirir; sonraki başlangıçlarda `IF NOT EXISTS` ile tekrar oluşturulmaz.

Yalnız bir Dashboard HTTP isteğinde, bakım/doğum uzlaştırması sonrasındaki ortak okuma sonuçları yeniden kullanılır. Süreli sayfa önbelleği yoktur. ContextVar ile istekler ayrılır; yanıt bittiğinde veya istisna oluştuğunda alan temizlenir. Diğer sayfalar ve POST işlemleri bu okuma paylaşımına girmez.

Altı yeni regresyon testi şu davranışları doğruladı:

1. İndeksler mevcut tablolarda oluşturulur; tekrar başlatma kayıtları değiştirmez. Tartım sorgusu yeni indeksi kullanır.
2. Ortak gebelik sonucu orijinal yardımcıyla aynıdır; aynı açılışın ikinci okuması yeniden SQL çalıştırmaz.
3. Doğum kaydından sonraki yeni açılışta gebe sayısı ve buzağı sayısı hemen güncellenir.
4. Bakım aşamasında, sayaçlar başlamadan önce okumalar tazedir.
5. İstek hatası sonraki işlemlere eski veri taşımaz.
6. Eşzamanlı bir başka istek yeni doğumu görür; ilk isteğin okuma alanıyla karışmaz.

## Kaynak ve paket

`python3 -m unittest discover -s tests`: **348 test başarılı**, 178,556 saniye. Altı yeni performans/güncellik testi ve önceki 342 regresyon testi dahildir. QR/DataMatrix testi proje gereksinimi olan zxing-cpp 2.3.0 ile çalışmıştır.

Yedi mobil ve iki masaüstü ölçüsündeki **431 tarayıcı kontrolü başarılıdır**; JavaScript hatası görülmedi. Önceki rasyon kilidi, miktar POST kaydı, Geri Al, ekleme penceresi, alt işlem çubuğu, rapor tarihleri ve CSV kontrolü yeniden geçti. Mobil düğme sınırları kesirli tarayıcı koordinatları için 0,01 px toleransla ölçüldü; CSS boyutları 44 px olarak korunur. Mobil JavaScript/service worker sözdizimi ve Python derleme kontrolleri başarılıdır. Mevcut taslak koruma ve sağlık ajandası JavaScript testleri de başarılıdır.

2.0.7 kaynağındaki 274 üst seviye fonksiyon/sınıf tanımı AST olarak aynıdır. Mevcut 219 tanımlık Enterprise çekirdek koruma listesi değiştirilmedi. Yeni `dashboard_performance` modülü Windows PyInstaller hiddenimports listesine ve kaynak derleme kontrolüne eklenmiştir. Mevcut solver ve kayıt işleyicileri değiştirilmedi.

Mobil kaynak ve kurulum adı 2.0.8 olarak güncellenmiştir. Önceki sürümün ayrıntılı doğrulaması `docs/history/DOGRULAMA_APP_EDITION_2_0_7.md` içindedir.

Gerçek Windows EXE kurulumu, iPhone/Safari ve Android cihazları bu ortamda çalıştırılmadı. Paket tam kaynak ve GitHub Windows kurulum akışıdır.
