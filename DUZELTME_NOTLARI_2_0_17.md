# AppEdition 2.0.18 — Rasyon Target Fix

- `_energy_balance()` artık NEm/NEg anahtarlarını yalnız mevcut ve pozitif olduğunda kullanır.
- Süt rasyonlarında bulunmayan `nem_req_mcal` / `neg_req_mcal` nedeniyle oluşan `KeyError` engellendi.
- Eksik enerji hedefi 0 varsayılarak bilimsel hesap yapılmıyor; besiye özgü GCAA kapasite hesabı uygulanmadan güvenli dönüş yapılıyor.
- 2.0.16 alt navigasyon `+` düzeni ve mevcut fonksiyon korunmuştur.
