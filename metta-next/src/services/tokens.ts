import { prisma } from "@/lib/prisma";
import Decimal from "decimal.js";
import { BaseDVCPerKg, QualityMultiplier, srtDelta } from "@/lib/policy";

export async function mintDVCForVerifiedDelivery(deliveryId: string) {
  const d = await prisma.delivery.findUnique({ where: { id: deliveryId }, include: { farmer: true }});
  if (!d || d.status !== "SETTLED" || !d.acceptedKg) return null;
  const mult = QualityMultiplier[d.grade] ?? 0;
  const amount = new Decimal(BaseDVCPerKg).mul(mult).mul(d.acceptedKg);
  return prisma.$transaction(async (trx) => {
    const farmer = await trx.farmer.update({
      where: { id: d.farmerId },
      data: {
        dvcBalance: { increment: amount },
        srtScore: { increment: Math.round(srtDelta(d.grade, Number(d.acceptedKg))) },
      },
    });
    return { farmerId: farmer.id, dvcMinted: amount.toNumber() };
  });
}

export async function stakeDVC(farmerId: string, amount: number) {
  return prisma.$transaction(async (trx) => {
    const f = await trx.farmer.findUnique({ where: { id: farmerId } });
    if (!f) throw new Error("Farmer not found");
    if (new Decimal(f.dvcBalance).lt(amount)) throw new Error("Insufficient DVC");
    await trx.farmer.update({
      where: { id: farmerId },
      data: { dvcBalance: { decrement: amount }, dvcStaked: { increment: amount } },
    });
  });
}

export async function unstakeDVC(farmerId: string, amount: number) {
  return prisma.$transaction(async (trx) => {
    const f = await trx.farmer.findUnique({ where: { id: farmerId } });
    if (!f) throw new Error("Farmer not found");
    if (new Decimal(f.dvcStaked).lt(amount)) throw new Error("Insufficient staked");
    await trx.farmer.update({
      where: { id: farmerId },
      data: { dvcStaked: { decrement: amount }, dvcBalance: { increment: amount } },
    });
  });
}

