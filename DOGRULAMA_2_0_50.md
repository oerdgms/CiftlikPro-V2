# AppEdition 2.0.50 — Finans bölümünde işletmede kalma süresi

Temel: 2.0.49. Tarih: 31.10.2026.

Hayvan ve buzağı mobil kartında Finansal Bilgiler'in en üstüne İşletmeye Giriş
ve Bizde Kalma alanları eklendi. Kaydedilmiş giriş tarihi, yoksa alış tarihi
kullanılır. Tarih yoksa Giriş tarihi girilmemiş yazılır; doğum/padok/rasyon
tarihinden süre tahmin edilmez. Aktif kayıtlarda bugüne, arşiv kayıtlarında
geçerli çıkış tarihine kadar geçen gün gösterilir. Gelecek giriş tarihi,
eksik veya çelişkili çıkış tarihi ayrıca belirtilir.

Mevcut maliyet hesapları, veri tabanı, solver ve PWA güncelleme denetleyicisi
değiştirilmedi. app/server.py, app/ration_recalculation.py ve pwa.js 2.0.49
ile bayt düzeyinde aynı. Veri göçü yoktur.

Doğrulama:

- 60 hedefli regresyon testi / 44,996 saniye, tamamı başarılı. Kapsam:
  giriş/alış tarihi önceliği, eksik/geçersiz/gelecek tarihler, sıfır gün,
  çıkış tarihinde duran süre, hayvan ve buzağı finansında değişmeyen maliyetler,
  mevcut referans arayüzü, PWA/sürüm kimliği ve rasyon yeniden hesaplaması.
- Chromium: 320, 390, 412, 820 pikselde hayvan ve buzağı için 8 görünüm
  kontrolü başarılı. Alanlar finans özetinin üstünde ve ekrana sığıyor.
- 2 PWA geçiş akışı başarılı: açık 2.0.49 ekranının sunucudaki gerçek 2.0.50
  sürüm bilgisini görmesi; eski worker/önbelleğin güncellenmesi sırasında
  yazılı formun korunması; iptal ve onay ile yeniden açılış; yeni sürümde
  tekrar kontrolün güncel sonucunu vermesi. Eski sayfa kimliği ve worker
  tarayıcı yönlendirmesiyle oluşturuldu; yeni sürüm bilgisi test sunucusundan geldi.
- JavaScript hatası yok; 390 piksel finans görünümü görsel olarak incelendi.
- scripts/sync_release.py --check başarılı.

Testler geçici verilerle yapıldı. Canlı işletme verisine erişilmedi; Windows EXE
üretilmedi ve gerçek telefon üzerinde bu sürüm henüz denenmedi. Genel 502 testlik
tarama yeniden çalıştırılmadı; bu küçük görünüm değişikliği için yukarıdaki
60 test çalıştırıldı.

Güncelleme kullanımı: Çiftlik bilgisayarında bu kaynak paketini mevcut veri
konumunu koruyarak çalıştırın. Telefonda Uygulama ve güncellemeler → Güncellemeyi
kontrol et → Yeni sürümü aç. Bu denetim bilgisayara ZIP indirmez veya kurmaz.
Telefona yeniden PWA yüklemek gerekmez; aynı HTTPS adresini kullanın.
