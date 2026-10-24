# ÇiftlikPro Enterprise — App Edition 2.0.34

24/10/2026. Temel: 2.0.33a CI Test Fix tam kaynak paketi.

## Hayvan işlemleri ve düzenleme

Hayvan kartındaki üç nokta menüsü artık Durum Ekle ile aynı paneli kullanır. Tutma çizgisi, Vazgeç düğmesi, hayvan kimliği ve ikonlu / açıklamalı işlem satırları aynı düzendedir. Satış / zayiat ve silme satırları mevcut işlem / onay bölümünü açar; menüden bir satıra basmak kayıt silmez.

Hayvan veya buzağı Düzenle bağlantısı mevcut sayfanın üzerinde açılır. Mobilde alt panel, masaüstünde ortalanmış pencere olarak görünür. Form kaydırılabilir; kaydetme / vazgeçme düğmeleri erişilebilir kalır. Vazgeç, Escape ve arka plana tıklama paneli kapatır. Hayvan kartına dönüldüğünde klavye odağı geri gelir. İşletme Notu işlemi not alanını hazır odaklar.

Aynı düzenleme adresi doğrudan açıldığında normal sayfa olarak da kullanılabilir. Formdaki mevcut alanlar, anne seçimi, dosya yükleme, fotoğraf optimizasyonu, alış maliyeti ve isteğe bağlı finans eşitleme seçimi korunur.

## Sabit TR ön eki

TR + 8–14 rakam biçimindeki mevcut standart küpelerde TR ayrı, sabit bir ön ektir. Rakamlar düzenlenebilir; TR dahil tam küpe yapıştırıldığında rakam bölümü alınır. Boş veya eksik küpe kaydedilmez. Başka bir hayvana ait küpe mevcut mükerrerlik kontrolü tarafından engellenir. Aktarılmış buzağı / yetişkin çiftinin bağlı küpeleri birlikte güncellenir.

Özel / eski küpe kimlikleri otomatik yeniden adlandırılmaz; mevcut düzenleme alanında korunur. Baba küpesi ayrı alandır.

## Sağlık form alanları

Hastalık / tedavi kaydındaki Veteriner Hekim alanı telefonda tam genişlikte, isim yazmaya uygun tek alandır. Tarih ve maliyet alanlarının yükseklikleri / boşlukları eşitlendi. Aşı, parazit ve vitamin programları aynı maliyet kutusunu kullanır; uzun başlıklar girişleri kaydırmaz.

TL simgesi alanın içinde ayrı gösterilir. `125,50` veya `125.50` girişi kuruşuyla kaydedilir. Hayvan başı uygulama tutarı, veteriner tutarı ve ilaç tutarı eski tam sayı biçimlendiricisinden ayrıldı. Plan oluşturma ile gerçek uygulama / gider kaydı ayrımı korunur.

## Doğrulama

440 otomatik testin tamamı geçti. 20 tarayıcı senaryosunda mobil / masaüstü form hizası, açma / kapatma, TR girişi, fotoğraflı gerçek kayıt ve kuruşlu sağlık uygulamaları doğrulandı. Ayrıntılar: DOGRULAMA_APP_EDITION_2_0_34.md.

## Kurulum

1. ZIP içindeki tam kaynakları tests klasörü dahil GitHub deposuna aktarın.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_34_Setup.exe` dosyasını kurun.
4. Telefon ve masaüstünde mevcut sunucu adresini yeniden açın.

ZIP tam kaynak / kurulum projesidir; hazır Windows EXE içermez. Mevcut veri klasörünüzü silmeyin. Birleşik sağlık, senkronizasyon, kompakt üreme kartları, ana sayfa düzeni ve canlı aramalar dahildir.
