import Decimal from "decimal.js";
import { FeesSplit, psMultiplier } from "@/lib/policy";
import { db } from "@/db/client";
import { epochs, farmers, rewards } from "@/db/schema";
import { eq, sum, gt } from "drizzle-orm";

export async function closeEpoch(label: string) {
  const [epoch] = await db.select().from(epochs).where(eq(epochs.label, label));
  if (!epoch || epoch.closed) throw new Error("Invalid epoch");

  const fee = new Decimal(epoch.feePool);
  const ops = fee.mul(FeesSplit.ops);
  const dvc = fee.mul(FeesSplit.dvcRewards);
  const pool = fee.mul(FeesSplit.communityPool);

  const [{ totalStaked = 0 }] = await db.select({ totalStaked: sum(farmers.dvcStaked).as("totalStaked") }).from(farmers);
  const total = new Decimal(totalStaked || 0);
  const stakers = await db
    .select({ id: farmers.id, dvcStaked: farmers.dvcStaked, srtScore: farmers.srtScore, dvcBalance: farmers.dvcBalance, psBalance: farmers.psBalance })
    .from(farmers)
    .where(gt(farmers.dvcStaked, 0));

  for (const f of stakers) {
    if (total.lte(0)) break;
    const share = new Decimal(f.dvcStaked).div(total);
    const dr = dvc.mul(share);
    const pr = pool.mul(share).mul(psMultiplier(f.srtScore));
    await db.update(farmers)
      .set({
        dvcBalance: Number(new Decimal(f.dvcBalance).add(dr)),
        psBalance: Number(new Decimal(f.psBalance).add(pr)),
      })
      .where(eq(farmers.id, f.id));
    await db.insert(rewards).values({
      id: crypto.randomUUID(),
      epochLabel: label,
      farmerId: f.id,
      dvcReward: dr.toNumber(),
      psReward: pr.toNumber(),
    });
  }

  await db.update(epochs)
    .set({ opsAmount: ops.toNumber(), dvcRewards: dvc.toNumber(), poolAmount: pool.toNumber(), closed: true, closedAt: Date.now() })
    .where(eq(epochs.id, epoch.id));

  return { opsAmount: ops.toNumber(), dvcAmount: dvc.toNumber(), poolAmount: pool.toNumber() };
}

