# 2.0.91 — Fotoğraf bağlantı iptali ve stok okuma maliyeti

## Değişiklik

- Fotoğraf gövdesi gönderilirken Windows ConnectionAbortedError oluşması, BrokenPipeError ve ConnectionResetError gibi beklenen bağlantı kesintisi olarak işlenir. İkinci HTTP yanıtı denenmez. Hem GET hem POST sınırında uygulanır.
- Bu düzenleme kesintinin fiziksel/ağ kaynağını ortadan kaldırdığını iddia etmez. Antivirüs veya ağ engeli bulunduğu bu logdan kanıtlanamaz; güvenlik yazılımlarını kapatmak gerekmez.
- Stok eşitlemesinde aktif padok nüfusu ve bağlı stok hareketleri toplu okunur. Ortak tarif aynı çağrı içinde bir kere okunur. Gün, işletme veya istekler arasında sonuç önbelleği kullanılmaz.
- Aynı gün nüfus veya rasyon değişimi, bozuk stok bağlantısının onarılması ve iptal edilen otomatik hareketlerin kaldırılması korunur. Manuel hareketler korunur. Veritabanı dayanıklılık ayarları değiştirilmez.

## Ölçüm

18/11/2026 tarihli kullanıcı yedeğinin değiştirilmemiş verileri bellek kopyasına alınarak aynı gün eşitleme karşılaştırıldı. Önce: 237 SQL execute çağrısı, yaklaşık 0,013 sn. Sonra: 10 çağrı, yaklaşık 0,009 sn. Her iki sonuç: created=0, updated=0, removed=0, quantity_kg=1252.28. Ölçüm bu Linux ortamındaki bellek kopyasınadır; kullanıcının Windows cihazında 1–1,6 saniyelik stok aşamasının aynı oranda hızlanacağı garanti edilmez.

## Doğrulama

İlk 20 hedefli test geçti. Kesilen fotoğraf gövdesi (aborted/reset/broken pipe), sonraki isteğin başarıyla dönmesi, gerçek fotoğraf hatasının hâlâ HTTP 500 ve log üretmesi, fotoğraf önbelleği ve yetkilendirme, değişmeyen stokta yazmama, nüfus değişikliği ve elle değiştirilen tüketimin onarılması kontrol edildi. Tam regresyon taraması: 584 testin tamamı geçti (349.778 sn). Güçlendirilmiş toplu okuma testi de tam taramada geçti.

Windows EXE derlemesi ve fiziksel iOS/Android cihaz testi bu ortamda yapılmadı.
