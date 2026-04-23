from __future__ import annotations

import random
from typing import Dict, List

from app.config import settings
from app.data.characters import build_initial_agents
from app.data.initial_relationships import build_initial_relationships
from app.data.locations import build_empty_occupancy
from app.engine.action_generator import generate_candidate_actions
from app.engine.action_resolver import resolve_slot_actions
from app.engine.emotion_engine import apply_lonely_if_needed
from app.engine.event_director import inject_global_tag_if_needed
from app.engine.need_engine import drift_needs
from app.engine.report_generator import generate_daily_report
from app.llm.llm_client import LLMClient
from app.models.event_models import DailyReport, EventRecord
from app.models.state_models import AgentState, ChosenAction, RelationshipMatrix, WorldState
from app.storage.json_store import JsonStateStore


SLOTS = [
    "morning",
    "late_morning",
    "afternoon",
    "evening",
    "late_evening",
    "night",
]

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class SimulationEngine:
    def __init__(self) -> None:
        random.seed(settings.random_seed)
        self.llm = LLMClient(enabled=settings.use_llm)
        self.store = JsonStateStore()

        self.world: WorldState
        self.agents: Dict[str, AgentState]
        self.relationships: RelationshipMatrix
        self.today_events: List[EventRecord]
        self.last_completed_day_events: List[EventRecord]
        self.reports: Dict[int, DailyReport]

        if self.store.exists():
            self._load_state()
        else:
            self._init_fresh_state()
            self._save_state()

    def _init_fresh_state(self) -> None:
        self.world = WorldState()
        self.agents = build_initial_agents()
        self.relationships = build_initial_relationships()
        self.today_events = []
        self.last_completed_day_events = []
        self.reports = {}
        self._update_day_meta()
        self._roll_daily_weather()
        self._rebuild_occupancy()

    def _serialize_state(self) -> dict:
        return {
            "world": self.world.model_dump(),
            "agents": {k: v.model_dump() for k, v in self.agents.items()},
            "relationships": {
                a: {b: rel.model_dump() for b, rel in row.items()}
                for a, row in self.relationships.items()
            },
            "today_events": [e.model_dump() for e in self.today_events],
            "last_completed_day_events": [e.model_dump() for e in self.last_completed_day_events],
            "reports": {str(day): report.model_dump() for day, report in self.reports.items()},
        }

    def _load_state(self) -> None:
        data = self.store.load()
        if not data:
            self._init_fresh_state()
            return

        self.world = WorldState.model_validate(data["world"])
        self.agents = {k: AgentState.model_validate(v) for k, v in data["agents"].items()}
        self.relationships = {
            a: {b: type(next(iter(row.values()))) .model_validate(rel) if False else None for b, rel in row.items()}
            for a, row in {}
        }  # 占位，下面覆盖
        self.relationships = {
            a: {b: self._relationship_model_validate(rel) for b, rel in row.items()}
            for a, row in data["relationships"].items()
        }
        self.today_events = [EventRecord.model_validate(e) for e in data.get("today_events", [])]
        self.last_completed_day_events = [
            EventRecord.model_validate(e) for e in data.get("last_completed_day_events", [])
        ]
        self.reports = {
            int(day): DailyReport.model_validate(report)
            for day, report in data.get("reports", {}).items()
        }
        self._rebuild_occupancy()

    @staticmethod
    def _relationship_model_validate(rel: dict):
        from app.models.state_models import RelationshipState
        return RelationshipState.model_validate(rel)

    def _save_state(self) -> None:
        self.store.save(self._serialize_state())

    def reset(self) -> None:
        self._init_fresh_state()
        self._save_state()

    def _rebuild_occupancy(self) -> None:
        occupancy = build_empty_occupancy()
        for agent_id, agent in self.agents.items():
            occupancy.setdefault(agent.current_location, [])
            occupancy[agent.current_location].append(agent_id)
        self.world.occupancy = occupancy

    def _update_day_meta(self) -> None:
        weekday_index = (self.world.day - 1) % 7
        self.world.weekday_name = WEEKDAYS[weekday_index]
        self.world.day_type = "weekend" if self.world.weekday_name in ("Saturday", "Sunday") else "weekday"

    def _advance_slot(self) -> bool:
        idx = SLOTS.index(self.world.current_slot)
        if idx < len(SLOTS) - 1:
            self.world.current_slot = SLOTS[idx + 1]
            return False
        self.world.current_slot = SLOTS[0]
        return True

    def step_slot(self) -> List[EventRecord]:
        self._update_day_meta()
        self._rebuild_occupancy()
        inject_global_tag_if_needed(self.today_events, self.world)

        chosen_actions: Dict[str, ChosenAction] = {}
        agent_order = list(self.agents.keys())
        random.shuffle(agent_order)

        for agent_id in agent_order:
            agent = self.agents[agent_id]
            same_location_count = len(self.world.occupancy.get(agent.current_location, []))

            drift_needs(agent, self.world, same_location_count)
            apply_lonely_if_needed(agent)

            candidates = generate_candidate_actions(agent, self.world, self.relationships)
            chosen = self.llm.choose_action(agent, self.world, self.relationships, candidates)
            chosen_actions[agent_id] = chosen

        new_events = resolve_slot_actions(
            chosen_actions=chosen_actions,
            world=self.world,
            agents=self.agents,
            relationships=self.relationships,
        )

        self.today_events.extend(new_events)
        self._rebuild_occupancy()

        day_finished = self._advance_slot()
        if day_finished:
            report = self.finish_day()
            self.reports[report.day] = report
            self.world.day += 1
            self._update_day_meta()
            self._roll_daily_weather()
            self._rebuild_occupancy()

        self._save_state()
        return new_events

    def finish_day(self) -> DailyReport:
        report_context = {
            "day": self.world.day,
            "events": [e.model_dump() for e in self.today_events],
            "agents": {k: v.model_dump() for k, v in self.agents.items()},
            "relationships": {
                a: {b: rel.model_dump() for b, rel in row.items()}
                for a, row in self.relationships.items()
            },
        }

        llm_report = self.llm.generate_daily_report(self.world.day, report_context)
        if llm_report is not None:
            report = llm_report
        else:
            report = generate_daily_report(
                day=self.world.day,
                events=self.today_events,
                agents=self.agents,
                relationships=self.relationships,
            )

        self.last_completed_day_events = list(self.today_events)
        self.today_events = []
        return report

    def run_full_day(self) -> tuple[List[EventRecord], DailyReport]:
        all_events: List[EventRecord] = []
        start_day = self.world.day

        while self.world.day == start_day:
            new_events = self.step_slot()
            all_events.extend(new_events)

        report = self.reports[start_day]
        self._save_state()
        return all_events, report
    
    def _roll_daily_weather(self) -> None:
        value = random.random()
        if value < 0.60:
            self.world.weather = "sunny"
        elif value < 0.85:
            self.world.weather = "cloudy"
        else:
            self.world.weather = "rainy"

    def save_state(self) -> None:
        self._save_state()

    def prepare_template_scenario(self, template_id: str) -> dict:
        from app.engine.debug_scenarios import prepare_template_scenario

        self.today_events = []
        info = prepare_template_scenario(
            template_id=template_id,
            world=self.world,
            agents=self.agents,
            relationships=self.relationships,
        )
        self._update_day_meta()
        self._rebuild_occupancy()
        self._save_state()
        return {
            "ok": True,
            "scenario": info,
            "world": self.world.model_dump(),
        }

    def run_multiple_days(self, days: int = 10) -> dict:
        template_counts: dict[str, int] = {}
        generated_days: list[int] = []

        for _ in range(days):
            start_day = self.world.day
            events, _report = self.run_full_day()
            generated_days.append(start_day)
            for event in events:
                template_counts[event.template_id] = template_counts.get(event.template_id, 0) + 1

        sorted_counts = dict(sorted(template_counts.items(), key=lambda x: x[1], reverse=True))
        self._save_state()
        return {
            "days_run": days,
            "generated_days": generated_days,
            "template_counts": sorted_counts,
            "unique_template_count": len(sorted_counts),
        }