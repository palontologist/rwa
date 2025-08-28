from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List

class Task(BaseModel):
    id: str
    duration_min: int
    priority: int
    deadline_ts: int
    deps: List[str] = Field(default_factory=list)

class WorkWindow(BaseModel):
    day: str
    start_ts: int
    end_ts: int

class BusySlot(BaseModel):
    day: str
    start_ts: int
    end_ts: int

class ScheduleEntry(BaseModel):
    task_id: str
    start_ts: int
    end_ts: int

class Inputs(BaseModel):
    tasks: List[Task]
    work_window: WorkWindow
    busy: List[BusySlot] = Field(default_factory=list)
    