from dataclasses import dataclass, field


@dataclass
class CareTask:
    title: str
    duration_minutes: int
    priority: str
    is_required: bool = True

    def describe(self) -> str:
        return (
            f"{self.title} takes {self.duration_minutes} minutes "
            f"and has {self.priority} priority."
        )


@dataclass
class Pet:
    name: str
    species: str
    care_tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        self.care_tasks.append(task)

    def get_tasks(self) -> list[CareTask]:
        return self.care_tasks


@dataclass
class Owner:
    name: str
    preferences: dict[str, str] = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def set_preferences(self, preferences: dict[str, str]) -> None:
        self.preferences = preferences


@dataclass
class DailyScheduler:
    available_minutes: int

    def build_schedule(self, owner: Owner, pet: Pet) -> list[CareTask]:
        raise NotImplementedError("Scheduling logic has not been implemented yet.")

    def rank_tasks(self, tasks: list[CareTask]) -> list[CareTask]:
        raise NotImplementedError("Task ranking has not been implemented yet.")

    def explain_schedule(self, schedule: list[CareTask]) -> str:
        raise NotImplementedError("Schedule explanation has not been implemented yet.")
