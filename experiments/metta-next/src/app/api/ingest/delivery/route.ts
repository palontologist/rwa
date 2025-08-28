import { NextRequest, NextResponse } from "next/server";
import { db } from "@/db/client";
import { deliveries } from "@/db/schema";

export async function POST(req: NextRequest) {
  const { id, farmerId, coopId, kg, grade, timestamp } = await req.json();
  await db.insert(deliveries).values({ id, farmerId, coopId, kg, grade, timestamp: new Date(timestamp).getTime(), status: "PENDING" });
  return NextResponse.json({ ok: true });
}

