import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class HttpClientManager:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
            )
        return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client is not None and not cls._client.is_closed:
            await cls._client.aclose()
            cls._client = None

async def get_http_client() -> httpx.AsyncClient:
    return await HttpClientManager.get_client()
