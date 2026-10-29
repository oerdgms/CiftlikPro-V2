# ÇiftlikPro Enterprise — App Edition 2.0.38

26/10/2026 · Temel: 2.0.37 tam kaynak paketi.

## Masaüstünde rasyon yazdırma

Rasyon Çalışma Masası'nda **Rasyondaki Yemler** başlığının sağında **Rasyonu Yazdır** düğmesi bulunur. Bu bağlantı seçili rasyonun mevcut hazırlama raporunu açar. Hayvan sayısı ile 1 / 7 / 30 günlük dönem seçilebilir; **Yazdır / PDF** ile çıktı alınır.

Önceki masaüstü tasarımı hem eski Yem Ekle / Yazdır alanını hem de Çözüm Durumu içindeki Rapor kısayolunu gizliyordu. Yeni düğme bu iki gizli alanın dışında yer alır. Rapor kaydedilmiş reçeteyi kullanır; kaydedilmemiş miktar değişikliklerini rapora geçirmek için önce reçeteyi kaydedin.

## Aktif hayvan raporu

Rapora buzağı eklenirken önceki seçim işlevi gerçek durumunu dikkate almadan tüm buzağılara Aktif yazıyordu. Bu nedenle aktif raporda satılmış buzağılar da sayılabiliyordu.

- **Aktif:** işletmedeki aktif yetişkinler ve aktif buzağılar. Satılan / kesilen / zayiat kayıtları dahil edilmez.
- **Satıldı / Kesildi:** yetişkin ve buzağıların seçilen durumdaki kayıtları.
- **Tümü:** aktif ve arşiv kayıtları, gerçek durumlarıyla birlikte.

Yetişkine aktarılmış buzağı kayıtları ikinci kez sayılmaz. Ekrandaki toplam, mobil kartlar, web önizleme, PDF ve Excel aynı seçimi kullanır. Hayvan kayıtları ve geçmiş satışlar bu düzeltmeyle değiştirilmez; yalnız rapor seçimi düzeltilir.

## Kurulum

1. ZIP içeriğinin tamamını, yeni `app/animal_reports.py` ve tests klasörü dahil GitHub kaynaklarına aktarın.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_38_Setup.exe` dosyasını kurun.
4. Mevcut masaüstü / telefon adresini yeniden açın.

ZIP tam kaynak / kurulum projesidir; hazır Windows EXE içermez. Önceki 2.0.37 toplu sağlık, rapel ve mobil pencere düzeltmeleri dahildir. Veritabanı şeması değişmez.
