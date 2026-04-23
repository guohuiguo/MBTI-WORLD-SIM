from app.models.event_models import EventTemplate


EVENT_TEMPLATES = [
    EventTemplate(id="A1", title="Bathroom Queue Conflict", category="apartment", location_tags=["bathroom_a", "bathroom_b"], time_slots=["morning"], tone="negative", base_importance=0.70, tags=["conflict", "schedule"]),
    EventTemplate(id="A2", title="Kitchen Breakfast Chat", category="apartment", location_tags=["kitchen"], time_slots=["morning"], tone="positive", base_importance=0.45, tags=["chat", "routine"]),
    EventTemplate(id="A3", title="Noise Complaint", category="apartment", location_tags=["living_room", "gym"], time_slots=["late_evening", "night"], tone="negative", base_importance=0.75, tags=["conflict", "noise"]),
    EventTemplate(id="A4", title="Shared Cooking Invitation", category="apartment", location_tags=["kitchen"], time_slots=["evening"], tone="positive", base_importance=0.55, tags=["bonding", "food"]),
    EventTemplate(id="A5", title="Fridge Food Mix-up", category="apartment", location_tags=["kitchen"], time_slots=["evening"], tone="mixed", base_importance=0.65, tags=["misunderstanding"]),
    EventTemplate(id="A6", title="Living Room Movie Proposal", category="apartment", location_tags=["living_room"], time_slots=["evening", "late_evening"], tone="positive", base_importance=0.55, tags=["group", "fun"]),
    EventTemplate(id="A7", title="Apartment Cleaning Debate", category="apartment", location_tags=["living_room", "kitchen"], time_slots=["afternoon", "evening"], tone="mixed", base_importance=0.70, tags=["chores", "conflict"]),
    EventTemplate(id="A8", title="Home Gym Challenge", category="apartment", location_tags=["gym"], time_slots=["evening"], tone="mixed", base_importance=0.55, tags=["competition"]),
    EventTemplate(id="A9", title="Late-night Emotional Talk", category="apartment", location_tags=["living_room", "kitchen"], time_slots=["late_evening", "night"], tone="positive", base_importance=0.80, tags=["deep_talk"]),
    EventTemplate(id="A10", title="Borrowed Item Not Returned", category="apartment", location_tags=["living_room", "bedroom_ethan", "bedroom_leo", "bedroom_grace", "bedroom_chloe"], time_slots=["evening"], tone="negative", base_importance=0.68, tags=["trust", "conflict"]),

    EventTemplate(id="U1", title="Walking to Class Together", category="university", location_tags=["campus_square"], time_slots=["late_morning"], tone="positive", base_importance=0.40, tags=["routine", "bonding"]),
    EventTemplate(id="U2", title="Study Group Invitation", category="university", location_tags=["library", "classroom"], time_slots=["afternoon"], tone="positive", base_importance=0.58, tags=["study"]),
    EventTemplate(id="U3", title="Library Seat Encounter", category="university", location_tags=["library"], time_slots=["afternoon"], tone="neutral", base_importance=0.42, tags=["encounter"]),
    EventTemplate(id="U4", title="Cafeteria Lunch Decision", category="university", location_tags=["cafeteria"], time_slots=["afternoon"], tone="positive", base_importance=0.45, tags=["food", "social"]),
    EventTemplate(id="U5", title="Group Project Assignment", category="university", location_tags=["classroom"], time_slots=["late_morning", "afternoon"], tone="mixed", base_importance=0.72, tags=["project", "pressure"]),
    EventTemplate(id="U6", title="Presentation Stress", category="university", location_tags=["classroom"], time_slots=["afternoon"], tone="mixed", base_importance=0.60, tags=["stress", "performance"]),
    EventTemplate(id="U7", title="Campus Club Booth", category="university", location_tags=["campus_square"], time_slots=["afternoon"], tone="positive", base_importance=0.50, tags=["activity", "social"]),
    EventTemplate(id="U8", title="Professor Praise or Criticism", category="university", location_tags=["classroom"], time_slots=["afternoon"], tone="mixed", base_importance=0.62, tags=["achievement", "feedback"]),

    EventTemplate(id="P1", title="Spontaneous Trip Proposal", category="park", location_tags=["entrance"], time_slots=["evening"], tone="positive", base_importance=0.60, tags=["novelty"]),
    EventTemplate(id="P2", title="Roller Coaster Dare", category="park", location_tags=["rides_area"], time_slots=["evening"], tone="mixed", base_importance=0.66, tags=["risk", "challenge"]),
    EventTemplate(id="P3", title="Getting Split Up", category="park", location_tags=["entrance", "rides_area", "arcade", "food_court"], time_slots=["evening"], tone="negative", base_importance=0.64, tags=["stress", "miscoordination"]),
    EventTemplate(id="P4", title="Arcade Competition", category="park", location_tags=["arcade"], time_slots=["evening"], tone="mixed", base_importance=0.58, tags=["competition", "fun"]),
    EventTemplate(id="P5", title="Souvenir Choice", category="park", location_tags=["food_court", "entrance"], time_slots=["late_evening"], tone="positive", base_importance=0.48, tags=["gift", "bonding"]),
    EventTemplate(id="P6", title="Rain Ruins Plan", category="park", location_tags=["entrance", "rides_area"], time_slots=["evening"], tone="negative", base_importance=0.72, tags=["weather", "plan_break"]),
]