# ÇiftlikPro Enterprise — App Edition 2.0.36

24/10/2026 · Temel: 2.0.35 tam kaynak paketi.

## Senkronizasyona tek yerden giriş

Üreme Yönetimi’nin sol üstündeki iki ayrı kısayol kaldırıldı. **Kızgınlık Kaydı → Tohumlama → Senkronizasyon** düğmeleri aynı işlem çubuğundadır.

Senkronizasyon düğmesi önce plan listesini açar. Aktif, Tamamlanan, İptal ve Tümü filtreleriyle mevcut kayıtlar görülebilir. Plan adı, küpe veya veteriner ile arama yapılabilir. Bir plan seçilince hayvanlar ve uygulama adımları açılır.

Yeni kayıt için bu ekrandaki **Senkronizasyon Tanımla** düğmesi kullanılır. Takvim, başlangıç tarihi ve saati, hayvanlar ve uygulama adımları aynı mevcut formdan kaydedilir. Üreme Yönetimi bağlantısıyla ana üreme ekranına dönülür.

Sağlık Yönetimi → Senkronizasyon aynı planları gösterir. İki giriş aynı veritabanını ve kayıt işlevlerini kullanır; ikinci bir plan kopyası oluşturulmaz. Mevcut doğrudan yeni kayıt, hayvan seçimi, plan ayrıntısı ve uygulama adımı bağlantıları çalışmaya devam eder.

## Kurulum

1. Tam ZIP içeriğiyle GitHub kaynaklarını güncelleyin; tests klasörü dahil bütün dosyaları aktarın.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_36_Setup.exe` dosyasını kurun.
4. Telefon ve masaüstünde mevcut adresi yeniden açın.

ZIP tam kaynak / kurulum projesidir. Hazır Windows EXE içermez. Önceki 2.0.35 özellikleri ve düzeltmeleri dahildir.
