# v3.9.20 Solver DEV4.17 — Sert Güvenlik ve Net GCAA

- Fazın nişasta sert üst sınırını aşan aday artık kaydedilmiyor.
- Besi yemi seçiliyse aynı besi çözümünde süt yeminin üst sınırı sıfırlanıyor.
- GCAA hedefi aday sıralamasında `%1` iki yönlü toleransla değerlendiriliyor;
  `%3` eksik büyüme kapasitesi artık başarılı çözüm sayılmıyor.
- Gönderilen `270 kg / 1,40 kg / 13 ay` senaryosu için nişasta, ticari yem
  profili ve GCAA regresyon kapıları eklendi.
- 40 otomatik test başarıyla tamamlandı.

# v3.9.20 Solver DEV4.16 — Net Rasyon Seçim Öncelikleri

- Nişasta ideal bandı ve buğday/tahıl KM oranı genel kalite ve maliyet
  sıralamasının önüne alındı.
- Buğday için `%30` hedef, `%30–40` dikkat bandı ve `%40` sert güvenlik sınırı
  birlikte uygulanıyor.
- Besi profilinde süt yemi, süt profilinde besi yemi ancak uygun profilli
  yemlerle ana hedef kapanmıyorsa kullanılabiliyor.
- Solver motor etiketi ve regresyon testleri DEV4.16 olarak güncellendi.

# v3.9.20 Solver DEV4.15 — Sunar Ticari Yem Profilleri

- Kullanıcının 08.04.2025 tarihli Çukoyem Geliştirme Besi Yemi etiketi kataloğa
  15 HP, 2650 ME, %3 ham yağ, %8,86 ham selüloz, %7,60 ham kül, %0,31 sodyum
  ve 10 kg/baş/gün etiket üst dozu kaynağıyla işlendi.
- Çuval/üretici değerleri için ayrı “ürün bazında etiket” alanları eklendi. Solverın
  kullandığı HP, yağ, kül, sodyum ve enerji değerleri referans KM'ye dönüştürülerek
  saklanır; böylece ürün etiketi ile KM hesabı birbirine karıştırılmaz.
- Eski `SIĞIR SÜT YEMİ` kaydı, Sunar'ın resmi ürün adıyla
  `SUNAR KARDELEN SÜT YEMİ,19,2700` olarak geçirildi. 19 HP ve 2700 kcal/kg
  ürün bilgisi doğrulandı; KM bazlı ME/NEm/NEg değerleri açıkça türetildi.
- Eski `BUZAĞI BÜYÜTME YEMİ` kaydı
  `SUNAR BUZAĞI BÜYÜTME ÖZEL DÖNEM YEMİ` olarak geçirildi. Sunar'ın 60-120 gün
  ve serbest tüketim programı eklendi.
- Sunar'ın yayımlamadığı NDF, nişasta ve mineral değerleri üretici analizi gibi
  gösterilmedi; mevcut tam profil açıkça “ÇiftlikPro/Besi_V5.02 referans tahmini”
  olarak işaretlendi ve etiket/laboratuvar doğrulama notu korundu.
- Mevcut veritabanlarında standart eski kayıtların kimliği ve rasyon geçmişi
  korunarak ad/veri geçişi yapılır; kullanıcı/laboratuvar kaynaklı satırlar ezilmez.
- 36 otomatik test başarıyla tamamlandı.

# v3.9.20 Solver DEV4.13 — Bilimsel Hedef Kartları

- **Hotfix 1:** GCAA arzı asgari hedefin %0,5'ten fazla altındaysa kart artık yanlış yeşil görünmez; gerçek açık yüzdesiyle uyarı verir.
- **Hotfix 1:** eNDF yeterliyken yalnız kaba yem KM payı düşükse öneri, “etkili lif düşük” demek yerine kaba/kesif faz dağılımını açıklar.
- **Hotfix 1:** Nişasta ideal bandının ilk 0,5 puan üzeri ölçüm/yuvarlama tamponu olarak “Sınırda” gösterilir ve tek başına göreli rumen riskini yükseltmez.
- **Hotfix 1:** Etiket üst dozu girilmemiş ticari yem için “güvenli üst sınıra ulaştı” varsayımı kaldırıldı.
- **Hotfix 1:** Uzun rasyon çözüm mesajı mobilde kısa özet + açılır “Ayrıntılar” biçiminde gösterilir.
- Önceki sürümde kaydedilen `animal_type` alanının hedef hesabında kullanılmaması düzeltildi.
- “Besi Erkek” artık kastre edilmemiş tosun/boğa (NASEM Chapter 20 Table 20-2), düve ve kastre erkek ise Table 20-1 profiliyle hesaplanır.
- Kart, solver, fizibilite ve akıllı öneriler tek dinamik KM hedefini kullanır.
- HP, Ca ve P değerleri minimum gereksinim olarak gösterilir; makul üst arz hedef sapması sayılmaz.
- Toplam ME yerine NEm/NEg arzından GCAA kapasitesi ana enerji göstergesi yapıldı.
- Dört sütunlu bilimsel özet; 1366 ve 1920 masaüstünde eşit kolon, mobilde yatay kaydırmalı kart düzeni kullanır.
- Eski kesin “tahmini rumen pH” kaldırılmıştır; yalnız veri kapsamı belirtilen göreli asidoz riski gösterilir.
- 500 kg / 1,30 kg-gün tosun/boğa kontrol noktası ve kart anlam testleri eklendi.

# v3.9.20 Solver DEV4.12 — Bilimsel Veri ve Fizibilite Kapısı

- DEV4.11’deki evrensel olmayan sert toplam tahıl, ticari yem ve buğday-pay kısıtları kaldırıldı.
- Yem bazında etiket/uzman alt ve üst doz alanları eklendi; tanımlı üst doz kesin solver sınırıdır.
- Nişasta rumen yıkılabilirliği, NDF sindirilebilirliği, RDP/RUP ve INRA UFV/PDI/PDIA/RPB/doluluk alanları veritabanı ile Yem Kataloğu düzenleme ekranına eklendi.
- Açıkça eşleşen arpa, buğday ve mısır kayıtlarına INRA 2018 referans alanları kullanıcı verisini ezmeden eklendi.
- eNDF’den tek sayı “rumen pH” türetimi kaldırıldı; toplam nişasta + bilinen yıkılabilir nişasta + eNDF veri kapsamlı göreli asidoz riskine dönüştürüldü.
- NASEM NEm/NEg arzından karşılanabilir GCAA hesaplandı ve temel fizibilite kriteri yapıldı.
- Ciddi KM/HP/ME/GCAA sapması, birden çok temel engel veya birleşik rumen güvenlik riski varsa reçete artık kaydedilmez; sınırlayan kısıt ve düzeltme önerisi gösterilir.
- Ticari yem etiketi veya nişasta yıkılabilirliği verisi eksikse kullanıcıya veri-kapsam uyarısı verilir.
- Birim testleri yeni bilimsel sınır ve fizibilite davranışına göre genişletildi.

# v3.9.20 Solver DEV4.11 — KM Bazlı Tahıl / Fabrika Yemi Dengesi

> Tarihsel not: Bu bölümdeki evrensel grup yüzdeleri DEV4.12’de kaldırılmıştır.

- `SIĞIR SÜT YEMİ` besi solverında ticari karma yem olarak tanındı; eski yanlış kategori ve %79,92 nişasta kaydı güvenli katalog değerine geçirildi.
- Ana sıralama ciddi güvenlik → KM/HP/ME/kaba fizibilitesi → diğer rumen rayları → kalite/maliyet olarak düzeltildi.
- Arpa, buğday ve diğer tahıllar yaş kg ile değil rasyon KM payıyla sınırlandırılır.
- Toplam tahıl KM üst sınırı başlangıç/geliştirme/bitirmede sırasıyla %24/%30/%34'tür.
- Tüm seçili fabrika yemleri ortak bir KM bütçesini paylaşır; grup üst sınırı sırasıyla %30/%35/%40'tır.
- Buğday, tahıl karışımı KM'sinin en çok %40'ıdır; yalnız arpa+buğday kullanılıyorsa arpa payı en az %60 kalır.
- HP ve ME eksikleri sıkı korunurken %10'a kadar makul fazlalık yanlış “hedef kaçtı” uyarısı üretmez.
- 11 otomatik test başarıyla tamamlandı.

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

- Besi rasyonlarına dönem bazlı nişasta hedefleri eklendi: başlangıç %20–24, geliştirme %23–27, bitirme %25–29 KM; üst güvenlik sınırları sırasıyla %28, %30 ve %31.
- Solver, ideal nişasta bandını yumuşak hedef; üst sınırı güçlendirilmiş güvenlik cezası olarak değerlendirir.
- Rasyon hedef ekranında “Nişasta + Rumen” kartı, kg/baş/gün hesabı ve uyarı durumu gösterilir.
- Rasyon Hazırlama / Toplam Yem çıktısına KM, nişasta yüzdesi, nişasta miktarı ve hedef/üst sınır eklendi.
- Kullanıcı tarafından eklenen özel yemlerde nişasta değeri veritabanına kaydedilir.

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
# DEV4.14 — Rasyon satırı, tahıl güvenliği ve ticari yem profilleri

- Masaüstünde son yem satırını örten sabit kayıt çubuğu normal akışa alındı.
- Buğday için toplam rasyon KM'sinin %30'u sert üst sınır; tahıl KM'sinde %50 üzeri
  buğday dominansı ise solver kalite sıralamasında yumuşak ceza oldu.
- Yedi jenerik ticari yem temel KM, lif, protein, enerji, nişasta ve mineral
  profilleriyle normalize edildi; ürün etiketi/laboratuvar isteyen ileri alanlar
  bilinmiyor olarak korundu.
- HP'nin hedefin %20 üstü ve enerjiye göre GCAA kapasitesinin hedefin %5 üstü,
  fizibiliteyi bozmayacak biçimde maliyetten önce yumuşakça cezalandırıldı.
- Kart adı “Enerjiye göre GCAA kapasitesi” oldu; gerçekleşen büyüme tahmini olmadığı
  ve yüksek protein/enerji kapasitesi durumları açıkça gösterildi.
- 31 otomatik test başarıyla tamamlandı.
