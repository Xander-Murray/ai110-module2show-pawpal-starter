from pawpal_system import CareTask, Pet


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
