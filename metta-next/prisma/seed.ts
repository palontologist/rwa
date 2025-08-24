import { prisma } from "../src/lib/prisma";

async function main() {
  await prisma.coop.upsert({ where: { id: "c1" }, update: {}, create: { id: "c1", name: "Coop One" }});
  await prisma.buyer.upsert({ where: { id: "b1" }, update: {}, create: { id: "b1", name: "Buyer One" }});
  for (const id of ["f1","f2","f3"]) {
    await prisma.farmer.upsert({ where: { id }, update: {}, create: { id, coopId: "c1" }});
  }
}

main().finally(() => prisma.$disconnect());

