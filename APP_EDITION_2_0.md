# App Edition 2.0.8 — Ortak Enterprise mobil arayüzü

## Temel

AppEdition 2.0.7 paketi üzerine Dashboard performans düzeltmesi uygulanmıştır. Çekirdek sürüm 3.9.23 DEV4 Hotfix1.22cr olarak korunur. Güncel katmanın kimliği AppEdition2.0.8-DashboardPerformance’tur.

Normal giriş adresi aynı kalır: port 8953, kök adres /. Eski /mobile bağlantısı ortak uygulamaya yönlendirilir.

## Görünüm

- Yeşil başlık, beşli alt menü, sayfaya uygun + işlemi.
- Fotoğraflı giriş, mevcut oturum ve şifre kurtarma formu.
- Ortak Dashboard hesaplamalarından sayılar ve sağlık/vade satırları.
- Kompakt, mevcut işlem formlarını koruyan hayvan ve finans satırları.
- Padok kapasitesi, hayvan sayısı ve rasyon özeti.
- Sağlık merkezinin mevcut filtreleri, doz planlama ve geçmiş kayıtları.
- Rasyon araması, tür filtresi ve padok ataması özeti.
- Mevcut Enterprise rasyon çalışma masası ve solver.
- Rapor, modül ve sistem araçları için kolay ulaşılabilir bağlantılar.
- iOS güvenli alanları, dinamik ekran yüksekliği, 16 px form alanları.

Eski mobil CSS katmanlarıyla çakışma, yalnız mobilde etkin olan bağımsız CSS katmanıyla giderilir. Masaüstünde yeni gezinme ve mobil kart dönüştürme çalışmaz.

## 2.0.8 Dashboard performansı

- `dashboard_performance.py` başlangıçta mevcut şema hazırlandıktan sonra 12 non-unique SQLite indeksi oluşturur. Tartım, gebelik, doğum, kayıp kontrolü, stok, fiyat ve padok sorguları yararlanır. Mevcut kayıtlar değiştirilmez.
- Aynı ana sayfa isteği içinde ortak sürü, gebelik ve sağlık hesapları bir kez yapılır. Paylaşım doğum uzlaştırması ve bakım işlemlerinden sonra başlar. İstek tamamlandığında veya hata verdiğinde alan temizlenir; başka kullanıcıya, isteğe veya POST işlemine taşınmaz. Sonraki açılış yeni veriyi okur.
- Mevcut kısa `[PERF] Dashboard hazır` ölçümü korunur. Bir saniyeyi aşan Dashboard yanıtlarında ayrıca bakım, görünüm ve sıkıştırmayı da kapsayan `[PERF] Dashboard sunucu yanıtı` süresi yazılır. Tarayıcının ekranı çizme süresi bu ölçüme dahil değildir.
- Performans modülü Windows EXE tanımına ve derleme kontrollerine eklenmiştir. Kurulum adı ve mobil kaynak kimliği 2.0.8’dir.
- Yerel, yapay büyük veri karşılaştırması ve sınırlar güncel doğrulama raporundadır. Kullanıcının bilgisayarındaki süre bu ölçümden garanti edilemez.

## 2.0.7 mobil rasyon ve rapor yerleşimi

- Yem adı, KM bilgileri ve kilit düğmesi üst satırda; eksi, geniş miktar alanı, artı ve silme düğmesi alt satırdadır. 44 px işlem düğmeleri kullanılır. Eski görsel katmanın kısa gecikmeli yerleşimi tamamlandıktan sonra aynı kilit düğmesi yeniden konumlanır; mevcut dinleyicisi ve kayıt alanları korunur.
- Genel form boşlukları miktar alanına uygulanmaz. Yerel sayı artırma okları gizlenir; mevcut eksi/artı düğmeleri çalışır. Silme düğmesinin metin ve CSS simgesi üst üste basılmaz; tek SVG simgesi gösterilir.
- Satırın dışında bulunan gizli kilit kayıt alanı mobil düğmeyle eşitlenir. Böylece kilidi açıp miktarı değiştirdikten sonra Kaydet gerçek yeni miktarı gönderir. Yeniden kilitleme ve Geri Al sonrasında da gizli alan mevcut satır durumunu izler; sunucunun kilit kuralları aynıdır.
- Gerçekte kullanılan `wb2-mobile-dock`, alt menü ve iOS güvenli alan yüksekliğine göre konumlanır. Listenin sonunda işlem çubuğu için boşluk vardır.
- Raporların sekmeleri, tarih aralığı, düğmeleri ve finans özeti esnek sütunlara alınır. Tarih alanlarının iç genişliği sınırlanır; rapor taşıyıcılarında odak sırasında yana kayabilecek ek kırpma alanları kaldırılır. Geniş finans tablosu ve grafik kendi kutusunda yatay kaydırılabilir.
- Mobilde uygulanan tarih ve hayvan filtreleri, ilk açılışta ve rapor sekmeleri arasında geçerken adres satırında korunur; yenileme aynı raporu açar.
- Mobil kaynaklar ve Windows kurulum dosyası 2.0.7 kimliğiyle sunulur. `server.py` içinde yalnız AppEdition build etiketi güncellenmiştir; solver, kayıt işleyicileri ve veritabanı şeması 2.0.6 paketiyle birebir aynıdır.

## 2.0.6 toplu kullanılabilirlik ve iletim düzeltmeleri

- Bildirimler ayrı `/notifications` sayfasına gider; ortak sağlık/ödeme görevleri, yaklaşan kızgınlık ve doğum kayıtları mevcut Enterprise yardımcılarıyla hesaplanır.
- Hayvan kartında Geçmiş, işletmeye giriş, sağlık, tartım, tohumlama, padok ve bağlı finans kayıtlarını tarih sırasıyla gösterir. Satış ve zayiat formları ayrı sekmede korunur; eski `#animalSale` ve `#animalLoss` bağlantıları bu sekmeyi açar.
- Buzağı sağlık, tartım ve iç üretim tabloları mobilde açılır kayıt kartlarıdır. İç üretim tarih ve tür alanları mobilde tek sütunla ayrılır; mevcut form alanları ve silme işlemi korunur.
- Fotoğraf yükleme formu masaüstünde etiketli ve aralıklı üç sütun, mobilde tek sütundur. Galerideki boş durum satırı tam genişlik kullanır.
- Mobilde İşletme Bilgileri ve Ayarlar bağlantısı doğrudan işletme formuna gider; eski Dashboard'u açan geçici genişletme kodu kaldırılmıştır.
- Dikey hareket sırasında `scrollTo` ile konum düzeltme kaldırılmıştır. `overflow-x:clip`, tek belge kaydırma alanı ve bulanıklık içermeyen sabit alt menü kullanılır. Doğal momentum korunur.
- Çift dokunma ve pinch için CSS ile dokunma/hareket korumaları birlikte kullanılır. Sürükleme ile gerçek kısa dokunmalar ayırt edilir; form ve düğmelere hızlı dokunmalar engellenmez. Fotoğrafın kendi büyütme penceresi korunur.
- HTML/CSS/JS gzip kabul eden istemcilere sıkıştırılmış gönderilir. HTML `no-store`; sürümlü kaynaklar uzun süreli önbellek kullanır. Gzip istemeyen istemciler aynı metni düz alır.
- 42 tarihi mobil belge `docs/history` içine taşınmıştır. Eski API ve kayıt işleyicileri, testler ve kurulum kaynakları korunmuştur; yalnız kullanılmayan mobil genişletme ve mükerrer build ataması temizlenmiştir.

## 2.0.5 giriş ve hayvan işlem düğmeleri

- Göster/Gizle düğmesi şifre alanının içinde dikey ortalanır; şifre metni için sağda ayrı boşluk bırakılır.
- Hayvan listesinde Görüntüle, Düzenle ve Sil işlemleri tam genişlikte tek satırda gösterilir. Ayrıntı, Kart ve Kompakt görünümün eski dar simge ölçüleri mobil katmana taşınmaz.
- Mevcut giriş, bağlantı, silme formu ve onay mekanizması korunmuştur.

## 2.0.4 mobil görüntü alanı kilidi

- Finans raporu dâhil mobil ekranlarda belge genişliği telefon ekranına sabitlenmiştir; sayfanın tamamı sağa-sola sürüklenmez.
- iOS ve Android için viewport üst sınırı 1 olarak belirlenmiş, kullanıcı yakınlaştırması kapatılmıştır. Safari hareket olayları, çoklu dokunma ve çift dokunma yakınlaştırmasına karşı mobil katmanda ek koruma uygulanır.
- Finans raporundaki geniş tablo/grafik, sekmeler ve özellikle yatay kullanılması gereken iç alanlar sayfayı genişletmeden kendi sınırları içinde kaydırılabilir kalır.
- Kilit yalnız 900 px ve altındaki App Edition görünümünde çalışır. Masaüstü genişlikleri, formlar, kayıt yolları ve iş kuralları değiştirilmemiştir.
- Mobil CSS ve JavaScript adresleri 2.0.6 önbellek anahtarıyla sunulur.

## 2.0.3 hayvan kartı düzenlemesi

- Buzağı kimlik alanı fotoğrafın yanında kompakt tutulur; canlı maliyet ve finans özeti fotoğraf sütununa sıkışmak yerine kartın tam genişliğinde sıralanır.
- Para ve gün metrikleri iki sütunlu eşit kutulara yerleşir; tek kalan toplam kutusu tam satırı kullanır. Uzun tutarlar, açıklamalar ve notlar kart sınırları içinde sarılır.
- Fotoğraf yükleme ve Kilo / Gelişim kartları telefonlarda tek sütunda, tabletlerde yeterli alan bulunduğunda iki sütunda çalışır. Dosya seçimi, tarih, kilo, not ve kayıt düğmeleri kendi kartının dışına çıkmaz.
- İç üretim maliyeti formu uygun telefon genişliklerinde iki sütunla sıkılaştırılır; dar ekranlarda güvenli biçimde tek sütuna döner.
- Yetişkin hayvanın kimlik başlığı, hızlı işlem düğmeleri, maliyet göstergeleri ve fotoğraf yükleme alanı aynı kompakt ölçülere getirilmiştir.
- Yalnız mobil sunum katmanı yeniden düzenlenmiştir. Fotoğraf, tartım, iç üretim maliyeti, sağlık ve finansın mevcut form yolları ile masaüstü görünümü değiştirilmemiştir.
- Mobil CSS ve JavaScript adresleri 2.0.3 önbellek anahtarıyla sunulur.

## 2.0.2 finans kartı düzeltmesi

- Finans kaydındaki üç nokta düğmesi ayrı işlem satırından tutar hücresine taşınmıştır. Kapalı kartta eski işlem hücresi tamamen gizlenir; böylece boş beyaz bant oluşmaz.
- Kart açıldığında Düzenle/Sil düğmeleri başlığın hemen altında kompakt bir satırda görünür; Tür, Kategori, Hayvan, Durum, Ödeme ve Vade ayrıntıları aynı kayıt üzerinden açılmaya devam eder.
- Değişiklik yalnız mobil sunum katmanındadır. Finans kaydetme, düzenleme ve silme yolları ile masaüstü finans tablosu değiştirilmemiştir.
- Mobil CSS ve JavaScript adresleri 2.0.2 önbellek anahtarıyla sunulur.

## 2.0.1 kullanılabilirlik düzeltmeleri

- Tüm mobil sayfalarda içerik sonuna alt menü ve güvenli alan yüksekliğini hesaba katan boşluk eklenir. Akıllı hayvan formunun kaydetme şeridi alt menünün üstünde sabitlenir.
- Hayvan Ekle ekranında Yetişkin ve Buzağı seçimi açıkça gösterilir. Buzağı seçeneği mevcut akıllı formu açar, doğum tarihini zorunlu tutar ve mevcut 10 aydan küçük olma kuralıyla aynı `/animal-add` kayıt işlemini kullanır.
- Hayvan listesindeki yeşil `+` düğmesi Hayvan Ekle ve Buzağı Ekle seçeneklerini ayrı gösterir.
- Hayvan kartındaki para değerleri iki sütunlu mobil kart sınırlarında kalır. Hızlı işlemlerde Fotoğraf Ekle tam satıra yerleşir; fotoğraf seçme, açıklama ve yükleme alanları ekran genişliğini aşmaz.
- Mobil CSS ve JavaScript adresleri 2.0.1 önbellek anahtarıyla sunulmuştu; 2.0.2 yeni anahtarla telefonun eski görünümü kullanmasını önler.

## Ortak kaynaklar

| Alan | Kullanılan kaynak |
|---|---|
| Hayvan sayıları | dashboard_herd_counts |
| Gebelik sayısı | active_pregnancy_records |
| İşler ve ödemeler | dashboard_export_tasks |
| Padok hayvanları | Mevcut render_paddock_management |
| Padok sayısı | Mevcut aktif paddocks kayıtları |
| Hayvan/finans/sağlık kayıtları | Aynı Enterprise formları ve POST yolları |
| Solver ve rasyon | Mevcut ration-workbench ve işlem yolları |
| Yem / stok | Mevcut feeds ekranı ve stok işlemleri |
| Süt / tarım / rapor / ayarlar | Mevcut Enterprise ekranları |

İkinci bir mobil veritabanı, farklı finans hesabı veya farklı solver oluşturulmamıştır. Eski MobileFull API kodu kaynakta geriye dönük olarak durur; yeni arayüz Bearer token veya ikinci mobil giriş kullanmaz.

## Toplu taşıma

Yeni /paddock/assign-many yolu mevcut oturum ve lisans kontrolleriyle çalışır. Yetişkin ve aktarılmamış aktif buzağı seçimi tek veritabanı işlemi içinde doğrulanır. Kapasite hesabında mevcut paddock_population, güncellemede mevcut sync_paddock_text kullanılır. İsim alanları, geçmiş ve padok güncelleme tarihleri birlikte yazılır.

Geçersiz seçim veya yetersiz kapasitede işlem bütünüyle geri alınır. Aynı gönderim tekrarlanırsa zaten hedef padoktaki hayvan için ikinci hareket kaydı oluşturulmaz.

## Paketleme

mobile_ui ve dashboard_performance Python modülleri ile mobile_assets klasörü PyInstaller paketine eklenmiştir. Windows Actions ve Inno Setup AppEdition 2.0.8 kurulum dosyasını hedefler. Çalışma zamanı veri klasörü ve mevcut lisans düzeni korunur.

Giriş arka planı bu uygulama için üretilen bir görseldir. Bitmap üretim promptu: gerçekçi Simental sığır, Türkiye kırsalında gün batımı, dikey fotoğraf, metin ve arayüz olmadan; üstte gökyüzü, altta form için koyu çimen. Üretim yerleşik görsel üretme aracıyla yapılmış ve JPEG olarak pakete alınmıştır.

## Sınırlar

Web uygulaması iOS/Android tarayıcılarına göre hazırlanmıştır. APK/IPA veya App Store/Google Play dağıtımı bu kaynak paketinde yoktur. İnternetsiz yazma kuyruğu yoktur; tüm iş kayıtları erişilebilir Enterprise sunucusunda yapılır. Gerçek iPhone/Android cihazı ve Windows kurulum EXE’si bu çalışma ortamında çalıştırılmamıştır.
