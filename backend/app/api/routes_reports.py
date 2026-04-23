from fastapi import APIRouter
from app.runtime import engine
from app.models.api_models import ReportResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{day}", response_model=ReportResponse)
def get_report(day: int) -> ReportResponse:
    return ReportResponse(report=engine.reports.get(day))