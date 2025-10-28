from backend.src.integration import MoodleConfig

from backend.src.integration.client import (
    APIClient,
    APICallingException
)


async def test_api_client_authentication(config: MoodleConfig) -> None:
    client = APIClient(config)
    await client.authenticate()
    assert client.token is not None, 'authentication token should not be None after successful authentication'


async def test_api_client_site_info(config: MoodleConfig) -> None:
    client = APIClient(config)
    await client.authenticate()
    site_info = await client.sync_site_info()
    assert site_info is not None, 'site info should not be None after successful retrieval'
    assert site_info.username == config.username, 'site info username should match the configured username'


async def test_api_client_invalid_endpoint(config: MoodleConfig) -> None:
    client = APIClient(config)
    await client.authenticate()
    try:
        await client._make_request('invalid_endpoint')
    except APICallingException as e:
        assert e.code == 1002, 'APICallingException code should be 1002 for invalid endpoint'
