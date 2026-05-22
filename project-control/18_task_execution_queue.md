# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 3 RAG ingestion/retrieval foundation.
2. Do not start Phase 4 unless explicitly instructed by the user.
3. When instructed, start Phase 4 with widget authentication and conversation API contract tasks.
4. Record Phase 4 chat/widget API decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P3 | Review Phase 3 branch | Phase 3 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P4-T1 | Define widget authentication contract | Phase 3 branch review/merge and explicit Phase 4 instruction | User instructs Phase 4 from latest `master` |
| P4-T2 and later | Chat/widget tasks | Phase 4 task dependencies and explicit instruction | Complete dependencies in `03_task_dependency_graph.md` |
| P5 and later | Frontend/admin/notification/analytics tasks | Earlier MVP phases | Complete dependencies in `03_task_dependency_graph.md` |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Ready for review.
- Phase 4: Not started; waits for explicit user instruction after Phase 3 review/merge.
- Phases 5 through 10: Not ready.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 3 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 4 starts:

- Contract/API design and widget UI planning can be split by Backend Agent and Frontend Agent.
- Conversation API implementation should wait for the authentication/widget contract.
- AI answer generation can use the Phase 3 retrieval and chat provider abstractions.
- Chat/widget tests should wait for the API and widget surfaces they validate.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
