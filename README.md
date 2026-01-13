# Intégration EDF Tempo Tarifs pour Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/polhar/hass_EDF_Tempo_Tarifs)](https://github.com/polhar/hass_EDF_Tempo_Tarifs/releases)
[![Validate](https://github.com/polhar/hass_EDF_Tempo_Tarifs/workflows/Validate/badge.svg)](https://github.com/polhar/hass_EDF_Tempo_Tarifs/actions)
[![codecov](https://codecov.io/gh/polhar/hass_EDF_Tempo_Tarifs/branch/main/graph/badge.svg)](https://codecov.io/gh/polhar/hass_EDF_Tempo_Tarifs)

Intégration Home Assistant pour récupérer les tarifs EDF Tempo via l'API publique data.gouv.fr.

## Fonctionnalités

- Récupère automatiquement les tarifs EDF Tempo
- Supporte toutes les puissances souscrites (6, 9, 12, 15, 18, 30, 36 kVA)
- Met à jour les données quotidiennement
- Crée des capteurs pour chaque type de tarif
- Interface de configuration intuitive

## Capteurs créés

| Nom du capteur | Description | Unité |
|---------------|-------------|-------|
| `tarif_hc_bleu_ttc` | Tarif Heures Creuses Bleu TTC | €/kWh |
| `tarif_hp_bleu_ttc` | Tarif Heures Pleines Bleu TTC | €/kWh |
| `tarif_hc_blanc_ttc` | Tarif Heures Creuses Blanc TTC | €/kWh |
| `tarif_hp_blanc_ttc` | Tarif Heures Pleines Blanc TTC | €/kWh |
| `tarif_hc_rouge_ttc` | Tarif Heures Creuses Rouge TTC | €/kWh |
| `tarif_hp_rouge_ttc` | Tarif Heures Pleines Rouge TTC | €/kWh |
| `abonnement_annuel_ttc` | Abonnement annuel TTC | €/an |
| `date_debut_tarifs` | Date d'application des tarifs | Date |

## Installation

### Via HACS (recommandé)

[![Ouvre votre instance Home Assistant et ajoute un dépôt dans la boutique communautaire Home Assistant.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=polhar&repository=hass_EDF_Tempo_Tarifs&category=integration)

Plus d'informations sur HACS [ici](https://hacs.xyz/).

ou

1. Allez dans HACS > Intégrations
2. Cliquez sur "Dépôts personnalisés"
3. Ajoutez l'URL de ce dépôt
4. Sélectionnez "Intégration" comme catégorie
5. Cliquez sur "Ajouter"
6. Cherchez "EDF Tempo Tarifs" et installez
7. Redémarrez Home Assistant

### Installation manuelle

1. Copiez le dossier `edf_tempo` dans `custom_components`
2. Redémarrez Home Assistant
3. Ajoutez l'intégration via Configuration > Intégrations

## Configuration

1. Allez dans Configuration > Intégrations
2. Cliquez sur "Ajouter une intégration"
3. Cherchez "EDF Tempo Tarifs"
4. Sélectionnez votre puissance souscrite
5. Validez

## API utilisée

Cette intégration utilise l'API publique de data.gouv.fr :
- https://tabular-api.data.gouv.fr/api/resources/0c3d1d36-c412-4620-8566-e5cbb4fa2b5a/data/

## Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs d'erreur
2. Ouvrez une issue sur GitHub
3. Vérifiez que l'API est accessible

## Développement

Pour contribuer :
1. Fork le dépôt
2. Créez une branche
3. Faites vos modifications
4. Ouvrez une Pull Request

## License

Ce projet est sous licence GPL V3.
