from datetime import date

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


def build_sample_owner() -> Owner:
    owner = Owner(name="Jordan", preferences={"preferred_start": "08:00"})

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(CareTask(title="Breakfast", duration_minutes=15, priority="high"))
    mochi.add_task(CareTask(title="Morning walk", duration_minutes=25, priority="high"))
    mochi.add_task(
        CareTask(
            title="Fetch practice",
            duration_minutes=20,
            priority="medium",
            is_required=False,
        )
    )

    luna = Pet(name="Luna", species="cat")
    luna.add_task(CareTask(title="Wet food", duration_minutes=10, priority="high"))
    luna.add_task(CareTask(title="Litter cleanup", duration_minutes=12, priority="high"))
    luna.add_task(
        CareTask(
            title="Window play time",
            duration_minutes=18,
            priority="low",
            is_required=False,
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)
    return owner


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

    print_pet_schedule(owner, owner.pets[0], available_minutes=40)
    print_pet_schedule(owner, owner.pets[1], available_minutes=25)


if __name__ == "__main__":
    main()
