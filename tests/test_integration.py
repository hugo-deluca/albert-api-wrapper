import pytest
import os

from albert_wrapper import AlbertAPIWrapper, APIConfig

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('ALBERT_API_KEY'),
    reason="Requires ALBERT_API_KEY environment variable"
)
class TestRealAPI:
    @pytest.fixture
    def real_wrapper(self):
        config = APIConfig(
            api_key=os.getenv('ALBERT_API_KEY'),
            base_url='https://albert.api.etalab.gouv.fr'
        )
        return AlbertAPIWrapper(config)
    
    def test_health_endpoint(self, real_wrapper):
        result = real_wrapper.get_health()
        assert result['status'] == 'ok'
    
    def test_get_models(self, real_wrapper):
        models = real_wrapper.get_models()
        assert len(models) > 0
        assert all('id' in model for model in models)