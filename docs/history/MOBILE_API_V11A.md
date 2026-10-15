# MobileAPI11a – Fotoğraf/Kamera düzeltmesi

- Hayvan Düzenle ekranına ayrı **Fotoğraf Çek** ve **Galeriden Seç** eylemleri eklendi.
- iPhone/Android arka kamera için `capture="environment"` kullanıldı.
- Seçilen/çekilen fotoğraf yüklemeden önce önizleniyor.
- Mevcut fotoğraf Düzenle ekranında gösteriliyor; dokununca tam boy açılıyor.
- Küçük mobil ekranlarda Düzenle formu tek sütuna geçerek doğum tarihi/padok çakışmasını önlüyor.
- Mevcut `/api/v1/photo` yükleme ve masaüstü `animal_photos` veri yapısı korunuyor.
