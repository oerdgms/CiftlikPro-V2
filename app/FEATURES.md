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

## V3.9.1 Akıllı Rasyon Hedefi
- Rasyona hedef canlı ağırlık ve hedef günlük canlı ağırlık artışı eklendi.
- Kuru madde, ham protein, metabolik enerji, NDF, kalsiyum ve fosfor için hedef/mevcut karşılaştırması eklendi.
- Eksik / uygun / fazla karar desteği eklendi.
- Hedef profili rasyon bazında sonradan güncellenebilir.
- Hesaplar ön değerlendirme/karar desteğidir; nihai rasyon uzman doğrulaması gerektirir.
