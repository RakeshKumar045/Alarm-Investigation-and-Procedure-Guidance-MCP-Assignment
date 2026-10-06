import asyncio

from mcp import ClientSession
from mcp.client.sse import sse_client



async def discover_tools():
    async with sse_client(
            "http://127.0.0.1:9000/sse"
    ) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            return [tool.name for tool in result.tools]


def test_mcp_tool_discovery():
    tools = asyncio.run(discover_tools())

    assert "asset_search" in tools
    assert "asset_metadata" in tools
    assert "alarm_retrieval" in tools
    assert "alarm_priority_score" in tools
    assert "operator_recommendations" in tools
