# AppEdition 2.0.55 — Doğrulama

31.10.2026. Temel sürüm 2.0.54.

## Kapsam

- ContextVar ile istek başına işletme veri yolları; DB, fotoğraf, yedek ve geçici geri yükleme yolları birlikte değişir. İlk işletme dosyaları taşınmaz.
- Ayrı işletme dizini ve kullanıcı erişim kayıtları; hesap kimliği/aktiflik/rol ilk veritabanından doğrulanır. Personelin ilk işletmeye eski erişimi korunur; ek işletmelerde açık izin gerekir. Yöneticiler bütün işletmelere erişir.
- HTML bağlantıları, form action ve submitter formaction adresleri, fotoğraf/önizleme adresleri ve AJAX istekleri işletmeye bağlanır. Formun eski bir sekmeden gönderilmesi seçili oturuma göre başka veritabanına yönlendirilmez.
- Kullanıcı yönetimi/giriş/şifre işlemleri ortak hesap deposunda çalışır. Yeni işletmelere hesaplar ortak kimlikleriyle eşitlenir.
- İçe aktarma önizlemeleri işletmeye ayrıdır. ZIP ve yeni JSON işletme kimliği taşır. Başka işletmeye ait kimlikli içeriğe geri yükleme/JSON aktarımı başlamaz.
- Açılış şema geçişleri ve günlük yedekler tanımlı işletmelerde ayrı yürür. Ortak özel yedek dizini işletme alt klasörlerine ayrılır.

## Sonuçlar

- Tam regresyon: 539 test / 305,126 saniye; tamamı başarılı. QR/DataMatrix için mevcut requirements bağımlılığı zxing-cpp 2.3.0 test ortamına kuruldu.
- İlk 536 test koşusunda 12 başarısızlık ve 1 hata vardı: URL işaretlemelerinin eski tek işletme çıktılarıyla uyumu ve önceki fotoğraf/rozet değişikliklerine ait eski beklentiler. Tek işletme davranışı etkinleştirme öncesinde korunarak ve üç eski görsel beklenti güncellenerek yukarıdaki son tam koşu geçti.
- Tam koşudan sonraki son JSON kimliği ve submitter formaction bağlama düzenlemelerinden sonra 14 çoklu işletme testi yeniden çalıştırıldı: 17,785 saniye, tamamı başarılı. Tam koşu bir kez daha tekrarlanmadı.
- Bu 14 test: ilk işletme dosya/record koruması, yeni işletmenin boşluğu, yolların geri dönmesi, HTTP oluşturma/geçiş, CSRF, personel yetkisi verme/kaldırma, eşzamanlı 18 sayfa isteği, eski sekmeden POST, aynı adlı fotoğraflar ve anonim erişim, form/AJAX/referer bağlama, yedek ayırma/aynı işletmeye geri yükleme/çapraz geri yükleme reddi, ortak şifre ve pasif hesap, önizleme ayrımı, API token kapsamı, finans POST ayrımı ve katalog/rasyon ayrımı, yeniden açılış ve tüm işletmelere günlük yedek, ortak özel yedek dizini, JSON kimliği ve çapraz aktarım reddi.
- Son Chromium kontrolü: 320 / 390 / 412 / 820 / 1366 px genişliklerde İşletmeler, hayvan listesi/kartı, Rasyon Çalışma Masası, Finans ve Yedekler — toplam 30 görünüm. İşletme alanı görünür ve yatay taşma yok. Yeni işletme oluşturma, oturum değiştirildikten sonra eski sekmeden profil kaydetme, AJAX ve Request nesnesiyle GET/POST, hesap doğrulama, ilk işletme hayvanlarının korunması ve JavaScript kapalı geçiş doğrulandı. JavaScript hatası yok.
- Enterprise çekirdek snapshot farkları yalnız ensure_archive_schema (veritabanına göre şema kontrolü) ve create_backup (manifest işletme kimliği). Rasyon, hayvan, finans ve stok hesaplarının kaynak snapshotları değişmedi.
- Sürüm eşitleme kontrolü, Python/JS sözdizimi ve ZIP CRC kontrolü tamamlandı.

Geçici/sentetik veriler kullanıldı. Kullanıcının çalışan veritabanına erişilmedi. Fiziksel iOS/Android ve Windows EXE testi yapılmadı; kaynak paket teslimidir.
