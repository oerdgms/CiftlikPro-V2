# ÇiftlikPro Mobile API3

MobileAPI3, gerçek telefon testindeki MobileAPI2 geri bildirimlerine göre hazırlanmıştır.

- Görevler artık `task / subject / detail / status / date` alanlarıyla gerçek işlem adı, hayvan/padok ve tarih gösterir.
- Tarihler mobil arayüzde DD/MM/YYYY gösterilir.
- Hayvan detayındaki ham JSON kaldırıldı; üreme zaman çizgisi, gebelik/TDT ve sağlık geçmişi kartlara dönüştürüldü.
- Padoklar kompakt kart görünümüne geçti; padoka dokununca o padoktaki aktif hayvanlar açılır.
- Üst başlık sadeleştirildi, alt navigasyon ve iOS safe-area davranışı iyileştirildi.
- API halen salt okunurdur; MobileAPI3 kayıt ekleme/düzenleme yapmaz.
