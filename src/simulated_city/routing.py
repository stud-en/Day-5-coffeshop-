from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math

from .movement import distance_meters


@dataclass(frozen=True, slots=True)
class Shop:
    """Simple coffee-shop location used by control routing."""

    shop_id: str
    name: str
    x: float
    y: float


def select_nearest_shop(*, person_x: float, person_y: float, shops: list[Shop]) -> Shop:
    """Return the nearest shop to the current person position."""
    if not shops:
        raise ValueError("shops must not be empty")
    return min(shops, key=lambda shop: distance_meters(person_x, person_y, shop.x, shop.y))


def build_move_command(
    *,
    person_id: str,
    mode: str,
    tick: int,
    source: str = "agent_control",
    target_shop: Shop | None = None,
) -> dict[str, str | int | dict[str, str | float] | None]:
    """Build a command payload for person movement mode changes."""
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"random_walk", "move_to_shop"}:
        raise ValueError("mode must be 'random_walk' or 'move_to_shop'")
    if tick < 0:
        raise ValueError("tick must be >= 0")
    if normalized_mode == "move_to_shop" and target_shop is None:
        raise ValueError("target_shop is required when mode is 'move_to_shop'")

    target_shop_payload = None
    if target_shop is not None:
        target_shop_payload = {
            "shop_id": target_shop.shop_id,
            "name": target_shop.name,
            "x": target_shop.x,
            "y": target_shop.y,
        }

    return {
        "source": source,
        "person_id": person_id,
        "mode": normalized_mode,
        "tick": tick,
        "target_shop": target_shop_payload,
        "timestamp": _utc_timestamp_iso(),
    }


def should_enter_shelter_mode(weather_state: str, current_mode: str) -> bool:
    """Return True when rain requires a transition to shelter-seeking mode."""
    return weather_state.strip().lower() == "rain" and current_mode.strip().lower() != "move_to_shop"


def should_enter_random_walk_mode(weather_state: str, current_mode: str) -> bool:
    """Return True when sunny weather requires random-walk mode."""
    return weather_state.strip().lower() == "sunny" and current_mode.strip().lower() != "random_walk"


def step_toward_target(
    *,
    x: float,
    y: float,
    target_x: float,
    target_y: float,
    step_distance: float,
) -> tuple[float, float, bool]:
    """Move from (x, y) toward a target by up to step_distance without teleporting."""
    if step_distance <= 0:
        raise ValueError("step_distance must be > 0")

    dx = target_x - x
    dy = target_y - y
    distance = math.hypot(dx, dy)
    if distance <= step_distance:
        return (target_x, target_y, True)
    ratio = step_distance / distance
    return (x + dx * ratio, y + dy * ratio, False)


def _utc_timestamp_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")