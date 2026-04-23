import type { CharacterCard } from "../types";

type Props = {
  cards: CharacterCard[];
  onSelect?: (card: CharacterCard) => void;
};

export default function CharacterCards({ cards, onSelect }: Props) {
  return (
    <div className="panel">
      <h3>Characters</h3>
      <div className="card-grid">
        {cards.map((card) => (
          <button
            key={card.id}
            type="button"
            className="character-card clickable-card"
            onClick={() => onSelect?.(card)}
          >
            <div className="character-header">
              <strong>{card.name}</strong>
              <span>{card.mbti}</span>
            </div>
            <div className="muted">{card.major}</div>
            <div>location: {card.location}</div>
            <div>emotion: {card.emotion}</div>
            <div className="small">
              top needs:{" "}
              {card.top_needs.map(([name, value]) => `${name}(${Math.round(value)})`).join(", ")}
            </div>
            <div className="small muted">memories: {card.memory_count}</div>
          </button>
        ))}
      </div>
    </div>
  );
}