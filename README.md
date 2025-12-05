# Albert API Wrapper - Documentation

## Introduction

Cette bibliothèque Python est un wrapper pour l'API Albert, développée pour faciliter l'intégration des fonctionnalités d'Albert dans vos applications. Albert est un service souverain d'intelligence artificielle générative.

## Fonctionnalités Principales

### 1. Gestion des Collections et Documents

- **Création/gestion de collections** : Organisez vos documents en collections personnalisées
- **Upload de documents** : Téléchargez des fichiers dans vos collections
- **Recherche dans les documents** : Trouvez des informations spécifiques dans vos documents

### 2. Fonctionnalités d'OCR (WORK IN PROGRESS)

- **Extraction de texte depuis des PDF** : Utilisez la reconnaissance optique de caractères (OCR) pour extraire du texte depuis des documents scannés
- **Personnalisation du traitement OCR** :
  - Choix du modèle OCR
  - Réglage de la résolution (DPI)
  - Personnalisation du prompt d'extraction

### 3. Interactions avec l'IA

- **Génération de texte** : Posez des questions à l'IA Albert
- **Chat avec recherche intégrée** : Combinez les réponses de l'IA avec des résultats de recherche dans vos documents

### 4. Fonctionnalités Avancées

- **Gestion des modèles** : Accès aux différents modèles disponibles
- **Vérification de santé de l'API** : Vérifiez la disponibilité du service

## Installation

Nous vous recommandons d'utiliser uv pour gérer vos environnements.
```bash
uv sync
```

## Configuration

Créez un fichier .env à la racine de votre projet avec votre clé API :
```
ALBERT_API_KEY=votre_cle_api
```

Configurez le wrapper :

```python
from albert_wrapper import APIConfig, AlbertAPIWrapper

config = APIConfig(
    api_key=os.getenv('ALBERT_API_KEY'),
    base_url='https://albert.api.etalab.gouv.fr'
)
albert = AlbertAPIWrapper(config)
```
## Utilisation
### Ouverture de session et vérification

```python
# Vérifier la santé de l'API
health = albert.get_health()
print(health)  # Devrait retourner {"status": "ok"}
```

### Gestion des collections
```python
# Créer une nouvelle collection
collection = albert.create_collection(
    name="Documents RH",
    description="Contient les documents relatifs aux ressources humaines"
)
```
```python
# Lister les collections
collections = albert.get_collections()
```

### Upload et gestion de documents

```python
# Upload d'un document
document = albert.create_document(
    file_name="contrat.pdf",
    file_path="/chemin/vers/fichier/contrat.pdf",
    collection_id=123
)

# Rechercher dans les documents
results = albert.search(
    prompt="quel est le processus de recrutement",
    collections=[123]
)
```

### Fonctionnalités OCR (WORK IN PROGRESS)

WIP.

### Interactions avec l'IA

```python
# Obtenir une réponse de l'IA
response = albert.chat(
    prompt="Expliquez-moi la politique de confidentialité de l'entreprise",
    model="albert-large"
)

# Chat avec résultats de recherche intégrés
search_chat = albert.chat_with_search(
    prompt="Quelles sont les conditions de congés payés ?",
    collections=[456],  # ID de la collection contenant les documents RH
    model="albert-large"
)
```

### Paramètres Avancés

Pour les fonctions OCR, vous pouvez personnaliser :

- Modèle OCR : Choisissez entre différents modèles disponibles
- Résolution (DPI) : Réglage entre 100 et 600 (par défaut 150)
- Prompt personnalisé : Adaptez l'instruction donnée au modèle OCR

### Gestion des Erreurs

Le wrapper gère automatiquement :

- Les erreurs de connexion
- Les erreurs de timeout
- Les réponses HTTP erronées

Avec un mécanisme de retry automatique configurable.

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

- Forkez le dépôt
- Créez une branche pour votre fonctionnalité (`git checkout -b feature AmazingFeature`)
- Commitez vos modifications (`git commit -m 'Ajout feature'`)
- Poussez la branche (git push origin feature/AmazingFeature)
- Ouvrez une Pull Request

## Bonnes Pratiques

### Gestion des clés API :
- Ne jamais commiter vos clés API dans le code
- Utilisez toujours le fichier .env pour la configuration

### Gestion des erreurs :

```python
try:
    result = albert.chat(prompt="Ma question")
except Exception as e:
    print(f"Erreur lors de la requête à l'API: {str(e)}")
```

### Exemples d'Utilisation Avancée

Intégration avec un service web

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
albert = AlbertAPIWrapper(config)  # Initialisation préalable

@app.route('/ask-albert', methods=['POST'])
def ask_albert():
    data = request.json
    question = data.get('question')
    collection_id = data.get('collection_id', 0)

    if not question:
        return jsonify({"error": "Question manquante"}), 400

    try:
        # Utilisez la recherche avec le chat pour une réponse plus précise
        response = albert.chat_with_search(
            prompt=question,
            collections=[collection_id] if collection_id else [],
            model="albert-large"
        )
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

Traitement par lots de documents

```python
def process_documents(collection_id, file_paths):
    results = []

    for file_path in file_paths:
        try:
            document = albert.create_document(
                file_name=os.path.basename(file_path),
                file_path=file_path,
                collection_id=collection_id
            )
            results.append({
                "file": file_path,
                "status": "success",
                "document_id": document.get("id")
            })
        except Exception as e:
            results.append({
                "file": file_path,
                "status": "error",
                "message": str(e)
            })

    return results
```

### Planification de Maintenance

Mises à jour :
- Vérifiez régulièrement les nouvelles versions du wrapper
- Consultez la documentation officielle d'Albert pour les changements d'API

Optimisation :
- Suivez les performances de votre application
- Ajustez les paramètres timeout et retry selon vos besoins

## Support et Documentation

Pour plus d'informations :

- Consultez la documentation officielle d'Albert
- Vérifiez les exemples inclus dans le dépôt

## License

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
