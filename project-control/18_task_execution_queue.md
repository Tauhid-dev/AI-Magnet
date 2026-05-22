# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 2 tenant/database foundation.
2. Do not start Phase 3 unless explicitly instructed by the user.
3. When instructed, start Phase 3 with P3-T1: Enable pgvector and vector schema and P3-T2: Define AI provider abstraction where dependencies allow.
4. Record Phase 3 vector/AI provider decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| ROADMAP-FINAL | Update visual roadmap artifacts | Required at the end of every future phase execution | Parent Planning Agent, Documentation Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P3-T1 | Enable pgvector and vector schema | Phase 2 is ready for review; can start only after user instruction | RAG/AI Agent, Database Agent | Yes, with P3-T2 after instruction |
| P3-T2 | Define AI provider abstraction | Phase 1 config exists; can start only after user instruction | RAG/AI Agent, Backend Agent | Yes, with P3-T1 after instruction |
| P3-T1 and later | RAG/database/chat/frontend/admin tasks | Earlier phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Ready for review.
- Phase 3: Not started; waits for explicit user instruction.
- Phases 4 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 3 starts:

- P3-T1 and P3-T2 can proceed in parallel if schema/provider ownership is clear.
- P3-T3 waits for P3-T1 and P3-T2.
- P3-T4 waits for P3-T1 and P3-T2.
- P3-T5 waits for ingestion and retrieval services.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
