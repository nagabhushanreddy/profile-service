"""Base HTTP client with retry logic."""

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class BaseHTTPClient:
    """Base HTTP client with retry and error handling."""
    
    def __init__(self, base_url: str, timeout: int = 10, retry_attempts: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        
        if headers is None:
            headers = {}
        
        if correlation_id:
            headers["X-Correlation-Id"] = correlation_id
        
        last_exception = None
        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_data,
                    params=params
                )
                
                if response.status_code < 400:
                    return response.json() if response.content else {}
                
                # Don't retry client errors (4xx)
                if 400 <= response.status_code < 500:
                    logger.error(
                        f"Client error from {url}: {response.status_code}",
                        extra={"correlation_id": correlation_id}
                    )
                    return {"error": response.text, "status_code": response.status_code}
                
                # Retry server errors (5xx)
                logger.warning(
                    f"Server error from {url} (attempt {attempt + 1}/{self.retry_attempts}): {response.status_code}",
                    extra={"correlation_id": correlation_id}
                )
                last_exception = Exception(f"Server error: {response.status_code}")
                
            except httpx.TimeoutException as e:
                logger.warning(
                    f"Timeout calling {url} (attempt {attempt + 1}/{self.retry_attempts})",
                    extra={"correlation_id": correlation_id}
                )
                last_exception = e
            except Exception as e:
                logger.error(
                    f"Error calling {url}: {str(e)}",
                    exc_info=True,
                    extra={"correlation_id": correlation_id}
                )
                last_exception = e
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        raise Exception(f"Failed to call {url} after {self.retry_attempts} attempts")
    
    async def get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET request."""
        return await self._request("GET", path, **kwargs)
    
    async def post(self, path: str, **kwargs) -> Dict[str, Any]:
        """POST request."""
        return await self._request("POST", path, **kwargs)
    
    async def patch(self, path: str, **kwargs) -> Dict[str, Any]:
        """PATCH request."""
        return await self._request("PATCH", path, **kwargs)
    
    async def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        """DELETE request."""
        return await self._request("DELETE", path, **kwargs)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
