# AppEdition 2.0.20h

- Mobil rasyon detayında `ration_requirement_panel()` renderini durduran f-string/CSS süslü parantez hatası düzeltildi.
- `.cp-science-first-render-toggle` CSS kuralı f-string içinde güvenli `{{ ... }}` biçimine alındı.
- Bilimsel Hedef Özeti mobilde ilk açılışta kapalı kalma davranışı korundu.
- Rasyon Düzenle / Profil Düzenle yerleşimlerine ve solver hesaplarına dokunulmadı.
- Enterprise kaynak snapshotı yalnız `ration_requirement_panel` için yeni doğrulanmış kaynakla güncellendi.
- `tests/test_app_edition.py`: 23/23 geçti.
