# ÇiftlikPro Enterprise V3.9.20 · HOTFIX 6.16 DEV

GitHub temiz kaynak paketi. HOTFIX 6.15 Clean Source tabanı üzerine hazırlanmıştır.

## Bu sürümde

1. Sürüm notları / kaynak geçmişi sabitlendi (`CHANGELOG.md`).
2. Finans tablosu işlem butonları kompakt ve tek hizada.
3. Akıllı Rasyon Çöz içinde **Besi / Süt** seçimi var. Süt rasyonu aynı `feed_catalog` veritabanını kullanır; kullanıcı canlı ağırlık + hedef süt miktarı girer ve seçtiği yemlerin miktarları otomatik dengelenir.
4. Aktif, satılan ve kesilen hayvanlarda küpe numarası aynı buton görünümünde gösterilir.

## Çalıştırma

`DEV_BASLAT.bat` ile DEV ortamı başlar. Varsayılan DEV portu: **8965**.

## Ana kaynaklar

- `app/server.py`
- `app/feed_catalog.json`
- `app/desktop_launcher.py`
- `DEV_BASLAT.bat`
- `CHANGELOG.md`

> Not: Süt Solver V1 karar-destek amaçlıdır. Gerçek yem laboratuvar analizleri katalogdaki referans değerlerden önceliklidir.
