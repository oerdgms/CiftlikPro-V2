# AppEdition 2.0.20b

- GitHub Python 3.12 ile yerel Python sürümleri arasında değişebilen `ast.dump` hash regresyon testi kaldırıldı.
- Enterprise core koruması kaldırılmadı; aynı fonksiyonlar artık Python sürümünden bağımsız, doğrudan kaynak-segment SHA-256 snapshot ile doğrulanıyor.
- `device_id`, `license_payload_bytes` dahil snapshot kapsamındaki çekirdek fonksiyonlar yeniden koruma altında.
- Uygulama/solver/lisans fonksiyonlarının çalışma koduna bu düzeltmede dokunulmadı.
