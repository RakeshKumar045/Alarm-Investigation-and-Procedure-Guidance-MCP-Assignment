import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession

from mcp.client.sse import sse_client


from rag.retrieval import RagRetriever

import re


load_dotenv()


class CopilotOrchestrator:
    def __init__(self):
        self.mcp_url = os.getenv(
            "MCP_SERVER_URL",
            "http://127.0.0.1:9000/mcp",
        )
        self.rag = RagRetriever(
            os.getenv("DOCUMENT_PATH", "./rag/documents")
        )

    async def run(self, question: str) -> dict[str, Any]:
        trace = []

        async with sse_client(self.mcp_url) as (
                read_stream,
                write_stream,
        ):

            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                discovered = await session.list_tools()
                available_tools = [
                    tool.name for tool in discovered.tools
                ]

                async def call_tool(name: str, arguments: dict[str, Any]):
                    if name not in available_tools:
                        raise RuntimeError(
                            f"MCP tool unavailable: {name}"
                        )

                    started = time.perf_counter()

                    try:
                        result = await session.call_tool(
                            name,
                            arguments=arguments,
                        )

                        duration_ms = round(
                            (time.perf_counter() - started) * 1000,
                            2,
                        )

                        parsed = self._parse_mcp_result(result)

                        trace.append({
                            "tool": name,
                            "arguments": arguments,
                            "duration_ms": duration_ms,
                            "status": "success",
                        })

                        return parsed

                    except Exception as exc:
                        trace.append({
                            "tool": name,
                            "arguments": arguments,
                            "status": "failed",
                            "error": str(exc),
                        })
                        raise

                asset_query = self._extract_asset_query(question)

                assets_response = await call_tool(
                    "asset_search",
                    {"query": asset_query, "limit": 10},
                )

                assets = assets_response.get("results", [])

                if not assets:
                    return {
                        "answer": "No matching asset was found.",
                        "trace": trace,
                        "citations": [],
                        "alarms": [],
                    }

                asset = assets[0]
                asset_id = asset["asset_id"]

                metadata = await call_tool(
                    "asset_metadata",
                    {"asset_id": asset_id},
                )

                alarms_response = await call_tool(
                    "alarm_retrieval",
                    {
                        "asset_id": asset_id,
                        "status": "active",
                        "page": 1,
                        "page_size": 50,
                    },
                )

                alarms = alarms_response.get("data", [])

                if not alarms:
                    return {
                        "answer": (
                            f"No active alarms were found for "
                            f"{asset['asset_name']}."
                        ),
                        "asset": asset,
                        "metadata": metadata,
                        "alarms": [],
                        "trace": trace,
                        "citations": [],
                    }

                selected_alarm = alarms[0]
                alarm_id = selected_alarm["alarm_id"]

                priority = await call_tool(
                    "alarm_priority_score",
                    {"alarm_id": alarm_id},
                )

                recommendations = await call_tool(
                    "operator_recommendations",
                    {"alarm_id": alarm_id},
                )

                related_ids = [
                    related["asset_id"]
                    for related in metadata.get("related_assets", [])
                ]

                correlation = None
                if related_ids:
                    correlation = await call_tool(
                        "alarm_correlation",
                        {
                            "asset_ids": [asset_id] + related_ids,
                        },
                    )

                rag_query = " ".join([
                    selected_alarm.get("alarm_name", ""),
                    selected_alarm.get("message", ""),
                    "operating procedure maintenance troubleshooting safety",
                ])

                citations = self.rag.search(rag_query, top_k=5)

                answer = self._compose_answer(
                    asset=asset,
                    alarm=selected_alarm,
                    priority=priority,
                    recommendations=recommendations,
                    citations=citations,
                )

                return {
                    "answer": answer,
                    "asset": asset,
                    "metadata": metadata,
                    "alarms": alarms,
                    "priority": priority,
                    "recommendations": recommendations,
                    "correlation": correlation,
                    "citations": citations,
                    "trace": trace,
                }

    @staticmethod
    def _parse_mcp_result(result) -> dict:
        for item in result.content:
            if hasattr(item, "text"):
                try:
                    return json.loads(item.text)
                except json.JSONDecodeError:
                    return {"text": item.text}

        return {}

    @staticmethod
    def _extract_asset_query(question: str) -> str:
        patterns = [
            r"\bboiler\s+feed\s+pump\s+\d+\b",
            r"\bcompressor\s+\d+\b",
            r"\bmotor\s+\d+\b",
            r"\bpump\s+\d+\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                return match.group(0)

        question_lower = question.lower()
        if "compressor" in question_lower:
            return "compressor"

        if "pump" in question_lower:
            return "pump"

        if "motor" in question_lower:
            return "motor"
        return question

    @staticmethod
    def _compose_answer(
        asset,
        alarm,
        priority,
        recommendations,
        citations,
    ) -> str:
        lines = [
            f"## Alarm investigation: {asset['asset_name']}",
            "",
            f"**Alarm:** {alarm['alarm_name']}",
            f"**Severity:** {alarm['severity']}",
            f"**Status:** {alarm['status']}",
            f"**Priority score:** {priority.get('priority_score')}",
            "",
            "### Assessment",
            recommendations.get(
                "likely_causes",
                ["No likely causes were returned by the API."],
            ).__str__(),
            "",
            "### Immediate actions",
        ]

        for action in recommendations.get("recommended_actions", []):
            lines.append(f"- {action}")

        lines.extend([
            "",
            "### Procedure alignment",
            "The API recommendations should be checked against the retrieved "
            "operating procedure and maintenance manual before execution.",
        ])

        if citations:
            lines.extend([
                "",
                "### Evidence",
            ])

            for citation in citations:
                lines.append(
                    f"- [{citation['document_id']}] "
                    f"{citation['title']} "
                    f"(score={citation['score']})"
                )

        return "\n".join(lines)
