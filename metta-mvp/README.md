MeTTa MVP (Track B: SRT + DVC + Pool Shares)

Minimal Python CLI to orchestrate the non-debt, data-backed token model. Uses a JSON store for state, policy config for tokenomics, and a thin engine to mint DVC, update SRT, handle staking, and distribute epoch rewards. Includes a MeTTa facts skeleton for alignment and future interpreter integration.

Quick start:

1) Install deps
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
2) Seed and ingest sample
   - python -m src.cli.main init --store ./state
   - python -m src.cli.main seed-sample --store ./state
   - python -m src.cli.main ingest-csv --store ./state ./src/samples/deliveries.csv
   - python -m src.cli.main mint-all --store ./state
   - python -m src.cli.main stake --store ./state f1 50
   - python -m src.cli.main epoch-set-fee --store ./state epoch_1 10000
   - python -m src.cli.main epoch-close --store ./state epoch_1
   - python -m src.cli.main export-balances --store ./state ./out/balances.csv

Notes:
- Store is a folder holding JSON files for entities and idempotency keys.
- All arithmetic is simple floats in MVP; replace with Decimal for production.
- Ledger side-effects are no-ops; swap to on-chain later.

