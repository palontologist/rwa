import { prisma } from "@/lib/prisma";
import Decimal from "decimal.js";
import { ProtocolFeeRate } from "@/lib/policy";

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
  return prisma.epoch.upsert({
    where: { label: p.epochLabel },
    update: { feePool: { increment: fee } },
    create: { label: p.epochLabel, feePool: fee },
  });
}

