# ÇiftlikPro Enterprise — App Edition 1.0

Bu sürüm ayrı bir mobil iş mantığı oluşturmaz. Telefon görünümü doğrudan mevcut Enterprise sayfalarını ve mevcut route/form/DB işlemlerini kullanır.

## Mobil UX
- Alt menü: Ana Sayfa | Hayvanlar | + | İşler | Modüller
- Ortadaki + hızlı işlem menüsü
- iOS safe-area ve yatay taşma koruması
- Modüller düğmesi mevcut Enterprise yan menüsünü açar
- Sağlık, finans, rasyon, yem/stok, üreme, padok ve diğer işlemler mevcut Enterprise route'larında kalır

## Mimari kural
İş mantığı = Enterprise. App Edition katmanı yalnız navigasyon ve responsive UX ekler. MobileFull V13 dosyaları geriye dönük referans olarak pakette tutulmuştur; yeni geliştirme hedefi değildir.

## Native paketleme
Bu kaynak App Edition web katmanıdır. Android/iOS native kabuğu bir sonraki paketleme aşamasında bu tek Enterprise arayüzünü açacak şekilde hazırlanmalıdır; backend tekrar yazılmamalıdır.
