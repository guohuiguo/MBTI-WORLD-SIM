import type { FrontendOverview } from "../types";

type Props = {
  world: FrontendOverview["world"];
  roomDistribution: FrontendOverview["room_distribution"];
};

function ZoneSection({
  title,
  rooms,
}: {
  title: string;
  rooms: { location: string; occupants: string[]; count: number }[];
}) {
  return (
    <div className="panel">
      <h3>{title}</h3>
      <div className="room-grid">
        {rooms.map((room) => (
          <div key={room.location} className="room-card">
            <div className="room-title">{room.location}</div>
            <div className="room-count">count: {room.count}</div>
            <div className="occupants">
              {room.occupants.length === 0 ? (
                <span className="muted">empty</span>
              ) : (
                room.occupants.map((o) => (
                  <span key={o} className="chip">
                    {o}
                  </span>
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function WorldPanel({ world, roomDistribution }: Props) {
  return (
    <div className="world-panel">
      <div className="panel top-summary">
        <h2>
          Day {world?.day ?? "-"} · {world?.weekday_name ?? "-"}
        </h2>
        <div className="summary-row">
          <span className="chip">slot: {world?.current_slot ?? "-"}</span>
          <span className="chip">weather: {world?.weather ?? "-"}</span>
          <span className="chip">type: {world?.day_type ?? "-"}</span>
          {(world?.active_global_tags ?? []).map((tag) => (
            <span key={tag} className="chip accent">
              {tag}
            </span>
          ))}
        </div>
      </div>

      <ZoneSection title="Apartment" rooms={roomDistribution.apartment ?? []} />
      <ZoneSection title="University" rooms={roomDistribution.university ?? []} />
      <ZoneSection title="Amusement Park" rooms={roomDistribution.amusement_park ?? []} />
    </div>
  );
}