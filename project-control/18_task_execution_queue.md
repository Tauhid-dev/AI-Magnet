# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 1 backend foundation.
2. Do not start Phase 2 unless explicitly instructed by the user.
3. When instructed, start Phase 2 with P2-T1: Select database and migration tooling.
4. Record the Phase 2 database tooling decision in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| ROADMAP-FINAL | Update visual roadmap artifacts | Required at the end of every future phase execution | Parent Planning Agent, Documentation Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P2-T1 | Select database and migration tooling | User approval/instruction for Phase 2 | Phase 1 branch reviewed/merged and user explicitly starts Phase 2 |
| P3-T1 and later | RAG/database/chat/frontend/admin tasks | Earlier phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Ready for review.
- Phase 2: Not started; waits for explicit user instruction.
- Phases 3 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 2 starts:

- P2-T2 and P2-T4 may proceed after P2-T1 if file ownership is clear.
- P2-T3 depends on P2-T2.
- P2-T5 waits for schema and data access helpers.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
