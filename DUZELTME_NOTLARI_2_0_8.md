# App Edition 2.0.8 — 15/10/2026 Dashboard performansı

Temel: AppEdition 2.0.7 tam paketi. Normal giriş adresi ve 8953 portu aynıdır. 2.0.7 rasyon/rapor düzenlemeleri dahildir.

Dashboard'da yavaş çalışan tartım, gebelik ve stok sorgularına indeks desteği eklenmiştir. Aynı açılışta birden fazla çağrılan gebelik ve sağlık hesaplarının sonucu yalnız o istek içinde paylaşılır. Sonraki açılış taze veri okur; doğum, aşı ve ödeme sonrası veriler süreli bir sayfa önbelleğinde tutulmaz.

600 yetişkin hayvan, 12.000 tartım ve 90.000 stok hareketi içeren yerel testte tek istek ortancası 0,662 saniyeden 0,120 saniyeye; dört eşzamanlı istemcinin ortancası 1,817 saniyeden 0,726 saniyeye düştü. Bunlar aynı test ortamındaki HTTP yanıt süreleridir; kullanıcının Windows bilgisayarı, gerçek veritabanı veya tarayıcı açılış süresi değildir.

Eski `[PERF] Dashboard hazır` satırı Dashboard gövdesi hesaplanınca yazılır. Bir saniyeyi aşan isteklerde yeni `[PERF] Dashboard sunucu yanıtı` satırı bakım, sunum ve sıkıştırma dahil sunucu süresini verir. Bu satırlar hata kaydı değildir.

Paket kaynak kod ve GitHub Windows EXE üretim akışını içerir. Hazır EXE/APK/IPA içermez. Kontroller ve ortam sınırları `DOGRULAMA_APP_EDITION_2_0.md` içindedir.
