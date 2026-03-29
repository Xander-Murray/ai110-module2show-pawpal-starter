# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

3 core actions include adding owner and pet info, track tasks, produce a daily plan

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design models the core parts of the PawPal+ system: the person using the app, the pet receiving care, the tasks
that need to be done, and the component that builds a daily plan. I kept it small on purpose so the design stays easy to
implement and matches the project requirements.

The classes I included were Owner, Pet, CareTask, and DailyScheduler. Owner is responsible for storing the pet owner's name,
preferences, and linked pets. Pet represents an individual pet and keeps track of its care tasks. CareTask represents a single
care activity such as feeding or walking, including duration, priority, and whether it is required. DailyScheduler is
responsible for the planning logic: ranking tasks, building a schedule based on available time and preferences, and explaining
why tasks were chosen.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. CareTask grew two new fields — `time` (HH:MM string) and `frequency` (once/daily/weekly) — that were not in the initial
design. The `time` field was needed to make sorting and conflict detection meaningful; without a scheduled time, "sort by time"
has nothing to sort. The `frequency` field was added so that recurring care activities (daily feeding, weekly baths) could
auto-queue a fresh task when marked complete, removing the need for the user to re-enter the same task every day.

DailyScheduler also gained three new methods: `sort_by_time`, `filter_tasks`, and `detect_conflicts`. These were not in the
original UML because the initial design focused only on building and explaining a schedule, not on presenting or auditing it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers available time in minutes (hard cap — tasks that exceed remaining time are skipped), task priority
(high > medium > low), whether a task is required, and task duration (shorter tasks are preferred when priority is equal so
more tasks fit in the window). Required tasks are always ranked above optional ones regardless of priority.

Available time was treated as the most important constraint because it is the real-world bottleneck: a pet owner who has
30 minutes cannot do 90 minutes of care no matter how high the priority. Priority and required status were next because they
encode what the pet actually needs to stay healthy. Duration as a tiebreaker was a practical choice to maximize the number of
tasks completed in the available window.

**b. Tradeoffs**

The conflict detector uses exact HH:MM point-in-time matching rather than checking whether task durations overlap. This means
two tasks scheduled at 08:00 and 08:15 will not be flagged even if the first task takes 30 minutes and clearly runs into the
second. The exact-match approach is simple, easy to understand, and impossible to accidentally mis-trigger, but it misses real
overlaps caused by long durations. For a student scheduling app this tradeoff is reasonable: the primary goal is to warn users
about obvious double-bookings (same start time), not to build a full calendar conflict engine. A future version could extend
the check by computing end times from duration and comparing intervals.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI was used for design brainstorming (exploring which algorithmic features to add), implementation (generating method
skeletons for sort_by_time and detect_conflicts), and test generation (drafting edge case tests for recurrence and conflict
logic). The most effective prompts were specific and constrained: asking for "a lightweight conflict detection strategy that
returns a warning message rather than crashing the program" produced a cleaner result than asking generically for
"conflict detection." Asking the AI to explain its suggestion before accepting it also helped catch cases where the logic
was correct but the naming was unclear.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI initially suggested making `detect_conflicts` raise a `ValueError` when a conflict was found, which would crash the
app. That approach was rejected because the assignment explicitly asked for a "warning message rather than crashing the
program." The method was rewritten to return a list of warning strings so the caller (UI or CLI) can decide how to display
them. The decision was verified by running the demo in `main.py` and confirming that conflicting tasks printed a warning
without stopping execution.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Tested: task status changes on `mark_complete`, task count growth via `add_task`, chronological sort order from
`sort_by_time` (including unscheduled tasks landing last), status filtering via `filter_tasks`, conflict detection for
duplicate times and absence of false positives, and recurrence behavior for once/daily/weekly frequencies.

These tests matter because they cover the four new algorithmic features added in Phase 4. Without them there is no way to
confirm that sort_by_time handles the "no time" edge case correctly or that a weekly task actually resets instead of staying
complete.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence: ★★★★☆ — all 11 automated tests pass and the CLI demo confirms end-to-end behavior. The main gap is that conflict
detection does not account for overlapping durations, only exact start times. Next tests to add: midnight/wrap-around times
(e.g., 23:45 task with 30-minute duration), a pet with zero tasks passed to `detect_conflicts`, and an owner whose available
time exactly equals one task's duration (boundary condition for the schedule builder).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The recurrence design is the part I am most satisfied with. Having `mark_complete` return a new `CareTask` rather than
mutating the pet's task list directly keeps each method focused on a single responsibility and makes the behavior easy to
test in isolation.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Conflict detection would be extended to compare intervals (start time + duration) rather than just start times. I would also
add a `date` field to `CareTask` so recurring tasks could be tracked across days rather than just within a single session.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is most useful when you already have a clear mental model of what you want to build. When I gave the AI a vague prompt
("add conflict detection"), the output needed significant rework. When I gave it a specific constraint ("return a warning
string, do not raise an exception"), it produced code that fit cleanly into the existing design. The human's job is to stay
the lead architect: define the interface first, then let AI fill in the implementation details.
