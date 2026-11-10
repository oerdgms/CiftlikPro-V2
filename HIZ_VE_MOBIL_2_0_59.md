# AppEdition 2.0.59 — Giriş, stok ve mobil menü

## Düzeltilen işlemler

- Her başarılı girişte ana hesaba yazılan `last_login`, işletmeler arası kullanıcı eşitlemesinden çıkarıldı. Yalnız bu tarih değiştiğinde diğer işletmenin kullanıcı tablosu silinip yeniden oluşturulmaz. Şifre, rol, aktiflik ve diğer hesap alanları eşitlenir. İşletme erişimleri ana hesaplardan her istekte kontrol edilmeye devam eder.
- Ana sayfa, yem veya padok açılışında otomatik tüketim eşitlemesi hâlâ çalışır. Tüketim ve bağlı stok hareketi aynıysa UPDATE ve yem maliyet geçmişinin DELETE/INSERT işlemleri atlanır. Hayvan sayısı/rasyon değişikliği, eksik stok bağlantısı veya değiştirilmiş tüketim hareketi yeniden işlenir. Manuel stok işlemleri korunur.
- Mobil yan menü 13 ana bağlantıdan 6 bağlantıya indirildi: Ana Sayfa, Hayvanlar, İşler ve Hatırlatmalar, Padoklar, Tüm Modüller, Ayarlar. Besi performansı, rasyon, sağlık, üreme, finans ve diğer işlevler Modüller ekranında korunur. İşletme değiştirme, çıkış ve PWA kurulum bağlantıları korunur.
- Ana sayfadaki “Tümü” bağlantıları “Tüm hayvanlar” ve “Tüm işler” olarak açıklandı. İşletme kısayollarının açıklaması açtıkları ekranlarla eşleştirildi.

Bu sürüm mobil sadeleştirmenin ilk adımıdır. Tüm uygulamanın kullanım kolaylığının yeni kullanıcılarla doğrulandığı anlamına gelmez. Fotoğraftan ağırlık tahmini bu sürüme eklenmedi.

## Ölçüm

Yeni `[PERF] İstek GET / ...` satırı dış istek süresini; hesap eşitleme, buzağı geçişi, stok eşitleme, maliyet geçmişi ve sayfa oluşturma sürelerini ve çağrı sayılarını gösterir. Giriş POST isteğinde şifre kontrolü de ölçülür. Yarım saniyeden uzun ilgili isteklerde otomatik yazılır. Tüm ilgili istekler için kaynak başlatılmadan önce `CIFTLIKPRO_PERF=1` ayarlanabilir.

Parantez içindeki sayı çağrı sayısıdır. Bazı aşamalar iç içedir; süreleri toplayarak toplam süre hesaplanmamalıdır. URL sorguları, işletme adları, şifreler ve hayvan bilgileri bu yeni ölçüm satırına yazılmaz.

Yapay bir padok/tek yem/181 günlük stok girişi testinde değişmeyen her yenilemede SQLite değiştirilen satır sayısı 364'ten 0'a indi. Bu sonuç müşteri bilgisayarındaki toplam açılış süresini veya 5 saniyelik gecikmenin tamamen giderildiğini kanıtlamaz. Gerçek işletme veritabanı ve fiziksel iOS PWA bu ortamda test edilmedi.

## Kaynaktan güncelleme

1. ÇiftlikPro içinden güncel yedek alın; mevcut veri klasörünü ayrıca koruyun.
2. Çalışan eski ÇiftlikPro penceresini ve sunucu terminalini kapatın. Aynı portta eski sürüm açık kalmasın.
3. ZIP'i yeni bir klasöre çıkarın ve `KAYNAKTAN_CALISTIR.bat` dosyasını çalıştırın.
4. Bu başlatıcı mevcut `%LOCALAPPDATA%\CiftlikPro` veri klasörünü kullanır. Veritabanlarını, `enterprises` klasörünü, fotoğrafları, lisansı veya yedekleri silmeyin. Özel bir başlatıcı/veri yolu kullanıyorsanız aynı veri yolunu koruyun.
5. Telefonda Uygulama ve güncellemeler alanından güncellemeyi kontrol edin, uygulamayı kapatıp yeniden açın. Gösterilen paket sürümü 2.0.59 olmalıdır. Çevrimdışı iken güncelleme alınamaz.

Bu paket kaynak dağıtımıdır; Windows EXE derlenmemiştir.
