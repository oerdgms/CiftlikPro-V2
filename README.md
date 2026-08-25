# ÇiftlikPro Enterprise v3.9.20 — 6.19

GitHub/kurulum için temiz kaynak. 6.19 Desktop ERP UX sürümüdür.

## Çalıştırma
- Masaüstü: `python app/desktop_launcher.py`
- Kaynaktan test: `KAYNAKTAN_CALISTIR.bat`

Kurulum paketinde `desktop_launcher.py` giriş noktası önerilir; böylece tarayıcı adres çubuğu yerine uygulama penceresi kullanılır.

## Güvence
6.19 değişiklikleri kullanıcı arayüzü/kabuk katmanındadır. 6.17/6.18 rasyon solver hesap mantığı korunmuştur.


## 6.19.1 Ağ erişimi
Masaüstü WebView yerel olarak `127.0.0.1` adresini kullanır; HTTP sunucusu ise `0.0.0.0` üzerinde dinler. Böylece aynı kurulum LAN IP ve Tailscale/VPN IP üzerinden de erişilebilir. Windows Güvenlik Duvarı ilk çalıştırmada Python/ÇiftlikPro için özel ağ erişimi sorarsa izin verilmelidir.
