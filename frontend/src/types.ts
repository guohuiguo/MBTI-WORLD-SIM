export type FocusEvent = {
  id: string;
  template_id: string;
  title: string;
  description: string;
  slot: string;
  actors: string[];
  location: string;
  tone: "positive" | "neutral" | "negative" | "mixed";
  importance: number;
  effects?: Record<string, unknown> | null;
};

export type RoomEntry = {
  location: string;
  occupants: string[];
  count: number;
};

export type CharacterCard = {
  id: string;
  name: string;
  mbti: string;
  major: string;
  location: string;
  emotion: string;
  top_needs: [string, number][];
  memory_count: number;
};

export type RelationshipEdge = {
  source: string;
  target: string;
  type: string;
  weight: number;
  details: Record<string, number>;
};

export type DailyReport = {
  day: number;
  headline: string;
  top_events: string[];
  relationship_changes: string[];
  character_highlights: Record<string, string>;
  tomorrow_hooks: string[];
};

export type FrontendOverview = {
  world: {
    day: number;
    weekday_name: string;
    day_type: string;
    current_slot: string;
    weather: string;
    active_global_tags: string[];
  };
  focus_events: FocusEvent[];
  event_feed: FocusEvent[];
  room_distribution: {
    apartment: RoomEntry[];
    university: RoomEntry[];
    amusement_park: RoomEntry[];
  };
  character_cards: CharacterCard[];
  relationship_graph: RelationshipEdge[];
  latest_report: DailyReport | null;
};

export type NeedState = {
  rest: number;
  social: number;
  achievement: number;
  novelty: number;
  order: number;
  autonomy: number;
  belonging: number;
};

export type EmotionState = {
  label: string;
  intensity: number;
  valence: number;
  arousal: number;
};

export type MemoryItem = {
  day: number;
  summary: string;
  related_characters: string[];
  location: string;
  importance: number;
  sentiment: number;
};

export type PersonalityState = {
  sociability: number;
  spontaneity: number;
  orderliness: number;
  empathy: number;
  competitiveness: number;
  curiosity: number;
  sensitivity: number;
  planning: number;
  impulsiveness: number;
};

export type AgentFullState = {
  id: string;
  name: string;
  mbti: string;
  age: number;
  gender: string;
  major: string;
  current_location: string;
  personality: PersonalityState;
  needs: NeedState;
  emotion: EmotionState;
  memories: MemoryItem[];
  short_term_goal?: string | null;
};

export type RelationshipState = {
  closeness: number;
  trust: number;
  tension: number;
  respect: number;
};

export type StateResponse = {
  world: {
    day: number;
    weekday_name: string;
    day_type: string;
    current_slot: string;
    weather: string;
    active_global_tags: string[];
    occupancy?: Record<string, string[]>;
  };
  agents: Record<string, AgentFullState>;
  relationships: Record<string, Record<string, RelationshipState>>;
  today_events: FocusEvent[];
};