"""Number platform for Solar of Things integration."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities (controls) for each device."""

    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    station_id: str = data["station_id"]
    device_coordinators = data["device_coordinators"]

    entities: list[NumberEntity] = []

    for device_id, coordinator in device_coordinators.items():
        device_meta = (
            (coordinator.data.get("device_meta") or {}) if coordinator.data else {}
        )
        device_name = device_meta.get("name", device_id)

        entities.extend(
            [
                SolarOfThingsMaximumTotalChargingCurrentNumber(
                    api, coordinator, station_id, device_id, device_name
                ),
                SolarOfThingsMaxUtilityChargeCurrentNumber(
                    api, coordinator, station_id, device_id, device_name
                ),
            ]
        )

    async_add_entities(entities)


class _BaseNumber(CoordinatorEntity, NumberEntity):
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

    @property
    def native_value(self):
        return ((self.coordinator.data or {}).get("settings") or {}).get(
            self._setting_key
        )


class SolarOfThingsMaximumTotalChargingCurrentNumber(_BaseNumber):
    _setting_key = "maximumChargingCurrentSetting"

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Maximum Total Charging Current"
        self._attr_unique_id = (
            f"{DOMAIN}_{station_id}_{device_id}_maximum_total_charging_current"
        )
        self._attr_native_min_value = 10
        self._attr_native_max_value = 120
        self._attr_native_step = 10
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_mode = NumberMode.BOX
        self._attr_device_class = NumberDeviceClass.CURRENT
        self._attr_icon = "mdi:battery-arrow-up"

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_maximum_total_charging_current, self._device_id, int(value)
        )
        await self.coordinator.async_request_refresh()


class SolarOfThingsMaxUtilityChargeCurrentNumber(_BaseNumber):
    _setting_key = "maximumMainsChargingCurrentSetting"

    def __init__(
        self, api, coordinator, station_id: str, device_id: str, device_name: str
    ) -> None:
        super().__init__(api, coordinator, station_id, device_id, device_name)
        self._attr_name = f"{device_name} Max Utility Charge Current"
        self._attr_unique_id = (
            f"{DOMAIN}_{station_id}_{device_id}_max_utility_charge_current"
        )
        self._attr_native_min_value = 10
        self._attr_native_max_value = 100
        self._attr_native_step = 10
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_mode = NumberMode.BOX
        self._attr_device_class = NumberDeviceClass.CURRENT
        self._attr_icon = "mdi:transmission-tower-import"

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(
            self._api.set_max_utility_charge_current, self._device_id, int(value)
        )
        await self.coordinator.async_request_refresh()
