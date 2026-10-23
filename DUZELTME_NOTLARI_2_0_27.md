# ÇiftlikPro App Edition 2.0.27 — Durum Ekle

22/10/2026. Temel: App Edition 2.0.26.

Sürü Merkezi’ndeki “Durumu düzenle” bağlantısı, “＋ Durum Ekle” düğmesiyle açılan ikonlu bir seçim penceresine dönüştürüldü. Hayvanın küpesi, adı ve mevcut süt/gebelik durumu pencerenin üstündedir. Masaüstünde iki sütunlu ortalanmış pencere, dar telefonda tek sütunlu alt panel kullanılır. İçerik kendi içinde kayar; üst başlık, Vazgeç ve formdaki Kaydet erişilebilir kalır. Formdan seçim ekranına geri dönülebilir; Escape, Vazgeç ve dış alana tıklama pencereyi kapatır. Odak açan düğmeye geri döner.

Yetişkin dişilerde kızgınlık, kart notu, tohumlama, Gebe/Boş sonucu, Sağmal, Kuru, Düve, doğum, sağlık ve tartım seçenekleri bulunur. Erkek ve buzağılarda kart notu, sağlık ve tartım sunulur. Satılmış, kayıp veya yetişkine aktarılmış buzağı kayıtları bu menüden işlem açamaz.

Kızgınlık, tohumlama, gebelik sonucu, süt durumu ve tartım formları mevcut Enterprise kayıt yollarını kullanır. Gebelik sonucu en güncel tohumlamaya bağlıdır; açık tohumlama kaydı yoksa tarih veya kayıt uydurulmaz. Yeni kayıt açmak yerine gerekli tohumlama formuna yönlendirilir. Kuru/Sağmal/Düve seçimleri gebelik sonucundan ayrı saklanır.

Doğum Bilgisi Ekle formunda anne hazırdır. Doğum tarihi, buzağı küpesi, cinsiyet, ırk, ad/takip no, baba küpesi ve not alınır. Kayıt, mevcut Çiftlikte Doğdu akışıyla gerçek buzağı oluşturur. Sağlık bağlantısı doğru hayvan seçili plan ekranını; İşletme Notu bağlantısı kartın mevcut not alanını açar.

Mobil hayvan kartının Durum Ekle ve Doğum Ekle hızlı işlemleri de aynı pencereyi kullanır. Üç noktalı işlemler, Satış/Zayiat ve baskı erişimi korunur. Masaüstü Ayrıntı/Kart/Kompakt düğme hizası ile mobil sabit sekme düzeltmesi dahildir.

JavaScript kapalıysa bağlantılar normal kayıt sayfası olarak açılabilir. İstemci varlıklarının önbellek kimliği 2.0.27; yeni animal_actions.py modülü Windows paket tanımına dahildir. Çekirdek app/server.py içinde yalnız yapı kimliği değişir.

Tam kaynak/kurulum projesidir. Windows hedefi: CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_27_Setup.exe. Hazır EXE içermez; mevcut GitHub Actions akışıyla derlenir.
