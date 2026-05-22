# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 6 super admin portal foundation.
2. Do not start Phase 7 unless explicitly instructed by the user.
3. When instructed, start Phase 7 with lead workflow and email notification provider decisions.
4. Record Phase 7 lead workflow, worker, and email provider decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P6 | Review Phase 6 branch | Phase 6 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P7-T1 | Define lead qualification workflow | Phase 6 branch review/merge and explicit Phase 7 instruction | User instructs Phase 7 from latest `master` |
| P7-T2 and later | Lead workflow and notification tasks | Phase 7 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P8 and later | Analytics/security/deployment tasks | Earlier MVP phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Complete.
- Phase 5: Complete.
- Phase 6: Ready for review.
- Phase 7: Not started; waits for explicit user instruction after Phase 6 review/merge.
- Phases 8 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 6 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 7 starts:

- Lead qualification workflow should happen before lifecycle implementation.
- Lead lifecycle and email provider abstraction can proceed in parallel after the workflow decision.
- Notification queue/retry behavior should follow the email provider and worker approach.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
