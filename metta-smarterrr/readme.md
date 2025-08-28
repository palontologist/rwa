metta-smarter: EDF + Priority Task Scheduler (Python toy)


This is a minimal, dependency-aware scheduler that:
- Automated Task Ordering: optimal sequence based on dependencies, deadlines, priorities
- Dependency Management: schedule only when all prerequisites are done
- Deadline Optimization: earliest-deadline-first (EDF) urgency in the score
- Efficient Time Allocation: greedy packing into free day slots
- Dynamic Adjustments: re-run after any change to recompute plan

Model
- Task: id, duration_min, priority, deadline_ts, deps[] (Unix ms)
- WorkWindow: day, start_ts, end_ts
- BusySlot: day, start_ts, end_ts
- ScheduleEntry: task_id, start_ts, end_ts


pip install -r requirements.txt

Quick start
python cli.py init
python cli.py run inputs.json --out out/schedule.csv

Dynamic adjustments
python cli.py add-task inputs.json T4 45 4 1754010000000 --deps T1
python cli.py set-deadline inputs.json T2 1754006000000
python cli.py add-busy inputs.json d1 1754010000000 1754011800000
python cli.py run inputs.json --out out/schedule.csv

How it works
- Readiness: ready when all deps are done
- Scoring: score = 2*priority + 1/(deadline-now)
- Placement: greedy earliest fit in free slots
- Errors: cycle/no-ready or no-fit

metta-smarter (MeTTa-based scheduler)

- Tasks as MeTTa facts; EDF + priority scoring; greedy packing into free slots.
- Dependencies respected; deadlines prioritized; dynamic: re-run after changes.

Quick start
1) python3 -m venv .venv && source .venv/bin/activate
2) pip install -r metta-smarter/requirements.txt
3) python metta-smarter/cli.py run

Edit tasks
- Update metta-smarter/tasks.metta (add (task ...), (duration ...), (priority ...), (deadline ...), (depends ...)).
- Re-run: python metta-smarter/cli.py run

Roasts
- LLM roast via MeTTa-Motto (chat-gpt-agent) with mild|medium|hot spice.
- Requires `motto` and your LLM key (e.g., OPENAI_API_KEY or OPENROUTER_API_KEY).

Notes
- Custom atoms (timems!, //) from python_ext.py are auto-registered.
- Output shows (assign T start end) rows for the chosen day (e.g., d1).