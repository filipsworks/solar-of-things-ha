"""Constants for the Solar of Things integration."""

DOMAIN = "solar_of_things"

# ─── Configuration keys ────────────────────────────────────────────────────────
CONF_IOT_TOKEN = "iot_token"  # legacy / advanced manual entry
CONF_STATION_ID = "station_id"
CONF_DEVICE_ID = "device_id"
CONF_TIME_ZONE = "time_zone"

# Credential-based auth (preferred)
CONF_USER_ID = "user_id"  # Siseli account / user-ID login (not email)
CONF_PASSWORD = "password"

# Runtime-stored token state (written back to config entry)
CONF_REFRESH_TOKEN = "refresh_token"
CONF_ACCESS_TOKEN_EXPIRES = "access_token_expires"  # ISO-8601 string
CONF_REFRESH_TOKEN_EXPIRES = "refresh_token_expires"  # ISO-8601 string

# ─── API bases ─────────────────────────────────────────────────────────────────
# Both auth and data endpoints live on the production server solar.siseli.com.
# The portal JS bundle embeds both test/prod AppIDs; AppID rBrTRfAPXz is the
# one accepted by solar.siseli.com (confirmed by live API testing 2026-03-07).
API_BASE_URL = "https://solar.siseli.com"  # data endpoints
API_AUTH_BASE_URL = "https://solar.siseli.com"  # auth / login endpoints

# ─── Auth endpoints (discovered from portal JS bundle) ─────────────────────────
# The login endpoint requires IOT-Open-AppID signing (see api.py _sign_request).
API_LOGIN = "/apis/login/account"  # POST + signed headers
API_REFRESH_TOKEN = "/login/refresh/access/token"  # POST, no token needed

# ─── IOT Open Platform app credentials (embedded in portal umi.js) ────────────
# rBrTRfAPXz is the production AppID accepted by solar.siseli.com.
# JO4DAiNeys is the test AppID (accepted only by test.solar.siseli.com).
IOT_APP_ID = "rBrTRfAPXz"
IOT_APP_SECRET_ENC = "I4D0KRr2339z3pQ/at91V9BpFAOe54DaTafwSm6suIQ="

# ─── Data endpoints ────────────────────────────────────────────────────────────
API_TIME_SERIES = "/apis/deviceState/simple/attribute/keys/history/v1"
API_MONTHLY_SUMMARY = "/apis/stationOverView/stateAttributeSummary/category/yearly"
API_LATEST_STATE = "/apis/deviceState/simple/state/latest/v1"
# Remote device config endpoints (discovered 2026-03-07 from live API testing).
# These accept a plain IOT-Token header (no IOT-Open-Sign) and use the device ID
# as a query parameter.  Write sends one setting key+value per call.
API_SETTINGS_GET = "/apis/remote/device/configs/cache/get"  # ?deviceId=<id>
API_SETTINGS_SET = "/apis/remote/device/config/write"  # ?deviceId=<id>
API_DEVICE_LIST = "/apis/device/list"

# ─── Token refresh window ──────────────────────────────────────────────────────
# Refresh the access token this many seconds *before* its stated expiry.
# Mirrors the portal JS which refreshes when ≤300 s remain.
TOKEN_REFRESH_LEAD_SECONDS = 300  # 5 minutes

# ─── Sensor keys ───────────────────────────────────────────────────────────────
SENSOR_KEYS = [
    "pvInputPower",
    "acOutputActivePower",
    "batteryDischargeCurrent",
    "batteryChargingCurrent",
    "batteryVoltage",
    "feedInPower",
    "batteryPower",
    "batterySOC",
    "gridPower",
    "loadPower",
]

SENSOR_DEFINITIONS = {
    "pvInputPower": {
        "name": "PV Input Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:solar-power",
    },
    "acOutputActivePower": {
        "name": "AC Output Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:power-plug",
    },
    "batteryDischargeCurrent": {
        "name": "Battery Discharge Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-down",
    },
    "batteryChargingCurrent": {
        "name": "Battery Charging Current",
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-up",
    },
    "batteryVoltage": {
        "name": "Battery Voltage",
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery",
    },
    "batteryPower": {
        "name": "Battery Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:battery-charging",
    },
    "batterySOC": {
        "name": "Battery State of Charge",
        "unit": "%",
        "device_class": "battery",
        "icon": "mdi:battery",
    },
    "feedInPower": {
        "name": "Grid Feed-in Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-export",
    },
    "gridPower": {
        "name": "Grid Import Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:transmission-tower-import",
    },
    "loadPower": {
        "name": "Load Power",
        "unit": "W",
        "device_class": "power",
        "icon": "mdi:home-lightning-bolt",
    },
    # Monthly summary sensors
    "monthly_pv_generated": {
        "name": "Monthly PV Generated",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:solar-power",
    },
    "monthly_grid_import": {
        "name": "Monthly Grid Import",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:transmission-tower-import",
    },
    "monthly_total_consumption": {
        "name": "Monthly Total Consumption",
        "unit": "kWh",
        "device_class": "energy",
        "icon": "mdi:home-lightning-bolt",
    },
    "monthly_solar_percentage": {
        "name": "Monthly Solar Coverage",
        "unit": "%",
        "icon": "mdi:percent",
    },
}

# Operating-mode select maps HA option strings to integer values
OUTPUT_MODE_MAP: dict[str, int] = {
    "Solar First (SUB)": 0,
    "Solar+Battery First (SBU)": 1,
    "Solar+Battery+Grid (SUF)": 2,
    "Power Export Control (PEC)": 3,
}
OUTPUT_MODE_REVERSE: dict[int, str] = {v: k for k, v in OUTPUT_MODE_MAP.items()}

# Charger-priority select
CHARGER_PRIORITY_MAP: dict[str, int] = {
    "Solar + Utility (CSO)": 0,
    "Solar First (SNU)": 1,
    "Solar Only (OSO)": 2,
    "Solar residual (SOR)": 3,
}
CHARGER_PRIORITY_REVERSE: dict[int, str] = {
    v: k for k, v in CHARGER_PRIORITY_MAP.items()
}

# ─── Battery Type select map ──────────────────────────────────────────────────
BATTERY_TYPE_MAP: dict[str, int] = {
    "AGM": 0,
    "FLD": 1,
    "USE": 2,
    "LIA": 3,
    "PYL": 4,
    "TQF": 5,
    "GRO": 6,
    "LIB": 7,
    "LIC": 8,
    "FEL": 9,
}
BATTERY_TYPE_REVERSE: dict[int, str] = {v: k for k, v in BATTERY_TYPE_MAP.items()}

# ─── Output Frequency select map ──────────────────────────────────────────────
RATED_FREQUENCY_MAP: dict[str, int] = {
    "50 Hz": 50,
    "60 Hz": 60,
}
RATED_FREQUENCY_REVERSE: dict[int, str] = {v: k for k, v in RATED_FREQUENCY_MAP.items()}

# ─── Output Voltage select map ────────────────────────────────────────────────
RATED_VOLTAGE_MAP: dict[str, int] = {
    "220 V": 220,
    "230 V": 230,
    "240 V": 240,
}
RATED_VOLTAGE_REVERSE: dict[int, str] = {v: k for k, v in RATED_VOLTAGE_MAP.items()}

# ─── Grid Connection Type select map ──────────────────────────────────────────
GRID_CONNECTION_PROTOCOL_TYPE_MAP: dict[str, int] = {
    "195.5–253 VAC 49–51 Hz": 1,
    "184–264.5 VAC 47.5–51.5 Hz": 2,
    "184–264.5 VAC 57–62 Hz": 3,
    "170–264.5 VAC 47.5–53.5 Hz": 4,
    "100–280 VAC 47.5–53.5 Hz": 5,
}
GRID_CONNECTION_PROTOCOL_TYPE_REVERSE: dict[int, str] = {
    v: k for k, v in GRID_CONNECTION_PROTOCOL_TYPE_MAP.items()
}

# ─── Number setting definitions ───────────────────────────────────────────────
# Each entry: {"key": api_key, "name": display_name, "min": ..., "max": ...,
#              "step": ..., "unit": ..., "device_class": ..., "icon": ...}
NUMBER_SETTING_DEFINITIONS: list[dict] = [
    {
        "key": "bmsLockMachineBatteryCapacity",
        "name": "BMS Inverter Cutoff",
        "min": 5,
        "max": 95,
        "step": 5,
        "unit": "%",
        "icon": "mdi:battery-arrow-down",
    },
    {
        "key": "batteryConstantChargingVoltageSetting",
        "name": "Bulk Voltage",
        "min": 24,
        "max": 30,
        "step": 0.1,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-charging-high",
    },
    {
        "key": "batteryEqualizationIntervalSetting",
        "name": "Equalization Interval",
        "min": 0,
        "max": 90,
        "step": 1,
        "unit": "day",
        "icon": "mdi:calendar-repeat",
    },
    {
        "key": "batteryEqualizationTimeSetting",
        "name": "Equalization Time",
        "min": 5,
        "max": 900,
        "step": 5,
        "unit": "minute",
        "icon": "mdi:clock-outline",
    },
    {
        "key": "batteryEqualizationTimeoutSetting",
        "name": "Equalization Timeout",
        "min": 5,
        "max": 900,
        "step": 5,
        "unit": "minute",
        "icon": "mdi:timer-outline",
    },
    {
        "key": "batteryEqualizationVoltageSetting",
        "name": "Equalization Voltage",
        "min": 24,
        "max": 30,
        "step": 0.1,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-charging-high",
    },
    {
        "key": "batteryFloatChargingVoltageSetting",
        "name": "Float Voltage",
        "min": 24,
        "max": 30,
        "step": 0.1,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-heart",
    },
    {
        "key": "batteryRechargeVoltageSetting",
        "name": "SBU Utility Takeover",
        "min": 22,
        "max": 25.5,
        "step": 0.5,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:transmission-tower-import",
    },
    {
        "key": "batteryRedischargeVoltageSetting",
        "name": "SBU Battery Takeover",
        "min": 24,
        "max": 29,
        "step": 0.5,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-check",
    },
    {
        "key": "ctZeroPower",
        "name": "Main Input Power",
        "min": 0.01,
        "max": 0.5,
        "step": 0.01,
        "unit": "kW",
        "icon": "mdi:home-lightning-bolt",
    },
    {
        "key": "dischargeCurrentLimit",
        "name": "Maximum Battery Discharge Current",
        "min": 20,
        "max": 200,
        "step": 10,
        "unit": "A",
        "device_class": "current",
        "icon": "mdi:battery-arrow-down",
    },
    {
        "key": "inverterStartupBatteryCapacity",
        "name": "Battery Startup SOC",
        "min": 5,
        "max": 100,
        "step": 1,
        "unit": "%",
        "icon": "mdi:battery-check",
    },
    {
        "key": "lowBatteryAlarmVoltageSetting",
        "name": "Battery Low Alarm",
        "min": 20,
        "max": 27,
        "step": 0.1,
        "unit": "V",
        "device_class": "voltage",
        "icon": "mdi:battery-alert",
    },
    {
        "key": "restoreBatteryDischargingBatteryCapacity",
        "name": "Battery DC Takeover",
        "min": 5,
        "max": 100,
        "step": 5,
        "unit": "%",
        "icon": "mdi:battery-charging-high",
    },
    {
        "key": "restoreMainsChargingBatteryCapacity",
        "name": "Battery Mains Charging Takeover",
        "min": 5,
        "max": 95,
        "step": 5,
        "unit": "%",
        "icon": "mdi:battery-charging-high",
    },
]

# ─── Toggle setting definitions ───────────────────────────────────────────────
# Each entry: {"key": api_key, "name": display_name, "icon": ...}
TOGGLE_SETTING_DEFINITIONS: list[dict] = [
    {
        "key": "bmsFunctionEnableSetting",
        "name": "BMS Enabled",
        "icon": "mdi:battery-lock",
    },
    {
        "key": "batteryEqualizationModeEnableSetting",
        "name": "Equalization Enabled",
        "icon": "mdi:battery-heart-outline",
    },
    {
        "key": "backlightOn",
        "name": "LCD Backlight",
        "icon": "mdi:lightbulb",
    },
    {
        "key": "buzzerOn",
        "name": "Buzzer",
        "icon": "mdi:bell-alert",
    },
    {
        "key": "displayAutomaticallyReturnsToHomepage",
        "name": "LCD Auto Homepage",
        "icon": "mdi:view-dashboard",
    },
    {
        "key": "ecoMode",
        "name": "ECO Mode",
        "icon": "mdi:leaf",
    },
    {
        "key": "inputSourceDetectionPromptSound",
        "name": "Input Source Change Beep",
        "icon": "mdi:volume-source",
    },
    {
        "key": "overTemperatureAutomaticRestart",
        "name": "Overheat Restart",
        "icon": "mdi:thermometer-alert",
    },
    {
        "key": "overloadToBypassOperation",
        "name": "Overload Bypass",
        "icon": "mdi:arrow-right-bold-hexagon-outline",
    },
]
