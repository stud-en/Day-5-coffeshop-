# Coffeeshop Simulation Clarification

## Project Summary
You are building a smart-city simulation where 5 people follow a random walk when weather is sunny, then move toward 2 coffee shops when weather changes to rain. Weather changes every 10–15 seconds, and the simulation is visualized on a live map.

## Scope Lock (Final Decisions)
The decisions in this document are final for the MVP and are intended to remove implementation ambiguity.
Any item marked optional is an extension and is not implemented in the MVP.

## 1) Refined 4-Component Design

### Trigger (Environment State Producer)
A weather agent publishes city weather state events (`sunny` or `rain`) at a periodic interval sampled from 10 to 15 seconds.

### Observer (State Consumers)
People agents subscribe to weather state events and update each person behavior state (for example: `random_walk` to `seeking_shelter`).

### Control Center (Decision Logic)
Movement logic applies two modes: random-walk movement during `sunny`, and nearest-shop routing during `rain`.

### Response (Actuation + Visualization)
People publish incremental position updates every tick (no teleporting). During `sunny`, people move with random-walk steps. During `rain`, people continuously move toward assigned coffee shops until arrival. The dashboard updates map visuals so sky/theme changes from clear (blue) to rainy (gray/darker).

## 2) MQTT Topic Plan (Publish/Subscribe)

### Weather Agent
- Publishes:
  - `city/weather/state`
  - `city/weather/tick`
- Subscribes:
  - none

### People Agent (single notebook managing all 5 people)
- Subscribes:
  - `city/weather/state`
  - `city/people/{person_id}/command`
- Publishes:
  - `city/people/{person_id}/state`
  - `city/people/{person_id}/position`
  - `city/people/aggregate`

### Control Agent
- Subscribes:
  - `city/weather/state`
  - `city/people/+/position`
- Publishes:
  - `city/people/{person_id}/command`

### Dashboard Agent
- Subscribes:
  - `city/weather/state`
  - `city/people/+/position`
  - optional `city/shops/+/status`
- Publishes:
  - usually none

## 3) Configuration Parameters

Use `config.yaml` loaded via `simulated_city.config.load_config()`.

### MQTT
- `mqtt.host`
- `mqtt.port`
- `mqtt.tls`
- `mqtt.username_env`
- `mqtt.password_env`
- `mqtt.base_topic`
- `mqtt.qos`
- `mqtt.retain_weather`

### Timing
- `simulation.weather_interval_min_s` (10)
- `simulation.weather_interval_max_s` (15)
- `simulation.tick_s` (1.0)

### Entities and Locations
- `simulation.num_people` (5)
- `simulation.num_shops` (2)
- `simulation.person_start_locations` (list of lat/lon)
- `simulation.shop_locations` (list of lat/lon)

### Movement / Behavior
- `simulation.person_speed_mps` (1.2)
- `simulation.arrival_radius_m` (3.0)
- `simulation.random_walk_step_m` (2.0)
- `simulation.random_walk_turn_deg_max` (45)
- `simulation.boundary_mode` (`bounce`)
- optional `simulation.max_shop_capacity`
- optional `simulation.reroute_on_full`

### Dashboard / Map
- `map.center`
- `map.zoom`
- `map.style_clear`
- `map.style_rain`

## 4) Notebook Plan (One per Agent Type)

- `notebooks/agent_weather.ipynb`
  - publishes weather transitions
- `notebooks/agent_people.ipynb`
  - subscribes to weather and publishes person movement/state
- `notebooks/agent_control.ipynb`
  - centralized movement command logic
- `notebooks/dashboard_city.ipynb`
  - subscribes to all relevant topics and renders the map with anymap-ts

## 5) Classes vs Functions

### Model as Classes (Stateful)
- `WeatherAgent`
- `PeopleAgent`
- `Person`
- `ControlAgent`
- `PersonState` (data model)
- `Shop` (data model)

### Keep as Simple Functions (Stateless)
- nearest-shop selection
- distance calculation
- payload building/validation
- topic naming helpers
- map style selection by weather

## 6) Library Code vs Notebook Code

### Put in `src/simulated_city/` (Reusable)
- config parsing/validation helpers
- MQTT helper wrappers and payload checks
- movement and routing utilities
- shared data models and constants

### Keep in notebooks (Scenario Runtime)
- agent loops and subscriptions
- per-agent publish cycles
- simulation initialization for this scenario
- dashboard visualization wiring

## 7) Ambiguities Resolved (Final MVP Rules)

1. Movement model: use continuous movement every simulation tick (`simulation.tick_s = 1.0`).
2. Shop selection: use nearest-shop routing only (no capacity logic in MVP).
3. Weather pattern: use strict alternating states (`sunny` then `rain`), with each change occurring after a random interval in [10, 15] seconds.
4. Sunny behavior: each person uses random-walk movement (bounded by map limits with `boundary_mode = bounce`).
5. Rain behavior: each person continuously moves toward the assigned shop (no teleporting).
6. Post-rain behavior: when weather changes back to `sunny`, each person resumes random-walk movement from the current location.
7. Agent granularity: use one people notebook that manages all 5 people.
8. Person identity model: create a `Person` class; assign each person a unique name and color from fixed predefined lists.
9. Control placement: use a separate control notebook (`agent_control.ipynb`) for routing commands.
10. Topic authority: only `agent_control.ipynb` publishes movement commands; `agent_people.ipynb` executes commands and publishes state/position.

---

## Recommended MVP Decisions

To keep implementation simple and aligned with workshop rules:
- use four notebooks: weather, control, people, and dashboard
- use nearest-shop routing only
- use random walk in sunny weather and continuous routing in rain
- use continuous movement with fixed speed and arrival radius (no teleporting)
- use strict alternating weather states with random interval in [10, 15] seconds
- resume random-walk behavior on sunny transitions
