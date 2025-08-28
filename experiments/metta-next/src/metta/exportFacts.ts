import { db } from "@/db/client";
import { farmers, coops, buyers, deliveries, epochs } from "@/db/schema";
import { writeFileSync } from "node:fs";
import { join } from "node:path";

function fact(head: string, ...args: (string | number)[]) {
  const parts = args.map((a) => (typeof a === "string" ? a : String(a)));
  return `(${head} ${parts.join(" ")})`;
}

async function main() {
  const [fs, cs, bs, ds, es] = await Promise.all([
    db.select().from(farmers),
    db.select().from(coops),
    db.select().from(buyers),
    db.select().from(deliveries),
    db.select().from(epochs),
  ]);

  const lines: string[] = [];
  cs.forEach((c) => lines.push(fact("Coop", c.id)));
  bs.forEach((b) => lines.push(fact("Buyer", b.id)));
  fs.forEach((f) => {
    lines.push(fact("Farmer", f.id));
    lines.push(fact("SRT-score", f.id, f.srtScore));
    lines.push(fact("DVC-balance", f.id, f.dvcBalance));
    lines.push(fact("PS-balance", f.id, f.psBalance));
  });
  ds.forEach((d) => {
    lines.push(`(Delivery ${d.id} :farmer ${d.farmerId} :coop ${d.coopId} :kg ${d.kg} :grade ${d.grade})`);
    if (d.acceptedKg != null) lines.push(`(Accepted ${d.id} :kg ${d.acceptedKg} :grade ${d.grade})`);
    if (d.status === "SETTLED") lines.push(`(Settled ${d.id})`);
  });
  es.forEach((e) => lines.push(`(FeePool ${e.label} ${e.feePool})`));

  const out = lines.join("\n") + "\n";
  const path = join(process.cwd(), "facts.metta");
  writeFileSync(path, out, "utf8");
  // eslint-disable-next-line no-console
  console.log(`Wrote ${lines.length} facts to ${path}`);
}

main();

