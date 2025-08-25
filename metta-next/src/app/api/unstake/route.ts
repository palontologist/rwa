import { NextRequest, NextResponse } from "next/server";
import { unstakeDVC } from "@/services/tokens";

export async function POST(req: NextRequest) {
  const { farmerId, amount } = await req.json();
  try {
    await unstakeDVC(farmerId, Number(amount));
    return NextResponse.json({ ok: true });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 400 });
  }
}

