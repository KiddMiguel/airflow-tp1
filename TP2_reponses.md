# TP 2 - Creer un premier DAG Airflow

## 1. Lancer l'environnement Airflow

L'environnement Airflow est lance avec Docker Compose depuis le dossier `airflow_tp`.

Commande utilisee :

```powershell
docker compose up -d
```

Le conteneur expose l'interface web sur :

```text
http://localhost:8080
```

## 2. Acceder a l'interface web

Une fois le conteneur demarre, l'interface Airflow est accessible dans le navigateur a l'adresse :

```text
http://localhost:8080
```

Dans cette configuration, l'utilisateur de connexion est :

```text
admin
```

## 3. Creer un DAG simple

Le fichier du DAG est :

[pipeline_meteo_villes.py](c:/Users/Admin/Documents/IPSSI/airflow_tp/dags/pipeline_meteo_villes.py)

Ce DAG s'appelle `pipeline_meteo_villes` et il execute un mini pipeline meteo sur plusieurs villes.

Il contient 4 taches Python explicites :

1. `extraire_meteo`
2. `valider_meteo`
3. `transformer_meteo`
4. `generer_rapport`

Le code metier appele par ces taches est dans :

[meteo_job.py](c:/Users/Admin/Documents/IPSSI/airflow_tp/jobs/meteo_job.py)

## 4. Definir explicitement les dependances

Les dependances sont definies directement dans le DAG avec :

```python
t1 >> t2 >> t3 >> t4
```

Cela signifie :

1. `extraire_meteo` s'execute d'abord
2. `valider_meteo` s'execute ensuite
3. `transformer_meteo` s'execute apres validation
4. `generer_rapport` s'execute a la fin

## 5. Lancer le DAG

Le DAG peut etre lance de deux manieres :

1. manuellement depuis l'interface Airflow avec `Trigger DAG`
2. automatiquement toutes les 5 minutes car le schedule actuel est :

```python
schedule="*/5 * * * *"
```

Le parametre `catchup=False` evite de rejouer les anciennes executions.

## 6. Consulter les logs d'une tache

Les logs peuvent etre consultes :

1. dans l'interface Airflow en cliquant sur une tache puis sur `Logs`
2. dans les fichiers locaux montes par Docker dans le dossier :

[logs](c:/Users/Admin/Documents/IPSSI/airflow_tp/logs)

## 7. Expliquer le role de chaque tache

### `extraire_meteo`

Cette tache appelle l'API Open-Meteo pour recuperer la meteo reelle des villes selectionnees.

Elle produit un fichier brut :

[meteo_brute.json](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/meteo_brute.json)

### `valider_meteo`

Cette tache verifie que les donnees extraites contiennent bien tous les champs attendus :

- ville
- country_code
- latitude
- longitude
- temperature
- humidite
- weather_code
- condition
- date_observation

### `transformer_meteo`

Cette tache nettoie et normalise les donnees :

- ville en majuscules
- temperature convertie en `float`
- humidite convertie en `int`
- structure finale plus propre

Elle produit :

[meteo_propre.json](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/meteo_propre.json)

### `generer_rapport`

Cette tache cree un rapport texte final avec :

- le nombre de villes analysees
- la temperature moyenne
- la ville la plus chaude
- le detail meteo par ville

Elle produit :

[rapport_meteo.txt](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/rapport_meteo.txt)

## 8. Preuve d'execution

Les fichiers generes prouvent que le DAG a bien tourne :

- [meteo_brute.json](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/meteo_brute.json)
- [meteo_propre.json](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/meteo_propre.json)
- [rapport_meteo.txt](c:/Users/Admin/Documents/IPSSI/airflow_tp/data/meteo/rapport_meteo.txt)

Exemple de resultat obtenu dans le rapport :

```text
RAPPORT METEO
=============
Nombre de villes analysees : 5
Temperature moyenne : 25.90 degC
Ville la plus chaude : BRAZZAVILLE (29.8 degC)
```

## 09. Resume du fonctionnement

Le workflow fonctionne ainsi :

1. Airflow declenche le DAG
2. le DAG recupere la meteo reelle depuis une API
3. les donnees sont verifiees
4. les donnees sont transformees
5. un rapport final est genere

Ce TP montre comment traduire un workflow simple en DAG Airflow avec des taches separees, ordonnees et lisibles.
