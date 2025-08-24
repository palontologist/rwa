import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { mintDVCForVerifiedDelivery } from "@/services/tokens";

export async function POST(req: NextRequest) {
  const { deliveryId, buyerId, amount, timestamp } = await req.json();
  const d = await prisma.delivery.findUnique({ where: { id: deliveryId }});
  if (!d || d.status !== "ACCEPTED") {
    return NextResponse.json({ error: "Delivery not accepted" }, { status: 400 });
  }
  await prisma.settlement.create({ data: { deliveryId, buyerId, amount, timestamp: new Date(timestamp) }});
  await prisma.delivery.update({ where: { id: deliveryId }, data: { status: "SETTLED" }});
  const minted = await mintDVCForVerifiedDelivery(deliveryId);
  return NextResponse.json({ ok: true, minted });
}

