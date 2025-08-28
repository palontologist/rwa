import { NextRequest, NextResponse } from "next/server";
import { closeEpoch } from "@/services/epochs";

export async function POST(req: NextRequest) {
  const { label } = await req.json();
  try {
    const res = await closeEpoch(label);
    return NextResponse.json({ ok: true, ...res });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 400 });
  }
}

