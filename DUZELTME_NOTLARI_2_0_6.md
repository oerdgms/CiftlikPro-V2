# App Edition 2.0.6 — 14/10/2026 toplu düzeltme notları

| Bildirilen madde | Paket sonucu |
|---|---|
| Masaüstü Bildirimler ana sayfayı açıyordu | Oturum/lisans korumalı bildirim listesi eklendi; üst ve mobil zil bağlantıları güncellendi. |
| Buzağı sağlık geçmişi yatay hareket ediyordu | Veriler mobilde başlığı ve alanları görünür kayıt kartlarına alındı. Buzağı kartında daha önce olmayan düzenle/sil işlemi eklenmedi; Sağlık Merkezi bağlantısı korundu. |
| İç üretim tarih/tür üst üste biniyordu | Mobilde form tek sütun; mevcut maliyete ekleme ve maliyet silme yolları korundu. |
| Mobil momentum kaydırması titriyordu | Sayfa scroll olayında konum zorlayan müdahale kaldırıldı, body ikinci scroll alanı oluşturmaz, alt menü blur işlemi kaldırıldı. Gerçek iPhone momentum doğrulaması kullanıcı cihazında yapılmalıdır. |
| Hayvan kartında çift dokunma zoom yapıyordu | CSS dokunma davranışı ve kısa çift dokunma koruması eklendi; sürükleme/form/düğme etkileşimi korunur. Safari cihaz doğrulaması gerekir. |
| İşletme ayrıntıları eski Dashboard'u açıyordu | Mobil ana sayfa artık işletme bilgileri ve ayarlar formuna bağlanır. |
| Gereksiz dosya/kod temizliği | Tarihi 42 belge arşive taşındı; kullanılmayan mobil genişletme kodu ve tekrarlı build ataması kaldırıldı. İşlevsel eski API'ler ve testler korundu. Derleme önbellekleri dağıtım dışıdır. |
| Mobil hız | HTML ve metin kaynaklarında gzip, sürümlü CSS/JS/giriş görselinde önbellek eklendi. Solver algoritması değişmedi. |
| Geçmiş sekmesi dişi hayvan satışını açıyordu | Geçmiş gerçek kayıtları gösterir; Satış / Zayiat ayrı sekmededir. |
| Fotoğraf galerisinde kutular düzensizdi | Dosya seçme, açıklama ve yükleme düğmesi masaüstünde hizalı; mobilde alt alta. |

Bu kaynak paketi aynı Enterprise veritabanı ve iş kurallarını kullanır. Hazır Windows EXE/APK/IPA içermez. Safari/iPhone momentum ve sistem yakınlaştırma davranışı Linux/Chromium testleriyle kesin olarak doğrulanamaz; bu iki madde için gerçek cihaz kontrolü gerekir.
