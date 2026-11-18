# 2.0.87 — Windows test süresi ve tanılama

35 dakika 5 saniyede iptal edilen çalışmada regresyon testleri 34 dakika 26 saniye sürmüş, EXE aşamasına geçilmemiştir. Paylaşılan son satırlar hangi testin beklediğini göstermediğinden Windows darboğazı henüz kesinleşmemiştir.

- Tam test keşfi korunur; testler atlanmaz ve başarısızlık derlemeyi durdurur.
- scripts/run_regression.py yalnız işletim sisteminin geçici dizini altındaki test SQLite bağlantılarında synchronous=OFF kullanır. Transaction, rollback ve kısıtlar korunur; bu testler elektrik kesilmesi dayanıklılığı ölçmez. --durable-db ile normal disk eşitlemesi kullanılabilir.
- Uygulama ve paketlenmiş EXE bu test betiğini yüklemez. Kullanıcı veritabanı ayarlarında değişiklik yoktur.
- Her testin adı ve süresi anında yazılır. Bir test 120 saniye sürerse tüm thread izleri yazılır.
- Testler bittiğinde test-timings.json ve en yavaş 20 test listesi üretilir; GitHub bu raporu ayrı artifact olarak yükler.
- Job sınırı 60 dakika, regresyon adımı 45 dakika. Bu süreler hız garantisi değildir; yalnız erken iptali önler.

Windows runner ve Windows kurulum EXE sonucu GitHub üzerinde doğrulanmalıdır.

Doğrulama: 573 testin tamamı geçti. Geçici dosya sınırı, synchronous ayarı, rollback, normal disk modu ve başarısız testte çıkış kodu 1 ayrıca doğrulandı.
