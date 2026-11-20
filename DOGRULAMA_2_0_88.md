# 2.0.88 — Giriş formu ve buzağı kimliği

- Mobil giriş formu en fazla 280 px, masaüstü formu en fazla 320 px genişliğe sahip, kendi alanında yatay ortalıdır. İşletme, kullanıcı adı, şifre ve giriş düğmesi aynı form genişliğini kullanır.
- Doğum maliyeti seçeneği tüm buzağı kartlarında görünür. Önceki koşul yaş değil anne kaydının bulunmasıydı.
- Anne bağlantısı eksik buzağıda maliyet kaydedilir; kullanıcıya üretim katkısının anneye henüz yansımadığı bildirilir. Anne bağlantısı tamamlanınca katkı mevcut kayıttan hesaplanır; nakit gelir/gider oluşturulmaz.
- Tarih doğum tarihi olarak korunur; tekrar giriş aynı doğum maliyetini günceller.
- Mobil temel kimlik bilgilerindeki anne küpesi ilgili hayvan kartını açar; masaüstündeki mevcut anne bağlantısı korunur.
- 60 gün ve üzerinde ay/yıl gösteriminin yanına toplam yaş gün olarak eklenir. 60 günden küçüklerde doğrudan gün gösterilir. Geçersiz/gelecek doğum tarihi için yaş uydurulmaz.

Yeni kontroller: 60 günlük anne bağlantısız buzağı kaydı, sonradan anneye katkı, anne kartı bağlantısı, tekrar girişte tek maliyet, 44/59/60/731 gün ve geçersiz tarihler.

Doğrulama: yeni buzağı senaryolarının 4 testi geçti. 576 testlik genel taramada 574 test geçti; yetkili kaynak değişiklikleri için App/age_text özeti güncellendi ve eksik zxing-cpp test bağımlılığı kurulduktan sonra kalan iki kontrol ayrıca geçti. Sürüm eşleşmesi ve Python derleme kontrolleri geçti. Gerçek iPhone ve Windows EXE bu ortamda çalıştırılmadı.
