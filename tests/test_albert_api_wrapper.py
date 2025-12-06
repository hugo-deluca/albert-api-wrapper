# pytest -m "not integration"
import pytest
from unittest.mock import Mock, patch, mock_open
import requests

from albert_wrapper import AlbertAPIWrapper, APIConfig

@pytest.fixture
def config():
    return APIConfig(
        api_key="test_key_123",
        base_url="https://api.example.com",
        timeout=30,
        max_retries=3
    )

@pytest.fixture
def wrapper(config):
    return AlbertAPIWrapper(config)

class TestHealthEndpoint:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_get_health_success(self, mock_request, wrapper):
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_request.return_value = mock_response
        
        # Act
        result = wrapper.get_health()
        
        # Assert
        assert result == {"status": "ok"}
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert kwargs['headers']['Authorization'] == "Bearer test_key_123"

class TestModels:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_get_models_returns_list(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': 'albert-small', 'name': 'Albert Small'},
                {'id': 'albert-large', 'name': 'Albert Large'}
            ]
        }
        mock_request.return_value = mock_response
        
        result = wrapper.get_models()
        
        assert len(result) == 2
        assert result[0]['id'] == 'albert-small'

    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_get_model_by_id(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 'albert-small', 'name': 'Albert Small'}
        mock_request.return_value = mock_response
        
        result = wrapper.get_model('albert-small')
        
        assert result['id'] == 'albert-small'
        # Verify correct endpoint was called
        args, kwargs = mock_request.call_args
        assert 'v1/models/albert-small' in args[1]

class TestCollections:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_create_collection(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 15560}
        mock_request.return_value = mock_response
        
        result = wrapper.create_collection('test_collection', 'test description')
        
        assert result['id'] == 15560
        args, kwargs = mock_request.call_args
        assert kwargs['json']['name'] == 'test_collection'
        assert kwargs['json']['description'] == 'test description'

    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_delete_collection_returns_empty(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_request.return_value = mock_response
        
        result = wrapper.delete_collection(123)
        
        assert result == {}

class TestDocuments:
    @patch('albert_wrapper.albert_api_wrapper.os.path.exists')
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake file content')
    def test_create_document_uploads_file(self, mock_open_file, mock_request, mock_exists, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': 769918}
        mock_request.return_value = mock_response
        
        result = wrapper.create_document(
            'test.pdf',
            '/path/to/test.pdf',
            collection_id=783
        )
        
        assert result['id'] == 769918
        args, kwargs = mock_request.call_args
        assert kwargs['files'] is not None
        assert kwargs['data']['collection'] == 783
    
    @patch('albert_wrapper.albert_api_wrapper.os.path.exists')
    def test_create_document_raises_when_file_not_found(self, mock_exists, wrapper):
        mock_exists.return_value = False
        
        with pytest.raises(ValueError, match="File not found: /nonexistent/file.pdf"):
            wrapper.create_document(
                'test.pdf',
                '/nonexistent/file.pdf',
                collection_id=783
            )
        
        mock_exists.assert_called_once_with('/nonexistent/file.pdf')

class TestRetryLogic:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    @patch('albert_wrapper.albert_api_wrapper.time.sleep')  # Mock sleep to speed up tests
    def test_retries_on_failure(self, mock_sleep, mock_request, wrapper):
        # Simulate 2 failures then success
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError()
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"status": "ok"}
        
        mock_request.side_effect = [
            requests.exceptions.ConnectionError(),
            requests.exceptions.ConnectionError(),
            mock_response_success
        ]
        
        result = wrapper.get_health()
        
        assert result == {"status": "ok"}
        assert mock_request.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_raises_after_max_retries(self, mock_request, wrapper):
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(requests.exceptions.ConnectionError):
            wrapper.get_health()
        
        assert mock_request.call_count == 4  # initial + 3 retries

class TestChat:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_chat_returns_content(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {'message': {'content': 'Bonjour! Comment puis-je vous aider?'}}
            ]
        }
        mock_request.return_value = mock_response
        
        result = wrapper.chat('Bonjour')
        
        assert result == 'Bonjour! Comment puis-je vous aider?'
        args, kwargs = mock_request.call_args
        assert kwargs['json']['messages'][0]['content'] == 'Bonjour'
        assert kwargs['json']['model'] == 'albert-small'

    @patch.object(AlbertAPIWrapper, 'search')
    @patch.object(AlbertAPIWrapper, 'chat')
    def test_chat_with_search_combines_results(self, mock_chat, mock_search, wrapper):
        mock_search.return_value = [
            {'chunk': {'content': 'Document 1 content'}},
            {'chunk': {'content': 'Document 2 content'}}
        ]
        mock_chat.return_value = 'Response based on documents'
        
        result = wrapper.chat_with_search('question', collections=[783])
        
        assert result == 'Response based on documents'
        mock_search.assert_called_once()
        mock_chat.assert_called_once()
        # Verify the prompt includes the chunks
        call_args = mock_chat.call_args[0][0]
        assert 'Document 1 content' in call_args
        assert 'Document 2 content' in call_args

class TestEdgeCases:
    @patch('albert_wrapper.albert_api_wrapper.requests.request')
    def test_handles_non_json_response(self, mock_request, wrapper):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'plain text response'
        mock_response.json.side_effect = ValueError("Not JSON")
        mock_response.text = 'plain text response'
        mock_request.return_value = mock_response
        
        result = wrapper.get_health()
        
        assert result == {"raw": "plain text response"}

    def test_guess_mime_type(self, wrapper):
        assert wrapper._guess_mime_type('file.pdf') == 'application/pdf'
        assert wrapper._guess_mime_type('file.txt') == 'text/plain'
        assert wrapper._guess_mime_type('file.unknown') == 'application/octet-stream'