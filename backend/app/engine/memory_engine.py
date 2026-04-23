from __future__ import annotations

import re
from typing import Dict, List

from app.models.state_models import AgentState, MemoryItem, WorldState


def _normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def remember_event(
    agents: Dict[str, AgentState],
    actor_ids: List[str],
    world: WorldState,
    summary: str,
    location: str,
    importance: float,
    sentiment: float,
    max_memories: int = 20,
    dedupe_window: int = 5,
) -> None:
    """
    只记录较重要事件，并对最近几条做简单去重。
    """
    if importance < 0.60:
        return

    normalized_summary = _normalize_text(summary)

    for actor_id in actor_ids:
        related = sorted([x for x in actor_ids if x != actor_id])
        recent = agents[actor_id].memories[-dedupe_window:]

        duplicate_found = False
        for mem in recent:
            if (
                mem.day == world.day
                and mem.location == location
                and sorted(mem.related_characters) == related
                and _normalize_text(mem.summary) == normalized_summary
            ):
                duplicate_found = True
                break

        if duplicate_found:
            continue

        agents[actor_id].memories.append(
            MemoryItem(
                day=world.day,
                summary=summary,
                related_characters=related,
                location=location,
                importance=importance,
                sentiment=sentiment,
            )
        )
        agents[actor_id].memories = agents[actor_id].memories[-max_memories:]