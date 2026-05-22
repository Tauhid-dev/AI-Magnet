# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 8 analytics and usage tracking foundation.
2. Do not start Phase 9 unless explicitly instructed by the user.
3. When instructed, start Phase 9 with tenant isolation and security review.
4. Record Phase 9 security, testing, CI, or deployment decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P8 | Review Phase 8 branch | Phase 8 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P9-T1 | Run tenant isolation and security review | Phase 8 branch review/merge and explicit Phase 9 instruction | User instructs Phase 9 from latest `master` |
| P9-T2 and later | Security, testing, CI, and deployment tasks | Phase 9 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P10 and later | Premium/future modules | MVP stability, customer demand validation, and explicit approval | Complete dependencies in `03_task_dependency_graph.md` and receive explicit approval |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Complete.
- Phase 5: Complete.
- Phase 6: Complete.
- Phase 7: Complete.
- Phase 8: Ready for review.
- Phase 9: Not started; waits for explicit user instruction after Phase 8 review/merge.
- Phase 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 8 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 9 starts:

- Tenant isolation and security review should happen before CI/deployment hardening.
- Backend security fixes, frontend test expansion, and deployment documentation can proceed in parallel only after review findings are known and scoped.
- CI pipeline work should run after test/lint commands are confirmed.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
