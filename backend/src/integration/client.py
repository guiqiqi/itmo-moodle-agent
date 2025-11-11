import aiohttp
from pydantic import BaseModel, TypeAdapter

from backend.src.integration import (
    IntegrationException,
    MoodleConfig,
    logger,
    Course
)

import typing as t
import typing_extensions as te


class AuthenticationForm(BaseModel):
    """Authentication form model."""
    username: str
    password: str
    service: str


class SiteInfo(BaseModel):
    """Site information model."""
    sitename: str
    username: str
    firstname: str
    lastname: str
    userid: int


class Token(BaseModel):
    """Authentication token model."""
    token: str | None = None
    error: t.Optional[str] | None = None


class AuthenticationException(IntegrationException):
    """Exception raised for authentication errors."""
    _code: int = 1001


class UnSynchronizedSiteInfo(IntegrationException):
    """Exception when API calling without syncornized siteinfo."""
    _code: int = 1002


class APICallingException(IntegrationException):
    """Exception raised for API calling errors."""
    _code: int = 1010


class APIClient:

    def __init__(self, config: MoodleConfig) -> None:
        self.config = config
        self.token: t.Optional[str] = None
        self.site: t.Optional[SiteInfo] = None
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    async def __aenter__(self) -> te.Self:
        """Prepare an authenticated client for using."""
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        await self.authenticate()
        await self.sync_site_info()
        return self

    async def __aexit__(self, *_) -> None:
        await self.session.close()

    async def authenticate(self) -> str:
        """Authenticate with Moodle and obtain a token."""
        token_url = f'{self.config.base_url}/login/token.php'
        auth_form = AuthenticationForm(
            username=self.config.username,
            password=self.config.password,
            service=self.config.service
        )
        async with self.session.get(token_url, params=auth_form.model_dump()) as resp:
            if resp.status != 200:
                logger.error(
                    f'authentication failed with status code {resp.status}')
                raise AuthenticationException(
                    'failed to authenticate with Moodle')
            data = await resp.json()
            token = Token(**data)
            if token.error:
                logger.error(f'authentication error: {token.error}')
                raise AuthenticationException(
                    f'authentication error: {token.error}')
            logger.info('successfully authenticated with Moodle')
            self.token = token.token
            assert self.token is not None
            return self.token

    async def sync_site_info(self) -> SiteInfo:
        """Retrieve site information."""
        data = await self._make_request('core_webservice_get_site_info')
        site_info = SiteInfo(**data)
        self.site = site_info
        return site_info

    async def _make_request(self, endpoint: str, params: t.Dict[str, t.Any] | None = None) -> t.Any:
        """Make an authenticated request to the Moodle API."""
        if not self.token:
            raise AuthenticationException('not authenticated')
        api_url = f'{self.config.base_url}/webservice/rest/server.php'

        if params is None:
            params = {}
        params.update({
            'wstoken': self.token,
            'moodlewsrestformat': 'json',
            'wsfunction': endpoint
        })

        async with self.session.get(api_url, params=params) as resp:
            if resp.status == 401 or resp.status == 403:
                logger.error('authentication token is invalid or expired')
                raise AuthenticationException(
                    'authentication token is invalid or expired')
            if resp.status != 200:
                logger.error(
                    f'API request to {endpoint} failed with status code {resp.status}')
                raise APICallingException(
                    f'API request to {endpoint} failed')
            try:
                data = await resp.json()
                return data
            except aiohttp.ContentTypeError as e:
                logger.error(
                    f'failed to parse JSON response from {endpoint}: {e}')
                raise APICallingException(
                    f'failed to parse JSON response from {endpoint}') from e

    async def get_courses(self) -> t.List[Course]:
        """Get all courses for current user."""
        if not self.site:
            raise UnSynchronizedSiteInfo(
                f'cannot obtain userid from site info: {self.site}')
        response = await self._make_request(
            endpoint='core_enrol_get_users_courses',
            params={'userid': self.site.userid}
        )
        return TypeAdapter(t.List[Course]).validate_python(response)
