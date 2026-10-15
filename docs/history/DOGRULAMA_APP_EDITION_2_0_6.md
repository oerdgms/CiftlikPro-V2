# App Edition 2.0.6 doğrulama

## Sonuç

- 342 Python regresyon testi: başarılı.
- Son arayüz düzenlemesinden sonra 23 App Edition testi ayrıca başarılı.
- Gönderilen AppEdition 1.0 kaynağıyla 219 mevcut fonksiyon/sınıfın AST karşılaştırması: tamamı aynı. Bu kontrol solver, finans, sağlık, üreme, stok ve mevcut kayıt işleyicilerini kapsar.
- Python derleme ve JavaScript sözdizimi kontrolleri: başarılı.

## Mobil tarayıcı kontrolü

Önceki giriş/işlem satırı düzeltmeleri 2.0.6 üzerinde yeniden doğrulandı: giriş düğmesi 320, 390, 412, 820 ve 1366 px genişliklerde şifre kutusunun sınırları ve merkez hizası açısından kontrol edildi; Göster/Gizle iki yönde çalıştı. Hayvan işlem satırı dört mobil genişlikte Ayrıntı, Kart ve Kompakt görünümleriyle toplam 12 durumda doğrulandı: üç düğme tek satırda, yazıları kırılmadan ve 44 px dokunma yüksekliğiyle kaldı. Silme formu korunmuştur.

Chromium üzerinde 320, 390, 412 ve 820 CSS piksel genişliğinde 25 ekran/adres kontrol edildi; toplam 100 kontrol başarılı. Bildirimler, finans ve hayvan raporları, maliyet detayları, arşivler ve buzağı kartı da ana matrise eklendi. Canlı sayfalarda görünen kart/form alanlarının yatay sınırları, global yatay kaydırma konumu, HTML/body taşma kilidi, başlangıçta kapalı olması gereken pencereler ve viewport ölçeği denetlendi. JavaScript hatası gözlenmedi.

Toplu düzeltme akışları ayrıca 320, 390, 412, 820, 1024 ve 1366 px genişliklerde denendi. Gerçek sağlık kaydı bulunan buzağı kartı, Süt/Yem/Bakım form geçişleri, çakışmayan tarih/tür alanları, fotoğraf yükleme alanlarının sınırları, Geçmiş ve Satış/Zayiat sekmelerinin ayrılığı, eski satış hash bağlantısı, mobil işletme formu ve masaüstü bildirim bağlantısı başarılıdır. Sentetik kısa çift dokunma/dblclick olayları engellendi; kök dokunma davranışı pan-x/pan-y, body dikey taşma davranışı visible olarak doğrulandı.

Safari'nin gerçek momentum ve zoom davranışı burada çalıştırılmadı. Sentetik dokunma ve CSS kontrolleri gerçek iPhone teyidinin yerine geçmez.

## İletim performansı

Gzip kabul eden doğrudan HTTP istemcisiyle, test veritabanında sayfa gövdesi baytları ölçüldü. Bu ölçüm toplam açılış süresi veya yüzde hızlanma değildir; aktarılan veri miktarıdır.

| Sayfa | Düz HTML | Gzip HTML | Azalma |
|---|---:|---:|---:|
| Ana sayfa | 364.020 B | 73.186 B | %79,9 |
| Hayvan listesi | 410.502 B | 78.039 B | %81,0 |
| Hayvan kartı | 355.586 B | 72.448 B | %79,6 |
| Buzağı kartı | 363.374 B | 74.588 B | %79,5 |
| Finans | 396.236 B | 80.959 B | %79,6 |
| Rasyon çalışma masası | 555.292 B | 104.024 B | %81,3 |

CSS 73.008 B yerine 12.032 B, JavaScript 36.367 B yerine 10.812 B aktarılır. Sürümlü CSS/JS/giriş görseli uzun süreli önbellek kullanır. Testler açılan gzip HTML'nin düz yanıttaki metinle aynı olduğunu, `gzip;q=0` istemcisinin sıkıştırılmadığını ve sayfaların no-store olduğunu doğrular. Önceki ve yeni tarayıcı zamanları çalışma ortamı koşulları farklı olduğu için kesin hızlanma oranı olarak kullanılmaz. HTML çözümleme yükü ile solver algoritması bu yamada korunmuştur.

42 geçmiş sürüm belgesi arşiv klasörüne taşındı. Kullanılmayan mobil eski Dashboard genişletme kodu ve mükerrer build ataması kaldırıldı. İşlevsel kaynaklar, eski API'ler ve regresyon testleri silinmedi.

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
