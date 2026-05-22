# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 10 premium/future modules planning.
2. Start any future instruction from latest `master`.
3. Do not implement premium/future modules unless the user explicitly requests a specific module.
4. When a premium module is requested, start from the matching `docs/future-modules/` plan and record new decisions in `10_decisions_log.md`.
5. At the end of every future phase or major instruction, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P10 | Review Phase 10 planning branch | Phase 10 future-module planning docs are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| None | No blocked numbered phase tasks | All planned Phase 10 research/scoping tasks are complete | New implementation tasks require explicit user instruction |

## Dependency status

- Phase 0: Complete.
- Phase 1: Complete.
- Phase 2: Complete.
- Phase 3: Complete.
- Phase 4: Complete.
- Phase 5: Complete.
- Phase 6: Complete.
- Phase 7: Complete.
- Phase 8: Complete.
- Phase 9: Complete and merged to `master`.
- Phase 10: Ready for review.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 10 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 10 review:

- Future premium-module implementation tasks can be split by module only after explicit instruction.
- Voice, messaging, billing, automation, CRM, local-model, and multi-region work should stay separate because they have different privacy, cost, and operational risks.
- Do not implement Voice AI, WhatsApp, SMS, Stripe, n8n, CRM integrations, mobile apps, marketplace, local model/Ollama support, or multi-region infrastructure without a new explicit instruction.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
