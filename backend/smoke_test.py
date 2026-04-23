from dotenv import load_dotenv
load_dotenv()

from app.engine.simulation_engine import SimulationEngine


def main() -> None:
    engine = SimulationEngine()

    print("=== Initial State ===")
    print(f"day={engine.world.day}, weekday={engine.world.weekday_name}, slot={engine.world.current_slot}")
    print(f"today_events={len(engine.today_events)}")

    print("\n=== Run One Full Day ===")
    all_events, report = engine.run_full_day()

    print(f"generated_events={len(all_events)}")
    for i, event in enumerate(all_events[:10], start=1):
        print(
            f"[{i}] day={event.day}, slot={event.slot}, template={event.template_id}, "
            f"title={event.title}, actors={event.actors}, location={event.location}"
        )
        print(f"    effects={event.effects.model_dump() if event.effects else None}")

    print("\n=== Final World State ===")
    print(f"day={engine.world.day}, weekday={engine.world.weekday_name}, slot={engine.world.current_slot}")

    print("\n=== Agent Summary ===")
    for agent_id, agent in engine.agents.items():
        print(
            f"{agent_id}: location={agent.current_location}, emotion={agent.emotion.label}, "
            f"top_need={max(agent.needs.model_dump().items(), key=lambda x: x[1])}, memories={len(agent.memories)}"
        )

    print("\n=== Daily Report ===")
    print(f"headline={report.headline}")
    print("top_events:")
    for item in report.top_events:
        print(f"  - {item}")
    print("relationship_changes:")
    for item in report.relationship_changes:
        print(f"  - {item}")
    print("tomorrow_hooks:")
    for item in report.tomorrow_hooks:
        print(f"  - {item}")


if __name__ == "__main__":
    main()