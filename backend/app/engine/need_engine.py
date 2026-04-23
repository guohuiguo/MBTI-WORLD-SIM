from app.models.state_models import AgentState, WorldState


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def drift_needs(agent: AgentState, world: WorldState, same_location_count: int) -> None:
    agent.needs.rest = _clamp(agent.needs.rest + 5)

    if same_location_count <= 1:
        growth = 4 + (agent.personality.sociability / 100) * 3
        agent.needs.social = _clamp(agent.needs.social + growth)

    if same_location_count >= 3:
        agent.needs.autonomy = _clamp(agent.needs.autonomy + 4)

    if world.current_slot in ("afternoon", "evening"):
        agent.needs.novelty = _clamp(agent.needs.novelty + 2)

    if world.current_slot in ("evening", "late_evening") and agent.personality.orderliness >= 70:
        agent.needs.order = _clamp(agent.needs.order + 2)


def apply_need_rewards(agent: AgentState, action_type: str) -> None:
    if action_type in ("talk", "invite", "watch_movie", "share_feelings", "play", "help"):
        agent.needs.social = _clamp(agent.needs.social - 12)
        agent.needs.belonging = _clamp(agent.needs.belonging - 8)

    elif action_type in ("rest",):
        agent.needs.rest = _clamp(agent.needs.rest - 14)
        agent.needs.autonomy = _clamp(agent.needs.autonomy - 6)

    elif action_type in ("study", "attend_class"):
        agent.needs.achievement = _clamp(agent.needs.achievement - 10)

    elif action_type in ("clean",):
        agent.needs.order = _clamp(agent.needs.order - 14)

    elif action_type in ("go_out", "play", "workout"):
        agent.needs.novelty = _clamp(agent.needs.novelty - 14)

    elif action_type in ("cook", "eat"):
        agent.needs.rest = _clamp(agent.needs.rest - 4)
        agent.needs.belonging = _clamp(agent.needs.belonging - 4)

    elif action_type == "move":
        agent.needs.novelty = _clamp(agent.needs.novelty - 1)
        agent.needs.autonomy = _clamp(agent.needs.autonomy - 1)