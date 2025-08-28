#!/usr/bin/env python3
from __future__ import annotations
import csv
import uuid
from pathlib import Path
from datetime import datetime
import typer
from rich import print

from ..storage.store import JsonStore
from ..storage.models import Farmer, Coop, Buyer, Delivery, Settlement, Epoch
from ..engine.engine import Engine


app = typer.Typer(help="MeTTa MVP CLI")


def store_from_flag(store: Path) -> JsonStore:
    return JsonStore(store)


@app.command()
def init(store: Path = typer.Option(Path("./state"), help="State folder")):
    JsonStore(store)
    print(f"[green]Initialized store at {store}")


@app.command()
def seed_sample(store: Path = typer.Option(Path("./state"))):
    s = store_from_flag(store)
    # coop, buyer, farmers
    s.upsert_coop(Coop(id="c1", name="Coop One"))
    s.upsert_buyer(Buyer(id="b1", name="Buyer One"))
    for fid in ["f1", "f2", "f3"]:
        s.upsert_farmer(Farmer(id=fid, coop_id="c1"))
    print("[green]Seeded sample identities")


@app.command()
def ingest_csv(
    csv_path: Path = typer.Argument(..., help="CSV with deliveries sample"),
    store: Path = typer.Option(Path("./state")),
):
    s = store_from_flag(store)
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            did = row["id"]
            if not s.mark_idempotent(f"delivery:{did}"):
                continue
            delivery = Delivery(
                id=did,
                farmer_id=row["farmer_id"],
                coop_id=row["coop_id"],
                kg=float(row["kg"]),
                grade=row["grade"],
                timestamp=datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")),
                accepted_kg=float(row["accepted_kg"]) if row["accepted_kg"] else None,
                status="SETTLED" if row.get("settled_ts") else ("ACCEPTED" if row.get("accepted_kg") else "PENDING"),
            )
            s.upsert_delivery(delivery)
            if row.get("settled_ts"):
                s.upsert_settlement(
                    Settlement(
                        id=str(uuid.uuid4()),
                        delivery_id=did,
                        buyer_id=row["buyer_id"],
                        amount=float(row["amount"]),
                        timestamp=datetime.fromisoformat(row["settled_ts"].replace("Z", "+00:00")),
                    )
                )
    print("[green]Ingested CSV deliveries/settlements")


@app.command()
def mint_all(store: Path = typer.Option(Path("./state"))):
    s = store_from_flag(store)
    eng = Engine(s)
    minted = 0
    for d in s.list_deliveries():
        res = eng.mint_dvc_for_delivery(d.id)
        if res:
            minted += 1
    print(f"[green]Minted for {minted} deliveries")


@app.command()
def stake(
    farmer_id: str = typer.Argument(...),
    amount: float = typer.Argument(...),
    store: Path = typer.Option(Path("./state")),
):
    s = store_from_flag(store)
    eng = Engine(s)
    ok = eng.stake_dvc(farmer_id, amount)
    print("[green]Staked" if ok else "[red]Stake failed")


@app.command()
def epoch_set_fee(label: str, amount: float, store: Path = typer.Option(Path("./state"))):
    s = store_from_flag(store)
    eng = Engine(s)
    ep = eng.set_epoch_fee_pool(label, amount)
    print(f"[green]Epoch {ep.label} fee_pool={ep.fee_pool}")


@app.command()
def epoch_close(label: str, store: Path = typer.Option(Path("./state"))):
    s = store_from_flag(store)
    eng = Engine(s)
    res = eng.close_epoch(label)
    print(res)


@app.command()
def export_balances(out_csv: Path, store: Path = typer.Option(Path("./state"))):
    s = store_from_flag(store)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["farmer_id", "srt_score", "dvc_balance", "dvc_staked", "ps_balance"])
        for farmer in s.list_farmers():
            writer.writerow([farmer.id, farmer.srt_score, farmer.dvc_balance, farmer.dvc_staked, farmer.ps_balance])
    print(f"[green]Exported balances to {out_csv}")


if __name__ == "__main__":
    app()

