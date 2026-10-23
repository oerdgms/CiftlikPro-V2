# ÇiftlikPro Enterprise — App Edition 2.0.31

Üreme Yönetimi hayvan kartları mobilde ve masaüstünde daha az alan kaplar.
Temel: 2.0.30 Birleşik Sağlık Yönetimi tam kaynak paketi.

## Kart düzeni

- Mobilde fotoğraf, küpe, isim, padok / ırk ve deneme rozeti üstte bir arada bulunur.
- Tarih ve gün bilgisi solda; Sonuç Gir / Kontrol Sonucu sağdadır. İç içe işlem kutuları kaldırıldı.
- Durum ve sonraki işlem açıklaması gösterilmeye devam eder.
- Uzun isimler satır sonunda kısalır. Tam kayıt ve isim kimlik / fotoğraf bağlantısıyla açılır; kaydedilmiş metin değiştirilmez.
- Fotoğrafsız hayvanda mevcut uygulama simgesi kullanılır. Satıra taşan dişi işareti kaldırıldı.
- Ayrı Seç düğmesi kaldırıldı. Kimlik veya fotoğraf aynı seçme bağlantısını açar.
- Birden fazla işlemli gebelik kartlarında tüm mevcut düğmeler korunur.
- Masaüstünde kimlik, tarih / durum ve işlem aynı hizadadır; dar telefonda içerik genişliği aşılmaz.

Arama, padok filtresi, aşamalar, Üreme Takibi / Akıllı Gebelik, akordeon, Tümünü Gör ve seçili hayvan ayrıntıları aynı davranışlarını korur. Gebelik sonucu, deneme sayısı, tahmini doğum ve kuru dönem hesapları değiştirilmedi.

## Kurulum

1. ZIP içindeki tüm kaynakları GitHub deposuna aktarın.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. Oluşan `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_31_Setup.exe` dosyasıyla güncelleyin.
4. Mevcut sunucu adresini yeniden açın; Modüller → Üreme Yönetimi.

ZIP tam kaynak / kurulum projesidir; hazır EXE içermez. Veritabanı veya veri klasörünü silmeyin. Birleşik Sağlık Yönetimi, senkronizasyon, laktasyon ve diğer önceki modüller pakete dahildir.
