"""Sensor platform for EDF Tempo Tarifs integration."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    CONF_PUISSANCE_SOUSCRITE
)
from .coordinator import EDFTempoTarifsCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up EDF Tempo Tarifs sensors from a config entry."""
    coordinator: EDFTempoTarifsCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    puissance = config_entry.data[CONF_PUISSANCE_SOUSCRITE]
    
    entities = []
    for sensor_key in SENSOR_TYPES:
        entities.append(EDFTempoTarifsSensor(coordinator, sensor_key, puissance))
    
    async_add_entities(entities)

class EDFTempoTarifsSensor(CoordinatorEntity, SensorEntity):
    """Representation of an EDF Tempo Tarifs sensor."""
    
    _attr_has_entity_name = True
    
    def __init__(
        self,
        coordinator: EDFTempoTarifsCoordinator,
        sensor_key: str,
        puissance: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._puissance = puissance
        
        sensor_info = SENSOR_TYPES[sensor_key]
        
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"edf_tempo_tarifs_{puissance}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"edf_tempo_tarifs_{puissance}")},
            "name": f"EDF Tempo Tarifs {puissance} kVA",
            "manufacturer": "EDF",
            "model": "Option Tempo"
        }
        
        # Selon la doc, pour DATE_DEBUT, device_class doit être "date"
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info.get("icon")
        
        # Set state class and precision for monetary values
        if sensor_key != "DATE_DEBUT":
            self._attr_state_class = sensor_info.get("state_class")
            self._attr_suggested_display_precision = sensor_info.get("suggested_display_precision")
    
    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        value = self.coordinator.data.get(self._sensor_key)
        
        # Pour DATE_DEBUT, s'assurer que c'est un objet date
        if self._sensor_key == "DATE_DEBUT" and isinstance(value, str):
            try:
                # Convertir la string en date
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        
        return value
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        
        if self.coordinator.data:
            attrs["puissance_souscrite_kva"] = int(self._puissance)
            
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
