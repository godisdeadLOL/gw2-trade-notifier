import logging
import httpx
from httpx_retries import Retry, RetryTransport

retry_transport = RetryTransport(retry=Retry(total=3, backoff_factor=0.5))


def get_client(access_token: str | None = None):
    headers = {}

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    return httpx.AsyncClient(base_url="https://api.guildwars2.com", headers=headers, transport=retry_transport)
