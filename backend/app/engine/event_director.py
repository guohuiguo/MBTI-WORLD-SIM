from app.models.event_models import EventRecord
from app.models.state_models import WorldState


def should_increase_drama(recent_events: list[EventRecord], world: WorldState) -> bool:
    if len(recent_events) < 2:
        return True
    recent = recent_events[-2:]
    return all(event.importance < 0.55 for event in recent)


def inject_global_tag_if_needed(recent_events: list[EventRecord], world: WorldState) -> None:
    preserved = [tag for tag in world.active_global_tags if tag.startswith("force_template:")]
    world.active_global_tags = preserved

    if should_increase_drama(recent_events, world):
        world.active_global_tags.append("needs_more_interaction")

    if world.day_type == "weekend" and world.current_slot in ("evening", "late_evening"):
        world.active_global_tags.append("weekend_fun_bias")