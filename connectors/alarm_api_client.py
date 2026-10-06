import uuid
from typing import Any

import httpx


class AlarmApiError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class AlarmApiClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _headers(self, trace_id: str | None = None) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "trace_id": trace_id or str(uuid.uuid4()),
            "x-client-id": "alarm-copilot-mcp",
            "x-metadata-tag": "copilot",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"

        last_error = None

        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self._headers(trace_id),
                        params=params,
                        json=json,
                    )

                if response.status_code >= 500 and attempt < 2:
                    continue

                if response.status_code >= 400:
                    detail = response.text[:500]
                    raise AlarmApiError(response.status_code, detail)

                return response.json()

            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt == 2:
                    raise AlarmApiError(504, "Alarm API request timed out") from exc

            except httpx.RequestError as exc:
                last_error = exc
                if attempt == 2:
                    raise AlarmApiError(503, "Alarm API unavailable") from exc

        raise AlarmApiError(503, "Alarm API request failed") from last_error

    async def search_assets(self, query: str, limit: int = 10):
        return await self.request(
            "GET",
            "/assets/search",
            params={"query": query, "limit": limit},
        )

    async def get_metadata(self, asset_id: str):
        return await self.request(
            "GET",
            f"/assets/{asset_id}/metadata",
        )

    async def get_alarms(
        self,
        asset_id: str,
        status: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ):
        params = {
            "asset_id": asset_id,
            "page": page,
            "page_size": page_size,
            "sort_by": "start_time",
            "sort_order": "desc",
        }

        if status:
            params["status"] = status

        return await self.request("GET", "/alarms", params=params)

    async def priority_score(self, alarm_id: str):
        return await self.request(
            "POST",
            "/alarms/priority-score",
            json={"alarm_id": alarm_id},
        )

    async def recommendations(self, alarm_id: str):
        return await self.request(
            "POST",
            "/recommendations/operator-actions",
            json={
                "alarm_id": alarm_id,
                "include_related": True,
                "include_asset_context": True,
                "include_historical_pattern": True,
            },
        )

    async def correlation(self, asset_ids: list[str]):
        return await self.request(
            "POST",
            "/alarms/correlation",
            json={
                "asset_ids": asset_ids,
                "correlation_method": "cooccurrence",
                "lag_window_minutes": 15,
                "severity_threshold": "medium",
                "min_support": 1,
            },
        )
