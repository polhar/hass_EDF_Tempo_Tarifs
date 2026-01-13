"""Constants for EDF Tempo Tarifs integration."""

import logging
from datetime import date, timedelta

DOMAIN = "edf_tempo_tarifs"
LOGGER = logging.getLogger(__name__)

# API endpoint - Documentation disponible :
# - Swagger: https://tabular-api.data.gouv.fr/api/resources/0c3d1d36-c412-4620-8566-e5cbb4fa2b5a/swagger/
# - Profile: https://tabular-api.data.gouv.fr/api/resources/0c3d1d36-c412-4620-8566-e5cbb4fa2b5a/profile/
API_URL = (
    "https://tabular-api.data.gouv.fr/api/resources/0c3d1d36-c412-4620-8566-e5cbb4fa2b5a/data/"
)
API_BASE_PARAMS = {"page_size": 1, "DATE_DEBUT__sort": "desc"}
API_TIMEOUT = 30  # secondes


def get_api_params(puissance_souscrite: int, date_max: date | None = None) -> dict:
    """
    Génère les paramètres d'API avec les valeurs dynamiques.

    Args:
        puissance_souscrite: La puissance souscrite en kVA
        date_max: Date maximum pour les tarifs (défaut: aujourd'hui)

    Returns:
        Dictionnaire des paramètres pour l'API
    """
    if date_max is None:
        date_max = date.today()

    return {
        **API_BASE_PARAMS,
        "P_SOUSCRITE__exact": str(puissance_souscrite),
        "DATE_DEBUT__less": date_max.isoformat(),
    }


CONF_PUISSANCE_SOUSCRITE = "puissance_souscrite"

VALID_PUISSANCES = [6, 9, 12, 15, 18, 30, 36]

SENSOR_TYPES = {
    "HCJB": {
        "name": "Tarif HC Bleu TTC",
        "api_field": "PART_VARIABLE_HCBleu_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "HPJB": {
        "name": "Tarif HP Bleu TTC",
        "api_field": "PART_VARIABLE_HPBleu_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "HCJW": {
        "name": "Tarif HC Blanc TTC",
        "api_field": "PART_VARIABLE_HCBlanc_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "HPJW": {
        "name": "Tarif HP Blanc TTC",
        "api_field": "PART_VARIABLE_HPBlanc_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "HCJR": {
        "name": "Tarif HC Rouge TTC",
        "api_field": "PART_VARIABLE_HCRouge_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "HPJR": {
        "name": "Tarif HP Rouge TTC",
        "api_field": "PART_VARIABLE_HPRouge_TTC",
        "device_class": "monetary",
        "state_class": "measurement",
        "unit": "€/kWh",
        "icon": "mdi:flash",
        "suggested_display_precision": 4,
    },
    "PART_FIXE_TTC": {
        "name": "Abonnement annuel TTC",
        "api_field": "PART_FIXE_TTC",
        "device_class": "monetary",
        "state_class": "total_increasing",
        "unit": "€/an",
        "icon": "mdi:cash",
        "suggested_display_precision": 2,
    },
    "DATE_DEBUT": {
        "name": "Date début tarifs",
        "api_field": "DATE_DEBUT",
        "device_class": "date",
        "icon": "mdi:calendar",
    },
}

UPDATE_INTERVAL = timedelta(hours=24)
RETRY_INTERVAL = timedelta(minutes=30)
