from fastapi import APIRouter

from app.engine.frontend_view_builder import build_frontend_overview
from app.runtime import engine

router = APIRouter(prefix="/frontend", tags=["frontend"])


@router.get("/overview")
def get_frontend_overview() -> dict:
    latest_report = engine.reports.get(engine.world.day - 1)
    return build_frontend_overview(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
        last_completed_day_events=engine.last_completed_day_events,
        latest_report=latest_report,
    )


@router.get("/focus-events")
def get_focus_events() -> dict:
    latest_report = engine.reports.get(engine.world.day - 1)
    overview = build_frontend_overview(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
        last_completed_day_events=engine.last_completed_day_events,
        latest_report=latest_report,
    )
    return {"focus_events": overview["focus_events"]}


@router.get("/event-feed")
def get_event_feed() -> dict:
    latest_report = engine.reports.get(engine.world.day - 1)
    overview = build_frontend_overview(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
        last_completed_day_events=engine.last_completed_day_events,
        latest_report=latest_report,
    )
    return {"event_feed": overview["event_feed"]}


@router.get("/character-cards")
def get_character_cards() -> dict:
    latest_report = engine.reports.get(engine.world.day - 1)
    overview = build_frontend_overview(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
        last_completed_day_events=engine.last_completed_day_events,
        latest_report=latest_report,
    )
    return {"character_cards": overview["character_cards"]}


@router.get("/relationship-graph")
def get_relationship_graph() -> dict:
    latest_report = engine.reports.get(engine.world.day - 1)
    overview = build_frontend_overview(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
        last_completed_day_events=engine.last_completed_day_events,
        latest_report=latest_report,
    )
    return {"relationship_graph": overview["relationship_graph"]}