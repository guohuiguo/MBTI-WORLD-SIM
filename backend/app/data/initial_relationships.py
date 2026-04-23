from app.models.state_models import RelationshipState


CHAR_IDS = ["ethan", "leo", "grace", "chloe"]


def _blank_matrix() -> dict[str, dict[str, RelationshipState]]:
    matrix: dict[str, dict[str, RelationshipState]] = {}
    for a in CHAR_IDS:
        matrix[a] = {}
        for b in CHAR_IDS:
            matrix[a][b] = RelationshipState()
    return matrix


def _set_pair(
    matrix: dict[str, dict[str, RelationshipState]],
    a: str,
    b: str,
    closeness: int,
    trust: int,
    tension: int,
    respect: int,
) -> None:
    matrix[a][b] = RelationshipState(
        closeness=closeness,
        trust=trust,
        tension=tension,
        respect=respect,
    )
    matrix[b][a] = RelationshipState(
        closeness=closeness,
        trust=trust,
        tension=tension,
        respect=respect,
    )


def build_initial_relationships() -> dict[str, dict[str, RelationshipState]]:
    matrix = _blank_matrix()

    _set_pair(matrix, "ethan", "leo", closeness=-10, trust=5, tension=20, respect=10)
    _set_pair(matrix, "ethan", "grace", closeness=20, trust=25, tension=0, respect=30)
    _set_pair(matrix, "ethan", "chloe", closeness=5, trust=0, tension=15, respect=18)
    _set_pair(matrix, "leo", "grace", closeness=28, trust=20, tension=0, respect=10)
    _set_pair(matrix, "leo", "chloe", closeness=25, trust=10, tension=8, respect=12)
    _set_pair(matrix, "grace", "chloe", closeness=10, trust=5, tension=10, respect=8)

    return matrix