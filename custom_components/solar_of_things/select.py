"""Select platform for Solar of Things integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CHARGER_PRIORITY_MAP,
    CHARGER_PRIORITY_REVERSE,
    DOMAIN,
    OUTPUT_MODE_MAP,
    OUTPUT_MODE_REVERSE,
)

_LOGGER = logging.getLogger(__name__)


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
        self._attr_options = OUTPUT_MODE_MAP
        self._attr_icon = "mdi:cog"

    @property
    def current_option(self) -> str | None:
        settings = (self.coordinator.data or {}).get("settings") or {}
        entry = settings.get("outputSourcePrioritySetting")
        if entry is None:
            return None
        raw = entry.get("value") if isinstance(entry, dict) else entry
        try:
            return OUTPUT_MODE_REVERSE.get(int(raw))
        except (TypeError, ValueError):
            return None

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_operating_mode, self._device_id, option
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsBatteryPrioritySelect(_BaseSelect):
    """Select entity for Charger Source Priority (chargerSourcePrioritySetting).

    Reflects the real device API key.  Values 0/1/2 map to CSO/SNU/OSO.
    """

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Charger Source Priority"
        self._attr_unique_id = f"{DOMAIN}_{station_id}_{device_id}_battery_priority"
        self._attr_options = CHARGER_PRIORITY_MAP
        self._attr_icon = "mdi:battery-sync"

    @property
    def current_option(self) -> str | None:
        settings = (self.coordinator.data or {}).get("settings") or {}
        entry = settings.get("chargerSourcePrioritySetting")
        if entry is None:
            return None
        raw = entry.get("value") if isinstance(entry, dict) else entry
        try:
            return CHARGER_PRIORITY_REVERSE.get(int(raw))
        except (TypeError, ValueError):
            return None

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_battery_priority, self._device_id, option
        )
        await self.coordinator.async_request_refresh()
