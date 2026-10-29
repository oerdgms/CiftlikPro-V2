# App Edition 2.0.40 — Kompakt Süt Girişi

26/10/2026 · Yapı: `AppEdition2.0.40-CompactMilkEntry`.

## Günlük giriş

**Modüller → Süt & Laktasyon** ekranında her hayvanın küpesi, adı, padoku ve biliniyorsa sağım günü aynı kimlik alanındadır. Telefonda Sabah ve Akşam litre kutuları yan yanadır; altlarında günlük toplam görünür. Masaüstü aynı formu kompakt satırlar halinde gösterir.

- Ondalıklı litre girişi desteklenir. Hayvan ve liste toplamı yazarken hesaplanır.
- **Ortalamalar**, 7 gün ortalaması, 30 gün ortalaması ve laktasyon toplamını açar. Bu değerler kaydedilmiş kayıtlardan hesaplanır.
- Manuel laktasyon başlangıcı bilinmiyorsa sağım günü ve laktasyon toplamı tahmin edilmez. Durum rozeti ve **Sağmal Listesi** mevcut düzenleme ekranına gider.
- Bugünkü süt üst özeti bütün aktif dişilerin kaydedilmiş toplamıdır. Alttaki liste toplamı seçilen durum grubundaki hayvanları kapsar; yazılmış değişiklikleri de gösterir. Metin araması liste toplamını değiştirmez.

## Arama ve kaydetme

Küpe, ad veya padok araması anında çalışır. Aramayla görünmeyen hayvanların yazılmış değerleri saklanır; aramayı temizleyince geri gelir. Arama kutusunda Enter sayfayı yenilemez. Süt alanında Enter bir sonraki görünür girişe, son alanda kaydetme düğmesine geçirir.

Alt çubukta değiştirilen hayvan sayısı ve **N Hayvanı Kaydet** görünür. Yalnız bu hayvanlar mevcut `/milk-center` kaydetme yoluna gönderilir. Değiştirilmemiş hayvanların mevcut kalite, not ve süt kayıtları yeniden yazılmaz. Aramayla gizlenmiş değiştirilmiş hayvanlar da sayı ve kayda dahildir.

Mevcut bir kaydın hem Sabah hem Akşam değerlerini temizleyip kaydetmek o günün değerini sıfıra çeker. Kaydetme, günün mevcut kaydını günceller; aynı güne ek bir kayıt oluşturmaz. Değişiklik yokken düğme pasiftir; gönderim sırasında yeniden tıklama engellenir.

Durum grubunu değiştirip Listele'ye basıldığında kaydedilmemiş giriş varsa önce uyarı çıkar. Vazgeçmek yazılanları korur. Sayfadan ayrılma uyarısı tarayıcının desteklediği standart uyarıdır.

## Kurulum

Tam ZIP kaynaklarını GitHub deposuna aktarın ve mevcut Windows kurulum iş akışını çalıştırın. Çıktı adı `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_40_Setup.exe` olur. Bu paket hazır EXE içermez.

Yeni `app/mobile_assets/milk-entry.css` ve `milk-entry.js` dosyalarını da aktarın. Mevcut veri klasörünü koruyun; bu değişiklik için veritabanı şeması veya veri taşıma işlemi eklenmedi. 2.0.39 toplu finans görünümü, rasyon yazdırma ve aktif hayvan raporu dahil önceki düzeltmeler pakettedir.
