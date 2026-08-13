ÇiftlikPro Enterprise V3.7.4
================================
Windows üzerinde çalışan yerel web tabanlı çiftlik ve sürü yönetim uygulaması.

Güncel öne çıkan özellikler:
- Hayvan, buzağı, tohumlama, kızgınlık, sağlık, finans ve besi performansı takibi
- Kişiselleştirilebilir Dashboard
- Türkçe GG/AA/YYYY tarih gösterimi
- Mobil ve ağ erişimi
- Yedekleme / geri yükleme
- Cihaza bağlı, dijital imzalı CFP lisans anahtarı aktivasyonu
- Yönetim ekranında lisans test etme ve lisans değiştirme

Kaynak paket, GitHub Actions + PyInstaller + Inno Setup ile Windows kurulum EXE'si üretmek için hazırlanmıştır.

ÇİFTLİKPRO ENTERPRISE — KAYNAK KOD V1.0
=======================================

Bu paket .exe, .bat veya .vbs içermez.
Haricî Python paketi ve pip gerektirmez.

ÇALIŞTIRMA
----------
1. ZIP dosyasını yeni bir klasöre çıkarın.
2. Klasörün içinde Komut İstemi veya PowerShell açın.
3. Şunu çalıştırın:

   python server.py

4. Tarayıcıdan açın:

   http://127.0.0.1:8935/login

GİRİŞ
-----
Kullanıcı adı: admin
Şifre: admin123

AĞDAN ERİŞİM
------------
Program açıldığında konsolda yerel ağ adresini gösterir.
Aynı Wi-Fi üzerindeki telefon/tablet bu adresi kullanabilir.

BİRLEŞİK MODÜLLER
-----------------
- Profesyonel dashboard
- Sabit üst menü ve ana navigasyon
- Dişi hayvan yönetimi
- Erkek hayvan yönetimi
- Ayrıntılı ve tıklanabilir hayvan kartları
- Hayvan bilgilerini düzenleme
- Fotoğraf yükleme ve fotoğraf galerisi
- Mobil tarayıcıdan kamerayla fotoğraf çekme
- Kilo kayıtları
- Süt verimi kayıtları
- 3 tohumlama kaydı
- Gebelik sonucu ve 280 günlük tahmini doğum
- Buzağı ekleme, düzenleme ve tıklanabilir detay kartı
- 10 ayını dolduran dişi buzağıların dişi hayvanlara geçişi
- 10 ayını dolduran erkek buzağıların erkek hayvanlara geçişi
- Sağlık, aşı, ilaç ve maliyet kayıtları
- Gelir/gider ekleme
- Hayvanla ilişkilendirilmiş finans kayıtları
- Tarih aralıklı finans raporları
- CSV rapor indirme
- JSON içe/dışa aktarma
- SQLite yedekleme
- Günlük otomatik yedek
- Mobil uyumlu görünüm

VERİ TAŞIMA
-----------
Önceki sürümlerin ciftlik.db dosyasını doğrudan kopyalamayın; şemalar farklı olabilir.
En güvenli yöntem:
1. Önceki sürümden JSON dışa aktarın.
2. Bu sürümde Veri Aktarımı > JSON'dan İçe Aktar bölümünü kullanın.
3. Çakışan küpelerde önce "Atla" seçeneğini tercih edin.

DOSYALAR
--------
server.py          Uygulamanın açık kaynak kodu
ciftlik.db         İlk çalıştırmada otomatik oluşur
uploads/           Hayvan fotoğrafları
backups/           Veritabanı yedekleri
FEATURES.md        Korunması gereken özellik kontrol listesi
TEST_REPORT.txt    Bu pakette yapılan otomatik testlerin özeti

PROGRAMI KAPATMA
----------------
Komut penceresinde Ctrl+C tuşlarına basın.

GÜVENLİK
--------
Bu sürüm yerel ağ içindir. Modemden port açarak doğrudan internete yayınlamayın.

V1.0.1 Sabit Menü Güncellemesi
------------------------------
- Yalnızca arayüz yerleşimi değiştirildi.
- Sol menü masaüstünde sayfa kaydırılırken sabit kalır.
- Üst çubuk sabit kalır.
- Ana içerik alanı bağımsız olarak aşağı kayar.
- Mobil görünümde menü yatay ve kaydırılabilir kalır.
- Hiçbir modül, veri tabanı tablosu veya işlev değiştirilmedi.


V1.1 Finans–Hayvan Durumu Entegrasyonu
--------------------------------------
- Hayvan Satışı finans kaydı seçilen hayvanı Satıldı durumuna geçirir.
- Kesim Geliri finans kaydı seçilen hayvanı Kesildi durumuna geçirir.
- Satılan/kesilen hayvanlar aktif listelerden ve dashboard sayılarından düşer.
- Fotoğraf, süt, kilo, sağlık, tohumlama ve finans geçmişi korunur.
- Satılan Hayvanlar ve Kesilen Hayvanlar arşiv ekranları eklendi.


V1.1.1 Arşiv Düzeltmesi
-----------------------
- Eski V1.0.1 ciftlik.db dosyaları açılışta otomatik yükseltilir.
- exit_date, exit_reason ve animal_status_action alanları eksikse oluşturulur.
- Satılan Hayvanlar ve Kesilen Hayvanlar ekranları düzeltildi.


V1.1.3 Güncellemeleri
---------------------
- Finans kayıtlarına Düzenle ve Sil seçenekleri eklendi.
- Satış/kesim kaydı değiştirildiğinde hayvan durumu yeniden hesaplanır.
- Satış/kesim kaydı silindiğinde başka geçerli kayıt yoksa hayvan tekrar Aktif olur.
- Tohumlama ekranında gebe hayvanlar yeşil renkle ve Gebe rozetiyle gösterilir.


V1.1.4 Gebelik Rengi Düzeltmesi
-------------------------------
- Pozitif, Gebe, Evet, True, 1, Olumlu ve benzeri gebelik değerleri tanınır.
- Gebe satırın yeşil rengi tablo çizgileri ve fareyle üzerine gelme stilinden etkilenmez.
- Sonuç alanında yeşil Gebe rozeti kesin olarak gösterilir.


V1.2.1 Dashboard Hayvan Ekleme
------------------------------
- Dişi Hayvanlar ekranındaki ekleme formu kaldırıldı.
- Dişi Hayvanlar ekranında küpe/takma ad araması ve tarayıcı öneri listesi bulunur.
- Dashboard'a tek Hayvan Ekle formu eklendi.
- Dişi kayıtlar Dişi Hayvanlar'a, erkek kayıtlar Erkek Hayvanlar'a, buzağı kayıtları Buzağılar'a yönlendirilir.


V1.2.2 Hayvan Ekle Butonu Düzeltmesi
------------------------------------
- Dashboard'daki eski /animals yönlendirmesi kaldırıldı.
- Hayvan Ekle butonu artık Dashboard'daki kayıt kartını açar.
- Dişi Hayvanlar sayfasına yanlış yönlendirme giderildi.


V1.2.3 Merkezi Hayvan Ekleme
----------------------------
- Sol menüye Hayvan Ekle bağlantısı eklendi.
- Dashboard'daki eski Hayvan Ekle ve Buzağı Ekle düğmeleri kaldırıldı.
- Merkezi Hayvan Ekle sayfası oluşturuldu.
- Dişi, Erkek ve Buzağılar sayfalarında yalnızca arama ve liste bulunur.
- Kayıt türüne göre doğru listeye otomatik yönlendirme korunur.


V1.3.1 Arama ve Form Düzeltmesi
-------------------------------
- Canlı aramalar sayfa tamamen yüklendikten sonra başlatılır.
- Hayvan Ekle formundaki f değişkeni hatası giderildi.
- Hayvan ekleme işlemi uçtan uca test edildi.
