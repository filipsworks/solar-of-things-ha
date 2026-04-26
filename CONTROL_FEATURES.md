# Solar System Control Features

## Overview

The Solar of Things integration now supports **full control** of your solar system settings through Home Assistant. You can adjust operating modes and battery priority directly from your dashboard or automations.

---

## 🎛️ Control Entities

### Select Entities (Dropdowns)

#### 1. **Operating Mode**
- **Type**: Select
- **Options**:
  - **Self-Use**: Maximize self-consumption
  - **Time-of-Use**: Optimize for electricity rates
  - **Backup**: Prioritize battery reserve
  - **Grid-Tie**: Prioritize grid export
  - **Off-Grid**: Independent operation
- **Entity**: `select.solar_station_xxxxx_operating_mode`

```yaml
# Switch to Time-of-Use mode
service: select.select_option
target:
  entity_id: select.solar_station_xxxxx_operating_mode
data:
  option: "Time-of-Use"
```

#### 2. **Battery Priority**
- **Type**: Select
- **Options**:
  - **Solar First**: Use solar before battery
  - **Battery First**: Use battery before solar
  - **Grid First**: Use grid before battery/solar
- **Entity**: `select.solar_station_xxxxx_battery_priority`

```yaml
# Prioritize solar energy
service: select.select_option
target:
  entity_id: select.solar_station_xxxxx_battery_priority
data:
  option: "Solar First"
```

---

## 🤖 Automation Examples

### 1. Dynamic Operating Mode

Switch modes based on electricity prices:

```yaml
automation:
  - alias: "Solar: Peak Price Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        above: 0.25  # High price threshold
    action:
      - service: select.select_action
        target:
          entity_id: select.solar_station_xxxxx_operating_mode
        data:
          option: "Time-of-Use"
      
      # Maximize battery usage during peak
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_battery_priority
        data:
          option: "Battery First"

  - alias: "Solar: Off-Peak Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        below: 0.10  # Low price threshold
    action:
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_operating_mode
        data:
          option: "Self-Use"
      
      # Prioritize solar during off-peak
      - service: select.select_option
        target:
          entity_id: select.solar_station_xxxxx_battery_priority
        data:
          option: "Solar First"
```

---

## 📊 Dashboard Examples

### Control Panel Card

```yaml
type: entities
title: Solar System Controls
entities:
  - entity: select.solar_station_xxxxx_operating_mode
    name: Operating Mode
  
  - entity: select.solar_station_xxxxx_battery_priority
    name: Battery Priority
```

### Battery Management Card

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.solar_station_xxx_battery_state_of_charge
    name: Battery Level
    min: 0
    max: 100
    needle: true
    segments:
      - from: 0
        color: "#db4437"
      - from: 20
        color: "#ff9800"
      - from: 50
        color: "#ffc107"
      - from: 80
        color: "#0f9d58"
```

### Quick Actions Card

```yaml
type: horizontal-stack
cards:
  - type: button
    name: Self-Use Mode
    icon: mdi:solar-power
    tap_action:
      action: call-service
      service: select.select_option
      target:
        entity_id: select.solar_station_xxxxx_operating_mode
      data:
        option: "Self-Use"
```

---

## ⚠️ Important Notes

### API Limitations

**Note**: The control API endpoints (`/api/device/settings/v1` and `/api/device/settings/update/v1`) are **assumed endpoints** based on common IoT patterns. You will need to:

1. **Verify** these endpoints exist in the actual Solar of Things API
2. **Test** with your device to confirm functionality
3. **Adjust** the API implementation based on actual response formats

### Finding Actual Control Endpoints

To find the real control endpoints:

1. Open https://solar.siseli.com
2. Go to settings/control page on the web interface
3. Open browser Developer Tools (F12) → Network tab
4. Make a settings change (e.g., adjust battery limit)
5. Find the API request in the Network tab
6. Note the:
   - Endpoint URL
   - Request method (POST/PUT)
   - Payload format
   - Response format

Then update `api.py` with the correct endpoints and formats.

### Safety Considerations

⚠️ **Always test control features carefully:**

- Start with non-critical settings
- Monitor system behavior after changes
- Don't exceed manufacturer specifications
- Have manual override capability

### Permissions

Some settings may require:
- Admin/installer level access
- Special authentication
- Firmware version requirements

Check your Solar of Things account permissions.

---

## 🔧 Troubleshooting

### Settings Not Changing

1. **Check logs**: Settings → System → Logs
2. **Verify device_id**: Must be correct for control operations
3. **Test API**: Try changing settings on solar.siseli.com web interface
4. **Check permissions**: Account may not have control access

### Control Entities Not Appearing

1. **Check device_id**: Required for control entities
2. **Restart HA**: After integration update
3. **Check coordinator**: Ensure settings are being fetched
4. **Review logs**: Look for error messages

### Values Not Updating

- Wait 5 minutes for next coordinator refresh
- Or restart Home Assistant to force update
- Check if web interface shows updated values

---

## 📝 Customization

You can customize available options by editing the integration files:

**Operating Modes** (`select.py`):
```python
OPERATING_MODES = [
    "Self-Use",
    "Time-of-Use",
    "Backup",
    "Grid-Tie",
    "Off-Grid",
    # Add more modes here
]
```

**Battery Priority** (`select.py`):
```python
BATTERY_PRIORITY_MODES = [
    "Solar First",
    "Battery First",
    "Grid First",
    # Add more priorities here
]
```
