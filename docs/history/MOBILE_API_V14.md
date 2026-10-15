# MobileAPI14 — Kompakt Düzenle + Çıkış İşlemleri

- Hayvan düzenleme artık detay sayfasının üstüne ikinci/tekrarlı kart eklemez; detay görünümünün yerine tek kompakt form açılır.
- Düzenleme formunda TR sabit ön ek + rakam küpe girişi, açık alan etiketleri, kompakt fotoğraf/kamera/galeri alanı bulunur.
- Hayvan kartına `⋯ İşlemler` eklendi.
- Aktif yetişkin hayvanda Satış, Kesim, Ölüm/Kayıp/Zorunlu İmha/İşletmeden Çıkarıldı işlemleri mobilde kullanılabilir.
- Aktif buzağıda Satış ve Ölüm/Kayıp işlemleri kullanılabilir.
- Satış/kesim kayıtları ortak finance tablosuna yazılır ve hayvan aktif sürüden masaüstü durum mantığıyla çıkarılır.
- Ölüm/kayıp işlemi masaüstündeki animal_loss_breakdown maliyet motorunu kullanır; eksik işletme maliyeti ve varsa tazminat finans hareketleri oluşturulur.
- API12/13 fotoğraf, gerçek maliyet, sağlık, üreme, tartım, kompakt hayvan/padok listesi korunur.
