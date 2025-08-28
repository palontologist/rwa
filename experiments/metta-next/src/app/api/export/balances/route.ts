import { NextResponse } from "next/server";
import { db } from "@/db/client";
import { farmers } from "@/db/schema";

export async function GET() {
  const rowsDb = await db.select().from(farmers);
  const header = "farmerId,srtScore,dvcBalance,dvcStaked,psBalance";
  const rows = rowsDb.map(f => [f.id, f.srtScore, f.dvcBalance, f.dvcStaked, f.psBalance].join(","));
  const csv = [header, ...rows].join("\n");
  return new NextResponse(csv, { headers: { "content-type": "text/csv" }});
}

