# Visual Roadmap System

## Purpose

This folder contains the deterministic visual phase tracker for the AI Tradie Receptionist Platform. It turns `roadmap_status.json` into a colourful PNG image that shows every project phase, phase status, key tasks, completion percentage, blockers, and summary counts.

The roadmap image should be regenerated after every phase execution so the project owner can track progress visually.

## Files

- `roadmap_status.json`: Source of truth for phase status and task progress.
- `generate_roadmap.py`: Local Python/Pillow image generator.
- `latest_roadmap.png`: Most recent generated roadmap image.
- `snapshots/`: Historical timestamped roadmap images.

## How roadmap_status.json works

Each phase entry includes:

- `phase_id`
- `phase_name`
- `status`
- `completion_percentage`
- `tasks`
- `completed_tasks`
- `pending_tasks`
- `blocked_tasks`
- `last_updated`
- `notes`

Allowed statuses:

- `NOT_STARTED`
- `IN_PROGRESS`
- `BLOCKED`
- `READY_FOR_REVIEW`
- `COMPLETE`

The optional top-level `active_phase_id` marks the current or next active phase for the visual highlight.

## Generate the roadmap

Run from the repository root:

```bash
python project-assets/roadmap/generate_roadmap.py
```

The script creates:

- A timestamped snapshot in `project-assets/roadmap/snapshots/`
- An updated `project-assets/roadmap/latest_roadmap.png`

## Phase update workflow

After every future phase execution:

1. Update `project-control/09_phase_execution_log.md`.
2. Update `project-control/12_phase_status_matrix.md`.
3. Update `project-control/13_quick_resume.md`.
4. Update `project-control/17_current_system_state.md`.
5. Update `project-assets/roadmap/roadmap_status.json`.
6. Run the roadmap generator.
7. Commit the new snapshot and updated `latest_roadmap.png`.

Do not overwrite historical snapshots. They provide a visual audit trail of project progress.
