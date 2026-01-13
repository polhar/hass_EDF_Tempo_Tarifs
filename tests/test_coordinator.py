"""Tests for the coordinator."""
import pytest
import threading
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.edf_tempo_tarifs.coordinator import EDFTempoTarifsCoordinator


# Marquer tous les tests de ce module pour accepter les tâches en attente
pytestmark = pytest.mark.usefixtures("expected_lingering_tasks")


@pytest.fixture
def mock_api_response():
    """Mock API response."""
    return {
        "data": [{
            "DATE_DEBUT": "2024-01-01",
            "PART_FIXE_TTC": 150.50,
            "PART_VARIABLE_HCBleu_TTC": 0.1234,
            "PART_VARIABLE_HPBleu_TTC": 0.1567,
            "PART_VARIABLE_HCBlanc_TTC": 0.1345,
            "PART_VARIABLE_HPBlanc_TTC": 0.1678,
            "PART_VARIABLE_HCRouge_TTC": 0.1456,
            "PART_VARIABLE_HPRouge_TTC": 0.1789,
            "P_SOUSCRITE": "6"
        }]
    }


@pytest.mark.asyncio
async def test_fetch_data_success(hass: HomeAssistant, mock_api_response):
    """Test successful data fetch."""

    mock_thread = MagicMock()
    mock_thread.name = "waitpid-123" 
    mock_thread.is_alive.return_value = False

    coordinator = EDFTempoTarifsCoordinator(hass, 6)

    with patch('threading.current_thread', return_value=mock_thread), \
         patch.object(coordinator._session, 'get') as mock_get:
        
        # Mock the async context manager
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await coordinator._fetch_data()
        
        assert result["DATE_DEBUT"] == date(2024, 1, 1)
        assert result["PART_FIXE_TTC"] == 150.50
        assert result["HCJB"] == 0.1234
        assert result["puissance_souscrite"] == 6


@pytest.mark.asyncio
async def test_fetch_data_empty_response(hass: HomeAssistant):
    """Test fetch with empty API response."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": []})
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(UpdateFailed, match="No data returned from API"):
            await coordinator._fetch_data()


@pytest.mark.asyncio
async def test_fetch_data_invalid_status(hass: HomeAssistant):
    """Test fetch with invalid HTTP status."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(UpdateFailed, match="API returned status 500"):
            await coordinator._fetch_data()


@pytest.mark.asyncio
async def test_fetch_data_conversion_error(hass: HomeAssistant):
    """Test fetch with data conversion error - values become None but no exception."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    invalid_data = {
        "data": [{
            "DATE_DEBUT": "invalid-date",
            "PART_FIXE_TTC": "not-a-number",
            "PART_VARIABLE_HCBleu_TTC": None,
            "PART_VARIABLE_HPBleu_TTC": None,
            "PART_VARIABLE_HCBlanc_TTC": None,
            "PART_VARIABLE_HPBlanc_TTC": None,
            "PART_VARIABLE_HCRouge_TTC": None,
            "PART_VARIABLE_HPRouge_TTC": None,
        }]
    }
    
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=invalid_data)
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Should raise UpdateFailed because all conversions failed
        with pytest.raises(UpdateFailed, match="No valid data after conversion"):
            await coordinator._fetch_data()


@pytest.mark.asyncio
async def test_fetch_data_partial_conversion_error(hass: HomeAssistant):
    """Test fetch with partial conversion error - some valid data exists."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    partial_data = {
        "data": [{
            "DATE_DEBUT": "invalid-date",  # Will fail conversion -> None
            "PART_FIXE_TTC": 150.50,  # Valid
            "PART_VARIABLE_HCBleu_TTC": 0.1234,  # Valid
            "PART_VARIABLE_HPBleu_TTC": 0.1567,
            "PART_VARIABLE_HCBlanc_TTC": 0.1345,
            "PART_VARIABLE_HPBlanc_TTC": 0.1678,
            "PART_VARIABLE_HCRouge_TTC": 0.1456,
            "PART_VARIABLE_HPRouge_TTC": 0.1789,
        }]
    }
    
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=partial_data)
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Should succeed because we have some valid data
        result = await coordinator._fetch_data()
        
        assert result["DATE_DEBUT"] is None  # Conversion failed
        assert result["PART_FIXE_TTC"] == 150.50  # Valid


@pytest.mark.asyncio
async def test_update_interval_reset_on_success(hass: HomeAssistant, mock_api_response):
    """Test that update interval resets after successful fetch."""
    from custom_components.edf_tempo_tarifs.const import UPDATE_INTERVAL, RETRY_INTERVAL
    
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    coordinator.update_interval = RETRY_INTERVAL  # Simulate retry state
    
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        await coordinator._async_update_data_logic()
        
        assert coordinator.update_interval == UPDATE_INTERVAL
        
@pytest.mark.asyncio
async def test_update_puissance_success(hass: HomeAssistant, mock_api_response):
    """Test successful power update."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    # Mock initial fetch
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        await coordinator._fetch_data()
    
    # Verify initial power
    assert coordinator.puissance_souscrite == 6
    
    # Update power
    await coordinator.update_puissance(9)
    
    # Verify power was updated
    assert coordinator.puissance_souscrite == 9


@pytest.mark.asyncio
async def test_update_puissance_same_value(hass: HomeAssistant, mock_api_response):
    """Test power update with same value doesn't trigger refresh."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    # Mock the async_request_refresh to track calls
    with patch.object(coordinator, 'async_request_refresh') as mock_refresh:
        # Update with same value
        await coordinator.update_puissance(6)
        
        # Should not trigger refresh
        mock_refresh.assert_not_called()
    
    # Power should still be 6
    assert coordinator.puissance_souscrite == 6


@pytest.mark.asyncio
async def test_update_puissance_triggers_refresh(hass: HomeAssistant):
    """Test that power update triggers refresh."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    # Mock the async_request_refresh
    with patch.object(coordinator, 'async_request_refresh') as mock_refresh:
        # Update with different value
        await coordinator.update_puissance(9)
        
        # Should trigger refresh
        mock_refresh.assert_called_once()
    
    assert coordinator.puissance_souscrite == 9


@pytest.mark.asyncio
async def test_update_puissance_updates_api_params(hass: HomeAssistant, mock_api_response):
    """Test that API params are updated when power changes."""
    coordinator = EDFTempoTarifsCoordinator(hass, 6)
    
    # Update power
    await coordinator.update_puissance(12)
    
    # Verify API call uses new power
    with patch.object(coordinator._session, 'get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        await coordinator._fetch_data()
        
        # Check that API was called with new power parameter
        call_args = mock_get.call_args
        params = call_args[1]['params']
        assert params['P_SOUSCRITE__exact'] == '12'
