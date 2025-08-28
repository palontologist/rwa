from __future__ import annotations
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
import time
from models import Task, WorkWindow, BusySlot, ScheduleEntry, Inputs

@dataclass
class Interval:
    start: int
    end: int
    def duration(self) -> int:
        return max(0, self.end - self.start)

def overlaps(a: Interval, b: Interval) -> bool:
    return a.start < b.end and b.start < a.end

def subtract_one(free: Interval, busy: Interval) -> List[Interval]:
    if not overlaps(free, busy): return [free]
    if busy.start <= free.start and busy.end >= free.end: return []
    if busy.start > free.start and busy.end < free.end:
        return [Interval(free.start, busy.start), Interval(busy.end, free.end)]
    if busy.start <= free.start and busy.end < free.end:
        return [Interval(busy.end, free.end)]
    if busy.start > free.start and busy.end >= free.end:
        return [Interval(free.start, busy.start)]
    return []

def subtract_many(free: Interval, busies: List[Interval]) -> List[Interval]:
    pieces = [free]
    for b in busies:
        next_pieces: List[Interval] = []
        for p in pieces:
            next_pieces.extend(subtract_one(p, b))
        pieces = next_pieces
        if not pieces: break
    return pieces

def free_slots(window: WorkWindow, busy: List[BusySlot]) -> List[Interval]:
    base = Interval(window.start_ts, window.end_ts)
    busies = [Interval(b.start_ts, b.end_ts) for b in busy if b.day == window.day]
    busies.sort(key=lambda x: x.start)
    slots = subtract_many(base, busies)
    return [s for s in slots if s.duration() > 0]

def now_ms() -> int:
    return int(time.time() * 1000)

def score(task: Task, current_ms: int) -> float:
    urg = 1.0 / max(1, (task.deadline_ts - current_ms))
    return (2.0 * task.priority) + urg

def topo_ready(tasks: Dict[str, Task], done: Set[str]) -> List[Task]:
    ready = []
    for t in tasks.values():
        if t.id in done: continue
        if all(dep in done for dep in t.deps): ready.append(t)
    return ready

def place_task_in_slots(task: Task, slots: List[Interval]) -> Tuple[ScheduleEntry | None, List[Interval]]:
    need = task.duration_min * 60_000
    for idx, s in enumerate(slots):
        if s.duration() >= need:
            start = s.start
            end = start + need
            rem: List[Interval] = []
            if end < s.end: rem.append(Interval(end, s.end))
            new_slots = slots[:idx] + rem + slots[idx+1:]
            return ScheduleEntry(task_id=task.id, start_ts=start, end_ts=end), new_slots
    return None, slots

def schedule(inputs: Inputs) -> List[ScheduleEntry]:
    slots = free_slots(inputs.work_window, inputs.busy)
    tasks: Dict[str, Task] = {t.id: t for t in inputs.tasks}
    done: Set[str] = set()
    scheduled: List[ScheduleEntry] = []
    while True:
        pending = [t for t in tasks.values() if t.id not in done and not any(se.task_id == t.id for se in scheduled)]
        if not pending: break
        ready = topo_ready(tasks, done)
        if not ready: raise RuntimeError("No ready tasks (dependency cycle or unmet deps)")
        pick = max(ready, key=lambda t: score(t, now_ms()))
        placed, slots = place_task_in_slots(pick, slots)
        if not placed: raise RuntimeError("No free slot fits selected task")
        scheduled.append(placed)
        done.add(pick.id)
    return scheduled