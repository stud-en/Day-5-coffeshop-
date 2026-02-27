from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PersonState(str, Enum):
    """Simple behavior states for a person in the simulation."""

    RANDOM_WALK = "random_walk"


@dataclass(slots=True)
class Person:
    """Represents one moving person in the city simulation."""

    person_id: str
    name: str
    color: str
    x: float
    y: float
    heading_deg: float
    state: PersonState = PersonState.RANDOM_WALK

    def position_tuple(self) -> tuple[float, float]:
        """Return position as an (x, y) tuple."""
        return (self.x, self.y)

    def to_log_dict(self) -> dict[str, str | float]:
        """Return a small dictionary for readable log output."""
        return {
            "person_id": self.person_id,
            "name": self.name,
            "color": self.color,
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "heading_deg": round(self.heading_deg % 360.0, 2),
            "state": self.state.value,
        }
