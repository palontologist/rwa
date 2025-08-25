import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const farmers = sqliteTable("Farmers", {
  id: text("id").primaryKey(),
  phone: text("phone"),
  coopId: text("coopId"),
  srtScore: integer("srtScore").default(0).notNull(),
  dvcBalance: real("dvcBalance").default(0).notNull(),
  dvcStaked: real("dvcStaked").default(0).notNull(),
  psBalance: real("psBalance").default(0).notNull(),
  createdAt: integer("createdAt", { mode: "timestamp_ms" }).default(sql`(unixepoch('now')*1000)`).notNull(),
  updatedAt: integer("updatedAt", { mode: "timestamp_ms" }),
});

export const coops = sqliteTable("Coops", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
});

export const buyers = sqliteTable("Buyers", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
});

export const deliveries = sqliteTable("Deliveries", {
  id: text("id").primaryKey(),
  farmerId: text("farmerId").notNull(),
  coopId: text("coopId").notNull(),
  kg: real("kg").notNull(),
  grade: text("grade").notNull(),
  timestamp: integer("timestamp", { mode: "timestamp_ms" }).notNull(),
  acceptedKg: real("acceptedKg"),
  settledId: text("settledId"),
  status: text("status").default("PENDING").notNull(),
});

export const settlements = sqliteTable("Settlements", {
  id: text("id").primaryKey(),
  deliveryId: text("deliveryId").unique().notNull(),
  buyerId: text("buyerId").notNull(),
  amount: real("amount").notNull(),
  timestamp: integer("timestamp", { mode: "timestamp_ms" }).notNull(),
});

export const epochs = sqliteTable("Epochs", {
  id: text("id").primaryKey(),
  label: text("label").unique().notNull(),
  feePool: real("feePool").default(0).notNull(),
  opsAmount: real("opsAmount").default(0).notNull(),
  dvcRewards: real("dvcRewards").default(0).notNull(),
  poolAmount: real("poolAmount").default(0).notNull(),
  closed: integer("closed", { mode: "boolean" }).default(false).notNull(),
  createdAt: integer("createdAt", { mode: "timestamp_ms" }).default(sql`(unixepoch('now')*1000)`).notNull(),
  closedAt: integer("closedAt", { mode: "timestamp_ms" }),
});

export const rewards = sqliteTable("Rewards", {
  id: text("id").primaryKey(),
  epochLabel: text("epochLabel").notNull(),
  farmerId: text("farmerId").notNull(),
  dvcReward: real("dvcReward").default(0).notNull(),
  psReward: real("psReward").default(0).notNull(),
});

