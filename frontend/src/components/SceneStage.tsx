import { useEffect, useMemo, useRef, useState } from "react";
import type { CharacterCard, FocusEvent, FrontendOverview } from "../types";

type SceneKey = "apartment" | "university" | "amusement_park";

type Props = {
  world: FrontendOverview["world"];
  cards: CharacterCard[];
  focusEvents: FocusEvent[];
  onSelectCharacter?: (card: CharacterCard) => void;
};

type Opening = {
  side: "top" | "right" | "bottom" | "left";
  offset: number;
  size?: number;
};

type FurnitureItem = {
  icon: string;
  label?: string;
  left: number;
  top: number;
  size?: "sm" | "md" | "lg";
};

type RoomConfig = {
  key: string;
  label: string;
  left: number;
  top: number;
  width: number;
  height: number;
  furniture?: FurnitureItem[];
  doors?: Opening[];
  windows?: Opening[];
};

type Position = {
  left: number;
  top: number;
};

const SCENE_NAMES: Record<SceneKey, string> = {
  apartment: "Apartment",
  university: "University",
  amusement_park: "Amusement Park",
};

const APARTMENT_SHELL = {
  left: 3,
  top: 8,
  width: 94,
  height: 82,
};

const APARTMENT_CORRIDOR_Y = APARTMENT_SHELL.top + APARTMENT_SHELL.height * 0.35;
const STORAGE_KEY = "mbti_world_sim_selected_scene";

function readInitialScene(): SceneKey {
  if (typeof window === "undefined") return "apartment";
  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === "apartment" || saved === "university" || saved === "amusement_park") {
    return saved;
  }
  return "apartment";
}

const APARTMENT_ROOMS: RoomConfig[] = [
  {
    key: "bedroom_ethan",
    label: "Ethan Room",
    left: 2,
    top: 4,
    width: 22,
    height: 28,
    windows: [{ side: "top", offset: 14, size: 22 }],
    doors: [{ side: "bottom", offset: 48, size: 14 }],
    furniture: [
      { icon: "🛏️", left: 14, top: 26, size: "lg" },
      { icon: "💻", left: 75, top: 24, size: "md" },
      { icon: "📚", left: 76, top: 44, size: "sm" },
      { icon: "♟️", left: 76, top: 62, size: "sm" },
      { icon: "🪟", left: 16, top: 8, size: "sm" },
    ],
  },
  {
    key: "bedroom_leo",
    label: "Leo Room",
    left: 25,
    top: 4,
    width: 22,
    height: 28,
    windows: [{ side: "top", offset: 48, size: 22 }],
    doors: [{ side: "bottom", offset: 48, size: 14 }],
    furniture: [
      { icon: "🛏️", left: 14, top: 26, size: "lg" },
      { icon: "📷", left: 77, top: 26, size: "md" },
      { icon: "🎧", left: 76, top: 46, size: "sm" },
      { icon: "🎨", left: 76, top: 62, size: "sm" },
      { icon: "🪟", left: 44, top: 8, size: "sm" },
    ],
  },
  {
    key: "bedroom_grace",
    label: "Grace Room",
    left: 48,
    top: 4,
    width: 22,
    height: 28,
    windows: [{ side: "top", offset: 46, size: 22 }],
    doors: [{ side: "bottom", offset: 48, size: 14 }],
    furniture: [
      { icon: "🛏️", left: 14, top: 26, size: "lg" },
      { icon: "🩺", left: 76, top: 26, size: "sm" },
      { icon: "🪴", left: 75, top: 45, size: "sm" },
      { icon: "🧸", left: 76, top: 62, size: "sm" },
      { icon: "🪟", left: 44, top: 8, size: "sm" },
    ],
  },
  {
    key: "bedroom_chloe",
    label: "Chloe Room",
    left: 71,
    top: 4,
    width: 27,
    height: 28,
    windows: [{ side: "top", offset: 38, size: 24 }],
    doors: [{ side: "bottom", offset: 40, size: 14 }],
    furniture: [
      { icon: "🛏️", left: 14, top: 26, size: "lg" },
      { icon: "🏋️", left: 77, top: 26, size: "sm" },
      { icon: "👟", left: 76, top: 46, size: "sm" },
      { icon: "🥇", left: 77, top: 62, size: "sm" },
      { icon: "🪟", left: 38, top: 8, size: "sm" },
    ],
  },
  {
    key: "living_room",
    label: "Living Room",
    left: 2,
    top: 37,
    width: 33,
    height: 27,
    windows: [{ side: "left", offset: 40, size: 18 }],
    doors: [{ side: "top", offset: 46, size: 14 }],
    furniture: [
      { icon: "🛋️", left: 16, top: 30, size: "lg" },
      { icon: "📺", left: 73, top: 26, size: "lg" },
      { icon: "🪴", left: 10, top: 68, size: "sm" },
      { icon: "🎮", left: 44, top: 72, size: "sm" },
      { icon: "☕", left: 28, top: 64, size: "md" },
    ],
  },
  {
    key: "kitchen",
    label: "Kitchen",
    left: 38,
    top: 37,
    width: 21,
    height: 27,
    windows: [{ side: "bottom", offset: 56, size: 18 }],
    doors: [{ side: "top", offset: 46, size: 14 }],
    furniture: [
      { icon: "🍳", left: 14, top: 24, size: "md" },
      { icon: "🧊", left: 77, top: 24, size: "md" },
      { icon: "🪑", left: 48, top: 63, size: "sm" },
      { icon: "🍽️", left: 34, top: 58, size: "md" },
      { icon: "☕", left: 12, top: 64, size: "sm" },
    ],
  },
  {
    key: "gym",
    label: "Gym",
    left: 61,
    top: 37,
    width: 19,
    height: 27,
    windows: [{ side: "bottom", offset: 40, size: 18 }],
    doors: [{ side: "top", offset: 46, size: 14 }],
    furniture: [
      { icon: "🏃", left: 18, top: 24, size: "md" },
      { icon: "🏋️", left: 68, top: 28, size: "md" },
      { icon: "🧘", left: 44, top: 64, size: "sm" },
      { icon: "💧", left: 72, top: 64, size: "sm" },
    ],
  },
  {
    key: "bathroom_a",
    label: "Bath A",
    left: 82,
    top: 37,
    width: 16,
    height: 11.5,
    doors: [{ side: "left", offset: 52, size: 12 }],
    furniture: [
      { icon: "🚿", left: 18, top: 34, size: "sm" },
      { icon: "🪥", left: 74, top: 34, size: "sm" },
      { icon: "🪞", left: 48, top: 70, size: "sm" },
    ],
  },
  {
    key: "bathroom_b",
    label: "Bath B",
    left: 82,
    top: 52.5,
    width: 16,
    height: 11.5,
    doors: [{ side: "left", offset: 52, size: 12 }],
    furniture: [
      { icon: "🛁", left: 22, top: 34, size: "sm" },
      { icon: "🧼", left: 74, top: 34, size: "sm" },
      { icon: "🪞", left: 48, top: 70, size: "sm" },
    ],
  },
];

const UNIVERSITY_ROOMS: RoomConfig[] = [
  {
    key: "classroom",
    label: "Classroom",
    left: 7,
    top: 14,
    width: 28,
    height: 26,
    furniture: [
      { icon: "🧑‍🏫", left: 12, top: 24, size: "md" },
      { icon: "📋", left: 22, top: 24, size: "sm" },
      { icon: "🪑", left: 78, top: 68, size: "sm" },
      { icon: "📝", left: 86, top: 68, size: "sm" },
    ],
  },
  {
    key: "library",
    label: "Library",
    left: 39,
    top: 12,
    width: 24,
    height: 28,
    furniture: [
      { icon: "📚", left: 14, top: 24, size: "md" },
      { icon: "🖥️", left: 78, top: 24, size: "sm" },
      { icon: "💡", left: 78, top: 68, size: "sm" },
      { icon: "🪑", left: 86, top: 68, size: "sm" },
    ],
  },
  {
    key: "cafeteria",
    label: "Cafeteria",
    left: 67,
    top: 16,
    width: 21,
    height: 23,
    furniture: [
      { icon: "🍱", left: 76, top: 70, size: "sm" },
      { icon: "🥤", left: 84, top: 70, size: "sm" },
      { icon: "🪑", left: 92, top: 70, size: "sm" },
    ],
  },
  {
    key: "campus_square",
    label: "Campus Square",
    left: 16,
    top: 51,
    width: 62,
    height: 18,
    furniture: [
      { icon: "🌳", left: 8, top: 30, size: "md" },
      { icon: "🌳", left: 92, top: 32, size: "md" },
      { icon: "🪑", left: 18, top: 70, size: "sm" },
      { icon: "🪑", left: 82, top: 70, size: "sm" },
    ],
  },
];

const PARK_ROOMS: RoomConfig[] = [
  {
    key: "entrance",
    label: "Entrance",
    left: 6,
    top: 18,
    width: 18,
    height: 18,
    furniture: [
      { icon: "🎟️", left: 80, top: 74, size: "sm" },
      { icon: "🗺️", left: 88, top: 74, size: "sm" },
    ],
  },
  {
    key: "rides_area",
    label: "Rides Area",
    left: 28,
    top: 10,
    width: 32,
    height: 30,
    furniture: [
      { icon: "🎡", left: 14, top: 22, size: "md" },
      { icon: "🎢", left: 24, top: 22, size: "md" },
      { icon: "🎠", left: 88, top: 78, size: "sm" },
    ],
  },
  {
    key: "arcade",
    label: "Arcade",
    left: 66,
    top: 18,
    width: 18,
    height: 18,
    furniture: [
      { icon: "🕹️", left: 80, top: 74, size: "sm" },
      { icon: "🎮", left: 88, top: 74, size: "sm" },
    ],
  },
  {
    key: "food_court",
    label: "Food Court",
    left: 18,
    top: 50,
    width: 58,
    height: 18,
    furniture: [
      { icon: "🍟", left: 84, top: 74, size: "sm" },
      { icon: "🍔", left: 90, top: 74, size: "sm" },
      { icon: "🥤", left: 96, top: 74, size: "sm" },
    ],
  },
];

function getRoomsByScene(scene: SceneKey): RoomConfig[] {
  if (scene === "apartment") return APARTMENT_ROOMS;
  if (scene === "university") return UNIVERSITY_ROOMS;
  return PARK_ROOMS;
}

function detectSceneByLocation(location: string): SceneKey {
  if (
    [
      "bedroom_ethan",
      "bedroom_leo",
      "bedroom_grace",
      "bedroom_chloe",
      "living_room",
      "kitchen",
      "gym",
      "bathroom_a",
      "bathroom_b",
    ].includes(location)
  ) {
    return "apartment";
  }

  if (["classroom", "library", "cafeteria", "campus_square"].includes(location)) {
    return "university";
  }

  return "amusement_park";
}

function getCharacterTheme(id: string) {
  switch (id) {
    case "ethan":
      return "theme-ethan";
    case "leo":
      return "theme-leo";
    case "grace":
      return "theme-grace";
    case "chloe":
      return "theme-chloe";
    default:
      return "theme-default";
  }
}

function getEmotionEmoji(emotion: string) {
  switch (emotion) {
    case "happy":
      return "😊";
    case "excited":
      return "⚡";
    case "stressed":
      return "💢";
    case "annoyed":
      return "😒";
    case "lonely":
      return "🥲";
    case "sad":
      return "☁️";
    case "satisfied":
      return "✨";
    case "calm":
      return "🌿";
    default:
      return "🙂";
  }
}

function fallbackEmotionLine(emotion: string) {
  switch (emotion) {
    case "happy":
      return "Feeling good!";
    case "excited":
      return "Let's go!";
    case "stressed":
      return "Too much...";
    case "annoyed":
      return "Seriously?";
    case "lonely":
      return "Anyone around?";
    case "sad":
      return "Need a quiet moment.";
    case "calm":
      return "Everything is okay.";
    case "satisfied":
      return "Nice.";
    default:
      return "Just chilling.";
  }
}

function toCuteBubble(event: FocusEvent, actorId: string) {
  const t = event.template_id;
  const title = (event.title || "").toLowerCase();

  if (t === "GEN_HELP") {
    return event.actors[0] === actorId ? "I can help!" : "Thanks for that.";
  }
  if (t === "GEN_TALK" || t === "SINGLE_TALK") return "Let's talk!";
  if (t === "INVITE_DECLINED") return "Not today...";
  if (t === "SINGLE_REST") return "Recharge time.";
  if (t === "SINGLE_WORKOUT") return "Gym mode!";
  if (t === "SINGLE_WATCH_MOVIE") return "Movie break!";
  if (t === "SINGLE_PLAY") return "This is fun.";
  if (t === "SINGLE_CLEAN") return "Need to tidy up.";

  if (title.includes("help")) return "Need a hand?";
  if (title.includes("talk")) return "Got a minute?";
  if (title.includes("stress")) return "Deep breath.";
  if (title.includes("rain")) return "Hmm...";
  if (title.includes("work")) return "Let's do this.";

  const text = event.title || event.description || "Something happened.";
  return text.length > 24 ? `${text.slice(0, 24)}...` : text;
}

function buildBubbleMap(cards: CharacterCard[], focusEvents: FocusEvent[]) {
  const map: Record<string, string> = {};

  for (const event of focusEvents) {
    for (const actorId of event.actors) {
      if (!map[actorId]) {
        map[actorId] = toCuteBubble(event, actorId);
      }
    }
  }

  for (const card of cards) {
    if (!map[card.id]) {
      map[card.id] = fallbackEmotionLine(card.emotion);
    }
  }

  return map;
}

function buildFocusActorSet(focusEvents: FocusEvent[]) {
  const set = new Set<string>();
  for (const event of focusEvents) {
    for (const actor of event.actors) set.add(actor);
  }
  return set;
}

function buildFocusRoomSet(focusEvents: FocusEvent[]) {
  const set = new Set<string>();
  for (const event of focusEvents) {
    if (event.location) set.add(event.location);
  }
  return set;
}

function toAbsoluteRoomRect(scene: SceneKey, room: RoomConfig) {
  if (scene === "apartment") {
    return {
      left: APARTMENT_SHELL.left + (APARTMENT_SHELL.width * room.left) / 100,
      top: APARTMENT_SHELL.top + (APARTMENT_SHELL.height * room.top) / 100,
      width: (APARTMENT_SHELL.width * room.width) / 100,
      height: (APARTMENT_SHELL.height * room.height) / 100,
    };
  }

  return {
    left: room.left,
    top: room.top,
    width: room.width,
    height: room.height,
  };
}

function getRoomMap(scene: SceneKey) {
  const map: Record<string, RoomConfig> = {};
  for (const room of getRoomsByScene(scene)) {
    map[room.key] = room;
  }
  return map;
}

function computeCharacterTargets(scene: SceneKey, visibleCards: CharacterCard[]) {
  const roomMap = getRoomMap(scene);
  const grouped: Record<string, CharacterCard[]> = {};

  for (const card of visibleCards) {
    if (!grouped[card.location]) grouped[card.location] = [];
    grouped[card.location].push(card);
  }

  const positions: Record<string, Position> = {};

  for (const [roomKey, roomCards] of Object.entries(grouped)) {
    const room = roomMap[roomKey];
    if (!room) continue;

    const rect = toAbsoluteRoomRect(scene, room);

    const anchors = [
      { x: 0.22, y: 0.52 },
      { x: 0.52, y: 0.58 },
      { x: 0.34, y: 0.76 },
      { x: 0.68, y: 0.74 },
    ];

    roomCards.forEach((card, index) => {
      const anchor = anchors[index % anchors.length];
      positions[card.id] = {
        left: rect.left + rect.width * anchor.x,
        top: rect.top + rect.height * anchor.y,
      };
    });
  }

  return positions;
}

function getDoorAnchor(scene: SceneKey, roomKey: string): Position | null {
  const roomMap = getRoomMap(scene);
  const room = roomMap[roomKey];
  if (!room) return null;

  const rect = toAbsoluteRoomRect(scene, room);
  const opening = room.doors?.[0];
  if (!opening) {
    return {
      left: rect.left + rect.width * 0.5,
      top: rect.top + rect.height * 0.9,
    };
  }

  if (opening.side === "top") {
    return {
      left: rect.left + rect.width * (opening.offset / 100),
      top: rect.top,
    };
  }

  if (opening.side === "bottom") {
    return {
      left: rect.left + rect.width * (opening.offset / 100),
      top: rect.top + rect.height,
    };
  }

  if (opening.side === "left") {
    return {
      left: rect.left,
      top: rect.top + rect.height * (opening.offset / 100),
    };
  }

  return {
    left: rect.left + rect.width,
    top: rect.top + rect.height * (opening.offset / 100),
  };
}

function renderOpeningStyle(opening: Opening) {
  const size = opening.size ?? 16;

  if (opening.side === "top" || opening.side === "bottom") {
    return {
      left: `${opening.offset}%`,
      width: `${size}%`,
      height: "8px",
      transform: "translateX(-50%)",
      top: opening.side === "top" ? "-4px" : undefined,
      bottom: opening.side === "bottom" ? "-4px" : undefined,
    };
  }

  return {
    top: `${opening.offset}%`,
    height: `${size}%`,
    width: "8px",
    transform: "translateY(-50%)",
    left: opening.side === "left" ? "-4px" : undefined,
    right: opening.side === "right" ? "-4px" : undefined,
  };
}

function WeatherOverlay({ weather }: { weather: string }) {
  if (weather === "rainy") {
    return (
      <div className="weather-overlay rainy">
        {Array.from({ length: 18 }).map((_, i) => (
          <span key={i} className="rain-drop" />
        ))}
      </div>
    );
  }

  if (weather === "cloudy") {
    return (
      <div className="weather-overlay cloudy">
        <span className="cloud cloud-1" />
        <span className="cloud cloud-2" />
        <span className="cloud cloud-3" />
      </div>
    );
  }

  return (
    <div className="weather-overlay sunny">
      <span className="sun" />
    </div>
  );
}

function UniversityBackdrop() {
  return (
    <div className="university-backdrop">
      <div className="uni-building-strip" />
      <div className="uni-path uni-path-1" />
      <div className="uni-tree uni-tree-1">🌳</div>
      <div className="uni-tree uni-tree-2">🌳</div>
      <div className="uni-tree uni-tree-3">🌳</div>
    </div>
  );
}

function ParkBackdrop() {
  return (
    <div className="park-backdrop">
      <div className="park-wheel">🎡</div>
      <div className="park-banner park-banner-1" />
      <div className="park-banner park-banner-2" />
      <div className="park-path" />
    </div>
  );
}

function ApartmentFloor({ focusRooms }: { focusRooms: Set<string> }) {
  return (
    <div className="apartment-shell-v5">
      <div className="apartment-top-label">Shared Apartment</div>
      <div className="apartment-corridor" />
      <div className="apartment-wall-line apartment-wall-line-1" />
      <div className="apartment-wall-line apartment-wall-line-2" />
      <div className="apartment-wall-line apartment-wall-line-3" />

      {APARTMENT_ROOMS.map((room) => (
        <div
          key={room.key}
          className={`apartment-room-v5 room-${room.key} ${focusRooms.has(room.key) ? "focused-room" : ""}`}
          style={{
            left: `${room.left}%`,
            top: `${room.top}%`,
            width: `${room.width}%`,
            height: `${room.height}%`,
          }}
        >
          <div className="room-title-bar">
            <span>{room.label}</span>
          </div>

          <div className="room-floor-pattern" />

          {(room.windows ?? []).map((opening, index) => (
            <span
              key={`window-${room.key}-${index}`}
              className={`room-window room-window-${opening.side}`}
              style={renderOpeningStyle(opening)}
            />
          ))}

          {(room.doors ?? []).map((opening, index) => (
            <span
              key={`door-${room.key}-${index}`}
              className={`room-door room-door-${opening.side}`}
              style={renderOpeningStyle(opening)}
            />
          ))}

          <div className="furniture-layer">
            {(room.furniture ?? []).map((item, index) => (
              <div
                key={`${room.key}-furniture-${index}`}
                className={`furniture-item furniture-${item.size ?? "md"}`}
                style={{
                  left: `${item.left}%`,
                  top: `${item.top}%`,
                }}
                title={item.label ?? ""}
              >
                {item.icon}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function GenericScene({
  scene,
  focusRooms,
}: {
  scene: Exclude<SceneKey, "apartment">;
  focusRooms: Set<string>;
}) {
  const rooms = getRoomsByScene(scene);

  return (
    <>
      {scene === "university" ? <UniversityBackdrop /> : <ParkBackdrop />}

      {rooms.map((room) => (
        <div
          key={room.key}
          className={`generic-room-v5 room-${room.key} ${focusRooms.has(room.key) ? "focused-room" : ""}`}
          style={{
            left: `${room.left}%`,
            top: `${room.top}%`,
            width: `${room.width}%`,
            height: `${room.height}%`,
          }}
        >
          <div className="room-title-bar">
            <span>{room.label}</span>
          </div>

          <div className="furniture-layer">
            {(room.furniture ?? []).map((item, index) => (
              <div
                key={`${room.key}-furniture-${index}`}
                className={`furniture-item furniture-${item.size ?? "md"}`}
                style={{
                  left: `${item.left}%`,
                  top: `${item.top}%`,
                }}
                title={item.label ?? ""}
              >
                {item.icon}
              </div>
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

export default function SceneStage({
  world,
  cards,
  focusEvents,
  onSelectCharacter,
}: Props) {
  const [scene, setScene] = useState<SceneKey>(readInitialScene);
  const [displayPositions, setDisplayPositions] = useState<Record<string, Position>>({});
  const prevLocationsRef = useRef<Record<string, string>>({});
  const timersRef = useRef<number[]>([]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, scene);
    }
  }, [scene]);

  useEffect(() => {
    return () => {
      timersRef.current.forEach((t) => window.clearTimeout(t));
      timersRef.current = [];
    };
  }, []);

  const visibleCards = useMemo(
    () => cards.filter((card) => detectSceneByLocation(card.location) === scene),
    [cards, scene]
  );

  const bubbleMap = useMemo(() => buildBubbleMap(cards, focusEvents), [cards, focusEvents]);
  const focusActors = useMemo(() => buildFocusActorSet(focusEvents), [focusEvents]);
  const focusRooms = useMemo(() => buildFocusRoomSet(focusEvents), [focusEvents]);
  const targetPositions = useMemo(
    () => computeCharacterTargets(scene, visibleCards),
    [scene, visibleCards]
  );

  useEffect(() => {
    timersRef.current.forEach((t) => window.clearTimeout(t));
    timersRef.current = [];

    const prevLocations = prevLocationsRef.current;
    const visibleIds = new Set(visibleCards.map((c) => c.id));

    setDisplayPositions((prev) => {
      const next: Record<string, Position> = {};
      for (const id of visibleIds) {
        next[id] = prev[id] ?? targetPositions[id];
      }
      return next;
    });

    for (const card of visibleCards) {
      const id = card.id;
      const nextLoc = card.location;
      const prevLoc = prevLocations[id];
      const target = targetPositions[id];

      if (!target) continue;

      if (!prevLoc || prevLoc === nextLoc || detectSceneByLocation(prevLoc) !== scene) {
        const t = window.setTimeout(() => {
          setDisplayPositions((prev) => ({ ...prev, [id]: target }));
        }, 30);
        timersRef.current.push(t);
        continue;
      }

      if (scene === "apartment") {
        const fromDoor = getDoorAnchor(scene, prevLoc);
        const toDoor = getDoorAnchor(scene, nextLoc);

        if (fromDoor && toDoor) {
          const mid1 = { left: fromDoor.left, top: APARTMENT_CORRIDOR_Y };
          const mid2 = { left: toDoor.left, top: APARTMENT_CORRIDOR_Y };

          setDisplayPositions((prev) => ({
            ...prev,
            [id]: prev[id] ?? {
              left: fromDoor.left,
              top: fromDoor.top,
            },
          }));

          const t1 = window.setTimeout(() => {
            setDisplayPositions((prev) => ({ ...prev, [id]: mid1 }));
          }, 40);

          const t2 = window.setTimeout(() => {
            setDisplayPositions((prev) => ({ ...prev, [id]: mid2 }));
          }, 220);

          const t3 = window.setTimeout(() => {
            setDisplayPositions((prev) => ({ ...prev, [id]: target }));
          }, 430);

          timersRef.current.push(t1, t2, t3);
          continue;
        }
      }

      const t = window.setTimeout(() => {
        setDisplayPositions((prev) => ({ ...prev, [id]: target }));
      }, 40);
      timersRef.current.push(t);
    }

    prevLocationsRef.current = Object.fromEntries(cards.map((c) => [c.id, c.location]));
  }, [scene, cards, visibleCards, targetPositions]);

  return (
    <div className="panel scene-panel v5">
      <div className="scene-header">
        <div>
          <h2>World Stage</h2>
          <div className="muted">
            Day {world.day} · {world.weekday_name} · {world.current_slot} · {world.weather}
          </div>
        </div>

        <div className="scene-tabs">
          {(Object.keys(SCENE_NAMES) as SceneKey[]).map((key) => (
            <button
              key={key}
              className={scene === key ? "scene-tab active" : "scene-tab"}
              onClick={() => setScene(key)}
              type="button"
            >
              {SCENE_NAMES[key]}
            </button>
          ))}
        </div>
      </div>

      <div className={`scene-canvas v5 scene-${scene}`}>
        <WeatherOverlay weather={world.weather} />

        <div className="scene-map-layer">
          {scene === "apartment" ? (
            <ApartmentFloor focusRooms={focusRooms} />
          ) : (
            <GenericScene
              scene={scene as Exclude<SceneKey, "apartment">}
              focusRooms={focusRooms}
            />
          )}
        </div>

        <div className="scene-character-layer">
          {visibleCards.map((card) => {
            const pos = displayPositions[card.id] ?? targetPositions[card.id] ?? { left: 50, top: 50 };
            const isFocused = focusActors.has(card.id);

            return (
              <button
                key={card.id}
                type="button"
                className={`scene-character-v5 ${getCharacterTheme(card.id)} ${isFocused ? "focused" : ""}`}
                style={{
                  left: `${pos.left}%`,
                  top: `${pos.top}%`,
                }}
                onClick={() => onSelectCharacter?.(card)}
              >
                <div className="speech-bubble v5">{bubbleMap[card.id]}</div>

                <div className="character-shadow" />
                <div className="character-stand">
                  <div className="avatar-head">{card.name.slice(0, 1)}</div>
                  <div className="avatar-body" />
                  <div className="avatar-emotion">{getEmotionEmoji(card.emotion)}</div>
                </div>

                <div className="character-nameplate-v5">
                  <span>{card.name.split(" ")[0]}</span>
                  <span className="character-nameplate-sub">{card.mbti}</span>
                </div>
              </button>
            );
          })}
        </div>

        <div className="scene-footer">
          <div className="scene-footer-pill">Scene: {SCENE_NAMES[scene]}</div>
          <div className="scene-footer-pill">Active characters: {visibleCards.length}</div>
          <div className="scene-footer-pill">Focus events: {focusEvents.length}</div>
        </div>
      </div>
    </div>
  );
}