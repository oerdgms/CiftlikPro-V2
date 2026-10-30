# 2.0.45 – KM Oranı

## Kullanım

Rasyon Detayı ekranında KM oranı (% canlı ağırlık) her zaman görünür. Varsayılan 2,50'dir. Örneğin 250 kg için 6,25 kg, 400 kg için 10,00 kg, 500 kg için 12,50 kg KM/gün hedeflenir. Oranı değiştirmek kilogram önizlemesini günceller.

- Kaydet: oranı yalnız bu rasyona kaydeder. Yem miktarları ve geçmiş tüketim/maliyetler değişmez.
- Bu oranla çöz: oranı kaydeder; mevcut yemleri, canlı ağırlığı ve hayvan profilini çözüm ekranına aktarır. Yem seçimini kontrol edip Rasyonu Çöz düğmesine basın. Sonuç yeni rasyon oluşturur; mevcut rasyonun miktarları korunur.
- Yeni rasyon çözümünde de aynı oran alanı bulunur. Varsayılan %2,50'dir; yarım bırakılmış çözüm taslağında önceden seçtiğiniz oran korunabilir.

KM kartı, canlı yem miktarı değişiklikleri ve solver fizibilite kontrolü aynı seçilmiş hedefi kullanır. Diyet enerji yoğunluğu artık bu hedefi değiştirmez. Solverin mevcut toleransları korunmuştur; seçili yemlerle hedefler birlikte karşılanamıyorsa sınırlama/sapma bildirilir veya çözüm kaydedilmez. Bu giriş otomatik hava/çamur/enerji düzeltmesi yapmaz.

## Protein kontrolü

Kayıtlı rasyon özeti bazı eski/tanınmış yem kayıtlarında katalog HP'sini, solver ise normalleştirilmiş HP'yi okuyabiliyordu. Özet aynı normalleştirilmiş HP hesabına bağlandı. Canlı önizleme ve solver zaten bu kaynağı kullanıyordu. Bilimsel ayrıntıda günlük HP arzı (g/gün) ve MP gereksinimi ayrı belirtilir.

HP yüzdesi kuru madde bazındadır. Günlük HP = toplam KM × HP yüzdesi / 100. Canlı ağırlık büyürken HP yüzdesi genellikle azalabilir; günlük gram miktarı ise tüketim, hedef büyüme ve hayvan profiline bağlıdır. HP ile metabolik protein aynı değildir. Mevcut HP hedefi referans tablolardan tarama tabanıdır; katalogda RDP/RUP olmadığı için tam metabolik protein arzı çözümü olarak yorumlanmaz. Oranı değiştirmek hayvanın MP gereksinimini veya referans HP yüzdesini kendiliğinden artırmaz; hedef KM yükseldikçe aynı yüzdeye karşılık gelen sunulan HP gramı yükselir.

Referans: NASEM 2016, Chapter 20, errata tabloları 20-1 ve 20-2: https://nap.nationalacademies.org/resource/19014/Beef%20Cattle%20errata%20sheet2.pdf

## Veri ve kurulum

Eski veritabanına target_dm_pct_bw alanı %2,50 varsayılanıyla eklenir. Var olan rasyon kalemleri, miktar geçmişi ve süt hesapları değiştirilmez. Önce uygulamadan yedek alın; sunucuyu kapatıp yeni kaynak paketini ayrı klasöre çıkarın ve mevcut veri klasörünü koruyarak kaynaktan çalıştırın. Telefonda sayfayı yenileyin. EXE derlenmedi. 2.0.43 Besi Performansı menüsü ve 2.0.44 liste sadeleştirmesi dahildir.
