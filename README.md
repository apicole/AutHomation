# AutHomation

Bienvenue dans **AutHomation**, ma plateforme personnelle pour connecter et piloter différents services "Cloud" liés à la domotique.  

> **Note :** Ne jugez pas trop mon code… je ne suis pas un développeur professionnel, mais j'essaie de créer une solution méthodique et pratique pour atteindre mon objectif : **me débarrasser des multiples applications sur mon smartphone** !

---

## Objectif

L'idée principale est de **mettre les outils à mon service** afin de simplifier la gestion de ma maison connectée. Quelques exemples d'automatisations déjà mises en place :  
- **Pré-régler le chauffage** selon les besoins.  
- **Contrôler les volets roulants** (y compris les Vélux via une télécommande "vampirisée" 😄).  
- **Automatiser la détection de présence** (via les adresses IP des appareils connectés) pour ajuster le rythme de la maison.

---

## Services et équipements pris en charge

AutHomation centralise les connexions vers de nombreux services Cloud et équipements connectés :  
- **Ewelink**, **Meross**, **Tuya** : gestion des prises et interrupteurs connectés.  
- **Enphase** : récupération des données de production et de consommation des panneaux photovoltaïques.  
- **Eufy** : caméras de surveillance.  
- **Airthings** : suivi de la qualité de l'air.  
- **Borne de charge EV** : gestion de la recharge des véhicules électriques.  
- **Cozytouch** : pilotage du chauffage.  
- **Yeelight** : contrôle des ampoules connectées Xiaomi.  
- **Sonos** : gestion des haut-parleurs pour des annonces vocales et des routines.  

---

## Structure du projet

- **`configv2.py`** : fichier de configuration pour centraliser les informations et éviter les répétitions.  
- **`funcpiev2.py`** : module contenant toutes les fonctions utiles.  

### Modules par périphérique/marque

| Module       | Description                                                                                 |
|--------------|---------------------------------------------------------------------------------------------|
| `cozy.py`    | Gestion du chauffage Cozytouch.                                                            |
| `crona.py`   | Routine de base (supervision de la maison, initialisation des variables, etc.).             |
| `enphase.py` | Récupération des données de la box Enphase (production/consommation photovoltaïque).        |
| `eufy.py`    | Non utilisé pour le moment (sécurité et confort volontairement séparés).                    |
| `meross.py`  | Gestion des prises connectées Meross.                                                      |
| `tuya.py`    | Gestion des prises et interrupteurs Tuya.                                                  |
| `myyeelight.py` | Contrôle des ampoules connectées Yeelight - Xiaomi.                                     |

Chaque module inclut des fonctionnalités spécifiques liées à :  
- **La météo**,  
- **Les éphémérides**,  
- **L'heure**,  
- **La géolocalisation**, etc.  
Ce qui implique la présence de nombreuses boucles d'automatisation.

---

## Dépendance à Internet

Malheureusement, **oui**. La plupart des modules utilisent des APIs basées sur le Cloud, nécessitant une connexion internet.  
- Exemple : Sans connexion, impossible de piloter le chauffage via l'application (seul le thermostat physique reste utilisable). L'authentification passe par un *token* généré par le Cloud.  

Cependant, je réduis cette dépendance où je peux. Par exemple :  
- J'auto-héberge mes fichiers MP3 pour les annonces sur les enceintes Sonos.  
  (e.g., un *ding* à 7h50 pour partir à l'école, un rappel pour sortir la poubelle le lundi soir, ou un message pour le jogging du petit le vendredi matin !).

---

## Utilisation

Planifiez le lancement du script via **Cron** ou tout autre outil de gestion de tâches pour une exécution toutes les X minutes.  

---

## ⚠️ Attention ⚠️

Le script écrit dans le fichier de configuration à chaque exécution.  
- Si deux scripts démarrent **simultanément**, tout ira bien.  
- Mais si deux scripts tentent de **terminer en même temps**, seul le premier à écrire pourra modifier le fichier correctement.

---

## Contribuez

Ce projet est une aventure personnelle, mais toutes vos suggestions ou contributions sont les bienvenues ! 🌟
