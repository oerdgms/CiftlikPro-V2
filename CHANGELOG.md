# v3.9.20 DEV4.8 — Mobile Stable / Logo Final

- Mobilde işlevsiz hedef göster/gizle düğmesi kaldırıldı.
- Masaüstü sidebar ÇiftlikPro logosu Dashboard satırının hemen üstünde görünür hale getirildi.
- GitHub Windows installer workflow korundu.
- Solver mantığına dokunulmadı.

## v3.9.20 Solver DEV4.1
- Sidebar `🐄 ÇiftlikPro` marka alanı yatay+dikey merkezlendi.
- Otomatik canlı ağırlık → besi dönemi seçimine manuel override eklendi.
- Faz kaba/kesif koridorları manuel seçimde de solver sınırlarına uygulanıyor.
- Ca/P aşım cezası güçlendirildi.
- GitHub/Windows installer dosyaları korundu.

# ÇiftlikPro Sürüm Notları

## v3.9.20 — 6.17 kaynak tabanı

- `Besi_V5.02.xlsm` formül/kısıt yapısı incelenerek besi solverı kısıt-öncelikli hale getirildi.
- Seçilen yemlerin miktarları aynı anda optimize edilir; kullanıcı manuel +/− ile rasyon kurmak zorunda değildir.
- Kuru Madde, Ham Protein, Metabolik Enerji ve Kaba/Kesif oranı yaklaşık ±%3,5 saha toleransında birlikte değerlendirilir.
- Solver sıralaması güvenlik → dört saha kartı → pratik miktarlar → maliyet şeklindedir.
- Seçilen normal yemler sonuçtan sessizce çıkarılmaz; katkı/mineral kalemleri kendi doz kurallarına göre sıfıra inebilir.
- NDF/eNDF, nişasta, tahmini rumen pH ve mineral sınırları ayrı güvenlik raylarıdır.
- Akıllı Süt Rasyonu ve 6.16 UX düzeltmeleri korunur.
- Arayüzde HOTFIX / DEV / PORT gibi geliştirme etiketleri kaldırıldı; sade `v3.9.20` görünümü kullanılır.

## 6.17 Desktop ERP Final — 2026-08-25
- DEV3 referans rasyon yerleşimi korundu.
- Desktop ERP görsel standardı tüm ana modüllere yayıldı.
- Tablo, form, filtre, kart ve araç çubuğu yoğunluğu ERP kullanımına göre standardize edildi.
- Solver, DB, login, LAN/Tailscale ve sunucu başlatma davranışına dokunulmadı.

## Desktop ERP DEV6 · 2026-08-26
- Mobilde alt sayfalardan Dashboard'a dönüş için üst ÇiftlikPro ana sayfa bağlantısı görünür hale getirildi ve hamburger menü korundu.
- Mobil hızlı işlem şeridi yatay kullanılabilir tutuldu; finans filtre/arama/Temizle taşmaları responsive düzeltildi.
- Hayvan satış/kesim çoklu seçim özetinde "Hayvan Başı Gelir" ifadesi netleştirildi; küpe butonları standart ERP stilinde korunuyor.
- Dashboard'daki tekrar eden küçük ÇiftlikPro metni kaldırıldı; çiftlik logosu/başlığı ana sayfa bağlantısı oldu.
- Ayarlar, yalnız Çiftlik Profili yerine program genelindeki ayarlara giriş sağlayan Ayarlar Merkezi olarak düzenlendi.
- Dashboard'un 8 özet kartı korundu; alt alan kompakt "Bugünün İşleri" (kızgınlık, gebelik/aşı, finans) panellerine dönüştürüldü.
- Solver, veritabanı, LAN/Tailscale ve 8953 ağ başlatma davranışı değiştirilmedi.


## Solver DEV4
- Canlı ağırlığa göre otomatik besi dönemi seçimi korunup faz oranları saha standardına göre revize edildi.
- Başlangıç: %50/%50; Geliştirme: %40/%60; Bitirme: %30–40/%60–70 (KM bazında).
- Faz kaba/kesif koridoru eNDF/pH güvenlik raylarından önce uygulanıyor.
- Kaba/kesif kartında sınırdaki yuvarlama kaynaklı yanlış “yüksek/düşük” uyarısı için tolerans eklendi.
- Hedef bağlamında besi dönemi ve faz kaba/kesif koridoru gösteriliyor.

## v3.9.20 Solver DEV4.3 — Desktop Rasyon UI
- Solver matematiğine ve dönem kurallarına dokunulmadı.
- Masaüstünde Yem Havuzu daraltıldı; ana çalışma alanına daha fazla yatay alan ayrıldı.
- KM / ME / HP / Kaba-Kesif / Günlük Maliyet / Rumen özeti tablonun hemen üstüne taşındı.
- Rasyon tablosu daha sıkı ERP satır yapısı, sabit başlık ve sabit yem adı sütunu ile yenilendi.
- Kaydet çubuğu masaüstünde görünür/sticky hale getirildi.
- Akıllı Dengeleme masaüstünde 3 kolon karar kartı olarak sıkılaştırıldı.
- Mobil rasyon görünümüne dokunulmadı.
- Kilitli ÇiftlikPro logo konumu korundu.

## Solver DEV4.5 — Mobile Restore / Logo Lock
- Solver mantığına dokunulmadı.
- Mobil rasyon görünümü masaüstü ERP dönüşümünden ayrıldı ve eski tek-kolon mobil akış korundu.
- Masaüstündeki tekrarlı rasyon özet şeridi kaldırıldı; Hedef ↔ Mevcut kartları korundu.
- Sidebar logo konumu Dashboard üstünde dikey ortalı ve sola yakın olarak kilitlendi.

## Solver DEV4.6 — Mobile DEV1 UI Restore
- Güncel DEV4.x solver korunarak DEV1 mobil rasyon çalışma masası responsive davranışı geri getirildi.
- Mobilde DEV4.5'teki native iki-kolon taşması kaldırıldı.
- Solver hesapları ve besi fazı kuralları değiştirilmedi.

## Solver DEV4.7 — Mobile Authoritative Restore
- Güncel DEV4.x solver ve besi fazı motoru aynen korundu.
- Masaüstü ERP DOM dönüşümü mobilde kapatıldı.
- Rasyon hedef ayarları mobilde aç/kapa paneline alındı.
- Hedef↔Mevcut kartları yatay mobil şerit haline getirildi.
- Rasyon çalışma tablosu tekrar büyük mobil yem kartlarına dönüştürüldü.
- Masaüstü ÇiftlikPro sidebar logosu Dashboard üstünde sticky/sabit konuma alındı.

## DEV4.7 GitHub Workflow Restore
- DEV4.7 current solver/mobile UI/logo fix preserved.
- `.github/workflows/windows-installer.yml` restored from the previously working GitHub workflow package.
- No solver calculation logic changed in this merge.

## DEV4.9 UI düzeltmesi
- Solver/optimizasyon mantığı değiştirilmedi.
- Masaüstü ÇiftlikPro markası Dashboard satırının hemen üstüne aşağı alındı ve kırpılma önlendi.
- Mobilde işlevsiz Hedef Bilgilerini Göster/Gizle düğmesi hem CSS hem DOM seviyesinde kaldırıldı.

## DEV4.10 — Desktop Sidebar Brand Final
- Masaüstü sol menü üst beyaz çubuğun altına alındı; ÇiftlikPro logosunun kırpılması giderildi.
- Logo Dashboard satırının hemen üstündeki ayrılmış alana sabitlendi.
- Solver ve mobil rasyon akışı değiştirilmedi.
# DEV4.10 Rapor ve Hayvan Aktarımı Güncellemesi

- Raporlar sayfasına aktif/tüm, grup, padok ve arama filtreli Tüm Hayvanlar Raporu eklendi.
- Ekrandaki hayvan listesi için temiz A4 yatay Yazdır/PDF görünümü ve gerçek XLSX dışa aktarımı eklendi.
- XLSX, CSV ve Tarım ve Orman Bakanlığı işletme hayvan raporu biçimindeki dijital PDF dosyalarından önizlemeli hayvan içe aktarma eklendi.
- İçe aktarmada mükerrer küpe engeli, tarih/cinsiyet doğrulaması, 10 aylık buzağı kuralı ve işlem öncesi otomatik güvenlik yedeği eklendi.
- Rasyon hazırlama çıktısında uygulama menüsü, sekme ve durum çubuğunun kâğıda taşınması engellendi; işletme başlığı ve sayfa kırılma kuralları düzeltildi.
- iPhone/Safari baskısında oluşan URL altbilgisi ve ikinci sayfada kaybolan tablo başlığı için doğrudan PDF üretimi eklendi; PDF artık yatay A4, tekrarlanan sütun başlıkları ve kontrollü sayfa numarası kullanır.
- Mobil Tüm Hayvanlar ekranı, geniş tablonun telefona sıkıştırılması yerine kart tabanlı iki kolonlu bilgi düzenine geçirildi.
- Mobil web önizlemeye temiz PDF'yi doğrudan açma düğmesi ve kart görünümü eklendi; yazdırmada masaüstü tablo düzeni korunur.
- Excel/PDF hayvan içe aktarma alanı uzun listenin altından Raporlar sayfasının üstüne taşındı; Veri Aktarımı ekranına da kısayol eklendi.
- Kullanıcının tiklerle belirlediği rapor sütunları ekran, mobil kart, web önizleme, PDF ve XLSX çıktılarında ortak kullanılmaya başlandı.
