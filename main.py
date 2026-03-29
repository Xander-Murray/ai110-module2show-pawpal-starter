from datetime import date

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


def build_sample_owner() -> Owner:
    owner = Owner(name="Jordan", preferences={"preferred_start": "08:00"})

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(CareTask(title="Breakfast", duration_minutes=15, priority="high", time="08:00", frequency="daily"))
    mochi.add_task(CareTask(title="Morning walk", duration_minutes=25, priority="high", time="08:30", frequency="daily"))
    mochi.add_task(
        CareTask(
            title="Fetch practice",
            duration_minutes=20,
            priority="medium",
            is_required=False,
            time="09:00",
            frequency="weekly",
        )
    )
    # Intentional conflict: same time as Morning walk to demo detect_conflicts
    mochi.add_task(CareTask(title="Flea treatment", duration_minutes=10, priority="high", time="08:30", frequency="once"))

    luna = Pet(name="Luna", species="cat")
    luna.add_task(CareTask(title="Wet food", duration_minutes=10, priority="high", time="07:30", frequency="daily"))
    luna.add_task(CareTask(title="Litter cleanup", duration_minutes=12, priority="high", time="12:00", frequency="daily"))
    luna.add_task(
        CareTask(
            title="Window play time",
            duration_minutes=18,
            priority="low",
            is_required=False,
            time="15:00",
            frequency="weekly",
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner


def demo_sorting(scheduler: DailyScheduler, pet: Pet) -> None:
    print(f"--- Tasks sorted by time for {pet.name} ---")
    sorted_tasks = scheduler.sort_by_time(pet.get_tasks())
    for task in sorted_tasks:
        time_label = task.time if task.time else "(no time)"
        print(f"  {time_label}  {task.title} ({task.duration_minutes} min)")
    print()


def demo_filtering(scheduler: DailyScheduler, pet: Pet) -> None:
    print(f"--- Pending tasks for {pet.name} ---")
    pending = scheduler.filter_tasks(pet.get_tasks(), status="pending")
    for task in pending:
        print(f"  {task.title} — {task.status}")
    print()


def demo_conflicts(scheduler: DailyScheduler, pet: Pet) -> None:
    print(f"--- Conflict detection for {pet.name} ---")
    warnings = scheduler.detect_conflicts(pet.get_tasks())
    if warnings:
        for warning in warnings:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts detected.")
    print()


def demo_recurrence(pet: Pet) -> None:
    print(f"--- Recurring task demo for {pet.name} ---")
    task = pet.care_tasks[0]
    print(f"  Completing '{task.title}' (frequency: {task.frequency})")
    next_task = task.mark_complete()
    print(f"  Status after: {task.status}")
    if next_task:
        print(f"  New recurring instance created: '{next_task.title}', status: {next_task.status}")
        pet.add_task(next_task)
        print(f"  Pet now has {len(pet.care_tasks)} tasks.")
    else:
        print("  No recurrence (frequency=once).")
    print()


def print_pet_schedule(owner: Owner, pet: Pet, available_minutes: int) -> None:
    scheduler = DailyScheduler(available_minutes=available_minutes)
    schedule = scheduler.build_schedule(owner, pet)

    print(f"{pet.name} the {pet.species.title()}")
    print(f"Available time: {available_minutes} minutes")

    if schedule:
        for index, task in enumerate(schedule, start=1):
            print(
                f"  {index}. {task.title} - {task.duration_minutes} minutes "
                f"({task.priority} priority)"
            )
    else:
        print("  No tasks fit into today's schedule.")

    print(scheduler.explain_schedule(schedule))
    print()


def main() -> None:
    owner = build_sample_owner()
    today = date.today().strftime("%B %d, %Y")

    print(f"Today's PawPal+ schedule for {owner.name}")
    print(today)
    print()

    scheduler = DailyScheduler(available_minutes=60)

    # Demo Phase 4 algorithms
    demo_sorting(scheduler, owner.pets[0])
    demo_filtering(scheduler, owner.pets[0])
    demo_conflicts(scheduler, owner.pets[0])
    demo_recurrence(owner.pets[1])

    # Original schedule output
    print_pet_schedule(owner, owner.pets[0], available_minutes=40)
    print_pet_schedule(owner, owner.pets[1], available_minutes=25)


if __name__ == "__main__":
    main()
