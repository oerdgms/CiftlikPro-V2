# Mobile API v4 — Padok Veri Eşitliği

Bu sürümde mobil Padoklar ekranı masaüstü Padok Yönetimi ile aynı nüfus tanımına bağlandı.

- Aktif yetişkin hayvanlar dahil edilir.
- Aktif ve henüz yetişkine aktarılmamış buzağılar dahil edilir.
- Ölüm/kayıp kaydı bulunan yetişkin ve buzağılar hariç tutulur.
- Mobil padok kartındaki sayı `paddock_population()` ortak fonksiyonundan gelir.
- Padok detayında yetişkin ve buzağı kayıtları birlikte gösterilir.
- Buzağı satırları mobil detay ekranından açılabilir.

Bu aşamada yeni yazma işlemi eklenmedi; önce masaüstü/mobil veri eşitliği güvenceye alındı.
