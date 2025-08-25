import Decimal from "decimal.js";
import { ProtocolFeeRate } from "@/lib/policy";
import { db } from "@/db/client";
import { epochs } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function fundEpochFromSettlement(p: {
  epochLabel: string;
  grossReceipts: number;
  facilityPrincipal: number;
  facilityInterest: number;
  opsCosts: number;
}) {
  const net = new Decimal(p.grossReceipts)
    .minus(p.facilityPrincipal)
    .minus(p.facilityInterest)
    .minus(p.opsCosts);
  const fee = Decimal.max(net, 0).mul(ProtocolFeeRate);
  const [existing] = await db.select().from(epochs).where(eq(epochs.label, p.epochLabel));
  if (existing) {
    await db.update(epochs).set({ feePool: Number(new Decimal(existing.feePool).add(fee)) }).where(eq(epochs.id, existing.id));
    const [updated] = await db.select().from(epochs).where(eq(epochs.id, existing.id));
    return updated;
  } else {
    const id = crypto.randomUUID();
    await db.insert(epochs).values({ id, label: p.epochLabel, feePool: fee.toNumber(), opsAmount: 0, dvcRewards: 0, poolAmount: 0, closed: false, createdAt: Date.now() });
    const [created] = await db.select().from(epochs).where(eq(epochs.id, id));
    return created;
  }
}

