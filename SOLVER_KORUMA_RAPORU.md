# Solver Koruma Raporu — Hotfix1.22bm

Bu hotfix yalnız Sağlık Merkezi çoklu hayvan planlama akışını değiştirir.

1.22bl ile AST düzeyinde karşılaştırılan 15 kritik rasyon/solver fonksiyonunun tamamı birebir aynıdır:
`beef_starch_targets`, `ration_requirement_targets`, `_solver_feed_role`, `smart_feed_bounds`, `_solver_nutrient`, `_solver_starch_pct`, `_feed_starch_degradability`, `_solver_feasibility_report`, `solve_smart_ration`, `safety_vector`, `hard_safety_vector`, `dairy_requirement_targets`, `dairy_feed_bounds`, `solve_smart_dairy_ration`, `ration_targets_for_record`.

Sonuç: rasyon solver davranışına dokunulmadı.
