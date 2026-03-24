from __future__ import annotations

from dataclasses import dataclass, field


PRIORITY_SCORES = {
    "high": 3,
    "medium": 2,
    "low": 1,
}


@dataclass
class CareTask:
    """Represents a single pet care activity that can be scheduled."""

    title: str
    duration_minutes: int
    priority: str
    is_required: bool = True
    status: str = field(default="pending", init=False)

    def __post_init__(self) -> None:
        """Validates and normalizes task data after initialization."""
        self.title = self.title.strip()
        self.priority = self.priority.strip().lower()

        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if self.priority not in PRIORITY_SCORES:
            raise ValueError("Task priority must be low, medium, or high.")

    def describe(self) -> str:
        """Returns a readable summary of the task details."""
        required_text = "required" if self.is_required else "optional"
        return (
            f"{self.title} takes {self.duration_minutes} minutes, "
            f"has {self.priority} priority, is {required_text}, "
            f"and is currently {self.status}."
        )

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.status = "complete"


@dataclass
class Pet:
    """Represents a pet and the care tasks assigned to it."""

    name: str
    species: str
    care_tasks: list[CareTask] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validates and normalizes pet data after initialization."""
        self.name = self.name.strip()
        self.species = self.species.strip().lower()

        if not self.name:
            raise ValueError("Pet name cannot be empty.")
        if not self.species:
            raise ValueError("Pet species cannot be empty.")

    def add_task(self, task: CareTask) -> None:
        """Adds a new care task to this pet."""
        self.care_tasks.append(task)

    def get_tasks(self) -> list[CareTask]:
        """Returns a copy of this pet's current task list."""
        return list(self.care_tasks)


@dataclass
class Owner:
    """Represents a pet owner with preferences and linked pets."""

    name: str
    preferences: dict[str, str] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validates owner data after initialization."""
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Owner name cannot be empty.")

    def add_pet(self, pet: Pet) -> None:
        """Associates a pet with this owner."""
        self.pets.append(pet)

    def set_preferences(self, preferences: dict[str, str]) -> None:
        """Replaces the owner's saved scheduling preferences."""
        self.preferences = dict(preferences)


@dataclass
class DailyScheduler:
    """Builds a daily care plan from a pet's available tasks."""

    available_minutes: int
    scheduled_tasks: list[CareTask] = field(default_factory=list, init=False)
    skipped_tasks: list[CareTask] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        """Validates the available scheduling time."""
        if self.available_minutes <= 0:
            raise ValueError("Available minutes must be greater than 0.")

    def build_schedule(self, owner: Owner, pet: Pet) -> list[CareTask]:
        """Selects ranked tasks that fit within the available time."""
        if pet not in owner.pets:
            raise ValueError("The selected pet does not belong to the owner.")

        ranked_tasks = self.rank_tasks(pet.get_tasks())
        self.scheduled_tasks = []
        self.skipped_tasks = []

        minutes_remaining = self.available_minutes

        for task in ranked_tasks:
            if task.duration_minutes <= minutes_remaining:
                self.scheduled_tasks.append(task)
                minutes_remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)

        return list(self.scheduled_tasks)

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        """Sorts tasks by required status, priority, and duration."""
        return sorted(
            tasks,
            key=lambda task: (
                not task.is_required,
                -PRIORITY_SCORES[task.priority],
                task.duration_minutes,
                task.title.lower(),
            ),
        )

    def explain_schedule(self, schedule: list[CareTask]) -> str:
        """Explains which tasks were scheduled and which were skipped."""
        if not schedule:
            return (
                "No tasks were scheduled. This usually means there were no tasks "
                "available or none fit within the available time."
            )

        total_minutes = sum(task.duration_minutes for task in schedule)
        lines = [
            f"Scheduled {len(schedule)} task(s) for a total of {total_minutes} minutes.",
            "Tasks were ordered by required status, priority, and shorter duration first.",
        ]

        for index, task in enumerate(schedule, start=1):
            lines.append(
                f"{index}. {task.title} ({task.duration_minutes} min, {task.priority} priority)"
            )

        if self.skipped_tasks:
            skipped_titles = ", ".join(task.title for task in self.skipped_tasks)
            lines.append(
                f"Skipped task(s) because of the time limit: {skipped_titles}."
            )

        return "\n".join(lines)
