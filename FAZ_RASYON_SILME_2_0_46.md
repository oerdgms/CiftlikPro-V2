# Hazır Faz Rasyonları – 2.0.46

Rasyonlar ekranından Faz 1, 2, 3 ve 4 diğer rasyonlar gibi Sil düğmesiyle kaldırılabilir. Eski başlangıç kodu adı bulunmayan hazır rasyonları yeniden ekleyebiliyor ve belirli hazır notları taşıyan rasyonların miktarlarını yeniden yazabiliyordu. Başlangıç reçetelerinin oluşturulma durumu artık ayrı kaydedilir. Silinenler yeniden başlatmada dönmez; adını veya miktarlarını değiştirdiğiniz rasyonlar korunur.

Mevcut veritabanına ilk geçişte mevcut reçeteler aynen benimsenir; bulunmayanlar silinmiş/istenmemiş kabul edilip eklenmez. Boş ve yeni kurulumda dört reçete yalnız bir kez oluşturulur. Sadece bu düzeltme için yeniden kurulum veya veri temizleme gerekmez.

Aktif padokta kullanılan rasyon önce padok ataması kaldırılmadan silinmez. Geçmiş padok ataması bulunan rasyon listeden kaldırılırken arşivlenir; eski maliyet ve tüketim ilişkileri korunur. Bu kontrolleri aşarak silme yapılmaz.

Önce uygulamadan yedek alın. Kaynak sunucusunu kapatıp yeni paketi ayrı klasöre çıkarın, mevcut veri klasörünü koruyarak kaynaktan çalıştırın. EXE oluşturulmadı. 2.0.45 KM yüzdesi ve protein düzeltmeleri dahildir.
