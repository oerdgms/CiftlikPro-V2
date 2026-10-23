# ÇiftlikPro Enterprise — App Edition 2.0.33

23/10/2026. Temel: 2.0.32 Masaüstü Ana Sayfa tam kaynak paketi.

## Canlı metin araması

Yeni masaüstü Sürü Merkezi'ndeki arama alanı eski, gizli formun arama dinleyicisine bağlı değildi. Görünen form artık doğrudan bütün sürü kayıtlarında arama yapar; sonuçlar daha sonra sayfalanır. Sonraki sayfalardaki hayvanlar da bulunur.

Küpe numarası, isim, ırk, padok ve notlarda kısmi metin aranabilir. Birden fazla kelime ilgili alanların herhangi birinde eşleşebilir. Örneğin “inci sari”, adı İnci olan SARI PADOK'taki hayvanı bulur. “ÇİĞDEM”, “Çiğdem” ve “cigdem” aynı biçimde eşleşir. Durum / tür / padok filtreleri aramaya birlikte uygulanır.

Hayvan araması mobilde ve masaüstünde yazarken sonuçları yeniler; arama odağı korunur. Alan temizlendiğinde filtre kapsamındaki liste geri gelir, bulunamayan sorguda boş sonuç mesajı gösterilir. Hızlı yazarken eski yanıtlar son sorgunun sonucunu değiştirmez. Mobil ve masaüstü görünüm değiştiğinde arama ve ortak filtreler eşleşir.

Finans, sağlık, süt, yem kataloğu, arşiv ve ilgili diğer GET liste aramaları yazarken çalışır. Üreme, padok, hayvan ve katalog seçimleri de ortak Türkçe metin eşleştirmesi kullanır. Diğer GET listeleri mevcut sunucu sorgusuna geçer; kayıt ekleme veya düzenleme formları otomatik gönderilmez. Seçim listesini aramak, daha önce işaretlenmiş hayvanları kaldırmaz.

## Ana Sayfayı Düzenle

Masaüstü karşılama satırındaki tek başına yuvarlak ayar simgesi kaldırıldı. Aynı yerde ince çerçeveli, küçük simgeli “Ana Sayfayı Düzenle” düğmesi bulunur. Düğme mevcut kart seçme / sıralama ekranını açar. Mobil ana sayfa ve mevcut hesaplamalar korunur.

## Kurulum

1. ZIP içindeki kaynakların tamamıyla GitHub deposunu güncelleyin.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_33_Setup.exe` dosyasını kurun.
4. Telefon ve bilgisayarda mevcut sunucu adresini yeniden açın.

ZIP tam kaynak / kurulum projesidir; hazır Windows EXE içermez. Veri klasörünüzü silmeyin. Birleşik sağlık, senkronizasyon, kompakt üreme ve önceki ana sayfa düzeni pakette bulunur.
