# ÇiftlikPro Mobile API v1 — Aşama 1

Bu geliştirme dalı mevcut 1.22ci yapısını koruyarak mobil istemciler için salt-okunur API ekler.

## Güvenlik
- API, mevcut aktif ÇiftlikPro lisansını doğrular.
- Giriş mevcut `users` hesabıyla yapılır.
- Başarılı mobil girişte 30 gün geçerli rastgele Bearer token üretilir.
- Token'ın kendisi veritabanında tutulmaz; yalnız SHA-256 özeti saklanır.
- Çıkış token'ı iptal eder.
- İlk aşama salt-okunurdur; veri değiştiren diğer API POST çağrıları reddedilir.

## Uçlar
- `GET /api/v1/status` — API ve uygulama sürümü (giriş gerektirmez)
- `POST /api/v1/login` — kullanıcı girişi
- `POST /api/v1/logout` — mobil oturumu kapat
- `GET /api/v1/me` — oturum kullanıcısı
- `GET /api/v1/animals?q=&status=Aktif&limit=100` — hayvan listesi
- `GET /api/v1/animals/<id>` — hayvan + son sağlık + üreme geçmişi
- `GET /api/v1/paddocks` — aktif padoklar ve aktif hayvan sayısı
- `GET /api/v1/tasks?filter=all|today|overdue|upcoming&q=` — sağlık/görev planı
- `GET /api/v1/health?limit=100` — sağlık kayıtları
- `GET /api/v1/reproduction` — tohumlama/gebelik kayıtları

## Örnek giriş gövdesi
```json
{"username":"admin","password":"...","device_name":"Osman iPhone"}
```

Sonraki çağrılarda `Authorization: Bearer <token>` başlığı kullanılır.

## Aşama 2 önerisi
Mobil istemci prototipi; ardından yetki matrisi ve güvenli yazma uçları (görev tamamlama, sağlık/aşı, tartım, üreme). Çevrimdışı kuyruk bundan sonra eklenmelidir.
