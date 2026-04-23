import type { DailyReport, RelationshipEdge } from "../types";

type Props = {
  edges: RelationshipEdge[];
  report: DailyReport | null;
};

export default function RelationshipGraph({ edges, report }: Props) {
  return (
    <div className="panel">
      <h3>Relationship Graph</h3>
      <div className="relation-list">
        {edges.length === 0 ? (
          <div className="muted">No strong relationship edges yet.</div>
        ) : (
          edges.map((edge) => (
            <div key={`${edge.source}-${edge.target}`} className="relation-row">
              <strong>
                {edge.source} ↔ {edge.target}
              </strong>
              <span className={`relation-type relation-${edge.type}`}>{edge.type}</span>
              <span>weight: {edge.weight}</span>
            </div>
          ))
        )}
      </div>

      <h3 style={{ marginTop: 20 }}>Latest Report</h3>
      {report ? (
        <div className="report-block">
          <div className="report-headline">{report.headline}</div>
          <div className="report-section">
            <strong>Top Events</strong>
            <ul>
              {report.top_events.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          </div>
          <div className="report-section">
            <strong>Tomorrow Hooks</strong>
            <ul>
              {report.tomorrow_hooks.map((e) => (
                <li key={e}>{e}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <div className="muted">No report yet.</div>
      )}
    </div>
  );
}