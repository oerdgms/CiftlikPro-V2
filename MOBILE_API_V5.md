# MobileAPI5 — Sürü Eşitliği + İlk Yazma İşlemi

- Aktif hayvan toplamı artık yetişkin aktif hayvanlar + yetişkine aktarılmamış aktif buzağıları aynı listede sayar.
- Kayıp/ölüm hareketi bulunan kayıtlar aktif sürü toplamından dışlanır.
- Mobil Hayvanlar listesi de buzağıları içerir; toplam ile liste aynı nüfusu kullanır.
- Planlı sağlık görevlerinde `Uygulandı` işlemi açıldı.
- Tek hayvan ve toplu/padok sağlık planları, masaüstündeki health_tasks -> health + finance akışını izler.
- Çift tıklama/mükerrer tamamlama DB durum geçişi ile engellenir.
- Legacy sağlık planı ve otomatik gebelik aşısı bu ilk yazma aşamasında salt okunur kalır.
