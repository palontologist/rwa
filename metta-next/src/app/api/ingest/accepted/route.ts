import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db/client";
import { deliveries } from "@/db/schema";
import { eq } from "drizzle-orm";

export async function POST(req: NextRequest) {
  const { deliveryId, acceptedKg } = await req.json();
  await db.update(deliveries).set({ acceptedKg, status: "ACCEPTED" }).where(eq(deliveries.id, deliveryId));
  return NextResponse.json({ ok: true });
}

