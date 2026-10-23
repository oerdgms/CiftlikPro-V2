# ÇiftlikPro App Edition 2.0.21 — Referans Mobil Tasarım

Temel paket: AppEdition 2.0.20n Mobile Science Above Targets.

## Uygulanan tasarım

1. Koyu yeşil ve ortalanmış ÇiftlikPro ana başlığı; diğer ekranlarda açık başlık.
2. Sürü Özeti: Genel, Sağmal, Kuru, Buzağı, Düve, Kızgın; üç sütun ve iki satır.
3. Yaklaşan işler: ana sayfada ilk üç iş; Tümü ile filtrelenebilir görev ekranı. Mevcut sağlık görevleri ve vadeli ödemeler kendi gerçek bağlantılarını kullanır.
4. Kullanıcı baş harfli sol menü; gerçek lisans bitişi; tüm mevcut modüller; çıkış.
5. Fotoğraflı hayvan listesi; sunucunun tüm kayıtlarında arama, durum ve padok/tür filtresi, artan/azalan sıralama, sayfalama. Düzenle bağlantısı her satırda bulunur.
6. Yeni hayvan/buzağı formu: mevcut alanlar tekrar kullanılmaktadır. Cinsiyet, amaç ve geliş seçimi asıl kayıt alanlarıyla eşlenir. Anne-baba, geliş, alış, sağlık ve fotoğraflar açılır gruplardadır.
7. Hayvan detayı: fotoğraf, kimlik ve üçlü özet; dört sütunlu hızlı işlem alanı; gerçek kayıtlardan yaşam döngüsü.
8. Genel, Üreme, Sağlık, Rasyon, Süt/Kilo, Finans, Fotoğraflar ve Geçmiş sekmeleri. Erkek/buzağıda uygun sekmeler gösterilir. Sekme seçilince içerik başlığın altında açılır; üst geri düğmesi özete döner.
9. Sağlık, gebelik, rasyon/padok ve finans bilgilerinde Enterprise yardımcıları esas alınır. Net kâr aynı gider ve maliyet hesabını kullanır.
10. Fotoğraf galerisi iki sütunludur; özgün yükleme formu ve büyütme davranışı korunur.
11. Sağlık Kaydı hayvanı önceden seçer. Padok Ata doğru hayvanı işaretler. Doğum Ekle anne ve buzağı türünü hazırlar. Tartım, süt, satış/zayiat, düzenle/sil ve çıktı işlemleri mevcut kayıtlara gider.
12. Modüller ekranı üç sütunludur. Süt, tarım, ilaç/veteriner, arşiv ve veri/yedekleme ek erişimlerde korunmuştur.

## Sınırlar ve uyumluluk

- Tasarım 900 piksel ve altına uygulanır. Masaüstünde mevcut Enterprise içerikleri kullanılır.
- Aynı veritabanı, lisans kontrolü, oturum ve kayıt yolları kullanılır; ek veritabanı veya örnek çiftlik verisi kurulmaz.
- Sensör/pedometre ve bireysel tüketim ölçümü gibi kaynakta bulunmayan bilgiler üretilmez.
- Süt/doğum kayıtları ve kuruya çıkarma tarihi sürü sınıflandırmasını belirler. Son 30 günün süt kaydı veya son 305 günün doğum kaydı sağmal sınıfı için kullanılır; kuruya çıkarılmış hayvan bu gruba girmez. Doğum ve süt kaydı bulunmayan yetişkin dişi düve olarak sınıflanır.
- ÇiftlikPro çekirdeği 3.9.23 DEV4 Hotfix1.22cr olarak korunur. Mobil yapı ve önbellek kimliği 2.0.21 olarak eşitlenmiştir.
- 2.0.20n bilimsel hedef paneli ve rasyon çözümleyici korunmuştur.
