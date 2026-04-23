from __future__ import annotations

import uuid
from typing import Dict, List, Optional, Set

from app.data.event_templates import EVENT_TEMPLATES
from app.engine.emotion_engine import update_emotion_after_action
from app.engine.memory_engine import remember_event
from app.engine.need_engine import apply_need_rewards
from app.models.event_models import EventEffect, EventRecord
from app.models.state_models import AgentState, ChosenAction, RelationshipMatrix, WorldState

BATHROOMS = {"bathroom_a", "bathroom_b"}
APARTMENT_SHARED = {"living_room", "kitchen", "gym", "bathroom_a", "bathroom_b"}
PARK_SUBLOCS = {"entrance", "rides_area", "arcade", "food_court"}
TEMPLATE_MAP = {t.id: t for t in EVENT_TEMPLATES}


def _event_id() -> str:
    return str(uuid.uuid4())[:8]


def _clamp_rel(value: int) -> int:
    return max(-100, min(100, value))


def _apply_relationship_delta(
    relationships: RelationshipMatrix,
    a: str,
    b: str,
    closeness: int = 0,
    trust: int = 0,
    tension: int = 0,
    respect: int = 0,
) -> None:
    if a == b:
        return

    ra = relationships[a][b]
    rb = relationships[b][a]

    ra.closeness = _clamp_rel(ra.closeness + closeness)
    ra.trust = _clamp_rel(ra.trust + trust)
    ra.tension = _clamp_rel(ra.tension + tension)
    ra.respect = _clamp_rel(ra.respect + respect)

    rb.closeness = _clamp_rel(rb.closeness + closeness)
    rb.trust = _clamp_rel(rb.trust + trust)
    rb.tension = _clamp_rel(rb.tension + tension)
    rb.respect = _clamp_rel(rb.respect + respect)


def _pairwise_delta(
    relationships: RelationshipMatrix,
    actor_ids: List[str],
    closeness: int = 0,
    trust: int = 0,
    tension: int = 0,
    respect: int = 0,
) -> None:
    for i in range(len(actor_ids)):
        for j in range(i + 1, len(actor_ids)):
            _apply_relationship_delta(
                relationships,
                actor_ids[i],
                actor_ids[j],
                closeness=closeness,
                trust=trust,
                tension=tension,
                respect=respect,
            )


def _snapshot_needs(agents: Dict[str, AgentState], actor_ids: List[str]) -> Dict[str, Dict[str, float]]:
    return {actor_id: agents[actor_id].needs.model_dump().copy() for actor_id in actor_ids}


def _snapshot_relationships(
    relationships: RelationshipMatrix,
    actor_ids: List[str],
) -> Dict[str, Dict[str, int]]:
    snap: Dict[str, Dict[str, int]] = {}
    for i in range(len(actor_ids)):
        for j in range(i + 1, len(actor_ids)):
            a, b = sorted((actor_ids[i], actor_ids[j]))
            snap[f"{a}|{b}"] = relationships[a][b].model_dump().copy()
    return snap


def _build_effects(
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
    actor_ids: List[str],
    before_needs: Dict[str, Dict[str, float]],
    before_relationships: Dict[str, Dict[str, int]],
) -> Optional[EventEffect]:
    need_delta: Dict[str, float] = {}
    relationship_delta: Dict[str, Dict[str, int]] = {}

    for actor_id in actor_ids:
        before = before_needs.get(actor_id, {})
        after = agents[actor_id].needs.model_dump()
        for k, before_v in before.items():
            delta = round(after[k] - before_v, 2)
            if abs(delta) > 0.01:
                need_delta[f"{actor_id}.{k}"] = delta

    for pair_key, before in before_relationships.items():
        a, b = pair_key.split("|")
        after = relationships[a][b].model_dump()
        pair_delta = {}
        for k, before_v in before.items():
            delta = after[k] - before_v
            if delta != 0:
                pair_delta[k] = delta
        if pair_delta:
            relationship_delta[pair_key] = pair_delta

    if not need_delta and not relationship_delta:
        return None

    return EventEffect(
        need_delta=need_delta,
        relationship_delta=relationship_delta,
    )


def _make_event(
    world: WorldState,
    template_id: str,
    title: str,
    description: str,
    actors: List[str],
    location: str,
    tone: str,
    importance: float,
    effects: Optional[EventEffect] = None,
) -> EventRecord:
    return EventRecord(
        id=_event_id(),
        day=world.day,
        slot=world.current_slot,
        template_id=template_id,
        title=title,
        description=description,
        actors=actors,
        location=location,
        tone=tone,  # type: ignore[arg-type]
        importance=importance,
        effects=effects,
    )


def _intended_location(agent: AgentState, action: ChosenAction) -> str:
    if action.target_location:
        return action.target_location
    if action.action_type == "go_out":
        return "entrance"
    if action.action_type == "attend_class":
        return "classroom"
    if action.action_type == "study":
        return "library"
    if action.action_type == "watch_movie":
        return "living_room"
    if action.action_type == "cook":
        return "kitchen"
    if action.action_type == "workout":
        return "gym"
    if action.action_type == "eat":
        return "kitchen"
    return agent.current_location


def _get_forced_template(world: WorldState) -> str | None:
    for tag in world.active_global_tags:
        if tag.startswith("force_template:"):
            return tag.split(":", 1)[1]
    return None


def _pick_best_pair_for_location(
    candidate_ids: List[str],
    relationships: RelationshipMatrix,
) -> List[str]:
    if len(candidate_ids) < 2:
        return []

    best_pair = None
    best_score = -10**9

    for i in range(len(candidate_ids)):
        for j in range(i + 1, len(candidate_ids)):
            a = candidate_ids[i]
            b = candidate_ids[j]
            rel = relationships[a][b]
            score = rel.closeness + rel.trust + rel.respect - rel.tension
            if score > best_score:
                best_score = score
                best_pair = [a, b]

    return best_pair or []


def _move_agents(agents: Dict[str, AgentState], actor_ids: List[str], location: str) -> None:
    for actor_id in actor_ids:
        agents[actor_id].current_location = location


def _apply_simple_rewards(
    agents: Dict[str, AgentState],
    actor_ids: List[str],
    action_type: str,
) -> None:
    for actor_id in actor_ids:
        apply_need_rewards(agents[actor_id], action_type)
        update_emotion_after_action(agents[actor_id], action_type, success=True)


def _should_accept_invite(
    inviter: AgentState,
    invitee: AgentState,
    relationships: RelationshipMatrix,
    inviter_id: str,
    invitee_id: str,
    target_location: str,
) -> bool:
    rel = relationships[inviter_id][invitee_id]
    score = 0.0

    score += rel.closeness * 0.25
    score += rel.trust * 0.25
    score -= rel.tension * 0.35

    score += invitee.needs.social * 0.15
    score += invitee.needs.novelty * 0.15
    score -= invitee.needs.rest * 0.20

    if target_location in ("library", "classroom"):
        score += invitee.needs.achievement * 0.15
        score += invitee.personality.planning * 0.10

    if target_location == "entrance":
        score += invitee.personality.impulsiveness * 0.12
        score += invitee.personality.curiosity * 0.10

    if target_location == "living_room":
        score += invitee.personality.sociability * 0.08

    return score >= 8.0


def _finalize_event(
    events: List[EventRecord],
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
    world: WorldState,
    actor_ids: List[str],
    before_needs: Dict[str, Dict[str, float]],
    before_relationships: Dict[str, Dict[str, int]],
    template_id: str,
    title: str,
    description: str,
    location: str,
    tone: str,
    importance: float,
    sentiment: float,
) -> None:
    effects = _build_effects(
        agents=agents,
        relationships=relationships,
        actor_ids=actor_ids,
        before_needs=before_needs,
        before_relationships=before_relationships,
    )
    event = _make_event(
        world=world,
        template_id=template_id,
        title=title,
        description=description,
        actors=actor_ids,
        location=location,
        tone=tone,
        importance=importance,
        effects=effects,
    )
    events.append(event)
    remember_event(
        agents=agents,
        actor_ids=actor_ids,
        world=world,
        summary=description,
        location=location,
        importance=importance,
        sentiment=sentiment,
    )


def resolve_slot_actions(
    chosen_actions: Dict[str, ChosenAction],
    world: WorldState,
    agents: Dict[str, AgentState],
    relationships: RelationshipMatrix,
) -> List[EventRecord]:
    events: List[EventRecord] = []
    used: Set[str] = set()

    intents: Dict[str, Dict[str, object]] = {}
    for actor_id, action in chosen_actions.items():
        intents[actor_id] = {
            "action": action,
            "loc": _intended_location(agents[actor_id], action),
        }

    # ------------------------------------------------------------------
    # Forced template handling for debug scenarios
    # ------------------------------------------------------------------
    forced_template = _get_forced_template(world)

    if forced_template == "A4":
        kitchen_ids = [
            actor_id
            for actor_id, data in intents.items()
            if data["loc"] == "kitchen"
        ]
        actor_ids = _pick_best_pair_for_location(kitchen_ids, relationships)
        if len(actor_ids) == 2 and world.current_slot == "evening":
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _move_agents(agents, actor_ids, "kitchen")
            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=4, trust=3, tension=-1)
            _apply_simple_rewards(agents, actor_ids, "cook")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "A4",
                TEMPLATE_MAP["A4"].title,
                f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} ended up sharing a cooking moment in the kitchen.",
                "kitchen",
                "positive",
                0.58,
                0.35,
            )
            return events

    if forced_template == "U4":
        cafeteria_ids = [
            actor_id
            for actor_id, data in intents.items()
            if data["loc"] == "cafeteria"
        ]
        actor_ids = _pick_best_pair_for_location(cafeteria_ids, relationships)
        if len(actor_ids) == 2 and world.current_slot == "afternoon":
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _move_agents(agents, actor_ids, "cafeteria")
            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=3, trust=2, tension=-1)
            _apply_simple_rewards(agents, actor_ids, "eat")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "U4",
                TEMPLATE_MAP["U4"].title,
                f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} ended up making a lunch decision together in the cafeteria.",
                "cafeteria",
                "positive",
                0.53,
                0.22,
            )
            return events

    if forced_template == "P5":
        souvenir_ids = [
            actor_id
            for actor_id, data in intents.items()
            if data["loc"] in {"food_court", "entrance"}
        ]
        actor_ids = _pick_best_pair_for_location(souvenir_ids, relationships)
        if len(actor_ids) == 2 and world.current_slot == "late_evening":
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            loc = intents[actor_ids[0]]["loc"]  # type: ignore[assignment]
            _move_agents(agents, actor_ids, loc)
            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=3, trust=2, respect=1)
            _apply_simple_rewards(agents, actor_ids, "talk")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "P5",
                TEMPLATE_MAP["P5"].title,
                f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} got unexpectedly thoughtful while choosing souvenirs.",
                loc,
                "positive",
                0.50,
                0.28,
            )
            return events

    if forced_template == "P6":
        park_ids = [
            actor_id
            for actor_id, data in intents.items()
            if data["loc"] in PARK_SUBLOCS
        ]
        actor_ids = park_ids[:2]
        if len(actor_ids) == 2 and world.weather == "rainy" and world.current_slot in ("evening", "late_evening"):
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], trust=-1, tension=4, closeness=-1)
            _apply_simple_rewards(agents, actor_ids, "move")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "P6",
                TEMPLATE_MAP["P6"].title,
                f"Rain disrupted the amusement park rhythm and forced {agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} to change plans.",
                "entrance",
                "negative",
                0.69,
                -0.25,
            )
            return events

    # ------------------------------------------------------------------
    # 1) invite handling
    # ------------------------------------------------------------------
    for inviter_id, data in intents.items():
        if inviter_id in used:
            continue

        action: ChosenAction = data["action"]  # type: ignore[assignment]
        target_loc: str = data["loc"]  # type: ignore[assignment]

        if action.action_type != "invite" or not action.target_character:
            continue

        target_id = action.target_character
        if target_id not in agents or target_id in used:
            continue

        inviter = agents[inviter_id]
        invitee = agents[target_id]
        actor_ids = [inviter_id, target_id]

        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        accepted = _should_accept_invite(
            inviter=inviter,
            invitee=invitee,
            relationships=relationships,
            inviter_id=inviter_id,
            invitee_id=target_id,
            target_location=target_loc,
        )

        if accepted:
            _move_agents(agents, actor_ids, target_loc)

            if target_loc == "entrance":
                _apply_relationship_delta(relationships, inviter_id, target_id, closeness=5, trust=3, tension=-1)
                _apply_simple_rewards(agents, actor_ids, "go_out")
                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "P1",
                    TEMPLATE_MAP["P1"].title,
                    f"{inviter.name} convinced {invitee.name} to make a spontaneous amusement park plan.",
                    target_loc,
                    "positive",
                    0.72,
                    0.65,
                )
            elif target_loc == "living_room":
                _apply_relationship_delta(relationships, inviter_id, target_id, closeness=4, trust=2)
                _apply_simple_rewards(agents, actor_ids, "watch_movie")
                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "A6",
                    TEMPLATE_MAP["A6"].title,
                    f"{inviter.name} pulled {invitee.name} into a shared hangout in the living room.",
                    target_loc,
                    "positive",
                    0.60,
                    0.50,
                )
            elif target_loc in ("library", "classroom"):
                _apply_relationship_delta(relationships, inviter_id, target_id, closeness=3, trust=4, respect=2)
                _apply_simple_rewards(agents, actor_ids, "study")
                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "U2",
                    TEMPLATE_MAP["U2"].title,
                    f"{inviter.name} and {invitee.name} agreed to study together.",
                    target_loc,
                    "positive",
                    0.66,
                    0.45,
                )
            elif target_loc == "gym":
                _apply_relationship_delta(relationships, inviter_id, target_id, closeness=2, respect=3, tension=1)
                _apply_simple_rewards(agents, actor_ids, "workout")
                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "A8",
                    TEMPLATE_MAP["A8"].title,
                    f"{inviter.name} turned the gym into a shared challenge with {invitee.name}.",
                    target_loc,
                    "mixed",
                    0.62,
                    0.20,
                )
            else:
                _apply_relationship_delta(relationships, inviter_id, target_id, closeness=3, trust=2)
                _apply_simple_rewards(agents, actor_ids, "talk")
                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "INVITE_ACCEPTED",
                    f"{inviter.name}'s invitation was accepted",
                    f"{invitee.name} accepted {inviter.name}'s invitation.",
                    target_loc,
                    "positive",
                    0.56,
                    0.35,
                )

            used.update(actor_ids)

        else:
            _apply_relationship_delta(relationships, inviter_id, target_id, closeness=-1, trust=-1, tension=2)
            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "INVITE_DECLINED",
                f"{invitee.name} turned down an invitation",
                f"{invitee.name} declined {inviter.name}'s invitation.",
                inviter.current_location,
                "mixed",
                0.52,
                -0.15,
            )
            used.add(inviter_id)

    # ------------------------------------------------------------------
    # 2) A1 bathroom queue conflict
    # ------------------------------------------------------------------
    bathroom_seekers = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used and data["loc"] in BATHROOMS and world.current_slot == "morning"
    ]
    if len(bathroom_seekers) >= 2:
        actor_ids = bathroom_seekers[:2]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "bathroom_a")
        _pairwise_delta(relationships, actor_ids, tension=8, trust=-2, closeness=-1)

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "A1",
            TEMPLATE_MAP["A1"].title,
            f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} ended up competing for bathroom access during the morning rush.",
            "bathroom_a",
            "negative",
            0.74,
            -0.60,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 3) A2 breakfast chat
    # ------------------------------------------------------------------
    kitchen_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used and data["loc"] == "kitchen" and world.current_slot == "morning"
    ]
    if len(kitchen_group) >= 2:
        actor_ids = kitchen_group[:2]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "kitchen")
        _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=3, trust=2, tension=-1)
        _apply_simple_rewards(agents, actor_ids, "talk")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "A2",
            TEMPLATE_MAP["A2"].title,
            f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} shared an easy breakfast conversation.",
            "kitchen",
            "positive",
            0.50,
            0.30,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 4) A4 shared cooking invitation (natural trigger)
    # ------------------------------------------------------------------
    kitchen_social_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and data["loc"] == "kitchen"
        and world.current_slot == "evening"
        and data["action"].action_type in ("cook", "eat", "talk", "help", "invite")
    ]
    if len(kitchen_social_group) >= 2:
        actor_ids = _pick_best_pair_for_location(kitchen_social_group, relationships)
        if len(actor_ids) == 2:
            rel = relationships[actor_ids[0]][actor_ids[1]]
            if rel.tension <= 18:
                before_needs = _snapshot_needs(agents, actor_ids)
                before_rels = _snapshot_relationships(relationships, actor_ids)

                _move_agents(agents, actor_ids, "kitchen")
                _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=4, trust=3, tension=-1)
                _apply_simple_rewards(agents, actor_ids, "cook")

                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "A4",
                    TEMPLATE_MAP["A4"].title,
                    f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} ended up sharing a cooking moment in the kitchen.",
                    "kitchen",
                    "positive",
                    0.58,
                    0.35,
                )
                used.update(actor_ids)

    # ------------------------------------------------------------------
    # 5) A5 fridge food mix-up
    # ------------------------------------------------------------------
    kitchen_evening_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and data["loc"] == "kitchen"
        and world.current_slot in ("evening", "late_evening")
        and data["action"].action_type in ("eat", "cook")
    ]
    if len(kitchen_evening_group) >= 2:
        actor_ids = kitchen_evening_group[:2]
        a, b = actor_ids
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "kitchen")
        _apply_relationship_delta(relationships, a, b, closeness=-2, trust=-3, tension=6)
        _apply_simple_rewards(agents, actor_ids, "eat")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "A5",
            TEMPLATE_MAP["A5"].title,
            f"{agents[a].name} and {agents[b].name} got into an awkward food mix-up in the kitchen.",
            "kitchen",
            "mixed",
            0.67,
            -0.20,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 6) U4 cafeteria lunch decision
    # ------------------------------------------------------------------
    if world.day_type == "weekday" and world.current_slot == "afternoon":
        cafeteria_group = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used
            and data["loc"] == "cafeteria"
            and data["action"].action_type in ("eat", "talk", "move")
        ]
        if len(cafeteria_group) >= 2:
            actor_ids = _pick_best_pair_for_location(cafeteria_group, relationships)
            if len(actor_ids) == 2:
                before_needs = _snapshot_needs(agents, actor_ids)
                before_rels = _snapshot_relationships(relationships, actor_ids)

                _move_agents(agents, actor_ids, "cafeteria")
                _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=3, trust=2, tension=-1)
                _apply_simple_rewards(agents, actor_ids, "eat")

                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "U4",
                    TEMPLATE_MAP["U4"].title,
                    f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} ended up making a lunch decision together in the cafeteria.",
                    "cafeteria",
                    "positive",
                    0.53,
                    0.22,
                )
                used.update(actor_ids)

    # ------------------------------------------------------------------
    # 7) U5 group project / class collaboration
    # ------------------------------------------------------------------
    if world.day_type == "weekday" and world.current_slot in ("late_morning", "afternoon"):
        classroom_group = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used
            and data["loc"] == "classroom"
            and data["action"].action_type in ("attend_class", "study")
        ]
        if len(classroom_group) >= 2:
            actor_ids = classroom_group[: min(3, len(classroom_group))]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _move_agents(agents, actor_ids, "classroom")
            _pairwise_delta(relationships, actor_ids, closeness=2, trust=2, respect=3)

            if "ethan" in actor_ids and "leo" in actor_ids:
                _apply_relationship_delta(relationships, "ethan", "leo", tension=2, respect=2)

            _apply_simple_rewards(agents, actor_ids, "attend_class")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "U5",
                TEMPLATE_MAP["U5"].title,
                "A class-related task pushed multiple roommates into a temporary shared academic situation.",
                "classroom",
                "mixed",
                0.70,
                0.10,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 8) U6 presentation stress
    # ------------------------------------------------------------------
    if world.day_type == "weekday" and world.current_slot == "afternoon":
        classroom_stress = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used
            and data["loc"] == "classroom"
            and (
                agents[actor_id].needs.achievement >= 55
                or agents[actor_id].needs.rest >= 65
                or agents[actor_id].emotion.label in ("stressed", "annoyed", "sad")
            )
        ]
        if classroom_stress:
            stressed_id = classroom_stress[0]
            supporters = [
                x for x in intents.keys()
                if x not in used
                and x != stressed_id
                and intents[x]["loc"] == "classroom"
            ]
            actor_ids = [stressed_id] + supporters[:1]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _move_agents(agents, actor_ids, "classroom")
            if len(actor_ids) == 2:
                _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], trust=3, respect=2, closeness=2)
            _apply_simple_rewards(agents, actor_ids, "attend_class")

            description = (
                f"{agents[stressed_id].name} struggled with presentation pressure, "
                f"and the moment affected the classroom dynamic."
            )
            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "U6",
                TEMPLATE_MAP["U6"].title,
                description,
                "classroom",
                "mixed",
                0.64,
                -0.05,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 9) A9 late-night emotional talk
    # ------------------------------------------------------------------
    for actor_id, data in intents.items():
        if actor_id in used:
            continue

        action: ChosenAction = data["action"]  # type: ignore[assignment]
        loc: str = data["loc"]  # type: ignore[assignment]

        if action.action_type == "share_feelings" and action.target_character and world.current_slot in ("late_evening", "night"):
            target_id = action.target_character
            if target_id not in agents or target_id in used:
                continue

            actor_ids = [actor_id, target_id]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _move_agents(agents, actor_ids, loc)
            _apply_relationship_delta(relationships, actor_id, target_id, closeness=8, trust=9, tension=-2, respect=2)
            _apply_simple_rewards(agents, actor_ids, "share_feelings")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "A9",
                TEMPLATE_MAP["A9"].title,
                f"{agents[actor_id].name} and {agents[target_id].name} had a rare emotionally honest late-night conversation.",
                loc,
                "positive",
                0.84,
                0.75,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 10) A3 noise complaint
    # ------------------------------------------------------------------
    if world.current_slot in ("late_evening", "night"):
        bedroom_locations = {f"bedroom_{aid}" for aid in agents.keys()}

        noisemakers = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used
            and data["loc"] in {"living_room", "gym"}
            and data["action"].action_type in ("joke", "watch_movie", "play")
        ]
        complainers = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used
            and actor_id not in noisemakers
            and agents[actor_id].current_location in APARTMENT_SHARED.union(bedroom_locations)
            and (
                agents[actor_id].needs.rest >= 65
                or agents[actor_id].needs.order >= 65
                or actor_id == "ethan"
            )
        ]

        if noisemakers and complainers:
            noisemaker_id = noisemakers[0]
            complainer_id = complainers[0]
            actor_ids = [noisemaker_id, complainer_id]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _apply_relationship_delta(
                relationships,
                noisemaker_id,
                complainer_id,
                closeness=-3,
                trust=-2,
                tension=10,
                respect=-1,
            )

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "A3",
                TEMPLATE_MAP["A3"].title,
                f"{agents[complainer_id].name} complained about the noise {agents[noisemaker_id].name} was making late at night.",
                intents[noisemaker_id]["loc"],  # type: ignore[arg-type]
                "negative",
                0.78,
                -0.70,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 11) A7 apartment cleaning debate
    # ------------------------------------------------------------------
    cleaners = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and data["loc"] in {"living_room", "kitchen"}
        and data["action"].action_type == "clean"
        and world.current_slot in ("afternoon", "evening")
    ]
    loungers = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and data["loc"] in {"living_room", "kitchen"}
        and data["action"].action_type in ("watch_movie", "joke", "play", "eat")
    ]
    if cleaners and loungers:
        actor_ids = [cleaners[0], loungers[0]]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        loc = intents[cleaners[0]]["loc"]  # type: ignore[assignment]
        _move_agents(agents, actor_ids, loc)
        _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], tension=8, trust=-2, closeness=-1, respect=-1)
        _apply_simple_rewards(agents, [actor_ids[0]], "clean")
        _apply_simple_rewards(agents, [actor_ids[1]], "talk")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "A7",
            TEMPLATE_MAP["A7"].title,
            f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} got into a debate over apartment chores and mess.",
            loc,
            "mixed",
            0.73,
            -0.25,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 12) A8 gym challenge
    # ------------------------------------------------------------------
    gym_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used and data["loc"] == "gym" and data["action"].action_type in ("workout", "play")
    ]
    if len(gym_group) >= 2 and world.current_slot in ("evening", "late_evening"):
        actor_ids = gym_group[:2]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "gym")
        _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=2, respect=4, tension=2)
        _apply_simple_rewards(agents, actor_ids, "workout")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "A8",
            TEMPLATE_MAP["A8"].title,
            f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} turned a workout into a mild competition.",
            "gym",
            "mixed",
            0.63,
            0.20,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 13) P6 rain ruins plan
    # ------------------------------------------------------------------
    if world.weather == "rainy" and world.current_slot in ("evening", "late_evening"):
        rainy_park_group = [
            actor_id
            for actor_id, data in intents.items()
            if actor_id not in used and data["loc"] in PARK_SUBLOCS
        ]
        if len(rainy_park_group) >= 2:
            actor_ids = rainy_park_group[:2]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], trust=-1, tension=4, closeness=-1)
            _apply_simple_rewards(agents, actor_ids, "move")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "P6",
                TEMPLATE_MAP["P6"].title,
                f"Rain disrupted the amusement park rhythm and forced {agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} to change plans.",
                "entrance",
                "negative",
                0.69,
                -0.25,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 14) P5 souvenir choice (must be before P3)
    # ------------------------------------------------------------------
    souvenir_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and data["loc"] in {"food_court", "entrance"}
        and world.current_slot == "late_evening"
        and world.weather != "rainy"
        and data["action"].action_type in ("talk", "eat", "move")
    ]
    if len(souvenir_group) >= 2:
        actor_ids = _pick_best_pair_for_location(souvenir_group, relationships)
        if len(actor_ids) == 2:
            rel = relationships[actor_ids[0]][actor_ids[1]]
            if rel.closeness + rel.trust - rel.tension >= 12:
                before_needs = _snapshot_needs(agents, actor_ids)
                before_rels = _snapshot_relationships(relationships, actor_ids)

                loc = intents[actor_ids[0]]["loc"]  # type: ignore[assignment]
                _move_agents(agents, actor_ids, loc)
                _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=3, trust=2, respect=1)
                _apply_simple_rewards(agents, actor_ids, "talk")

                _finalize_event(
                    events, agents, relationships, world, actor_ids,
                    before_needs, before_rels,
                    "P5",
                    TEMPLATE_MAP["P5"].title,
                    f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} got unexpectedly thoughtful while choosing souvenirs.",
                    loc,
                    "positive",
                    0.50,
                    0.28,
                )
                used.update(actor_ids)

    # ------------------------------------------------------------------
    # 15) P3 getting split up (narrowed; only after P5)
    # ------------------------------------------------------------------
    park_movers = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used
        and agents[actor_id].current_location in PARK_SUBLOCS
        and data["loc"] in PARK_SUBLOCS
        and data["action"].action_type in ("move", "play", "go_out")
    ]

    if len(park_movers) >= 2 and world.current_slot in ("evening", "late_evening"):
        intended_locs = {intents[aid]["loc"] for aid in park_movers}
        actually_relocating = [
            aid for aid in park_movers
            if agents[aid].current_location != intents[aid]["loc"]
        ]

        if len(intended_locs) >= 2 and len(actually_relocating) >= 1:
            actor_ids = park_movers[:2]
            before_needs = _snapshot_needs(agents, actor_ids)
            before_rels = _snapshot_relationships(relationships, actor_ids)

            _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], trust=-2, tension=5, closeness=-1)
            _apply_simple_rewards(agents, actor_ids, "move")

            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "P3",
                TEMPLATE_MAP["P3"].title,
                f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} got separated while moving through the amusement park.",
                "entrance",
                "negative",
                0.65,
                -0.30,
            )
            used.update(actor_ids)

    # ------------------------------------------------------------------
    # 16) P2 coaster dare / P4 arcade competition
    # ------------------------------------------------------------------
    rides_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used and data["loc"] == "rides_area"
    ]
    if len(rides_group) >= 2:
        actor_ids = rides_group[:2]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "rides_area")
        _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=2, respect=3, tension=2)
        _apply_simple_rewards(agents, actor_ids, "play")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "P2",
            TEMPLATE_MAP["P2"].title,
            f"{agents[actor_ids[0]].name} pushed {agents[actor_ids[1]].name} into a thrill-seeking amusement park moment.",
            "rides_area",
            "mixed",
            0.68,
            0.15,
        )
        used.update(actor_ids)

    arcade_group = [
        actor_id
        for actor_id, data in intents.items()
        if actor_id not in used and data["loc"] == "arcade" and data["action"].action_type in ("play", "joke")
    ]
    if len(arcade_group) >= 2:
        actor_ids = arcade_group[:2]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, "arcade")
        _apply_relationship_delta(relationships, actor_ids[0], actor_ids[1], closeness=2, respect=2, tension=3)
        _apply_simple_rewards(agents, actor_ids, "play")

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            "P4",
            TEMPLATE_MAP["P4"].title,
            f"{agents[actor_ids[0]].name} and {agents[actor_ids[1]].name} got caught up in a playful arcade competition.",
            "arcade",
            "mixed",
            0.60,
            0.18,
        )
        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 17) generic pair interactions
    # ------------------------------------------------------------------
    for actor_id, data in intents.items():
        if actor_id in used:
            continue

        action: ChosenAction = data["action"]  # type: ignore[assignment]
        loc: str = data["loc"]  # type: ignore[assignment]

        if action.action_type not in ("talk", "help", "argue") or not action.target_character:
            continue

        target_id = action.target_character
        if target_id not in agents or target_id in used:
            continue

        actor_ids = [actor_id, target_id]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        _move_agents(agents, actor_ids, loc)

        if action.action_type == "talk":
            _apply_relationship_delta(relationships, actor_id, target_id, closeness=4, trust=2, tension=-1)
            _apply_simple_rewards(agents, actor_ids, "talk")
            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "GEN_TALK",
                "Talk interaction",
                f"{agents[actor_id].name} initiated a meaningful conversation with {agents[target_id].name}.",
                loc,
                "positive",
                0.54,
                0.25,
            )
        elif action.action_type == "help":
            _apply_relationship_delta(relationships, actor_id, target_id, closeness=4, trust=6, respect=2)
            _apply_simple_rewards(agents, actor_ids, "help")
            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "GEN_HELP",
                "Help interaction",
                f"{agents[actor_id].name} stepped in to help {agents[target_id].name}.",
                loc,
                "positive",
                0.62,
                0.40,
            )
        else:
            _apply_relationship_delta(relationships, actor_id, target_id, closeness=-4, trust=-3, tension=10, respect=-2)
            _apply_simple_rewards(agents, actor_ids, "argue")
            _finalize_event(
                events, agents, relationships, world, actor_ids,
                before_needs, before_rels,
                "GEN_ARGUE",
                "Argument",
                f"{agents[actor_id].name} and {agents[target_id].name} clashed directly.",
                loc,
                "negative",
                0.74,
                -0.65,
            )

        used.update(actor_ids)

    # ------------------------------------------------------------------
    # 18) single fallback
    # ------------------------------------------------------------------
    for actor_id, data in intents.items():
        if actor_id in used:
            continue

        actor = agents[actor_id]
        action: ChosenAction = data["action"]  # type: ignore[assignment]
        loc: str = data["loc"]  # type: ignore[assignment]

        actor_ids = [actor_id]
        before_needs = _snapshot_needs(agents, actor_ids)
        before_rels = _snapshot_relationships(relationships, actor_ids)

        actor.current_location = loc

        if action.action_type == "study":
            title = f"{actor.name} focused on studying"
            description = f"{actor.name} spent this slot studying at {loc}."
            tone = "positive"
            importance = 0.44
            sentiment = 0.20
        elif action.action_type == "attend_class":
            title = f"{actor.name} attended class"
            description = f"{actor.name} went through a normal class session."
            tone = "neutral"
            importance = 0.42
            sentiment = 0.05
        elif action.action_type == "rest":
            title = f"{actor.name} took a break"
            description = f"{actor.name} rested alone for a while."
            tone = "positive"
            importance = 0.38
            sentiment = 0.15
        elif action.action_type == "cook":
            title = f"{actor.name} cooked"
            description = f"{actor.name} spent time in the kitchen."
            tone = "positive"
            importance = 0.40
            sentiment = 0.20
        elif action.action_type == "clean":
            title = f"{actor.name} cleaned up"
            description = f"{actor.name} tried to make the shared space more orderly."
            tone = "mixed"
            importance = 0.48
            sentiment = 0.10
        elif action.action_type == "workout":
            title = f"{actor.name} worked out"
            description = f"{actor.name} used the gym alone."
            tone = "positive"
            importance = 0.46
            sentiment = 0.20
        elif action.action_type == "eat":
            title = f"{actor.name} grabbed food"
            description = f"{actor.name} went to the kitchen for a meal."
            tone = "neutral"
            importance = 0.34
            sentiment = 0.05
        elif action.action_type == "move":
            title = f"{actor.name} moved locations"
            description = f"{actor.name} went to {loc}."
            tone = "neutral"
            importance = 0.30
            sentiment = 0.00
        elif action.action_type == "go_out":
            title = f"{actor.name} headed out"
            description = f"{actor.name} decided to go out alone."
            tone = "positive"
            importance = 0.52
            sentiment = 0.20
        elif action.action_type == "watch_movie":
            title = f"{actor.name} started a movie"
            description = f"{actor.name} settled into a solo movie session."
            tone = "positive"
            importance = 0.42
            sentiment = 0.20
        elif action.action_type == "play":
            title = f"{actor.name} looked for fun"
            description = f"{actor.name} did something playful to fight boredom."
            tone = "positive"
            importance = 0.44
            sentiment = 0.20
        else:
            title = f"{actor.name} acted"
            description = f"{actor.name} spent the slot doing something routine."
            tone = "neutral"
            importance = 0.30
            sentiment = 0.00

        apply_need_rewards(actor, action.action_type)
        update_emotion_after_action(actor, action.action_type, success=True)

        _finalize_event(
            events, agents, relationships, world, actor_ids,
            before_needs, before_rels,
            f"SINGLE_{action.action_type.upper()}",
            title,
            description,
            loc,
            tone,
            importance,
            sentiment,
        )
        used.add(actor_id)

    return events