# AppEdition 2.0.60 — Mobil raporlar ve dönüş bağlantıları

## Değişiklikler

- Mobil finans raporundaki sabit genişlikli grafik ekran genişliğine uyar. Aylık sütunlar telefonlarda iki, daha geniş mobil ekranlarda üç sütunlu gruplarla aşağı doğru devam eder. Veriler kesilerek gizlenmez.
- Kategori Özeti mobilde Tür/Kategori/Adet/Toplam etiketli kartlar hâlinde gösterilir. Uzun kategori adları ve büyük tutarlar satıra sarılır. Grafik ve kategori alanında yatay kaydırma kaldırıldı. Masaüstü tablo görünümü ve dışa aktarma hesapları korunur.
- Üreme raporunun yazdırma sayfasına Ana Sayfa, Raporlara Dön ve Üreme Merkezine Dön bağlantıları eklendi. Seçilen işletme korunur; üreme merkezine dönüşte kategori ve arama filtreleri de korunur. Dönüş bağlantıları yazdırılan kağıtta görünmez. Ortak yazdırma sayfasını kullanan diğer raporlar da Ana Sayfa ve Raporlara Dön bağlantılarını alır.
- Rapor sekmesi değişirken adresin tüm sorgusunun silinmesi düzeltildi. Masaüstünde de işletme kimliği ve tarih/arama filtreleri korunur.

2.0.59 hız ve sade menü düzenlemeleri dahildir. Bu sürüm ilave giriş/stok hızlandırması içermez. Paylaşılan 2.0.59 ölçümlerinde POST /login 1.078 sn, bunun şifre kontrolü 1.012 sn; ana sayfa istekleri yaklaşık 1.0–1.27 sn, stok eşitlemesi yaklaşık 0.28–0.47 sn idi. Bu değerler ayrı performans incelemesi içindir; rapor görünümü düzeltmesinin bu süreleri giderdiği iddia edilmez.

## Kontroller

- Finans/PWA, AppEdition ve giriş dayanıklılığı: 32 test geçti.
- Üreme raporları ve dönüş/işletme yetkileri ile çekirdek kaynak karşılaştırması: 8 test geçti. Kaynak karşılaştırma testi önceki grupta da bulunduğundan toplam 39 farklı test doğrulandı. 2.0.59'daki tam 563 test bu sürümde baştan çalıştırılmadı.
- Chromium 153: 320, 390 ve 820 px genişliklerde 12 aylık kayıt, çok uzun kategori adı ve büyük tutarlarla belge, grafik ve kategori alanlarının yatay taşma oluşturmadığı ölçüldü. 1366 px masaüstünde belge taşması olmadığı doğrulandı; geniş tablolarda mevcut alan içi kaydırma korunur.
- Dört genişlikte üreme raporundan hem Raporlara Dön hem Ana Sayfa bağlantıları tıklanarak aynı işletmede kaldığı doğrulandı. Yazdırma modunda dönüş düğmeleri gizlenir; PDF indirme çalışır. JavaScript hatası görülmedi. Fiziksel iPhone/Safari/Android bu ortamda test edilmedi.
- Yalnız `simple_table_print` sunumu ve App içindeki tek rapor sekmesi URL ifadesi değişti. Bu iki bilinçli sunum değişikliği için kaynak referansları güncellendi; diğer çekirdek/solver referansları korundu. Sunar katalog değerleri ve finans hesapları değişmedi.

## Kaynaktan güncelleme

Yedek aldıktan sonra eski uygulama ve sunucu terminalini kapatın. ZIP'i yeni klasöre çıkarıp KAYNAKTAN_CALISTIR.bat dosyasını çalıştırın. Standart başlatıcı mevcut %LOCALAPPDATA%\CiftlikPro veri klasörünü kullanır; bu klasörü silmeyin. Özel veri yolu kullanıyorsanız aynı yolu koruyun. Telefonda Uygulama ve güncellemeler alanından yeni sürümü kontrol edip uygulamayı kapatıp açın. Sürüm 2.0.60 olmalıdır. EXE bu kaynak paketinde derlenmemiştir.
