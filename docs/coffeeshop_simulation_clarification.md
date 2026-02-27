# Coffeeshop Simulation Clarification

## Project Summary
You are building a smart-city simulation where 5 people move toward 2 coffee shops when weather changes to rain. Weather changes every 10–15 seconds, and the simulation is visualized on a live map.

## 1) Refined 4-Component Design

### Trigger (Environment State Producer)
A weather agent publishes city weather state events (`sunny` or `rain`) at a periodic interval sampled from 10 to 15 seconds.

### Observer (State Consumers)
People agents subscribe to weather state events and update each person behavior state (for example: `outdoors` to `seeking_shelter`).

### Control Center (Decision Logic)
Movement logic decides which coffee shop each person should go to when weather is `rain`. The simplest rule is nearest-shop routing.

### Response (Actuation + Visualization)
People publish updated positions until they arrive at a coffee shop. The dashboard updates map visuals so sky/theme changes from clear (blue) to rainy (gray/darker).

## 2) MQTT Topic Plan (Publish/Subscribe)

### Weather Agent
- Publishes:
  - `city/weather/state`
  - optional `city/weather/tick`
- Subscribes:
  - none

### People Agent (single notebook managing all 5 people)
- Subscribes:
  - `city/weather/state`
- Publishes:
  - `city/people/{person_id}/state`
  - `city/people/{person_id}/position`
  - optional `city/people/aggregate`

### Optional Control Agent (if centralized routing is used)
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
- `simulation.tick_s`

### Entities and Locations
- `simulation.num_people` (5)
- `simulation.num_shops` (2)
- `simulation.person_start_locations` (list of lat/lon)
- `simulation.shop_locations` (list of lat/lon)

### Movement / Behavior
- `simulation.person_speed_mps`
- `simulation.arrival_radius_m`
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
- `notebooks/agent_control.ipynb` (optional)
  - centralized movement command logic
- `notebooks/dashboard_city.ipynb`
  - subscribes to all relevant topics and renders the map with anymap-ts

## 5) Classes vs Functions

### Model as Classes (Stateful)
- `WeatherAgent`
- `PeopleAgent` or `PersonAgent`
- optional `ControlAgent`
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

## 7) Ambiguities to Resolve Before Coding with solutions

1. Movement model: continuous movement every tick, or immediate move to destination? Solution: continous movement every tick.
2. Shop selection: nearest only, or capacity-aware routing? Solution: Nearest only.
3. Weather pattern: strict alternating sunny/rain, or random each cycle? Solution: Strict alternating.
4. Post-rain behavior: do people stay in shops or return outside when sunny? Solution: People return outside.
5. Agent granularity: one people notebook managing all 5, or one notebook per person? Solutions: One notebook with 5 people. Make people a Class, that selects a random name and color from a list with 10 names and a list with 10 colors.
6. Control placement: separate control notebook, or embed routing logic in people agent for MVP? Solution: Sepatate control notebook.

---

## Recommended MVP Decisions

To keep implementation simple and aligned with workshop rules:
- use one weather agent notebook, one people agent notebook, one dashboard notebook
- use nearest-shop routing only
- use continuous movement with fixed speed and arrival radius
- use random weather interval in [10, 15] seconds
