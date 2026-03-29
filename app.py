import streamlit as st

from pawpal_system import CareTask, DailyScheduler, Owner, Pet


def get_owner() -> Owner:
    """Returns the persistent owner stored for this browser session."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(name="Jordan")
    return st.session_state.owner


def find_pet(owner: Owner, pet_name: str) -> Pet | None:
    """Finds a pet by name using a case-insensitive lookup."""
    pet_name = pet_name.strip().lower()
    for pet in owner.pets:
        if pet.name.lower() == pet_name:
            return pet
    return None


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

owner = get_owner()

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ stores one owner for the current session, lets you add pets and care tasks,
and builds a daily plan using your scheduling logic.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

st.subheader("Owner Profile")
updated_owner_name = st.text_input("Owner name", value=owner.name).strip()
if updated_owner_name and updated_owner_name != owner.name:
    owner.name = updated_owner_name

preferred_start = st.text_input(
    "Preferred start time",
    value=owner.preferences.get("preferred_start", "08:00"),
)
owner.set_preferences({"preferred_start": preferred_start})

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("Pet name")
    new_pet_species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    try:
        if find_pet(owner, new_pet_name):
            st.error("A pet with that name already exists in this session.")
        else:
            owner.add_pet(Pet(name=new_pet_name, species=new_pet_species))
            st.success(f"Added {new_pet_name.strip()} to {owner.name}'s pets.")
    except ValueError as error:
        st.error(str(error))

if owner.pets:
    st.write("Current pets:")
    st.table(
        [{"Name": pet.name, "Species": pet.species.title(), "Tasks": len(pet.care_tasks)} for pet in owner.pets]
    )
else:
    st.info("No pets added yet. Add one to start building a care plan.")

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.caption("Add a pet before creating care tasks.")
else:
    pet_options = [pet.name for pet in owner.pets]
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_name = st.selectbox("Pet", pet_options)
        task_title = st.text_input("Task title")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        task_time = st.text_input("Scheduled time (HH:MM, optional)", value="")
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        is_required = st.checkbox("Required task", value=True)
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        selected_pet = find_pet(owner, selected_pet_name)
        if selected_pet is None:
            st.error("Choose a valid pet before adding a task.")
        else:
            try:
                selected_pet.add_task(
                    CareTask(
                        title=task_title,
                        duration_minutes=int(duration),
                        priority=priority,
                        is_required=is_required,
                        time=task_time.strip(),
                        frequency=frequency,
                    )
                )
                st.success(f"Added {task_title.strip()} for {selected_pet.name}.")
            except ValueError as error:
                st.error(str(error))

    scheduler = DailyScheduler(available_minutes=60)

    for pet in owner.pets:
        st.markdown(f"### {pet.name} the {pet.species.title()}")

        if not pet.care_tasks:
            st.info(f"No tasks for {pet.name} yet.")
            continue

        # Detect and show any scheduling conflicts before the task table.
        conflicts = scheduler.detect_conflicts(pet.get_tasks())
        for warning in conflicts:
            st.warning(warning)

        # Display tasks sorted chronologically by scheduled time.
        sorted_tasks = scheduler.sort_by_time(pet.get_tasks())
        st.table(
            [
                {
                    "Task": task.title,
                    "Time": task.time if task.time else "--",
                    "Minutes": task.duration_minutes,
                    "Priority": task.priority.title(),
                    "Frequency": task.frequency.title(),
                    "Required": "Yes" if task.is_required else "No",
                    "Status": task.status.title(),
                }
                for task in sorted_tasks
            ]
        )

        # Mark-complete controls with recurrence handling.
        pending_tasks = scheduler.filter_tasks(pet.get_tasks(), status="pending")
        if pending_tasks:
            st.markdown("**Mark a task complete:**")
            task_to_complete = st.selectbox(
                "Select task",
                [t.title for t in pending_tasks],
                key=f"complete_select_{pet.name}",
            )
            if st.button("Mark complete", key=f"complete_btn_{pet.name}"):
                # Find the actual task object in pet.care_tasks (not a copy).
                for task in pet.care_tasks:
                    if task.title == task_to_complete and task.status == "pending":
                        next_task = task.mark_complete()
                        if next_task:
                            pet.add_task(next_task)
                            st.success(
                                f'"{task_to_complete}" marked complete. '
                                f"A new {task.frequency} instance has been added."
                            )
                        else:
                            st.success(f'"{task_to_complete}" marked complete.')
                        break
                st.rerun()

st.divider()

st.subheader("Build Schedule")
if not owner.pets:
    st.caption("Add at least one pet before generating a schedule.")
else:
    schedule_pet_name = st.selectbox("Pet to schedule", [pet.name for pet in owner.pets], key="schedule_pet")
    available_minutes = st.number_input(
        "Available time today (minutes)",
        min_value=1,
        max_value=480,
        value=60,
    )

    if st.button("Generate schedule"):
        selected_pet = find_pet(owner, schedule_pet_name)
        if selected_pet is None:
            st.error("Choose a valid pet to build a schedule.")
        elif not selected_pet.care_tasks:
            st.warning(f"{schedule_pet_name} does not have any tasks yet.")
        else:
            sched = DailyScheduler(available_minutes=int(available_minutes))
            schedule = sched.build_schedule(owner, selected_pet)

            # Show any time conflicts for the scheduled tasks.
            conflicts = sched.detect_conflicts(schedule)
            for warning in conflicts:
                st.warning(f"Scheduling conflict: {warning}")

            if schedule:
                st.success(f"Built a schedule with {len(schedule)} task(s).")
                # Sort the final plan by scheduled time before displaying.
                display_schedule = sched.sort_by_time(schedule)
                st.table(
                    [
                        {
                            "Order": index,
                            "Task": task.title,
                            "Time": task.time if task.time else "--",
                            "Minutes": task.duration_minutes,
                            "Priority": task.priority.title(),
                            "Required": "Yes" if task.is_required else "No",
                        }
                        for index, task in enumerate(display_schedule, start=1)
                    ]
                )
            else:
                st.warning("No tasks fit within the available time.")

            st.markdown("### Why this plan was chosen")
            st.text(sched.explain_schedule(schedule))
