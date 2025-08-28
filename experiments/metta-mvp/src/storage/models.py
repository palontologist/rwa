from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Farmer(BaseModel):
    id: str
    coop_id: Optional[str] = None
    srt_score: float = 0.0
    dvc_balance: float = 0.0
    dvc_staked: float = 0.0
    ps_balance: float = 0.0


class Coop(BaseModel):
    id: str
    name: str


class Buyer(BaseModel):
    id: str
    name: str


class Delivery(BaseModel):
    id: str
    farmer_id: str
    coop_id: str
    kg: float
    grade: str
    timestamp: datetime
    accepted_kg: Optional[float] = None
    status: str = "PENDING"  # PENDING | ACCEPTED | SETTLED | DISPUTED


class Settlement(BaseModel):
    id: str
    delivery_id: str
    buyer_id: str
    amount: float
    timestamp: datetime


class Epoch(BaseModel):
    id: str
    label: str
    fee_pool: float = 0.0
    ops_amount: float = 0.0
    dvc_rewards: float = 0.0
    pool_amount: float = 0.0
    closed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None


class Reward(BaseModel):
    id: str
    epoch_label: str
    farmer_id: str
    dvc_reward: float = 0.0
    ps_reward: float = 0.0

