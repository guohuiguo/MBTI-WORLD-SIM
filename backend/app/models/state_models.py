from __future__ import annotations

from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field


CharacterId = Literal["ethan", "leo", "grace", "chloe"]
TimeSlot = Literal[
    "morning",
    "late_morning",
    "afternoon",
    "evening",
    "late_evening",
    "night",
]
DayType = Literal["weekday", "weekend"]
EmotionLabel = Literal[
    "calm",
    "happy",
    "excited",
    "annoyed",
    "stressed",
    "lonely",
    "embarrassed",
    "sad",
    "satisfied",
]
ActionType = Literal[
    "move",
    "rest",
    "study",
    "cook",
    "clean",
    "talk",
    "invite",
    "joke",
    "argue",
    "workout",
    "help",
    "play",
    "go_out",
    "attend_class",
    "eat",
    "watch_movie",
    "share_feelings",
]


class PersonalityProfile(BaseModel):
    sociability: int
    planning: int
    empathy: int
    impulsiveness: int
    orderliness: int
    competitiveness: int
    curiosity: int
    expressiveness: int


class NeedState(BaseModel):
    social: float = 50.0
    achievement: float = 50.0
    rest: float = 50.0
    order: float = 50.0
    novelty: float = 50.0
    belonging: float = 50.0
    autonomy: float = 50.0


class EmotionState(BaseModel):
    label: EmotionLabel = "calm"
    intensity: float = 0.3
    valence: float = 0.0
    arousal: float = 0.3


class MemoryItem(BaseModel):
    day: int
    summary: str
    related_characters: List[CharacterId] = Field(default_factory=list)
    location: str
    importance: float = 0.5
    sentiment: float = 0.0


class AgentState(BaseModel):
    id: CharacterId
    name: str
    mbti: str
    gender: str
    age: int
    major: str
    personality: PersonalityProfile
    needs: NeedState
    emotion: EmotionState
    current_location: str
    short_term_goal: Optional[str] = None
    long_term_style_goal: Optional[str] = None
    memories: List[MemoryItem] = Field(default_factory=list)


class RelationshipState(BaseModel):
    closeness: int = 0
    trust: int = 0
    tension: int = 0
    respect: int = 0


RelationshipMatrix = Dict[CharacterId, Dict[CharacterId, RelationshipState]]


class CandidateAction(BaseModel):
    action_type: ActionType
    target_character: Optional[CharacterId] = None
    target_location: Optional[str] = None
    note: str = ""


class ChosenAction(BaseModel):
    action_type: ActionType
    target_character: Optional[CharacterId] = None
    target_location: Optional[str] = None
    utterance: str = ""
    reason: str = ""


class WorldState(BaseModel):
    day: int = 1
    weekday_name: str = "Monday"
    day_type: DayType = "weekday"
    current_slot: TimeSlot = "morning"
    weather: str = "sunny"
    active_global_tags: List[str] = Field(default_factory=list)
    occupancy: Dict[str, List[CharacterId]] = Field(default_factory=dict)


class SimulationSnapshot(BaseModel):
    world: WorldState
    agents: Dict[CharacterId, AgentState]
    relationships: RelationshipMatrix