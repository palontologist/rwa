from typing import Dict

# Base tokenomics
BASE_DVC_PER_KG: float = 0.1

QUALITY_MULTIPLIER: Dict[str, float] = {
    "G1": 1.0,
    "G2": 0.8,
    "G3": 0.6,
}

FEES_SPLIT = {
    "ops": 0.4,
    "dvc_rewards": 0.3,
    "community_pool": 0.3,
}

PROTOCOL_FEE_RATE: float = 0.05


def srt_delta(grade: str, kg: float) -> float:
    if grade == "G1":
        return 0.05 * kg
    if grade == "G2":
        return 0.03 * kg
    return 0.01 * kg


def ps_multiplier(srt_score: float) -> float:
    return 1.2 if srt_score >= 1000 else 1.0


def compute_dvc_mint(accepted_kg: float, grade: str) -> float:
    q = QUALITY_MULTIPLIER.get(grade, 0.0)
    return BASE_DVC_PER_KG * q * float(accepted_kg)

