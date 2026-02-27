# Coffeeshop Phased Implementation Plan (PLAN Mode)

This plan is based on the clarified design in `docs/coffeeshop_simulation_clarification.md`.

Scope of this document:
- Describe phases and structure only
- List files, tests, and dependencies
- Do not implement code yet

---

## Phase 1: Minimal Working Example (One Agent, Basic Logic)

### 1) New files
- Notebook:
  - `notebooks/agent_people.ipynb`
- Library modules:
  - `src/simulated_city/models.py`
  - `src/simulated_city/movement.py`

### 2) Architecture (Notebook vs Library)
- Notebook:
  - single simulation loop for 5 people
  - per-tick random-walk updates in sunny state
  - local state display/log output
- Library:
  - reusable movement utilities
  - data models and shared state definitions

### 3) Classes vs functions
- Classes:
  - `Person`
  - `PersonState`
- Helper functions:
  - `random_walk_step(...)`
  - `apply_boundary_bounce(...)`
  - `distance_meters(...)`

### 4) Tests/Verification
- `python scripts/validate_structure.py`
- `python -m pytest tests/test_smoke.py`
- Manual verification:
  - run notebook and confirm movement is continuous (no teleporting)

### 5) Investigation before next phase
- Confirm coordinate convention and map bounds to use everywhere
- Confirm random-walk behavior parameters are reasonable for visualization

### 6) Dependencies
- No new dependencies expected in this phase

---

## Phase 2: Add Configuration File (config.yaml)

### 1) New files
- Modify:
  - `config.yaml`
  - `notebooks/agent_people.ipynb`
  - `src/simulated_city/config.py`
- Optional new module:
  - `src/simulated_city/simulation_config.py`
- Modify tests:
  - `tests/test_config.py`

### 2) Architecture (Notebook vs Library)
- Notebook:
  - load configuration and apply values to loop
- Library:
  - typed config models
  - parsing and validation helpers

### 3) Classes vs functions
- Classes/dataclasses:
  - `SimulationConfig`
  - `MovementConfig`
  - `MapConfig`
- Helper functions:
  - range checks
  - normalization of coordinate inputs

### 4) Tests/Verification
- `python scripts/verify_setup.py`
- `python -m pytest tests/test_config.py`
- Manual verification:
  - modify one config value and confirm behavior changes as expected

### 5) Investigation before next phase
- Finalize MQTT payload fields for weather/state/position/command
- Confirm canonical topic naming for MVP (`city/...`)

### 6) Dependencies
- No new dependencies expected in this phase

---

## Phase 3: Add MQTT Publishing

### 1) New files
- Notebook:
  - `notebooks/agent_weather.ipynb`
- Library modules:
  - `src/simulated_city/topics.py`
  - `src/simulated_city/payloads.py`
- Optional updates:
  - `src/simulated_city/mqtt.py` (only if shared helper gaps are found)

### 2) Architecture (Notebook vs Library)
- Notebook:
  - weather loop
  - publish weather state/tick messages
- Library:
  - topic constants/builders
  - payload building utilities

### 3) Classes vs functions
- Class (optional):
  - `WeatherAgent`
- Helper functions:
  - `weather_state_topic()`
  - `weather_tick_topic()`
  - `build_weather_payload(...)`

### 4) Tests/Verification
- `python -m pytest tests/test_mqtt_profiles.py tests/test_smoke.py`
- Manual verification:
  - run weather notebook and confirm MQTT publishes expected message shape/cadence

### 5) Investigation before next phase
- Confirm notebook MQTT callback and reconnect strategy
- Confirm retained message behavior for weather state

### 6) Dependencies
- No new dependencies expected (MQTT libs already in project)

---

## Phase 4: Add Second Agent with MQTT Subscription

### 1) New files
- Notebook:
  - `notebooks/agent_control.ipynb`
- Modify:
  - `notebooks/agent_people.ipynb`
- Library module:
  - `src/simulated_city/routing.py`
- Optional tests:
  - `tests/test_routing.py`

### 2) Architecture (Notebook vs Library)
- Control notebook:
  - subscribe to weather + people positions
  - publish person command messages
- People notebook:
  - subscribe to command topic
  - execute state transitions and movement mode changes
- Library:
  - nearest-shop routing
  - command payload helpers

### 3) Classes vs functions
- Classes:
  - `ControlAgent`
  - `Shop`
- Helper functions:
  - `select_nearest_shop(...)`
  - `build_move_command(...)`
  - transition checks

### 4) Tests/Verification
- `python -m pytest`
- Manual integrated verification (weather + control + people):
  - sunny => random walk
  - rain => continuous movement to nearest shop

### 5) Investigation before next phase
- Confirm expected command frequency and anti-spam strategy
- Confirm authority model (control publishes commands, people execute)

### 6) Dependencies
- No new dependencies expected in this phase

---

## Phase 5: Add Dashboard Visualization

### 1) New files
- Notebook:
  - `notebooks/dashboard_city.ipynb`
- Optional library module:
  - `src/simulated_city/dashboard_state.py`
- Reuse/possible update:
  - `src/simulated_city/maplibre_live.py`

### 2) Architecture (Notebook vs Library)
- Dashboard notebook:
  - subscribe to weather and people topics
  - render live map with `anymap-ts`
- Library:
  - map feature transformations
  - weather-to-style mapping helpers

### 3) Classes vs functions
- Class (optional):
  - `DashboardState`
- Helper functions:
  - `to_feature_collection(...)`
  - `style_for_weather(...)`

### 4) Tests/Verification
- `python scripts/validate_structure.py`
- `python -m pytest tests/test_maplibre_live.py`
- Manual verification:
  - run all notebooks and validate movement + weather style changes

### 5) Investigation before next phase
- Tune redraw interval vs message rate for smooth map updates
- Confirm UI remains responsive while callbacks process MQTT messages

### 6) Dependencies
- Ensure notebook extras are installed:
  - `pip install -e ".[notebooks]"`

---

## Phase 6: Hardening, Documentation, and Acceptance

### 1) New files
- Modify docs as needed:
  - `docs/exercises.md`
  - `docs/mqtt.md`
  - `docs/overview.md`
  - `README.md`
- Optional validator alignment:
  - `scripts/validate_structure.py`
- Add focused tests where coverage gaps remain:
  - e.g., payload/topic/routing tests

### 2) Architecture (Notebook vs Library)
- No major architecture changes
- Stabilize contracts between notebooks and shared library helpers

### 3) Classes vs functions
- Prefer keeping new utilities stateless unless persistent state is clearly needed
- Avoid adding extra classes beyond MVP needs

### 4) Tests/Verification
- `python scripts/verify_setup.py`
- `python scripts/validate_structure.py`
- `python -m pytest`
- Manual acceptance run with all notebooks active

### 5) Investigation before completion
- Confirm no drift between design doc, config schema, topic schema, and runtime behavior
- Confirm all MVP rules are met (distributed notebooks, MQTT communication, no teleporting)

### 6) Dependencies
- No new dependencies unless a clearly justified gap appears

---

## Dependency Summary
- Required project extras for notebook workflow:
  - `pip install -e ".[dev,notebooks]"`
- Mapping for live dashboard:
  - `anymap-ts[all]` (already specified in project extras)
- MQTT client:
  - `paho-mqtt` (already specified)
- No `folium`, `plotly`, or live `matplotlib` mapping for this workflow

---

## Suggested Review Checklist Before Phase 1 Implementation
- Confirm topic namespace and payload schema are accepted
- Confirm config keys and defaults are accepted
- Confirm test/verification commands are accepted
- Confirm file naming and notebook split are accepted
