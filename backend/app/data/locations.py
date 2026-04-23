APARTMENT_LOCATIONS = [
    "bedroom_ethan",
    "bedroom_leo",
    "bedroom_grace",
    "bedroom_chloe",
    "living_room",
    "kitchen",
    "gym",
    "bathroom_a",
    "bathroom_b",
]

UNIVERSITY_LOCATIONS = [
    "classroom",
    "library",
    "cafeteria",
    "campus_square",
]

AMUSEMENT_PARK_LOCATIONS = [
    "entrance",
    "rides_area",
    "arcade",
    "food_court",
]

ALL_LOCATIONS = (
    APARTMENT_LOCATIONS
    + UNIVERSITY_LOCATIONS
    + AMUSEMENT_PARK_LOCATIONS
)

APARTMENT_ZONE = set(APARTMENT_LOCATIONS)
UNIVERSITY_ZONE = set(UNIVERSITY_LOCATIONS)
AMUSEMENT_ZONE = set(AMUSEMENT_PARK_LOCATIONS)


def build_empty_occupancy() -> dict[str, list[str]]:
    return {loc: [] for loc in ALL_LOCATIONS}