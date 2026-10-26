# ÇiftlikPro Enterprise — App Edition 2.0.37

24/10/2026 · Temel: 2.0.36 tam kaynak paketi.

## Toplu Yapıldı

Sağlık Yönetimi’nde aynı programın tarihi gelen aynı doz / uygulama grubunda **Toplu Yapıldı** kartı görünür. Örneğin 67 hayvana ilk doz planlandıysa, bu kart 67 hayvanı bir arada açar. Ana liste 25 satıra bölünse de toplu seçim bütün uygun grubu içerir.

1. Ana sayfadaki ilgili sağlık kartını veya Sağlık Yönetimi’ndeki programı açın.
2. **Toplu Yapıldı** düğmesine dokunun.
3. Gerçek uygulama tarihini bir kez girin. Gruptaki hayvanlar seçili gelir; yapılmayan hayvanların işaretini kaldırın.
4. Gerekirse küpe / ad araması veya padok filtresi kullanın. **Yalnız görünenleri seç** filtredeki hayvanları, **Tümünü seç** bütün grubu seçer. Arama tek başına seçimi değiştirmez.
5. Alttaki hayvan sayısı ve toplam maliyeti kontrol edip **67 Hayvana Yapıldı Olarak Kaydet** düğmesiyle kaydedin. Düğmedeki sayı seçiminize göre değişir.

Her hayvana ayrı sağlık kaydı ve maliyet varsa ayrı gider kaydı işlenir. Seçilmeyenler beklemede kalır. Aynı gönderim yeniden ulaştığında ikinci sağlık veya gider kaydı oluşturulmaz. Seçimde geçersiz / pasif hayvan, değişmiş takvim veya yapılmamış önceki uygulama varsa toplu işlem kısmen kaydedilmez; liste yenilenerek seçim düzeltilir.

## Rapel ve diğer programlar

Toplu işlem yalnız seçilen doz / uygulamayı tamamlar. Rapeller beklemede kalır; tarih her hayvanın gerçek ilk uygulama tarihinden hesaplanır. Sonraki dönemsel tekrarlar da mevcut program kuralını kullanır. Eski çoklu hayvan / padok aşı programlarında sonraki bekleyen doz tarihleri de gerçek uygulama tarihine göre ilerler.

Aşı, parazit, vitamin / mineral ve tedavi programlarında aynı akış kullanılır. Henüz tarihi gelmemiş veya önceki uygulaması yapılmamış adımlar toplu karta alınmaz. Tedavinin farklı gün ve günlük uygulama sıraları birbirine karıştırılmaz. Senkronizasyon kendi adım ayrıntısı üzerinden kaydedilir.

Mobil ana sayfada çoklu planın 67 hayvanlık uzun küpe listesi kısa bir özetle gösterilir. Tam hayvan listesi ve seçim uygulama ekranında korunur.

## Kurulum

1. ZIP içeriğinin tamamını, tests klasörü dahil GitHub kaynaklarına aktarın.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_37_Setup.exe` dosyasını kurun.
4. Telefon ve masaüstünde mevcut adresi yeniden açın.

ZIP tam kaynak / kurulum projesidir; hazır Windows EXE içermez. Önceki sürümün senkronizasyon ve mobil pencere düzeltmeleri dahildir. Yeni veritabanı tablosu gerekmez; mevcut programlar kullanılmaya devam edilir.
