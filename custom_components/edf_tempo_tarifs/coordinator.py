"""Data update coordinator for EDF Tempo Tarifs."""
from __future__ import annotations
from datetime import date, datetime
import logging
from typing import Any

import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    API_URL,
    API_PARAMS,
    CONF_PUISSANCE_SOUSCRITE,
    LOGGER,
    UPDATE_INTERVAL,
    RETRY_INTERVAL,
    SENSOR_TYPES
)

class EDFTempoTarifsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching EDF Tempo Tarifs data."""

    def __init__(
        self,
        hass: HomeAssistant,
        puissance_souscrite: int
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            update_method=self._async_update_data_logic
        )
        
        self.puissance_souscrite = puissance_souscrite
        self._session = aiohttp.ClientSession()

    async def _async_update_data_logic(self) -> dict[str, Any]:
        """Fetch data from API with retry logic."""
        try:
            return await self._fetch_data()
        except Exception as err:
            LOGGER.warning("Failed to update EDF Tempo Tarifs data: %s. Retrying in %s", err, RETRY_INTERVAL)
            self.update_interval = RETRY_INTERVAL
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        params = API_PARAMS.copy()
        params["P_SOUSCRITE__exact"] = str(self.puissance_souscrite)
        
        LOGGER.debug("Fetching EDF Tempo Tarifs data for %s kVA", self.puissance_souscrite)
        
        async with async_timeout.timeout(30):
            async with self._session.get(API_URL, params=params) as response:
                if response.status != 200:
                    raise UpdateFailed(f"API returned status {response.status}")
                
                data = await response.json()
                
                if not data.get("data"):
                    raise UpdateFailed("No data returned from API")
                
                # Get the most recent entry (first in the list due to __id__sort=desc)
                latest_data = data["data"][0]
                
                # DEBUG: Afficher les données brutes
                LOGGER.debug("Données brutes API DATE_DEBUT: %s (type: %s)", 
                           latest_data.get("DATE_DEBUT"), 
                           type(latest_data.get("DATE_DEBUT")))
                
                # Check if we have valid data (not all null)
                has_valid_data = False
                for sensor_info in SENSOR_TYPES.values():
                    if latest_data.get(sensor_info["api_field"]) is not None:
                        has_valid_data = True
                        break
                
                if not has_valid_data:
                    raise UpdateFailed("No valid data found in API response")
                
                # Validate that we have the required fields
                parsed_data = {}
                
                for sensor_key, sensor_info in SENSOR_TYPES.items():
                    api_field = sensor_info["api_field"]
                    raw_value = latest_data.get(api_field)
                    
                    value = None
                    if raw_value is not None:
                        try:
                            # DATE_DEBUT - conversion STRING → DATE
                            if sensor_key == "DATE_DEBUT":
                                # Convertir explicitement en string puis parser
                                value = datetime.strptime(str(raw_value), "%Y-%m-%d").date()
                            
                            # Tarifs - conversion en float
                            elif api_field in ["PART_FIXE_TTC", "PART_VARIABLE_HCBleu_TTC", 
                                             "PART_VARIABLE_HPBleu_TTC", "PART_VARIABLE_HCBlanc_TTC",
                                             "PART_VARIABLE_HPBlanc_TTC", "PART_VARIABLE_HCRouge_TTC",
                                             "PART_VARIABLE_HPRouge_TTC"]:
                                value = float(raw_value)
                            
                            else:
                                value = raw_value
                                
                        except (ValueError, TypeError) as e:
                            LOGGER.error("Erreur conversion %s: %s (valeur: %s, type: %s)", 
                                       sensor_key, e, raw_value, type(raw_value))
                            value = None
                    
                    parsed_data[sensor_key] = value
                
                # Reset update interval to normal after successful update
                from .const import UPDATE_INTERVAL
                self.update_interval = UPDATE_INTERVAL
                
                # Also store the raw data for debugging
                parsed_data["raw_data"] = latest_data
                parsed_data["last_update"] = datetime.now()
                parsed_data["puissance_souscrite"] = self.puissance_souscrite
                
                LOGGER.debug("Données finales DATE_DEBUT: %s (type: %s)", 
                           parsed_data.get("DATE_DEBUT"), 
                           type(parsed_data.get("DATE_DEBUT")))
                LOGGER.debug("Successfully updated EDF Tempo Tarifs data")
                return parsed_data

    async def async_close(self):
        """Close the session."""
        await self._session.close()
