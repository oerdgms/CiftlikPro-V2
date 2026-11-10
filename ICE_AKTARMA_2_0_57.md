# AppEdition 2.0.57 — İçe aktarma akışı

01.11.2026. Temel sürüm 2.0.56. Kaynaktan çalıştırma paketi.

- İşletme Ayarları > Veri Aktarımı > Dosya Seçme Ekranını Aç ve raporlardaki İçe Aktarma bağlantıları ortak /animals/import ekranını açar. Mobil raporlar giriş ekranı artık dosya seçme ekranının önüne geçmez.
- Eski /reports?tab=import adresi yeni ekrana yönlendirilir. Aktarım tamamlanınca Sürü Raporları sekmesi açılır; eski gizli import/rapor anchor adresleri bu akışta düzeltilir.
- Dosya okuma formu uygulama içinde fetch ile yüklenir. Yükleniyor durumu görünür; çift gönderim engellenir. Hata aynı formda gösterilir, seçilen dosya korunur ve yeniden deneme düğmesi açılır. Bağlantı hatasında otomatik kayıt gönderimi yapılmaz.
- JavaScript kapalıyken de okunamayan dosya için boş sayfa yerine uygulama içinde açıklama ve yeniden dosya seçme formu gösterilir; bu durumda tarayıcı güvenliği nedeniyle dosya yeniden seçilmelidir.
- Geçerli dosyalar için önce kompakt önizleme kartları açılır. Bu aşamada hayvan kaydı eklenmez. Kullanıcının ayrı onayıyla mevcut yedekleme, mükerrer kontrolü ve aktarım işleyicisi çalışır.
- İşletme kimliği yükleme, önizleme, iptal ve onay adreslerinde korunur. Önizleme başka işletmede açılmaz. Kullanıcı/yönetici izinleri korunur.

## Desteklenen dosyalar

XLSX, başlıkları olan CSV ve metin içeren dijital Bakanlık PDF raporları desteklenir. Sınır 12 MB'dır. CSV başlıkları örneğin Küpe No, Cinsiyet, Doğum Tarihi ve Irk olabilir.

Fotoğraf olarak taranmış PDF'nin içinde seçilebilir metin yoksa mevcut okuyucu hayvanları çıkaramaz. Bu sürüme OCR motoru eklenmedi. Böyle bir dosya için OCR ile metin çıkarılması ve özellikle küpe/tarihlerin kontrol edilmesi veya sistemden orijinal PDF/Excel alınması gerekir. Dosya taranmışsa bunun için açık mesaj gösterilir; kayıt eklenmez.

Bilgisayarda yeni sürümü mevcut veri konumuyla çalıştırıp telefondan Uygulama ve güncellemeler ile yenileyin. Önceki işletme seçimi, fotoğraf, rasyon ve diğer düzeltmeler dahildir. Yem kataloğu değiştirilmedi.

Mobil Raporlar giriş ekranına da doğrudan Hayvan İçe Aktarma kartı eklendi; dosya seçme ekranını açması beş genişlikteki son tarayıcı kontrolünde doğrulandı.
