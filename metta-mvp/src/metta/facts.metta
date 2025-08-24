; Minimal MeTTa-aligned facts (illustrative)
(Farmer f1)
(Farmer f2)
(Farmer f3)
(Coop c1)
(Buyer b1)

; balances
(DVC-balance f1 0)
(DVC-balance f2 0)
(DVC-balance f3 0)
(PS-balance f1 0)
(PS-balance f2 0)
(PS-balance f3 0)
(SRT-score f1 0)
(SRT-score f2 0)
(SRT-score f3 0)

; policy
(Fees-split :ops 0.4 :dvc_rewards 0.3 :community_pool 0.3)
(BaseDVCPerKg 0.1)
(QualityMultiplier G1 1.0)
(QualityMultiplier G2 0.8)
(QualityMultiplier G3 0.6)
