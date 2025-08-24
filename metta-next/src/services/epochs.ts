import { prisma } from "@/lib/prisma";
import Decimal from "decimal.js";
import { FeesSplit, psMultiplier } from "@/lib/policy";

export async function closeEpoch(label: string) {
  const epoch = await prisma.epoch.findUnique({ where: { label }});
  if (!epoch || epoch.closed) throw new Error("Invalid epoch");

  const fee = new Decimal(epoch.feePool);
  const ops = fee.mul(FeesSplit.ops);
  const dvc = fee.mul(FeesSplit.dvcRewards);
  const pool = fee.mul(FeesSplit.communityPool);

  const agg = await prisma.farmer.aggregate({ _sum: { dvcStaked: true } });
  const total = new Decimal(agg._sum.dvcStaked ?? 0);
  const stakers = await prisma.farmer.findMany({ where: { dvcStaked: { gt: 0 } }, select: { id:true, dvcStaked:true, srtScore:true }});

  await prisma.$transaction(async (trx) => {
    for (const f of stakers) {
      const share = total.gt(0) ? new Decimal(f.dvcStaked).div(total) : new Decimal(0);
      const dr = dvc.mul(share);
      const pr = pool.mul(share).mul(psMultiplier(f.srtScore));
      await trx.farmer.update({ where: { id:f.id }, data: { dvcBalance: { increment: dr }, psBalance: { increment: pr } }});
      await trx.reward.create({ data: { epochId: epoch.id, farmerId: f.id, dvcReward: dr, psReward: pr }});
    }
    await trx.epoch.update({ where: { id: epoch.id }, data: { opsAmount: ops, dvcRewards: dvc, poolAmount: pool, closed: true, closedAt: new Date() }});
  });

  return { opsAmount: ops.toNumber(), dvcAmount: dvc.toNumber(), poolAmount: pool.toNumber() };
}

