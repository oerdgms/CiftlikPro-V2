# App Edition 2.0.30 — Doğrulama

## Sonuç

- 429 Python regresyon testi geçti. Tüm test modülleri dört bağımsız süreçte çalıştırıldı: 208 + 63 + 79 + 79.
- Sağlık merkezi için 17 yeni test: tekrarlı şema geçişi, geçmişi koruma, dört uygulama kategorisi, karma hayvan/buzağı seçimi, planın uygulama sayılmaması, mükerrer gönderim, gerçek tarihli rapel/tekrar, ay sonu hesabı, geçersiz kayıtların geri alınması, eski form sürümü, duraklatma/kaldırma, uygulamayı geri alma, gider düzenleme, hastalık tutar dağılımı, kaçışlama, eski kaynaklar, HTTP/oturum/CSRF, tedavi günü ve günlük uygulamalar, buzağı transferi, geçmiş görünümünde tekil kayıt ve PDF erişimi kapsandı.
- 320, 390, 768 ve 1322 piksel genişliklerde altı kategori: 24 tarayıcı görünümü kontrol edildi. Yatay taşma veya JavaScript sayfa hatası görülmedi.
- Gerçek mobil form akışları tarayıcıda çalıştırıldı: program oluşturma, uygulamayı tamamlama, gider düzenleme, uygulamayı geri alma, hasta kaydı, iyileşti işaretleme, çok günlük tedavi ve PDF indirme.
- 1440 ve 390 piksel görünümleri görsel olarak incelendi. Kayıt seçenekleri menüsünün genel `details` kuralıyla kesilmesi giderildi; tıklama akışı tekrar doğrulandı.
- Python derleme/sözdizimi ve yeni JavaScript sözdizimi kontrolleri geçti.
- Mevcut ajanda ve rasyon taslak JavaScript regresyonları geçti.

## Veri ve uyumluluk

Yeni merkez mevcut health / health_courses / health_tasks kayıtlarını kullanır. Ayrı bir hayvan veya finans kopyası oluşturulmaz. Hastalık bağlantıları ve programın tekrar/rapel ayarları yeni ek tablolarda tutulur. Yapılan uygulamalar mevcut sağlık geçmişine, ilgili gider mevcut finans tablosuna yazılır.

Programların hedefleri kimlik bazındadır. Padok değişimi hedef listesini değiştirmez. Buzağı transferinde görev ve hastalık bağlantısının hayvan kaydına taşınması eklenmiştir. Çekirdek kaynak denetimindeki yalnız bu aktarım işlevinin özeti güncellenmiştir; bunun için davranış testi vardır.

Eski sağlık kayıtları, gebelik aşıları, eski tekli/çoklu görevler ve senkronizasyon görevleri yeni merkezde gösterilir. Tarihi boş plan kaydı yapılmış uygulama gibi gösterilmez. Eski URL ve POST işlemleri korunmuştur. `/synchronization` adresi de sağlık merkezi içindeki senkronizasyon görünümünü açar.

## Paket

- Çekirdek sürüm: `3.9.23 DEV4 Hotfix1.22cr`.
- App Edition kimliği: `AppEdition2.0.30-UnifiedHealth`.
- Mobil kaynak/önbellek kimliği: `2.0.30`.
- Windows çıktı adı: `CiftlikPro_Enterprise_V3_9_23_DEV4_AppEdition_2_0_30_Setup.exe`.
- Yeni Python modülleri ve sağlık CSS/JS dosyaları Windows derleme/kurulum ve kaynak smoke kontrollerine dahil edilmiştir.
- Kaynak ZIP kullanıcı veritabanı, oturum, lisans veya önizleme verisi içermez.

Testler geçici veritabanlarında ve yerel tarayıcıda yapıldı. Windows EXE bu Linux ortamında derlenmedi; üretim akışı mevcut GitHub Actions dosyasıdır.
