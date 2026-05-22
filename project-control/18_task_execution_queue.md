# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 0 memory/context-recovery docs.
2. Start Phase 1 with P1-T1: Select backend tooling.
3. Record tooling decision in `10_decisions_log.md`.
4. Continue Phase 1 with backend foundation tasks.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| P1-T1 | Select backend tooling | Phase 0 planning docs exist; no app code required before decision | Backend Agent, QA/Test Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P1-T2 | Create FastAPI backend foundation | P1-T1 | Backend tooling decision recorded |
| P1-T3 | Add config and environment loading | P1-T1 | Backend tooling decision recorded |
| P1-T4 | Add health endpoint and logging | P1-T2, P1-T3 | Backend skeleton and config exist |
| P1-T5 | Add backend tests | P1-T2, P1-T4 | Backend skeleton and health endpoint exist |
| P2-T1 | Select database and migration tooling | Phase 1 foundation | Backend tooling selected and backend structure exists |
| P3-T1 and later | RAG/database/chat/frontend/admin tasks | Earlier phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Ready for review.
- Phase 1: Can begin after user explicitly instructs implementation planning or setup.
- Phases 2 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next task is a decision task.

After P1-T1:

- P1-T2 and P1-T3 may proceed in parallel if file ownership is clear.
- P1-T4 waits for P1-T2 and P1-T3.
- P1-T5 waits for P1-T2 and P1-T4.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
