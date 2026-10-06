import asyncio
import json

import pytest
from mcp import ClientSession
from mcp.client.sse import sse_client

from rag.retrieval import RagRetriever


MCP_URL = "http://127.0.0.1:9000/sse"


async def run_mcp_workflow():
    async with sse_client(MCP_URL) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]

            assert "asset_search" in tool_names
            assert "alarm_retrieval" in tool_names
            assert "operator_recommendations" in tool_names

            asset_result = await session.call_tool(
                "asset_search",
                arguments={
                    "query": "Boiler Feed Pump 101",
                    "limit": 10,
                },
            )

            asset_payload = json.loads(
                asset_result.content[0].text
            )

            asset_id = asset_payload["results"][0]["asset_id"]

            alarm_result = await session.call_tool(
                "alarm_retrieval",
                arguments={
                    "asset_id": asset_id,
                    "status": "active",
                    "page": 1,
                    "page_size": 50,
                },
            )

            alarm_payload = json.loads(
                alarm_result.content[0].text
            )

            assert alarm_payload["data"]

            alarm_id = alarm_payload["data"][0]["alarm_id"]

            recommendation_result = await session.call_tool(
                "operator_recommendations",
                arguments={"alarm_id": alarm_id},
            )

            recommendation_payload = json.loads(
                recommendation_result.content[0].text
            )

            assert recommendation_payload["recommended_actions"]
            assert recommendation_payload["likely_causes"]

            return {
                "asset_id": asset_id,
                "alarm_id": alarm_id,
                "recommendations": recommendation_payload,
            }


@pytest.mark.e2e
def test_mcp_alarm_and_rag_workflow():
    mcp_result = asyncio.run(run_mcp_workflow())

    retriever = RagRetriever("./rag/documents")

    retrieved = retriever.search(
        "Boiler Feed Pump Low Flow operating procedure "
        "maintenance safety suction pressure",
        top_k=5,
    )

    assert retrieved
    assert any(
        result["document_id"] == "PROC-BFP-001"
        for result in retrieved
    )

    assert mcp_result["recommendations"]["likely_causes"]
