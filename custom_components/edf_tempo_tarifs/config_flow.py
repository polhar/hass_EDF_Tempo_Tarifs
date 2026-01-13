"""Config flow for EDF Tempo Tarifs integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_PUISSANCE_SOUSCRITE, DOMAIN, VALID_PUISSANCES


class EDFTempoTarifsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EDF Tempo Tarifs."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                puissance = int(user_input[CONF_PUISSANCE_SOUSCRITE])

                if puissance not in VALID_PUISSANCES:
                    errors[CONF_PUISSANCE_SOUSCRITE] = "invalid_puissance"
                else:
                    # Create unique ID based on puissance
                    await self.async_set_unique_id(f"edf_tempo_tarifs_{puissance}")
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"EDF Tempo Tarifs {puissance} kVA",
                        data={CONF_PUISSANCE_SOUSCRITE: str(puissance)},
                    )
            except (ValueError, TypeError):
                errors[CONF_PUISSANCE_SOUSCRITE] = "invalid_puissance"

        # Create schema with human-readable options
        puissance_options = {str(p): f"{p} kVA" for p in VALID_PUISSANCES}

        schema = vol.Schema(
            {
                vol.Required(CONF_PUISSANCE_SOUSCRITE, default="6" if not errors else None): vol.In(
                    puissance_options
                )
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={"valid_puissances": ", ".join(map(str, VALID_PUISSANCES))},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EDFTempoTarifsOptionsFlowHandler(config_entry)


class EDFTempoTarifsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for EDF Tempo Tarifs."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        super().__init__()
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            try:
                puissance = int(user_input[CONF_PUISSANCE_SOUSCRITE])

                if puissance not in VALID_PUISSANCES:
                    errors[CONF_PUISSANCE_SOUSCRITE] = "invalid_puissance"
                else:
                    # Récupérer la puissance actuelle
                    current_puissance = int(
                        self._config_entry.data.get(CONF_PUISSANCE_SOUSCRITE, 0)
                    )

                    # Mettre à jour la config entry
                    self.hass.config_entries.async_update_entry(
                        self._config_entry,
                        data={CONF_PUISSANCE_SOUSCRITE: str(puissance)},
                        title=f"EDF Tempo Tarifs {puissance} kVA",
                    )

                    # SI la puissance change, TOUJOURS recharger pour mettre à jour le nom du device
                    if puissance != current_puissance:
                        await self.hass.config_entries.async_reload(self._config_entry.entry_id)
                    else:
                        # Si même puissance, juste mettre à jour le coordinateur
                        if (
                            DOMAIN in self.hass.data
                            and self._config_entry.entry_id in self.hass.data[DOMAIN]
                        ):
                            coordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
                            await coordinator.update_puissance(puissance)

                    return self.async_create_entry(title="", data={})
            except (ValueError, TypeError):
                errors[CONF_PUISSANCE_SOUSCRITE] = "invalid_puissance"

        # Récupérer la valeur actuelle
        current_puissance = self._config_entry.data.get(CONF_PUISSANCE_SOUSCRITE, "6")

        puissance_options = {str(p): f"{p} kVA" for p in VALID_PUISSANCES}

        schema = vol.Schema(
            {
                vol.Required(CONF_PUISSANCE_SOUSCRITE, default=current_puissance): vol.In(
                    puissance_options
                )
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={"valid_puissances": ", ".join(map(str, VALID_PUISSANCES))},
        )
