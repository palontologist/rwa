from __future__ import annotations
from typing import Protocol


class Ledger(Protocol):
    async def credit_dvc(self, farmer_id: str, amount: float) -> None: ...
    async def debit_dvc(self, farmer_id: str, amount: float) -> None: ...
    async def mint_ps(self, farmer_id: str, amount: float) -> None: ...


class MockLedger:
    async def credit_dvc(self, farmer_id: str, amount: float) -> None:
        return None

    async def debit_dvc(self, farmer_id: str, amount: float) -> None:
        return None

    async def mint_ps(self, farmer_id: str, amount: float) -> None:
        return None

