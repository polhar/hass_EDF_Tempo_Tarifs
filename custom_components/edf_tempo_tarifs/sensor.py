"""Sensor platform for EDF Tempo Tarifs integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES
from .coordinator import EDFTempoTarifsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EDF Tempo Tarifs sensors from a config entry."""
    coordinator: EDFTempoTarifsCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
    for sensor_key in SENSOR_TYPES:
        entities.append(EDFTempoTarifsSensor(coordinator, sensor_key, config_entry.entry_id))

    async_add_entities(entities)


class EDFTempoTarifsSensor(CoordinatorEntity, SensorEntity):
    """Representation of an EDF Tempo Tarifs sensor."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: EDFTempoTarifsCoordinator, sensor_key: str, entry_id: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._entry_id = entry_id

        sensor_info = SENSOR_TYPES[sensor_key]

        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{entry_id}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "manufacturer": "EDF",
            "model": "Option Tempo",
        }

        self._attr_device_class = sensor_info.get("device_class")
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info.get("icon")

        # Set state class and precision for monetary values
        if sensor_key != "DATE_DEBUT":
            self._attr_state_class = sensor_info.get("state_class")
            self._attr_suggested_display_precision = sensor_info.get("suggested_display_precision")

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._entry_id)},
            "name": f"EDF Tempo Tarifs {self.coordinator.puissance_souscrite} kVA",
            "manufacturer": "EDF",
            "model": "Option Tempo",
        }

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        return self.coordinator.data.get(self._sensor_key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}

        if self.coordinator.data:
            attrs["puissance_souscrite_kva"] = self.coordinator.puissance_souscrite

            last_update = self.coordinator.data.get("last_update")
            if last_update:
                attrs["last_update"] = last_update.isoformat()

        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.coordinator.data
            and self._sensor_key in self.coordinator.data
            and self.coordinator.data[self._sensor_key] is not None
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.last_update_success:
            return

        # Récupérer la nouvelle valeur depuis le coordinateur
        new_value = None
        if self.coordinator.data and self._sensor_key in self.coordinator.data:
            new_value = self.coordinator.data.get(self._sensor_key)

        # Récupérer l'ancienne valeur actuelle
        old_value = self._attr_native_value

        # Comparaison simple et directe
        if old_value == new_value and self.available:
            # Même valeur ET déjà disponible, on ne fait RIEN
            return

        # Si la valeur a changé OU si l'entité n'est pas encore disponible
        self._attr_native_value = new_value

        # Force l'entité à devenir disponible si elle ne l'est pas déjà
        if not self.available:
            self._attr_available = True

        self.async_write_ha_state()
