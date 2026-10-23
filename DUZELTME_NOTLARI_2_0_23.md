# ÇiftlikPro App Edition 2.0.23

22/10/2026. Temel: 2.0.22 Manuel Laktasyon / Erkek kartı.

## 1. Mobil ve masaüstü işlevleri

Yeni mobil durumların masaüstünde görünmemesi giderildi. Aynı kayıtlı manuel laktasyon, aynı sürü sınıflandırması ve aynı filtreleme/sayfalama seçimi her iki görünümde kullanılır. Masaüstüne altılı sürü özeti, yönetim bağlantıları, hayvan satırında durum rozetleri ve hayvan kartında laktasyon bilgi alanı eklendi. Sağmal filtresi tüm kayıtlar üzerinde sayfalama öncesi uygulanır; yalnız açık sayfanın satırları üzerinde çalışmaz.

Masaüstü hayvan listesinde görüntüle, düzenle, sil, arşiv, rapor, tür/padok/arama ve üç görünüm seçeneği korunur. İşlemler mevcut Enterprise uç noktalarına gider.

Süt & Laktasyon Merkezi her iki görünümde ortak ekran kullanır. Sağmal sayısı manuel seçili hayvanlardan gelir; varsayılan giriş listesi bu hayvanlardır. Tüm aktif dişiler, Kuru, Düve, Belirtilmedi ve Laktasyonda değil filtreleri mevcuttur. Sabah/akşam girişleri mevcut süt kayıt yolundan kaydedilir. Bugünkü toplam tüm aktif dişilerin gerçek süt toplamıdır; ilk iki KPI sayacı filtre seçimiyle yeniden tanımlanmaz.

Hayvan süt panelinde de manuel başlangıç esas alınır. Başlangıç bilinmiyorsa sağım günü, laktasyon toplamı ve 305 gün tahmini boş gösterilir. Girilmiş başlangıçtan önceki süt, yeni laktasyon toplamına katılmaz; gerçek gün ve 7/30 günlük girilmiş gün ortalamaları korunur. Kayıtlı süt/finans verisi yeniden yazılmaz.

## 2. Ana Sayfa Düzeni

İşletme ayarlarındaki eski Dashboard Düzeni bağlantısı çalışan Ana Sayfa Düzeni ekranını açar. Ana sayfanın altından da erişilir.

- Mobil bölümler: İşletme Bilgileri, Sürü Özeti, Yaklaşan İşlemler. Göster/gizle ve oklarla sıralama.
- Sürü kartları: Genel, Sağmal, Kuru, Buzağı, Düve, Erkek. Seçim ve sıra mobil/masaüstü özette ortaktır.
- Yaklaşan işlem satırı: 3, 5 veya 10. Tüm görevler ekranı bu sınıra tabi değildir.
- Düzeni Kaydet ve Varsayılana Dön. En az bir bölüm ve bir kart zorunludur.
- Ayarlar kullanıcıya özeldir, mevcut veritabanında kalıcıdır. Kullanıcılar birbirinin görünümünü değiştirmez.

Masaüstünün gelir/gider, canlı ağırlık, performans vb. diğer dashboard kartları eski masaüstü düzenleyicisinden yönetilmeye devam eder. Yeni düzenleyicide bu bağlantı bilgisayarda kullanılabilir. Mobilde eski /?edit=1 bağlantısı yeni düzenleyiciye yönlendirilir.

## 3. Modüller

Süt & Laktasyon, İlaç & Veteriner, Tarım Yönetimi, Hayvan Arşivi ve Veri & Yedekleme başlıkları ana kutucuk listesine alındı. Toplam 14 kutucuk, telefonda üç sütun; geniş masaüstünde dört sütun. Katlanır Diğer Modüller grubu kaldırıldı. /modules ve mevcut /?app_view=modules adresleri aynı ekranı açar.

## Paket

Yeni modüller: home_layout.py ve desktop_views.py. Yeni varlıklar: shared.css ve shared.js. PyInstaller ve GitHub Actions derleme/smoke listelerine eklendi. Çekirdek sürüm 3.9.23 DEV4 Hotfix1.22cr olarak korunur; uygulama yapısı 2.0.23'tür. Tam kaynak ZIP, Windows EXE dosyasını üretmek için mevcut Actions akışını içerir.
