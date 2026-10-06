import os
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from connectors.alarm_api_client import AlarmApiClient, AlarmApiError

load_dotenv()

mcp = FastMCP("Alarm Management MCP Server")

client = AlarmApiClient(
    base_url=os.getenv("ALARM_API_BASE_URL", "http://127.0.0.1:8000"),
    token=os.getenv("ALARM_API_TOKEN", "demo-token"),
    timeout=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10")),
)


def map_error(exc: AlarmApiError) -> RuntimeError:
    if exc.status_code == 401:
        return RuntimeError("Alarm API authentication failed")
    if exc.status_code == 404:
        return RuntimeError("Requested alarm or asset was not found")
    if exc.status_code == 504:
        return RuntimeError("Alarm API timed out")
    return RuntimeError("Alarm API request failed")


@mcp.tool()
async def asset_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Search for plant assets by name, type, or description."""
    if not query.strip():
        raise ValueError("query must not be empty")

    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    try:
        return await client.search_assets(query.strip(), limit)
    except AlarmApiError as exc:
        raise map_error(exc) from exc


@mcp.tool()
async def asset_metadata(asset_id: str) -> dict[str, Any]:
    """Retrieve asset metadata and related assets."""
    if not asset_id.strip():
        raise ValueError("asset_id must not be empty")

    try:
        return await client.get_metadata(asset_id)
    except AlarmApiError as exc:
        raise map_error(exc) from exc


@mcp.tool()
async def alarm_retrieval(
    asset_id: str,
    status: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
    """Retrieve historical or active alarms for an asset."""
    if not asset_id.strip():
        raise ValueError("asset_id must not be empty")

    if page < 1:
        raise ValueError("page must be greater than zero")

    if page_size < 1 or page_size > 200:
        raise ValueError("page_size must be between 1 and 200")

    try:
        return await client.get_alarms(
            asset_id=asset_id,
            status=status,
            page=page,
            page_size=page_size,
        )
    except AlarmApiError as exc:
        raise map_error(exc) from exc


@mcp.tool()
async def alarm_priority_score(alarm_id: str) -> dict[str, Any]:
    """Calculate priority score for a specific alarm."""
    if not alarm_id.strip():
        raise ValueError("alarm_id must not be empty")

    try:
        return await client.priority_score(alarm_id)
    except AlarmApiError as exc:
        raise map_error(exc) from exc


@mcp.tool()
async def operator_recommendations(alarm_id: str) -> dict[str, Any]:
    """Retrieve recommended operator actions and likely causes."""
    if not alarm_id.strip():
        raise ValueError("alarm_id must not be empty")

    try:
        return await client.recommendations(alarm_id)
    except AlarmApiError as exc:
        raise map_error(exc) from exc


@mcp.tool()
async def alarm_correlation(asset_ids: list[str]) -> dict[str, Any]:
    """Correlate alarms across related assets."""
    if not asset_ids:
        raise ValueError("asset_ids must not be empty")

    try:
        return await client.correlation(asset_ids)
    except AlarmApiError as exc:
        raise map_error(exc) from exc


if __name__ == "__main__":

    # mcp.settings.host = "127.0.0.1"  # without docker, run
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9000
    mcp.run(transport="sse")
