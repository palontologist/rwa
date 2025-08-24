from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, List

from .models import Farmer, Coop, Buyer, Delivery, Settlement, Epoch, Reward


class JsonStore:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.paths = {
            "farmers": self.root / "farmers.json",
            "coops": self.root / "coops.json",
            "buyers": self.root / "buyers.json",
            "deliveries": self.root / "deliveries.json",
            "settlements": self.root / "settlements.json",
            "epochs": self.root / "epochs.json",
            "rewards": self.root / "rewards.json",
            "idempo": self.root / "idempotency.json",
        }
        for p in self.paths.values():
            if not p.exists():
                p.write_text(json.dumps({}))

    # low-level read/write
    def _read(self, key: str) -> Dict:
        return json.loads(self.paths[key].read_text())

    def _write(self, key: str, data: Dict) -> None:
        self.paths[key].write_text(json.dumps(data, indent=2))

    # idempotency
    def mark_idempotent(self, key: str) -> bool:
        data = self._read("idempo")
        if key in data:
            return False
        data[key] = True
        self._write("idempo", data)
        return True

    # farmers
    def get_farmer(self, fid: str) -> Optional[Farmer]:
        data = self._read("farmers")
        if fid in data:
            return Farmer(**data[fid])
        return None

    def upsert_farmer(self, farmer: Farmer) -> None:
        data = self._read("farmers")
        data[farmer.id] = farmer.model_dump(mode="json")
        self._write("farmers", data)

    def list_farmers(self) -> List[Farmer]:
        data = self._read("farmers")
        return [Farmer(**v) for v in data.values()]

    # coops
    def upsert_coop(self, coop: Coop) -> None:
        data = self._read("coops")
        data[coop.id] = coop.model_dump(mode="json")
        self._write("coops", data)

    # buyers
    def upsert_buyer(self, buyer: Buyer) -> None:
        data = self._read("buyers")
        data[buyer.id] = buyer.model_dump(mode="json")
        self._write("buyers", data)

    # deliveries
    def get_delivery(self, did: str) -> Optional[Delivery]:
        data = self._read("deliveries")
        if did in data:
            return Delivery(**data[did])
        return None

    def upsert_delivery(self, delivery: Delivery) -> None:
        data = self._read("deliveries")
        data[delivery.id] = delivery.model_dump(mode="json")
        self._write("deliveries", data)

    def list_deliveries(self) -> List[Delivery]:
        data = self._read("deliveries")
        return [Delivery(**v) for v in data.values()]

    # settlements
    def upsert_settlement(self, settlement: Settlement) -> None:
        data = self._read("settlements")
        data[settlement.id] = settlement.model_dump(mode="json")
        self._write("settlements", data)

    # epochs
    def get_epoch_by_label(self, label: str) -> Optional[Epoch]:
        data = self._read("epochs")
        for v in data.values():
            if v.get("label") == label:
                return Epoch(**v)
        return None

    def upsert_epoch(self, epoch: Epoch) -> None:
        data = self._read("epochs")
        data[epoch.id] = epoch.model_dump(mode="json")
        self._write("epochs", data)

    def list_epochs(self) -> List[Epoch]:
        data = self._read("epochs")
        return [Epoch(**v) for v in data.values()]

    # rewards
    def add_reward(self, reward: Reward) -> None:
        data = self._read("rewards")
        data[reward.id] = reward.model_dump(mode="json")
        self._write("rewards", data)

