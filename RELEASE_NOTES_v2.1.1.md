# Solar of Things — Home Assistant Integration
## Release v2.1.1

> **Tag:** `v2.1.1` | **Branch:** `main` | **Date:** 2026-03-05
> **Repository:** https://github.com/conexocasa/solar-of-things-ha
> **Portal:** https://solar.siseli.com

---

## What's new in v2.1.1

This is a **housekeeping and packaging release**. It adds HACS metadata
and a GitHub PR template so that:

1. HACS can install directly from the release ZIP asset.
2. A future HACS default-repository submission has a consistent PR
   template to work from.

### Added
- **`.github/PULL_REQUEST_TEMPLATE.md`**
  Standardised pull-request template covering the HACS default
  submission checklist (integration name, domain, validation steps,
  documentation links).

### Changed
- **`hacs.json`** — four updates:
  - Added all platforms: `sensor`, `number`, `select`, `switch`
  - `zip_release: true` — tells HACS to fetch the release ZIP asset
    instead of cloning the repo
  - `filename: solar-of-things-ha.zip` — exact asset name HACS looks
    for on the GitHub Release page
  - `homeassistant: "2023.1.0"` — minimum supported HA version
- **`manifest.json`** — version bumped from `2.1.0` → `2.1.1`

---

## Complete Changelog

### v2.1.1 (2026-03-05)
- Added HACS release packaging support (`zip_release`, `filename`)
- Added GitHub PR template (`.github/PULL_REQUEST_TEMPLATE.md`)
- Bumped `manifest.json` version to `2.1.1`

### v2.1.0 (2026-02-26)
- **Station-based device auto-discovery** via `POST /apis/device/list`
  — no need to manually enter every `deviceId`
- Config flow: `station_id` required; `device_id` optional
  (blank = all devices, set = single device only)
- Updated documentation/issue-tracker URLs in `manifest.json`

### v2.0.0 (2024-02-10)
- **8 control entities** added:
  - `Number` — Battery Charge Limit (0–100 %)
  - `Number` — Battery Discharge Limit (0–100 %)
  - `Number` — Grid Charge Power Limit (0–5 000 W)
  - `Select` — Operating Mode (Self-Use / TOU / Backup / Grid-Tie / Off-Grid)
  - `Select` — Battery Priority (Solar First / Battery First / Grid First)
  - `Switch` — Grid Charging
  - `Switch` — Grid Feed-In
  - `Switch` — Backup Mode
- Settings API integration (read + update device configuration)
- Comprehensive control documentation (`CONTROL_FEATURES.md`)
- 15+ automation examples

### v1.0.0 (2024-02-10)
- Initial release
- Real-time sensors: PV power, AC output, battery (current/voltage/SOC/power),
  grid feed-in/import, load power
- Monthly PV generation via station summary API
- 5-minute polling with Home Assistant coordinator pattern
- Multi-station support through multiple config entries
- Energy Dashboard compatible
- IOT-Token authentication

---

## Installation

### Option A — HACS Custom Repository (recommended)

```
1. Open HACS → Integrations
2. Click ⋮ → Custom repositories
3. Add:  https://github.com/conexocasa/solar-of-things-ha
         Category: Integration
4. Click "Solar of Things" → Install
5. Restart Home Assistant
```

### Option B — Release ZIP (manual)

```
1. Download solar-of-things-ha.zip from this release (see Assets below)
2. Unzip — you will see:
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
3. Copy custom_components/solar_of_things/ →
       /config/custom_components/solar_of_things/
4. Restart Home Assistant
```

### Option C — Git clone (developers)

```bash
cd /config/custom_components
git clone https://github.com/conexocasa/solar-of-things-ha.git solar_of_things_repo
cp -r solar_of_things_repo/custom_components/solar_of_things ./solar_of_things
# Restart Home Assistant
```

---

## Upgrading from a previous version

### From v2.1.0
No breaking changes. Replace files and restart.

```bash
# Manual upgrade
cp -r custom_components/solar_of_things /config/custom_components/
# Restart Home Assistant
```

Via HACS: HACS → Integrations → Solar of Things → Update → Restart.

### From v2.0.0 or v1.0.0
No breaking changes, but **re-configure the integration**:
- `station_id` is now **required** (was optional in v1/v2.0)
- `device_id` is now **optional** (leave blank for auto-discovery)

Steps:
1. Settings → Devices & Services → Solar of Things → Delete
2. Restart Home Assistant
3. Settings → Devices & Services → + Add Integration → Solar of Things
4. Enter IOT Token + Station ID (Device ID optional)

---

## Configuration

### Getting your credentials

| Credential | Where to find it | Format |
|------------|-----------------|--------|
| IOT Token | DevTools → Network → any `/apis/` request → Request Headers → `IOT-Token` | String |
| Station ID | DevTools → Network → request payload → `stationId` | 18 digits |
| Device ID | DevTools → Network → request payload → `deviceId` | 18 digits (optional) |

1. Log in to https://solar.siseli.com
2. Open Developer Tools (F12)
3. Go to the **Network** tab and refresh the page
4. Click any `/apis/` request and copy the values above

### Config flow fields

| Field | Required | Description |
|-------|----------|-------------|
| IOT Token | ✅ | Authentication token from the Siseli portal |
| Station ID | ✅ | 18-digit station identifier; used to discover all devices |
| Device ID | ☑ Optional | 18-digit device ID; set to restrict entities to one device |
| Time Zone | ☑ Optional | Sent as `IOT-Time-Zone` header (default: `Asia/Manila`) |

---

## Available entities (per device)

### Sensors (updated every 5 minutes)

| Entity | Unit | Notes |
|--------|------|-------|
| PV Input Power | W | DC solar panel power |
| AC Output Power | W | AC inverter output |
| Battery Discharge Current | A | — |
| Battery Charging Current | A | — |
| Battery Voltage | V | — |
| Battery Power | W | Calculated: (discharge − charge) × voltage |
| Battery State of Charge | % | May be `null` on some devices |
| Grid Feed-in Power | W | Export to grid |
| Grid Import Power | W | Import from grid (calculated) |
| Load Power | W | Total home load |

### Monthly sensors (station level, updated every 30 minutes)

| Entity | Unit | Notes |
|--------|------|-------|
| Monthly PV Generated | kWh | Current calendar month |

### Control entities

| Entity | Type | Range / Options |
|--------|------|----------------|
| Battery Charge Limit | Number | 0–100 % |
| Battery Discharge Limit | Number | 0–100 % |
| Grid Charge Power Limit | Number | 0–5 000 W |
| Operating Mode | Select | Self-Use, Time-of-Use, Backup, Grid-Tie, Off-Grid |
| Battery Priority | Select | Solar First, Battery First, Grid First |
| Grid Charging | Switch | On / Off |
| Grid Feed-In | Switch | On / Off |
| Backup Mode | Switch | On / Off |

> **Note:** Control endpoints may vary by device model and firmware.
> If sliders/switches have no effect, check the Troubleshooting guide.

---

## API endpoints used

This integration uses the same endpoints as the Siseli web portal
and the reference client implementation:

| Purpose | Method | Endpoint |
|---------|--------|----------|
| Station → device list | POST | `/apis/device/list` |
| Time-series telemetry | POST | `/apis/deviceState/simple/attribute/keys/history/v1` |
| Monthly station summary | POST | `/apis/stationOverView/stateAttributeSummary/category/yearly` |

Reference client: https://github.com/Hyllesen/solar-of-things-solar-usage

---

## Troubleshooting

See the full guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Quick reference

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Cannot connect" in config flow | Expired / wrong IOT-Token | Grab a fresh token from the portal network tab |
| 401 / 403 in HA logs | Expired token or wrong timezone header | Refresh token; set correct Time Zone |
| No devices created | Wrong Station ID or empty device list | Verify Station ID; check logs for `/apis/device/list` response |
| Entities "Unavailable" | Coordinator update failed | Check HA logs; verify HA can reach `solar.siseli.com` |
| Sensors show "Unknown" | API returns `null` for that field | Normal for some sensors (e.g. battery SOC on batteryless systems) |
| Control entities do nothing | Settings endpoints vary by firmware | Capture the portal network request and compare to integration endpoints |

Enable debug logs by adding to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.solar_of_things: debug
```

---

## Release assets

| File | Description |
|------|-------------|
| `solar-of-things-ha.zip` | HACS-ready ZIP (`custom_components/solar_of_things/…`) |
| Source code (zip) | Full repository snapshot |
| Source code (tar.gz) | Full repository snapshot |

---

## Links

| Resource | URL |
|----------|-----|
| Repository | https://github.com/conexocasa/solar-of-things-ha |
| Issues | https://github.com/conexocasa/solar-of-things-ha/issues |
| Siseli portal | https://solar.siseli.com |
| API reference client | https://github.com/Hyllesen/solar-of-things-solar-usage |
| HACS | https://hacs.xyz |
| Home Assistant | https://www.home-assistant.io |

---

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed
by Siseli / Solar of Things. Use at your own risk.
