export const BaseDVCPerKg = 0.1;

export const QualityMultiplier: Record<string, number> = {
  G1: 1.0,
  G2: 0.8,
  G3: 0.6,
};

export const FeesSplit = {
  ops: 0.4,
  dvcRewards: 0.3,
  communityPool: 0.3,
};

export const ProtocolFeeRate = 0.05;

export function srtDelta(grade: string, kg: number): number {
  if (grade === "G1") return 0.05 * kg;
  if (grade === "G2") return 0.03 * kg;
  return 0.01 * kg;
}

export function psMultiplier(srtScore: number): number {
  return srtScore >= 1000 ? 1.2 : 1.0;
}

