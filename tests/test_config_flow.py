"""Tests for the config flow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData

from custom_components.edf_tempo_tarifs.config_flow import (
    EDFTempoTarifsConfigFlow,
    EDFTempoTarifsOptionsFlowHandler,
)
from custom_components.edf_tempo_tarifs.const import CONF_PUISSANCE_SOUSCRITE, DOMAIN, VALID_PUISSANCES


@pytest.mark.asyncio
async def test_flow_user_step(hass: HomeAssistant):
    """Test user step in config flow."""
    # Initialise the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Submit the form with valid data
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_PUISSANCE_SOUSCRITE] == "6"
    assert result["title"] == "EDF Tempo Tarifs 6 kVA"


@pytest.mark.asyncio
async def test_flow_user_step_invalid_puissance(hass: HomeAssistant):
    """Test user step with invalid power - schema validation catches it."""
    # Initialise the flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # Submit the form with invalid data (power not in list)
    # This will be caught by the schema validation before reaching our code
    with pytest.raises(InvalidData) as exc_info:
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PUISSANCE_SOUSCRITE: "99"}
        )
    
    # Verify the error message
    assert "Schema validation failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_flow_user_step_already_configured(hass: HomeAssistant):
    """Test that we cannot configure two entries with the same power."""
    # Create a mock entry via the flow first
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    assert result["type"] == FlowResultType.CREATE_ENTRY
    first_entry_id = result["result"].entry_id
    
    # Try to configure another entry with the same power
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    
    # Now submit the form with the same power (6)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    # Should abort because already configured
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_options_flow_update_puissance(hass: HomeAssistant):
    """Test options flow updates power."""
    # Create an entry via the flow first
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    entry = result["result"]
    
    # Create a mock coordinator and add it to hass.data
    mock_coordinator = MagicMock()
    mock_coordinator.update_puissance = AsyncMock(return_value=None)
    mock_coordinator.puissance_souscrite = 6
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mock_coordinator

    # Initialise the options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit the form with a new power value
    with patch.object(hass.config_entries, 'async_reload') as mock_reload:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_PUISSANCE_SOUSCRITE: "9"}
        )
        
        # Should reload when power changes (to update device name)
        mock_reload.assert_called_once_with(entry.entry_id)
        # update_puissance should NOT be called because we're reloading
        mock_coordinator.update_puissance.assert_not_called()
        assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_options_flow_fallback_reload(hass: HomeAssistant):
    """Test options flow falls back to reload when coordinator not found."""
    # Create an entry via the flow first
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    entry = result["result"]
    
    # Initialise the options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "init"

    # Submit the form with a new power value
    with patch.object(hass.config_entries, 'async_reload') as mock_reload:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_PUISSANCE_SOUSCRITE: "9"}
        )
        
        # Should trigger reload because power changed
        mock_reload.assert_called_once_with(entry.entry_id)
        assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_options_flow_same_puissance(hass: HomeAssistant):
    """Test options flow with same power value."""
    # Create an entry via the flow first
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    entry = result["result"]
    
    # Create a mock coordinator
    mock_coordinator = MagicMock()
    mock_coordinator.update_puissance = AsyncMock()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mock_coordinator

    # Initialise the options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    # Submit the form with the same power value
    with patch.object(hass.config_entries, 'async_reload') as mock_reload:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
        )
        
        # Should not reload when power is the same
        mock_reload.assert_not_called()
        # Should update coordinator with same power (even though it won't change)
        mock_coordinator.update_puissance.assert_called_once_with(6)
        assert result["type"] == FlowResultType.CREATE_ENTRY


@pytest.mark.asyncio
async def test_options_flow_invalid_puissance(hass: HomeAssistant):
    """Test options flow with invalid power - caught by schema."""
    # Create an entry via the flow first
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={CONF_PUISSANCE_SOUSCRITE: "6"}
    )
    
    entry = result["result"]
    
    # Initialise the options flow
    result = await hass.config_entries.options.async_init(entry.entry_id)
    
    # Submit the form with invalid power value (99 not in VALID_PUISSANCES)
    with pytest.raises(InvalidData) as exc_info:
        await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={CONF_PUISSANCE_SOUSCRITE: "99"}  # Invalid
        )
    
    # Schema validation should fail
    assert "Schema validation failed" in str(exc_info.value)
