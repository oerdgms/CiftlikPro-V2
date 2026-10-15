# ÇiftlikPro Mobile Full V8 — Reference UI + Sağlık Planlama + Finans Fix

- Enterprise çekirdeği: V3.9.23 DEV4 Hotfix1.22cr
- Mobil build: MobileFullV8-ReferenceUI-HealthPlan-FinanceFix
- Finans: kategori artık serbest metin değil; mevcut finans kategorileri + güvenli varsayılanlardan seçilir.
- Finans kayıt POST yolu için kısa ve açık `/api/v1/finance/save` endpoint'i eklendi; eski module endpoint'i uyumluluk için korunur.
- Finans türü masaüstündeki `normalize_finance_type` kuralından geçirilir.
- Sağlık Merkezi: `+ Sağlık Kaydı` ve `+ Plan Oluştur` eylemleri eklendi.
- Sağlık planı: tek hayvan/buzağı için aşı doz/adım veya ilaç tedavi günü/aralığı/günlük doz planı üretir; görevler mevcut Bugün/Geciken/Yaklaşan altyapısına düşer.
- Mevcut V7 saha işlemleri ve solver korunur.
