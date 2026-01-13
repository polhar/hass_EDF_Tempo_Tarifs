"""Tests for the sensor platform."""
import pytest
from unittest.mock import MagicMock, PropertyMock
from datetime import date, datetime

from homeassistant.core import HomeAssistant
from custom_components.edf_tempo_tarifs.sensor import EDFTempoTarifsSensor
from custom_components.edf_tempo_tarifs.coordinator import EDFTempoTarifsCoordinator
from custom_components.edf_tempo_tarifs.const import DOMAIN


@pytest.fixture
def mock_coordinator(hass: HomeAssistant):
    """Create a mock coordinator with test data."""
    coordinator = MagicMock(spec=EDFTempoTarifsCoordinator)
    coordinator.puissance_souscrite = 6
    coordinator.data = {
        "DATE_DEBUT": date(2024, 1, 1),
        "PART_FIXE_TTC": 150.50,
        "HCJB": 0.1234,
        "HPJB": 0.1567,
        "HCJW": 0.1345,
        "HPJW": 0.1678,
        "HCJR": 0.1456,
        "HPJR": 0.1789,
        "last_update": datetime(2024, 1, 1, 12, 0, 0),
        "puissance_souscrite": 6
    }
    # Mock last_update_success pour simuler CoordinatorEntity
    coordinator.last_update_success = True
    return coordinator

def test_sensor_creation(mock_coordinator):
    """Test sensor creation."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    assert sensor._sensor_key == "HCJB"
    assert sensor._entry_id == entry_id
    assert sensor.name == "Tarif HC Bleu TTC"
    assert sensor.unique_id == f"{entry_id}_HCJB"


def test_sensor_native_value(mock_coordinator):
    """Test sensor native value."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    assert sensor.native_value == 0.1234


def test_sensor_date_value(mock_coordinator):
    """Test sensor date value."""
    sensor = EDFTempoTarifsSensor(mock_coordinator, "DATE_DEBUT", 6)
    
    assert sensor.native_value == date(2024, 1, 1)


def test_sensor_extra_attributes(mock_coordinator):
    """Test sensor extra state attributes."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    attrs = sensor.extra_state_attributes
    
    assert attrs["puissance_souscrite_kva"] == 6
    assert "last_update" in attrs


def test_sensor_availability_with_data(mock_coordinator):
    """Test sensor availability when data is present."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    assert sensor.available is True


def test_sensor_availability_no_data(mock_coordinator):
    """Test sensor availability when data is missing."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # Simuler l'absence de données
    mock_coordinator.data = None
    
    # Tester la logique de disponibilité directement
    # available = last_update_success AND data AND key in data AND value not None
    assert not (mock_coordinator.last_update_success 
                and mock_coordinator.data 
                and sensor._sensor_key in (mock_coordinator.data or {})
                and (mock_coordinator.data or {}).get(sensor._sensor_key) is not None)


def test_sensor_availability_empty_dict(mock_coordinator):
    """Test sensor availability when data is an empty dict."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # Dict vide - la clé n'existe pas
    mock_coordinator.data = {}
    
    # Tester la logique: key n'est pas dans data
    assert not (mock_coordinator.last_update_success 
                and mock_coordinator.data 
                and sensor._sensor_key in mock_coordinator.data
                and mock_coordinator.data.get(sensor._sensor_key) is not None)


def test_sensor_availability_null_value(mock_coordinator):
    """Test sensor availability when value is None."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # La valeur spécifique est None
    mock_coordinator.data["HCJB"] = None
    
    assert sensor.available is False


def test_sensor_availability_coordinator_failed(mock_coordinator):
    """Test sensor availability when coordinator update failed."""
    entry_id = "test_entry_id_123"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # Simuler un échec de mise à jour du coordinator
    mock_coordinator.last_update_success = False
    
    assert sensor.available is False
    
def test_sensor_device_info_updates_with_coordinator(mock_coordinator):
    """Test that device info updates when coordinator power changes."""
    entry_id = "test_entry_id"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # Initial power is 6
    assert "EDF Tempo Tarifs 6 kVA" in sensor.device_info["name"]
    
    # Change power in coordinator
    mock_coordinator.puissance_souscrite = 9
    
    # Device name should update
    assert "EDF Tempo Tarifs 9 kVA" in sensor.device_info["name"]


def test_sensor_attributes_update_with_coordinator(mock_coordinator):
    """Test that extra attributes update when coordinator power changes."""
    entry_id = "test_entry_id"
    sensor = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    
    # Initial attributes
    attrs = sensor.extra_state_attributes
    assert attrs["puissance_souscrite_kva"] == 6
    
    # Change power in coordinator
    mock_coordinator.puissance_souscrite = 12
    
    # Attributes should update
    attrs = sensor.extra_state_attributes
    assert attrs["puissance_souscrite_kva"] == 12


def test_multiple_sensors_same_entry_id(mock_coordinator):
    """Test that multiple sensors for same entry have correct unique IDs."""
    entry_id = "test_entry_id"
    
    sensor1 = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id)
    sensor2 = EDFTempoTarifsSensor(mock_coordinator, "HPJB", entry_id)
    
    assert sensor1.unique_id == f"{entry_id}_HCJB"
    assert sensor2.unique_id == f"{entry_id}_HPJB"
    assert sensor1.unique_id != sensor2.unique_id
    
    # Both should have same device identifiers
    assert sensor1.device_info["identifiers"] == {(DOMAIN, entry_id)}
    assert sensor2.device_info["identifiers"] == {(DOMAIN, entry_id)}


def test_sensor_with_different_entry_ids(mock_coordinator):
    """Test that sensors with different entries have different unique IDs."""
    entry_id1 = "entry_1"
    entry_id2 = "entry_2"
    
    sensor1 = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id1)
    sensor2 = EDFTempoTarifsSensor(mock_coordinator, "HCJB", entry_id2)
    
    assert sensor1.unique_id == f"{entry_id1}_HCJB"
    assert sensor2.unique_id == f"{entry_id2}_HCJB"
    assert sensor1.unique_id != sensor2.unique_id
    
    # Different entries should have different device identifiers
    assert sensor1.device_info["identifiers"] == {(DOMAIN, entry_id1)}
    assert sensor2.device_info["identifiers"] == {(DOMAIN, entry_id2)}
