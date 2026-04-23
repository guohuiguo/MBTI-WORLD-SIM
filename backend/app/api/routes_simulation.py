from fastapi import APIRouter
from app.runtime import engine
from app.models.api_models import RunDayResponse, StepResponse

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/step", response_model=StepResponse)
def step_simulation() -> StepResponse:
    new_events = engine.step_slot()
    return StepResponse(
        world=engine.world,
        new_events=new_events,
        agents=engine.agents,
        relationships=engine.relationships,
    )


@router.post("/run-day", response_model=RunDayResponse)
def run_day() -> RunDayResponse:
    all_events, report = engine.run_full_day()
    return RunDayResponse(
        world=engine.world,
        all_events=all_events,
        report=report,
        agents=engine.agents,
        relationships=engine.relationships,
    )


@router.post("/reset")
def reset_simulation() -> dict:
    engine.reset()
    return {"ok": True, "message": "simulation reset"}