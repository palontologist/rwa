import { db } from "@/db/client";
import { buyers, coops, farmers } from "@/db/schema";

async function main() {
  await db.insert(coops).values({ id: "c1", name: "Coop One" }).onConflictDoNothing();
  await db.insert(buyers).values({ id: "b1", name: "Buyer One" }).onConflictDoNothing();
  for (const id of ["f1", "f2", "f3"]) {
    await db.insert(farmers).values({ id, coopId: "c1", srtScore: 0, dvcBalance: 0, dvcStaked: 0, psBalance: 0, createdAt: Date.now() }).onConflictDoNothing();
  }
}

main();

