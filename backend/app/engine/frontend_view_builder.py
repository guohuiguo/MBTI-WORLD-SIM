from __future__ import annotations

from typing import Dict, List

from app.models.event_models import DailyReport, EventRecord
from app.models.state_models import AgentState, RelationshipMatrix, WorldState


def _dedupe_focus_events(events: List[EventRecord], limit: int = 5) -> List[dict]:
    seen = set()
    result = []
    sorted_events = sorted(events, key=lambda e: e.importance, reverse=True)

    for event in sorted_events:
        sig = (event.template_id, tuple(sorted(event.actors)), event.location)
        if sig in seen:
            continue
        seen.add(sig)
        result.append(
            {
                "id": event.id,
                "template_id": event.template_id,
                "title": event.title,
                "description": event.description,
                "slot": event.slot,
                "actors": event.actors,
                "location": event.location,
                "tone": event.tone,
                "importance": event.importance,
                "effects": event.effects.model_dump() if event.effects else None,
            }
        )
        if len(result) >= limit:
            break
    return result


def build_focus_events(today_events: List[EventRecord], last_completed_day_events: List[EventRecord], limit: int = 5) -> List[dict]:
    source = today_events if today_events else last_completed_day_events
    return _dedupe_focus_events(source, limit=limit)


def build_event_feed(today_events: List[EventRecord], last_completed_day_events: List[EventRecord], limit: int = 50) -> List[dict]:
    source = today_events if today_events else last_completed_day_events
    ordered = list(source)[-limit:]
    return [
        {
            "id": e.id,
            "template_id": e.template_id,
            "title": e.title,
            "description": e.description,
            "slot": e.slot,
            "actors": e.actors,
            "location": e.location,
            "tone": e.tone,
            "importance": e.importance,
            "effects": e.effects.model_dump() if e.effects else None,
        }
        for e in ordered
    ]


def build_room_distribution(world: WorldState) -> Dict[str, List[dict]]:
    zones = {
        "apartment": [],
        "university": [],
        "amusement_park": [],
    }

    for location, occupants in world.occupancy.items():
        entry = {
            "location": location,
            "occupants": occupants,
            "count": len(occupants),
        }
        if location.startswith("bedroom_") or location in {"living_room", "kitchen", "gym", "bathroom_a", "bathroom_b"}:
            zones["apartment"].append(entry)
        elif location in {"classroom", "library", "cafeteria", "campus_square"}:
            zones["university"].append(entry)
        else:
            zones["amusement_park"].append(entry)

    return zones


def build_character_cards(agents: Dict[str, AgentState]) -> List[dict]:
    cards = []
    for agent_id, agent in agents.items():
        sorted_needs = sorted(agent.needs.model_dump().items(), key=lambda x: x[1], reverse=True)
        cards.append(
            {
                "id": agent_id,
                "name": agent.name,
                "mbti": agent.mbti,
                "major": agent.major,
                "location": agent.current_location,
                "emotion": agent.emotion.label,
                "top_needs": sorted_needs[:2],
                "memory_count": len(agent.memories),
            }
        )
    return cards


def build_relationship_graph(relationships: RelationshipMatrix, threshold: int = 12) -> List[dict]:
    edges = []
    seen = set()

    for a, row in relationships.items():
        for b, rel in row.items():
            if a == b:
                continue
            key = tuple(sorted((a, b)))
            if key in seen:
                continue
            seen.add(key)

            strongest = max(abs(rel.closeness), abs(rel.trust), abs(rel.tension), abs(rel.respect))
            if strongest < threshold:
                continue

            if rel.tension >= max(rel.closeness, rel.trust, rel.respect, 0):
                edge_type = "tense"
                weight = rel.tension
            elif rel.trust >= max(rel.closeness, rel.respect, 0):
                edge_type = "trust"
                weight = rel.trust
            elif rel.closeness >= max(rel.respect, 0):
                edge_type = "close"
                weight = rel.closeness
            else:
                edge_type = "respect"
                weight = rel.respect

            edges.append(
                {
                    "source": a,
                    "target": b,
                    "type": edge_type,
                    "weight": weight,
                    "details": rel.model_dump(),
                }
            )

    return sorted(edges, key=lambda x: abs(x["weight"]), reverse=True)


def build_frontend_overview(
    world: WorldState,
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
    today_events: List[EventRecord],
    last_completed_day_events: List[EventRecord],
    latest_report: DailyReport | None,
) -> dict:
    return {
        "world": {
            "day": world.day,
            "weekday_name": world.weekday_name,
            "day_type": world.day_type,
            "current_slot": world.current_slot,
            "weather": world.weather,
            "active_global_tags": world.active_global_tags,
        },
        "focus_events": build_focus_events(today_events, last_completed_day_events, limit=5),
        "event_feed": build_event_feed(today_events, last_completed_day_events, limit=50),
        "room_distribution": build_room_distribution(world),
        "character_cards": build_character_cards(agents),
        "relationship_graph": build_relationship_graph(relationships),
        "latest_report": latest_report.model_dump() if latest_report else None,
    }