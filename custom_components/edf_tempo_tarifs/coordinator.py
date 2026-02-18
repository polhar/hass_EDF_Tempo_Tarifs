"""Data update coordinator for EDF Tempo Tarifs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_TIMEOUT,
    API_URL,
    DOMAIN,
    LOGGER,
    RETRY_INTERVAL,
    SENSOR_TYPES,
    UPDATE_INTERVAL,
    get_api_params,
)


class EDFTempoTarifsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching EDF Tempo Tarifs data."""

    def __init__(self, hass: HomeAssistant, puissance_souscrite: int) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            update_method=self._async_update_data_logic,
        )

        self.puissance_souscrite = puissance_souscrite
        self._session = async_get_clientsession(hass)

    async def _async_update_data_logic(self) -> dict[str, Any]:
        """Fetch data from API with retry logic."""
        try:
            data = await self._fetch_data()
            # Reset à l'intervalle normal après succès
            self.update_interval = UPDATE_INTERVAL
            return data
        except Exception as err:
            LOGGER.warning(
                "Failed to update EDF Tempo Tarifs data: %s. Retrying in %s",
                err,
                RETRY_INTERVAL,
            )
            # Changer temporairement l'intervalle (sera reset au prochain succès)
            self.update_interval = RETRY_INTERVAL
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def _fetch_data(self) -> dict[str, Any]:
        """Fetch data from API."""
        params = get_api_params(self.puissance_souscrite)

        LOGGER.debug("Fetching EDF Tempo Tarifs data for %s kVA", self.puissance_souscrite)

        async with (
            async_timeout.timeout(API_TIMEOUT),
            self._session.get(API_URL, params=params) as response,
        ):
            if response.status != 200:
                raise UpdateFailed(f"API returned status {response.status}")

            data = await response.json()

            if not data.get("data") or not isinstance(data["data"], list) or len(data["data"]) == 0:
                raise UpdateFailed("No data returned from API")

            # Get the most recent entry (first in the list due to __id__sort=desc)
            latest_data = data["data"][0]

            # Check if we have valid data (not all null in source)
            has_valid_data = False
            for sensor_info in SENSOR_TYPES.values():
                if latest_data.get(sensor_info["api_field"]) is not None:
                    has_valid_data = True
                    break

            if not has_valid_data:
                raise UpdateFailed("No valid data found in API response")

            # Parse and convert data based on device_class
            parsed_data = {}

            for sensor_key, sensor_info in SENSOR_TYPES.items():
                api_field = sensor_info["api_field"]
                raw_value = latest_data.get(api_field)

                value = None
                if raw_value is not None:
                    try:
                        # Conversion selon le device_class
                        if sensor_info.get("device_class") == "date":
                            value = datetime.strptime(str(raw_value), "%Y-%m-%d").date()
                        elif sensor_info.get("device_class") == "monetary":
                            value = float(raw_value)
                        else:
                            value = raw_value

                    except (ValueError, TypeError) as e:
                        LOGGER.error(
                            "Erreur conversion %s: %s (valeur: %s, type: %s)",
                            sensor_key,
                            e,
                            raw_value,
                            type(raw_value),
                        )
                        value = None

                parsed_data[sensor_key] = value

            # Check if we have at least some successfully converted data
            has_converted_data = False
            for _key, value in parsed_data.items():
                if value is not None:
                    has_converted_data = True
                    break

            if not has_converted_data:
                raise UpdateFailed("No valid data after conversion")

            # Store metadata
            parsed_data["raw_data"] = latest_data
            parsed_data["last_update"] = datetime.now()
            parsed_data["puissance_souscrite"] = self.puissance_souscrite

            LOGGER.debug("Successfully updated EDF Tempo Tarifs data")
            return parsed_data

    async def update_puissance(self, nouvelle_puissance: int):
        """Mettre à jour la puissance souscrite sans recréer le coordinateur."""
        if nouvelle_puissance != self.puissance_souscrite:
            self.puissance_souscrite = nouvelle_puissance
            # Forcer une mise à jour immédiate avec la nouvelle puissance
            await self.async_request_refresh()
