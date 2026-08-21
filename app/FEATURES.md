# ÇiftlikPro Enterprise V1.0 — Özellik Kilidi

Aşağıdaki modüller yeni sürümlerde korunmalıdır:

- [x] Profesyonel dashboard
- [x] Dişi hayvanlar
- [x] Erkek hayvanlar
- [x] Hayvan düzenleme
- [x] Tıklanabilir hayvan kartı
- [x] Fotoğraf yükleme
- [x] Mobil kamera
- [x] Fotoğraf galerisi
- [x] Süt takibi
- [x] Kilo takibi
- [x] Tohumlama
- [x] Gebelik ve 280 gün hesabı
- [x] Buzağı ekleme/düzenleme
- [x] Tıklanabilir buzağı kartı
- [x] 10 aylık otomatik geçiş
- [x] Sağlık/aşı/ilaç
- [x] Gelir/gider ekleme
- [x] Finans raporları
- [x] CSV dışa aktarma
- [x] JSON içe/dışa aktarma
- [x] Manuel ve günlük yedekleme
- [x] Ağ erişimi
- [x] Mobil uyumluluk

Her yeni sürümde bu dosya kontrol listesi olarak kullanılmalıdır.

## V3.7.9 Otomatik Hayvan Alımı Finans Entegrasyonu
- Dişi/Erkek hayvan eklerken alış fiyatı > 0 ise Finans'a otomatik Gider / Hayvan Alımı kaydı açılır.
- Alış ödeme yöntemi hayvan ekleme ekranından seçilir.
- Daha önce Hayvan Alımı finans kaydıyla ilişkilendirilmiş hayvanlar yeni Hayvan Alımı seçiminde gösterilmez.
- Backend aynı hayvana ikinci Hayvan Alımı bağlantısını engeller.


## V3.8.0 Sağlık + Aşı Planlama
- Sağlık seçiminde yalnız aktif dişi/erkek ve aktif buzağılar görünür; satılan/kesilen hayvanlar dışlanır.
- Küpe/takma ad ile aranabilir seçim.
- Aşı kaydında 2. doz planlama: varsayılan 15 gün, değiştirilebilir.
- Dashboard ve Sağlık ekranında yaklaşan/geciken doz uyarıları.
- 2. Doz Yapıldı ile gerçek uygulama tarihi sağlık geçmişine kaydedilir.

## V3.9.0 — Padok + Yem & Rasyon
- Padok tanımlama: ad, kod, tür, kapasite, not.
- Aktif hayvan ve buzağıları padoklara atama/taşıma; eski serbest metin padokları otomatik migrasyonla korunur.
- Padok hareket geçmişi veri tabanında saklanır.
- Besi_V5.02.xlsm besin veri tabanından 246 yem maddesi referans kataloğa alınmıştır; eski fiyatlar özellikle aktarılmamıştır.
- Yem besin alanları: KM, HP, NDF, TDN, ME, NEm, NEg, nişasta, yağ, kül, Ca, P, Mg, K, Na, S.
- Tarihli yem fiyat geçmişi ve stok giriş/çıkış/tüketim hareketleri.
- Rasyon oluşturma ve yem bazında kg/baş/gün miktarı tanımlama.
- Rasyon analizi: yaş yem, kuru madde, ham protein, NDF, ME, Ca/P ve günlük baş maliyeti.
- Rasyonu padoka atama; padok ekranında aktif rasyon ve baş/gün maliyeti gösterimi.
- Rasyon analizi karar destek amaçlıdır; nihai besleme programı veteriner/zooteknist değerlendirmesi gerektirir.

## V3.9.2 Akıllı Rasyon Hedefi
- Rasyona hedef canlı ağırlık ve hedef günlük canlı ağırlık artışı eklendi.
- Kuru madde, ham protein, metabolik enerji, NDF, kalsiyum ve fosfor için hedef/mevcut karşılaştırması eklendi.
- Eksik / uygun / fazla karar desteği eklendi.
- Hedef profili rasyon bazında sonradan güncellenebilir.
- Hesaplar ön değerlendirme/karar desteğidir; nihai rasyon uzman doğrulaması gerektirir.


## V3.9.4 Akıllı Rasyon Dengeleme
- Fazla HP/Ca/P/NDF için mevcut rasyondan azaltma adayları.
- Tüm yem kataloğunda +0,50 kg simülasyonu ile eksik tamamlayan adayların çoklu-besin puanlaması.
- Fiyatı olmayan yemlerde Fiyat girilmemiş gösterimi ve stok görünürlüğü.
- Azalt + ekle kombine dengeleme fikirleri.
- Negatif simülasyonun uygulanabilmesi ve rasyon miktar düzenleme UX hotfixleri korunur.


## V3.9.5 Kompakt Rasyon Masası
- Akıllı Rasyon Hedefi ile Rasyon Çalışma Masası art arda yerleştirildi.
- Akıllı dengeleme ilk bakışta üç kısa çözüm kartına indirildi.
- Uzun yem adayları ve teknik tablolar varsayılan olarak kapalı hale getirildi.
- Yeni yem ekleme ve padoka atama ikincil katlanabilir alanlara taşındı.

## V3.9.6 Besi + Süt Akıllı Rasyon
- Yeni Rasyon formu varsayılan kapalı; yalnız ihtiyaç olduğunda açılır.
- Yeni rasyon oluşturma akışı Besi ve Süt olarak ayrıldı.
- Süt rasyonu için ana girdiler: ortalama canlı ağırlık ve hedef süt (L/gün).
- Akıllı Süt Rasyonu Hedefi KM, HP, ME, NDF, Ca ve P için hedef/mevcut/durum karşılaştırması yapar.
- Süt yağı ve süt proteini gelişmiş/isteğe bağlı hedef girdileri olarak saklanır.
- Mevcut Çalışma Masası ve Akıllı Dengeleme motoru, rasyon tipine göre Besi veya Süt hedeflerini kullanır.
- Süt hedefleri ön değerlendirme/karar desteğidir; nihai rasyon veteriner veya zooteknist tarafından doğrulanmalıdır.


## V3.9.6 Besi + Süt Akıllı Rasyon
- Yeni Rasyon formu varsayılan kapalıdır.
- Besi ve Süt rasyonu oluşturma akışları ayrıldı.
- Süt rasyonu ana hedef girdileri: canlı ağırlık + hedef süt L/gün.
- Süt hedef motoru KM, HP, ME, NDF, Ca ve P karşılaştırması yapar; çalışma masası ve akıllı dengeleme aynı hedefleri kullanır.


## V3.9.7 Hızlı Yem Ekle
- Besi ve süt rasyonlarında Akıllı Rasyon Hedefi ile Rasyon Çalışma Masası arasına ortak Hızlı Yem Ekle paneli eklendi.
- 246 yemlik katalog arama ile filtrelenir; ilk 8 sonuç gösterilir.
- Yem kartında grup, KM, HP, NDF, fiyat, stok ve rasyondaki mevcut miktar görünür.
- Seçilen yem için miktar doğrudan yazılabilir veya +/- 0,10 kg ile ayarlanabilir.
- Rasyonda zaten bulunan yem seçilirse mevcut miktar otomatik gelir ve güncelleme yapılır.

## V3.9.16 - NASEM Yem Kataloğu + Düzenle/Sil
- Yem Kataloğu kaynak yaklaşımı NASEM 2016 Beef / NASEM 2021 Dairy referanslarına taşındı.
- NASEM 2021 Table 19-1 ile birebir eşleştirilebilen temel yemlerde KM/HP/NDF/nişasta/mineral alanları güncellendi.
- Kullanıcının daha önce elle değiştirdiği kayıtlar otomatik migrasyonda ezilmez.
- Sistem kataloğundaki ve kullanıcı tarafından eklenen tüm aktif yemlere Düzenle özelliği eklendi.
- Düzenleme ekranı: KM, HP, NDF, TDN, ME, NEm, NEg, nişasta, yağ, kül, Ca, P, Mg, K, Na, S ve kaynak.
- Sil işlemi güvenli soft-delete yapar; geçmiş rasyon/fiyat/stok kayıtları korunur.


## V3.9.18 - Kızgınlık Seçim Hotfix
- Takma adı boş aktif dişilerde kızgınlık ekranı hayvan seçimi düzeltildi.
- Kızgınlık seçicisinde görünen etiket ve hidden animal_id aynı normalize edilmiş veri üzerinden eşleştiriliyor.
- Küpe numarası doğrudan yazıldığında da hayvan ID'si doğru atanıyor.

## V3.9.20 Hotfix 2
- Sağlıkta ilaç tedavisi için tedavi günü ve günlük uygulama sayısı planı.
- Aşılarda 1-10 doz ve dozlar arası gün tanımlama; her doz ayrı Yapıldı takibi.
- Padok bazında toplu aşı planlama; plan anındaki hayvan listesi sabitlenir.
- Padok dozu tek butonla toplu Yapıldı; her hayvanın sağlık geçmişine ayrı kayıt işlenir.
- Planlanan sağlık işlemleri mobil kart görünümüne geçirildi; gecikme durumu ve işlem butonları taşmadan görünür.
