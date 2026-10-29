# App Edition 2.0.42 Mobil Pilot Hazırlık — 28/10/2026

## Temel ve kapsam

Kullanıcının stabil bildirdiği `2.0.41-Bugunun_Isleri_Dusuk_Cozunurluk_FULL` kaynakları esas alındı. Kaynak ZIP değişmeden saklanır. Bu paket 2.1 kararlı onayı veya APK/IPA değildir.

- `app/release_info.py`: çalışma zamanı, kaynak sürümü ve dağıtım kimliğinin tek kaynağı.
- `scripts/sync_release.py`: servis çalışanı önbelleği, Windows Setup/Actions adları ve RELEASE.json eşitlemesi; CI için salt okunur `--check`.
- Eski sunum modüllerinin HTML, CSS ve JS içinde ürettiği literal kaynak adresleri aynı sürüm anahtarına getirilir. Sürümü eski/yanlış anahtarlar değişmiş dosyayı kalıcı önbellek olarak almaz.
- `/app-build.json`: işletme kaydı/şifre/oturum içermeyen, no-store sürüm sorgusu. Kaynak ve Windows EXE smoke adımları bu cevabı RELEASE.json ile karşılaştırır.
- Bağlantı ekranı yeniden denemeyi 6 saniyeyle sınırlar; eski `/mobile-api/ping` ve `/mobile` geçişi yerine ilk istenen ekranı/filtreyi yeniler.
- Eski rasyon kartı kapsayıcısının `href` alanı yokken URL oluşturma hatası giderildi. İçteki gerçek bağlantı okunur; tasarım ve solver değişmez.

## Otomatik kontroller

Son test sayısı ve sonucu paketleme öncesi tam regresyon günlüğüyle doğrulanır. İlk geniş tarama 476/476 başarılıdır; ardından CSS içindeki görsel adresi için bir ek test dahil edilmiştir. Güncel son sonuç aşağıda belirtilir.

- Tam son regresyon: **477 test başarılı**.
- Sürüm/pilot hazırlığı testleri ayrıca **9/9 başarılı**.
- 2.0.41 temel mobil testleri değişiklik öncesinde **23/23 başarılı**.
- 13 sayfa × 5 genişlik (320/390/412/820/1366 px): **65/65 tarayıcı kontrolü başarılı**. Güncel build, kaynak sürümü, temel gezinme ve JavaScript hataları kontrol edildi.
- Gerçek Chromium servis çalışanında önce 2.0.41 örnek önbelleği kuruldu, ardından 2.0.42'ye yükseltildi; eski önbellek silindi. Giriş alanlarına yazılan kullanıcı adı/şifre, zorunlu sayfa yenilemesi olmadan korundu.
- Test sunucusunun bağlantısı kesildi; filtreli hayvan listesi adresinde çevrimdışı ekran açıldı. Yeniden deneme hata durumundan tekrar kullanılabilir hale geldi. Sunucu geri açılınca aynı `/all-animals?kind=calf` ekranına dönüldü.
- Yanıt vermeyen sürüm sorgusu tarayıcıda bekletildi; 6 saniyelik iptal sınırında düğmenin tekrar kullanılabilir olduğu ayrıca doğrulandı.
- Tarayıcı CacheStorage içeriğinde yalnız bağlantı sayfası ve iki simge vardı; işletme HTML'i/kayıtları yoktu. POST için çevrimdışı kuyruk eklenmedi.
- 2.0.41 ZIP ile karşılaştırmada sunucudaki **220 üst düzey fonksiyon/sınıf tanımı aynıdır**. Tüm CSS kaynakları ve mevcut iş kuralı modülleri birebir korunur. Sunucuda yalnız build kimliğinin importu değişmiştir.
- Sürüm eşitleme kontrolü ve JavaScript sözdizimi kontrolleri başarılıdır.

## Çalıştırılmayan ortamlar

Bu ortamda Windows Inno Setup/EXE kurulumunu, gerçek iPhone/Safari ve Android cihazlarını çalıştırmadık. Kaynak testlerinin geçmesi bu fiziksel cihaz onaylarını tamamlamaz. Windows Actions akışına kaynak ve paketlenmiş EXE sürüm sorgusu denetimleri eklenmiştir; ilgili Windows çalıştırmasının sonucu kullanıcı ortamında görülecektir.

Fiziksel cihaz ve LAN/VPN/HTTPS kontrol tablosu `MOBIL_PILOT_KONTROL.md` içindedir. Başarılı saha onaylarından sonra 2.1 kararlı adlandırması değerlendirilmelidir.
