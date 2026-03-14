"""HTTP client utilities."""
import httpx
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential


class HTTPClient:
    """Async HTTP client with retry logic."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def get(
        self,
        url: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> httpx.Response:
        """Send GET request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    async def post(
        self,
        url: str,
        data: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> httpx.Response:
        """Send POST request."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response

    async def download(
        self,
        url: str,
        headers: Optional[dict] = None,
    ) -> bytes:
        """Download binary content."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        response = await self._client.get(url, headers=headers)
        response.raise_for_status()
        return response.content


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
async def fetch_with_retry(
    url: str,
    method: str = "GET",
    **kwargs,
) -> httpx.Response:
    """Fetch URL with automatic retry."""
    async with HTTPClient() as client:
        if method.upper() == "GET":
            return await client.get(url, **kwargs)
        elif method.upper() == "POST":
            return await client.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")


async def download_file(url: str, dest_path: str, headers: Optional[dict] = None):
    """Download file to disk."""
    async with HTTPClient() as client:
        content = await client.download(url, headers=headers)

        with open(dest_path, "wb") as f:
            f.write(content)
