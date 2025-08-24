import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET() {
  const farmers = await prisma.farmer.findMany();
  const header = "farmerId,srtScore,dvcBalance,dvcStaked,psBalance";
  const rows = farmers.map(f => [f.id, f.srtScore, f.dvcBalance, f.dvcStaked, f.psBalance].join(","));
  const csv = [header, ...rows].join("\n");
  return new NextResponse(csv, { headers: { "content-type": "text/csv" }});
}

