from simulated_city.config import load_config
import pytest
import textwrap


def test_load_config_defaults_when_missing(tmp_path) -> None:
    """Test that default config loads when file is missing."""
    cfg = load_config(tmp_path / "missing.yaml")
    assert cfg.mqtt.host
    assert cfg.mqtt.port
    # Should have at least the default 'local' profile
    assert "local" in cfg.mqtt_configs or len(cfg.mqtt_configs) > 0


def test_load_config_reads_yaml(tmp_path) -> None:
    """Test reading YAML config with multi-broker structure."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [default]
          profiles:
            default:
              host: example.com
              port: 1883
              tls: false
          client_id_prefix: demo
          keepalive_s: 30
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.mqtt.host == "example.com"
    assert cfg.mqtt.port == 1883
    assert cfg.mqtt.tls is False
    assert cfg.mqtt.client_id_prefix == "demo"
    assert cfg.mqtt.keepalive_s == 30


def test_load_config_finds_parent_config_yaml(tmp_path, monkeypatch) -> None:
    """Test that config is found in parent directories."""
    # Simulate running from a subdirectory (like notebooks/)
    root = tmp_path
    (root / "config.yaml").write_text(
        """
        mqtt:
          active_profiles: [parent]
          profiles:
            parent:
              host: parent.example.com
              port: 1883
              tls: false
          client_id_prefix: demo
          keepalive_s: 30
        """.strip(),
        encoding="utf-8",
    )

    subdir = root / "notebooks"
    subdir.mkdir()
    monkeypatch.chdir(subdir)

    cfg = load_config("config.yaml")
    assert cfg.mqtt.host == "parent.example.com"

def test_load_config_multi_broker_with_active_profiles(tmp_path) -> None:
    """Test multi-broker configuration with active_profiles list."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [local, public]
          profiles:
            local:
              host: localhost
              port: 1883
              tls: false
            public:
              host: broker.example.com
              port: 1883
              tls: false
          client_id_prefix: multi-test
          keepalive_s: 60
          base_topic: test-city
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    
    # Primary broker (first in list)
    assert cfg.mqtt.host == "localhost"
    assert cfg.mqtt.port == 1883
    
    # All brokers available by name
    assert "local" in cfg.mqtt_configs
    assert "public" in cfg.mqtt_configs
    assert cfg.mqtt_configs["local"].host == "localhost"
    assert cfg.mqtt_configs["public"].host == "broker.example.com"


def test_load_config_single_broker_with_active_profiles(tmp_path) -> None:
    """Test single-broker configuration using active_profiles."""
    p = tmp_path / "config.yaml"
    p.write_text(
        """
        mqtt:
          active_profiles: [local]
          profiles:
            local:
              host: localhost
              port: 1883
              tls: false
          client_id_prefix: single-test
          keepalive_s: 60
          base_topic: test-city
        """.strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    
    # Primary broker
    assert cfg.mqtt.host == "localhost"
    
    # Only local broker in configs
    assert "local" in cfg.mqtt_configs
    assert len(cfg.mqtt_configs) == 1


def test_load_config_parses_phase2_simulation_config(tmp_path) -> None:
    """Phase 2: simulation movement/map config is parsed into typed fields."""
    p = tmp_path / "config.yaml"
    p.write_text(
        textwrap.dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              people_count: 5
              seed: 7
              movement:
                tick_s: 0.5
                total_ticks: 8
                step_distance_m: 2.5
                max_turn_deg: 30
                boundary_mode: bounce
              map:
                min_x: 0
                max_x: 50
                min_y: 0
                max_y: 60
              names: [Alex, Sam]
              colors: [red, blue]
            """
        ).strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.simulation is not None
    assert cfg.simulation.people_count == 5
    assert cfg.simulation.seed == 7
    assert cfg.simulation.movement.tick_s == 0.5
    assert cfg.simulation.movement.total_ticks == 8
    assert cfg.simulation.movement.step_distance_m == 2.5
    assert cfg.simulation.movement.max_turn_deg == 30.0
    assert cfg.simulation.map.min_x == 0.0
    assert cfg.simulation.map.max_y == 60.0
    assert cfg.simulation.names == ("Alex", "Sam")
    assert cfg.simulation.colors == ("red", "blue")


def test_load_config_normalizes_map_bounds(tmp_path) -> None:
    """Phase 2: map bounds are normalized if min/max are reversed."""
    p = tmp_path / "config.yaml"
    p.write_text(
        textwrap.dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              movement:
                tick_s: 1.0
                total_ticks: 2
                step_distance_m: 1.0
                max_turn_deg: 20
                boundary_mode: bounce
              map:
                min_x: 100
                max_x: 0
                min_y: 80
                max_y: 10
            """
        ).strip(),
        encoding="utf-8",
    )

    cfg = load_config(p)
    assert cfg.simulation is not None
    assert cfg.simulation.map.min_x == 0.0
    assert cfg.simulation.map.max_x == 100.0
    assert cfg.simulation.map.min_y == 10.0
    assert cfg.simulation.map.max_y == 80.0


def test_load_config_rejects_invalid_movement_ranges(tmp_path) -> None:
    """Phase 2: invalid movement values are rejected."""
    p = tmp_path / "config.yaml"
    p.write_text(
        textwrap.dedent(
            """
            mqtt:
              active_profiles: [local]
              profiles:
                local:
                  host: localhost
                  port: 1883
                  tls: false
            simulation:
              movement:
                tick_s: -1
                total_ticks: 2
                step_distance_m: 1.0
                max_turn_deg: 20
                boundary_mode: bounce
            """
        ).strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="simulation.movement.tick_s"):
        load_config(p)