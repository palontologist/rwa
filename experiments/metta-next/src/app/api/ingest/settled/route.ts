import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db/client";
import { mintDVCForVerifiedDelivery } from "@/services/tokens";
import { settlements, deliveries } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function POST(req: NextRequest) {
  const { deliveryId, buyerId, amount, timestamp } = await req.json();
  const [d] = await db.select().from(deliveries).where(eq(deliveries.id, deliveryId));
  if (!d || d.status !== "ACCEPTED") {
    return NextResponse.json({ error: "Delivery not accepted" }, { status: 400 });
  }
  await db.insert(settlements).values({ id: crypto.randomUUID(), deliveryId, buyerId, amount, timestamp: new Date(timestamp).getTime() });
  await db.update(deliveries).set({ status: "SETTLED" }).where(eq(deliveries.id, deliveryId));
  const minted = await mintDVCForVerifiedDelivery(deliveryId);
  return NextResponse.json({ ok: true, minted });
}

