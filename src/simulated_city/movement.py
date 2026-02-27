from __future__ import annotations

import math
import random


def distance_meters(x1: float, y1: float, x2: float, y2: float) -> float:
    """Return Euclidean distance in the simulation coordinate space."""
    return math.hypot(x2 - x1, y2 - y1)


def random_walk_step(
    x: float,
    y: float,
    heading_deg: float,
    step_distance: float,
    max_turn_deg: float,
    rng: random.Random,
) -> tuple[float, float, float]:
    """Compute one random-walk step and return new x, y, and heading."""
    turn_delta = rng.uniform(-max_turn_deg, max_turn_deg)
    new_heading = (heading_deg + turn_delta) % 360.0
    heading_rad = math.radians(new_heading)
    new_x = x + step_distance * math.cos(heading_rad)
    new_y = y + step_distance * math.sin(heading_rad)
    return (new_x, new_y, new_heading)


def apply_boundary_bounce(
    x: float,
    y: float,
    heading_deg: float,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
) -> tuple[float, float, float]:
    """Reflect position/heading when a step crosses rectangular boundaries."""
    new_x = x
    new_y = y
    new_heading = heading_deg % 360.0

    if new_x < min_x:
        new_x = min_x + (min_x - new_x)
        new_heading = (180.0 - new_heading) % 360.0
    elif new_x > max_x:
        new_x = max_x - (new_x - max_x)
        new_heading = (180.0 - new_heading) % 360.0

    if new_y < min_y:
        new_y = min_y + (min_y - new_y)
        new_heading = (-new_heading) % 360.0
    elif new_y > max_y:
        new_y = max_y - (new_y - max_y)
        new_heading = (-new_heading) % 360.0

    return (new_x, new_y, new_heading)
