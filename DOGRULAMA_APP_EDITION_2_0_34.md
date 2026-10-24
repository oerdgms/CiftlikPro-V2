# App Edition 2.0.34 — Doğrulama

24/10/2026

## Otomatik testler

- GitHub Actions ile aynı discovery komutunda 440 testin tamamı geçti; test atlanmadı. Gerçek QR / DataMatrix denemesi dahildir.
- Yeni altı test, hayvan / buzağı düzenleme formu, sabit TR alanı, boş / eksik / mükerrer küpe reddi, iki yönde bağlı kayıt eşitlemesi, kuruşlu alış tutarı ve eski özel küpe düzenlemesini doğrular.
- Önceki arama, arayüz eşitliği, sağlık, finans, rapor, üreme ve paketleme kontrolleri birlikte geçti.

## Arayüz ve kayıt denemeleri

- Chromium'da 320, 393, 430, 768 ve 1440 piksel genişliklerde veteriner hekim ve aşı / parazit / vitamin maliyet kutuları kontrol edildi. Alanlar taşmadı; tarih ve maliyet kutuları hizalı kaldı.
- Veteriner hekim alanı dar telefonda formun tam genişliğini kullandı. Maliyet alanları ondalık klavye istedi ve kuruş girişini korudu.
- Hayvan İşlemleri menüsü, Durum Ekle ile aynı panelde açıldı. Kimlik ve açıklamalı işlem satırları görüldü. Düzenleme menü içinden ve hızlı işlemden açıldı.
- Vazgeç ve Escape, değiştirilmiş formu kayıt yapmadan kapattı; odak önceki düğmeye döndü.
- Gerçek buzağı düzenleme formuyla TR küpesi, takma ad, kuruşlu alış fiyatı ve gerçek PNG fotoğraf yüklendi. Kayıt yeniden açılıp değerler ve fotoğraf doğrulandı.
- Yetişkin hayvan formu masaüstü penceresinden kaydedildi; yeni değer doğrudan düzenleme sayfasında doğrulandı.
- Normal sayfa adresleri 320, 393, 768 ve 1440 pikselde hayvan / buzağı için kontrol edildi. TR ön eki sabit kaldı; yatay taşma görülmedi.
- Aşı, parazit ve vitamin için gerçek uygulama kaydı oluşturuldu. `125,50`, `75.25` ve sıfır tutar kaydı, sağlık geçmişinde doğru kuruşlarla görüntülendi.
- Hastalık / tedavi kaydı veteriner hekim adı, veteriner maliyeti ve ilaç maliyetiyle kaydedildi. Tarayıcıda JavaScript sayfa hatası görülmedi.

- Ek panel denemelerinde İşletme Notu akışı not alanını odakladı; not kutusu sabit düğmelerin üzerinde görünür kaldı. TR alanının tek dış çerçeve kullandığı kontrol edildi.
- Arka plana tıklayarak kapatınca sayfanın kaydırma konumu korundu. Silme menüsü yalnız mevcut onay bölümünü açtı; hiçbir POST isteği gönderilmedi.

## Kaynak kapsamı

- Kayıt yazan App.do_POST içinde yalnız hayvan ve buzağı düzenleme küpelerini TR rakam alanından alma satırları değişti. Mükerrerlik, bağlı kayıt güncelleme, fotoğraf ve finans işlemleri aynı kaldı.
- Diğer çekirdek fonksiyonların kaynak özetleri 2.0.33a ile aynı kaldı; App özeti yeni düzenleme arayüzü ve küpe girişi için güncellendi.
- Sağlık defteri, maliyet hesaplama, senkronizasyon, sürü sayıları ve veritabanı şeması değiştirilmedi.
- Windows paketleme tanımına `animal_edit_ui` eklendi. Kaynak kontrolü yeni modülü derler; kaynak / EXE smoke adımları ortak arama dosyasını da denetler.

## Paket

- Çekirdek: `3.9.23 DEV4 Hotfix1.22cr`.
- App Edition: `AppEdition2.0.34-AnimalEditHealthForms`.
- Önbellek ve kurulum: `2.0.34`.
- Windows çıktı adı: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_34_Setup.exe`.

Kontroller geçici veritabanlarında ve yerel Chromium üzerinde yapıldı. Windows EXE bu ortamda derlenmedi; mevcut GitHub Actions akışından oluşturulur. Paket kullanıcı veritabanı, lisans, oturum, tarayıcı görüntüsü veya test fotoğrafı içermez.
