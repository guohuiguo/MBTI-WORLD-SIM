import { createPortal } from "react-dom";
import type { StateResponse } from "../types";

type Props = {
  characterId: string | null;
  stateData: StateResponse | null;
  onClose: () => void;
};

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)));
}

function emotionTone(label: string) {
  switch (label) {
    case "happy":
    case "satisfied":
    case "calm":
      return "emotion-good";
    case "excited":
      return "emotion-bright";
    case "stressed":
    case "annoyed":
      return "emotion-bad";
    case "sad":
    case "lonely":
      return "emotion-soft";
    default:
      return "emotion-neutral";
  }
}

function relationSummary(rel: {
  closeness: number;
  trust: number;
  tension: number;
  respect: number;
}) {
  const candidates = [
    { key: "closeness", value: rel.closeness, label: "close" },
    { key: "trust", value: rel.trust, label: "trust" },
    { key: "tension", value: rel.tension, label: "tense" },
    { key: "respect", value: rel.respect, label: "respect" },
  ].sort((a, b) => Math.abs(b.value) - Math.abs(a.value));

  return candidates[0];
}

function prettyNeedName(key: string) {
  return key.charAt(0).toUpperCase() + key.slice(1);
}

function getAvatarTheme(id: string) {
  switch (id) {
    case "ethan":
      return "avatar-ethan";
    case "leo":
      return "avatar-leo";
    case "grace":
      return "avatar-grace";
    case "chloe":
      return "avatar-chloe";
    default:
      return "avatar-default";
  }
}

export default function CharacterDetailModal({ characterId, stateData, onClose }: Props) {
  if (!characterId || !stateData) return null;

  const agent = stateData.agents[characterId];
  const relMap = stateData.relationships[characterId];

  if (!agent || !relMap) return null;

  const relationRows = Object.entries(relMap)
    .filter(([otherId]) => otherId !== characterId)
    .map(([otherId, rel]) => ({
      otherId,
      otherName: stateData.agents[otherId]?.name ?? otherId,
      rel,
      summary: relationSummary(rel),
    }))
    .sort((a, b) => Math.abs(b.summary.value) - Math.abs(a.summary.value));

  const needEntries = Object.entries(agent.needs).sort((a, b) => b[1] - a[1]);
  const recentMemories = [...agent.memories]
    .sort((a, b) => b.day - a.day || b.importance - a.importance)
    .slice(0, 6);

  const modalNode = (
    <div className="modal-overlay top-layer-modal" onClick={onClose}>
      <div className="modal-card detail-modal v2 top-layer-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header modal-header-v2">
          <div className="character-hero">
            <div className={`character-hero-avatar ${getAvatarTheme(agent.id)}`}>
              {agent.name.slice(0, 1)}
            </div>

            <div className="character-hero-text">
              <h2>
                {agent.name} · {agent.mbti}
              </h2>
              <div className="muted">
                {agent.major} · {agent.current_location}
              </div>

              <div className="hero-tags">
                <span className="hero-tag">{agent.gender}</span>
                <span className="hero-tag">age {agent.age}</span>
                <span className={`hero-tag ${emotionTone(agent.emotion.label)}`}>
                  {agent.emotion.label}
                </span>
              </div>
            </div>
          </div>

          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="detail-grid">
          <div className="detail-column">
            <div className="modal-section">
              <strong>Current Emotion</strong>
              <div className={`emotion-pill ${emotionTone(agent.emotion.label)}`}>
                {agent.emotion.label}
              </div>
              <div className="detail-mini-stats">
                <span>intensity: {agent.emotion.intensity.toFixed(2)}</span>
                <span>valence: {agent.emotion.valence.toFixed(2)}</span>
                <span>arousal: {agent.emotion.arousal.toFixed(2)}</span>
              </div>
            </div>

            <div className="modal-section">
              <strong>Needs</strong>
              <div className="needs-list">
                {needEntries.map(([key, value]) => (
                  <div key={key} className="need-row">
                    <div className="need-row-top">
                      <span>{prettyNeedName(key)}</span>
                      <span>{Math.round(value)}</span>
                    </div>
                    <div className="need-bar">
                      <div
                        className="need-bar-fill"
                        style={{ width: `${clampPercent(value)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="modal-section">
              <strong>Short-term Goal</strong>
              <div className="muted">
                {agent.short_term_goal ? agent.short_term_goal : "No explicit short-term goal."}
              </div>
            </div>
          </div>

          <div className="detail-column">
            <div className="modal-section">
              <strong>Recent Memories</strong>
              {recentMemories.length === 0 ? (
                <div className="muted">No memories yet.</div>
              ) : (
                <div className="memory-list">
                  {recentMemories.map((memory, index) => (
                    <div key={`${memory.day}-${index}`} className="memory-card">
                      <div className="memory-meta">
                        <span>Day {memory.day}</span>
                        <span>{memory.location}</span>
                      </div>
                      <div className="memory-summary">{memory.summary}</div>
                      <div className="memory-sub muted">
                        importance {memory.importance.toFixed(2)} · sentiment {memory.sentiment.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="modal-section">
              <strong>Relationships</strong>
              <div className="relationship-detail-list">
                {relationRows.map((row) => (
                  <div key={row.otherId} className="relationship-detail-card">
                    <div className="relationship-detail-top">
                      <strong>{row.otherName}</strong>
                      <span className={`relation-badge relation-${row.summary.label}`}>
                        {row.summary.label}
                      </span>
                    </div>
                    <div className="relationship-metrics">
                      <span>closeness: {row.rel.closeness}</span>
                      <span>trust: {row.rel.trust}</span>
                      <span>tension: {row.rel.tension}</span>
                      <span>respect: {row.rel.respect}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return createPortal(modalNode, document.body);
}