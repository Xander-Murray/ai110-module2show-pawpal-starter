from pawpal_system import CareTask, DailyScheduler, Owner, Pet


# --- Original tests ---

def test_mark_complete_changes_task_status() -> None:
    task = CareTask(title="Breakfast", duration_minutes=15, priority="high")

    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "complete"


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    first_task = CareTask(title="Morning walk", duration_minutes=20, priority="high")
    second_task = CareTask(title="Brush coat", duration_minutes=10, priority="medium")

    assert len(pet.get_tasks()) == 0

    pet.add_task(first_task)
    assert len(pet.get_tasks()) == 1

    pet.add_task(second_task)
    assert len(pet.get_tasks()) == 2


# --- Phase 4: Sorting ---

def test_sort_by_time_returns_chronological_order() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    t1 = CareTask(title="Evening walk", duration_minutes=20, priority="medium", time="17:00")
    t2 = CareTask(title="Breakfast", duration_minutes=15, priority="high", time="08:00")
    t3 = CareTask(title="Lunch", duration_minutes=10, priority="low", time="12:30")

    sorted_tasks = scheduler.sort_by_time([t1, t2, t3])

    assert [t.time for t in sorted_tasks] == ["08:00", "12:30", "17:00"]


def test_sort_by_time_puts_unscheduled_tasks_last() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    timed = CareTask(title="Walk", duration_minutes=20, priority="high", time="09:00")
    untimed = CareTask(title="Groom", duration_minutes=10, priority="low")

    sorted_tasks = scheduler.sort_by_time([untimed, timed])

    assert sorted_tasks[0].title == "Walk"
    assert sorted_tasks[1].title == "Groom"


# --- Phase 4: Filtering ---

def test_filter_tasks_by_status_returns_only_matching() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    pending_task = CareTask(title="Feed", duration_minutes=10, priority="high")
    done_task = CareTask(title="Walk", duration_minutes=20, priority="medium")
    done_task.mark_complete()

    pending_results = scheduler.filter_tasks([pending_task, done_task], status="pending")
    complete_results = scheduler.filter_tasks([pending_task, done_task], status="complete")

    assert len(pending_results) == 1
    assert pending_results[0].title == "Feed"
    assert len(complete_results) == 1
    assert complete_results[0].title == "Walk"


# --- Phase 4: Conflict detection ---

def test_detect_conflicts_flags_duplicate_times() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    t1 = CareTask(title="Morning walk", duration_minutes=25, priority="high", time="08:30")
    t2 = CareTask(title="Flea treatment", duration_minutes=10, priority="high", time="08:30")
    t3 = CareTask(title="Breakfast", duration_minutes=15, priority="high", time="08:00")

    warnings = scheduler.detect_conflicts([t1, t2, t3])

    assert len(warnings) == 1
    assert "08:30" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Flea treatment" in warnings[0]


def test_detect_conflicts_returns_empty_when_no_conflicts() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    t1 = CareTask(title="Walk", duration_minutes=20, priority="high", time="08:00")
    t2 = CareTask(title="Feed", duration_minutes=10, priority="high", time="09:00")

    warnings = scheduler.detect_conflicts([t1, t2])

    assert warnings == []


def test_detect_conflicts_ignores_unscheduled_tasks() -> None:
    scheduler = DailyScheduler(available_minutes=60)
    t1 = CareTask(title="Walk", duration_minutes=20, priority="high")
    t2 = CareTask(title="Feed", duration_minutes=10, priority="high")

    # Both have no time — should not be flagged as a conflict
    warnings = scheduler.detect_conflicts([t1, t2])

    assert warnings == []


# --- Phase 4: Recurrence ---

def test_daily_task_creates_new_instance_on_complete() -> None:
    task = CareTask(title="Wet food", duration_minutes=10, priority="high", frequency="daily")

    next_task = task.mark_complete()

    assert task.status == "complete"
    assert next_task is not None
    assert next_task.status == "pending"
    assert next_task.title == "Wet food"
    assert next_task.frequency == "daily"


def test_weekly_task_creates_new_instance_on_complete() -> None:
    task = CareTask(title="Bath", duration_minutes=30, priority="medium", frequency="weekly")

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.frequency == "weekly"
    assert next_task.status == "pending"


def test_once_task_does_not_create_recurrence() -> None:
    task = CareTask(title="Vet checkup", duration_minutes=60, priority="high", frequency="once")

    next_task = task.mark_complete()

    assert task.status == "complete"
    assert next_task is None
