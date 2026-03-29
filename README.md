# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Task management** — add care tasks with title, duration, priority, scheduled time, frequency, and required status
- **Sorting by time** — task lists display in chronological order using each task's HH:MM time field; unscheduled tasks appear last
- **Filtering by status** — view only pending or completed tasks for any pet
- **Conflict warnings** — the app detects two or more tasks scheduled at the same time and surfaces a visible warning in the UI
- **Daily/weekly recurrence** — marking a recurring task complete automatically queues a fresh instance for the next occurrence
- **Schedule builder** — ranks tasks by required status, priority, and duration to fit within available time, then explains the chosen plan

## Smarter Scheduling

Phase 4 added lightweight algorithmic intelligence to the scheduler:

- `DailyScheduler.sort_by_time(tasks)` — uses `sorted()` with a lambda key on the HH:MM string; tasks without a time sort last via the sentinel value `"99:99"`
- `DailyScheduler.filter_tasks(tasks, status=...)` — list comprehension filter by task status
- `DailyScheduler.detect_conflicts(tasks)` — groups tasks by time into a dict and flags any time slot with more than one task; ignores unscheduled tasks
- `CareTask.mark_complete()` — returns a fresh `CareTask` copy when frequency is `daily` or `weekly`, letting the caller attach it to the pet's task list

**Tradeoff:** Conflict detection only checks for exact HH:MM matches. Two tasks scheduled at 08:00 and 08:15 will not be flagged even if their durations overlap. This keeps the logic simple and readable at the cost of missing partial overlaps.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Run the CLI demo

```bash
python main.py
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

Run the full test suite with:

```bash
source .venv/bin/activate
python -m pytest
```

The suite covers:

- **Task status** — `mark_complete` sets status to `"complete"`
- **Pet task count** — `add_task` correctly grows the task list
- **Sorting correctness** — `sort_by_time` returns tasks in HH:MM order; unscheduled tasks land last
- **Filtering** — `filter_tasks` isolates pending vs. complete tasks accurately
- **Conflict detection** — duplicate times produce a warning; distinct times and unscheduled tasks do not
- **Recurrence** — daily and weekly tasks produce a new pending instance on completion; once-only tasks do not

**Confidence level: ★★★★☆** — all 11 tests pass. The main untested gap is exact-overlap conflict detection (duration-based rather than time-point-based) and edge cases around the 24:00/midnight boundary for time sorting.

## 📸 Demo

<!-- Replace with your screenshot after running the app -->
<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
