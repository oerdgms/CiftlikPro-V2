# ÇiftlikPro Enterprise — App Edition 2.0.39

26/10/2026 · Temel: 2.0.38 tam kaynak paketi.

## Finansta toplu sağlık görünümü

Toplu aşı / parazit / vitamin / tedavi uygulamaları, mobil ve masaüstü Finans listesinde aynı program ve uygulama grubuna ait tek satır olarak görünür. Örneğin hayvan başına 100 TL'lik 67 aşı için **Şap Aşısı · 67 hayvan · ₺6.700,00** gösterilir. Hastalık kaydının hayvanlara dağıtılmış giderleri de ilgili hastalık kaydı altında gruplanır.

1. Finans'ta işlem adına veya **Dağılımı gör** bağlantısına tıklayın.
2. Toplam gider, hayvan sayısı ve hayvan başına dağılımı görün.
3. Küpe, ad veya padokla dağılım içindeki hayvanı arayın. Bu arama üstteki işlem toplamını değiştirmez.
4. **Sağlık kaydı** bağlantısından ilgili hayvanın kaydını açın. Burada tutar değişirse hayvanın gideri ve grup toplamı birlikte güncellenir.
5. **Finansa dön** ile aynı filtrelere dönün.

## Mevcut kayıtlar ve hesaplar

Mevcut 67 ayrı gider, sağlık programı / görev bağlantıları bulunduğunda otomatik olarak tek görünür işlem altında toplanır. Yeniden aşı veya finans kaydı girmeniz gerekmez. Hayvanların ayrı gider payları tutulmaya devam eder; raporlardaki toplam gider, hayvan maliyetleri ve ayrıntılı finans CSV çıktısı aynı kayıtları kullanır. Bu sürüm yeni gider veya veritabanı tablosu oluşturmaz.

Yalnız isim veya tarih benzerliği gruplama için yeterli değildir. Program / görev veya hastalık bağlantısı olmayan serbest giderler ayrı görünür. Farklı programlar, dozlar, günlük uygulamalar, dönemler, tarihler, açıklamalar veya ödeme koşulları ayrı tutulur. Belirsiz / çakışan sağlık bağlantıları otomatik gruba alınmaz.

Finans'ın ana araması önce kayıtları süzer. Örneğin bir küpe arandığında yalnız o hayvanın eşleşen gideri gösterilir; üst finans toplamları da seçilen filtreye uyar. İşlem ayrıntısındaki arama ise yalnız o işlemin hayvan dağılımını süzer.

Sayfalama gruplama sonrasında yapılır. **1 işlem · 67 kayıt** ifadesi tek görünür sağlık işlemi altında 67 ayrı hayvan gideri bulunduğunu belirtir. Tarih / tür / kategori / ödeme filtreleri, yem faturası önizlemesi ve diğer finans işlemleri kullanılmaya devam eder.

## Kurulum

1. ZIP içeriğinin tamamını GitHub kaynaklarına aktarın. Yeni `app/finance_groups.py`, `finance-groups.css`, `finance-groups.js` ve tests klasörü dahil olmalıdır.
2. Actions → CiftlikPro Windows Kurulum → Run workflow.
3. `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_39_Setup.exe` dosyasını kurun.
4. Mevcut masaüstü / telefon adresini yeniden açın ve Finans'a girin.

ZIP tam kaynak / kurulum projesidir; hazır Windows EXE içermez. 2.0.38 rasyon yazdırma / hayvan raporu ve 2.0.37 toplu sağlık / rapel özellikleri dahildir.
