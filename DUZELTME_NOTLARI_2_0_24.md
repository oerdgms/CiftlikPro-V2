# ÇiftlikPro App Edition 2.0.24 — Mobil Sekme Kaydırma Düzeltmesi

22/10/2026. Temel paket: App Edition 2.0.23 Masaüstü / Mobil Bütünlük.

Hayvan ve buzağı detayındaki Genel, Üreme, Sağlık, Rasyon, Süt/Kilo ve diğer sekmelerin kaydırma sırasında titremesine karşı sabitleme düzeni değiştirildi.

- Sekme şeridi doğal yerinde gösterilir; üst başlığa ulaştığında aynı sabit başlığın içine alınır. İçerik içinde ayrıca sticky katman olarak çalışmaz.
- Şeridin içerikteki yüksekliği korunur. Sabitleme sınırı, şeridin taşınmasıyla değişmez; içerik aşağı/yukarı sıçramaz.
- Sınır geçişi IntersectionObserver ile izlenir. Her kaydırma karesinde üst konum/yükseklik yeniden yazılmaz.
- Odaklanmış sekmelerin negatif üst marjı kaldırıldı. Başlık yüksekliği veya ekran boyutu değişince hizalama yenilenir.
- Yatay sekme kaydırması ve seçili sekmenin görünür alana gelmesi devam eder. Başlığa taşınan sekmelerin tıklama işlemleri aynı düğmelerle çalışır.
- Üst geri düğmesi özete döner; sekme şeridi doğal yerini geri alır. Masaüstü görünümü değişmez.

2.0.23'teki manuel laktasyon, masaüstü sürü özeti/filtreleri, Ana Sayfa Düzeni ve 14 modül bu tam pakette korunmuştur. Kayıt, finans, stok veya rasyon işlemlerinin mantığı değiştirilmemiştir. Yeni veritabanı değişikliği yoktur.

Yapı/varlık/önbellek ve Windows kurulum kimliği 2.0.24'tür. Çekirdek sürüm 3.9.23 DEV4 Hotfix1.22cr olarak korunur. Bu ZIP tam kaynak/kurulum projesidir; Windows EXE mevcut GitHub Actions akışıyla oluşturulur.
