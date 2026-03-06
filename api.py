"""API client for Solar of Things (solar.siseli.com).

Authentication strategy
─────────────────────────────────────────────────────────────────────────────
The Siseli portal uses a dual-token system discovered via JS bundle analysis:

  • POST /login/account          → accessToken + refreshToken + expiry timestamps
  • POST /login/refresh/access/token → new accessToken (+ new refreshToken) using
                                        the current refreshToken

accessToken  = the "IOT-Token" HTTP header value; short-lived (hours/days)
refreshToken = long-lived; used only to mint a new accessToken

This class supports three auth modes, tried in priority order:

  1. Email + password  (recommended)
     • Call login() at startup → stores both tokens in memory.
     • _ensure_token_valid() checks expiry before every API call and proactively
       refreshes (TOKEN_REFRESH_LEAD_SECONDS = 5 min before expiry, matching the
       portal JS behaviour).
     • If refresh fails, raises TokenExpiredError so the HA integration can
       trigger a re-auth flow.

  2. Token-pair (accessToken + refreshToken) without password
     • User pastes both tokens from DevTools.
     • Same proactive-refresh logic; re-auth needed when refreshToken expires.

  3. Legacy IOT-token only (backwards compatibility)
     • No refresh possible; raises TokenExpiredError on 401 so HA can prompt
       the user to re-enter a fresh token.

Usage in Home Assistant
─────────────────────────────────────────────────────────────────────────────
  api = SolarOfThingsAPI(
      email="user@example.com",
      password="secret",          # or omit and pass iot_token=
      time_zone="Asia/Manila",
      on_token_refreshed=_save_tokens_callback,
  )
  await hass.async_add_executor_job(api.login)
  data = await hass.async_add_executor_job(api.fetch_latest_data, device_id)
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

import requests

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]

from .const import (
    API_BASE_URL,
    API_LOGIN,
    API_REFRESH_TOKEN as API_REFRESH_TOKEN_ENDPOINT,
    API_TIME_SERIES,
    API_MONTHLY_SUMMARY,
    API_DEVICE_LIST,
    API_SETTINGS_GET,
    API_SETTINGS_SET,
    TOKEN_REFRESH_LEAD_SECONDS,
)

_LOGGER = logging.getLogger(__name__)

_DEFAULT_TZ = "Asia/Manila"


# ──────────────────────────────────────────────────────────────────────────────
# Custom exceptions
# ──────────────────────────────────────────────────────────────────────────────

class TokenExpiredError(Exception):
    """Raised when the access token has expired and cannot be refreshed.

    The HA integration should catch this and call
    config_entry.async_start_reauth() so the user can re-enter credentials.
    """


class AuthenticationError(Exception):
    """Raised when login credentials are rejected by the server."""


# ──────────────────────────────────────────────────────────────────────────────
# Helper: parse Siseli ISO expiry strings safely
# ──────────────────────────────────────────────────────────────────────────────

def _parse_expiry(value: str | None) -> datetime | None:
    """Return an aware UTC datetime from an ISO-8601 string, or None."""
    if not value:
        return None
    try:
        # Python 3.7+ fromisoformat doesn't handle trailing 'Z'
        cleaned = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Main API client
# ──────────────────────────────────────────────────────────────────────────────

class SolarOfThingsAPI:
    """Solar of Things API wrapper with automatic token refresh.

    Parameters
    ----------
    email:              Siseli portal login e-mail (preferred auth method).
    password:           Siseli portal password.
    iot_token:          Legacy/manual IOT-Token (used when email/password absent).
    refresh_token:      Stored refresh token (persisted between HA restarts).
    access_token_expires: ISO-8601 string of current access-token expiry.
    refresh_token_expires: ISO-8601 string of current refresh-token expiry.
    time_zone:          IOT-Time-Zone header value.
    on_token_refreshed: Optional callback(access_token, refresh_token,
                        access_expires_iso, refresh_expires_iso) called after
                        every successful token refresh so the HA entry can
                        persist the new tokens without restarting.
    """

    def __init__(
        self,
        *,
        email: str | None = None,
        password: str | None = None,
        iot_token: str | None = None,
        refresh_token: str | None = None,
        access_token_expires: str | None = None,
        refresh_token_expires: str | None = None,
        time_zone: str | None = None,
        on_token_refreshed: Callable[[str, str, str, str], None] | None = None,
    ) -> None:
        self._email = email
        self._password = password
        self._time_zone = time_zone or _DEFAULT_TZ
        self._on_token_refreshed = on_token_refreshed

        # Token state
        self._access_token: str = iot_token or ""
        self._refresh_token: str = refresh_token or ""
        self._access_expires: datetime | None = _parse_expiry(access_token_expires)
        self._refresh_expires: datetime | None = _parse_expiry(refresh_token_expires)

        # Thread-safety for concurrent refresh calls
        self._refresh_lock = threading.Lock()

        # Determine auth mode
        if email and password:
            self._auth_mode = "password"
        elif iot_token and refresh_token:
            self._auth_mode = "token_pair"
        elif iot_token:
            self._auth_mode = "legacy"
        else:
            raise ValueError("Provide either (email + password) or iot_token.")

        # HTTP session (headers updated after every token refresh)
        self.session = requests.Session()
        self._apply_token_headers()

    # ─── Session headers ───────────────────────────────────────────────────────

    def _apply_token_headers(self) -> None:
        """Write the current access token into the session headers."""
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "IOT-Token": self._access_token,
                "IOT-Time-Zone": self._time_zone,
                "Origin": "https://solar.siseli.com",
                "Referer": "https://solar.siseli.com/",
                "User-Agent": (
                    "HomeAssistant-SolarOfThings/2.2.0 "
                    "(+https://github.com/conexocasa/solar-of-things-ha)"
                ),
            }
        )

    # ─── Public auth helpers ───────────────────────────────────────────────────

    def login(self) -> None:
        """Authenticate with email + password and store the resulting tokens.

        Raises AuthenticationError on bad credentials, or requests.RequestException
        on network failure.  Safe to call from a background thread.
        """
        if self._auth_mode not in ("password",):
            raise RuntimeError("login() requires email + password auth mode.")

        _LOGGER.debug("SolarOfThings: logging in as %s", self._email)

        payload = {
            "email": self._email,
            "password": self._password,
            "loginType": "email",
        }

        # Auth endpoints must NOT carry the IOT-Token header yet
        resp = requests.post(
            f"{API_BASE_URL}{API_LOGIN}",
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Origin": "https://solar.siseli.com",
                "Referer": "https://solar.siseli.com/",
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") not in (0, None, "0"):
            msg = data.get("message") or data.get("msg") or str(data)
            raise AuthenticationError(f"Login failed: {msg}")

        self._store_tokens(data.get("data") or data)

    def refresh_access_token(self) -> None:
        """Use the stored refresh token to obtain a new access token.

        Raises TokenExpiredError if the refresh token is also expired or invalid.
        """
        if not self._refresh_token:
            raise TokenExpiredError("No refresh token available.")

        _LOGGER.debug("SolarOfThings: refreshing access token")

        resp = requests.post(
            f"{API_BASE_URL}{API_REFRESH_TOKEN_ENDPOINT}",
            json={"refreshToken": self._refresh_token},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json; charset=utf-8",
                "Origin": "https://solar.siseli.com",
                "Referer": "https://solar.siseli.com/",
            },
            timeout=30,
        )

        if resp.status_code in (401, 403):
            raise TokenExpiredError("Refresh token rejected by server (expired or invalid).")

        resp.raise_for_status()
        data = resp.json()

        if data.get("code") not in (0, None, "0"):
            raise TokenExpiredError(
                f"Refresh failed: code={data.get('code')} message={data.get('message')}"
            )

        self._store_tokens(data.get("data") or data)

    # ─── Internal token management ─────────────────────────────────────────────

    def _store_tokens(self, payload: dict[str, Any]) -> None:
        """Extract tokens from a login/refresh response payload and persist them."""
        access = (
            payload.get("accessToken")
            or payload.get("iotToken")
            or payload.get("token")
            or ""
        )
        refresh = payload.get("refreshToken") or ""
        access_exp = (
            payload.get("accessTokenWillExpiredAt")
            or payload.get("accessTokenExpiredAt")
            or ""
        )
        refresh_exp = (
            payload.get("refreshTokenWillExpiredAt")
            or payload.get("refreshTokenExpiredAt")
            or ""
        )

        if not access:
            raise AuthenticationError(
                f"Login/refresh response did not contain an access token. "
                f"Keys received: {list(payload.keys())}"
            )

        self._access_token = access
        self._refresh_token = refresh
        self._access_expires = _parse_expiry(access_exp)
        self._refresh_expires = _parse_expiry(refresh_exp)

        # Update session header immediately
        self._apply_token_headers()

        _LOGGER.debug(
            "SolarOfThings: token updated, expires=%s",
            self._access_expires.isoformat() if self._access_expires else "unknown",
        )

        # Notify the HA integration so it can persist the new token state
        if self._on_token_refreshed:
            try:
                self._on_token_refreshed(
                    self._access_token,
                    self._refresh_token,
                    self._access_expires.isoformat() if self._access_expires else "",
                    self._refresh_expires.isoformat() if self._refresh_expires else "",
                )
            except Exception as cb_err:  # pragma: no cover
                _LOGGER.warning("Token-refresh callback raised: %s", cb_err)

    def _token_needs_refresh(self) -> bool:
        """Return True if the access token is absent or about to expire."""
        if not self._access_token:
            return True
        if self._access_expires is None:
            # Unknown expiry: only refresh if we already have a refresh token
            return bool(self._refresh_token)
        lead = timedelta(seconds=TOKEN_REFRESH_LEAD_SECONDS)
        return datetime.now(timezone.utc) >= (self._access_expires - lead)

    def _ensure_token_valid(self) -> None:
        """Proactively refresh the access token if needed.

        Thread-safe: uses a lock so parallel coordinator updates don't
        trigger multiple simultaneous refresh calls.

        Raises TokenExpiredError when all refresh strategies are exhausted.
        """
        if not self._token_needs_refresh():
            return

        with self._refresh_lock:
            # Double-check inside the lock (another thread may have refreshed)
            if not self._token_needs_refresh():
                return

            _LOGGER.info("SolarOfThings: access token expiring; attempting refresh")

            # Strategy 1: use refresh token
            if self._refresh_token:
                try:
                    self.refresh_access_token()
                    return
                except TokenExpiredError:
                    _LOGGER.warning(
                        "SolarOfThings: refresh token expired/invalid; "
                        "attempting re-login"
                    )
                except Exception as err:
                    _LOGGER.error("SolarOfThings: token refresh request failed: %s", err)

            # Strategy 2: re-login with stored credentials
            if self._auth_mode == "password" and self._email and self._password:
                try:
                    self.login()
                    return
                except AuthenticationError as err:
                    raise TokenExpiredError(
                        f"Re-login failed (credentials rejected): {err}"
                    ) from err
                except Exception as err:
                    raise TokenExpiredError(
                        f"Re-login failed (network error): {err}"
                    ) from err

            # Strategy 3: nothing left — tell HA to trigger re-auth
            raise TokenExpiredError(
                "Access token expired and no refresh strategy succeeded. "
                "Please re-authenticate in Home Assistant."
            )

    # ─── Internal HTTP helper ──────────────────────────────────────────────────

    def _post(self, path: str, payload: dict[str, Any], *, timeout: int = 30) -> dict[str, Any]:
        """Perform a POST, automatically refreshing the token on 401.

        On second 401 (after refresh) raises TokenExpiredError.
        """
        self._ensure_token_valid()

        resp = self.session.post(f"{API_BASE_URL}{path}", json=payload, timeout=timeout)

        if resp.status_code == 401:
            _LOGGER.warning("SolarOfThings: received 401; forcing token refresh")
            # Force an immediate refresh even if _token_needs_refresh() is False
            self._access_expires = None
            self._ensure_token_valid()
            resp = self.session.post(f"{API_BASE_URL}{path}", json=payload, timeout=timeout)

        resp.raise_for_status()
        return resp.json()

    # ─── Public properties (for persistence in HA config entry) ───────────────

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @property
    def access_token_expires_iso(self) -> str:
        return self._access_expires.isoformat() if self._access_expires else ""

    @property
    def refresh_token_expires_iso(self) -> str:
        return self._refresh_expires.isoformat() if self._refresh_expires else ""

    # ─── Time helpers ──────────────────────────────────────────────────────────

    def _now(self) -> datetime:
        if ZoneInfo:
            try:
                return datetime.now(tz=ZoneInfo(self._time_zone))
            except Exception:
                return datetime.now()
        return datetime.now()

    def _format_time(self, dt: datetime) -> str:
        if ZoneInfo:
            try:
                dt = dt.astimezone(ZoneInfo(self._time_zone))
            except Exception:
                pass
        return dt.replace(microsecond=0).isoformat()

    # ─── Station → device listing ──────────────────────────────────────────────

    def list_devices(self, station_id: str, page_size: int = 50) -> list[dict[str, Any]]:
        """Return all devices under a station (paginated)."""
        devices: list[dict[str, Any]] = []
        page = 1
        total: int | None = None

        while True:
            data = self._post(
                API_DEVICE_LIST,
                {"page": page, "count": page_size, "stationId": station_id},
            )

            if data.get("code") not in (0, None):
                raise RuntimeError(
                    f"Device list error code={data.get('code')} "
                    f"message={data.get('message')}"
                )

            d = data.get("data") or {}
            total = d.get("total", total)
            batch = d.get("list") or []
            if not isinstance(batch, list):
                batch = []

            devices.extend(batch)

            if total is None:
                if len(batch) < page_size:
                    break
            else:
                if len(devices) >= int(total):
                    break
            if not batch:
                break
            page += 1

        return devices

    # ─── Time-series (per device) ──────────────────────────────────────────────

    def fetch_latest_data(self, device_id: str) -> dict[str, Any]:
        """Fetch the latest readings for a device (last 1 hour)."""
        end_time = self._now()
        start_time = end_time - timedelta(hours=1)

        keys = [
            "pvInputPower",
            "acOutputActivePower",
            "batteryDischargeCurrent",
            "batteryChargingCurrent",
            "batteryVoltage",
            "feedInPower",
            "batterySOC",
        ]

        data = self._post(
            API_TIME_SERIES,
            {
                "deviceId": device_id,
                "count": 2000,
                "page": 1,
                "fromTime": self._format_time(start_time),
                "toTime": self._format_time(end_time),
                "orderByTimeAsc": True,
                "keys": keys,
            },
        )

        if data.get("code") not in (0, None):
            raise RuntimeError(
                f"Timeseries error code={data.get('code')} "
                f"message={data.get('message')}"
            )

        payload_data = (data.get("data") or {}).get("payload") or {}
        fields = payload_data.get("fields") or {}

        latest_values: dict[str, Any] = {}
        for key, arr in fields.items():
            if isinstance(arr, list) and arr:
                latest_values[key] = arr[-1]

        # Unit normalisation: acOutputActivePower is kW in API → W
        if "acOutputActivePower" in latest_values:
            try:
                latest_values["acOutputActivePower"] = (
                    float(latest_values["acOutputActivePower"]) * 1000.0
                )
            except Exception:
                pass

        # Derived values
        voltage = float(latest_values.get("batteryVoltage") or 0)
        discharge = float(latest_values.get("batteryDischargeCurrent") or 0)
        charge = float(latest_values.get("batteryChargingCurrent") or 0)
        latest_values["batteryPower"] = (discharge - charge) * voltage

        pv_power = float(latest_values.get("pvInputPower") or 0)
        ac_output = float(latest_values.get("acOutputActivePower") or 0)
        feed_in = float(latest_values.get("feedInPower") or 0)
        battery_power = float(latest_values.get("batteryPower") or 0)

        latest_values["gridPower"] = max(0.0, ac_output - pv_power + battery_power + feed_in)
        latest_values["loadPower"] = ac_output

        return latest_values

    # ─── Monthly summary (station) ─────────────────────────────────────────────

    def fetch_monthly_summary(self, station_id: str) -> dict[str, Any]:
        """Fetch monthly PV summary for the current month."""
        now = self._now()
        year = now.year
        month_key = f"{year}-{str(now.month).zfill(2)}"

        self._ensure_token_valid()
        resp = self.session.post(
            f"{API_BASE_URL}{API_MONTHLY_SUMMARY}"
            f"?stationId={station_id}&summaryCategoryKey=pvInverterElectricityQuantityClass",
            json={"time": str(year)},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") not in (0, None):
            raise RuntimeError(
                f"Monthly summary error code={data.get('code')} "
                f"message={data.get('message')}"
            )

        props = (((data.get("data") or {}).get("properties")) or [])
        out: dict[str, Any] = {}

        for prop in props:
            prop_key = ((prop.get("property") or {}).get("key"))
            if not prop_key:
                continue
            for tp in prop.get("timePoints") or []:
                if tp.get("time") == month_key and tp.get("isRealValue"):
                    out[prop_key] = tp.get("value")

        if "pvGeneratedEnergy" in out:
            return {"monthly_pv_generated": float(out.get("pvGeneratedEnergy") or 0)}

        return {}

    # ─── Settings / control (per device) ──────────────────────────────────────

    def fetch_settings(self, device_id: str) -> dict[str, Any]:
        """Fetch current device settings."""
        try:
            data = self._post(API_SETTINGS_GET, {"deviceId": device_id})
            settings: dict[str, Any] = {}
            if "data" in data:
                sd = data["data"]
                settings["batteryChargeLimit"] = sd.get("batteryChargeLimit", 100)
                settings["batteryDischargeLimit"] = sd.get("batteryDischargeLimit", 10)
                settings["gridChargeLimit"] = sd.get("gridChargeLimit", 0)
                settings["operatingMode"] = sd.get("operatingMode", "Self-Use")
                settings["batteryPriority"] = sd.get("batteryPriority", "Solar First")
                settings["gridChargingEnabled"] = sd.get("gridChargingEnabled", False)
                settings["gridFeedInEnabled"] = sd.get("gridFeedInEnabled", True)
                settings["backupModeEnabled"] = sd.get("backupModeEnabled", False)
            return settings
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching settings for device %s: %s", device_id, err)
            return {}

    def _update_setting(self, device_id: str, setting_key: str, value: Any) -> bool:
        try:
            data = self._post(
                API_SETTINGS_SET,
                {"deviceId": device_id, "settings": {setting_key: value}},
            )
            if data.get("success") is True or data.get("code") in (0, None):
                _LOGGER.info("Updated %s=%s for device %s", setting_key, value, device_id)
                return True
            _LOGGER.error("Failed to update %s for device %s: %s", setting_key, device_id, data)
            return False
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error updating %s for device %s: %s", setting_key, device_id, err)
            return False

    def set_battery_charge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "batteryChargeLimit", limit)

    def set_battery_discharge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "batteryDischargeLimit", limit)

    def set_grid_charge_limit(self, device_id: str, limit: int) -> bool:
        return self._update_setting(device_id, "gridChargeLimit", limit)

    def set_operating_mode(self, device_id: str, mode: str) -> bool:
        return self._update_setting(device_id, "operatingMode", mode)

    def set_battery_priority(self, device_id: str, priority: str) -> bool:
        return self._update_setting(device_id, "batteryPriority", priority)

    def set_grid_charging(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "gridChargingEnabled", enabled)

    def set_grid_feed_in(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "gridFeedInEnabled", enabled)

    def set_backup_mode(self, device_id: str, enabled: bool) -> bool:
        return self._update_setting(device_id, "backupModeEnabled", enabled)

    # ─── Validation ───────────────────────────────────────────────────────────

    def test_connection(self, station_id: str) -> bool:
        """Validate credentials + station by listing devices and querying telemetry."""
        try:
            devices = self.list_devices(station_id)
            if not devices:
                return False
            device_id = str((devices[0].get("id") or ""))
            if not device_id:
                return False
            self.fetch_latest_data(device_id)
            return True
        except TokenExpiredError:
            raise
        except Exception as err:
            _LOGGER.error("Connection test failed: %s", err)
            return False
