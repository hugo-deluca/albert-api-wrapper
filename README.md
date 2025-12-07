# Albert API Wrapper

Une bibliothèque Python pour interagir avec l'API Albert d'Etalab, accompagnée d'une interface web pour gérer vos collections et documents.

Disclaimer. Je ne suis pas affilié à Etalab ou au produit Albert.

[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation du wrapper Python](#utilisation-du-wrapper-python)
- [Interface web](#interface-web)
- [Documentation API](#documentation-api)
- [Tests](#tests)
- [Contribution](#contribution)

## Fonctionnalités

### Wrapper Python

- **API** : Accès à certains endpoints Albert (collections, documents, chat, recherche)
- **Gestion automatique des erreurs** : Retry automatique avec backoff exponentiel
- **Upload de fichiers** : Support de multiples formats
- **Chat et RAG** : WORK IN PROGRESS : pas de conservation d'historique de discussion pour le moment. Interrogez vos documents avec recherche sémantique intégrée
- **Recherche avancée** : Recherche dans vos collections de documents
- **Configuration flexible** : Timeouts, retries et paramètres personnalisables

### Interface Web

- **Dashboard** : Vue d'ensemble de l' API (santé, collections, modèles)
- **Gestion des collections** : Créer, visualiser et supprimer des collections (privées/publiques)
- **Gestion des documents** : Upload, recherche, filtrage et suppression avec pagination
- **Interface de chat** : Discutez avec Albert avec ou sans RAG (WORK IN PROGRESS, pas de conservation d'historique de discussion)

## Installation

### Prérequis

- Python 3.12
- Une clé API Albert 

### Installation depuis GitHub

#### Avec pip

```bash
# Cloner le dépôt
git clone https://github.com/hugo-deluca/albert-api-wrapper.git
cd albert-api-wrapper

# Installer le package
pip install -e .

# Ou avec l'interface web
pip install -e ".[web]"

# Ou avec les dépendances de développement
pip install -e ".[dev]"
```

#### Avec uv (recommandé)

```bash
# Cloner le dépôt
git clone https://github.com/hugo-deluca/albert-api-wrapper.git
cd albert-api-wrapper

# Synchroniser les dépendances
uv sync

# Ou avec l'interface web
uv sync --extra web

# Ou avec les dépendances de développement
uv sync --extra dev
```

## Configuration

Créez un fichier `.env` à la racine du projet :

```env
ALBERT_API_KEY=votre_clé_api_ici
ALBERT_API_BASE_URL=https://albert.api.etalab.gouv.fr
SECRET_KEY=votre_clé_secrète_pour_flask
```

Vous pouvez copier le fichier `.env.example` fourni :

```bash
cp .env.example .env
# Puis éditez .env avec vos informations
```

## Utilisation du wrapper Python

### Configuration de base

```python
from albert_wrapper import AlbertAPIWrapper, APIConfig
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
config = APIConfig(
    api_key=os.getenv('ALBERT_API_KEY'),
    base_url=os.getenv('ALBERT_API_BASE_URL'),
    timeout=30,
    max_retries=3,
    retry_delay=1.0
)

# Initialisation
albert = AlbertAPIWrapper(config)
```

### Vérifier la santé de l'API

```python
health = albert.get_health()
print(health)  # {'status': 'ok'}
```

### Gestion des collections

```python
# Lister toutes les collections
collections = albert.get_collections()

# Obtenir une collection spécifique
collection = albert.get_collection(collection_id=123)

# Créer une collection
new_collection = albert.create_collection(
    name="Ma collection",
    description="Description de ma collection"
)
print(new_collection)  # {'id': 456}

# Supprimer une collection
albert.delete_collection(collection_id=456)
```

### Gestion des documents

```python
# Lister les documents
documents = albert.get_documents(
    collection=123,
    limit=20,
    offset=0
)

# Rechercher des documents par nom
documents = albert.get_documents(
    name="rapport.pdf",
    collection=123
)

# Obtenir un document spécifique
document = albert.get_document(document_id=789)

# Upload un document depuis un chemin fichier
result = albert.create_document(
    file_name="rapport.pdf",
    file_path="/chemin/vers/rapport.pdf",
    collection_id=123
)

# Upload un document depuis un objet fichier
result = albert.create_document(
    file_name="Rapport",
    file_path='/chemin/vers/rapport.pdf',
    collection_id=123
)

print(result)  # {'id': 890}

# Supprimer un document
albert.delete_document(document_id=890)
```

### Recherche sémantique

```python
# Rechercher dans des collections
results = albert.search(
    prompt="Quelles sont les mesures de sécurité ?",
    collections=[123, 456],
    limit=5
)

for result in results:
    print(result['chunk']['content'])
    print(result['score'])
```

### Chat avec Albert

WORK IN PROGRESS, pas d'historique de conversation.

```python
# Chat simple
response = albert.chat(
    prompt="Explique-moi la photosynthèse",
    model="albert-small"
)
print(response)

# Chat avec RAG (Retrieval Augmented Generation)
response = albert.chat_with_search(
    prompt="Quels sont les principaux points du rapport ?",
    collections=[123],
    model="albert-large"
)
print(response)
```

### Modèles disponibles

```python
# Lister tous les modèles
models = albert.get_models()
for model in models:
    print(f"{model['id']}: {model['name']}")

# Obtenir un modèle spécifique
model = albert.get_model("albert-large")
```

### Gestion des erreurs

```python
from requests.exceptions import RequestException

try:
    collection = albert.create_collection(name="Test")
except RequestException as e:
    print(f"Erreur API: {e}")
except ValueError as e:
    print(f"Erreur de validation: {e}")
```

## Interface Web

### Lancement

```bash
# Avec la commande installée
albert-ui

# Ou avec uv
uv run albert-ui

# Ou directement avec Python
python -m web_ui.app
```

L'interface sera accessible sur **http://localhost:5000**

### Changement de port

Éditez `web_ui/app.py` :

```python
def main():
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changez le port ici
```

### Fonctionnalités de l'interface

#### Dashboard
- Statut de l'API
- Nombre de collections
- Modèles disponibles
- Accès rapide aux fonctionnalités

#### Collections
- **Visualisation** : Cartes avec badges de visibilité (privé/public)
- **Création** : Modal avec nom et description
- **Suppression** : Confirmation avant suppression
- **Navigation** : Lien direct vers les documents de chaque collection

#### Documents
- **Liste paginée** : 10, 20, 50 ou 100 documents par page
- **Filtrage** : Par collection et nom
- **Recherche** : Recherche en temps réel
- **Upload** : Drag & drop de fichiers (max 16MB)
- **Métadonnées** : Affichage des chunks et date de création
- **Actions** : Suppression avec confirmation

#### Chat

WORK IN PROGRESS. Pas d'historique de conversation conservé.

- **Modèles** : Sélection entre albert-small et albert-large
- **Mode simple** : Chat direct avec Albert
- **Mode RAG** : Recherche dans vos collections sélectionnées

## Tests

### Exécuter les tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/test_wrapper.py

# Tests d'intégration (nécessite ALBERT_API_KEY)
pytest tests/test_integration.py -m integration

# Avec couverture
pytest --cov=albert_wrapper --cov-report=html
```

### Structure des tests

```
tests/
├── test_wrapper.py       # Tests unitaires avec mocks
└── test_integration.py   # Tests d'intégration (API réelle)
```

## Développement

### Structure du projet

```
albert-api-wrapper/
├── albert_wrapper/          # Package principal
│   ├── __init__.py
│   ├── wrapper.py          # Classe principale
│   └── config.py           # Configuration
├── web_ui/                  # Interface web
│   ├── __init__.py
│   ├── app.py              # Application Flask
│   ├── routes.py           # Routes et endpoints
│   ├── templates/          # Templates HTML
│   └── static/             # CSS et JavaScript
├── tests/                   # Tests
├── pyproject.toml          # Configuration du projet
├── README.md               # Ce fichier
└── .env.example            # Exemple de configuration
```

### Contribuer

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -am 'Ajout d'une fonctionnalité'`)
4. Pushez vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## Exemples d'utilisation

### Script complet

```python
#!/usr/bin/env python3
from albert_wrapper import AlbertAPIWrapper, APIConfig
import os

def main():
    # Configuration
    config = APIConfig(
        api_key=os.getenv('ALBERT_API_KEY'),
        base_url='https://albert.api.etalab.gouv.fr'
    )
    albert = AlbertAPIWrapper(config)
    
    # Créer une collection
    collection = albert.create_collection(
        name="Rapports 2024",
        description="Documents importants de l'année"
    )
    collection_id = collection['id']
    print(f"Collection créée : {collection_id}")
    
    # Upload un document
    doc = albert.create_document(
        file_name="rapport.pdf",
        file_path="./rapport.pdf",
        collection_id=collection_id
    )
    print(f"Document uploadé : {doc['id']}")
    
    # Rechercher et discuter
    response = albert.chat_with_search(
        prompt="Résume les points principaux",
        collections=[collection_id],
    )
    print(f"Réponse : {response}")

if __name__ == "__main__":
    main()
```

### L'interface web est-elle sécurisée ?

L'interface est conçue pour un usage local ou interne.

### Puis-je utiliser le wrapper sans l'interface web ?

Le wrapper Python est indépendant. Installez simplement avec `pip install -e .` (ou `uv`) sans l'option `[web]`.

### Comment personnaliser les paramètres de retry ?

```python
config = APIConfig(
    api_key=your_key,
    base_url=base_url,
    max_retries=5,        # Plus de tentatives
    retry_delay=2.0       # Plus de temps entre tentatives
)
```

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
