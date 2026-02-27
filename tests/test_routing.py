import pytest

from simulated_city.routing import (
    Shop,
    build_move_command,
    select_nearest_shop,
    should_enter_random_walk_mode,
    should_enter_shelter_mode,
    step_toward_target,
)


def test_select_nearest_shop() -> None:
    shops = [
        Shop(shop_id="shop_1", name="North", x=10.0, y=10.0),
        Shop(shop_id="shop_2", name="South", x=80.0, y=80.0),
    ]
    nearest = select_nearest_shop(person_x=12.0, person_y=11.0, shops=shops)
    assert nearest.shop_id == "shop_1"


def test_build_move_command_requires_shop_for_move_to_shop() -> None:
    with pytest.raises(ValueError, match="target_shop"):
        build_move_command(person_id="person_1", mode="move_to_shop", tick=1)


def test_build_move_command_for_random_walk() -> None:
    payload = build_move_command(person_id="person_1", mode="random_walk", tick=2)
    assert payload["person_id"] == "person_1"
    assert payload["mode"] == "random_walk"
    assert payload["target_shop"] is None


def test_transition_checks() -> None:
    assert should_enter_shelter_mode("rain", "random_walk") is True
    assert should_enter_shelter_mode("sunny", "random_walk") is False
    assert should_enter_random_walk_mode("sunny", "move_to_shop") is True
    assert should_enter_random_walk_mode("rain", "move_to_shop") is False


def test_step_toward_target() -> None:
    x, y, arrived = step_toward_target(
        x=0.0,
        y=0.0,
        target_x=3.0,
        target_y=4.0,
        step_distance=2.0,
    )
    assert round(x, 3) == 1.2
    assert round(y, 3) == 1.6
    assert arrived is False