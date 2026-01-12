## EDF Tempo Tarifs

Cette intégration récupère les tarifs EDF Tempo via l'API publique data.gouv.fr.

### Fonctionnalités principales

- Récupération automatique des tarifs
- Support de toutes les puissances souscrites
- Mise à jour quotidienne
- Interface de configuration simple

### Capteurs disponibles

L'intégration crée 8 capteurs :
- 6 capteurs pour les tarifs variables (HC/HP pour Bleu, Blanc, Rouge)
- 1 capteur pour l'abonnement annuel
- 1 capteur pour la date d'application

### Configuration

1. Installez via HACS
2. Ajoutez l'intégration
3. Sélectionnez votre puissance souscrite
4. Les capteurs seront automatiquement créés

### Notes

Les tarifs sont mis à jour une fois par jour. L'intégration gère automatiquement les changements de tarifs.

Pour plus d'informations, consultez le [README](README.md).