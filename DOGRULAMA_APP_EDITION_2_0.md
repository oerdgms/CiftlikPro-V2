# App Edition 2.0.5 doğrulama

## Sonuç

- 339 Python regresyon testi: başarılı.
- Son arayüz düzenlemesinden sonra 20 App Edition testi ayrıca başarılı.
- Gönderilen AppEdition 1.0 kaynağıyla 219 mevcut fonksiyon/sınıfın AST karşılaştırması: tamamı aynı. Bu kontrol solver, finans, sağlık, üreme, stok ve mevcut kayıt işleyicilerini kapsar.
- Python derleme ve JavaScript sözdizimi kontrolleri: başarılı.

## Mobil tarayıcı kontrolü

2.0.5 giriş düğmesi 320, 390, 412, 820 ve 1366 px genişliklerde şifre kutusunun sınırları ve merkez hizası açısından doğrulandı; Göster/Gizle iki yönde çalıştı. Hayvan işlem satırı dört mobil genişlikte Ayrıntı, Kart ve Kompakt görünümleriyle toplam 12 durumda doğrulandı: üç düğme tek satırda, yazıları kırılmadan ve 44 px dokunma yüksekliğiyle kaldı. Silme formu korunmuştur.

Chromium üzerinde 320, 390, 412 ve 820 CSS piksel genişliğinde 24 ekran/adres kontrol edildi; toplam 96 kontrol başarılı. Finans ve hayvan raporları, maliyet detayları, arşivler ve buzağı kartı da ana matrise eklendi. Canlı sayfalarda görünen kart/form alanlarının yatay sınırları, global yatay kaydırma konumu, HTML/body taşma kilidi, başlangıçta kapalı olması gereken pencereler ve viewport ölçeği denetlendi. JavaScript hatası gözlenmedi.

Her mobil sayfada viewport etiketi `maximum-scale=1` ve `user-scalable=no` değerleriyle tekil olarak doğrulandı; programlı yatay kaydırma denemesinden sonra global `scrollX` değeri 0 kaldı. Finans raporundaki geniş kategori tablosunun sayfayı taşırmadan kendi kutusunda yatay kaydırılabildiği ayrıca gerçek tarayıcı etkileşimiyle kontrol edildi.

Kullanıcının ilettiği iPhone ekranlarındaki dört sorun için ayrıca 320, 390 ve 412 CSS piksel genişliğinde 30 hedef kontrol yapıldı. Yetişkin/Buzağı seçimi, gerçek `record_type=Buzağı` geçişi, son kaydetme şeridinin alt menünün üstünde kalması, fotoğraf kutusu sınırları, hayvan kartında `₺122.906,02` örnek tutarının kart içinde kalması, Fotoğraf Ekle paneli ve JavaScript hatasız çalışma başarılıdır.

Finans kartındaki üç nokta satırı için aynı üç telefon genişliğinde 33 ek hedef kontrol yapıldı. Kapalı kart yüksekliği, eski işlem bandının tamamen gizlenmesi, üç noktanın tutar alanında kalması, başlık/tutar çakışmaması, Düzenle/Sil satırının boşluksuz açılması, yeniden kapanma, yatay taşma ve JavaScript hataları denetlendi; kontrollerin tamamı başarılıdır.

Hayvan kartı düzenlemesi için 320, 390 ve 412 CSS piksel genişliğinde 54 ek hedef kontrol yapıldı. Buzağı kimlik–fotoğraf satırı, maliyet/finans kutularının tam genişliği, boşluk sınırı, uzun tutarların kutuda kalması, fotoğraf/tartım kartlarının sıralanması, form alanlarının taşmaması ve yetişkin kartının maliyet/fotoğraf alanları doğrulandı; kontrollerin tamamı başarılıdır.

Ana sayfa, İşler, Modüller, hayvan listesi/kartı/ekleme, padok, finans/finans düzenleme, sağlık, rasyon listesi/çalışma masası, yem kataloğu, üreme, süt, tarım, ayarlar, rapor ve arşiv ekranları kapsamdaydı.

## Gerçek arayüz işlemleri

İşlemler yalnız test için oluşturulan geçici veritabanında yapıldı:

1. Hızlı işlem menüsü açılıp kapatıldı.
2. 11 ana modül ve diğer sistem bağlantıları kontrol edildi.
3. Hayvan araması mevcut canlı arama mekanizmasıyla denendi; bir sonuç döndü, kart görünümü ve düzenle/sil formları korundu.
4. İki hayvan seçilip gerçek toplu taşıma formu gönderildi.
5. Yeni finans kaydı gerçek Enterprise formuyla kaydedildi; Türkçe tutar normalizasyonu ve listede görünmesi doğrulandı.
6. İki dozlu sağlık planı gerçek Enterprise formuyla oluşturuldu.
7. Rasyon aramasıyla seçilen reçete aynı Enterprise çalışma masasında açıldı.
8. Rapor menüsünden mevcut hayvan raporu formuna geçildi.
9. Finans raporunda global sayfa sabit tutulurken geniş tablonun kendi alanında yatay kaydırılabildiği doğrulandı.
10. Masaüstünde Dashboard, finans, padok, sağlık, rasyon ve çalışma masası açıldı; mevcut üst menü/form görünümü korundu, mobil gezinme ve kart dönüştürme etkinleşmedi.

## Toplu taşıma ve ortak veri testleri

- Yetişkin ve buzağı hareketi birlikte sayılara, padok adına ve geçmişe yazılır.
- Kapasite yetersizliği tüm seçimi geri alır.
- Geçersiz/inaktif hayvan, aktarılmış buzağı ve inaktif hedef kabul edilmez.
- Aynı taşıma tekrarı mükerrer geçmiş oluşturmaz.
- Giriş oturumu olmayan gönderim kabul edilmez.
- Ana sayfa sayıları ve sağlık/vade görevleri aynı Enterprise yardımcılarından alınır.
- Manifest, simgeler, giriş görseli, CSS, JavaScript ve çevrimdışı bağlantı ekranı HTTP üzerinden doğrulandı.

## Kaynak pakette giderilen doğrulama sorunları

Eski testlerin 1.22ci sürümünü, önceki MobileAPI etiketlerini ve tek HTML sınıfı yazımını arayan beklentileri paketle uyumlu hale getirildi. İş kuralı doğrulamaları korunur; yeni çekirdek karşılaştırması 219 mevcut tanımı ayrıca korur. Yem filtresi kontrolü mevcut ortak stok durumu kuralına güncellendi.

Akıllı hayvan formunun başlangıçta kullandığı mevcut gebelik arayüz fonksiyonu daha erken tanımlanır. Fonksiyonun birebir aynı metni kullanılır; gebelik veya kayıt iş kuralları değiştirilmez.

## Çalıştırılmayan ortamlar

Gerçek iPhone/Android cihazları ve Windows EXE kurulumu bu Linux çalışma ortamında çalıştırılmadı. Tarayıcı kontrolleri Chromium ve mobil boyutlar üzerinden yapıldı. Windows Actions akışında hem kaynak sunucu hem paketlenmiş EXE için mobil kaynakların yüklenmesi kontrolü eklendi.
