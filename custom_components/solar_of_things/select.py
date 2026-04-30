"""Select platform for Solar of Things integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BATTERY_TYPE_MAP,
    BATTERY_TYPE_REVERSE,
    CHARGER_PRIORITY_MAP,
    CHARGER_PRIORITY_REVERSE,
    DOMAIN,
    GRID_CONNECTION_PROTOCOL_TYPE_MAP,
    GRID_CONNECTION_PROTOCOL_TYPE_REVERSE,
    OUTPUT_MODE_MAP,
    OUTPUT_MODE_REVERSE,
    RATED_FREQUENCY_MAP,
    RATED_FREQUENCY_REVERSE,
    RATED_VOLTAGE_MAP,
    RATED_VOLTAGE_REVERSE,
)

_LOGGER = logging.getLogger(__name__)

OUTPUT_MODE_BY_VALUE: dict[int, str] = OUTPUT_MODE_REVERSE
OUTPUT_MODES = list(OUTPUT_MODE_BY_VALUE.values())

CHARGER_PRIORITY_BY_VALUE: dict[int, str] = CHARGER_PRIORITY_REVERSE
CHARGER_PRIORITIES = list(CHARGER_PRIORITY_BY_VALUE.values())

BATTERY_TYPE_BY_VALUE: dict[int, str] = BATTERY_TYPE_REVERSE
BATTERY_TYPES = list(BATTERY_TYPE_BY_VALUE.values())

RATED_FREQUENCY_BY_VALUE: dict[int, str] = RATED_FREQUENCY_REVERSE
RATED_FREQUENCIES = list(RATED_FREQUENCY_BY_VALUE.values())

RATED_VOLTAGE_BY_VALUE: dict[int, str] = RATED_VOLTAGE_REVERSE
RATED_VOLTAGES = list(RATED_VOLTAGE_BY_VALUE.values())

GRID_CONNECTION_PROTOCOL_TYPE_BY_VALUE: dict[int, str] = (
    GRID_CONNECTION_PROTOCOL_TYPE_REVERSE
)
GRID_CONNECTION_PROTOCOL_TYPES = list(GRID_CONNECTION_PROTOCOL_TYPE_BY_VALUE.values())


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    station_id: str = data["station_id"]
    device_coordinators = data["device_coordinators"]

    entities: list[SelectEntity] = []

    for device_id, coordinator in device_coordinators.items():
        device_name = (coordinator.device_meta or {}).get("name") or device_id
        entities.extend(
            [
                SolarOfThingsOperatingModeSelect(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsBatteryPrioritySelect(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsBatteryTypeSelect(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsRatedFrequencySelect(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsRatedVoltageSelect(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsGridConnectionTypeSelect(
                    api, coordinator, station_id, device_id, device_name
                ),
            ]
        )

    async_add_entities(entities)


class _BaseSelect(CoordinatorEntity, SelectEntity):
    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(coordinator)
        self._api = api
        self._station_id = station_id
        self._device_id = device_id
        self._device_name = device_name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._station_id, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Siseli",
            "model": (self.coordinator.data.get("device_meta") or {}).get("model")
            if self.coordinator.data
            else None,
            "via_device": (DOMAIN, self._station_id),
        }

    def _get_setting_value(self, key: str) -> int | None:
        """Extract the integer value for a device setting key from coordinator data."""
        settings = (self.coordinator.data or {}).get("settings") or {}
        entry = settings.get(key)
        if entry is None:
            return None
        raw = entry.get("value") if isinstance(entry, dict) else entry
        try:
            return int(raw)
        except (TypeError, ValueError):
            return None


class SolarOfThingsOperatingModeSelect(_BaseSelect):
    """Select entity for Output Source Priority (outputSourcePrioritySetting).

    Reflects the real device API key.  Values 0/1/2 map to USO/SUB/SBU.
    """

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Output Source Priority"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_operating_mode"
        self._attr_options = OUTPUT_MODES
        self._attr_icon = "mdi:cog"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("outputSourcePrioritySetting")
        if val is None:
            return None
        return OUTPUT_MODE_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_operating_mode, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsBatteryPrioritySelect(_BaseSelect):
    """Select entity for Charger Source Priority (chargerPrioritySetting).

    Reflects the real device API key.  Values 0/1/2 map to CSO/SNU/OSO.
    """

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Charger Source Priority"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_battery_priority"
        self._attr_options = CHARGER_PRIORITIES
        self._attr_icon = "mdi:battery-sync"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("chargerPrioritySetting")
        if val is None:
            return None
        return CHARGER_PRIORITY_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_battery_priority, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsBatteryTypeSelect(_BaseSelect):
    """Select entity for Battery Type (batteryTypeSetting)."""

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Battery Type"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_battery_type"
        self._attr_options = BATTERY_TYPES
        self._attr_icon = "mdi:battery"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("batteryTypeSetting")
        if val is None:
            return None
        return BATTERY_TYPE_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_battery_type, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsRatedFrequencySelect(_BaseSelect):
    """Select entity for Output Frequency (ratedFrequencySetting)."""

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Output Frequency"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_rated_frequency"
        self._attr_options = RATED_FREQUENCIES
        self._attr_icon = "mdi:waveform"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("ratedFrequencySetting")
        if val is None:
            return None
        return RATED_FREQUENCY_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_rated_frequency, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsRatedVoltageSelect(_BaseSelect):
    """Select entity for Output Voltage (ratedVoltageSetting)."""

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Output Voltage"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_rated_voltage"
        self._attr_options = RATED_VOLTAGES
        self._attr_icon = "mdi:sine-wave"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("ratedVoltageSetting")
        if val is None:
            return None
        return RATED_VOLTAGE_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_rated_voltage, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsGridConnectionTypeSelect(_BaseSelect):
    """Select entity for Grid Connection Type (gridConnectionProtocolTypeSetting)."""

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Grid Connection Type"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_grid_connection_type"
        self._attr_options = GRID_CONNECTION_PROTOCOL_TYPES
        self._attr_icon = "mdi:transmission-tower"

    @property
    def current_option(self) -> str | None:
        val = self._get_setting_value("gridConnectionProtocolTypeSetting")
        if val is None:
            return None
        return GRID_CONNECTION_PROTOCOL_TYPE_BY_VALUE.get(val)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_grid_connection_protocol_type, self._device_id, option
        )
        await self.coordinator.async_request_refresh()
