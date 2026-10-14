# MobileAPI17 — Fotoğraf Görüntüleme Birliği

Sürüm: 3.9.23 DEV4 Hotfix1.22cr

- Hayvan detayında kayıtlı profil fotoğrafı yeniden görünür.
- Detaydaki fotoğrafa dokununca lightbox/büyük önizleme açılır.
- Fotoğrafı olan hayvanda hızlı işlem `Fotoğrafı Gör`; değiştirme ayrı `Değiştir` eylemidir.
- Fotoğrafı olmayan hayvanda `Fotoğraf Ekle` gösterilir.
- Hayvan listesi, padok ve arşivdeki küçük fotoğraflar büyütme davranışını korur.
- Fotoğraf ekleme formu aynı anda yalnız bir kez açılabilir; art arda dokunmada ikinci/üçüncü form üretilmez.
- Yetişkin ve buzağı detay API'leri profil fotoğrafını en güncel fotoğraf tablosundan alır; eski `photo_url` alanı fallback olarak korunur.
- API16 doğum/arşiv, API15 alış-finans, maliyet, sağlık ve üreme akışları korunur.
