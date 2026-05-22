# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 5 business portal foundation.
2. Do not start Phase 6 unless explicitly instructed by the user.
3. When instructed, start Phase 6 with super admin role model and protected admin portal foundation.
4. Record Phase 6 admin role, routing, and audit decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P5 | Review Phase 5 branch | Phase 5 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P6-T1 | Define super admin role model | Phase 5 branch review/merge and explicit Phase 6 instruction | User instructs Phase 6 from latest `master` |
| P6-T2 and later | Super admin portal tasks | Phase 6 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P7 and later | Notification/analytics/security tasks | Earlier MVP phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Complete.
- Phase 5: Ready for review.
- Phase 6: Not started; waits for explicit user instruction after Phase 5 review/merge.
- Phases 7 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 5 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 6 starts:

- Super admin role model should happen before protected admin UI work.
- Admin API contract review and frontend route shell can proceed in parallel after the role decision.
- Tenant list/detail, tenant status management, usage overview, system health, and audit logging views should follow the agreed admin authorization contract.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
