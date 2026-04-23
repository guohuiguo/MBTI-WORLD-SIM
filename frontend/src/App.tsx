import { useCallback, useEffect, useRef, useState } from "react";
import { fetchOverview, fetchState, resetSimulation, runDay, stepSimulation } from "./api";
import type { CharacterCard, FrontendOverview, StateResponse } from "./types";
import WorldPanel from "./components/WorldPanel";
import EventFeed from "./components/EventFeed";
import CharacterCards from "./components/CharacterCards";
import RelationshipGraph from "./components/RelationshipGraph";
import CharacterDetailModal from "./components/CharacterDetailModal";
import SceneStage from "./components/SceneStage";
import "./styles.css";

function getErrorMessage(err: unknown) {
  return err instanceof Error ? err.message : "Unknown error";
}

function normalizeOverview(raw: Partial<FrontendOverview> | null | undefined): FrontendOverview {
  return {
    world: {
      day: raw?.world?.day ?? 0,
      weekday_name: raw?.world?.weekday_name ?? "",
      day_type: raw?.world?.day_type ?? "",
      current_slot: raw?.world?.current_slot ?? "",
      weather: raw?.world?.weather ?? "",
      active_global_tags: raw?.world?.active_global_tags ?? [],
    },
    room_distribution: {
      apartment: raw?.room_distribution?.apartment ?? [],
      university: raw?.room_distribution?.university ?? [],
      amusement_park: raw?.room_distribution?.amusement_park ?? [],
    },
    focus_events: raw?.focus_events ?? [],
    event_feed: raw?.event_feed ?? [],
    character_cards: raw?.character_cards ?? [],
    relationship_graph: raw?.relationship_graph ?? [],
    latest_report: raw?.latest_report ?? null,
  };
}

export default function App() {
  const [data, setData] = useState<FrontendOverview | null>(null);
  const [stateData, setStateData] = useState<StateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);

  const [autoRunning, setAutoRunning] = useState(false);
  const [autoIntervalMs, setAutoIntervalMs] = useState(1200);

  const autoTimerRef = useRef<number | null>(null);
  const autoBusyRef = useRef(false);

  const loadOverview = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const [overview, fullState] = await Promise.all([fetchOverview(), fetchState()]);
      setData(normalizeOverview(overview));
      setStateData(fullState);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    const [overview, fullState] = await Promise.all([fetchOverview(), fetchState()]);
    setData(normalizeOverview(overview));
    setStateData(fullState);
  }, []);

  async function runAction(action: () => Promise<unknown>) {
    try {
      setLoading(true);
      setError("");
      await action();
      await refreshAll();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    return runAction(resetSimulation);
  }

  function handleStep() {
    return runAction(stepSimulation);
  }

  function handleRunDay() {
    return runAction(runDay);
  }

  function handleSelectCharacter(card: CharacterCard) {
    setSelectedCharacterId(card.id);
  }

  function stopAuto() {
    setAutoRunning(false);
    if (autoTimerRef.current !== null) {
      window.clearTimeout(autoTimerRef.current);
      autoTimerRef.current = null;
    }
    autoBusyRef.current = false;
  }

  function startAuto() {
    if (autoRunning) return;
    setAutoRunning(true);
  }

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  useEffect(() => {
    if (!autoRunning) {
      if (autoTimerRef.current !== null) {
        window.clearTimeout(autoTimerRef.current);
        autoTimerRef.current = null;
      }
      return;
    }

    const tick = async () => {
      if (autoBusyRef.current) {
        autoTimerRef.current = window.setTimeout(tick, autoIntervalMs);
        return;
      }

      autoBusyRef.current = true;

      try {
        setError("");
        await stepSimulation();
        await refreshAll();
      } catch (err) {
        setError(getErrorMessage(err));
        stopAuto();
        return;
      } finally {
        autoBusyRef.current = false;
      }

      autoTimerRef.current = window.setTimeout(tick, autoIntervalMs);
    };

    autoTimerRef.current = window.setTimeout(tick, autoIntervalMs);

    return () => {
      if (autoTimerRef.current !== null) {
        window.clearTimeout(autoTimerRef.current);
        autoTimerRef.current = null;
      }
    };
  }, [autoRunning, autoIntervalMs, refreshAll]);

  useEffect(() => {
    return () => {
      if (autoTimerRef.current !== null) {
        window.clearTimeout(autoTimerRef.current);
      }
    };
  }, []);

  if (loading && !data) {
    return <div className="page">Loading...</div>;
  }

  if (error && !data) {
    return <div className="page error">{error}</div>;
  }

  if (!data) {
    return <div className="page">No data.</div>;
  }

  return (
    <div className="page">
      <div className="toolbar">
        <h1>MBTI World Simulator</h1>
        <div className="toolbar-actions">
          <button onClick={handleReset} disabled={loading || autoRunning}>
            Reset
          </button>
          <button onClick={handleStep} disabled={loading || autoRunning}>
            Step
          </button>
          <button onClick={handleRunDay} disabled={loading || autoRunning}>
            Run Day
          </button>
          <button onClick={loadOverview} disabled={loading}>
            Refresh
          </button>

          <button
            onClick={startAuto}
            disabled={autoRunning || loading}
            className="auto-btn"
            title="Automatically step the simulation"
          >
            Auto Step
          </button>

          <button
            onClick={stopAuto}
            disabled={!autoRunning}
            className="stop-btn"
            title="Stop auto stepping"
          >
            Stop
          </button>

          <select
            value={autoIntervalMs}
            onChange={(e) => setAutoIntervalMs(Number(e.target.value))}
            disabled={autoRunning}
            className="speed-select"
            title="Auto step speed"
          >
            <option value={600}>0.6s</option>
            <option value={900}>0.9s</option>
            <option value={1200}>1.2s</option>
            <option value={1600}>1.6s</option>
            <option value={2200}>2.2s</option>
          </select>
        </div>
      </div>

      {autoRunning ? (
        <div className="auto-status-banner">
          Auto Step running · interval {autoIntervalMs} ms
        </div>
      ) : null}

      {error ? <div className="error-banner">{error}</div> : null}

      <SceneStage
        world={data.world}
        cards={data.character_cards}
        focusEvents={data.focus_events}
        onSelectCharacter={(card) => handleSelectCharacter(card)}
      />

      <div className="layout" style={{ marginTop: 16 }}>
        <div className="left-column">
          <WorldPanel world={data.world} roomDistribution={data.room_distribution} />
        </div>

        <div className="center-column">
          <EventFeed focusEvents={data.focus_events} eventFeed={data.event_feed} />
        </div>

        <div className="right-column">
          <CharacterCards
            cards={data.character_cards}
            onSelect={(card) => handleSelectCharacter(card)}
          />
          <RelationshipGraph
            edges={data.relationship_graph}
            report={data.latest_report}
          />
        </div>
      </div>

      <CharacterDetailModal
        characterId={selectedCharacterId}
        stateData={stateData}
        onClose={() => setSelectedCharacterId(null)}
      />
    </div>
  );
}