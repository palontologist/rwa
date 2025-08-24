import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(req: NextRequest) {
  const { deliveryId, acceptedKg } = await req.json();
  const d = await prisma.delivery.update({ where: { id: deliveryId }, data: { acceptedKg, status: "ACCEPTED" }});
  return NextResponse.json({ ok: true, delivery: d });
}

