from __future__ import annotations

from typing import Dict, List, Tuple

from app.models.event_models import DailyReport, EventRecord
from app.models.state_models import AgentState, RelationshipMatrix


def _event_signature(event: EventRecord) -> Tuple[str, str]:
    return (event.title.strip().lower(), event.description.strip().lower())


def _dedupe_preserve_order(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        key = item.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _select_diverse_top_events(events: List[EventRecord], max_items: int = 5) -> List[str]:
    sorted_events = sorted(events, key=lambda e: e.importance, reverse=True)

    selected: List[str] = []
    seen_signatures = set()
    template_counter: Dict[str, int] = {}

    for event in sorted_events:
        sig = _event_signature(event)
        if sig in seen_signatures:
            continue

        # 同一种模板最多保留 2 条，避免刷屏
        template_counter.setdefault(event.template_id, 0)
        if template_counter[event.template_id] >= 2:
            continue

        seen_signatures.add(sig)
        template_counter[event.template_id] += 1
        selected.append(f"{event.title}: {event.description}")

        if len(selected) >= max_items:
            break

    return selected


def _build_relationship_changes(relationships: RelationshipMatrix, max_items: int = 5) -> List[str]:
    pair_records: List[Tuple[float, str]] = []
    seen_pairs = set()

    for a, row in relationships.items():
        for b, rel in row.items():
            if a == b:
                continue
            pair_key = tuple(sorted((a, b)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # 用“显著性”做排序
            strength = max(abs(rel.tension), abs(rel.trust), abs(rel.closeness), abs(rel.respect))

            if rel.tension >= 25:
                desc = f"{a} ↔ {b}: tension is notably high"
            elif rel.trust >= 25:
                desc = f"{a} ↔ {b}: trust is clearly building"
            elif rel.closeness >= 25:
                desc = f"{a} ↔ {b}: they are growing closer"
            elif rel.respect >= 25:
                desc = f"{a} ↔ {b}: mutual respect is becoming more visible"
            else:
                continue

            pair_records.append((strength, desc))

    pair_records.sort(key=lambda x: x[0], reverse=True)
    return [desc for _, desc in pair_records[:max_items]]


def _build_character_highlights(agents: Dict[str, AgentState]) -> Dict[str, str]:
    result = {}
    for agent_id, agent in agents.items():
        top_need_name, top_need_value = max(agent.needs.model_dump().items(), key=lambda x: x[1])
        result[agent_id] = (
            f"{agent.name} is {agent.emotion.label} in {agent.current_location}, "
            f"mainly driven by {top_need_name} ({top_need_value:.0f})."
        )
    return result


def _build_tomorrow_hooks(agents: Dict[str, AgentState], max_items: int = 5) -> List[str]:
    hooks: List[str] = []

    for agent in agents.values():
        if agent.needs.social >= 75:
            hooks.append(f"{agent.name} may strongly seek connection tomorrow.")
        if agent.needs.order >= 75:
            hooks.append(f"{agent.name} may react sharply to disorder tomorrow.")
        if agent.needs.novelty >= 75:
            hooks.append(f"{agent.name} may try to create excitement tomorrow.")
        if agent.needs.rest >= 80:
            hooks.append(f"{agent.name} may need recovery time tomorrow.")
        if agent.emotion.label in ("annoyed", "stressed", "sad"):
            hooks.append(f"{agent.name}'s current mood could affect tomorrow's atmosphere.")

    hooks = _dedupe_preserve_order(hooks)
    if not hooks:
        hooks = ["The next day may depend on who chooses to act first."]

    return hooks[:max_items]


def generate_daily_report(
    day: int,
    events: List[EventRecord],
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
) -> DailyReport:
    diverse_top_events = _select_diverse_top_events(events, max_items=5)

    if events:
        headline = sorted(events, key=lambda e: e.importance, reverse=True)[0].description
    else:
        headline = "The day was relatively quiet, but subtle shifts continued beneath the surface."

    relationship_changes = _build_relationship_changes(relationships, max_items=5)
    character_highlights = _build_character_highlights(agents)
    tomorrow_hooks = _build_tomorrow_hooks(agents, max_items=5)

    return DailyReport(
        day=day,
        headline=headline,
        top_events=diverse_top_events,
        relationship_changes=relationship_changes,
        character_highlights=character_highlights,
        tomorrow_hooks=tomorrow_hooks,
    )