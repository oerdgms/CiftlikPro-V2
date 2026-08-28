# ÇiftlikPro v3.9.20 — Saha Test Paketi

Bu paket güncel Solver DEV4.x mantığını korur. Son düzeltmeler yalnız arayüz ve GitHub paket yapısındadır:

- Mobil rasyon görünümü korunmuştur.
- İşlevsiz “Hedef Bilgilerini Göster/Gizle” düğmesi kaldırılmıştır.
- Masaüstünde 🐄 ÇiftlikPro logosu sol menüde Dashboard satırının hemen üzerinde görünür konuma sabitlenmiştir.
- `.github/workflows/windows-installer.yml` dahildir.
- Solver hesap/optimizasyon mantığı değiştirilmemiştir.

# ÇiftlikPro v3.9.20 — Solver DEV4

Bu geliştirme sürümü, besi rasyonu solverında **canlı ağırlık → besi dönemi → faz kaba/kesif koridoru → rumen güvenliği → besin hedefleri → kalite/maliyet** sırasını uygular.

## Faz standardı (KM bazında)

- **Besi Başlangıç:** 200–299 kg referansı, hedef yaklaşık **%50 kaba / %50 kesif** (solver koridoru %47–53 kaba).
- **Besi Geliştirme:** 300–449 kg, hedef yaklaşık **%40 kaba / %60 kesif** (solver koridoru %37–43 kaba).
- **Besi Bitirme:** 450 kg ve üzeri, yem kalitesi ve rumen güvenliğine göre **%30–40 kaba / %60–70 kesif**, merkez hedef %35/%65.

Saman zorunlu değildir. Kaliteli kaba yem (yonca, silaj, uygun kuru ot) kaba yem hedefini ve eNDF ihtiyacını karşılayabiliyorsa saman 0 olabilir. Solver düşük kaliteli kaba yemi yalnız ucuz olduğu için yükseltmemeye devam eder.

## DEV4 test planı

Aynı yem havuzuyla 250 kg, 350 kg ve 500 kg canlı ağırlıkta çözüm alın. Kaba/kesif oranı, eNDF, rumen pH, KM, HP, ME, Ca/P ve yem dağılımını karşılaştırın.

Ana program sürümü değişmedi: **v3.9.20**.


## v3.9.20 Solver DEV4.1 saha paketi
- Eski `🐄 ÇiftlikPro` marka yazısı korunur; masaüstü sol menüde ayrılan başlık kutusunda yatay ve dikey merkezlenir.
- Besi dönemi varsayılan olarak canlı ağırlıktan otomatik seçilir: <300 kg Başlangıç, 300–449 kg Geliştirme, 450+ kg Bitirme.
- İstenirse Rasyon Çöz ve hedef düzenleme ekranından Besi Başlangıç / Geliştirme / Bitirme manuel seçilebilir.
- KM bazında kaba/kesif koridorları: Başlangıç %47–53 kaba (merkez %50), Geliştirme %37–43 (merkez %40), Bitirme %30–40 (merkez %35).
- Ca/P hedef üstü cezası güçlendirildi; makro hedefleri korurken mineral taşmasını azaltmaya öncelik verir.
- GitHub Actions `windows-installer.yml` pakette korunmuştur. Kurulum EXE'si GitHub Actions artifact olarak üretilebilir.

### DEV4.9 saha UI notu
Bu paket DEV4.8 solver davranışını aynen korur. Değişiklik yalnız masaüstü sidebar logo konumu ve mobildeki işlevsiz hedef göster/gizle düğmesinin kaldırılmasıdır.

## DEV4.10 rapor ve hayvan aktarımı

- Tüm Hayvanlar raporu mobilde sıkışık geniş tablo yerine okunaklı hayvan kartları olarak gösterilir; web önizlemede de telefona özel kart düzeni ve doğrudan temiz PDF düğmesi bulunur.
- “Excel / PDF'den Hayvan İçe Aktar” alanı Raporlar sayfasının en üstündedir ve Veri Aktarımı sayfasında ayrıca belirgin bir kısayolu vardır.
- “Raporda Gösterilecek Sütunlar” seçimleri ekrandaki listeye, mobil kartlara, web önizlemeye, doğrudan PDF'ye ve Excel çıktısına birlikte uygulanır.
