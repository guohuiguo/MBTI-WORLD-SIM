from app.models.state_models import AgentState


def update_emotion_after_action(agent: AgentState, action_type: str, success: bool = True) -> None:
    if not success:
        agent.emotion.label = "stressed"
        agent.emotion.intensity = min(1.0, agent.emotion.intensity + 0.2)
        agent.emotion.valence = max(-1.0, agent.emotion.valence - 0.2)
        return

    if action_type in ("talk", "invite", "watch_movie", "share_feelings", "play"):
        agent.emotion.label = "happy"
        agent.emotion.intensity = 0.5
        agent.emotion.valence = 0.6
        agent.emotion.arousal = 0.5

    elif action_type in ("rest",):
        agent.emotion.label = "calm"
        agent.emotion.intensity = 0.3
        agent.emotion.valence = 0.2
        agent.emotion.arousal = 0.2

    elif action_type in ("argue",):
        agent.emotion.label = "annoyed"
        agent.emotion.intensity = 0.7
        agent.emotion.valence = -0.6
        agent.emotion.arousal = 0.8

    elif action_type in ("study", "attend_class", "clean"):
        agent.emotion.label = "satisfied"
        agent.emotion.intensity = 0.4
        agent.emotion.valence = 0.3
        agent.emotion.arousal = 0.4


def apply_lonely_if_needed(agent: AgentState) -> None:
    if agent.needs.social >= 80:
        agent.emotion.label = "lonely"
        agent.emotion.intensity = 0.7
        agent.emotion.valence = -0.4
        agent.emotion.arousal = 0.3

    if agent.needs.rest >= 85:
        agent.emotion.label = "stressed"
        agent.emotion.intensity = 0.7
        agent.emotion.valence = -0.5
        agent.emotion.arousal = 0.6