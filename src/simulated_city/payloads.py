from __future__ import annotations

from datetime import datetime, timezone


_ALLOWED_WEATHER_STATES = {"sunny", "rain"}


def _utc_timestamp_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def build_weather_payload(*, weather_state: str, tick: int, source: str = "agent_weather") -> dict[str, str | int]:
    """Build a validated weather payload for MQTT publishing."""
    normalized_state = weather_state.strip().lower()
    if normalized_state not in _ALLOWED_WEATHER_STATES:
        raise ValueError("weather_state must be 'sunny' or 'rain'")
    if tick < 0:
        raise ValueError("tick must be >= 0")

    return {
        "source": source,
        "weather_state": normalized_state,
        "tick": tick,
        "timestamp": _utc_timestamp_iso(),
    }
