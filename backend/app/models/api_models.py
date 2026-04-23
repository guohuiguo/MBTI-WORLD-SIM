from typing import Dict, List, Optional
from pydantic import BaseModel
from app.models.event_models import DailyReport, EventRecord
from app.models.state_models import AgentState, RelationshipMatrix, WorldState


class StateResponse(BaseModel):
    world: WorldState
    agents: Dict[str, AgentState]
    relationships: RelationshipMatrix
    today_events: List[EventRecord]


class StepResponse(BaseModel):
    world: WorldState
    new_events: List[EventRecord]
    agents: Dict[str, AgentState]
    relationships: RelationshipMatrix


class RunDayResponse(BaseModel):
    world: WorldState
    all_events: List[EventRecord]
    report: DailyReport
    agents: Dict[str, AgentState]
    relationships: RelationshipMatrix


class ReportResponse(BaseModel):
    report: Optional[DailyReport] = None