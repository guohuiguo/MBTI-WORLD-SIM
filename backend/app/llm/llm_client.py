from __future__ import annotations

import json
import os
import traceback
from typing import List, Optional

from app.config import settings
from app.models.event_models import DailyReport
from app.models.state_models import (
    AgentState,
    CandidateAction,
    ChosenAction,
    RelationshipMatrix,
    WorldState,
)

try:
    from google import genai
except Exception:
    genai = None


class LLMClient:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled
        self.model_name = settings.gemini_model
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.enabled and self.api_key and genai is not None:
            self.client = genai.Client(api_key=self.api_key)

        print(
            "[LLMClient] init:",
            {
                "enabled": self.enabled,
                "model_name": self.model_name,
                "has_api_key": bool(self.api_key),
                "genai_imported": genai is not None,
                "client_ready": self.client is not None,
            },
        )

    def choose_action(
        self,
        agent: AgentState,
        world: WorldState,
        relationships: RelationshipMatrix,
        candidate_actions: List[CandidateAction],
    ) -> ChosenAction:
        if not self.enabled or self.client is None:
            return self._rule_based_fallback(agent, world, relationships, candidate_actions)

        prompt = self._build_action_prompt(agent, world, relationships, candidate_actions)

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": ChosenAction.model_json_schema(),
                },
            )

            text = response.text if hasattr(response, "text") else ""
            if not text:
                print("[Gemini choose_action] Empty response.text")
                return self._rule_based_fallback(agent, world, relationships, candidate_actions)

            try:
                parsed = ChosenAction.model_validate_json(text)
                return self._sanitize_choice(parsed, candidate_actions)
            except Exception as parse_err:
                print("[Gemini choose_action] JSON parse failed")
                print("agent:", agent.id)
                print("raw text:", text)
                print("parse error:", repr(parse_err))
                return self._rule_based_fallback(agent, world, relationships, candidate_actions)

        except Exception as api_err:
            print("=" * 80)
            print("[Gemini choose_action] API CALL FAILED")
            print("agent:", agent.id)
            print("model:", self.model_name)
            print("error type:", type(api_err).__name__)
            print("error repr:", repr(api_err))
            print("traceback:")
            traceback.print_exc()
            print("=" * 80)
            return self._rule_based_fallback(agent, world, relationships, candidate_actions)

    def generate_daily_report(
        self,
        day: int,
        report_context: dict,
    ) -> Optional[DailyReport]:
        if not self.enabled or self.client is None:
            return None

        prompt = (
            "You are generating a concise in-universe daily report for a social simulation game.\n"
            "Be specific, readable, and grounded only in the provided context.\n"
            "Return JSON only.\n\n"
            f"Context:\n{json.dumps(report_context, ensure_ascii=False, indent=2)}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": DailyReport.model_json_schema(),
                },
            )

            text = response.text if hasattr(response, "text") else ""
            if not text:
                print("[Gemini daily_report] Empty response.text")
                return None

            try:
                report = DailyReport.model_validate_json(text)
                report.day = day
                return report
            except Exception as parse_err:
                print("[Gemini daily_report] JSON parse failed")
                print("day:", day)
                print("raw text:", text)
                print("parse error:", repr(parse_err))
                return None

        except Exception as api_err:
            print("=" * 80)
            print("[Gemini daily_report] API CALL FAILED")
            print("day:", day)
            print("model:", self.model_name)
            print("error type:", type(api_err).__name__)
            print("error repr:", repr(api_err))
            print("traceback:")
            traceback.print_exc()
            print("=" * 80)
            return None

    def _build_action_prompt(
        self,
        agent: AgentState,
        world: WorldState,
        relationships: RelationshipMatrix,
        candidate_actions: List[CandidateAction],
    ) -> str:
        visible_characters = []
        for other_id, rel in relationships[agent.id].items():
            if other_id == agent.id:
                continue
            visible_characters.append(
                {
                    "id": other_id,
                    "relationship": rel.model_dump(),
                }
            )

        prompt_obj = {
            "system_role": (
                f"You are {agent.name}, a {agent.age}-year-old {agent.gender} college student "
                f"with {agent.mbti}-like traits. Stay consistent with your personality, current needs, "
                f"current emotion, and relationship history. Choose only one action from candidate_actions. "
                f"Return strict JSON matching the schema."
            ),
            "self_profile": {
                "name": agent.name,
                "mbti": agent.mbti,
                "major": agent.major,
                "personality": agent.personality.model_dump(),
                "emotion": agent.emotion.model_dump(),
                "needs": agent.needs.model_dump(),
                "current_location": agent.current_location,
                "short_term_goal": agent.short_term_goal,
                "long_term_style_goal": agent.long_term_style_goal,
                "recent_memories": [m.model_dump() for m in agent.memories[-5:]],
            },
            "world": world.model_dump(),
            "relationships": visible_characters,
            "candidate_actions": [c.model_dump() for c in candidate_actions],
            "instructions": [
                "Prefer actions that make sense in the current location and time slot.",
                "Do not invent unsupported action types.",
                "Do not invent unsupported target characters.",
                "You may leave utterance empty if the action is not dialog-heavy.",
                "Reason should be short and grounded in needs/emotion/personality.",
            ],
        }
        return json.dumps(prompt_obj, ensure_ascii=False, indent=2)

    def _sanitize_choice(
        self,
        choice: ChosenAction,
        candidate_actions: List[CandidateAction],
    ) -> ChosenAction:
        allowed = {
            (c.action_type, c.target_character, c.target_location)
            for c in candidate_actions
        }

        key = (choice.action_type, choice.target_character, choice.target_location)
        if key in allowed:
            return choice

        for c in candidate_actions:
            if c.action_type == choice.action_type:
                return ChosenAction(
                    action_type=c.action_type,
                    target_character=c.target_character,
                    target_location=c.target_location,
                    utterance=choice.utterance,
                    reason=f"Sanitized from invalid target. Original reason: {choice.reason}",
                )

        c = candidate_actions[0]
        return ChosenAction(
            action_type=c.action_type,
            target_character=c.target_character,
            target_location=c.target_location,
            utterance="",
            reason="Sanitized to first candidate.",
        )

    def _rule_based_fallback(
        self,
        agent: AgentState,
        world: WorldState,
        relationships: RelationshipMatrix,
        candidate_actions: List[CandidateAction],
    ) -> ChosenAction:
        scored = []
        for action in candidate_actions:
            score = self._score_action(agent, world, relationships, action)
            scored.append((score, action))

        scored.sort(key=lambda x: x[0], reverse=True)
        best = scored[0][1]

        return ChosenAction(
            action_type=best.action_type,
            target_character=best.target_character,
            target_location=best.target_location,
            utterance=self._build_utterance(agent, best),
            reason=f"Rule-based fallback score={scored[0][0]:.2f}",
        )

    def _score_action(
        self,
        agent: AgentState,
        world: WorldState,
        relationships: RelationshipMatrix,
        action: CandidateAction,
    ) -> float:
        score = 0.0

        if action.action_type in ("talk", "invite", "watch_movie", "share_feelings"):
            score += agent.needs.social * 0.6
            score += agent.personality.sociability * 0.3

        if action.action_type in ("study", "attend_class"):
            score += agent.needs.achievement * 0.7
            score += agent.personality.planning * 0.2

        if action.action_type == "rest":
            score += agent.needs.rest * 0.9

        if action.action_type == "clean":
            score += agent.needs.order * 0.8
            score += agent.personality.orderliness * 0.2

        if action.action_type in ("go_out", "play", "workout"):
            score += agent.needs.novelty * 0.7
            score += agent.personality.impulsiveness * 0.2

        if action.action_type == "help":
            score += agent.personality.empathy * 0.7
            score += agent.needs.belonging * 0.2

        if agent.id == "ethan" and action.action_type in ("study", "clean"):
            score += 10
        if agent.id == "leo" and action.action_type in ("invite", "watch_movie", "joke", "talk"):
            score += 10
        if agent.id == "grace" and action.action_type in ("cook", "help", "share_feelings"):
            score += 10
        if agent.id == "chloe" and action.action_type in ("workout", "go_out", "play"):
            score += 10

        return score

    def _build_utterance(self, agent: AgentState, action: CandidateAction) -> str:
        if action.action_type == "invite":
            return f"{agent.name} invites someone to do something together."
        if action.action_type == "talk":
            return f"{agent.name} starts a conversation."
        if action.action_type == "argue":
            return f"{agent.name} pushes back sharply."
        if action.action_type == "share_feelings":
            return f"{agent.name} opens up emotionally."
        if action.action_type == "watch_movie":
            return f"{agent.name} suggests a movie night."
        return ""