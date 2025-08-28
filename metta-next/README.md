# Roadmap and Next.js Implementation

This repo implements Track B (non-debt, data‑backed token model): SRT + DVC + Pool Shares with fee routing.

What’s implemented (Next.js + Turso + Drizzle)

- DB: Turso (libsql) via Drizzle ORM
- Schema: Farmer, Coop, Buyer, Delivery, Settlement, Epoch, Reward
- Services:
  - tokens: mint DVC on verified deliveries, SRT updates; stake/unstake
  - epochs: fee split and pro‑rata rewards (DVC + PS) to stakers
  - settlement: season figures → fund epoch fee pool
- API routes:
  - POST /api/ingest/delivery
  - POST /api/ingest/accepted
  - POST /api/ingest/settled
  - POST /api/stake, POST /api/unstake
  - POST /api/epoch/fund, POST /api/epoch/close
  - GET  /api/export/balances (CSV)

Setup

1) Install deps
   - npm i
2) Configure env
   - cp .env.example .env
   - set TURSO_DATABASE_URL and TURSO_AUTH_TOKEN
3) Migrate and seed
   - npx drizzle-kit generate
   - npx drizzle-kit push
   - npm run seed
4) Run dev
   - npm run dev

High‑level roadmap

- Ingest/webhooks and CSV upload with idempotency and disputes
- Policy controls in admin UI; SRT gates and PS multipliers
- Staking cooldowns/vesting and timestamp guards
- Nightly/weekly epoch close jobs; charts and audit exports
- Ledger adapters to mirror on‑chain later

MeTTa (https://metta-lang.dev/) mapping in this Next.js project

- Facts → Tables: Farmers, Coops, Buyers, Deliveries, Settlements, Epochs, Rewards
- Predicates → Queries + guards:
  - VerifiedEventSet(d): Deliveries.status == "SETTLED" and acceptedKg != null
- Rules → Pure services (TypeScript):
  - DVC mint: BaseDVCPerKg × QualityMultiplier(grade) × acceptedKg
  - SRT update: srtDelta(grade, kg)
  - Rewards: FeePool × split → pro‑rata to stakers; PS with optional SRT multiplier
- Side effects → API routes: DB writes only; ledger adapters can be added later

Optional: export current DB state as MeTTa facts (facts.metta) via `npm run metta:export`.
