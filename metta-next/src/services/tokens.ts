import Decimal from "decimal.js";
import { BaseDVCPerKg, QualityMultiplier, srtDelta } from "@/lib/policy";
import { db } from "@/db/client";
import { deliveries, farmers, settlements } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function mintDVCForVerifiedDelivery(deliveryId: string) {
  const [d] = await db.select().from(deliveries).where(eq(deliveries.id, deliveryId));
  if (!d || d.status !== "SETTLED" || d.acceptedKg == null) return null;
  const mult = QualityMultiplier[d.grade] ?? 0;
  const amount = new Decimal(BaseDVCPerKg).mul(mult).mul(d.acceptedKg);
  const [f] = await db.select().from(farmers).where(eq(farmers.id, d.farmerId));
  if (!f) return null;
  await db.update(farmers)
    .set({
      dvcBalance: Number(new Decimal(f.dvcBalance).add(amount)),
      srtScore: f.srtScore + Math.round(srtDelta(d.grade, Number(d.acceptedKg))),
    })
    .where(eq(farmers.id, d.farmerId));
  return { farmerId: d.farmerId, dvcMinted: amount.toNumber() };
}

export async function stakeDVC(farmerId: string, amount: number) {
  const [f] = await db.select().from(farmers).where(eq(farmers.id, farmerId));
  if (!f) throw new Error("Farmer not found");
  if (new Decimal(f.dvcBalance).lt(amount)) throw new Error("Insufficient DVC");
  await db.update(farmers)
    .set({ dvcBalance: Number(new Decimal(f.dvcBalance).minus(amount)), dvcStaked: Number(new Decimal(f.dvcStaked).add(amount)) })
    .where(eq(farmers.id, farmerId));
}

export async function unstakeDVC(farmerId: string, amount: number) {
  const [f] = await db.select().from(farmers).where(eq(farmers.id, farmerId));
  if (!f) throw new Error("Farmer not found");
  if (new Decimal(f.dvcStaked).lt(amount)) throw new Error("Insufficient staked");
  await db.update(farmers)
    .set({ dvcStaked: Number(new Decimal(f.dvcStaked).minus(amount)), dvcBalance: Number(new Decimal(f.dvcBalance).add(amount)) })
    .where(eq(farmers.id, farmerId));
}

