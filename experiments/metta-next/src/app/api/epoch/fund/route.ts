import { NextRequest, NextResponse } from "next/server";
import { fundEpochFromSettlement } from "@/services/settlement";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const epoch = await fundEpochFromSettlement(body);
  return NextResponse.json({ ok: true, epoch });
}

