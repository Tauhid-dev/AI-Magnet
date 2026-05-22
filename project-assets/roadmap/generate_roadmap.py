#!/usr/bin/env python3
"""Generate a deterministic visual roadmap from roadmap_status.json."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
STATUS_FILE = ROOT / "roadmap_status.json"
SNAPSHOT_DIR = ROOT / "snapshots"
LATEST_FILE = ROOT / "latest_roadmap.png"

CANVAS_WIDTH = 2200
MARGIN = 64
GUTTER = 36
CARD_WIDTH = (CANVAS_WIDTH - (MARGIN * 2) - GUTTER) // 2
CARD_HEIGHT = 370
CARD_RADIUS = 8

STATUS_STYLES = {
    "COMPLETE": {
        "fill": (231, 248, 238),
        "border": (33, 150, 83),
        "badge": (33, 150, 83),
        "text": (20, 96, 55),
    },
    "IN_PROGRESS": {
        "fill": (229, 241, 255),
        "border": (45, 118, 220),
        "badge": (45, 118, 220),
        "text": (25, 79, 154),
    },
    "BLOCKED": {
        "fill": (255, 235, 235),
        "border": (218, 55, 60),
        "badge": (218, 55, 60),
        "text": (148, 35, 40),
    },
    "READY_FOR_REVIEW": {
        "fill": (246, 239, 255),
        "border": (128, 75, 196),
        "badge": (235, 139, 37),
        "text": (96, 57, 146),
    },
    "NOT_STARTED": {
        "fill": (245, 246, 248),
        "border": (150, 158, 171),
        "badge": (112, 119, 132),
        "text": (80, 87, 101),
    },
}

INK = (28, 34, 43)
MUTED = (96, 106, 120)
BACKGROUND = (250, 252, 255)
CARD_SHADOW = (222, 228, 236)
WHITE = (255, 255, 255)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            continue
    return ImageFont.load_default()


FONT_TITLE = load_font(48, bold=True)
FONT_SUBTITLE = load_font(24)
FONT_PHASE = load_font(28, bold=True)
FONT_BADGE = load_font(19, bold=True)
FONT_BODY = load_font(21)
FONT_SMALL = load_font(18)
FONT_FOOTER = load_font(23, bold=True)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int],
    outline: tuple[int, int, int] | None = None,
    width: int = 1,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def badge_text(status: str) -> str:
    return status.replace("_", " ")


def status_style(status: str) -> dict[str, tuple[int, int, int]]:
    return STATUS_STYLES.get(status, STATUS_STYLES["NOT_STARTED"])


def draw_badge(draw: ImageDraw.ImageDraw, x: int, y: int, status: str) -> None:
    label = badge_text(status)
    style = status_style(status)
    padding_x = 14
    padding_y = 8
    width = text_width(draw, label, FONT_BADGE) + padding_x * 2
    height = 36
    draw_rounded_rect(draw, (x, y, x + width, y + height), 8, style["badge"])
    draw.text((x + padding_x, y + padding_y - 1), label, fill=WHITE, font=FONT_BADGE)


def draw_progress(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, percent: int, color: tuple[int, int, int]) -> None:
    height = 18
    draw_rounded_rect(draw, (x, y, x + width, y + height), 8, (224, 229, 236))
    fill_width = max(0, min(width, int(width * percent / 100)))
    if fill_width:
        draw_rounded_rect(draw, (x, y, x + fill_width, y + height), 8, color)


def visible_tasks(phase: dict) -> list[str]:
    tasks = phase.get("tasks", [])
    return tasks[:7]


def draw_phase_card(
    draw: ImageDraw.ImageDraw,
    phase: dict,
    x: int,
    y: int,
    active_phase_id: str | None,
) -> None:
    status = phase.get("status", "NOT_STARTED")
    style = status_style(status)
    is_active = phase.get("phase_id") == active_phase_id

    shadow_box = (x + 6, y + 8, x + CARD_WIDTH + 6, y + CARD_HEIGHT + 8)
    draw_rounded_rect(draw, shadow_box, CARD_RADIUS, CARD_SHADOW)

    border = (24, 96, 180) if is_active else style["border"]
    border_width = 5 if is_active else 3
    card_box = (x, y, x + CARD_WIDTH, y + CARD_HEIGHT)
    draw_rounded_rect(draw, card_box, CARD_RADIUS, style["fill"], border, border_width)

    top = y + 24
    phase_label = f"{phase.get('phase_id', '')}: {phase.get('phase_name', '')}"
    title_lines = wrap_text(draw, phase_label, FONT_PHASE, CARD_WIDTH - 300)
    for line in title_lines[:2]:
        draw.text((x + 26, top), line, fill=INK, font=FONT_PHASE)
        top += 34

    draw_badge(draw, x + CARD_WIDTH - 250, y + 26, status)

    if is_active:
        draw.text((x + CARD_WIDTH - 250, y + 70), "CURRENT ACTIVE", fill=(24, 96, 180), font=FONT_SMALL)

    top = max(top + 14, y + 112)
    percent = int(phase.get("completion_percentage", 0))
    draw.text((x + 26, top), f"Completion: {percent}%", fill=style["text"], font=FONT_BODY)
    draw_progress(draw, x + 195, top + 5, CARD_WIDTH - 245, percent, style["border"])
    top += 42

    tasks = visible_tasks(phase)
    draw.text((x + 26, top), "Key tasks", fill=INK, font=FONT_BADGE)
    top += 32
    for task in tasks:
        lines = wrap_text(draw, task, FONT_BODY, CARD_WIDTH - 90)
        marker = "✓" if task in phase.get("completed_tasks", []) else "•"
        marker_color = STATUS_STYLES["COMPLETE"]["border"] if marker == "✓" else MUTED
        draw.text((x + 32, top), marker, fill=marker_color, font=FONT_BODY)
        draw.text((x + 58, top), lines[0], fill=INK, font=FONT_BODY)
        top += 28
        for continuation in lines[1:2]:
            draw.text((x + 58, top), continuation, fill=INK, font=FONT_BODY)
            top += 28
        if top > y + CARD_HEIGHT - 72:
            break

    blockers = phase.get("blocked_tasks", [])
    notes = phase.get("notes", "")
    bottom_y = y + CARD_HEIGHT - 50
    if status == "BLOCKED" and blockers:
        blocker_text = f"Blocked: {blockers[0]}"
        dependency_text = "Dependency warning: resolve blocker before execution."
        draw.text((x + 26, bottom_y - 25), blocker_text[:95], fill=STATUS_STYLES["BLOCKED"]["text"], font=FONT_SMALL)
        draw.text((x + 26, bottom_y), dependency_text, fill=STATUS_STYLES["BLOCKED"]["text"], font=FONT_SMALL)
    elif notes:
        note_lines = wrap_text(draw, f"Note: {notes}", FONT_SMALL, CARD_WIDTH - 52)
        draw.text((x + 26, bottom_y), note_lines[0], fill=MUTED, font=FONT_SMALL)


def count_by_status(phases: Iterable[dict], status: str) -> int:
    return sum(1 for phase in phases if phase.get("status") == status)


def draw_legend(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    labels = [
        ("Green = Complete", "COMPLETE"),
        ("Blue = In Progress", "IN_PROGRESS"),
        ("Red = Blocked", "BLOCKED"),
        ("Purple/Orange = Ready for Review", "READY_FOR_REVIEW"),
        ("Grey = Not Started", "NOT_STARTED"),
    ]
    current_x = x
    for label, status in labels:
        style = status_style(status)
        draw_rounded_rect(draw, (current_x, y, current_x + 24, y + 24), 6, style["badge"])
        draw.text((current_x + 34, y - 1), label, fill=INK, font=FONT_SMALL)
        current_x += text_width(draw, label, FONT_SMALL) + 82


def main() -> None:
    with STATUS_FILE.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    phases = data["phases"]
    active_phase_id = data.get("active_phase_id")
    rows = (len(phases) + 1) // 2
    header_height = 210
    footer_height = 150
    canvas_height = header_height + rows * (CARD_HEIGHT + GUTTER) + footer_height

    image = Image.new("RGB", (CANVAS_WIDTH, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(image)

    title = data.get("title", "AI Tradie Receptionist Platform — Phase Roadmap")
    generated_at = datetime.now().astimezone()
    generated_label = generated_at.strftime("Generated %Y-%m-%d %H:%M:%S %Z")

    draw.text((MARGIN, 42), title, fill=INK, font=FONT_TITLE)
    draw.text((MARGIN, 104), generated_label, fill=MUTED, font=FONT_SUBTITLE)
    draw_legend(draw, MARGIN, 154)

    start_y = header_height
    for index, phase in enumerate(phases):
        col = index % 2
        row = index // 2
        x = MARGIN + col * (CARD_WIDTH + GUTTER)
        y = start_y + row * (CARD_HEIGHT + GUTTER)
        draw_phase_card(draw, phase, x, y, active_phase_id)

    completed = count_by_status(phases, "COMPLETE")
    blocked = count_by_status(phases, "BLOCKED")
    pending = sum(1 for phase in phases if phase.get("status") == "NOT_STARTED")
    in_progress = count_by_status(phases, "IN_PROGRESS")
    review = count_by_status(phases, "READY_FOR_REVIEW")
    active_phase = next((phase for phase in phases if phase.get("phase_id") == active_phase_id), None)
    active_label = f"{active_phase_id}"
    if active_phase:
        active_label = f"{active_phase_id}: {active_phase.get('phase_name')} ({active_phase.get('status')})"

    footer_top = canvas_height - footer_height + 32
    footer_box = (MARGIN, footer_top - 18, CANVAS_WIDTH - MARGIN, canvas_height - 42)
    draw_rounded_rect(draw, footer_box, CARD_RADIUS, (238, 243, 249), (203, 212, 224), 2)
    summary = (
        f"Total phases: {len(phases)}    "
        f"Completed: {completed}    "
        f"Active phase: {active_label}    "
        f"Pending: {pending}    "
        f"Blocked: {blocked}    "
        f"In progress: {in_progress}    "
        f"Ready for review: {review}"
    )
    draw.text((MARGIN + 28, footer_top + 16), summary, fill=INK, font=FONT_FOOTER)

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_name = generated_at.strftime("roadmap_phase_snapshot_%Y%m%d_%H%M%S.png")
    snapshot_path = SNAPSHOT_DIR / snapshot_name
    image.save(snapshot_path)
    shutil.copyfile(snapshot_path, LATEST_FILE)

    print(f"Snapshot: {snapshot_path}")
    print(f"Latest: {LATEST_FILE}")


if __name__ == "__main__":
    main()
