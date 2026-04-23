from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from app.models.state_models import CharacterId, TimeSlot


EventTone = Literal["positive", "neutral", "negative", "mixed"]


class EventTemplate(BaseModel):
    id: str
    title: str
    category: str
    location_tags: List[str] = Field(default_factory=list)
    time_slots: List[TimeSlot] = Field(default_factory=list)
    min_actors: int = 1
    max_actors: int = 2
    tone: EventTone = "neutral"
    base_importance: float = 0.5
    tags: List[str] = Field(default_factory=list)


class EventEffect(BaseModel):
    need_delta: Dict[str, float] = Field(default_factory=dict)
    relationship_delta: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class EventRecord(BaseModel):
    id: str
    day: int
    slot: TimeSlot
    template_id: str
    title: str
    description: str
    actors: List[CharacterId]
    location: str
    tone: EventTone
    importance: float
    effects: Optional[EventEffect] = None


class DailyReport(BaseModel):
    day: int
    headline: str
    top_events: List[str]
    relationship_changes: List[str]
    character_highlights: Dict[str, str]
    tomorrow_hooks: List[str]