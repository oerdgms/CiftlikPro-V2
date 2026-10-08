Hotfix1.22bp: Akıllı Üreme Yaşam Döngüsü eklendi. Taze, Üreme Kontrolü, Tohumlamaya Hazır, Kuruya Çıkarılacak, Kuru ve Yakın Doğum durumları dinamik hesaplanır; bireysel kızgınlık geçmişinden tahmin, kuruya çıkarma işlemi ve işletmeye özel üreme eşikleri desteklenir.
Hotfix1.22bn: Ayrı “İşlem Yapılmamış” kartı ve filtresi kaldırıldı. Boş / İşlem Bekleyen tek grup olarak gösterilir; özet satırı işlem yapılmamış ve yeniden işlem bekleyen sayılarını ayrı verir, kart rozetleri ayrımı korur.
Hotfix1.22bn: Üreme Merkezi tüm aktif dişileri kapsar. Ayrı İşlem Yapılmamış filtresi kaldırıldı; tüm boş/işlem bekleyen dişiler tek Boş / İşlem Bekleyen grubunda gösterilir. Özet satırı işlem yapılmamış ve yeniden işlem bekleyen sayılarını ayrı verir; kart rozetleri ayrımı korur.

# ÇiftlikPro Enterprise V3.9.23 DEV4 Hotfix1.22bj

## Hotfix1.22bj – Dashboard Hızlı Ödeme

- Dashboard `Bugünün İşleri` içindeki vadeli ödeme satırlarında durum rozetinin yanında onaylı `Öde` düğmesi bulunur; ödeme bugünün tarihiyle kapatılır ve kullanıcı Dashboard'da kalır.
- Ödeme başlığına tıklanınca genel finans formunun başındaki `Ödeme Durumu` kartı açılır; ödeme tarihi seçilerek `Ödendi Olarak İşaretle` işlemi yapılabilir.
- Ödenmiş kayıt aynı karttan yeniden `Ödenmedi` durumuna alınabilir; hızlı işlem yalnız ödeme durumunu değiştirir, gider tutarını veya bağlı hayvan kaydını yeniden oluşturmaz.
- İşlem kaydı denetim günlüğüne eklenir; yinelenen gönderimler ikinci kez ödeme oluşturmaz.
- Windows kurulum sürümü, çıktı dosyası ve GitHub Actions artifact yolu `1.22bj` adıyla eşitlendi.

## Hotfix1.22bi – Üreme Filtresi ve Hızlı Gebelik Sonucu

- Üreme Merkezi üst aşama filtrelerinin CSS nedeniyle yeniden açılması giderildi; filtreler masaüstü ve mobilde gerçekten yalnız seçilen grubu gösterir.
- `Gebelik Kontrolü`, `Gebe`, `Gebe Değil` ve `Doğuma Yaklaşan` ayrı filtreler olarak çalışır; `Tümü` sayısı benzersiz hayvanlar üzerinden hesaplanır.
- Kontrol bekleyen, gebe ve gebe olmayan hayvan kartlarından `Kontrol Bekliyor / Gebe / Gebe Değil` sonucu tek pencerede değiştirilebilir.
- Hızlı işlem yalnız hayvanın en güncel tohumlama kaydını günceller; pozitif sonuçta tahmini doğum tarihi yeniden hesaplanır, negatif/bekleyen sonuçta temizlenir.
- Windows kurulum sürümü, çıktı dosyası ve GitHub Actions artifact yolu `1.22bi` adıyla eşitlendi.

## Hotfix1.22bh – Gebelik Sayacı Senkronizasyonu

- Dashboard, Üreme Merkezi, Tohumlama listesi ve gebelik aşıları tek aktif gebelik kaynağına bağlandı.
- Doğumla kapanan gebelik, Dashboard açıldığında yeniden uzlaştırılır ve gebe sayısından düşer.
- Eski `Pozitif` kayıtların kızgınlık ve aşı listelerini yanlışlıkla engellemesi önlendi.
- 1.22bg hayvan kartı ve geçmiş veri uzlaştırma düzeltmeleri korunur.
- Windows kurulum sürümü, çıktı dosyası ve GitHub Actions artifact yolu `1.22bh` adıyla eşitlendi.

## Hotfix1.22bg – Gebelik/Doğum Uzlaştırma

- Daha önce doğumu kaydedilmiş fakat tohumlama sonucu `Pozitif` kalmış eski kayıtlar başlangıçta otomatik `Doğum` durumuna alınır.
- Hayvan kartının üst Gebelik özeti, aktif gebelik yokken eski `Pozitif` sonucuna geri dönmez.
- Üreme Durumu paneli, Dashboard gebelik sayısı ve hayvan kartı aynı aktif gebelik kuralını kullanır.
- İşlem idempotenttir; kapatılmış doğum kayıtları sonraki açılışlarda yeniden değiştirilmez.
- 1.22bf Dashboard yerleşimi ile 1.22be doğum/padok/sayaç düzeltmeleri korunur.
- Windows kurulum sürümü, çıktı dosyası ve GitHub Actions artifact yolu `1.22bg` adıyla eşitlendi.

## Hotfix1.22bf – Modern Dashboard Masaüstü Yerleşim Düzeltmesi

- Masaüstünde `Bugünün İşleri`, `Sürü Dağılımı`, `Yaklaşan Doğumlar`, `Kritik Stoklar` ve `Son Hareketler` yeniden dengeli üç sütun akışına alındı.
- `Bugünün İşleri` ilk sütunda iki satırı kaplar; kısa sağ panellerin altında oluşan büyük boşluklar kaldırıldı.
- Mobil Dashboard kuralları ile 1.22be doğum, gebelik, padok devri ve sürü sayacı düzeltmeleri aynen korundu.
- Windows kurulum sürümü, çıktı dosyası ve GitHub Actions artifact yolu `1.22bf` adıyla eşitlendi.

## Hotfix1.22be – Doğum ve Görünüm Tamamlama

- Dashboard toplamları artık yalnız aktif, zayiatta olmayan ve yetişkine aktarılmamış kayıtları sayar.
- Çiftlikte doğan yavru için padok seçilmezse annenin aktif padoku otomatik devralınır; giriş tarihi doğum tarihi olur.
- İşletmede doğan buzağının kartında yanıltıcı `Alış` satırı yerine `İşletmede doğdu`, maliyet kutusunda `Başlangıç Maliyeti` gösterilir.
- Mobil Üreme Merkezi akordeon başlıklarında sabit üst menü için güvenli kaydırma payı eklendi.

## Hotfix1.22bd – Sunar 21.28 Süt Yemi

- `SUNAR 21.28 TAMAMLAYICI SÜT YEMİ` katalog ve mevcut DB migrasyonuna eklendi.
- Etiket değerleri: HP %21, ME 2800 kcal/kg, ham yağ %3,10, ham selüloz %8,64, ham kül %6,60, sodyum %0,32.
- Etikette yer almayan NDF, nişasta, Ca/P ve ileri solver alanları aynı sınıftaki Sunar süt yemi referans profili olarak işaretlenmiştir; laboratuvar analiziyle doğrulanmalıdır.


## Hotfix1.22ba – 0 Stok + Doğumda Gebelik Kapatma

Dashboard 0 kg yemleri Kritik Stoklar listesinde göstermez. Çiftlikte doğan buzağı kaydedildiğinde annenin ilgili aktif gebeliği otomatik kapanır.


## Hotfix1.22ba – Sağlık Ajandası İşlem Menüsü

- Ajanda kartlarındaki üç nokta düğmesi iPhone/Safari ve diğer dokunmatik ekranlarda güvenilir biçimde açılıp kapanır.
- Menü artık tarayıcının değişken `details` davranışına bağlı değildir; gerçek bir düğme, `aria-expanded` durumu ve kontrollü görünürlük kullanır.
- Mobilde menü düğmenin üstüne, masaüstünde altına açılır; kart ve sabit durum çubuğu tarafından kesilmez.
- Dışarı dokunma ve Escape menüyü kapatır; aynı anda yalnız bir kartın işlem menüsü açık kalır.
- Düzenle, Sil, Hayvanı Aç ve 1 Gün Ertele işlemlerinin sunucu akışı değiştirilmemiştir.

## Hotfix1.22ax – Fotoğraf Büyütme Görüntüleyicisi

- Hayvan kartındaki profil ve galeri fotoğrafları dokunarak/tıklayarak büyütülebilir.
- Buzağı kartındaki kayıtlı profil fotoğrafı aynı görüntüleyiciyi kullanır.
- Görüntüleyici arka plana, kapatma düğmesine veya Escape tuşuna basılarak kapanır.
- Mobil güvenli alanlar, klavye erişimi ve sayfa kaydırma kilidi desteklenir; sürü listesindeki küçük görseller değiştirilmez.
- GitHub Actions kurulum kontrolü, SHA-256 üretimi ve artifact yolu Inno Setup'ın `1.22ax` çıktı adıyla eşitlendi.
- Inno Setup 6'nın yeni işlev adı kullanılarak eski `FileCopy` uyarısı kaldırıldı.

## Hotfix1.22aw – Hayvan Fotoğrafı ve Bağlı Küpe Düzeltmesi

- Buzağı kartından yetişkin karta aktarılmış hayvanlar fotoğraf eklenerek yeniden düzenlenebilir.
- Aynı hayvana bağlı geçmiş buzağı satırı artık yanlışlıkla mükerrer küpe sayılmaz.
- Küpe değişirse yetişkin kartı ile bağlı geçmiş kaydın küpesi birlikte güncellenir.
- Gerçek başka bir hayvan veya buzağı aynı küpeyi kullanıyorsa güvenlik kontrolü işlemi engellemeye devam eder.

## Hotfix1.22av – Sürü Merkezi Filtre Hizalaması

- Masaüstü ve orta çözünürlükte Hayvan ara, Padok, Göster, Filtrele ve Temizle kontrolleri aynı taban çizgisine alındı.
- Sol menüden sonra kalan içerik genişliğine uyum sağlaması için sabit alt genişlikler akışkan hale getirildi.
- 1180 px ve altında güvenli iki satır düzenine geçilir; kontrol taşması ve üst üste binme önlenir.
- Mobil açılır filtre, sürü görünüm seçenekleri ve liste kartları değiştirilmedi.

## Hotfix1.22au – Mobil Bugünün İşleri Düzeltmesi

- Dashboard `Bugünün İşleri` listesi yalnız dikey kaydırılır; iOS'ta aşağı-yukarı kaydırırken oluşan sağa-sola hareket kaldırıldı.
- Tarih sütunu 84 px olarak korunurken uzun görev başlıkları ve açıklamalar iki satıra kadar güvenli biçimde sarılır.
- Kalan gün rozeti kart sınırları içinde sabitlenir; görev metninin veya rozetin satır dışına taşması engellenir.
- Tümü, Geciken, Bugün ve Yaklaşan filtreleri mobilde yatay kaydırmasız tek sabit sıraya sığdırıldı.
- Değişiklik yalnız modern Dashboard görev kartına uygulanır; masaüstü ve diğer paneller korunur.

## Hotfix1.22at – Mobil Sürü Görünümü Düzeltmesi

- Ayrıntı görünümündeki masaüstü hücre ölçülerinin mobil karta taşınması engellendi; kimlik başlığı, rozetler ve bilgi alanları ekran genişliğine sığdırıldı.
- Kompakt görünümde Görüntüle, Düzenle ve Sil işlemleri yalnız simgeli, sabit ölçülü tek satırda düzenlendi; üst üste binen yazılar kaldırıldı.
- Sil düğmesindeki çift çöp kutusu simgesine yol açan eski ve yeni CSS üreticisi çakışması giderildi.
- Doğrulanmış Kart görünümü ile masaüstü Ayrıntı/Kart/Kompakt yerleşimleri korunmuştur.

## Hotfix1.22as – Sürü Merkezi Görünüm Sistemi

- Ayrıntı, Kart ve Kompakt görünüm seçenekleri eklendi; değişim sayfa yenilemeden uygulanır.
- Tercih kullanıcı hesabına kaydedilir ve Dişi, Erkek, Buzağı ile sayfalama geçişlerinde korunur.
- Ayrıntı görünümü tüm bilimsel/kimlik alanlarını, Kart görünümü fotoğraflı özeti, Kompakt görünüm daha fazla hayvanı ekranda gösterir.
- Mobilde üç görünüm de ekran genişliğine göre ayrı düzenlenir; görüntüle, düzenle ve sil işlemleri korunur.

## Hotfix1.22ar – Tek Sürü Merkezi Yönlendirmesi

- Sol menüdeki Dişi, Erkek ve Buzağı bağlantıları yeni Sürü Merkezi'nin ilgili filtresini açar.
- Eski `/animals`, `/males` ve `/calves` adresleri güvenli biçimde aynı filtreli Sürü Merkezi'ne yönlendirilir; eski tablo görünümü geri gelmez.
- Buzağı kartındaki listeye dönüş ile hayvan ekleme, düzenleme ve silme sonrası dönüşler doğru kategori filtresini korur.
- Arama ve desteklenen filtre parametreleri eski bağlantılardan yeni görünüme aktarılır.

## Hotfix1.22aq – Kompakt Seçili Hayvan Kartı

- Üreme Merkezi'ndeki seçili hayvan kartı mobilde ekran genişliğine sığan kompakt düzene geçirildi.
- Başlık ve hayvan kartı bağlantısı tek satırda; tekrar eden büyük küpe kutusu mobilde gizlidir.
- Padok ve aşama küçük rozetlerle gösterilir, beş aşamalı süreç çizgisi yatay taşmadan ekrana sığar.
- Bilgilendirme ve tüm kayıtlar işlemi tek kompakt satırda tutulur; masaüstü detay düzeni korunur.

## Hotfix1.22ap – Aşama Filtreli Üreme Merkezi

- Mobilde iPhone adres çubuğu kaynaklı ekran yüksekliği değişimleri artık açık akordeonu kapatmaz.
- `Tohumlandı`, `Sonuç Gir`, `Kontrol Kaydet` ve `Doğum Kaydet` düğmeleri tek satırda, kart sınırları içinde kalır.
- Masaüstünde dar dört sütun yerine aşama düğmeleri ve tek geniş hayvan listesi kullanılır.
- Tümü, Kızgınlık, Tohumlandı, Kontrol, Gebe ve Doğuma Yaklaşan filtreleri arama ve padok filtresiyle birlikte çalışır.

## Hotfix1.22ao – Mobil Üreme Merkezi

- Kızgınlık, Tohumlama, Gebelik Kontrolü ve Doğuma Yaklaşan bölümleri mobilde aynı kompakt akordeon düzenine geçirildi.
- Her açık bölüm ilk üç hayvanı fotoğrafı, kısa özeti, durum rozeti ve ilgili işlemiyle gösterir; kalan kayıtlar `Tümünü Gör` ile açılır.
- Arama ve padok filtresi görünür kayıt sayısını ve `Tümünü Gör` sayacını canlı günceller.
- Masaüstündeki dört sütunlu çalışma düzeni ve mevcut kayıt işlemleri korunmuştur.

## Hotfix1.22an – Fotoğraflı ve Sıralanabilir Sürü Merkezi

- Masaüstünde arama, Padok, Göster ve işlem düğmeleri ilk açılıştan itibaren aynı araç satırında görünür; kapanmış filtre bölümü nedeniyle oluşan boş alan kaldırıldı.
- Hayvan listesine kayıtlı profil fotoğrafı eklendi. Fotoğraf yoksa dişi, erkek ve buzağı için güvenli simge gösterilir.
- Hayvan, Tür, Irk, Padok, Yaş ve Durum başlıkları tıklanarak artan/azalan sıralama yapılabilir; seçim sayfalama ve kategori geçişlerinde korunur.
- Masaüstü liste satırları fotoğraf + kimlik özetiyle yenilendi. Mobilde aynı veri, fotoğrafı ve kısa özeti olan kompakt kartta; işlemler tek sırada gösterilir.
- Solver, rasyon, stok, sağlık ve kayıt silme kuralları değiştirilmedi.

## Hotfix1.22am – Sürü Merkezi Filtre Tasarımı

- Masaüstünde geniş arama, Padok, Göster ve işlem düğmeleri hizalı araç çubuğundadır.
- Mobilde arama hep görünür; Padok/Göster ve düğmeler açılır Filtreler bölümündedir. Seçili padok varsa bölüm açık başlar ve rozet gösterir.
- Tekrarlanan Tür seçimi kaldırıldı; kategori sekmeleri ve gizli kind alanı filtreyi korur.
- Sonuç sayısı ve seçili padok liste üstünde gösterilir; mobil hayvan kartları iki kolonlu kompakt düzendedir.
- Solver, stok ve silme işlemi değişmedi. Görseldeki örnek hayvan fotoğrafları bu pakete eklenmedi.

## Hotfix1.22al – Mobil Hayvan İşlemleri

- Sürü Merkezi mobil kartlarındaki `Görüntüle`, `Düzenle` ve silme işlemi tek satıra alındı.
- Silme işlemi 44 px dokunma alanına sahip kompakt çöp kutusu düğmesi olarak gösterilir; mevcut onay penceresi korunur.
- Değişiklik yalnız mobil hayvan listesini etkiler; masaüstü tablo ve diğer ekranların işlem düğmeleri değişmez.

## Hotfix1.22ak – Dashboard İlk Açılış Görüntüsü

- Modern/Klasik anahtarı ilk çizimden önce biçimlendirilir; mobilde ham mavi butonların kısa süre görünmesi engellenir.
- Alt durum çubuğundaki sürüm etiketi uygulama sürümüyle yeniden eşitlenmiştir.
- Dashboard tercihi, sağlık ajandası, solver ve veritabanı işlemleri değiştirilmemiştir.

## Hotfix1.22af – Mobil Süt Girişi Responsive

Mobil süt girişi kart düzenine geçirildi; masaüstü tablo korunmuştur.

Bu hotfix, Hotfix1.22aa üzerine yapılan bütünlük kontrolünü ve iki doğrulanmış düzeltmeyi içerir. Bilimsel değerler panelinin eski `w/x/z/aa` denetleyicileri son HTML'den temizlenerek tek aç/kapat denetleyicisine indirildi. Aktif ek yem kaydı ileri bir tarihe düzenlendiğinde bugünkü tüketim artık kaybolmaz; mevcut dönem planlanan tarihten bir gün önce kapanır ve yeni dönem ayrıca oluşturulur. Solver DEV4.19.6 korunmuştur.

## Hotfix1.22af – Süt & Laktasyon Yönetimi V1

- Yeni Süt & Laktasyon Merkezi: toplu sabah/akşam süt girişi, DIM, 7/30 günlük ortalama, laktasyon toplamı, 305 gün tahmini ve süt düşüş uyarısı.
- Hayvan kartında süt kalite alanları (yağ, protein, SCC) ve laktasyon KPI kartları.
- Mevcut milk tablosu geriye uyumlu migration ile genişletilir; eski veritabanları korunur.
- Hotfix1.22ab QA paneli ve tarihli ek yem geliştirmeleri aynen korunur.

## Hotfix1.22ab

- Düşük çözünürlük bilimsel panelinde birikmiş eski CSS/JavaScript katmanları final sayfadan kaldırılır; yalnız tek denetleyici çalışır.
- Panel normal belge akışında 2 kolon, dar masaüstünde tek kolon açılır; rasyon satırlarının üzerine binmez ve sayfa kaydırmasını kilitlemez.
- Aktif ek yemin ileri tarihli miktar/yem değişikliği bugünkü kaydı geleceğe taşımaz; tarihsel dönemler korunur.
- Toplam **134 otomatik test** geçmiştir; 28 solver/rasyon fonksiyonu Hotfix1.22aa ile AST düzeyinde birebir aynıdır.

## Devralınan paket: Hotfix1.22aa

Bilimsel panelin aç/kapat ve kaydırma düzeltmeleri korunmuştur; yukarıdaki tek denetleyici katmanı eski geçici uygulamaların yerini alır.

# Hotfix1.22z
- Bilimsel değerler paneli masaüstünde varsayılan kapalı başlar.
- Aç/Kapat düğmesi düşük çözünürlükte yeniden çalışır.
- Bilimsel panel açıkken sayfa kaydırması engellenmez.
- 1.22x/y scroll normalizasyonu kaldırıldı; solver değiştirilmedi.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.22y — Düşük Çözünürlük Rasyon Akışı + Donma Hotfix

- 1600 CSS px ve altında bilimsel hedef panelinin fixed/floating davranışı kapatıldı.
- Bilimsel kartlar normal belge akışında 2×2; daha dar masaüstünde tek kolon çalışır.
- Rasyon yem tablosu panelin gerçek yüksekliğinden sonra başlar; %100 zoom düşük çözünürlükte üst üste binme engellendi.
- Hotfix1.22w içindeki stok, arama, tarih ve toplu rasyon düzeltmeleri korunur.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.22w — Tutarlılık ve Düşük Çözünürlük Düzeltmeleri

- Hotfix1.22v kaynak paketi temel alınmıştır.
- Düşük çözünürlükte `Tüm bilimsel değerleri göster` panelinin başlığı açılıp içeriğinin görünmemesi giderildi; panel orta genişlikte iki, daha dar ekranda tek kolonda doğal sayfa akışına geçer.
- Yem Kataloğu araması noktalama işaretlerinden, Türkçe karakterlerden ve kelime sırasından bağımsız olarak tüm katalogda çalışır.
- Günlük yem kullanımı ve maliyet hesabı; ana rasyon, tarih aralığı, padok mevcudu ve ek yemleri birlikte değerlendirir.
- Gelecek tarihli toplu rasyon ataması bugünkü aktif rasyonu erken kapatmaz.
- Geçmiş tarihli fiziksel stok sayımı, sayımdan sonraki stok hareketlerini silmeden yalnız o tarihteki farkı işler; gelecek tarihli ve negatif sayım reddedilir.
- Solver DEV4.19.6, bilimsel hedefler ve yem miktarı optimizasyonu değiştirilmemiştir.

## Hotfix1.22w

- Düşük çözünürlükte bilimsel ayrıntı paneli için görünürlük, yükseklik ve responsive kolon düzeltmesi eklendi.
- Arama, tarih-etkin rasyon/ek yem kullanımı, gelecek tarihli atama ve tarihsel stok eşitleme akışları yeniden doğrulandı.
- 132 otomatik testin tamamı geçti; 28 solver/rasyon fonksiyonu 1.22v tabanıyla AST düzeyinde birebir aynıdır.

## Devralınan paket: Hotfix1.22v — Dashboard + Toplu Rasyon + İç Üretim + Ek Yem

- Modern/Klasik Dashboard seçimi mobilde kalıcı çalışır; seçim tekrar Moderne dönmez.
- Tek rasyon birden fazla aktif padoka aynı başlangıç tarihiyle toplu atanabilir.
- Kendi doğan buzağıya süt, yem, ot/yonca, bakım ve diğer **İç Üretim Maliyeti** kalemleri eklenebilir; bunlar nakit gideri ikinci kez oluşturmaz ve 10 aylık transferde yetişkin karta devredilir.
- Padoklara ana rasyon dışında **Ek Yem / Takviye** (kg/baş/gün) eklenebilir; ana rasyonla birlikte günlük maliyet ve stok tüketimine otomatik katılır.
- Ana rasyon ile ek yem aynı yemse stokta iki ayrı tüketim değil, tek birleşik günlük tüketim hareketi tutulur.
- Solver DEV4.19.6 ve bilimsel hedefler değiştirilmemiştir.


### Hotfix1.22v

- Düşük çözünürlükte Bilimsel Hedef Özeti 2×2, daha dar masaüstünde tek kolon düzene geçer; yem satırlarının üzerine binmez.
- Yem Kataloğu başlıkları tıklanarak artan/azalan sıralanabilir: Yem, KM, HP, NDF, ME, Ca, P, Fiyat, Stok, Günlük Kullanım ve Tahmini Yeterlilik.
- Stokta / Kritik Stok / Stok Yok filtreleri arama ve sıralamayla birlikte çalışır.
- Fiziksel Stok Eşitle, geçmişi silmeden yalnız fark kadar Sayım + / Sayım - hareketi oluşturur.
- Günlük Kullanım hesabına aktif padok ek yemleri de katılır.
- Mobil yem seç → miktar akışı korunmuştur.
- Solver/rasyon matematiği değiştirilmemiştir.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22l — Dashboard Seçim Düzeltmesi

- Mobil Safari'de Modern/Klasik seçiminin genel mükerrer kayıt korumasına takılması giderildi.
- Görünüm tercihi güvenli ve idempotent çalışır; tekrar gönderilse bile seçilen Dashboard açılır.
- Hotfix1.22k Dashboard tasarımı ve Solver DEV4.19.6 aynen korunur.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22k — Modern / Klasik Dashboard Seçimi

- Ana sayfadaki iki Dashboard'un alt alta görünmesi kaldırıldı; aynı anda yalnız seçilen görünüm açılır.
- `Modern / Klasik` seçimi hem masaüstünde hem mobilde kullanılabilir ve kullanıcı hesabına kalıcı kaydedilir.
- İlk kullanımda Modern görünüm açılır; Klasik görünüm mevcut kişiselleştirilebilir kartları ve operasyon panellerini korur.
- Hotfix1.22j mobil Dashboard düzenlemeleri ve Solver DEV4.19.6 aynen korunur.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22j — Mobil Dashboard ve Gerçek Stok Özeti

- Mobil Aylık Net tutarı, büyük meblağlarda da KPI kartının içine sığar.
- Kritik Stoklar yalnız stok girişi yapılmış yemleri ve gerçek kalan kilogramlarını gösterir; kullanılmamış katalog yemleri listelenmez.
- Son Hareketler mobilde üç kayıtla özetlenir; tam liste `Tümünü Gör` bağlantısında korunur.
- Hotfix1.22i mobil yem logosu düzeltmesi ve Solver DEV4.19.6 aynen korunur.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22i — Tek Mobil Yem Logosu

- Mobil yem kartındaki eski sıra rozeti ve CSS ile üretilen ikinci yem logosu kaldırıldı.
- Her satırda yalnız gerçek yem logosu ve onun köşesinde küçük miktar kilidi görünür.
- Hotfix1.22h masaüstü hedef kartı açılış düzeltmesi ile Solver DEV4.19.6 aynen korunur.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22h — Tek Mobil Yem Simgesi

- iPhone/Safari'de eski `::before` simgesi ile gerçek yem simgesinin birlikte görünmesi giderildi.
- Her mobil yem satırında yalnız bir gerçek simge kalır; yinelenen DOM simgeleri de açılışta temizlenir.
- Masaüstünde eski hedef tablosunun yeni kartlardan önce görünmesine yol açan ilk açılış sıçraması giderildi.
- Hotfix1.22g mobil yem ve hedef kartları ile Solver DEV4.19.6 aynen korunur.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22g — Okunabilir Mobil Rasyon Kartları

- Mobil yem satırlarında ikon, yem adı ve KM bilgileri ayrı alanlara yerleştirildi; adların birkaç harfe sıkışması giderildi.
- Miktar kilidi yem ikonunun küçük rozeti haline getirildi; `− / miktar / +` alanı geniş ve dokunulabilir kaldı.
- Mobil KM, GCAA, HP ve NDF hedefleri masaüstü tasarım dilinde ikonlu, durum rozetli ve Hedef/Rasyon karşılaştırmalı 2×2 kartlara dönüştürüldü.
- Hotfix1.22f mısır flake katalog düzeltmesi korunur; Solver DEV4.19.6 değiştirilmemiştir.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.22f — Katalog ve Mobil Yem Görseli Düzeltmesi

- MISIR PULU (FLAKED) katalog ortalaması KM %87, HP %8,5, nişasta %67,5, yağ %2 ve ME 3,10 Mcal/kg KM olarak uygulanır.
- Mevcut veritabanlarındaki eski %75/%90 nişasta kayıtları açılışta güvenli biçimde düzeltilir; makul laboratuvar kayıtları korunur.
- Mobil rasyon satırındaki yem simgesi gerçek HTML öğesi olarak ilk yüklemede çizilir; görmek için yeme dokunmak gerekmez.
- Solver DEV4.19.6 matematiği ve hedef aralıkları değiştirilmemiştir.

## Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19h — İşlevsel Rasyon Masası

Bu sürüm, Hotfix1.19g içindeki **Solver DEV4.19.6** matematiğini ve bilimsel hedef aralıklarını aynen korur; çalışma masasının kullanım katmanını geliştirir.

- Her yem satırında kalıcı miktar kilidi vardır. Kilitli miktar elle, hızlı ayarla veya Akıllı Dengeleme önerisiyle değiştirilemez.
- Yaş kilogramına ek olarak yem başına **KM kg** ve toplam rasyon KM payı canlı gösterilir.
- Katalog kaynağında açık kullanım yaşı bulunan yemler hedef yaşla karşılaştırılır. Örneğin 60–120 günlük Sunar Buzağı Büyütme yemi 11 aylık profile eklenmez.
- Solverın ilk oluşturduğu miktarlar ve sonradan yapılan değişiklikler önce/sonra özetiyle görünür.
- KM, GCAA, HP, NDF ve diğer hedeflerde hedef bölgesi ile mevcut konumu gösteren görsel şeritler eklendi.
- Mobil ve masaüstü kompakt tasarım, bilimsel nişasta bantları ve tam GCAA kayıt kapısı korunur.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19g — Bilimsel Nişasta Bantları

Bu sürüm, enerji öncelikli tam çözümü korur ve nişastayı tek bir `%28` duvarı yerine besi fazına göre yönetir. Başlangıç/Büyütme için ideal `%20–30` ve dikkat `%30–34`; Geliştirme/Orta-İleri için ideal `%24–36` ve dikkat `%36–40`; Bitirme için ideal `%28–40` ve dikkat `%40–45` uygulanır. `%45` üzeri genel sert güvenlik kapısıdır.

Nişasta dikkat bandına çıktığında sonuç tek başına reddedilmez; eNDF, etkin rumen nişastası, tahıl payı, kaba/kesif koridoru ve işleme/adaptasyon riski birlikte değerlendirilir. Böylece `%29,2` gibi başlangıç/büyütme ideal bandındaki güvenli enerji sonuçları çözülebilir.

Bu sürümde Rasyon Çöz, seçilen yemlerin günlük kilogramlarını otomatik artırıp azaltarak hedefi arar. Yaş boş bırakılan 250 kg ve üzeri besi hayvanlarında doğru genel besi DMI varsayımı kullanılır. Tam GCAA hedefi güvenli biçimde yakalanamazsa çözüm kaydedilmez ve sınırlayan kısıt açıklanır. Tehlikeli nişasta, lif, mineral, tahıl veya kaba/kesif sonuçları da kaydedilmez.

- Mobil yem kartları hedef görseldeki yatay ve kompakt satır düzenine dönüştürüldü.
- Kategori simgesi, yem adı, fiyat, `− / miktar / +`, günlük maliyet ve küçük silme ikonu tek satırda birleştirildi.
- Büyük “Çıkar” düğmesi, geniş fiyat kutuları ve üstte yinelenen işlem düğmeleri kaldırıldı.
- Rasyon toplam kg değeri yem başlığında canlı gösterilir.
- Profil, çözüm özeti, 2×2 KPI kartları ve alt Yem Ekle/Kaydet çubuğu korunur.
- Solver DEV4.19.6, bilimsel hedef aralıkları ve rasyon hesapları değiştirilmemiştir.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19c — Görsel Akış + Çözüm Durumu Düzeltmesi

- Solverın oluşturup kaydettiği reçete, besin kartlarındaki küçük sapmalar nedeniyle artık yanlışlıkla “Sınırlı” gösterilmez; çözüm sonucu **Çözüldü**, küçük sapmalar **ince ayar** olarak ayrılır.
- Mobil çalışma masasındaki DOM yerleşim hatası giderildi; profil, kompakt çözüm özeti, 2×2 hedef kartları ve yem listesi doğru sırada görünür.
- Mobil bilimsel ayrıntılar yatay şerit yerine tek sütunda açılır; sayfa yatay taşmaz.
- Solver DEV4.19.3, bilimsel hedef aralıkları ve rasyon hesapları değiştirilmemiştir.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19b — Masaüstü + Mobil Rasyon Çalışma Masası

- Masaüstünde sol Yem Havuzu, orta hedef/rasyon alanı ve sağ karar paneli birlikte çalışır.
- KM, GCAA, HP ve NDF değerleri 2×2 kartlarla; nişasta, kaba/kesif ve maliyet tek satırda gösterilir.
- Profil ve bilimsel ayrıntılar isteğe bağlı açılır.
- Yem Ekle, Geri Al ve Kaydet işlemleri masaüstünde ekran altında sabittir.
- Hotfix1.19a mobil tasarımı aynen korunur.
- Solver DEV4.19.3 ve hedef aralıkları değiştirilmemiştir.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19a — Mobil Rasyon Çalışma Masası

- Mobilde çözüm durumu ve uyarı sayısı tek satırda görünür; nedenler düğmeyle açılır.
- KM, GCAA, HP ve NDF değerleri 2×2 ana kart düzenindedir.
- Nişasta, kaba/kesif ve maliyet kompakt özet satırında gösterilir.
- Rasyon yemleri büyük −/+ kontrolleriyle düzenlenir.
- Yem Ekle ve Kaydet düğmeleri ekran altında sabit kalır.
- Masaüstü görünümü, Solver DEV4.19.3 ve hedef aralıkları korunmuştur.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.19 — Rasyon Çalışma Masası 2

- Rasyon ekranında `Uygun / Sınırlı / Çözüm yok` durumu tek bakışta görünür.
- En önemli nedenler, sayısal mevcut değer ve önerilen sonraki adım aynı karar panelinde toplanır.
- Yem sayısı, günlük maliyet, alternatif öneriler, Yem Ekle, rapor ve Akıllı Dengeleme kısayolları birlikte sunulur.
- Masaüstü, tablet ve mobil için uyarlanabilir görünüm kullanılır.
- Solver DEV4.19.3, hedef aralıkları ve hesap motorları değiştirilmemiştir.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.18d — Menü ve Kontrast Düzeltmesi

- Sol üstteki üç çizgi düğmesi mobil ve masaüstünde sol menüyü açıp kapatır.
- Menü dış alana dokunma/tıklama veya `Esc` ile kapanır; erişilebilirlik durumu güncellenir.
- Tam geniş Dashboard/Üreme/Hayvan ekranlarında gizlenen sol menü çekmece olarak geri getirildi.
- Üst hızlı menü yazıları ile hastalık bilgi kartı başlık ve rozet kontrastları güçlendirildi.
- Hotfix1.18c bağlantı günlüğü koruması ile Solver DEV4.19.3, rasyon, finans, stok ve veritabanı işleyişi korunur.

# Önceki sürüm: ÇiftlikPro v3.9.23 DEV4 Hotfix1.18c — Bağlantı Günlüğü Düzeltmesi

- Windows kaynak başlatıcısı ve installer, uzaktan kapanan istemci bağlantıları için aynı korumalı HTTP sunucusunu kullanır.
- WinError 10053/10054 kaynaklı gereksiz traceback gizlenir; diğer sunucu hataları görünür kalır.
- Hotfix1.18b birleşik Dashboard ve Solver DEV4.19.3 korunur.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.18b — Birleşik Dashboard

Padok Yönetimi 2.0 tasarım dili; gerçek verilerle çalışan Dashboard, dört aşamalı Üreme Merkezi ve Hayvan 360° kartına taşındı. Dashboard'un yeni kokpiti ile kişiselleştirilebilir kartlar, kızgınlık, aşı, ödeme, finans ve işletme panelleri aynı sayfada görüntülenir. Üstteki bağlantıdan diğer panellere gidilir; **Kartları Düzenle** ile sekiz kart yuvası kişiselleştirilir. Solver DEV4.19.3 ve mevcut hesap motorları değiştirilmemiştir.

## Önceki sürüm: Hotfix1.16 — Ortak Çalışma Alanları

Hotfix1.14–1.16; Sürü Merkezi, cinsiyete duyarlı hayvan kartı, Sağlık/Finans/Rapor/Yem/Tarım çalışma alanları ve güvenli yönetim işlemlerini birlikte sunar.

## Önceki sürüm: Hotfix1.13 — Besi Performansı 2.0

Besi Performansı ekranı artık günlük kullanıma **Devam Eden** sekmesinden
başlar. Devam eden, tartım bekleyen, düşük performanslı, hedefte ve tamamlanan
hayvanlar sayaçlı sekmelerle birbirinden ayrılır.

Liste sayfa başına 10 hayvan gösterir. Bir satır seçildiğinde aynı ekranın
altında aylık tartım girişi, kilo grafiği, GCAA, 30 günlük tahmin, maliyet ve
kârlılık bilgileri tek çalışma panelinde açılır. Satılmış/kesilmiş hayvanlar
otomatik olarak Tamamlanan Besiler altında kalır; mevcut kayıtlar korunur.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.12 — Padok Çalışma Paneli

Padoklar ekranı artık üstte kompakt seçim kartları, altta seçili padoka ait tek
geniş çalışma paneli kullanır. Arama, durum filtresi, sıralama ve üç farklı
kart görünümüyle istenen padok hızla bulunur.

Seçili padokta hayvan listesi, rasyon, günlük yem tüketimi, notlar ve hareket
geçmişi sekmeler halinde izlenir. Her hayvan satırından kart açma, düzenleme,
başka padoka taşıma ve hayvan kaydını silmeden padoktan çıkarma yapılabilir.
Yeni padok ve taşıma işlemleri aynı sayfada açılan işlem pencerelerinde
tamamlanır. Mevcut veritabanı ve yüklenen fotoğraflar güncellemede korunur.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.7 — Yem Alım Faturası ve Tarihli Stok Maliyeti

Bu sürümde **Yem** kategorisi gerçek alım faturası akışına alındı. Tek faturada birden fazla yem kalemi; miktar, birim, torba kg, birim fiyat, tedarikçi, fatura no ve vade bilgisiyle kaydedilir. Finans tarafında tek gider oluşur, her ürün stoğa ayrı girer.

- `Yem` seçildiğinde işlem türü otomatik ve zorunlu olarak **Gider** olur.
- Fatura toplamı satırların `miktar × birim fiyat` toplamından hesaplanır; elle girilen toplam esas alınmaz.
- Vadeli alımda vade tarihi zorunludur ve ödeme kapatılana kadar Finans/Dashboard uyarısında kalır.
- Her yem kalemi alım tarihinde stoğa girer.
- Rasyon maliyeti artık stok hareketlerinden hesaplanan **hareketli ağırlıklı ortalama maliyeti** kullanır; geriye dönük fatura eklendiğinde sonraki maliyet geçmişi yeniden hesaplanır.
- Finans listesinde yem faturası açılır detay olarak ürün satırları, tedarikçi, fatura no ve toplamla görünür.
- Çoklu fatura silinirse bağlı stok hareketleri ve maliyet geçmişi birlikte geri alınır.
- Mobilde fatura satırları iki sütunlu kompakt düzene geçer.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.1 — Çoklu Yem Birim Fiyatı

Hotfix1.1, çoklu yem faturasında her satıra `Adet / Miktar`, `Birim`,
`Torba kg` ve seçilen birime göre `Birim Fiyat` alanlarını ekler. Kalem tutarı
`miktar × birim fiyat`, fatura toplamı ise bütün kalemlerin toplamı olarak
otomatik hesaplanır ve sunucu tarafından yeniden doğrulanır.

Torba fiyatı gerçek kg fiyatına dönüştürülür. Örneğin 50 kg'lık torba 1.000 TL
ise stok ve tarihsel yem fiyatına 20 TL/kg yazılır. Rasyon maliyetleri ilgili
tarihteki son `feed_prices` kaydını kullandığından yeni alış fiyatı, alım
tarihinden itibaren rasyon ve hayvan maliyet hesaplarına otomatik yansır.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1 — Finans Formu Güvenilirlik Düzeltmesi

Hotfix1, sahada görülen finans formu koşul hatalarını giderir. Ödeme yöntemi
`Vadeli` seçildiği anda işlem türünden bağımsız olarak Vade Tarihi alanı açılır
ve tarih zorunlu olur. Bekleyen kayıtlar vadesinden 7 gün önce Dashboard'daki
Yaklaşan Ödemeler alanına girer; vade günü ve gecikme durumu ayrıca gösterilir.

`Yem` kategorisi artık hem tarayıcıda hem sunucuda otomatik olarak `Gider`
sayılır ve çoklu yem sepeti koşulsuz açılır. Bir faturada `+ Yem Ekle` ile farklı
ürünler, torba/kg miktarları ve isteğe bağlı kalem tutarları girilebilir; tek
finans kaydıyla her ürün için ayrı stok girişi oluşur. Türkçe yazılan `243.000`
tutarı da artık `243.000,00 TL` olarak kaydedilir; `243,00 TL`ye dönüşmez.

# ÇiftlikPro v3.9.23 DEV4 — Fotoğraf, Vadeli Ödeme ve Çoklu Yem Faturası

DEV4; tüm kayıt işlemlerinde çift dokunmayı hem arayüzde hem sunucuda engeller,
işlem sırasında düğmeyi pasifleştirip durum metni gösterir. Sağlık planları,
tamamlanmış sağlık kayıtları ve ilaç tedavileri düzenlenebilir veya güvenli
biçimde silinebilir; bağlı stok ve finans kayıtları birlikte uzlaştırılır.

Padok Yönetimi artık geniş bir tablo yerine doluluk, aktif rasyon, günlük
maliyet ve padoktaki gerçek hayvanları gösteren duyarlı kartlardan oluşur.
Hayvanlar kart üzerinden taşınabilir; boş padoklar silinebilir. Mobil hayvan ve
buzağı profil fotoğrafı bilgi alanını kapatmayacak sabit küçük önizlemeye alındı.

## Önceki paket

### ÇiftlikPro v3.9.23 DEV2 — Akıllı Mobil Hayvan Ekle

DEV1 ile yeni hayvan kaydına sabit `TR` küpe ön eki, canlı mükerrer kontrolü,
en fazla 8 kamera/galeri fotoğrafı, cihaz destekli barkod/karekod okuma ve
cinsiyet–amaç–geliş kaynağı–yaşa göre değişen akıllı form eklendi. Satın alınan
hayvanın alış bedeli isteğe bağlı olarak Finansa aktarılır; çiftlikte doğanlarda
anne zorunludur ve 10 aydan küçük kayıtlar otomatik Buzağılar bölümüne gider.

### ÇiftlikPro v3.9.22 DEV2 — Tarım & Ziraat Tam CRUD

Bu sürüm özmal ve kiralık tarla kartlarını, üretim sezonlarını, tarla işlemlerini,
tohum/gübre/ilaç stoklarını, hasat lotlarını ve tarımsal kârlılığı ÇiftlikPro'ya
ekler. Tarım finansı hayvancılık finansından ayrı tutulur.

Çiftlikte kullanılacak mahsul için **Hayvancılığa İç Transfer** işlemi tek
hareketle tarım iç satış geliri, hayvancılık yem gideri ve yem stok girişi
oluşturur. Bu işlem kasa/banka hareketi değildir; transfer geri alındığında üç
bağlı kayıt birlikte silinir. Dışarıya mahsul satışı ise tarım geliri ve mahsul
stok çıkışı oluşturur.

Hasat kaydı doğrudan gelir sayılmaz. Sezon raporu; gerçekleşen satış/transfer,
kalan stok değeri, dekar verimi, üretim maliyeti ve ekonomik kâr/zararı ayrı
gösterir. DEV4.19.3 solver, hayvan maliyet/zayiat hesapları ve DEV5.1
ilaç-hastalık modülü korunmuştur.

DEV2 ile tarla, üretim sezonu, tarla işlemi, girdi alımı, hasat, dış satış,
hayvancılığa iç transfer ve manuel Tarım Finans kayıtlarının tamamına
`Düzenle` ile güvenli `Sil / Geri Al` işlemleri eklendi. Kaynak işlem
değiştirildiğinde ona bağlı tarım finansı, hayvancılık finansı, mahsul stoğu,
yem stoğu ve fiyat bağlantıları birlikte uzlaştırılır. Kullanılmış stoğu eksiye
düşürecek değişiklik veya silme engellenir; otomatik finans satırları yalnız
kendi kaynak işleminden değiştirilebilir.

## Önceki DEV4 Hotfix2 kapsamı

Hotfix2, zayiat kaydı bulunan hayvanı aktif dişi/erkek/buzağı ve tüm aktif
hayvanlar listelerinden kesin olarak çıkarır. Önceki sürümde oluşmuş ancak
durumu aktif kalmış kayıtlar uygulama açılışında otomatik onarılır.

Ölen / Kayıp Hayvanlar arşivine `Düzenle` ve onaylı `Sil / Geri Al` işlemleri
eklendi. Düzenleme tarih, olay, neden, teşhis ve kurtarma gelirini değiştirince
maliyet ile otomatik finans bağlantılarını yeniden hesaplar. Sil/Geri Al yalnız
zayiatın oluşturduğu finans satırlarını kaldırır; hayvan alış ve gerçek tedavi
kayıtlarını korur, hayvanı yeniden aktif sürüye döndürür.

## Hotfix1 kapsamı

Hotfix1, ölüm/kayıp kaydında küpeye bağlı eski finans hareketlerini uzlaştırır.
Önceden giderleştirilmiş hayvan alımı ve tedavi ikinci kez yazılmaz. Rasyon,
bakım, henüz aktarılmamış tedavi ve diğer maliyetlerden yalnız eksik kalan tutar
Finans'a `Hayvan Ölümü / Zayiat` gideri olarak eklenir. Sigorta, et ve kurtarma
geliri ayrı gelir kaydıdır ve zayiat arşivindeki brüt kayıptan düşülür.

Doğrulama örneği: 100.000 TL alış önceden finanstayken 60 gün × 180 TL rasyon
ve henüz aktarılmamış 3.000 TL tedavi için yeni gider 13.800 TL; brüt ekonomik
kayıp 113.800 TL'dir. Tedavi de önceden finanstaysa yeni gider yalnız 10.800 TL olur.

## DEV4 kapsamı

V3.9.21 DEV4 ile dişi, erkek ve buzağıların alış bedeli; günlük yem, bakım ve
padok rasyon giderleri aynı maliyet motorunda birleştirilir. Ölüm, kayıp,
zorunlu imha veya işletmeden çıkış kaydı maliyeti olay tarihinde dondurur;
finansa nakit dışı zarar, varsa sigorta/kurtarma bedelini gelir olarak aktarır.
Ölen ve kayıp hayvanlar ayrı arşivde geçmiş kayıtları silinmeden korunur.

Finans ekranı nakit gelir-giderden ayrı bir `Zayiat / Zarar` toplamı gösterir;
böylece daha önce ödenmiş alış ve işletme giderleri ikinci kez nakit gider
sayılmaz.

DEV4.19.3 solver çekirdeği değiştirilmeden korunmuştur.

## Önceki DEV3 kapsamı

V3.9.21 DEV3; ilaç kataloğu, parti/lot ve son kullanma tarihi, stok hareketi,
hayvan/buzağı tedavi kaydı, doz ve uygulama yolu, et-süt arınma tarihleri ile
ilaç giderinin finansa aktarılmasını ekler. Katalog ürünleri tedavi önerisi
değildir; doz veteriner reçetesinden girilir. Arınma tarihi son uygulama ve
ürünün doğrulanmış asgari bekleme süresinden hesaplanır.

Kurulum, açık `CiftlikPro.exe` sürecini önce normal, gerekirse zorla kapatır;
dosya değişiminden önce yerel veritabanının tarihli güvenlik kopyasını alır ve
kurulum sonunda uygulamayı yeniden başlatabilir.

DEV4.19.3 solver çekirdeği değiştirilmeden korunmuştur.

DEV4.19.3, kaydedilmiş rasyon açıldığında tarayıcıdaki canlı hedef kartının
türetilmiş NEm/NEg yerine ham sıfır alanlarını okuyarak doğru GCAA değerini
ezmesini düzeltir. Sunucu özeti, canlı miktar değişimi ve rasyon simülasyonları
artık aynı normalize edilmiş besin değerlerini kullanır.

DEV4.19.2, kullanıcının gerçek yedeğinde görülen eksik enerji alanını düzeltir.
ME değeri bulunan fakat NEm/NEg alanları boş kullanıcı yemleri artık sıfır enerji
sayılmaz; yalnız eksik alanlar NRC tipi ME dönüşümüyle çalışma değerine çevrilir.
Gerçek analiz girilmiş alanlara dokunulmaz. Aynı yaklaşım eksik TDN ve kaba yem
eNDF alanlarında muhafazakâr çalışma değeri sağlar.

DEV4.19.1, 260 kg / 10 ay / 1,40 kg GCAA saha testinde görülen geç kayıt
reddini düzeltir. Ciddi kaba/kesif koridoru sapması artık yalnız sonuçta değil,
aday araması sırasında da sert raydır; solver güvenli koridordaki yem miktarı
kombinasyonlarını önceliklendirir.

DEV4.19, seçilen kaba ve kesif yemlerin tamamını uygulanabilir alt miktarda
rasyonda tutar ve miktarlarını besin değerlerine göre yeniden dengeler. Fazın
kaba/kesif koridorunu ciddi aşan aday, toplam tahıl faz üst sınırını aşan aday
ve buğdayın tahıl KM içindeki payı `%32` üstüne çıkan aday kaydedilmez. `%30–32`
buğday payı yalnız küçük sapma olarak “sınırlı” kabul edilir. Sunar 15.26 için
`10 kg`, Kardelen 19.27 için `6–12 kg` etiket sınırları kesin korunur. 250, 350
ve 500 kg besi ile 25 litre süt senaryoları kalıcı regresyon kapısındadır.

DEV4.18, 19–20 Ağustos 2026 tarihli gerçek ürün etiketlerini Yem Kataloğu'na
işler. `Sunar 15.26 Geliştirme Besi Yemi` ile `Sunar Kardelen 19.27 Süt Yemi`
adları, etiket HP/yağ/selüloz/kül/sodyum değerleri ve kuru madde dönüşümleri
güncellenmiştir. Kardelen'in `6–12 kg/baş/gün` etiket sınırı artık süt
solverında da kesin uygulanır. NDF, nişasta, Ca/P ve KM etikette bulunmadığı için
referans tahmin olarak açıkça ayrılır.

DEV4.17, faz nişasta üst sınırını kayıt kapısı yapar; besi yemi varken süt
yemini çözümden çıkarır ve enerjiye göre GCAA kapasitesini hedefin `%1`
çevresinde tutar. Güvenli ve hedefe yakın bir aday bulunamazsa yanlış rasyonu
kaydetmek yerine sınırlayan kısıtları kullanıcıya bildirir.

DEV4.16, hedefleri karşılayan adaylar arasında nişasta ideal bandını,
buğday/tahıl KM dengesini ve hayvan profiline uygun ticari yem kullanımını
maliyet ve genel çeşitlilikten önce değerlendirir. DEV4.15 Sunar yem profilleri
ve etiket alanları korunmuştur.

Bu paket, DEV4.14 rasyon güvenlik düzeltmelerine ek olarak kullanıcının gerçek
Sunar 15.26 ve Kardelen 19.27 etiketlerini, ayrıca Sunar Buzağı Büyütme Özel
Dönem Yemi'ni Yem Kataloğu'nda tutar. Üreticinin yayımlamadığı analiz alanları
tahmin olarak açıkça işaretlenir; kesin etiket değeri gibi sunulmaz. Ürün
etiketindeki değerler ayrı alanlarda aynen saklanır; solverın kullandığı besin
alanları ise kuru madde bazındadır.

Sunar Kardelen için güncel etiketteki `6–12 kg/baş/gün`; Buzağı Büyütme için
60–120 gün ve serbest tüketim bilgisi kaynak notunda yer alır. Mevcut
kullanıcı/laboratuvar analizleri korunur.

## DEV4.13 Bilimsel Hedef Kartları

Bu paket, besi hedef kartları ile solverın aynı bilimsel hesap kaynağını kullanmasını sağlar:

- DEV4.13 Hotfix 1, saha testinde görülen 1,24/1,30 GCAA kartının yanlış yeşil görünmesini düzeltir; minimumun altındaki anlamlı her sapma açıkça gösterilir.
- eNDF ile kaba yem KM payı ayrı yorumlanır; %24,0 ideal sınırının en çok 0,5 puan üzeri ölçüm/yuvarlama tamponunda “Sınırda” olarak değerlendirilir.
- Mobilde uzun çözüm açıklaması kısa özet halinde başlar; bilimsel ayrıntılar kullanıcı isterse açılır.
- “Besi Erkek” seçimi NASEM Chapter 20 Table 20-2 büyüyen tosun/boğa profiline; düve ve kastre erkek seçimi Table 20-1 profiline bağlanır.
- Kuru madde hedefi, rasyonun gerçek NEm yoğunluğundan canlı hesaplanır; kart ve solver aynı değeri kullanır.
- HP, Ca ve P kartları eşitlik hedefi değil **minimum gereksinim** olarak değerlendirilir. Makul hedef üstü arz yanlış “fazla” hatası üretmez.
- Toplam ME kartı ana karar kartından çıkarılmıştır. Enerji yeterliliği, NEm/NEg’den hesaplanan **GCAA kapasitesi** ile gösterilir.
- INRA 2018 yem alanları NASEM değerlerine karıştırılmaz; yalnız veri kapsamı ve fermantasyon doğrulamasında kullanılır.
- Tek bir eNDF denkleminden “tahmini rumen pH” üretilmez. Toplam nişasta, bilinen nişasta yıkılabilirliği ve eNDF ile göreli asidoz riski gösterilir.
- Evrensel tahıl, buğday veya fabrika yemi yüzdesi sert kısıt değildir. Ürün etiketi/uzman dozu girilmişse kesin sınırdır.
- Güvensiz, GCAA hedefini ciddi kaçıran veya KM ile hedef büyümeyi yapay biçimde telafi eden reçete kaydedilmez; sınırlayan kısıt açıklanır.
- Mobil/masaüstü rasyon görünümü, raporlar, hayvan aktarımı ve GitHub kurulum iş akışı korunmuştur.

# ÇiftlikPro v3.9.20 — Solver DEV4

Bu geliştirme sürümü, besi rasyonu solverında **canlı ağırlık → besi dönemi → faz kaba/kesif koridoru → rumen güvenliği → besin hedefleri → kalite/maliyet** sırasını uygular.

## Faz standardı (KM bazında)

- **Besi Başlangıç:** 200–299 kg referansı, hedef yaklaşık **%50 kaba / %50 kesif** (solver koridoru %47–53 kaba).
- **Besi Geliştirme:** 300–449 kg, hedef yaklaşık **%40 kaba / %60 kesif** (solver koridoru %37–43 kaba).
- **Besi Bitirme:** 450 kg ve üzeri, yem kalitesi ve rumen güvenliğine göre **%30–40 kaba / %60–70 kesif**, merkez hedef %35/%65.

Saman zorunlu değildir. Kaliteli kaba yem (yonca, silaj, uygun kuru ot) kaba yem hedefini ve eNDF ihtiyacını karşılayabiliyorsa saman 0 olabilir. Solver düşük kaliteli kaba yemi yalnız ucuz olduğu için yükseltmemeye devam eder.

## DEV4 test planı

Aynı yem havuzuyla 250 kg, 350 kg ve 500 kg canlı ağırlıkta çözüm alın. Kaba/kesif oranı, NDF/eNDF, toplam ve etkin nişasta, göreli asidoz riski, KM, HP, ME, NEm/NEg’den GCAA kapasitesi, Ca/P ve yem dağılımını karşılaştırın.

Ana program sürümü değişmedi: **v3.9.20**.

## DEV4.12–DEV4.13 yem sınırı ilkesi

Rasyon içindeki paylar KM bazında izlenir:
`(kg/baş/gün × KM oranı) / toplam rasyon KM`.

- DEV4.11’deki toplam tahıl, ticari yem ve buğday payı kuralları evrensel bilimsel sınır olmadıkları için kaldırılmıştır.
- Başlangıç/geliştirme/bitirme nişasta rakamları muhafazakâr çalışma ve dikkat bantlarıdır; tek başlarına klinik tanı veya evrensel fizyolojik üst sınır değildir.
- Yüksek nişasta ancak hızlı yıkılabilir nişasta ve etkili lif yetersizliğiyle birlikte ciddi güvenlik kapısına dönüşür.
- Yem Kataloğu → Düzenle ekranındaki etiket alt/üst dozları solver tarafından kesin uygulanır.
- Buğdayın tahıl KM payı %50’yi geçtiğinde işleme, adaptasyon, TMR ve kaba yem yönetimi için açık uyarı verilir; uygulama kendiliğinden %40 gibi bir oran uydurmaz.

Ayrıntılı hedef kartı düzeltmesi: `docs/SOLVER_DEV4_13_HEDEF_KARTLARI.md`.
Bilimsel veri katmanı ve model sınırları: `docs/SOLVER_DEV4_12_BILIMSEL_KATMAN.md`.


## v3.9.20 Solver DEV4.1 saha paketi
- Eski `🐄 ÇiftlikPro` marka yazısı korunur; masaüstü sol menüde ayrılan başlık kutusunda yatay ve dikey merkezlenir.
- Besi dönemi varsayılan olarak canlı ağırlıktan otomatik seçilir: <300 kg Başlangıç, 300–449 kg Geliştirme, 450+ kg Bitirme.
- İstenirse Rasyon Çöz ve hedef düzenleme ekranından Besi Başlangıç / Geliştirme / Bitirme manuel seçilebilir.
- KM bazında kaba/kesif koridorları: Başlangıç %47–53 kaba (merkez %50), Geliştirme %37–43 (merkez %40), Bitirme %30–40 (merkez %35).
- Ca/P hedef üstü cezası güçlendirildi; makro hedefleri korurken mineral taşmasını azaltmaya öncelik verir.
- GitHub Actions `windows-installer.yml` pakette korunmuştur. Kurulum EXE'si GitHub Actions artifact olarak üretilebilir.

### DEV4.9 saha UI notu
Bu paket DEV4.8 solver davranışını aynen korur. Değişiklik yalnız masaüstü sidebar logo konumu ve mobildeki işlevsiz hedef göster/gizle düğmesinin kaldırılmasıdır.

## DEV4.10 rapor ve hayvan aktarımı

Rasyon modülünde besi dönemine göre nişasta hedefi, üst güvenlik sınırı, rumenle birlikte canlı hedef kartı ve yazdırılabilir besin özeti bulunur. Solver nişastayı enerji, NDF/eNDF ve kaba/kesif dengesiyle birlikte değerlendirir.

- Tüm Hayvanlar raporu mobilde sıkışık geniş tablo yerine okunaklı hayvan kartları olarak gösterilir; web önizlemede de telefona özel kart düzeni ve doğrudan temiz PDF düğmesi bulunur.
- “Excel / PDF'den Hayvan İçe Aktar” alanı Raporlar sayfasının en üstündedir ve Veri Aktarımı sayfasında ayrıca belirgin bir kısayolu vardır.
- “Raporda Gösterilecek Sütunlar” seçimleri ekrandaki listeye, mobil kartlara, web önizlemeye, doğrudan PDF'ye ve Excel çıktısına birlikte uygulanır.
# ÇiftlikPro v3.9.21 DEV2 — İlaç & Veteriner

İlaç ve veteriner ana ekranı saha kullanımına uygun özet + işlem çekmeceleri düzenindedir. Katalog, stok/SKT, tedavi, arınma ve finans bağlantısı aynı modülde izlenir. Katalog kaydı tedavi önerisi değildir; doz veteriner reçetesinden, arınma süresi Bakanlık ruhsat sorgusundaki güncel Ürün Özellikleri Özeti'nden doğrulanarak girilir.

### Hotfix1.10 notu
Dashboard ve Sağlık ekranındaki otomatik gebelik aşı alarmları artık doğrudan tamamlanabilir/ertelenebilir. Tailscale veya mobil tarayıcı bağlantı kesmelerinden doğan normal WinError 10054 kayıtları sessiz karşılanır.


## Hotfix1.22q
- Modern/Klasik Dashboard seçimi mobilde de kalıcı çalışır; seçim değeri gizli alanla güvenli gönderilir.
- Padoklar ekranına **Toplu Rasyon Ata** eklendi; tek rasyon birden fazla aktif padoka aynı başlangıç tarihiyle atanabilir.
- Aynı padokta aynı rasyon ve başlangıç tarihi zaten aktifse tekrar kayıt oluşturulmaz.
- Toplu atama sonrası günlük yem stok tüketimi anında yeniden eşitlenir.
- Solver DEV4.19.6 değiştirilmemiştir.


- 1.22x MutationObserver geri besleme döngüsü kaldırıldı; düşük çözünürlük panel normal akışta kalır.


# Hotfix1.22aj - Sağlık Merkezi ve yaklaşan işler

- Ana sayfadaki bekleyen işler artık eski planları, yeni doz/tedavi görevlerini ve önümüzdeki 30 günün gebelik aşılarını birlikte gösterir. İlk dört sağlık satırı sınırı kaldırıldı; liste kendi içinde kayar.
- Bugün Yapılacak göstergesi yalnız bugün tarihli işleri sayar.
- Sağlık kartları tarih kutusu, durum rozeti ve daha kompakt işlem düğmeleriyle yeniden düzenlendi; planlar tarih sırasıyla gösterilir.
- PDF indir / Yazdır ana sayfadan Sağlık ekranına taşındı. Çıktı seçili filtre ve küpe/ürün/işlem aramasını takip eder; yalnız bekleyen sağlık işlerini içerir. Hayvan Dosyaları geçmiş ekranında çıktı düğmeleri gizlidir.
- Padok uygulamaları çıktıdaki tek satırda hayvan sayısıyla özetlenir. Gebelik aşıları 30 günlük pencereyle alınır.
- Rasyon taslak koruması korunur. Solver, bilimsel eşikler ve stok tüketimi değiştirilmedi.

Kontrol: mevcut 137 Python testi ve ek sağlık entegrasyon testi geçti. Rasyon taslak betiği testleri tekrar geçti. Çok sayfalı A4 PDF görsel olarak kontrol edildi. Tarayıcı yerleşimi ve kullanıcının kendi kayıtlarıyla kurulum testi henüz doğrulanmadı.
