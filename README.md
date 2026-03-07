# ☀️ Solar of Things — Home Assistant Integration

<p align="center">
  <a href="https://github.com/conexocasa/solar-of-things-ha/releases/latest">
    <img src="https://img.shields.io/github/v/release/conexocasa/solar-of-things-ha?style=for-the-badge&label=Latest%20Release&color=orange" alt="Latest Release">
  </a>
  <a href="https://github.com/custom-components/hacs">
    <img src="https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge" alt="HACS Custom">
  </a>
  <a href="https://www.home-assistant.io/">
    <img src="https://img.shields.io/badge/Home%20Assistant-2023.1%2B-41BDF5?style=for-the-badge&logo=home-assistant" alt="Home Assistant">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/github/license/conexocasa/solar-of-things-ha?style=for-the-badge" alt="MIT License">
  </a>
  <a href="https://github.com/conexocasa/solar-of-things-ha/actions/workflows/validate.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/conexocasa/solar-of-things-ha/validate.yml?branch=main&style=for-the-badge&label=CI" alt="CI Status">
  </a>
</p>

<p align="center">
  <strong>Monitor and control your Siseli solar inverter directly from Home Assistant.</strong><br>
  Real-time power data · Battery management · Grid control · Energy Dashboard ready
</p>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Sensors](#sensors)
- [Control Entities](#control-entities)
- [Requirements](#requirements)
- [Installation](#installation)
  - [HACS (Recommended)](#hacs-recommended)
  - [Manual Installation](#manual-installation)
- [Configuration](#configuration)
  - [Step 1 — Find Your Credentials](#step-1--find-your-credentials)
  - [Step 2 — Add the Integration](#step-2--add-the-integration)
  - [Step 3 — Verify Entities](#step-3--verify-entities)
  - [Multiple Stations](#multiple-stations)
- [Screenshots](#screenshots)
- [Energy Dashboard](#energy-dashboard)
- [Automation Examples](#automation-examples)
- [Dashboard Card Examples](#dashboard-card-examples)
- [Troubleshooting](#troubleshooting)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

---

## Overview

The **Solar of Things** integration connects Home Assistant to the
[Siseli solar portal](https://solar.siseli.com) and provides:

- **Auto-discovery** of every inverter device under your station — enter your
  Station ID once and Home Assistant finds all your devices automatically.
- **10+ real-time sensors** for power, battery, grid and load data, updated
  every 5 minutes.
- **4 monthly summary sensors** for energy totals and solar coverage.
- **8 control entities** (sliders, dropdowns, switches) to manage battery
  limits, operating modes and grid settings directly from HA.
- Full compatibility with the **Home Assistant Energy Dashboard**.
- **Multi-station support** — add the integration once per station.

> API behavior is based on the Siseli web portal and the reference CLI client
> at [Hyllesen/solar-of-things-solar-usage](https://github.com/Hyllesen/solar-of-things-solar-usage).

---

## Features

| Category | What you get |
|---|---|
| 🔍 **Auto-discovery** | Enter Station ID → HA fetches all device IDs automatically |
| 📊 **Real-time monitoring** | 10 per-device sensors, updated every 5 min |
| 📅 **Monthly statistics** | 4 station-level energy summary sensors |
| 🎛️ **System control** | 8 control entities (battery limits, modes, grid switches) |
| ⚡ **Energy Dashboard** | All power and energy sensors are dashboard-ready |
| 🏠 **Multi-station** | Unlimited stations via multiple config entries |
| 🔒 **Secure auth** | User ID + Password login with automatic token refresh (no manual token copying) |
| 🌏 **Timezone-aware** | Configurable `IOT-Time-Zone` header per integration |
| 🔄 **Auto-retry** | HA coordinator pattern with automatic retry on failure |

---

## Sensors

### Real-time Device Sensors
> Updated every **5 minutes** · One set per discovered device

| Entity | Unit | Device Class | Description |
|---|---|---|---|
| `{device} PV Input Power` | W | `power` | Solar panel DC input power |
| `{device} AC Output Power` | W | `power` | AC power delivered to loads |
| `{device} Battery Charging Current` | A | `current` | Current flowing into battery |
| `{device} Battery Discharge Current` | A | `current` | Current flowing out of battery |
| `{device} Battery Voltage` | V | `voltage` | Battery bank terminal voltage |
| `{device} Battery Power` | W | `power` | Net battery power (calculated: discharge − charge × voltage) |
| `{device} Battery State of Charge` | % | `battery` | Battery charge level |
| `{device} Grid Feed-in Power` | W | `power` | Power exported to the utility grid |
| `{device} Grid Import Power` | W | `power` | Power imported from the utility grid (calculated) |
| `{device} Load Power` | W | `power` | Total household / load consumption |

### Monthly Station Sensors
> Updated every **30 minutes** · Requires Station ID

| Entity | Unit | Device Class | Description |
|---|---|---|---|
| `Station {id} Monthly PV Generated` | kWh | `energy` | Total solar generation this month |
| `Station {id} Monthly Grid Import` | kWh | `energy` | Total grid import this month |
| `Station {id} Monthly Total Consumption` | kWh | `energy` | Total household consumption this month |
| `Station {id} Monthly Solar Coverage` | % | — | Percentage of consumption met by solar |

---

## Control Entities

> Control entities require your device firmware/account to support the
> settings API. If controls are unresponsive, see
> [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Number Entities (Sliders)

| Entity | Range | Step | Unit | Description |
|---|---|---|---|---|
| `{device} Battery Charge Limit` | 0 – 100 | 1 | % | Maximum SOC target for charging |
| `{device} Battery Discharge Limit` | 0 – 100 | 1 | % | Minimum SOC before stopping discharge |
| `{device} Grid Charge Limit` | 0 – 5000 | 100 | W | Max grid power used for battery charging |

### Select Entities (Dropdowns)

| Entity | Options | Description |
|---|---|---|
| `{device} Operating Mode` | Self-Use · Time-of-Use · Backup · Grid-Tie · Off-Grid | System operating strategy |
| `{device} Battery Priority` | Solar First · Battery First · Grid First | Energy source priority order |

### Switch Entities

| Entity | Description |
|---|---|
| `{device} Grid Charging` | Allow/deny battery charging from the grid |
| `{device} Grid Feed-In` | Allow/deny exporting excess power to the grid |
| `{device} Backup Mode` | Reserve battery capacity for power outages |

---

## Requirements

| Requirement | Details |
|---|---|
| Home Assistant | 2023.1 or newer |
| Siseli account | Active account at [solar.siseli.com](https://solar.siseli.com) |
| IOT-Token | Retrieved from browser DevTools (see [Configuration](#configuration)) |
| Station ID | 18-digit ID from the Siseli portal |
| Network | Home Assistant must be able to reach `https://solar.siseli.com` |

---

## Installation

### HACS (Recommended)

> HACS is the easiest way to install and keep the integration up to date.

1. Open **HACS** in your Home Assistant sidebar.
2. Click **Integrations**.
3. Click the three-dot menu **⋮** (top-right) → **Custom repositories**.
4. Add the repository:
   ```
   https://github.com/conexocasa/solar-of-things-ha
   ```
   Category: **Integration**
5. Click **Add**, then search for **Solar of Things**.
6. Click **Download** and confirm.
7. **Restart Home Assistant.**

> After restarting, continue to [Configuration](#configuration).

---

### Manual Installation

1. Download the latest release asset:
   **[solar-of-things-ha.zip](https://github.com/conexocasa/solar-of-things-ha/releases/latest)**

2. Extract the ZIP. Inside you will find:
   ```
   custom_components/
   └── solar_of_things/
       ├── __init__.py
       ├── api.py
       ├── config_flow.py
       ├── const.py
       ├── manifest.json
       ├── number.py
       ├── select.py
       ├── sensor.py
       ├── strings.json
       ├── switch.py
       └── translations/
           └── en.json
   ```

3. Copy the **`solar_of_things`** folder into your HA config directory:
   ```
   /config/custom_components/solar_of_things/
   ```

4. **Restart Home Assistant.**

> Verify the folder is in the right place: go to
> **Settings → System → Logs** and look for `solar_of_things`.
> No errors means the component loaded correctly.

---

## Configuration

### Step 1 — Find Your Credentials

You need three values from the Siseli portal.
All three are visible in the browser's Network tab — no third-party tools needed.

1. Open [https://solar.siseli.com](https://solar.siseli.com) and log in.
2. Press **F12** (or **Cmd + Option + I** on macOS) to open DevTools.
3. Click the **Network** tab.
4. Press **Ctrl + R** (or **Cmd + R**) to refresh the page.
5. Click any request that goes to `solar.siseli.com` and look at:

| Value | Where to find it | Example |
|---|---|---|
| **IOT-Token** | Request **Headers** tab → `IOT-Token` | `CA49A160DBFFE7A827...` |
| **Station ID** | Request **Payload** tab → `stationId` | `423564214316007425` |
| **Device ID** | Request **Payload** tab → `deviceId` | `423564214341173249` |

> **Tip:** Filter the Network tab by typing `device/list` or `history` to find
> the relevant requests faster.

> **Security:** Your IOT-Token is session-based and may expire.
> If the integration stops working, re-copy a fresh token from the portal.

---

### Step 2 — Add the Integration

1. In Home Assistant go to **Settings → Devices & Services**.
2. Click **+ Add Integration** (bottom-right).
3. Search for **Solar of Things** and select it.
4. Fill in the configuration form:

   | Field | Required | Description |
   |---|---|---|
   | **IOT Token** | ✅ Yes | Paste your `IOT-Token` header value |
   | **Station ID** | ✅ Yes | 18-digit Station ID |
   | **Device ID** | ⬜ Optional | Leave blank to auto-discover ALL devices |
   | **Time zone** | ⬜ Optional | Default: `Asia/Manila`. Set to your local tz (e.g. `Europe/Berlin`) |

5. Click **Submit**. The integration will:
   - Validate your token by calling the Siseli API.
   - Auto-discover all device IDs under the station.
   - Create HA entities for every discovered device.

> **Device ID is optional.** If you leave it blank, Home Assistant will call
> `POST /apis/device/list` and create entities for every inverter under your
> station automatically. Set `Device ID` only if you want to restrict entities
> to a single device.

---

### Step 3 — Verify Entities

After adding the integration, go to
**Settings → Devices & Services → Solar of Things** and click your station.

You should see:

- ☀️ Sensor entities (PV power, battery, grid, load)
- 🔢 Number sliders (battery charge/discharge limits, grid charge limit)
- 🔽 Select dropdowns (operating mode, battery priority)
- 🔘 Switches (grid charging, grid feed-in, backup mode)
- 📊 Monthly energy summary sensors (if station ID is set)

> Entities may show **Unknown** for the first 5 minutes while the coordinator
> fetches the first data update.

---

### Multiple Stations

To monitor more than one station:

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration** again.
3. Search for **Solar of Things** and add it with the credentials for your
   second station.
4. Repeat for every additional station.

Each station appears as a separate device group in Home Assistant with its own
set of sensors and control entities.

---

## Screenshots

> The screenshots below show typical HA entity cards for this integration.
> Your entity names will include your device name (e.g. `1_Inverter`) instead
> of the placeholder shown.

### Device sensors in Entities view
```
┌─────────────────────────────────────────────────────┐
│  1_Inverter · Siseli Solar Inverter                 │
├─────────────────────────────────────────────────────┤
│  ☀️  PV Input Power              22 W               │
│  🔌  AC Output Power            324 W               │
│  🔋  Battery State of Charge     76 %               │
│  🔋  Battery Voltage           27.2 V               │
│  ⬆️  Battery Charging Current   1.2 A               │
│  ⬇️  Battery Discharge Current  0.0 A               │
│  ⚡  Battery Power             32.6 W               │
│  🏠  Load Power                324 W               │
│  📤  Grid Feed-in Power          0 W               │
│  📥  Grid Import Power           0 W               │
├─────────────────────────────────────────────────────┤
│  🎛️  Battery Charge Limit       ████░░░░  80 %      │
│  🎛️  Battery Discharge Limit    █░░░░░░░  10 %      │
│  🎛️  Grid Charge Limit          ░░░░░░░░   0 W      │
│  🔽  Operating Mode             Self-Use            │
│  🔽  Battery Priority           Solar First         │
│  🔘  Grid Charging              OFF                 │
│  🔘  Grid Feed-In               ON                  │
│  🔘  Backup Mode                OFF                 │
└─────────────────────────────────────────────────────┘
```

### Monthly station summary sensors
```
┌─────────────────────────────────────────────────────┐
│  Solar Station 423564214316007425                   │
├─────────────────────────────────────────────────────┤
│  📊  Monthly PV Generated      95.45 kWh            │
│  📊  Monthly Grid Import        0.00 kWh            │
│  📊  Monthly Total Consumption  0.00 kWh            │
│  📊  Monthly Solar Coverage       — %               │
└─────────────────────────────────────────────────────┘
```

### Energy Dashboard configuration
```
  Solar production  ──▶  sensor.1_inverter_pv_input_power
  Grid consumption  ──▶  sensor.1_inverter_grid_import_power
  Return to grid    ──▶  sensor.1_inverter_grid_feed_in_power
  Battery charge    ──▶  sensor.1_inverter_battery_charging_current
  Battery discharge ──▶  sensor.1_inverter_battery_discharge_current
```

---

## Energy Dashboard

This integration is fully compatible with the HA Energy Dashboard.

Go to **Settings → Dashboards → Energy** and add:

| Dashboard slot | Entity to use |
|---|---|
| Solar production | `sensor.{device}_pv_input_power` |
| Grid consumption | `sensor.{device}_grid_import_power` |
| Return to grid | `sensor.{device}_grid_feed_in_power` |
| Battery charge | `sensor.{device}_battery_charging_current` |
| Battery discharge | `sensor.{device}_battery_discharge_current` |

For monthly totals use the station-level sensors:

| Dashboard slot | Entity to use |
|---|---|
| Solar production (monthly) | `sensor.station_{id}_monthly_pv_generated` |
| Grid import (monthly) | `sensor.station_{id}_monthly_grid_import` |

---

## Automation Examples

### Low battery alert
```yaml
automation:
  - alias: "Solar — Low Battery Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.1_inverter_battery_state_of_charge
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Solar Battery Low"
          message: >
            Battery is at
            {{ states('sensor.1_inverter_battery_state_of_charge') }}%.
            Consider reducing load or enabling grid charging.
```

### Auto-enable grid charging at night
```yaml
automation:
  - alias: "Solar — Enable Grid Charging at Night"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.1_inverter_grid_charging
```

### Switch to backup mode before a storm
```yaml
automation:
  - alias: "Solar — Backup Mode Before Storm"
    trigger:
      - platform: state
        entity_id: weather.home
        to: "rainy"
    condition:
      - condition: numeric_state
        entity_id: sensor.1_inverter_battery_state_of_charge
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.1_inverter_backup_mode
      - service: number.set_value
        target:
          entity_id: number.1_inverter_battery_charge_limit
        data:
          value: 95
```

### Time-of-use mode during peak hours
```yaml
automation:
  - alias: "Solar — TOU Mode During Peak Hours"
    trigger:
      - platform: time
        at: "17:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.1_inverter_operating_mode
        data:
          option: "Time-of-Use"
  - alias: "Solar — Self-Use Mode After Peak"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.1_inverter_operating_mode
        data:
          option: "Self-Use"
```

---

## Dashboard Card Examples

### Entities card — quick status overview
```yaml
type: entities
title: ☀️ Solar System
entities:
  - entity: sensor.1_inverter_pv_input_power
    name: Solar Generation
    icon: mdi:solar-power
  - entity: sensor.1_inverter_battery_state_of_charge
    name: Battery Level
    icon: mdi:battery
  - entity: sensor.1_inverter_load_power
    name: Home Load
    icon: mdi:home-lightning-bolt
  - entity: sensor.1_inverter_grid_import_power
    name: Grid Import
    icon: mdi:transmission-tower-import
  - entity: sensor.1_inverter_grid_feed_in_power
    name: Grid Feed-In
    icon: mdi:transmission-tower-export
```

### Glance card — at-a-glance numbers
```yaml
type: glance
title: Solar At a Glance
entities:
  - entity: sensor.1_inverter_pv_input_power
    name: PV
  - entity: sensor.1_inverter_battery_state_of_charge
    name: Battery
  - entity: sensor.1_inverter_load_power
    name: Load
  - entity: sensor.1_inverter_grid_import_power
    name: Grid In
  - entity: sensor.1_inverter_grid_feed_in_power
    name: Grid Out
```

### Control panel card
```yaml
type: entities
title: 🎛️ Solar Controls
entities:
  - entity: select.1_inverter_operating_mode
    name: Operating Mode
  - entity: select.1_inverter_battery_priority
    name: Battery Priority
  - entity: number.1_inverter_battery_charge_limit
    name: Charge Limit
  - entity: number.1_inverter_battery_discharge_limit
    name: Discharge Limit
  - entity: number.1_inverter_grid_charge_limit
    name: Grid Charge Limit
  - type: divider
  - entity: switch.1_inverter_grid_charging
    name: Grid Charging
  - entity: switch.1_inverter_grid_feed_in
    name: Grid Feed-In
  - entity: switch.1_inverter_backup_mode
    name: Backup Mode
```

---

## Troubleshooting

See the full guide: **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

Quick reference for the most common issues:

| Symptom | Most likely cause | Fix |
|---|---|---|
| "Cannot Connect" on setup | Expired or wrong IOT-Token | Re-copy fresh token from portal DevTools |
| No devices discovered | Wrong Station ID | Verify 18-digit stationId in portal Network tab |
| Entities show "Unavailable" | Token expired or portal unreachable | Check HA logs + re-enter token |
| Sensors always "Unknown" | API returns null for that field | Normal for unsupported sensors on your model |
| Controls do nothing | Settings endpoint varies by firmware | Check HA logs for endpoint + HTTP status |
| Integration not in search | Files not installed correctly | Verify `/config/custom_components/solar_of_things/` exists |

### Enable debug logging
Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.solar_of_things: debug
```
Restart HA, reproduce the problem, then check **Settings → System → Logs**.

---

## API Reference

This integration targets the same endpoints used by the Siseli web portal.

| Endpoint | Method | Purpose |
|---|---|---|
| `/apis/device/list` | POST | Discover all device IDs under a station |
| `/apis/deviceState/simple/attribute/keys/history/v1` | POST | Real-time time-series telemetry per device |
| `/apis/stationOverView/stateAttributeSummary/category/yearly` | POST | Monthly energy summary per station |

### Required request headers

| Header | Value |
|---|---|
| `IOT-Token` | Your authentication token |
| `IOT-Time-Zone` | Your timezone string (e.g. `Asia/Manila`) |
| `Content-Type` | `application/json; charset=utf-8` |
| `Origin` | `https://solar.siseli.com` |

> Reference client (Node.js CLI with same API behavior):
> [Hyllesen/solar-of-things-solar-usage](https://github.com/Hyllesen/solar-of-things-solar-usage)

---

## Contributing

Contributions are very welcome!

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes and add tests if applicable.
4. Run the validation workflow locally:
   ```bash
   python3 -m py_compile __init__.py api.py config_flow.py \
     const.py sensor.py number.py select.py switch.py
   ```
5. Commit with a clear message and open a Pull Request.

Bug reports and feature requests → use the **GitHub Issues** templates:
[github.com/conexocasa/solar-of-things-ha/issues/new/choose](https://github.com/conexocasa/solar-of-things-ha/issues/new/choose)

---

## Changelog

See **[CHANGELOG.md](CHANGELOG.md)** for a full history.

| Version | Highlights |
|---|---|
| **v2.3.0** | User ID/Account auth, working IOT-Open signing (AES+HMAC+MD5), correct login endpoint |
| **v2.2.0** | Email + Password auth, automatic token refresh 5 min before expiry, HA re-auth flow |
| **v2.1.1** | HACS metadata, GitHub Actions CI/CD, issue templates, release script |
| **v2.1.0** | Station-based device auto-discovery (`/apis/device/list`) |
| **v2.0.0** | Control entities (battery limits, operating modes, grid switches) |
| **v1.0.0** | Initial release — monitoring sensors, config flow, multi-station |

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## Disclaimer

This is an **unofficial** community integration and is not affiliated with,
endorsed by, or supported by Siseli or Solar of Things.
Use at your own risk. The API may change without notice.

---

<p align="center">
  Made with ☀️ for the Home Assistant community<br>
  <a href="https://github.com/conexocasa/solar-of-things-ha/issues">Report a Bug</a> ·
  <a href="https://github.com/conexocasa/solar-of-things-ha/issues">Request a Feature</a> ·
  <a href="https://community.home-assistant.io">HA Community Forum</a>
</p>
