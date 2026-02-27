from __future__ import annotations


CITY_ROOT_TOPIC = "city"


def weather_state_topic() -> str:
    """Return the canonical weather-state topic for the MVP."""
    return f"{CITY_ROOT_TOPIC}/weather/state"


def weather_tick_topic() -> str:
    """Return the canonical weather-tick topic for the MVP."""
    return f"{CITY_ROOT_TOPIC}/weather/tick"
