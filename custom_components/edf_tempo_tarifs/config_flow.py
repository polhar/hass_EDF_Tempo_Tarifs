"""Config flow for EDF Tempo Tarifs integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, VALID_PUISSANCES, CONF_PUISSANCE_SOUSCRITE

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
                        data={
                            CONF_PUISSANCE_SOUSCRITE: str(puissance)
                        }
                    )
            except (ValueError, TypeError):
                errors[CONF_PUISSANCE_SOUSCRITE] = "invalid_puissance"

        # Create schema with human-readable options
        puissance_options = {str(p): f"{p} kVA" for p in VALID_PUISSANCES}
        
        schema = vol.Schema({
            vol.Required(
                CONF_PUISSANCE_SOUSCRITE,
                default="6" if not errors else None
            ): vol.In(puissance_options)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "valid_puissances": ", ".join(map(str, VALID_PUISSANCES))
            }
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
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({}),
            description="Cette intégration ne comporte pas d'options supplémentaires."
        )
