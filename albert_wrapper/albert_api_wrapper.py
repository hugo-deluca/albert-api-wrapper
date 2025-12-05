import os
import mimetypes
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import requests
from dotenv import load_dotenv

from .config import APIConfig

load_dotenv()

@dataclass
class APIConfig:
    """Configuration for the Albert API connection.

    Attributes:
        api_key (str): API key for authentication
        base_url (str): Base URL of the Albert API
        timeout (int): Request timeout in seconds (default: 30)
        max_retries (int): Maximum number of retry attempts (default: 3)
        retry_delay (float): Delay between retries in seconds (default: 1.0)
    """
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0

class AlbertAPIWrapper:
    """A Python wrapper for interacting with Albert via API.

    This class provides methods to send requests to Albert API and handle responses.
    Includes functionality for health checks, model management, collections, documents,
    search, and chat completions.
    """

    # API endpoints
    COLLECTIONS_ENDPOINT = 'v1/collections'
    DOCUMENTS_ENDPOINT = 'v1/documents'
    CHAT_ENDPOINT = 'v1/chat/completions'
    MODELS_ENDPOINT = 'v1/models'
    HEALTH_ENDPOINT = 'health'
    SEARCH_ENDPOINT = 'v1/search'
    OCR_ENDPOINT = 'v1/ocr-beta'

    def __init__(self, config: APIConfig):
        """Initialize the API wrapper with configuration.

        Args:
            config (APIConfig): Configuration object containing API details
        """
        self.config = config
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_key}"
        }

    def _guess_mime_type(self, file_name: str) -> str:
        """Guess the MIME type of a file based on its name.

        Args:
            file_name (str): Name of the file

        Returns:
            str: MIME type or 'application/octet-stream' if not detected
        """
        mime_type, _ = mimetypes.guess_type(file_name)
        return mime_type or "application/octet-stream"

    def _make_request(
        self,
        endpoint: str,
        method: str = 'GET',
        payload: Optional[Dict[str, Any]] = None,
        files: Optional[Dict] = None,
        retry_count: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a request to the Albert API with retry logic.

        Args:
            endpoint (str): API endpoint
            method (str): HTTP method (default: 'GET')
            payload (Dict[str, Any], optional): Request payload
            files (Dict, optional): Files to upload
            retry_count (int): Current retry count (used internally for retries)

        Returns:
            Dict[str, Any]: API response

        Raises:
            requests.exceptions.RequestException: If the request fails after all retries
        """
        url = f"{self.config.base_url}/{endpoint}"

        try:
            if files:
                # Remove content-type header to avoid 422 errors
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}"
                }
                response = requests.request(
                    'POST',
                    url,
                    headers=headers,
                    data=payload,
                    files=files,
                    timeout=self.config.timeout,
                    **kwargs
                )
            else:
                response = requests.request(
                    method,
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.config.timeout,
                    **kwargs
                )

            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}

            response.raise_for_status()

            # Try parsing JSON, but don't trigger retries on JSON errors
            try:
                return response.json()
            except ValueError:
                return {"raw": response.text}

        except requests.exceptions.RequestException as e:
            if retry_count < self.config.max_retries:
                time.sleep(self.config.retry_delay * (retry_count + 1))
                return self._make_request(
                    endpoint,
                    method,
                    payload,
                    files,
                    retry_count + 1,
                    **kwargs
                )
            raise e

    # =============================================
    # HEALTH CHECKS
    # =============================================

    def get_health(self) -> Dict[str, Any]:
        """Retrieve the health status of the API.

        Returns:
            Dict[str, Any]: Health status information
        Returns:
            Dict[str, Any]: Health status information
        """
        return self._make_request(self.HEALTH_ENDPOINT)

    # =============================================
    # MODELS
    # =============================================

    def get_models(self) -> List[Dict[str, Any]]:
        """Retrieve the list of available models from the API.

        Returns:
            List[Dict[str, Any]]: List of model information dictionaries
        """
        response = self._make_request(self.MODELS_ENDPOINT)
        return response.get('data', [])

    def get_model(self, model_id: str) -> Dict[str, Any]:
        """Retrieve details of a specific model from the API.

        Args:
            model_id (str): ID of the model to retrieve

        Returns:
            Dict[str, Any]: Model details
        """
        endpoint = f"{self.MODELS_ENDPOINT}/{model_id}"
        return self._make_request(endpoint)

    # =============================================
    # COLLECTIONS
    # =============================================

    def get_collections(self) -> List[Dict[str, Any]]:
        """Retrieve the list of collections from the API.

        Returns:
            List[Dict[str, Any]]: List of collection information dictionaries
        """
        response = self._make_request(self.COLLECTIONS_ENDPOINT)
        return response.get('data', [])

    def get_collection(self, collection_id: int) -> Dict[str, Any]:
        """Retrieve details of a specific collection.

        Args:
            collection_id (int): ID of the collection to retrieve

        Returns:
            Dict[str, Any]: Collection details
        """
        endpoint = f"{self.COLLECTIONS_ENDPOINT}/{collection_id}"
        return self._make_request(endpoint)

    def create_collection(self, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new collection in the API.

        Args:
            name (str): Name of the collection
            description (str, optional): Description of the collection

        Returns:
            Dict[str, Any]: Response containing the created collection ID
        """
        endpoint = self.COLLECTIONS_ENDPOINT
        data = {
            'name': name,
            'description': description
        }
        return self._make_request(endpoint, 'POST', payload=data)

    def delete_collection(self, collection_id: int) -> Dict[str, Any]:
        """Delete a collection from the API.

        Args:
            collection_id (int): ID of the collection to delete

        Returns:
            Dict[str, Any]: Empty response on success
        """
        endpoint = f"{self.COLLECTIONS_ENDPOINT}/{collection_id}"
        return self._make_request(endpoint, 'DELETE')

    # =============================================
    # DOCUMENTS
    # =============================================

    def get_documents(
        self,
        name: Optional[str] = None,
        collection: int = 0,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve documents from the API with optional filtering.

        Args:
            name (str, optional): Name of the document to filter by
            collection (int): Collection ID to filter by (0 for all collections)
            limit (int): Maximum number of documents to return
            offset (int): Offset for pagination

        Returns:
            List[Dict[str, Any]]: List of document information dictionaries
        """
        endpoint = f"{self.DOCUMENTS_ENDPOINT}"
        params = {
            'name': name or '',
            'collection': collection,
            'limit': limit,
            'offset': offset
        }
        response = self._make_request(endpoint, 'GET', params=params)
        return response.get('data', [])

    def get_document(self, document_id: int) -> Dict[str, Any]:
        """Retrieve details of a specific document.

        Args:
            document_id (int): ID of the document to retrieve

        Returns:
            Dict[str, Any]: Document details
        """
        endpoint = f"{self.DOCUMENTS_ENDPOINT}/{document_id}"
        return self._make_request(endpoint)

    def create_document(
        self,
        file_name: str,
        file_path: str,
        collection_id: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Upload a file to create a new document.

        Args:
            file_name (str): Name of the file
            file_path (str): Path to the file
            collection_id (int): ID of the collection to add the document to
            **kwargs: Additional parameters for the API request

        Returns:
            Dict[str, Any]: Response containing the created document ID
        """
        mime_type = self._guess_mime_type(file_name)
        endpoint = self.DOCUMENTS_ENDPOINT
        data = {
            'collection': collection_id
        }
        files = {
            "file": (file_name, open(file_path, "rb"), mime_type)
        }
        return self._make_request(
            endpoint,
            'POST',
            payload=data,
            files=files,
            **kwargs
        )

    def delete_document(self, document_id: int) -> Dict[str, Any]:
        """Delete a document from the API.

        Args:
            document_id (int): ID of the document to delete

        Returns:
            Dict[str, Any]: Empty response on success
        """
        endpoint = f"{self.DOCUMENTS_ENDPOINT}/{document_id}"
        return self._make_request(endpoint, 'DELETE')

    # =============================================
    # OCR (OPTICAL CHARACTER RECOGNITION)
    # =============================================
    # FIXME? Error 500 when requesting this endpoint

    def ocr_document(
        self,
        file_path: str,
        model: str = 'albert-large',
        dpi: int = 150,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract text from PDF files using OCR.

        Args:
            file_path (str): Path to the PDF file to process
            model (str): The OCR model to use
            dpi (int): DPI for image rendering (100-600, default: 150)
            prompt (str, optional): Custom prompt for OCR processing

        Returns:
            Dict[str, Any]: OCR results containing extracted text

        Raises:
            ValueError: If file_path doesn't exist or dpi is out of range
            requests.exceptions.RequestException: If the API request fails
        """
        # Validate input parameters
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        if not (100 <= dpi <= 600):
            raise ValueError("DPI must be between 100 and 600")

        # Default prompt if none provided
        default_prompt = (
            "Tu es un système d'OCR très précis. Extrait tout le texte visible de cette image. "
            "Ne décris pas l'image, n'ajoute pas de commentaires. Réponds uniquement avec le texte brut extrait, "
            "en préservant les paragraphes, la mise en forme et la structure du document. "
            "Si aucun texte n'est visible, réponds avec 'Aucun texte détecté'. "
            "Je veux une sortie au format markdown. Tu dois respecter le format de sortie pour bien conserver les tableaux."
        )
        prompt = prompt or default_prompt

        # Prepare the file data
        file_name = os.path.basename(file_path)
        mime_type = self._guess_mime_type(file_name)

        # Prepare the form data
        data = {
            'model': model,
            'dpi': dpi,
            'prompt': prompt
        }

        files = {
            'file': (file_name, open(file_path, 'rb'), mime_type)
        }

        # Make the API request
        try:
            response = self._make_request(
                self.OCR_ENDPOINT,
                method='POST',
                payload=data,
                files=files
            )

            # Extract and return the text content
            return response
        finally:
            # Ensure the file is closed
            if 'file' in files:
                files['file'][1].close()
    
    # =============================================
    # SEARCH
    # =============================================

    def search(
        self,
        prompt: str,
        collections: List[int],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Search documents in specified collections.

        Args:
            prompt (str): Search query
            collections (List[int]): List of collection IDs to search in
            **kwargs: Additional search parameters

        Returns:
            List[Dict[str, Any]]: List of search results with chunks and scores
        """
        endpoint = self.SEARCH_ENDPOINT
        data = {
            'prompt': prompt,
            'collections': collections,
            **kwargs
        }
        response = self._make_request(endpoint, 'POST', payload=data)
        return response.get('data', [])

    # =============================================
    # CHAT COMPLETIONS
    # =============================================

    def chat(
        self,
        prompt: str,
        model: str = 'albert-small',
        **kwargs
    ) -> str:
        """Get a chat response from the specified model.

        Args:
            prompt (str): User message
            model (str): Model to use for completion (default: 'albert-small')
            **kwargs: Additional chat parameters

        Returns:
            str: Model's response as plain text
        """
        endpoint = self.CHAT_ENDPOINT
        data = {
            'messages': [{'role': 'user', 'content': prompt}],
            'model': model,
            **kwargs
        }
        response = self._make_request(endpoint, 'POST', payload=data)
        return response.get('choices', [{}])[0].get('message', {}).get('content', '')

    def chat_with_search(
        self, 
        prompt: str, 
        collections: List[int],
        model: str = 'albert-large',
        search_kwargs: dict = None,
        chat_kwargs: dict = None
    ) -> str:
        """
        Returns Albert's response based on search results from specified collections.
        
        Args:
            prompt: The question to answer
            collections: List of collection IDs to search
            model: Model to use for chat
            search_kwargs: Additional parameters for search (e.g., limit, method)
            chat_kwargs: Additional parameters for chat (e.g., temperature, max_tokens)
        """
        search_kwargs = search_kwargs or {}
        chat_kwargs = chat_kwargs or {}
        
        search_results = self.search(prompt, collections, **search_kwargs)
        
        prompt_template = "Réponds à la question suivante en te basant sur les documents ci-dessous : {prompt}\n\nDocuments :\n{chunks}"
        chunks = "\n\n\n".join([result["chunk"]["content"] for result in search_results])
        augmented_prompt = prompt_template.format(prompt=prompt, chunks=chunks)
        
        chat_response = self.chat(augmented_prompt, model, **chat_kwargs)
        return chat_response
