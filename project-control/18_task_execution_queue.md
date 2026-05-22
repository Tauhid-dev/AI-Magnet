# Task Execution Queue

## Queue purpose

This file helps the parent agent choose the next executable tasks without re-reading the entire roadmap and dependency graph.

## Current recommended execution order

1. Review and merge Phase 9 security, testing, CI, and deployment foundation.
2. Do not start Phase 10 unless explicitly instructed by the user.
3. When instructed, start Phase 10 with future-module research and scoping only.
4. Record Phase 10 premium/future-module decisions in `10_decisions_log.md`.
5. At the end of every phase, update `project-assets/roadmap/roadmap_status.json` and run `python project-assets/roadmap/generate_roadmap.py`.

## Ready tasks

| Task ID | Task name | Why ready | Recommended role | Parallel-safe |
|---|---|---|---|---|
| REVIEW-P9 | Review Phase 9 branch | Phase 9 implementation and validation are complete locally | Parent Planning Agent | No |

## Blocked tasks

| Task ID | Task name | Blocked by | Unblock condition |
|---|---|---|---|
| P10-T1 | Research voice AI module | Phase 9 branch review/merge and explicit Phase 10 approval | User instructs Phase 10 research from latest `master` |
| P10-T2 | Research SMS and WhatsApp modules | Phase 9 branch review/merge and explicit Phase 10 approval | User instructs Phase 10 research from latest `master` |
| P10-T3 | Research billing module | Phase 9 branch review/merge and explicit Phase 10 approval | User instructs Phase 10 research from latest `master` |
| P10-T4 | Research automation and local model support | Phase 9 branch review/merge and explicit Phase 10 approval | User instructs Phase 10 research from latest `master` |

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
- Phase 9: Ready for review.
- Phase 10: Not started; waits for explicit user instruction after Phase 9 review/merge.

## Tasks safe for parallel execution

Currently none, because the next step is Phase 9 review/merge rather than implementation.

Roadmap updates should happen after phase work and memory updates are complete, so they should not run in parallel with status-changing tasks.

After Phase 10 starts:

- Phase 10 tasks are research/scoping tasks unless the user explicitly approves implementation.
- Voice, messaging, billing, and automation research can run in parallel because their output files are separate.
- Do not implement Voice AI, WhatsApp, SMS, Stripe, n8n, mobile apps, marketplace, or multi-region infrastructure without a new explicit instruction.

## Queue update rules

- Update this file when a task moves from blocked to ready.
- Keep only near-term executable tasks detailed.
- Use `03_task_dependency_graph.md` as the source of truth for full dependency details.
- Do not duplicate the whole task graph here.
