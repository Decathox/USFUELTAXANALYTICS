# 🇺🇸 US Fuel Tax Analytics API

API REST développée avec **FastAPI** permettant d’analyser les taxes sur les carburants appliquées par les États américains à partir d’un fichier XML historique.
(https://data.bts.gov/Research-and-Statistics/Tax-Rates-by-Motor-Fuel-and-State/e5cn-ri8q/about_data)

---

# 📌 Objectif

Ce projet implémente une API capable de répondre à trois besoins métiers :

* 🔎 Consultation des taxes à une date donnée
* 📊 Analyse statistique (moyenne arithmétique)
* 🏆 Classement des États par niveau de taxation

---

# ⚙️ Installation & Lancement

## Prérequis

* Python 3.10+

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn main:app --reload
```

## Accès

* Swagger : [http://localhost:8000/docs](http://localhost:8000/docs)
* Health check : [http://localhost:8000/health](http://localhost:8000/health)

---

# 🚀 Endpoints

## 1. Consultation ponctuelle

Récupère les taxes applicables pour un État à une date donnée.

```http
GET /USFuelTaxes/{state_code}/taxes_at_date?date=YYYY-MM-DD
```

### Exemple

```bash
curl "http://127.0.0.1:8000/USFuelTaxes/AL/taxes_at_date?date=2020-08-01"
```

---

## 2. Analyse statistique (moyenne arithmétique)

Calcule la moyenne des taxes par type de carburant pour un État sur la totalité de la période du dataset.

```http
GET /USFuelTaxes/{state_code}/taxes_averages_by_fuels
```

### Exemple

```bash
curl "http://127.0.0.1:8000/USFuelTaxes/AL/taxes_averages_by_fuels"
```

---

## 3. Classement des États

Classe tous les États pour une année et un carburant donné.

```http
GET USFuelTaxes/rankings?year=YYYY-MM-DD&fuel_type_code=
```

### Exemple

```bash
curl "http://127.0.0.1:8000/USFuelTaxes/rankings?year=2019&fuel_type_code=1a"
```
---

# 📂 Structure du projet

```text
USFUELTAXANALYTICS/
├── api/           # Routes FastAPI
├── domain/        # Modèles métier
├── loader/        # Parsing XML
├── repositories/  # Index mémoire
├── services/      # Logique métier
├── schemas/       # Schémas API
├── tests/         # Tests unitaires
└── main.py        # Entrée application

dataset.xml        # Fichier XML source
```

---

## Données invalides

* Les entrées incomplètes sont ignorées
* Les doublons d’ID sont ignorés
* Les États sans données exploitables sont exclus des résultats

---

# 🧪 Tests

Lancer les tests :

```bash
pytest
```

Contenu :

* tests unitaires du service
* validation des cas métier :

  * consultation
  * moyenne
  * ranking

---

# 📌 Conclusion

Ce projet propose une API :

* performante (chargement en mémoire + index)
* robuste (gestion des erreurs et données invalides)
* maintenable (architecture claire)

---

👉 Projet réalisé dans le cadre d’un test technique.
