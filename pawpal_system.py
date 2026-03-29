from __future__ import annotations

from dataclasses import dataclass, field


PRIORITY_SCORES = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

VALID_FREQUENCIES = {"once", "daily", "weekly"}


@dataclass
class CareTask:
    """Represents a single pet care activity that can be scheduled."""

    title: str
    duration_minutes: int
    priority: str
    is_required: bool = True
    # Optional scheduled time in HH:MM format; empty string means unscheduled.
    time: str = ""
    # How often the task repeats: once, daily, or weekly.
    frequency: str = "once"
    status: str = field(default="pending", init=False)

    def __post_init__(self) -> None:
        """Validates and normalizes task data after initialization."""
        self.title = self.title.strip()
        self.priority = self.priority.strip().lower()
        self.time = self.time.strip()
        self.frequency = self.frequency.strip().lower()

        if not self.title:
            raise ValueError("Task title cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than 0 minutes.")
        if self.priority not in PRIORITY_SCORES:
            raise ValueError("Task priority must be low, medium, or high.")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError("Task frequency must be once, daily, or weekly.")
        if self.time and not _is_valid_time(self.time):
            raise ValueError("Task time must be in HH:MM format (e.g. 08:30).")

    def describe(self) -> str:
        """Returns a readable summary of the task details."""
        required_text = "required" if self.is_required else "optional"
        time_text = f" at {self.time}" if self.time else ""
        return (
            f"{self.title} takes {self.duration_minutes} minutes{time_text}, "
            f"has {self.priority} priority, is {required_text}, "
            f"recurs {self.frequency}, and is currently {self.status}."
        )

    def mark_complete(self) -> CareTask | None:
        """Marks the task complete and returns a new recurring instance if applicable.

        Returns a fresh CareTask for the next occurrence when frequency is
        'daily' or 'weekly', otherwise returns None.
        """
        self.status = "complete"
        if self.frequency in {"daily", "weekly"}:
            return CareTask(
                title=self.title,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                is_required=self.is_required,
                time=self.time,
                frequency=self.frequency,
            )
        return None


def _is_valid_time(value: str) -> bool:
    """Returns True if value is a valid HH:MM time string."""
    parts = value.split(":")
    if len(parts) != 2:
        return False
    hh, mm = parts
    if not (hh.isdigit() and mm.isdigit()):
        return False
    return 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59


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

    def sort_by_time(self, tasks: list[CareTask]) -> list[CareTask]:
        """Sorts tasks chronologically by their scheduled time.

        Tasks without a time value sort to the end of the list.
        """
        return sorted(
            tasks,
            key=lambda task: task.time if task.time else "99:99",
        )

    def filter_tasks(
        self,
        tasks: list[CareTask],
        *,
        status: str | None = None,
        pet_name: str | None = None,
        pet: Pet | None = None,
    ) -> list[CareTask]:
        """Returns tasks matching the given filters.

        Args:
            tasks: The task list to filter.
            status: If provided, keep only tasks whose status matches.
            pet_name: Unused at this level; present for API symmetry when
                callers pass a name string (filtering by pet is done by
                selecting the right pet's task list upstream).
            pet: Unused at this level; same rationale as pet_name.
        """
        result = tasks
        if status is not None:
            result = [t for t in result if t.status == status]
        return result

    def detect_conflicts(self, tasks: list[CareTask]) -> list[str]:
        """Returns warning strings for any tasks scheduled at the same time.

        Only tasks with an explicit time value are checked; unscheduled tasks
        are ignored. This is a lightweight exact-match check — it flags
        identical HH:MM values but does not compute overlapping durations.
        """
        time_map: dict[str, list[str]] = {}
        for task in tasks:
            if task.time:
                time_map.setdefault(task.time, []).append(task.title)

        warnings = []
        for time_value, titles in time_map.items():
            if len(titles) > 1:
                joined = ", ".join(f'"{t}"' for t in titles)
                warnings.append(
                    f"Conflict at {time_value}: {joined} are all scheduled at the same time."
                )
        return warnings

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
