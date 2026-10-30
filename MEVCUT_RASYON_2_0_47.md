# Mevcut Rasyonu Yeniden Hesaplama

Rasyon Detayı ekranındaki görünür alanda hayvanın canlı ağırlığını ve KM oranını girin. Varsayılan oran %2,50'dir; seçtiğiniz yüzde kilo değişiminde korunur. Örneğin 400 → 450 kg değişiminde %2,50 ile hedef KM 10 → 11,25 kg/gün olur. Önizleme kilogramı yazdıkça güncellenir.

Kaydet yalnız canlı ağırlık ve KM hedefini kaydeder; yem miktarlarını değiştirmez. Yeniden Hesapla mevcut rasyonun yemlerini, kayıtlı günlük artış hedefini, yaşını ve hayvan profilini kullanarak yeniden çözüm üretir. Sonuçta mevcut/yeni yem miktarları, KM, HP ve maliyet gösterilir.

- Vazgeç: mevcut rasyon ve miktarlar korunur.
- Aynı Rasyona Uygula: aynı rasyon numarası, adı ve padok bağlantıları korunarak yem miktarları ve hedefler güncellenir. Yeni bir rasyon oluşturulmaz.

Kilitli yem miktarı sabit kalır. Kilit güncel yem sınırlarıyla uyuşmuyorsa veya seçili yemlerle çözüm bulunamıyorsa mevcut rasyon korunur ve açıklama gösterilir. Mevcut solverin hedef toleransları ve güvenlik kontrolleri sürer. Süt rasyonuna yeni yeniden hesaplama işlemi uygulanmaz; süt motoru korunmuştur.

Yenilenen miktarlar bugünün tarihiyle miktar geçmişine eklenir. Önceki günlerin kayıtlı miktarları değiştirilmez. Aynı günün son geçerli miktarı mevcut tarihli hesap mantığıyla kullanılır. Eski stok tüketim hareketleri yeniden oluşturulmaz; yeni padok ataması eklenmez.

Önizleme kullanıcıya özeldir, 20 dakika geçerlidir ve bir kez uygulanabilir. Önizlemeden sonra rasyon/kalem/kilit/yem analizi/fiyat değişmişse uygulama reddedilir; yeni verilerle yeniden hesaplanmalıdır. Başka bir kullanıcının önizlemesi uygulanamaz. Önizlemeyi açmak işletme rasyonunu değiştirmez.

Kurulum: uygulamadan yedek alın. Kaynak sunucusunu kapatıp bu paketi ayrı klasöre çıkarın ve mevcut veri klasörünü koruyarak kaynaktan başlatın. EXE oluşturulmadı. 2.0.45 KM/protein ve 2.0.46 Faz rasyonu silme düzeltmeleri dahildir.
