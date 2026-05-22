# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 4 chat/widget foundation.
2. Do not start Phase 5 unless explicitly instructed by the user.
3. When instructed, start Phase 5 with frontend structure selection and business portal foundation.
4. Record Phase 5 frontend/auth decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P4 | Review Phase 4 branch | Phase 4 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P5-T1 | Select frontend structure | Phase 4 branch review/merge and explicit Phase 5 instruction | User instructs Phase 5 from latest `master` |
| P5-T2 and later | Business portal tasks | Phase 5 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P6 and later | Admin/notification/analytics tasks | Earlier MVP phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Ready for review.
- Phase 5: Not started; waits for explicit user instruction after Phase 4 review/merge.
- Phases 6 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 4 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 5 starts:

- Frontend structure selection should happen before large UI work.
- Portal shell and backend API contract review can proceed in parallel after structure is chosen.
- Knowledge, leads, conversations, widget setup, and analytics views should follow the available backend APIs.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
