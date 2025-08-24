from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
import uuid

from ..storage.store import JsonStore
from ..storage.models import Delivery, Farmer, Epoch, Reward
from ..policy.policy import (
    compute_dvc_mint,
    srt_delta,
    FEES_SPLIT,
    PROTOCOL_FEE_RATE,
    ps_multiplier,
)


@dataclass
class MintResult:
    farmer_id: str
    dvc_minted: float


class Engine:
    def __init__(self, store: JsonStore):
        self.store = store

    # Verification predicate: Delivery + Accepted + Settled encoded as Delivery(status==SETTLED and accepted_kg present)
    def is_verified(self, delivery: Delivery) -> bool:
        return delivery.status == "SETTLED" and delivery.accepted_kg is not None

    # Mint DVC and update SRT
    def mint_dvc_for_delivery(self, delivery_id: str) -> Optional[MintResult]:
        delivery = self.store.get_delivery(delivery_id)
        if not delivery or not self.is_verified(delivery):
            return None
        farmer = self.store.get_farmer(delivery.farmer_id)
        if not farmer:
            return None
        amount = compute_dvc_mint(delivery.accepted_kg or 0.0, delivery.grade)
        farmer.dvc_balance += amount
        farmer.srt_score += srt_delta(delivery.grade, float(delivery.accepted_kg or 0.0))
        self.store.upsert_farmer(farmer)
        return MintResult(farmer_id=farmer.id, dvc_minted=amount)

    # Staking
    def stake_dvc(self, farmer_id: str, amount: float) -> bool:
        farmer = self.store.get_farmer(farmer_id)
        if not farmer or amount <= 0 or farmer.dvc_balance < amount:
            return False
        farmer.dvc_balance -= amount
        farmer.dvc_staked += amount
        self.store.upsert_farmer(farmer)
        return True

    def unstake_dvc(self, farmer_id: str, amount: float) -> bool:
        farmer = self.store.get_farmer(farmer_id)
        if not farmer or amount <= 0 or farmer.dvc_staked < amount:
            return False
        farmer.dvc_staked -= amount
        farmer.dvc_balance += amount
        self.store.upsert_farmer(farmer)
        return True

    # Epoch operations
    def set_epoch_fee_pool(self, label: str, amount: float) -> Epoch:
        epoch = self.store.get_epoch_by_label(label)
        if epoch is None:
            epoch = Epoch(id=str(uuid.uuid4()), label=label, fee_pool=amount)
        else:
            epoch.fee_pool += amount
        self.store.upsert_epoch(epoch)
        return epoch

    def close_epoch(self, label: str) -> Dict:
        epoch = self.store.get_epoch_by_label(label)
        if not epoch or epoch.closed:
            return {"error": "invalid or closed epoch"}

        ops_amt = epoch.fee_pool * FEES_SPLIT["ops"]
        dvc_amt = epoch.fee_pool * FEES_SPLIT["dvc_rewards"]
        pool_amt = epoch.fee_pool * FEES_SPLIT["community_pool"]

        farmers = self.store.list_farmers()
        total_staked = sum(f.dvc_staked for f in farmers)

        rewards: List[Reward] = []
        for f in farmers:
            if total_staked <= 0 or f.dvc_staked <= 0:
                continue
            share = f.dvc_staked / total_staked
            dvc_reward = dvc_amt * share
            ps_reward = pool_amt * share * ps_multiplier(f.srt_score)
            f.dvc_balance += dvc_reward
            f.ps_balance += ps_reward
            self.store.upsert_farmer(f)
            rewards.append(
                Reward(
                    id=str(uuid.uuid4()),
                    epoch_label=label,
                    farmer_id=f.id,
                    dvc_reward=dvc_reward,
                    ps_reward=ps_reward,
                )
            )

        for r in rewards:
            self.store.add_reward(r)

        epoch.ops_amount = ops_amt
        epoch.dvc_rewards = dvc_amt
        epoch.pool_amount = pool_amt
        epoch.closed = True
        epoch.closed_at = datetime.utcnow()
        self.store.upsert_epoch(epoch)

        return {
            "ops": ops_amt,
            "dvc": dvc_amt,
            "pool": pool_amt,
            "rewards": len(rewards),
        }

