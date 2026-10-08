# Hotfix1.22br — Runtime DB / ERR_EMPTY_RESPONSE Fix

- 1.22bq'da CI dosya kilidi için eklenen global AutoClosingConnection kaldırıldı.
- Çalışan uygulamada standart sqlite3.Connection davranışı geri getirildi.
- Hızlı gebelik sonucu / kuru durum mükerrer işlem istisnaları korunuyor.
- Üreme Responsive UI ve Akıllı Üreme Yaşam Döngüsü korunuyor.

# Hotfix1.22br — Üreme Kartları Responsive UI

- Üreme Merkezi hayvan kartları masaüstünde 3 bölgeli, mobilde dikey ve kompakt düzene alındı.
- Sonucu Güncelle / Kuruya Çıkar gibi aksiyonlar kartın ayrı işlem alanında hizalandı.
- Akıllı durum satırı kart içine kompakt yerleştirildi; gereksiz boşluk ve kart yüksekliği azaltıldı.
- 1.22bo Akıllı Üreme Yaşam Döngüsü mantığı, filtreler, PDF çıktıları ve solver/rasyon kodu korunur.

## 3.9.23 DEV4 Hotfix1.22br
- Akıllı Üreme Yaşam Döngüsü: Taze, Üreme Kontrolü, Tohumlamaya Hazır, Kuruya Çıkarılacak, Kuru, Yakın Doğum ve doğum alarmı.
- Kuruya çıkar / geri al işlemi, doğumda otomatik kuru durum temizliği.
- Hayvanın geçmiş kızgınlık aralıklarından bireysel sonraki kızgınlık penceresi tahmini.
- Üreme eşikleri Ayarlar Merkezi'nden işletmeye göre değiştirilebilir.
- Üreme çıktı raporları yeni akıllı kategorileri destekler.

## 3.9.23 DEV4 Hotfix1.22bn
- Üreme Merkezi: tüm kategoriler için filtreye göre Yazdır/PDF çıktı.
- Sağlık Merkezi: ilaç/aşı planları için plan özeti Yazdır/PDF çıktı.
- Mobil çıktı düğmeleri kompakt yerleşim.

# Hotfix1.22bm — Çoklu Hayvan Sağlık / Aşı Planı

- Sağlık planı Uygulama Kapsamı'na **Birden Fazla Hayvan** eklendi.
- Küpe/takma ad ile ara → **+ Ekle** akışı ve seçilen hayvan rozetleri eklendi.
- Tek plan kaydı seçilen tüm aktif hayvan/buzağılara ayrı sağlık görevi üretir.
- Çoklu plan tek kartta görünür; **X Hayvan Yapıldı** işlemi ilgili uygulamayı tüm seçilen hayvanların sağlık geçmişine işler.
- Çoklu kapsam Aşı ve İlaç planlarında desteklenir; Muayene tek hayvan olarak kalır.
- Mükerrer seçim ve 2'den az hedef backend tarafında engellenir.

Hotfix1.22bm: Ayrı “İşlem Yapılmamış” kartı ve filtresi kaldırıldı. Boş / İşlem Bekleyen tek grup olarak gösterilir; özet satırı işlem yapılmamış ve yeniden işlem bekleyen sayılarını ayrı verir, kart rozetleri ayrımı korur.
Hotfix1.22bm: Üreme Merkezi tüm aktif dişileri kapsar. Ayrı İşlem Yapılmamış filtresi kaldırıldı; tüm boş/işlem bekleyen dişiler tek Boş / İşlem Bekleyen grubunda gösterilir. Özet satırı işlem yapılmamış ve yeniden işlem bekleyen sayılarını ayrı verir; kart rozetleri ayrımı korur.

# Hotfix1.22bj - Dashboard Hızlı Ödeme

- `Bugünün İşleri` vadeli ödeme satırına, onay pencereli ve çift gönderim kilitli `Öde` eylemi eklendi.
- Hızlı ödeme başarıyla tamamlandığında Dashboard'a dönülür ve kapanan görev bekleyen işler listesinden çıkar.
- Ödeme satırının ayrıntı bağlantısı `/finance/edit` içindeki yeni `Ödeme Durumu` kartına gider; ödeme tarihi kullanıcı tarafından değiştirilebilir.
- Genel finans kayıtlarında bekleyen/ödenmiş durumu görünür hale getirildi ve gerektiğinde `Ödenmedi Yap` geri alma eylemi eklendi.
- Ödeme kapatma işlemi denetim günlüğüne yazılır; finans tutarı, stok ve hayvan ilişkileri değiştirilmez.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22bj` ile eşlendi.

# Hotfix1.22bi - Üreme Filtresi ve Hızlı Gebelik Sonucu

- Üreme Merkezi filtrelerini etkisizleştiren geç yüklenen `display:grid!important` çakışması kesin `hidden` kuralıyla giderildi.
- Mobilde de görünen aşama çubuğuna `Gebelik Kontrolü` ve `Gebe Değil` filtreleri eklendi; Gebe filtresi tüm pozitif kayıtları gösterir.
- `Tümü` sayacı, doğuma yaklaşan alt kümesini iki kez saymadan benzersiz hayvan kimliklerinden üretilir.
- Hayvan kartındaki hızlı sonuç penceresiyle son tohumlama `Kontrol Bekliyor`, `Gebe` veya `Gebe Değil` yapılabilir.
- Hızlı düzeltme eski bir denemeyi yanlışlıkla değiştirmez; yalnız en güncel tohumlama kaydını kabul eder ve tahmini doğum tarihini sonuçla birlikte senkronlar.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22bi` ile eşlendi.

# Hotfix1.22bh - Gebelik Sayacı Senkronizasyonu

- Dashboard, Üreme Merkezi, Tohumlama listesi ve gebelik aşıları tek aktif gebelik kaynağına bağlandı.
- Dashboard her açılışta doğumla kapanması gereken eski pozitif kayıtları güvenle uzlaştırır.
- Doğum kaydı bulunan hayvan gebe sayacından, gebelik aşılarından ve gebe engelli kızgınlık listesinden çıkar.
- 1.22bg hayvan kartı ve geçmiş veri uzlaştırma düzeltmeleri korunmuştur.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22bh` ile eşitlendi.

# Hotfix1.22bg - Gebelik/Doğum Uzlaştırma

- Eski verilerde doğumdan sonra açık kalmış pozitif tohumlama kayıtları başlangıçta otomatik `Doğum` durumuna geçirilir.
- Hayvan kartı üst Gebelik KPI'sının, aktif gebelik bulunmadığı halde eski `Pozitif` sonucunu göstermesi engellendi.
- Uzlaştırma tekrar çalıştırılabilir ve yalnız doğum tarihi tohumlama tarihinden sonra olan kayıtları etkiler.
- 1.22bf masaüstü Dashboard yerleşimi ve önceki doğum/padok/sayaç düzeltmeleri korunmuştur.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22bg` ile eşitlendi.

# Hotfix1.22bf - Modern Dashboard Masaüstü Yerleşim Düzeltmesi

- `Bugünün İşleri` kartını tek satıra zorlayan 1.22be masaüstü geçersiz kılma kuralı kaldırıldı.
- Geniş ekranda görev paneli yeniden ilk sütunda iki satırı kaplar; Kritik Stoklar ve Son Hareketler ikinci satırı doldurur.
- Sağdaki kısa kartların altında oluşan büyük boşluklar giderildi; mobil Dashboard davranışı değiştirilmedi.
- 1.22be doğum sonrası gebelik kapatma, anne padoku devri ve tutarlı sürü sayaçları korunmuştur.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22bf` ile eşitlendi.

# Hotfix1.22be - Doğum ve Görünüm Tamamlama

- Dashboard sürü sayaçları pasif/zayiat kayıtlarını ve yetişkine aktarılmış buzağıları dışlayacak şekilde ortak sorguda birleştirildi.
- Yeni doğumla aktif buzağı ve toplam sayaçları artarken annenin son aktif gebeliği `Doğum` durumuyla kapanır.
- Çiftlikte doğan yavru, kullanıcı farklı bir padok seçmediyse annenin padok kimliği ve adını otomatik devralır.
- Akıllı kayıt formunda anne seçimi padoku önden doldurur; sunucu tarafı aynı kuralı zorunlu güvence olarak uygular.
- İşletmede doğan buzağı kartındaki `Alış` anlatımı kaldırıldı; köken ve başlangıç maliyeti doğru terimlerle gösterilir.
- Mobil Üreme Merkezi kaydırma hedefleri sabit menünün altında görünür kalır.
- Inno Setup ve GitHub Actions kurulum dosyası adları `1.22be` ile eşitlendi.

# Hotfix1.22bd - Dashboard Vadeli Ödeme Doğrudan İşlem

- Dashboard > Bugünün İşleri içindeki vadeli ödeme satırı artık Finans Raporu yerine ilgili finans kaydının /finance/edit ekranını açar.
- Tümünü Gör bağlantıları genel ekranlarda kalır.
- Ödeme ekranında Ödendi/Ödenmedi durumu ve Ödendi Yap işlemi mevcut akışla korunur.
- Solver/rasyon mantığına dokunulmadı.

# Hotfix1.22bd - Sunar 21.28 Tamamlayıcı Süt Yemi

- SUNAR 21.28 tamamlayıcı süt yemi katalog ve mevcut DB migrasyonuna eklendi.
- Üretici etiketi alanları ürün bazında saklandı: HP %21, ME 2800 kcal/kg, ham selüloz %8,64, yağ %3,10, kül %6,60, sodyum %0,32.
- Etikette bulunmayan alanların referans tahmin olduğu kaynak notunda açıkça belirtildi.

# Hotfix1.22ba - Dashboard stok ve doğum/gebelik düzeltmesi

- Dashboard Kritik Stoklar yalnız pozitif kalan stokları gösterir; 0 kg stoklar listeden çıkar.
- Buzağı doğum kaydında annenin ilgili aktif gebeliği otomatik olarak `Doğum` durumuna alınır.
- Üreme Merkezi ve Dashboard aktif gebelik/doğuma yaklaşan listeleri doğmuş gebeliği tekrar göstermez.
- Solver/rasyon matematiğine dokunulmadı.

# Hotfix1.22az - Sağlık ajandası üç nokta menüsü

- Sağlık ajandası işlem menüsü yerel `details` öğesi yerine dokunmatik uyumlu düğme kontrollü yapıya geçirildi.
- Açık/kapalı durum, dışarı dokunma ve Escape davranışı tek noktadan yönetildi.
- Mobil açılır menü yukarı yönlendirilerek alt durum çubuğu ve sonraki kartla çakışması önlendi.
- Mevcut sağlık planı, tamamlama, düzenleme, silme ve erteleme uçları korunmuştur.

# Hotfix1.22ax - Fotoğraf büyütme görüntüleyicisi

- Hayvan profil, fotoğraf galerisi ve buzağı profil görsellerine erişilebilir büyütme eklendi.
- Tam ekran katmanı mobil güvenli alanlara uyar; arka plan, kapatma düğmesi ve Escape ile kapanır.
- Özellik yalnız büyütülebilir olarak işaretlenen detay fotoğraflarında çalışır.
- Windows kurulum workflow'unda kalan eski `1.22au` EXE yolları `1.22ax` ile eşitlendi.
- Inno Setup yedekleme kodu `FileCopy` yerine güncel `CopyFile` işlevine geçirildi.

# Hotfix1.22aw - Hayvan fotoğrafı ve bağlı küpe düzeltmesi

- Yetişkin karta aktarılmış buzağının tarihsel satırı düzenleme sırasında yabancı mükerrer kayıt sayılmaz.
- Fotoğraf yüklemeli hayvan düzenleme akışı bağlı küpe geçmişiyle birlikte doğrulandı.
- Yalnız bağlı yetişkin/buzağı çifti hariç tutulur; diğer tüm mükerrer küpeler engellenir.

# Hotfix1.22av - Sürü Merkezi filtre hizalaması

- Masaüstü arama ve filtre kontrolleri ortak 16 px etiket ve 44 px kontrol satırlarına sabitlendi.
- Orta çözünürlükte kalan içerik alanına göre küçülen akışkan sütunlar kullanıldı.
- Dar masaüstünde güvenli tek sütun geçişi korunurken mobil akordeon kuralları değiştirilmedi.

# Hotfix1.22au - Mobil Bugünün İşleri düzeltmesi

- Mobil Dashboard görev listesinde yatay kaydırma kapatıldı; liste yalnız dikey kayar.
- Uzun görev adı ve açıklamalar iki satıra kadar sarılır, tarih ve kalan-gün rozeti kart içinde kalır.
- Dört görev filtresi telefon genişliğinde tek sabit sıraya dönüştürüldü.
- Düzeltme yalnız `Bugünün İşleri` paneline sınırlandı; Sürü Merkezi ve masaüstü görünümü değiştirilmedi.

# Hotfix1.22at - Mobil Sürü görünümü düzeltmesi

- Ayrıntı görünümünde mobil kart başlığı ve veri alanları yeniden ölçülendirildi; taşan/kesilen hayvan adı ile gereksiz büyük Tür/Durum kutuları düzeltildi.
- Kompakt görünümün işlemleri tek satırda üç sabit ikon düğmesine dönüştürüldü; yazı çakışması ve çift çöp kutusu kaldırıldı.
- İşlem bağlantılarına erişilebilir başlıklar eklendi; kayıt silme onayı ve sunucu işlemleri değiştirilmedi.
- Kart görünümü ve masaüstü Sürü Merkezi düzenleri korunmuştur.

# Hotfix1.22as - Sürü Merkezi görünüm sistemi

- Ayrıntı, Kart ve Kompakt görünüm seçenekleri eklendi.
- Görünüm tercihi kullanıcı hesabına kaydedilerek kategori ve sayfa geçişlerinde kalıcı hale getirildi.
- Kart düzeni masaüstünde akışkan ızgara, mobilde tek sütun fotoğraflı kart olarak düzenlendi.
- Kompakt düzen masaüstü ve mobilde daha fazla kaydı gösterirken temel işlemleri erişilebilir tuttu.
- Dişi, Erkek ve Buzağı aynı görünüm bileşenini kullanır; arşivlerin finans ve geri alma sütunları değiştirilmedi.

# Hotfix1.22ar - Tek Sürü Merkezi yönlendirmesi

- Sol menü, Dashboard özetleri ve eski kategori adresleri Dişi, Erkek ve Buzağı filtreleriyle Sürü Merkezi'ne bağlandı.
- Buzağı detayından dönüş ile kayıt ekleme, düzenleme ve silme sonrasındaki dönüş adresleri yeni listeye geçirildi.
- Eski bağlantılardan gelen arama ve filtre bilgileri korunur; aynı kategori için iki farklı arayüz açılması önlendi.

# Hotfix1.22aq - Kompakt seçili hayvan kartı

- Mobil Üreme Merkezi seçili hayvan detayı yeniden boyutlandırıldı; yatay taşma ve gereksiz dikey alan azaltıldı.
- Tekrarlanan küpe metriği mobilde gizlendi; padok ve aşama iki kompakt rozet olarak gösterilir.
- Beş aşamalı üreme akışı küçük ikonlarla ekran genişliğine sabitlendi.
- Hayvan kartı ve tüm kayıtlar bağlantıları mobilde kısa etiketlere dönüştürüldü.
- Masaüstü detay kartının bilgi yoğunluğu ve yerleşimi değiştirilmedi.

# Hotfix1.22ap - Aşama filtreli Üreme Merkezi

- Mobil Safari kaydırmasında oluşan `resize` olayının akordeonu başlangıç durumuna döndürmesi engellendi; durum yalnız mobil/masaüstü eşiği gerçekten değiştiğinde yeniden kurulur.
- İşlem düğmeleri tek satır, sınırlı genişlik ve güvenli kutu ölçüsüyle kart içine sabitlendi.
- Masaüstü Üreme Merkezi aşama sekmeleriyle filtrelenen tek geniş liste düzenine geçirildi.
- Pozitif gebelik kayıtları için ayrı `Gebe` filtresi eklendi; mobilde mevcut dört akordeon korunarak tekrar eden gebe bölümü gizlendi.
- Arama, padok ve aşama filtreleri birlikte çalışır; mevcut kayıt formları ve işlem uçları değiştirilmedi.

# Hotfix1.22ao - Mobil Üreme Merkezi

- Üreme Merkezi'nin dört operasyon bölümü mobilde açılır/kapanır kompakt kartlara dönüştürüldü.
- Açık bölümde ilk üç hayvan fotoğraf, kimlik özeti, durum ve işlemle gösterilir; daha uzun listeler isteğe bağlı açılır.
- Fotoğraf kaynağı hayvan profil fotoğrafından, yoksa fotoğraf geçmişindeki ilk kayıttan alınır; fotoğraf yoksa güvenli simge kullanılır.
- Arama ve padok filtresi akordeon görünümüyle birlikte çalışır; eşleşen bölüm otomatik açılır.
- Masaüstü dört sütun görünümü ile mevcut Tohumlandı, Sonuç Gir, Kontrol Kaydet ve Doğum Kaydet akışları korunmuştur.

# Hotfix1.22an - Fotoğraflı ve sıralanabilir Sürü Merkezi

- Masaüstü filtre denetimleri kalıcı görünür hale getirildi; boş kalan sağ alan giderildi.
- Aktif hayvan ve buzağı sorgularına profil fotoğrafı eklendi; galeri fotoğrafı yedek kaynak olarak kullanılır.
- Hayvan, Tür, Irk, Padok, Yaş ve Durum sütunlarına sunucu taraflı artan/azalan sıralama eklendi.
- Masaüstü satırı fotoğraflı kimlik özetine; mobil satır fotoğraflı kompakt karta dönüştürüldü.
- Sıralama, filtre, kategori ve sayfalama parametreleri birlikte korunur.

# Hotfix1.22am - Sürü Merkezi araç çubuğu

- Filtre formu sunucu HTML'inde yenilendi; masaüstünde hizalı, mobilde açılır bölüm.
- Tür alanı yerine mevcut kategori sekmeleri kullanılır; arama ve padok seçimi kategori/sayfalama bağlantılarında korunur.
- Sonuç özeti eklendi; mobil hayvan kartları kompaktlaştırıldı. İşlem düğmelerinin tek sırası korunur.
- Sürü Merkezi dışındaki filtre formları, solver ve stok hesapları değiştirilmedi.

# Hotfix1.22al - Mobil hayvan işlem satırı

- Sürü Merkezi mobil kartlarında Görüntüle, Düzenle ve Sil işlemleri tek satırda düzenlendi.
- Silme düğmesi kompakt ikon görünümüne geçirildi; 44 px dokunma alanı ve kayıt silme onayı korundu.
- Kural yalnız Sürü Merkezi mobil tablosuna sınırlandı; masaüstü ve diğer modüller etkilenmez.

# Hotfix1.22ak - Dashboard ilk çizim düzeltmesi

- Modern/Klasik Dashboard anahtarının CSS'i ilk HTML çiziminden önce `<head>` içinde yüklenir.
- Mobil Safari'de görülen ham mavi, alt alta buton parlaması kaldırıldı.
- `APP_LABEL`, `APP_VERSION` ile eşitlendi; alt durum çubuğu artık gerçek paket sürümünü gösterir.
- Modern/Klasik tercih davranışı, sağlık ajandası, solver ve stok hesapları değiştirilmedi.

# Hotfix1.22aj - Sağlık Merkezi ve yaklaşan işler

- Ana sayfadaki bekleyen işler artık eski planları, yeni doz/tedavi görevlerini ve önümüzdeki 30 günün gebelik aşılarını birlikte gösterir. İlk dört sağlık satırı sınırı kaldırıldı; liste kendi içinde kayar.
- Bugün Yapılacak göstergesi yalnız bugün tarihli işleri sayar.
- Sağlık kartları tarih kutusu, durum rozeti ve daha kompakt işlem düğmeleriyle yeniden düzenlendi; planlar tarih sırasıyla gösterilir.
- PDF indir / Yazdır ana sayfadan Sağlık ekranına taşındı. Çıktı seçili filtre ve küpe/ürün/işlem aramasını takip eder; yalnız bekleyen sağlık işlerini içerir. Hayvan Dosyaları geçmiş ekranında çıktı düğmeleri gizlidir.
- Padok uygulamaları çıktıdaki tek satırda hayvan sayısıyla özetlenir. Gebelik aşıları 30 günlük pencereyle alınır.
- Rasyon taslak koruması korunur. Solver, bilimsel eşikler ve stok tüketimi değiştirilmedi.

Kontrol: mevcut 137 Python testi ve ek sağlık entegrasyon testi geçti. Rasyon taslak betiği testleri tekrar geçti. Çok sayfalı A4 PDF görsel olarak kontrol edildi. Tarayıcı yerleşimi ve kullanıcının kendi kayıtlarıyla kurulum testi henüz doğrulanmadı.

# 3.9.23 DEV4 Hotfix1.22af

- Windows installer artık kullanıcı profiline kurulum için yönetici hesabını zorunlu tutmaz (`PrivilegesRequired=lowest`).
- Yönetici yetkisi gerektiren otomatik `netsh` güvenlik duvarı komutları kurulum/uninstall akışından kaldırıldı; bu komutlar artık kurulumu bloke etmez.
- Dashboard > Bugünün İşleri satırında tarih alanı 84 px yapıldı; tarih, içerik ve kalan-gün rozeti düşük çözünürlükte birbirine binmez.
- 1.22ae süt/rasyon responsive düzenlemeleri korunur.

# Hotfix1.22af – GitHub Test/Paketleme Düzeltmesi

- 1.22ae ile uyumsuz kalan 9 regresyon testi 1.22ae sürüm beklentisine güncellendi.
- GitHub Actions ve Inno Setup çıktı adı `Hotfix1_22af_Setup.exe` olarak eşitlendi.
- Rasyon/süt işlev kodunda geri alma yapılmadı.


## v3.9.23 DEV4 Hotfix1.22af
- Mobil Süt & Laktasyon giriş kartları kompaktlaştırıldı; giriş kutuları kısaltıldı ve alt durum çubuğu için güvenli boşluk artırıldı.
- Rasyon Hedef ↔ Rasyon kartlarında düşük çözünürlükte KM/GCAA/HP/NDF hedef ve rasyon değerlerinin taşması azaltıldı.
- Hedef kartlarının altındaki tamamlama/progress şeritleri kaldırıldı.
- Nişasta ve Kaba/Kesif özetlerine hedef aralığı ile mevcut rasyon değeri birlikte eklendi.
- Solver/hesap çekirdeği değiştirilmedi.
# Hotfix1.22ad – Mobil Süt Girişi Responsive

- Mobilde Süt & Laktasyon tablosu kart düzenine çevrildi; yatay taşma kaldırıldı.
- Sabah/Akşam girişleri dokunmatik kullanım için büyütüldü.
- Girilen Sabah + Akşam değeri kartta Bugün toplamını anlık günceller.
- Arama ve kaydet butonu mobilde tam genişlik oldu.
- Masaüstü süt tablosu ve 1.22ac süt altyapısı korunmuştur.

# Hotfix1.22ad – Süt & Laktasyon Yönetimi V1

- Süt & Laktasyon Merkezi eklendi.
- Sabah/akşam toplu süt girişi ve günlük toplam.
- DIM, laktasyon numarası, 7/30 gün ortalaması, pik, laktasyon toplamı ve 305 gün tahmini.
- Önceki 7 güne göre %15+ düşüşte uyarı.
- Hayvan kartında süt yağı, protein ve SCC kaydı.
- Eski süt kayıtları ve veritabanı korunur.

# Hotfix1.22ab
- Hotfix1.22aa paketi tüm testler ve sürüm dosyalarıyla yeniden kontrol edildi.
- Bilimsel panelde aynı anda çalışan eski `w/x/z/aa` aç/kapat katmanları final HTML'den kaldırıldı; tek, bağımsız denetleyici bırakıldı.
- Düşük çözünürlükte panel doğal sayfa akışında görünür; rasyon tablosuyla çakışmaz ve sayfa kaydırması kilitlenmez.
- Aktif ek yem ileri tarihe düzenlendiğinde mevcut dönem korunur, yeni miktar/yem ayrı gelecek dönem kaydı olarak planlanır.
- Solver DEV4.19.6 ve bilimsel hedefler değiştirilmedi; 134 otomatik test geçti.

## Devralınan Hotfix1.22aa
- Bilimsel değerler butonundaki eski üst üste click handler zinciri temizlendi.
- Bilimsel panel artık bağımsız aç/kapat sınıfıyla yönetilir; ikinci tıklamada güvenli biçimde kapanır.
- Panel açılırken body/html scroll kilidi temizlenir; sayfa yukarı-aşağı kaymaya devam eder.
- Solver DEV4.19.6 değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22z
- Bilimsel değerler panelinin düşük çözünürlükte zorla açık kalması düzeltildi.
- Bilimsel değerler aç/kapat düğmesi ve sayfa kaydırması düzeltildi.
- Solver DEV4.19.6 korunmuştur.

## 3.9.23 DEV4 Hotfix1.22y
- Düşük çözünürlük panelindeki MutationObserver geri besleme döngüsü kaldırıldı; tarayıcı donması giderildi.
- 1366×768 / %100 benzeri düşük masaüstü çözünürlüklerinde bilimsel hedef panelinin rasyon tablosu üzerine binmesi giderildi.
- Floating panel 1600 CSS px ve altında devre dışı; panel normal akışta 2×2 / tek kolon responsive çalışır.
- Solver matematiği değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22w
- Hotfix1.22v kaynak paketi esas alınarak tüm regresyon kontrolleri yeniden çalıştırıldı.
- Düşük çözünürlükte açıldığı halde içeriği görünmeyen `Tüm bilimsel değerler` paneli, orta genişlikte 2 kolon ve daha dar ekranda tek kolon olarak görünür doğal akışa alındı.
- Yem Kataloğu araması Türkçe karakter, noktalama ve çok kelimeli sorgularda tüm katalog üzerinde tutarlı çalışır.
- Günlük yem kullanımı ve maliyet hesabı; tarih-etkin ana rasyon, padok mevcudu ve ek yemleri birlikte hesaplar.
- Gelecek tarihli toplu rasyon ataması mevcut rasyonu atama tarihine kadar korur.
- Geçmiş tarihli fiziksel stok sayımı, sonraki hareketleri koruyarak sayım tarihindeki farka göre hareket oluşturur; negatif ve gelecek tarihli sayım engellenir.
- Solver DEV4.19.6 ve 28 solver/rasyon fonksiyonu Hotfix1.22v tabanıyla AST düzeyinde birebir aynıdır.
- 132 otomatik testin tamamı başarıyla geçti.

## 3.9.23 DEV4 Hotfix1.22v
- Düşük çözünürlükte Bilimsel Hedef Özeti 2×2 / tek kolon responsive düzene geçer; rasyon yem satırlarının üstüne binmez.
- Yem Kataloğu başlıkları tıklanarak Yem, KM, HP, NDF, ME, Ca, P, Fiyat, Stok, Günlük Kullanım ve Tahmini Yeterlilik alanlarına göre artan/azalan sıralanabilir.
- Stokta / Kritik Stok / Stok Yok filtreleri arama ve sıralamayla birlikte çalışır.
- Fiziksel Stok Eşitle işlemi geçmiş hareketleri silmeden yalnız fark kadar Sayım + / Sayım - hareketi oluşturur.
- Günlük Kullanım hesabına aktif padok ek yemleri de dahil edilir.
- Solver DEV4.19.6 değiştirilmemiştir.

## 3.9.23 DEV4 Hotfix1.22u
- Yem Kataloğu araması artık yalnız açık sayfadaki 15 satırı değil tüm aktif kataloğu tarar.
- Yazdıkça arama 350 ms bekleme sonrası sunucu tarafında tüm katalogda yenilenir.
- Türkçe karakterler aramada normalize edilir (ı/i, ş/s, ğ/g, ü/u, ö/o, ç/c).
- Solver/rasyon matematiğine dokunulmadı.

## 3.9.23 DEV4 Hotfix1.22t
- Mobil yem seçimi iki adımlı akış: yem seç → miktar gir → ekle/güncelle.
- Yem seçildiğinde liste kapanır; miktar alanı doğrudan görünür, “Yem Değiştir” ile listeye dönülür.
- iPhone Safari için alt dock modal açıkken gizli kalır; solver matematiği değişmedi.

- Mobil yem ekleme ekranı tek kompakt pencereye dönüştürüldü; alt sabit dock pencere açıkken gizlenir.
- Seçilen yem için kg miktarı ve Rasyona Ekle/Güncelle alanı her zaman görünür tutuldu.
- Yem ekleme penceresine kapatma düğmesi eklendi.
- Buzağı kartı Fotoğraf ve Kilo/Gelişim bölümlerindeki düşük çözünürlük taşmaları giderildi.
- Solver DEV4.19.6 korunmuştur.

## 3.9.23 DEV4 Hotfix1.22q
- Padok Ek Yem / Takviye kartları kompaktlaştırıldı; Düzenle ve Kaldır işlemleri yan yana alındı.
- Ek yem kaydı artık yem, kg/baş/gün, başlangıç tarihi ve not alanlarıyla yerinde düzenlenebilir.
- Hayvan kartındaki Kilo Gelişim / Tartım Geçmişi düşük çözünürlükte responsive kart satırlarına dönüşür; yatay taşma engellendi.
- Tartım giriş alanları dar ekranlarda 2 kolon / tek kolon düzene geçer.
- Rasyon solver DEV4.19.6 değişmedi.


## 3.9.23 DEV4 Hotfix1.22p
- Rasyon Çalışma Masası altındaki eski tek-padok dropdown kaldırıldı.
- Padoklar işaret kutuları ile çoklu seçilebilir.
- Tümünü Seç / Seçimi Temizle / Seçili Padoklara Ata / Tüm Aktif Padoklara Ata eklendi.
- Mevcut `/ration/assign-bulk` güvenli toplu atama altyapısı doğrudan çalışma masasına bağlandı.

## 3.9.23 DEV4 Hotfix1.22b — Referans UI yakınlaştırma
- Masaüstü rasyon masası referans görsele daha yakın yeniden düzenlendi.
- Çözüm Durumu Yem Havuzu altında görünür akışta tutuldu.
- KPI kartlarına referanstaki ilerleme rayları eklendi.
- Rasyon tablosu, satırlar, kilit/miktar grubu, silme ve toplam satırı kompaktlaştırıldı.
- Alt işlem barı sabit overlay olmaktan çıkarılıp tablonun doğal altına alındı.
- Rasyon Bilgileri sağ drawer görünümüne yaklaştırıldı.
- 1.22a mobil kompakt satır düzeni korundu.

## v3.9.23 DEV4 Hotfix1.22
- Rasyon çalışma masası referans görsele göre yeniden düzenlendi.
- Çözüm Durumu Yem Havuzu altında görünür ve sabit akışta.
- KPI kartları, kompakt yem tablosu ve mobil kilit/miktar kontrolü yenilendi.
- Solver ve bilimsel hesap çekirdeği korunmuştur.

# Hotfix1.21 — Referans Rasyon UI
- Çözüm Durumu Yem Havuzu altına taşındı.
- Hedef/Rasyon kartları referans görseldeki modern dört kart tasarımına geçirildi.
- Kilit + miktar kontrolleri tek kompakt satırda; mobil taşma azaltıldı.
- Solver ve bilimsel hesap çekirdeği değiştirilmedi.

# ÇiftlikPro v3.9.23 DEV4 Hotfix1.20

- Rasyon Çözüm Durumu ana çalışma kolonuna alındı; sol alta kayma giderildi.
- Yem miktar kilitleri miktar kontrol hücresine hizalandı.
- Hedef ↔ Rasyon Özeti daha kompakt ERP şeridine dönüştürüldü.
- Rasyon Bilgileri sağdan açılan panel haline getirildi.
- Mısır Pulu (Flaked): KM %87, HP %8,5, nişasta %67,5, yağ %2, ME 3,10 Mcal/kg olarak güncellendi; NDF gibi kullanıcı tarafından verilmeyen alanlar korunur.
- Mobil rasyon yem ikonları ilk HTML renderında atanır; tıklama beklemeden görünür.

## 3.9.23 DEV4 Hotfix1.19h — İşlevsel Rasyon Masası

- Rasyon kalemi miktar kilidi kalıcı hale getirildi; kilitli yemler elle ve Akıllı Dengeleme uygulamalarında korunur.
- Her yem için yaş miktarı, KM kg ve toplam rasyon KM payı birlikte canlı gösterilir.
- Ürün kaynağındaki açık yaş aralığı hedef profile uymuyorsa yem seçimden önce engellenir ve mevcut reçetede uyarılır.
- Solver sonucu ile kaydedilmemiş miktar/kilit değişiklikleri önce/sonra özetinde gösterilir.
- Hedef kartlarına masaüstü ve mobilde çalışan hedef aralığı şeritleri eklendi.
- Solver çekirdeği ve bilimsel hedefler değiştirilmedi; sürüm `DEV4.19.6` olarak korundu.

## 3.9.23 DEV4 Hotfix1.19g — Bilimsel Nişasta Bantları

- `%28` tek ve sert nişasta engeli kaldırıldı; nişasta artık besi fazına göre ideal, dikkat ve genel güvenlik katmanlarıyla değerlendirilir.
- Başlangıç/Büyütme: ideal `%20–30`, dikkat `%30–34`.
- Geliştirme/Orta-İleri: ideal `%24–36`, dikkat `%36–40`.
- Bitirme: ideal `%28–40`, dikkat `%40–45`.
- `%45` üzeri genel güvenlik kapısıdır; daha düşük sonuçlar eNDF, hızlı rumen nişastası, tahıl ve kaba/kesif raylarıyla birlikte değerlendirilir.
- `%29,2` gibi büyütme fazında ideal bantta kalan sonuçlar artık yalnız nişasta nedeniyle reddedilmez.
- Enerji/GCAA önceliği, seçili yem miktarı optimizasyonu ve çalışma masası tasarımı korunmuştur.
- Solver motoru `DEV4.19.6` olarak işaretlendi.

## 3.9.23 DEV4 Hotfix1.19f — Enerji Öncelikli Tam Çözüm

- GCAA açığı bulunan sonuçların `%8'e kadar` **Sınırlı çözüm** olarak kaydedilmesi kaldırıldı.
- Solver, güvenlik rayları içinde GCAA hedefini önceliklendirir; arpa, mısır silajı ve uygun besi yemi gibi yüksek net enerjili seçili yemleri artırırken gereksiz HP yükselten yemleri azaltır.
- HP fazlası için yumuşak ceza `%20` yerine `%10` güvenlik payından sonra başlar.
- Enerji tohumlaması artık ME yanında NEm/NEg yoğunluğunu kullanır ve fazla HP/nişastayı geri plana iter.
- GCAA hedefinin `%0,5` altında kalan rasyon kaydedilmez; gerçek engel kullanıcıya bildirilir.
- Hedef veya güvenlik uyarısı bulunan kayıt artık yeşil **Çözüldü** görünmez; doğru durum **Sınırlı** veya **Çözüm yok** olur.
- Solver motoru `DEV4.19.5` olarak işaretlendi.

## 3.9.23 DEV4 Hotfix1.19e — Seçili Yem Akıllı Dengeleme

- Rasyon Çöz, kullanıcının seçtiği yemlerin kg miktarlarını artırıp azaltarak önce tam hedefi arar.
- Yaş boş bırakılan 250 kg ve üzeri besi hayvanlarında yanlışlıkla buzağı DMI denklemine düşme düzeltildi.
- Güvenlik raylarını aşmayan ve yalnız GCAA hedefini en fazla %8 kaçıran en iyi aday artık açıkça **Sınırlı çözüm** olarak miktarlarıyla kaydedilir; hedefe ulaşılmış gibi gösterilmez.
- Nişasta, NDF/eNDF, mineral, tahıl ve ciddi kaba/kesif güvenlik kapıları korunur; tehlikeli adaylar kaydedilmez.
- Ekranda `%47,0` görünen kaba yem oranının aynı anda “%47'nin altında” denmesine yol açan yuvarlama uyuşmazlığı düzeltildi.
- Solver motoru `DEV4.19.4` olarak işaretlendi.

## 3.9.23 DEV4 Hotfix1.19d — Kompakt Mobil Rasyon

- Mobil yem tablosu hedef tasarımdaki kompakt yatay satır bileşenine dönüştürüldü.
- Yem türüne göre kategori simgesi, kompakt miktar kontrolü ve küçük silme işlemi eklendi.
- Fiyat ve günlük maliyet satır içinde sadeleştirildi; toplam kg canlı başlığa eklendi.
- Yinelenen mobil üst işlemler kaldırıldı; sabit alt Yem Ekle/Kaydet çubuğu korundu.
- Masaüstü çalışma masası, Solver DEV4.19.3, hedef aralıkları ve hesaplar değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.19c — Görsel Akış + Çözüm Durumu Düzeltmesi

- Mobilde karar panelini yanlış DOM ebeveynine ekleyen yerleşim hatası düzeltildi.
- Solver tarafından kaydedilmiş reçetelerde genel durum “Çözüldü”; küçük besin sapmaları ayrı “ince ayar” olarak gösterilir.
- Kaydedilmemiş kullanıcı değişikliklerinde durum yeniden canlı kartlara göre değerlendirilir.
- Mobil bilimsel ayrıntı görünümünde yatay taşma kaldırıldı.
- Solver DEV4.19.3, hedef aralıkları ve hesap fonksiyonları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.19b — Masaüstü + Mobil Rasyon Çalışma Masası

- Masaüstünde sol Yem Havuzu, orta çalışma alanı ve sağ Çözüm Durumu paneli üç sütunlu düzende birleştirildi.
- Hayvan profili ve seçili yem sayısı kompakt üst çubukta toplandı.
- KM, GCAA, HP ve NDF için 2×2 ana hedef kartları eklendi; nişasta, kaba/kesif ve maliyet tek satıra alındı.
- Profil formu ve tüm bilimsel hedefler isteğe bağlı açılır hale getirildi.
- Yem Ekle, Geri Al ve Değişiklikleri Kaydet masaüstünde sabit alt işlem çubuğuna taşındı.
- Hotfix1.19a mobil tasarım, Solver DEV4.19.3 ve hedef aralıkları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.19a — Mobil Rasyon Çalışma Masası

- Mobil karar paneli tek satırlık durum/uyarı özetine küçültüldü; neden ve ayrıntılar isteğe bağlı açılır.
- KM, GCAA, HP ve NDF için 2×2 ana hedef kartları eklendi.
- Nişasta, kaba/kesif ve maliyet ikincil özet satırında toplandı.
- Bilimsel hedeflerin tamamı ayrı aç/kapat alanında korunur.
- Mobil yem satırları büyütülmüş miktar kontrolleriyle sadeleştirildi.
- Yem Ekle ve Kaydet işlemleri ekran altındaki sabit işlem çubuğuna taşındı.
- Masaüstü Hotfix1.19 görünümü, Solver DEV4.19.3 ve hedef aralıkları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.19 — Rasyon Çalışma Masası 2

- Mevcut rasyon sonucu için `Uygun / Sınırlı / Çözüm yok` durum şeridi eklendi.
- Bilimsel hedef kartlarındaki en güçlü uyarılar, neden ve önerilen sonraki adımla birlikte yeni karar panelinde gösterilir.
- Yem sayısı, günlük maliyet, alternatif öneri sayısı ve hızlı işlem bağlantıları tek alanda toplandı.
- Karar paneli masaüstünde sağ sütun, orta genişlikte alt panel, mobilde üst kart olarak uyarlanır.
- Solver DEV4.19.3, hedef aralıkları, rasyon hesapları ve kayıt akışları değiştirilmedi.
- Hotfix1.18d menü/kontrast ve Hotfix1.18c bağlantı günlüğü düzeltmeleri korunur.

## 3.9.23 DEV4 Hotfix1.18d — Menü ve Okunabilirlik

- Tam geniş çalışma kabuğunda CSS ile gizlenen sol menü, mobil ve masaüstünde çalışan erişilebilir çekmeceye dönüştürüldü.
- Üç çizgi düğmesinin aç/kapa durumu, dış alana tıklama, menü bağlantısı seçme, pencere boyutu değişimi ve `Esc` kapanışı birlikte yönetilir.
- Üst hızlı menü bağlantılarında açık zemin üzerinde koyu metin ve belirgin aktif/odak rengi sabitlendi.
- Hastalık bilgi kartındaki koyu zemin üstü başlık beyaza; açık rozet yazıları yüksek kontrastlı koyu yeşile çevrildi.
- Hotfix1.18c bağlantı günlüğü düzeltmesi, Dashboard, Solver DEV4.19.3, stok, finans ve veritabanı işlemleri korunur.

## 3.9.23 DEV4 Hotfix1.18c — Windows Başlatıcı Bağlantı Günlüğü

- Windows başlatıcısı kaynak sunucuyla aynı korumalı HTTP sunucu sınıfını kullanır. Tailscale ve tarayıcı bağlantısı aniden kapandığında görülen WinError 10053/10054 traceback'i artık gereksiz yere konsola basılmaz.
- Diğer istisnalar görünür kalır; Dashboard, Solver DEV4.19.3, stok ve finans hesapları korunur.

## 3.9.23 DEV4 Hotfix1.18b — Birleşik Dashboard

- Yeni referans tasarımlı kokpit korunurken önceki Dashboard işlevleri yeniden görünür hale getirildi.
- Kişiselleştirilebilir Dashboard Kartlarım ve kart düzenleme akışı geri getirildi.
- Yaklaşan kızgınlık, gebelik aşısı, vadeli ödeme, besi performansı, finans eğilimi, doğum, sağlık ve işletme özetleri birleştirildi.
- Mevcut işlem butonları ve kayıt akışları korunarak yalnızca sunum katmanı birleştirildi.
- Yeni kokpitten eski panellere doğrudan geçiş bağlantısı eklendi; gereksiz çift Dashboard şablonu temizlendi.

## 3.9.23 DEV4 Hotfix1.18a — Tam Genişlik Yerleşim Düzeltmesi

- Sol menü gizlendiğinde kalan 198 px boşluk kaldırıldı; ana içerik gerçek ekran genişliğine oturtuldu.
- Dashboard'un sağdan taşması ve Aylık Net/sağ panel kesilmesi düzeltildi.
- ÇiftlikPro başlığı ve Dashboard bağlantısı referans tasarımdaki üst başlığa geri getirildi.
- Üst menü yüksekliği ve içerik başlangıcı referans görsellere göre hizalandı.
- Dashboard karşılaması yerel saate göre Günaydın, İyi Günler, İyi Akşamlar veya İyi Geceler olarak değişiyor.

## 3.9.23 DEV4 Hotfix1.18 — Referans Tasarım Paketi

- Dashboard, Üreme Merkezi ve Hayvan 360° ekranları referans görsellerdeki tam geniş üst menü ve kart düzenine uyarlandı.
- Dashboard görev kartına Tümü, Geciken, Bugün ve Yaklaşan çalışan filtreleri eklendi.
- Üreme Merkezi'ne gerçek padok filtresi, açıklamalı sütunlar ve ayrıntılı seçili hayvan süreç kartı eklendi.
- Mobilde KPI kartları iki sütuna alındı; üst menü kontrollü yatay kaydırmalı hale getirildi.
- Solver, rasyon hesapları, padok işlemleri, finans ve stok motorları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.17 — Dashboard 2.0 · Üreme Merkezi · Hayvan 360°

- Padok panelinin görsel dili Dashboard, Üreme Merkezi ve hayvan detayına taşındı.
- Dashboard gerçek sağlık, vade, doğum, yem stoku ve işlem günlüğü verileriyle yeniden düzenlendi.
- Üreme kayıtları kızgınlık → tohumlama → gebelik kontrolü → doğum akışında birleştirildi.
- Hayvan 360° kartına gebelik ilerlemesi, sağlık özeti, kilo grafiği, finans özeti, zaman çizgisi ve hızlı işlemler eklendi.
- Mobil ve tablet kırılımları eklendi; Solver DEV4.19.3 ve hesap motorları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.16 — Ortak Çalışma Alanları

- Hotfix1.14: Sürü Merkezi ve cinsiyete duyarlı hayvan detay sekmeleri eklendi.
- Hotfix1.15: Sağlık, Finans ve Raporlar kompakt filtreli çalışma alanlarına dönüştürüldü.
- Hotfix1.16: Yem ve Tarım listeleri geliştirildi; işlem günlüğü filtrelendi; yedek oluşturma/silme POST akışına taşındı.
- Hotfix1.13a rapor ekranındaki `display` NameError düzeltmesi dahil edildi.
- Solver DEV4.19.3, rasyon hesapları, padok/besi motorları ve mevcut finans-stok hesapları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.13 — Besi Performansı 2.0

- Besi ekranı varsayılan olarak yalnızca devam eden aktif hayvanlarla açılır.
- Devam Eden, Tartım Bekleyen, Düşük, Hedefte, Tamamlanan ve Tümü için sayaçlı sekmeler eklendi.
- Son tartımı 30 günü geçen veya hiç tartılmamış aktif hayvanlar Tartım Bekleyen listesine alınır.
- 13 sütunlu uzun tablo yerine kompakt 8 sütunlu operasyon listesi ve sayfa başına 10 hayvan düzeni getirildi.
- Seçilen hayvan için tartım ekleme, kilo grafiği, GCAA, 30 günlük tahmin, maliyet ve kârlılık aynı çalışma panelinde birleştirildi.
- Mobilde hayvan satırları kart görünümüne dönüşür; filtreler ve çalışma paneli tek sütunda kullanılabilir.
- Satılmış/kesilmiş hayvanlar Tamamlanan Besiler altında kalır; mevcut tartım, maliyet ve finans bağlantıları korunur.
- Uygulama, installer ve GitHub Actions sürüm kaynakları Hotfix1.13 ile eşitlendi.

## 3.9.23 DEV4 Hotfix1.12 — Padok Çalışma Paneli

- Padok Yönetimi, referans görseldeki akışa uygun biçimde üstte seçilebilir kompakt kartlar ve altta tek geniş çalışma paneli olarak yenilendi.
- Arama; padok adı, kodu, notu, hayvan küpesi, takma adı ve ırkında çalışır. Durum filtresi, sıralama ve küçük/büyük/liste görünümleri eklendi.
- Toplam padok, aktif hayvan, canlı ağırlık ve aktif rasyonlardan hesaplanan günlük yem özetleri eklendi.
- Seçili padokta doluluk, canlı ağırlık, aktif rasyon, günlük yem, oluşturma ve son güncelleme bilgileri birlikte gösterilir.
- Hayvan listesine satır bazında kartı aç, düzenle, başka padoka taşı ve hayvan kaydını silmeden padoktan çıkar işlemleri eklendi.
- Rasyon atama, yem tüketimi, notlar ve padok hareket geçmişi aynı panelde ayrı sekmelere alındı.
- Yeni padok, hayvan ekleme ve taşıma işlemleri sayfadan kopmadan açılan pencerelere taşındı; seçili padok işlem sonrasında korunur.
- Padok son güncelleme zamanı için geriye uyumlu veritabanı migrasyonu eklendi. Mevcut veriler, fotoğraflar, rasyonlar ve hareket geçmişi korunur.
- Uygulama, installer ve GitHub Actions sürüm kaynakları Hotfix1.12 ile eşitlendi.

## 3.9.23 DEV4 Hotfix1.9 — Professional Dashboard + Padok 2.0 Mobil + Tek Sürüm Kaynağı

- Login ve alt durum çubuğu artık aynı `APP_VERSION` kaynağını kullanır; 1.8/1.7 etiket ayrışması giderildi.
- Eski varsayılan Dashboard düzeni Professional kokpite otomatik yükseltilir: aktif hayvan, gebe, yaklaşan doğum, aktif padok, toplam canlı ağırlık, ortalama GCAA, düşük performans ve günlük padok yem maliyeti.
- Kullanıcının gerçekten özelleştirdiği Dashboard düzeni korunur; tüm eski kartlar kart seçicisinde kalır.
- Padok 2.0 mobil hayvan satırında tür/cinsiyet/ırk/kilo bilgisi artık kesilmek yerine satıra yayılır.
- Installer/GitHub Actions sürüm referansları Hotfix1.9 ile eşitlendi.

## 3.9.23 DEV4 Hotfix1.7 — Yem Faturası Ödeme Akışı + Finans Rapor Düzeni
- Yem faturasında Ödendi / Ödenmedi işlemi finans tablosundan kaldırılıp Fatura Detayı penceresine taşındı.
- Ödenmiş faturada “Ödenmedi Yap”, bekleyen faturada “Ödendi Yap” işlemi aynı detay penceresinde gösterilir.
- Finans listesindeki işlem adı tüm kayıtlarda sade “Düzenle” olarak standardize edildi.
- Finans tablosunda eksik Vade başlığı düzeltilerek sütun kayması giderildi.
- Finans Raporları masaüstü/tablet/mobil düzeni sabitlendi; kategori tablosu ve grafik taşmaları yatay güvenli alanlara alındı.
- Build, installer ve GitHub Actions sürüm referansları Hotfix1.7 ile eşitlendi.


## 3.9.23 DEV4 Hotfix1.5 Build Fix
- GitHub Actions sürüm doğrulama testi Hotfix1.5 ile eşitlendi.
- Inno Setup OutputBaseFilename Hotfix1.5 olarak güncellendi.
- Workflow içindeki kurulum EXE yolu, SHA-256 dosya adı ve artifact yolu Hotfix1.5 ile eşitlendi.
- Eski Hotfix1.3 beklentisi kullanan regresyon testi Hotfix1.5 olarak düzeltildi.
# V3.9.23 DEV4 Hotfix1.5 — Finans Tablosu Görsel Düzeltme

- Yem faturası detayı artık tablo satırını büyütmiyor; ayrı, kompakt bir fatura önizleme penceresinde açılıyor.
- Finans tablosunda açıklama hücresinin taşması engellendi.
- İşlem sütunu Faturayı Düzenle / Ödemeyi Geri Al / Sil butonlarını bozulmadan gösterecek şekilde genişletildi ve gerektiğinde kontrollü satır kırıyor.
- Fatura önizlemesi masaüstü ve mobilde uyumlu hale getirildi; ESC ve dış alana tıklama ile kapanır.
- Hotfix1.4 ödeme geri alma davranışı korunur.

# V3.9.23 DEV4 Hotfix1.4 — Vadeli Ödeme Geri Alma Hotfix

- Yanlışlıkla **Ödendi** yapılan vadeli kayıtlar için Finans tablosunun **İşlem** sütununa belirgin **↩ Ödemeyi Geri Al** butonu eklendi.
- Geri alma işlemi yalnızca ödeme durumunu `Bekliyor` yapar; **finans giderini, yem faturasını ve stok hareketlerini silmez/değiştirmez**.
- İşlem öncesi açık onay mesajı ve çift tıklama kilidi eklendi.
- Geri alma işlemi denetim kaydına (audit) yazılır.


- Çoklu yem faturalarına gerçek **Faturayı Düzenle** ekranı eklendi.
- Tarih, tedarikçi, fatura no, vade ve tüm yem kalemleri değiştirilebilir.
- Düzenlemede eski stok hareketleri geri alınır; yeni kalemler yazılır ve ağırlıklı ortalama maliyet yeniden hesaplanır.
- Vadeli borcu **Ödendi** yapmadan önce onay istenir ve çift tıklama kilidi uygulanır.
- Yanlış kapatılmış vadeli kayıtlar için **Geri Al** işlemi eklendi.

# V3.9.23 DEV4 Hotfix1.2 — Yem Faturası + Hareketli Ortalama Maliyet

- Yem alımı tek finans gideri + çoklu fatura kalemi olarak kaydediliyor.
- Tedarikçi ve fatura no alanları eklendi.
- Yem kategorisi backend ve arayüzde Gider yönüne kilitlendi.
- Kalemlerden stok girişi ve tarihli alış fiyatı otomatik oluşuyor.
- Yeni `feed_cost_history` ile stok hareketlerinden hareketli ağırlıklı ortalama maliyet tutuluyor.
- Rasyon geçmiş maliyet hesabı bu tarihli stok maliyetini kullanıyor.
- Geri tarihli alım veya fatura silme sonrası ilgili yemin maliyet geçmişi yeniden hesaplanıyor.
- Finans listesinde yem faturası kalemleri açılır detay olarak gösteriliyor.

# V3.9.23 DEV4 Hotfix1.1 — Çoklu Yem Birim Fiyatı ve Rasyon Maliyeti

- Her yem satırına seçilen birime göre zorunlu Birim Fiyat alanı eklendi.
- Kalem toplamı ve tek finans fatura toplamı canlı ve otomatik hesaplanır.
- Sunucu, gönderilen fatura toplamına güvenmeyip toplamı yeniden
  `miktar × birim fiyat` üzerinden oluşturur.
- Torba fiyatı torba kilosuna bölünerek gerçek TL/kg stok fiyatına çevrilir.
- Alışın TL/kg fiyatı `feed_stock_transactions` ve tarihsel `feed_prices`
  kayıtlarına yazılır; rasyon maliyeti alım tarihinden itibaren bu fiyatı kullanır.
- Orijinal TL/torba veya TL/kg değeri `purchase_unit_price` alanında ayrıca
  korunur.

# V3.9.23 DEV4 Hotfix1 — Vadeli Finans ve Çoklu Yem Formu

- `Vadeli` seçimi artık işlem türünden bağımsız olarak Vade Tarihi alanını açar
  ve sunucu vade tarihini zorunlu doğrular.
- Bekleyen vadeli kayıtlar 7 gün önceden Dashboard'daki Yaklaşan Ödemeler
  kartında; vade günü “Bugün ödenecek”, sonrasında “Gecikmiş” olarak görünür.
- `Yem` kategorisi istemci ve sunucu tarafında otomatik `Gider` olarak korunur;
  bu nedenle eski `Gelir + Yem` uyumsuzluğu yeniden oluşamaz.
- `Yem` seçildiğinde çoklu ürün sepeti her zaman açılır. Aynı faturaya sınırsız
  sayıda yem satırı eklenir ve her satır ayrı stok girişine dönüştürülür.
- `243.000` gibi Türkçe binlik ayraçlı tutarlar sunucuda güvenli biçimde
  `243000` olarak okunur.
- Finans tablosunun yatay taşma ve işlem düğmesi erişimi iyileştirildi.

# V3.9.23 DEV4 — Fotoğraf, Vadeli Ödeme ve Çoklu Yem Faturası

- Hayvan ekleme ekranındaki sekiz boş fotoğraf kutusu kaldırıldı. Tek “Fotoğraf Ekle” alanı, fotoğraf seçildikçe yatay küçük önizlemeler oluşturur; ilk görsel profil fotoğrafıdır.
- Vadeli giderlerde vade tarihi zorunlu hale getirildi. Bekleyen, bugün ödenecek ve gecikmiş ödemeler Dashboard ile Finans ekranında gösterilir; “Ödendi” ile kapatılır.
- Tek yem faturasında birden fazla katalog yemi, kg veya torba birimi ve torba kilosuyla girilebilir. Finans kaydı tek kalırken stok/fiyat hareketleri her yem için ayrı oluşur.
- Kalem tutarı bilinmiyorsa toplam fatura tutarı kilogram ağırlığına göre kalemlere dağıtılır; girilmiş kalem toplamları faturayla eşleşmiyorsa kayıt engellenir.
- Tüm oturum açılmış POST formlarında arayüz kilidi ve sunucu tarafında 20 saniyelik atomik mükerrer istek koruması eklendi.
- Eski `feed_finance_links` kayıtları korunur; çoklu faturalar geriye uyumlu `finance_feed_items` tablosunda tutulur.

# V3.9.23 DEV3 — Sağlık, Padok ve Mobil Kart Hotfix

- Aşı/ilaç programı oluşturma ve “Yapıldı” işlemlerinde düğme ilk dokunuşta
  pasifleşir; `Yapılıyor…` durumu görünür ve ikinci gönderim istemci ile sunucu
  tarafında engellenir.
- Aynı sağlık görevi yalnız bir kez tamamlanabilir; padok toplu uygulamalarında
  da atomik görev sahiplenme kullanılır.
- Sağlık planlarına ve tamamlanmış aşı/muayene kayıtlarına `Düzenle` / `Sil`
  eklendi. Plan silme, tamamlanmış geçmişi koruyup bekleyen işleri iptal eder.
- İlaç tedavileri düzenlenirken veya silinirken FEFO stok çıkışları, arınma
  tarihleri, sağlık geçmişi ve bağlı finans gideri tek işlemde uzlaştırılır.
- Padok Yönetimi; doluluk kartları, içindeki hayvanların küpe/ad listesi, hızlı
  taşıma, aktif rasyon, günlük maliyet, padoksuz hayvanlar ve hareket geçmişiyle
  mobil uyumlu olarak yenilendi.
- Dolu padok silme ve kapasiteyi aşan taşıma engellendi; boş padok güvenli biçimde
  arşivlenebilir.
- Mobil hayvan/buzağı profil fotoğrafı 88×88 önizlemeye sınırlandı; fotoğrafın
  bilgi ve maliyet kartlarının üstüne taşması önlendi.

# V3.9.23 DEV2 — Annesiz Buzağı Kartı Hotfix

- Anne küpesi olmayan / bilinmeyen buzağıların detay kartı artık açılır.
- Buzağı liste ve rapor sorguları anne kaydına `LEFT JOIN` ile bağlanır; anne olmadığı için kayıt kaybolmaz.
- Buzağı kartında anne bilgisi yoksa `Girilmemiş` gösterilir.
- Buzağı düzenleme ekranında anne artık opsiyoneldir; sonradan eklenebilir veya boş bırakılabilir.
- Çiftlikte doğdu akışındaki anne zorunluluğu korunur; satın alınan / dış transfer genç hayvanlarda anne bilinmeyebilir.

# V3.9.23 DEV1 — Akıllı Mobil Hayvan Ekle

- Yeni kayıtta değiştirilemeyen `TR` ön eki ve TR sonrası 8–14 rakam doğrulaması.
- Hayvanlar ile buzağılarda ortak, canlı mükerrer küpe sorgusu.
- İlk kayıt sırasında en fazla 8 fotoğraf; ilk görsel profil, tamamı galeri kaydı.
- Destekleyen tarayıcılarda canlı veya fotoğraftan barkod/karekod okuma.
- Tür, ırk, cinsiyet, amaç, geliş kaynağı, doğum/giriş tarihi, kilo, padok,
  karantina, sağlık, soy, maliyet ve not alanlarından oluşan akıllı mobil form.
- Satın alma, çiftlikte doğum ve dış transfer seçimlerine göre koşullu alanlar.
- 10 aydan küçük doğum tarihinde otomatik buzağı kaydı; çiftlikte doğumda anne zorunlu.
- Yetişkin ve buzağı satın alımlarında tek seferlik Finans gider bağlantısı.

## Önceki paket

### V3.9.22 DEV2 — Tarım & Ziraat Tam Düzenle / Sil

- Tarla, üretim sezonu, tarla işlemi, girdi alımı ve hasat kayıtlarına
  düzenle ile güvenli silme/geri alma işlemleri eklendi.
- Dış mahsul satışı düzenlendiğinde satış geliri ve mahsul stok çıkışı aynı
  kaynak bağlantısıyla güncelleniyor.
- Hayvancılığa iç transfer düzenlendiğinde tarım geliri, hayvancılık yem
  gideri, mahsul çıkışı, yem stok girişi, yem fiyatı ve finans bağlantısı tek
  işlem içinde birlikte güncelleniyor.
- Kullanılmış girdi, mahsul veya yem stoğunu eksiye düşürecek miktar azaltma,
  hedef değiştirme ve silme işlemleri engellendi.
- Manuel Tarım Finans kayıtlarına düzenle/sil eklendi; otomatik satırlar yalnız
  kaynak tarla, işlem, alım, satış veya transfer kaydından yönetiliyor.
- DEV4.19.3 solver, hayvan maliyet/zayiat hesapları ve DEV5.1 resmî
  ilaç-hastalık katalogları değiştirilmeden korundu.

# V3.9.22 DEV1 — Tarım & Ziraat Yönetimi

- Özmal ve kiralık tarla kartları; alan, sulama, ada/parsel, mevki ve kira
  bilgilerinin kaydı eklendi.
- Tarla başına yıllık üretim sezonu ve ürün planı oluşturuldu.
- Sürme, ikileme, ekim, gübreleme, ilaçlama, sulama, hasat ve nakliye dahil
  tarla işlemleri; mazot, işçilik, dış hizmet ve diğer maliyetlerle kaydediliyor.
- Tohum, gübre, zirai ilaç ve diğer girdiler için ayrı tarım deposu eklendi.
  Satın alma Tarım Finans'a gider yazılıyor; tarlada kullanım tekrar gider
  üretmeden ilgili sezona maliyet dağıtıyor.
- Hasat kaydı doğrudan gelir yazmak yerine mahsul stoğu ve tahmini stok değeri
  oluşturuyor. Dış satışta gelir ve stok çıkışı birlikte kaydediliyor.
- Hayvancılığa iç transfer tek bağlı işlemle tarım geliri, hayvancılık yem
  gideri, mahsul stok çıkışı, yem stok girişi ve yem fiyat geçmişi oluşturuyor.
- İç transfer kasa/banka hareketi sayılmıyor; bağlı hareketler yalnız tarım
  modülünden birlikte geri alınabiliyor.
- Tarım Finans, hayvancılık bilançosundan ayrıldı; tarla, ürün ve sezon bazlı
  maliyet, verim, TL/kg ve ekonomik sonuç raporları eklendi.
- Mevcut DEV4.19.3 solver ve DEV5.1 resmî ilaç/hastalık katalogları korunmuştur.

# v3.9.21 DEV4 Hotfix2 — Zayiat Aktif Liste ve Arşiv İşlemleri

- Zayiat arşivinde kaydı bulunan yetişkin ve buzağılar tüm aktif listelerden
  ayrıca dışlanarak durum alanından bağımsız güvenlik sağlandı.
- Eski zayiat kaydı olduğu halde `Aktif` kalmış hayvanların durumu uygulama
  başlangıcında son olay ve olay tarihiyle otomatik onarılıyor.
- Ölen / Kayıp Hayvanlar arşivine `Düzenle` ve `Sil / Geri Al` eklendi.
- Düzenleme sonrası donmuş maliyet ve yalnız zayiatın otomatik finans satırları
  güvenli şekilde yeniden oluşturuluyor.
- Sil/Geri Al, alış ve tedavi geçmişini koruyup zayiat finans satırlarını kaldırır
  ve hayvanı aktif sürüye döndürür.
- DEV4.19.3 solver çekirdeği değiştirilmedi.

# v3.9.21 DEV4 Hotfix1 — Mükerrersiz Zayiat Muhasebesi

- Küpeye bağlı `Hayvan Alımı` gideri tespit edilerek ölüm anında ikinci kez
  gider yazılması engellendi.
- Tedavi ve veteriner maliyetleri hayvanın brüt ekonomik kaybına eklendi.
- Finans bağlantılı tedavi/veteriner giderleri tanınarak mükerrer kayıt önlendi.
- Finansa yalnız alış, rasyon/bakım veya tedaviden daha önce aktarılmamış kalan
  tutar `Hayvan Ölümü / Zayiat` gideri olarak ekleniyor.
- Sigorta, et ve kurtarma geliri ayrı gelir kaydıdır; zayiat arşivinde brüt
  kayıptan düşülerek net zarar gösterilir.
- Zayiat arşivine alış, rasyon/bakım, tedavi, diğer, önceden finans, yeni gider,
  kurtarma geliri ve net zayiat sütunları eklendi.
- DEV4.19.3 solver çekirdeği değiştirilmedi.

# v3.9.21 DEV4 — Ortak Hayvan Maliyeti ve Ölüm / Zayiat

- Dişi, erkek ve buzağılar aynı alış + günlük bakım + padok rasyonu maliyet
  motoruna bağlandı.
- Buzağı günlük yem/bakım ve hedef satış tutarı alanları eklendi; ergin hayvana
  geçişte maliyet ve padok geçmişi korunuyor.
- Ölüm, kayıp, zorunlu imha ve işletmeden çıkış işlemleri eklendi.
- Çıkış tarihinde toplam maliyet donduruluyor; kayıt pasife alınarak geçmişi
  değişmez hale geliyor.
- Net zayiat finansa `Zarar` türünde, nakit dışı kayıt olarak aktarılıyor; varsa
  sigorta veya kurtarma bedeli ayrıca gelir yazılıyor.
- `Ölen / Kayıp Hayvanlar` arşivi ve finans zayiat özeti eklendi.
- DEV4.19.3 solver çekirdeği değiştirilmedi.

# v3.9.21 DEV3 — Dişi Hayvan Maliyet ve Satış Kârlılığı

- İlaç kataloğu: ürün, etkin madde, firma, terapötik grup, uygulama yolu,
  farmasötik şekil, resmî kaynak ve et/süt arınma süresi.
- Parti/lot, SKT, miktar, birim, maliyet ve tedarikçi bazında ilaç stoğu.
- Hayvan/buzağı tedavisi; doz, uygulama sıklığı, teşhis, veteriner, reçete,
  toplam tüketim ve otomatik et/süt güvenli çıkış tarihleri.
- Stok yetersizliği ve tedavi tarihinden önce dolan parti için kayıt engeli.
- İlaç alışı ve tedavide kullanılan ürün maliyeti için finans bağlantısı.
- Kurulum öncesi otomatik DB yedeği, güvenli süreç kapatma ve kurulum sonrası
  yeniden başlatma akışı.
- DEV4.19.3 solver çekirdeği dondurulmuş biçimde korundu.

# v3.9.20 Solver DEV4.19.3 — Canlı Hedef Kartı Hotfix

- Solverın yaklaşık `1,39 kg` hesapladığı GCAA değerinin rasyon detayında canlı
  JavaScript tarafından ham NEm/NEg ile `0,67 kg` gösterilmesi düzeltildi.
- Rasyon satırlarının canlı hesap veri alanları, sunucuyla aynı normalize edilmiş
  ME/NEm/NEg/eNDF/HP/NDF değerlerinden üretiliyor.
- Miktar değişikliği simülasyonları da aynı besin katmanına bağlandı.

# v3.9.20 Solver DEV4.19.2 — Gerçek Veritabanı Enerji Hotfix

- Kullanıcının gerçek yedeğindeki Mısır Koçanı Silajı kaydında ME `2,65` iken
  NEm/NEg/TDN/eNDF alanlarının sıfır olması nedeniyle yemin enerji kapasitesinin
  yok sayıldığı belirlendi.
- ME mevcutsa eksik NEm ve NEg, NRC tipi net enerji polinomlarıyla; eksik TDN,
  ME dönüşümüyle; eksik silaj eNDF'si muhafazakâr `%70` çalışma oranıyla tamamlanıyor.
- Beş yemli gerçek saha senaryosu GCAA `1,387`, kaba yem `%51,3`; sekiz yemli
  gerçek senaryo GCAA `1,396`, kaba yem `%49,0` ile çözüldü.

# v3.9.20 Solver DEV4.19.1 — 260 kg Saha Hotfix

- 260 kg / 10 ay / 1,40 kg GCAA ve sekiz seçili yem senaryosunda optimizerın
  kaba/kesif koridoru dışındaki adayı seçip en sonda reddetmesi düzeltildi.
- Faz koridorunun 5 puandan fazla dışı, aday sıralamasının sert güvenlik
  vektörüne taşındı; solver güvenli kombinasyonu arama sırasında seçiyor.
- Arpa ezmesi, arpa samanı, buğday kepeği, mısır koçanı silajı, soya küspesi,
  Sunar 15.26, Sunar Buzağı Büyütme ve yonca saha seti regresyona alındı.

# v3.9.20 Solver DEV4.19 — Son Kilitleme

- Seçilen tüm normal yemler uygulanabilir saha minimumuyla çözümde tutuluyor;
  enerji/protein açığı aynı yemlerin miktarları değiştirilerek yeniden aranıyor.
- Faz kaba/kesif koridorunun 5 puandan fazla aşılması ve faz toplam tahıl KM
  üst sınırının aşılması artık kesin kayıt engeli.
- Buğday/tahıl KM oranında `%30–32` yalnız küçük “sınırlı” sapma; `%32–40`
  çözümsüz, `%40` üstü güvensiz kabul ediliyor.
- Sunar 15.26 `0–10 kg`, Kardelen 19.27 `6–12 kg` ürün sınırları korunuyor.
- Etikette bulunmayan Sunar 15.26 nişastası, ürünün `%9,27` ham selülozu ve
  yan ürün ağırlıklı hammaddeleriyle uyumlu açık referans tahmin olarak `%30`
  tutuluyor; laboratuvar değeri gibi sunulmuyor.
- 250/350/500 kg besi ve 25 litre süt saha senaryoları regresyon testine alındı.

# v3.9.20 Solver DEV4.18 — Gerçek Sunar Etiketleri

- 20/08/2026 tarihli `Sunar 15.26 Geliştirme Besi Yemi` etiketi işlendi: ürün
  bazında `%15 HP`, `%3,00 yağ`, `%9,27 ham selüloz`, `%7,73 kül` ve `%0,27
  sodyum`.
- Besi yemi enerji sınıfı ürün koduna uygun `2600 kcal/kg` olarak düzeltildi;
  `%88,35` referans KM ile `2,943 ME`, `1,984 NEm` ve `1,333 NEg Mcal/kg KM`
  kullanılıyor. Güncel etikette ME ayrı analitik satır olmadığı kaynak notunda
  açıkça belirtiliyor.
- 19/08/2026 tarihli `Sunar Kardelen 19.27 Süt Yemi` etiketi işlendi: ürün
  bazında `%19 HP`, `%3,50 yağ`, `%9,07 ham selüloz`, `%6,89 kül` ve `%0,33
  sodyum`.
- Kardelen'in `6–12 kg/baş/gün` etiket sınırı süt solverına bağlandı; süt
  solverındaki etiket alt/üst sınırını atlayan eski yol düzeltildi.
- Eski Çukoyem/Sığır Besi ve Sığır Süt adları, yem kimliği ile rasyon, fiyat ve
  stok bağlantıları korunarak yeni Sunar adlarına geçiriliyor.
- KM, NDF, nişasta, Ca/P ve ileri rumen alanları gerçek analiz olmadığı için
  referans tahmin olarak kalıyor; vitamin/iz element kartları belgeye eklendi
  fakat eksik mikro-mineral modeliyle otomatik premiks optimizasyonuna katılmadı.
- 40 otomatik test başarıyla tamamlandı.

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
## v3.9.21 DEV2 — İlaç & Veteriner saha ekranı
- 1366 px ekranda taşan üçlü form düzeni kaldırıldı; katalog, stok ve tedavi işlemleri sağ çekmecelere alındı.
- Ana ekrana katalog, stoksuz ürün, 60 gün içinde SKT ve aktif arınma özetleri eklendi.
- İlaç kataloğuna ürün/etkin madde/firma araması ve terapötik grup filtresi eklendi.
- Tedavi hayvan seçimine küpe/isim araması eklendi.
- Bakanlığın resmî ruhsatlı veteriner ilaçları sorgusuna doğrudan bağlantı ve kaynak doğrulama uyarısı eklendi.
- Tedavide stok tüketimi tek parti zorunluluğundan çıkarıldı; SKT'si en yakın uygun partiden başlayarak FEFO yöntemiyle birden çok partiye bölünebilir.
- Solver DEV4.19.3 dondurulmuş haliyle korundu; rasyon matematiğine dokunulmadı.
# v3.9.21 DEV3 — Dişi Hayvan Maliyet ve Satış Kârlılığı
- Dişi hayvanlarda alış bedeli, tarihsel padok/rasyon gideri ve günlük bakım aynı maliyet motorunda birleştirildi.
- Dişi hayvan listesine alış, birikmiş rasyon+bakım ve anlık toplam maliyet sütunları eklendi.
- Hayvan kartındaki canlı maliyet paneli ve satış formu dişi hayvanlar için de açıldı.
- Satış onaylandığında gelir ilgili küpeye Finans > Hayvan Satışı olarak kaydedilir; hayvan Satılanlar arşivine taşınır.
- Satılanlar arşivinde alış, işletme gideri, toplam maliyet, satış geliri ve net kâr/zarar gösterilir.
- Yeni hayvan alışında “Finansa gider olarak kaydet” onayı eklendi; düzenlemede bağlı alış finans kaydı oluşturulabilir veya güncellenebilir.
- Maliyet satış tarihinde donar; geçmiş padok/rasyon fiyat revizyonları tarihsel olarak korunur.
- Solver DEV4.19.3 değiştirilmedi.
# V3.9.21 DEV5.1

- Hotfix2: Bakanlık HBS tablosundaki sığır/buzağı/dana/manda hedefli 1.241 benzersiz ruhsatlı ürün başlangıç kataloğuna aktarıldı.
- Hotfix2: Ruhsatlı ürün ayrıntı sayfası, ATCvet, hedef tür, etken madde, firma ve Bakanlık ürün özeti bağlantısı eklendi.
- Hotfix2: Resmî tabloda bulunmayan arınma süreleri tahmin edilmedi; ürün özetinden doğrulanana kadar tedavi kullanımı kilitli tutuldu.
- Hotfix1: GitHub Actions sürüm ve kurulum dosyası doğrulamaları DEV5.1 adına güncellendi.
- Hotfix1: Katalogdaki 46/47 hastalığın tamamında boş ayrıntı alanları güvenli operasyonel içerikle dolduruldu; yer tutucu metin kaldırıldı.
- İlaç ve veteriner ekranı beş sekmeye ayrıldı; uzun katalogların aynı anda açılması kaldırıldı.
- Hastalık sayısı 47'ye çıkarıldı ve canlı arama eklendi.
- Hastalık adları tıklanabilir yapıldı; tanım, etken, bulaşma, belirtiler, ayırıcı tanı, ilk yapılacaklar, veteriner yaklaşımı, korunma ve bildirim kartları eklendi.
- Şap, bruselloz, şarbon, mastitis, hipokalsemi, timpani, buzağı ishali ve BRD için genişletilmiş güvenli bilgi kartları eklendi.
- Hastalık detayından seçili teşhisle tedavi kayıt çekmecesi açılabilir.

# V3.9.21 DEV5

- Windows kullanıcı oturumunda ÇiftlikPro arka planda otomatik başlatılır; masaüstü kısayolu tarayıcıyı açmaya devam eder.
- Bakanlık ruhsat sorgusuna bağlı, ticari marka olmayan 18 etken maddelik başlangıç rehberi eklendi.
- Yaygın ve resmî bildirim önceliği bulunan 23 hastalık için operasyonel kayıt kataloğu eklendi.
- Resmî kaynaktan doğrulanmayan et/süt arınma bilgisi “Doğrulanmadı” gösterilir ve tedavi kaydı engellenir.
- Ölü, kayıp veya pasif hayvana yeni tedavi kaydı açılması hem listede hem sunucu tarafında engellendi.
- Solver DEV4.19.3 donduruldu; matematik ve kısıt katmanına dokunulmadı.

## V3.9.23 DEV4 Hotfix1.10 — DashboardPro Sağlık Akışı
- Dashboard Gebelik / Aşı Alarmı artık doğrudan işlem yapılabilir: **Aşıyı Yap**, **Hayvanı Aç**, **1 Gün Ertele**.
- Dashboard'un kompakt kartlarında işlem butonlarının yanlışlıkla gizlenmesine neden olan CSS düzeltildi.
- Sağlık ekranına otomatik 7./8. ay gebelik aşı görevleri eklendi; ilgili hayvanı manuel aramadan tamamlanabilir veya ertelenebilir.
- Aşı tamamlandığında gerçek sağlık geçmişine işlenir; mükerrer kayıt koruması devam eder.
- Ertelenen gebelik aşı tarihi kalıcı olarak saklanır ve Dashboard/Sağlık ekranında yeni tarihle izlenir.
- Yaklaşan ödeme kartındaki mevcut hızlı işlem butonları kompakt Dashboard'da görünür hale getirildi.
- Tailscale/telefon gibi istemcilerin bağlantıyı kapatmasıyla oluşan WinError 10053/10054, ConnectionReset/BrokenPipe durumları sunucuyu kirleten traceback yerine sessiz karşılanır; gerçek sunucu hataları görünmeye devam eder.
- Login/footer/yedek manifesti tek APP_VERSION kaynağını kullanmaya devam eder.

## 3.9.23 DEV4 Hotfix1.22e
- Mobil hedef kartları modern renkli 2x2 düzene geçirildi.
- Mobil Çözüm Durumu varsayılan görünümde sadeleştirildi; ayrıntılar açılır yapıda korundu.
- Mobil + Yem Ekle / Kaydet çubuğunun son yem satırlarını kapatmaması için güvenli alt boşluk artırıldı.
- 1.22d masaüstü miktar alanları ve yeni çöp kutusu görünümü korundu.

## 3.9.23 DEV4 Hotfix1.22f
- MISIR PULU (FLAKED) için katalog nişasta ortalaması %67,5 olarak sabitlendi; kesif yem sınıfı düzeltildi.
- Mevcut kullanıcı veritabanlarında kalmış eski %75/%90 nişasta kayıtları için kalıcı migrasyon eklendi.
- Mobil yem satırlarının sol simgeleri tıklama beklemeden ilk HTML yüklemesinde görünür hale getirildi.
- Solver DEV4.19.6 ve bilimsel hedef aralıkları değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22g
- Mobil yem kartında ikon/ad/KM etiketlerinin aynı yatay satırda sıkışması giderildi.
- Kilit düğmesi ikon üzerinde küçük rozete taşındı; yem adı için daha geniş alan açıldı.
- Mobil hedef kartları masaüstü görsel dilinde ikonlu, renkli, durum rozetli 2×2 düzene geçirildi.
- Solver DEV4.19.6 ve Hotfix1.22f katalog migrasyonu aynen korundu.

## 3.9.23 DEV4 Hotfix1.22h
- iOS/Safari'de eski satır pseudo-simgesi ile gerçek yem simgesinin üst üste görünmesi giderildi.
- Mobil satır açılışında eski `data-feed-icon` verisi ve olası yinelenen simgeler temizlenir.
- Masaüstü Rasyon Çalışma Masası açılırken eski hedef görünümünün bir an görünüp yeni kartlara dönüşmesi giderildi; kartlar hazır olduğunda tek seferde gösterilir.
- Hotfix1.22g hedef kartları, mobil düzen ve Solver DEV4.19.6 değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22i
- Mobil yem satırında kalan eski `td::after` logo katmanı ve sıra numarası rozeti kaldırıldı.
- Her satırda tek gerçek yem logosu bırakıldı; miktar kilidi küçük ve ayrı bir köşe rozeti olarak korundu.
- Hotfix1.22h masaüstü hedef kartı açılış düzeltmesi ve Solver DEV4.19.6 değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22j
- Mobil Dashboard Aylık Net değeri büyük tutarlarda kart içinde kalacak şekilde sıkıştırıldı.
- Kritik Stoklar paneli, yalnız gerçekten stok girişi bulunan yemlerin kalan miktarlarını gösterir.
- Mobil Son Hareketler paneli üç satırla sınırlandı; masaüstü görünümü ve tam işlem günlüğü korunur.
- Rasyon Solver DEV4.19.6 ve bilimsel hedefler değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22k
- Ana sayfadaki Modern ve Klasik Dashboard'ların aynı anda alt alta oluşturulması kaldırıldı.
- Kullanıcı bazında kalıcı `Modern / Klasik` görünüm seçimi eklendi; varsayılan görünüm Modern'dir.
- Kart düzenleme bağlantısı Klasik görünümü güvenli biçimde açar; mevcut kişiselleştirilmiş kart dizilimi korunur.
- Rasyon Solver DEV4.19.6 ve bilimsel hedefler değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22l
- Modern/Klasik Dashboard tercihi genel çift-gönderim korumasından ayrıldı.
- Mobil Safari aynı isteği tekrar gönderse bile tercih kaydedilir ve mükerrer kayıt uyarısı gösterilmez.
- Rasyon Solver DEV4.19.6 ve bilimsel hedefler değiştirilmedi.

## 3.9.23 DEV4 Hotfix1.22m
- Aktif padok rasyonları günlük yem tüketimiyle stok hareketlerine bağlandı.
- Günlük tüketim `rasyon kg/baş/gün × aktif padok mevcudu` olarak hesaplanır.
- Padok/yem/gün tekilliği sayesinde aynı gün mükerrer düşüm engellenir; aynı gün değişen hayvan sayısı veya miktar mevcut hareket üzerinde uzlaştırılır.
- Geçmiş günlere otomatik tüketim yazılmaz ve yalnız kaydedilmiş, padoka atanmamış reçeteler stok düşürmez.
- Rasyon Solver DEV4.19.6 ve bilimsel hedefler değiştirilmedi.


## 3.9.23 DEV4 Hotfix1.22o
- Modern/Klasik Dashboard seçiminin mobilde yeniden Moderne dönmesine yol açan form gönderim hatası düzeltildi.
- Padok yönetimine **Toplu Rasyon Ata** eklendi; tek rasyon birden fazla aktif padoka tek işlemde atanabilir.
- Padoklara ana rasyon dışında **Ek Yem / Takviye** ekleme, silme, günlük kg/baş ve maliyet takibi eklendi.
- Ek yemler ana rasyonla birlikte stoktan günlük ve idempotent düşer; aynı yem iki kaynakta varsa tek tüketim hareketinde birleşir.
- Kendi doğan buzağılar için **İç Üretim Maliyeti** eklendi: süt, yem, bakım ve diğer kalemler küpe bazında birikir; yem kalemleri isteğe bağlı stoktan düşer.
- İç üretim maliyeti Finans ekranında nakit dışı ayrı toplam olarak gösterilir ve nakit gideri ikinci kez azaltmaz.
- Buzağı 10 aylık olduğunda yetişkin karta aktarılırken iç üretim maliyeti de devredilir.
- Rasyon solver çekirdeği DEV4.19.6 değiştirilmedi.

## Hotfix1.22aj — Sağlık Ajandası
- Günlere göre ajanda varsayılan; Kartlar görünümü seçilebilir ve tarayıcıda hatırlanır.
- Arama ve filtreler boş gün gruplarını gizler; mevcut aşı/tedavi işlemleri korunur.
- Mobilde satırlar alt alta; ikincil işlemler üç nokta menüsündedir.

## Hotfix1.22bd
- Temiz DB ilk katalog yüklemesi artık üretici etiket (`label_*`) alanlarını da taşır.
- 1.22bb ile oluşmuş Sunar 21.28 sıfır etiket alanları güvenli migrasyonla onarılır.
- GitHub regresyon testi için sürüm/Setup beklentileri 1.22bd ile eşitlendi.
