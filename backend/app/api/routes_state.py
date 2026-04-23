from fastapi import APIRouter
from app.models.api_models import StateResponse
from app.runtime import engine

router = APIRouter(prefix="/state", tags=["state"])


@router.get("", response_model=StateResponse)
def get_state() -> StateResponse:
    return StateResponse(
        world=engine.world,
        agents=engine.agents,
        relationships=engine.relationships,
        today_events=engine.today_events,
    )