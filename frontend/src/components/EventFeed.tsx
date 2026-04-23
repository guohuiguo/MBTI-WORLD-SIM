import type { FocusEvent } from "../types";

type Props = {
  focusEvents: FocusEvent[];
  eventFeed: FocusEvent[];
};

export default function EventFeed({ focusEvents, eventFeed }: Props) {
  return (
    <div className="event-layout">
      <div className="panel">
        <h3>Focus Events</h3>
        <div className="event-list">
          {focusEvents.length === 0 ? (
            <div className="muted">No focus events yet.</div>
          ) : (
            focusEvents.map((event) => (
              <div key={event.id} className={`event-card tone-${event.tone}`}>
                <div className="event-header">
                  <strong>{event.title}</strong>
                  <span>{event.slot}</span>
                </div>
                <div>{event.description}</div>
                <div className="muted small">
                  actors: {event.actors.join(", ")} · location: {event.location}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="panel">
        <h3>Event Feed</h3>
        <div className="event-list event-feed-scroll">
          {eventFeed.length === 0 ? (
            <div className="muted">No event feed yet.</div>
          ) : (
            eventFeed.map((event) => (
              <div key={event.id} className="event-row">
                <div className="small muted">
                  [{event.slot}] {event.template_id}
                </div>
                <div>{event.description}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}