import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(req: NextRequest) {
  const { id, farmerId, coopId, kg, grade, timestamp } = await req.json();
  await prisma.delivery.create({ data: { id, farmerId, coopId, kg, grade, timestamp: new Date(timestamp), status: "PENDING" }});
  return NextResponse.json({ ok: true });
}

