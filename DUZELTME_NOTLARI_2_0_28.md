# App Edition 2.0.28 — Senkronizasyon

## Erişim ve plan oluşturma

Modüller → Senkronizasyon. Üreme Merkezi, Sağlık & Aşı ve aktif dişi hayvanın Üreme Bilgileri bölümünde de giriş bulunur. Modüller ızgarası 15 eşit kutucuk içerir.

1. Senkronizasyon Tanımla düğmesini açın; takvimi, başlangıç tarihini ve saatini seçin.
2. Hayvan grubunu seçin; küpe / ad / padok aramasıyla hayvanları tek tek veya görünenleri topluca işaretleyin. En çok 300 hayvan seçilebilir.
3. Uygulama takvimini inceleyin. Adımlar başlangıçtan itibaren gün + ek saat ile tanımlanır; tarih ve saat önizlemesi gösterilir. Adımlar artan zaman sırasıyla olmalıdır.
4. Ürün, doz, birim ve yolu veteriner planından girin. Planı bu bilgiler tamamlanmadan saklamak mümkündür; hormon / ilaç adımı uygulanırken bu bilgiler zorunludur.
5. Veteriner, notlar ve istenirse hayvan başına ücretleri girin; uygunluk ve takvimin veteriner planıyla kontrol edildiğini işaretleyip kaydedin.

Doğum sonrası gün sayısı kayıtlı doğumdan hesaplanır. Düve grubu mevcut manuel Düve durumunu kullanır; doğum kaydı bulunmaması tek başına Düve sayılmaz. Boş inek filtresine doğum sonrası inekler de dahildir. Gebe, sonucu beklenen, pasif, kayıp ve başka aktif senkronizasyonu olan hayvanlar yeni plana eklenemez. Doğum sonrası gün hesabı klinik uygunluk kararı değildir; işletmenin kayıtlı bekleme süresi formda gösterilir.

## Takvimler

- Ovsynch 56 ve Ovsynch 48.
- Double Ovsynch; Presynch 12 / Ovsynch 56; Presynch 14 / Ovsynch 56; G6G / Ovsynch 56.
- Düve için 5 gün CIDR-Synch: başlangıç GnRH + iki PGF veya başlangıç GnRH olmadan tek PGF seçenekleri.
- Veterinerin özel planı: adımlar ve zamanları elle tanımlanır.

İnek şablonlarında Düve olarak işaretli hayvanlar; düve şablonlarında diğer dişiler seçime sunulmaz. Özel plan tüm uygun dişilerle kullanılabilir. Şablonlar ilaç reçetesi veya otomatik uygunluk önerisi değildir. Hormon / ilaç dozları ve ürünleri boş başlar.

Zamanlama kaynakları, 22/10/2026 tarihinde DCRC'nin resmî protokol sayfasından kontrol edilmiştir. Yayımlanan inek ve düve belgeleri 2018 güncellemesidir. Takvim işletme veterinerinin planına göre düzenlenebilir; kaydedilen uygulama takvimi planın kendi kopyasıdır.

- https://www.dcrcouncil.org/protocols/
- https://www.dcrcouncil.org/wp-content/uploads/2019/04/Dairy-Cow-Protocol-Sheet-Updated-2018.pdf
- https://www.dcrcouncil.org/wp-content/uploads/2018/12/Dairy-Heifer-Protocol-Sheet-Updated-2018.pdf

## Uygulama ve görevler

Plan ayrıntısında hayvanı açıp ilgili adımda Uygulamayı kaydet seçeneğini kullanın. Gerçekleşen saat ve uygulayan kullanıcı saklanır; sağlık geçmişine bir kayıt eklenir. Gelecekteki uygulama yapılmış sayılamaz. Önceki bekleyen adımlar atlanarak sonraki adım tamamlanamaz. Aynı kaydı tekrar göndermek ikinci sağlık kaydı oluşturmaz.

Bekleyen bir adımın Düzenle alanı yalnız o hayvanın o adımını değiştirir; neden / veteriner notu işlem geçmişine yazılır. Başka ekranda değişen uygulama eski formdan ezilemez. Gecikme sonraki adımları otomatik kaydırmaz. Saatler Türkiye saatidir.

Tohumlama adımı ayrıca onaylandığında gerçek tohumlama kaydı açar; aynı gün zaten varsa onu bağlar. Mevcut uygulamadaki üç deneme sınırı korunur; sonuç Bekleniyor olur, gebelik pozitif sayılmaz.

Her hayvan / adım ana sayfa, Görevler, Bildirimler ve ortak görev çıktılarında ayrı görünür; saat listede yer alır. Bağlantı ilgili hayvana ve adıma gider. Sonradan gebelik veya pasife alma bilgisi girilen hayvana bekleyen hormon görevi gösterilmez; uygulama kaydı da engellenir. Plan ayrıntısında kontrol nedeni görünür. Form açıkken durum değişse bile sunucu yeniden denetler.

## Ücretler, düzenleme ve iptal

Ücretler hayvan başınadır. Planı kaydetmek finans gideri oluşturmaz. Plan ayrıntısındaki Gideri finansa işle işlemi seçilen tarihte her plan hayvanına bir Nakit / Gider kaydı açar; iptal edilmiş hayvanlar bu işlemden çıkarılır. Tekrar gönderim aynı gideri çoğaltmaz; kayıt hayvanın maliyetine mevcut finans sistemi üzerinden katılır. Bu işlem ilaç stok hareketi oluşturmaz.

Henüz uygulama veya gider içermeyen aktif plan baştan düzenlenebilir. Başlayan planda bekleyen adımlar hayvan bazında düzenlenir. Bir hayvanın veya tüm planın kalan adımları neden girilerek iptal edilebilir; gerçekleşmiş sağlık / finans kayıtları korunur. Hiç uygulama veya finans kaydı içermeyen planlar silinebilir.

Rasyon, stok tüketimi, mevcut doğum kayıtları ve manuel laktasyon sınıflandırması değiştirilmedi.
