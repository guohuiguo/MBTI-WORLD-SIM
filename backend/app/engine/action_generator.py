from typing import List

from app.data.locations import AMUSEMENT_ZONE, APARTMENT_ZONE, UNIVERSITY_ZONE
from app.models.state_models import AgentState, CandidateAction, RelationshipMatrix, WorldState

BATHROOMS = {"bathroom_a", "bathroom_b"}


def _is_weekday_class_time(world: WorldState) -> bool:
    return world.day_type == "weekday" and world.current_slot in ("late_morning", "afternoon")


def _trusted_targets(agent_id: str, relationships: RelationshipMatrix, min_trust: int = 10) -> list[str]:
    result = []
    for other_id, rel in relationships[agent_id].items():
        if other_id == agent_id:
            continue
        if rel.trust >= min_trust:
            result.append(other_id)
    return result


def generate_candidate_actions(
    agent: AgentState,
    world: WorldState,
    relationships: RelationshipMatrix,
) -> List[CandidateAction]:
    actions: List[CandidateAction] = []

    current_loc = agent.current_location
    in_apartment = current_loc in APARTMENT_ZONE
    in_university = current_loc in UNIVERSITY_ZONE
    in_park = current_loc in AMUSEMENT_ZONE

    # morning apartment routines
    if world.current_slot == "morning" and in_apartment:
        preferred_bathroom = "bathroom_a" if agent.id in ("ethan", "grace") else "bathroom_b"
        actions.append(CandidateAction(action_type="move", target_location=preferred_bathroom, note="Morning bathroom routine"))
        actions.append(CandidateAction(action_type="eat", target_location="kitchen", note="Grab breakfast"))

    # weekday class / campus routine
    if _is_weekday_class_time(world):
        actions.append(CandidateAction(action_type="move", target_location="classroom", note="Go to class"))
        actions.append(CandidateAction(action_type="attend_class", target_location="classroom", note="Attend class"))
        actions.append(CandidateAction(action_type="move", target_location="library", note="Go to library"))
        actions.append(CandidateAction(action_type="study", target_location="library", note="Study on campus"))

        # U4 cafeteria setup
        if world.current_slot == "afternoon":
            actions.append(CandidateAction(action_type="move", target_location="cafeteria", note="Head to cafeteria"))
            actions.append(CandidateAction(action_type="eat", target_location="cafeteria", note="Get lunch on campus"))
            actions.append(CandidateAction(action_type="talk", target_location="cafeteria", note="Talk during lunch break"))

    # tired
    if agent.needs.rest >= 70:
        bedroom = f"bedroom_{agent.id}"
        actions.append(CandidateAction(action_type="move", target_location=bedroom, note="Need rest"))
        actions.append(CandidateAction(action_type="rest", target_location=bedroom, note="Recover energy"))

    # achievement
    if agent.needs.achievement >= 60:
        target = "library" if not in_university else current_loc
        actions.append(CandidateAction(action_type="move", target_location=target, note="Go study"))
        actions.append(CandidateAction(action_type="study", target_location=target, note="Focus on academics"))
        for other_id in relationships[agent.id]:
            if other_id == agent.id:
                continue
            actions.append(
                CandidateAction(
                    action_type="invite",
                    target_character=other_id,
                    target_location="library",
                    note="Invite someone to a study session",
                )
            )

    # social
    if agent.needs.social >= 60:
        for other_id in relationships[agent.id]:
            if other_id == agent.id:
                continue
            actions.append(CandidateAction(action_type="talk", target_character=other_id, note="Need social interaction"))

    # park logic
    if in_park:
        # rainy park => try to regroup / shelter
        if world.weather == "rainy" and world.current_slot in ("evening", "late_evening"):
            actions.append(CandidateAction(action_type="move", target_location="entrance", note="Rain is disrupting the plan"))
            actions.append(CandidateAction(action_type="move", target_location="food_court", note="Look for cover and regroup"))
            actions.append(CandidateAction(action_type="eat", target_location="food_court", note="Wait out the rain"))

        # normal park movement
        if world.current_slot in ("evening", "late_evening"):
            actions.append(CandidateAction(action_type="move", target_location="rides_area", note="Try something thrilling"))
            actions.append(CandidateAction(action_type="move", target_location="arcade", note="Look for a fun challenge"))
            actions.append(CandidateAction(action_type="move", target_location="food_court", note="Take a break in the park"))
            actions.append(CandidateAction(action_type="move", target_location="entrance", note="Regroup near the entrance"))
            actions.append(CandidateAction(action_type="play", target_location="rides_area", note="Do something exciting"))
            actions.append(CandidateAction(action_type="play", target_location="arcade", note="Play at the arcade"))

        # P5 late-evening souvenir vibe
        if world.current_slot == "late_evening":
            actions.append(CandidateAction(action_type="talk", target_location="food_court", note="Talk while winding down"))
            actions.append(CandidateAction(action_type="eat", target_location="food_court", note="Grab something before leaving"))
            actions.append(CandidateAction(action_type="move", target_location="entrance", note="Browse near the exit"))

    # novelty / park entry
    if agent.needs.novelty >= 65:
        if world.current_slot in ("evening", "late_evening"):
            if not in_park:
                actions.append(CandidateAction(action_type="go_out", target_location="entrance", note="Seek novelty"))
                for other_id in relationships[agent.id]:
                    if other_id != agent.id:
                        actions.append(
                            CandidateAction(
                                action_type="invite",
                                target_character=other_id,
                                target_location="entrance",
                                note="Invite someone to go to the amusement park",
                            )
                        )
            else:
                actions.append(CandidateAction(action_type="play", target_location="rides_area", note="Need stimulation in the park"))
                actions.append(CandidateAction(action_type="play", target_location="arcade", note="Need stimulation in the arcade"))
        else:
            actions.append(CandidateAction(action_type="play", target_location="living_room", note="Need stimulation"))

    # order
    if agent.needs.order >= 60 and in_apartment:
        actions.append(CandidateAction(action_type="clean", target_location="living_room", note="Restore order in the living room"))
        actions.append(CandidateAction(action_type="clean", target_location="kitchen", note="Restore order in the kitchen"))

    # apartment food / shared evening
    if in_apartment and world.current_slot in ("evening", "late_evening"):
        actions.append(CandidateAction(action_type="eat", target_location="kitchen", note="Evening snack or meal"))
        actions.append(CandidateAction(action_type="cook", target_location="kitchen", note="Prepare food in the kitchen"))
        actions.append(CandidateAction(action_type="talk", target_location="kitchen", note="Talk in the kitchen"))

    # character bias
    if agent.id == "chloe":
        actions.append(CandidateAction(action_type="workout", target_location="gym", note="Chloe enjoys action"))
        for other_id in relationships[agent.id]:
            if other_id != agent.id:
                actions.append(
                    CandidateAction(
                        action_type="invite",
                        target_character=other_id,
                        target_location="gym",
                        note="Invite someone to the gym",
                    )
                )

    if agent.id == "leo":
        actions.append(CandidateAction(action_type="watch_movie", target_location="living_room", note="Leo likes shared fun"))
        actions.append(CandidateAction(action_type="joke", target_location="living_room", note="Leo lightens the mood"))
        for other_id in relationships[agent.id]:
            if other_id != agent.id:
                actions.append(
                    CandidateAction(
                        action_type="invite",
                        target_character=other_id,
                        target_location="living_room",
                        note="Invite someone to hang out in the living room",
                    )
                )

    if agent.id == "ethan":
        actions.append(CandidateAction(action_type="study", target_location="library", note="Ethan prefers productivity"))
        if in_apartment and world.current_slot in ("evening", "late_evening"):
            actions.append(CandidateAction(action_type="clean", target_location="living_room", note="Ethan dislikes mess"))

    if agent.id == "grace":
        actions.append(CandidateAction(action_type="cook", target_location="kitchen", note="Grace maintains shared routine"))
        trusted = _trusted_targets(agent.id, relationships, min_trust=8)
        if world.current_slot in ("late_evening", "night"):
            for other_id in trusted:
                actions.append(
                    CandidateAction(
                        action_type="share_feelings",
                        target_character=other_id,
                        target_location="living_room",
                        note="Grace builds emotional connection",
                    )
                )
        for other_id in relationships[agent.id]:
            if other_id != agent.id:
                actions.append(CandidateAction(action_type="help", target_character=other_id, note="Grace offers support"))

    # default fallback
    actions.append(CandidateAction(action_type="eat", target_location="kitchen", note="Basic routine"))
    actions.append(CandidateAction(action_type="move", target_location="living_room", note="Default move"))

    unique = []
    seen = set()
    for act in actions:
        key = (act.action_type, act.target_character, act.target_location, act.note)
        if key not in seen:
            seen.add(key)
            unique.append(act)

    return unique[:14]