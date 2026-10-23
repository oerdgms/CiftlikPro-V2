# ÇiftlikPro App Edition 2.0.22

22/10/2026. Önceki sürüm: 2.0.21 referans mobil tasarım.

## Ana sayfa

Altı kart: Genel, Sağmal, Kuru / Buzağı, Düve, Erkek. Erkek kartı, aktif yetişkin erkekleri sayar ve aynı hayvanların tür filtresini açar. Buzağılar kendi kartında kalır. Kızgınlık listesi ve Üreme Merkezi erişimi korunur.

## Manuel laktasyon

Hayvanlar veya Süt & Laktasyon → Laktasyon Belirle ekranında aktif yetişkin dişiler tek tek ya da topluca seçilir. Varsayılan seçim boştur; kullanıcının 12 hayvanı kendisinin işaretlemesi gerekir. Hayvan detayındaki Durum Ekle veya Laktasyon durumunu düzenle bağlantısı tekli düzenlemeyi açar.

Durumlar: Belirtilmedi, Laktasyonda (Sağmal), Kuru, Düve, Laktasyonda değil. Süt girişi, son doğum, 30 veya 305 günlük süreler otomatik üyelik oluşturmaz veya seçili laktasyonu sona erdirmez. Özet, liste ve mobil detay aynı kayıtlı durumu kullanır.

Durum tarihi zorunludur; başlangıç tarihi ve kaçıncı laktasyon olduğu isteğe bağlıdır. Başlangıç boşsa mobil özette sağım günü gösterilmez; durum tarihi başlangıç kabul edilmez. Toplu işlemde boş başlangıç/sıra alanları aynı mevcut laktasyondaki bilinen değerleri korur. Tekli düzenlemede boş bırakılarak temizlenebilir.

Mevcut kuruya çıkarma tarihi önceliklidir. Manuel Kuru kaydı aynı animals.dry_since alanına işler; diğer durumlar açık kuru işaretini kaldırır. Üreme ekranı veya doğum işlemi manuel Kuru kaydının tarihini kaldırırsa durum Belirtilmedi olur ve yeni seçim bekler.

İlk kurulumda süt/doğum verilerine bakarak seçim yapılmaz. Açık kuru kayıtları korunur; Düve dahil diğer durumlar kullanıcı tarafından belirlenir. Sayıların toplamı Genel ile eşit olmak zorunda değildir: Buzağı/Erkek ayrı gruplardır; durumu belirtilmeyen dişiler yalnız Genel içinde sayılır.

## Kayıt ve paket

Durum ve değişiklik geçmişi işletmenin mevcut veritabanındaki iki yeni tabloda saklanır. Güncelleme seçimin tamamında atomiktir; aktif olmayan, zayiatlı veya erkek kayıt içeren seçimde hiçbir durum değişmez. Hayvan silinince ilgili durum/geçmiş temizlenir. Oturum ve lisans kontrolleri geçerlidir. Süt miktarları veya finans satırları bu işlemle üretilmez.

Çekirdek 3.9.23 DEV4 Hotfix1.22cr kimliği korunur. Mobil önbellek ve Windows kurulum hedefi 2.0.22 olarak güncellenmiştir. ZIP tam kaynak/kurulum projesidir; hazır EXE içermez. Windows kurulum dosyası .github/workflows/windows-installer.yml ile oluşturulur.
