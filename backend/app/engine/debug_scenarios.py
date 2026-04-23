from __future__ import annotations

from typing import Dict

from app.models.state_models import AgentState, RelationshipMatrix, WorldState


def _set_need(agent: AgentState, **kwargs: float) -> None:
    for key, value in kwargs.items():
        setattr(agent.needs, key, value)


def _clear_short_state(agent: AgentState) -> None:
    agent.short_term_goal = None
    agent.emotion.label = "calm"
    agent.emotion.intensity = 0.3
    agent.emotion.valence = 0.1
    agent.emotion.arousal = 0.3


def _boost_pair_relationship(
    relationships: RelationshipMatrix,
    a: str,
    b: str,
    closeness: int = 20,
    trust: int = 20,
    tension: int = 0,
    respect: int = 10,
) -> None:
    relationships[a][b].closeness = closeness
    relationships[b][a].closeness = closeness
    relationships[a][b].trust = trust
    relationships[b][a].trust = trust
    relationships[a][b].tension = tension
    relationships[b][a].tension = tension
    relationships[a][b].respect = respect
    relationships[b][a].respect = respect


def prepare_template_scenario(
    template_id: str,
    world: WorldState,
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
) -> dict:
    supported = {"A4", "U4", "P5", "P6"}
    if template_id not in supported:
        raise ValueError(f"Unsupported template scenario: {template_id}")

    for agent in agents.values():
        _clear_short_state(agent)

    world.active_global_tags = [f"force_template:{template_id}"]

    if template_id == "A4":
        world.day = 1
        world.weekday_name = "Monday"
        world.day_type = "weekday"
        world.current_slot = "evening"
        world.weather = "sunny"

        agents["grace"].current_location = "kitchen"
        agents["leo"].current_location = "kitchen"
        agents["ethan"].current_location = "bedroom_ethan"
        agents["chloe"].current_location = "gym"

        _set_need(agents["grace"], social=74, belonging=70, rest=28, novelty=22, order=36)
        _set_need(agents["leo"], social=76, belonging=58, rest=32, novelty=40, order=18)

        _boost_pair_relationship(relationships, "grace", "leo", closeness=28, trust=24, tension=0, respect=14)

        return {
            "template_id": "A4",
            "description": "Grace and Leo are in the kitchen on a friendly evening, with a force tag for A4."
        }

    if template_id == "U4":
        world.day = 3
        world.weekday_name = "Wednesday"
        world.day_type = "weekday"
        world.current_slot = "afternoon"
        world.weather = "sunny"

        agents["leo"].current_location = "cafeteria"
        agents["grace"].current_location = "cafeteria"
        agents["ethan"].current_location = "library"
        agents["chloe"].current_location = "campus_square"

        _set_need(agents["leo"], social=68, rest=40, achievement=34, novelty=28, belonging=48)
        _set_need(agents["grace"], social=56, rest=38, achievement=40, novelty=18, belonging=60)

        _boost_pair_relationship(relationships, "grace", "leo", closeness=24, trust=22, tension=0, respect=12)

        return {
            "template_id": "U4",
            "description": "Grace and Leo are together in the cafeteria on a weekday afternoon, with a force tag for U4."
        }

    if template_id == "P5":
        world.day = 6
        world.weekday_name = "Saturday"
        world.day_type = "weekend"
        world.current_slot = "late_evening"
        world.weather = "sunny"

        agents["leo"].current_location = "food_court"
        agents["chloe"].current_location = "food_court"
        agents["grace"].current_location = "entrance"
        agents["ethan"].current_location = "arcade"

        _set_need(agents["leo"], social=64, novelty=44, rest=28, belonging=46)
        _set_need(agents["chloe"], social=50, novelty=54, rest=26, belonging=34)

        _boost_pair_relationship(relationships, "leo", "chloe", closeness=22, trust=16, tension=4, respect=14)

        return {
            "template_id": "P5",
            "description": "Leo and Chloe are near the end of a park trip in a souvenir-friendly setup, with a force tag for P5."
        }

    if template_id == "P6":
        world.day = 6
        world.weekday_name = "Saturday"
        world.day_type = "weekend"
        world.current_slot = "evening"
        world.weather = "rainy"

        agents["leo"].current_location = "rides_area"
        agents["chloe"].current_location = "arcade"
        agents["grace"].current_location = "entrance"
        agents["ethan"].current_location = "food_court"

        _set_need(agents["leo"], social=60, novelty=76, rest=24, belonging=40)
        _set_need(agents["chloe"], social=46, novelty=82, rest=22, belonging=30)

        _boost_pair_relationship(relationships, "leo", "chloe", closeness=18, trust=12, tension=8, respect=12)

        return {
            "template_id": "P6",
            "description": "The park is rainy and characters are scattered across park sub-locations, with a force tag for P6."
        }

    raise ValueError(f"Unhandled template scenario: {template_id}")