#!/usr/bin/env python3
import json
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from models import Task, WorkWindow, BusySlot, Inputs
from engine import schedule

app = typer.Typer(help="Smarter Scheduler (EDF + Priority, deps-aware)")
console = Console()

@app.command()
def init(path: Path = typer.Option(Path("./metta-smarter"), help="Project folder")):
    path.mkdir(parents=True, exist_ok=True)
    sample = {
        "tasks": [
            {"id": "T1", "duration_min": 60, "priority": 5, "deadline_ts": 1754005200000, "deps": []},
            {"id": "T2", "duration_min": 30, "priority": 3, "deadline_ts": 1754008800000, "deps": []},
            {"id": "T3", "duration_min": 90, "priority": 4, "deadline_ts": 1754012400000, "deps": []},
        ],
        "work_window": {"day": "d1", "start_ts": 1754000400000, "end_ts": 1754029200000},
        "busy": [{"day": "d1", "start_ts": 1754004600000, "end_ts": 1754006400000}],
    }
    (path / "inputs.json").write_text(json.dumps(sample, indent=2))
    console.print(f"[green]Wrote sample {(path/'inputs.json').as_posix()}")

@app.command()
def add_task(
    inputs: Path = typer.Argument(..., help="inputs.json path"),
    task_id: str = typer.Argument(...),
    duration: int = typer.Argument(..., help="minutes"),
    priority: int = typer.Argument(...),
    deadline: int = typer.Argument(..., help="unix ms"),
    deps: str = typer.Option("", help="comma-separated deps"),
):
    data = json.loads(inputs.read_text())
    dep_list = [d for d in deps.split(",") if d]
    data["tasks"].append(
        {"id": task_id, "duration_min": duration, "priority": priority, "deadline_ts": deadline, "deps": dep_list}
    )
    inputs.write_text(json.dumps(data, indent=2))
    console.print("[green]Added task.")

@app.command()
def set_deadline(inputs: Path, task_id: str, deadline: int):
    data = json.loads(inputs.read_text())
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["deadline_ts"] = deadline
    inputs.write_text(json.dumps(data, indent=2))
    console.print("[green]Updated deadline.")

@app.command()
def add_busy(inputs: Path, day: str, start: int, end: int):
    data = json.loads(inputs.read_text())
    data.setdefault("busy", []).append({"day": day, "start_ts": start, "end_ts": end})
    inputs.write_text(json.dumps(data, indent=2))
    console.print("[green]Added busy slot.")

@app.command()
def run(inputs: Path = typer.Argument(...), out: Path = typer.Option(Path("./schedule.csv"))):
    data = json.loads(inputs.read_text())
    inp = Inputs(
        tasks=[Task(**t) for t in data["tasks"]],
        work_window=WorkWindow(**data["work_window"]),
        busy=[BusySlot(**b) for b in data.get("busy", [])],
    )
    sched = schedule(inp)

    table = Table(title="Schedule")
    table.add_column("Task")
    table.add_column("Start (ms)")
    table.add_column("End (ms)")
    for s in sched:
        table.add_row(s.task_id, str(s.start_ts), str(s.end_ts))
    console.print(table)

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        f.write("task_id,start_ts,end_ts\n")
        for s in sched:
            f.write(f"{s.task_id},{s.start_ts},{s.end_ts}\n")
    console.print(f"[green]Wrote {out}")

if __name__ == "__main__":
    app()
    