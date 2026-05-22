# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 7 notifications and lead workflow foundation.
2. Do not start Phase 8 unless explicitly instructed by the user.
3. When instructed, start Phase 8 with usage event taxonomy and analytics query decisions.
4. Record Phase 8 analytics decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P7 | Review Phase 7 branch | Phase 7 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P8-T1 | Define usage event taxonomy | Phase 7 branch review/merge and explicit Phase 8 instruction | User instructs Phase 8 from latest `master` |
| P8-T2 and later | Analytics and usage tracking tasks | Phase 8 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P9 and later | Security/deployment tasks | Earlier MVP phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Complete.
- Phase 5: Complete.
- Phase 6: Complete.
- Phase 7: Ready for review.
- Phase 8: Not started; waits for explicit user instruction after Phase 7 review/merge.
- Phases 9 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 7 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 8 starts:

- Usage event taxonomy should happen before analytics query and dashboard expansion.
- Backend usage aggregation and frontend analytics display can proceed in parallel after API contracts are defined.
- Tenant-scoped analytics tests should follow the analytics query implementation.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
