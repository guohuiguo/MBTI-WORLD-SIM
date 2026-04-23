from fastapi import APIRouter, Query

from app.runtime import engine

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/supported-template-scenarios")
def get_supported_template_scenarios() -> dict:
    return {
        "supported": ["A4", "U4", "P5", "P6"],
        "usage": [
            "POST /debug/prepare-template/A4",
            "POST /simulation/step",
            "GET /frontend/overview",
        ],
    }


@router.post("/prepare-template/{template_id}")
def prepare_template(template_id: str) -> dict:
    return engine.prepare_template_scenario(template_id)


@router.post("/run-days")
def run_days(days: int = Query(default=10, ge=1, le=200)) -> dict:
    return engine.run_multiple_days(days=days)