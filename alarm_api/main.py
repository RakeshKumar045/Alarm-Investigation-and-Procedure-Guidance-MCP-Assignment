from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel

from .data import ALARMS, ASSETS

app = FastAPI(title="Alarm Management API Simulator", version="1.0.0")

EXPECTED_TOKEN = "demo-token"

CALCULATIONS: dict[str, dict] = {}


def authenticate(authorization: Optional[str]) -> None:
    if authorization != f"Bearer {EXPECTED_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid bearer token")


def trace_response(trace_id: Optional[str]) -> dict:
    return {
        "trace_id": trace_id or str(uuid4()),
        "service": "alarm-api-simulator",
    }


class TimeRange(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class SummaryRequest(BaseModel):
    asset_ids: Optional[list[str]] = None
    site: Optional[str] = None
    unit: Optional[str] = None
    time_range: Optional[TimeRange] = None
    severity: Optional[list[str]] = None
    group_by: list[str] = ["alarm_name"]
    kpis: list[str] = ["alarm_count"]


class CorrelationRequest(BaseModel):
    asset_ids: list[str]
    time_range: Optional[TimeRange] = None
    correlation_method: str = "cooccurrence"
    lag_window_minutes: int = 15
    severity_threshold: str = "medium"
    min_support: int = 1


class PriorityRequest(BaseModel):
    alarm_id: str


class RecommendationRequest(BaseModel):
    alarm_id: str
    include_related: bool = True
    include_asset_context: bool = True
    include_historical_pattern: bool = True


class TrendsRequest(BaseModel):
    asset_ids: Optional[list[str]] = None
    site: Optional[str] = None
    unit: Optional[str] = None
    time_range: Optional[TimeRange] = None
    bucket: str = "daily"
    metrics: list[str] = ["alarm_count", "avg_ack_delay"]

class FloodAnalysisRequest(BaseModel):
    unit: Optional[str] = None
    site: Optional[str] = None
    time_range: Optional[TimeRange] = None
    threshold_count: int = 10
    rolling_window_minutes: int = 10

class RationalizationRequest(BaseModel):
    asset_ids: Optional[list[str]] = None
    site: Optional[str] = None
    unit: Optional[str] = None
    time_range: Optional[TimeRange] = None
    recurrence_threshold: int = 5
    stale_minutes_threshold: int = 180


class CalculationGenerateRequest(BaseModel):
    calculation_type: str
    filters: dict = {}


class CalculationExecuteRequest(BaseModel):
    calculation_id: str
    filters: dict = {}



@app.get("/health")
def health():
    return {"status": "ok", "service": "alarm-api-simulator"}


@app.get("/assets/search")
def search_assets(
    query: str,
    limit: int = Query(default=10, ge=1, le=100),
    unit: Optional[str] = None,
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    query_lower = query.lower()
    results = [
        asset
        for asset in ASSETS
        if query_lower in asset["asset_name"].lower()
        and (unit is None or asset["unit"].lower() == unit.lower())
    ]

    return {
        "results": results[:limit],
        "count": len(results),
    }


@app.get("/assets/{asset_id}/metadata")
def asset_metadata(
    asset_id: str,
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    asset = next((a for a in ASSETS if a["asset_id"] == asset_id), None)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    related = [
        a for a in ASSETS
        if a["asset_id"] in asset.get("related_asset_ids", [])
    ]

    return {
        "asset": asset,
        "related_assets": related,
    }


@app.get("/alarms")
def get_alarms(
    asset_id: Optional[str] = None,
    site: Optional[str] = None,
    unit: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: str = "start_time",
    sort_order: str = "desc",
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    asset_map = {a["asset_id"]: a for a in ASSETS}

    rows = []
    for alarm in ALARMS:
        asset = asset_map.get(alarm["asset_id"], {})

        if asset_id and alarm["asset_id"] != asset_id:
            continue
        if site and asset.get("site") != site:
            continue
        if unit and asset.get("unit") != unit:
            continue
        if status and alarm["status"] != status:
            continue

        rows.append({**alarm, "asset_name": asset.get("asset_name")})

    reverse = sort_order.lower() == "desc"
    rows.sort(key=lambda row: row.get(sort_by, ""), reverse=reverse)

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "data": rows[start:end],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": len(rows),
            "has_next": end < len(rows),
        },
    }


@app.get("/alarms/{alarm_id}")
def get_alarm(
    alarm_id: str,
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    alarm = next((a for a in ALARMS if a["alarm_id"] == alarm_id), None)

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")

    asset = next(a for a in ASSETS if a["asset_id"] == alarm["asset_id"])

    return {
        "alarm": alarm,
        "asset": asset,
    }


@app.post("/alarms/summary")
def alarm_summary(
    request: SummaryRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    rows = []
    for alarm in ALARMS:
        asset = next(a for a in ASSETS if a["asset_id"] == alarm["asset_id"])

        if request.asset_ids and alarm["asset_id"] not in request.asset_ids:
            continue
        if request.site and asset["site"] != request.site:
            continue
        if request.unit and asset["unit"] != request.unit:
            continue
        if request.severity and alarm["severity"] not in request.severity:
            continue

        rows.append({**alarm, "asset_name": asset["asset_name"]})

    grouped = {}
    for alarm in rows:
        key = tuple(alarm.get(field) for field in request.group_by)
        grouped.setdefault(key, []).append(alarm)

    groups = []
    for key, group in grouped.items():
        values = dict(zip(request.group_by, key))
        values.update({
            "alarm_count": len(group),
            "recurring_rate": round(
                sum(a["occurrence_count"] for a in group) / len(group), 2
            ),
            "avg_ack_delay": 4.0,
        })
        groups.append(values)

    return {
        **trace_response(trace_id),
        "groups": groups,
        "total_alarm_count": len(rows),
    }


@app.post("/alarms/correlation")
def correlation(
    request: CorrelationRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    matching = [
        alarm for alarm in ALARMS
        if alarm["asset_id"] in request.asset_ids
    ]

    return {
        **trace_response(trace_id),
        "correlations": [
            {
                "alarm_name": alarm["alarm_name"],
                "asset_id": alarm["asset_id"],
                "support": alarm["occurrence_count"],
                "confidence": min(0.99, 0.5 + alarm["occurrence_count"] / 100),
                "likely_factor": (
                    "Low suction flow or restriction"
                    if "Flow" in alarm["alarm_name"]
                    else "Process condition or equipment degradation"
                ),
            }
            for alarm in matching
        ],
    }


@app.post("/alarms/priority-score")
def priority_score(
    request: PriorityRequest,
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    alarm = next((a for a in ALARMS if a["alarm_id"] == request.alarm_id), None)

    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")

    severity_score = {
        "critical": 90,
        "high": 70,
        "medium": 40,
        "low": 20,
    }.get(alarm["severity"], 10)

    score = min(100, severity_score + min(alarm["occurrence_count"], 10))

    return {
        "alarm_id": alarm["alarm_id"],
        "priority_score": score,
        "priority": "urgent" if score >= 90 else "high",
        "reason": "Severity and recurrence frequency",
    }


@app.post("/recommendations/operator-actions")
def recommendations(
    request: RecommendationRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    alarm = next(
        (
            item
            for item in ALARMS
            if item["alarm_id"] == request.alarm_id
        ),
        None,
    )

    if not alarm:
        raise HTTPException(
            status_code=404,
            detail="Alarm not found",
        )

    alarm_name = alarm["alarm_name"].lower()

    if "motor trip" in alarm_name:
        likely_causes = [
            "Motor overload",
            "High motor winding temperature",
            "Protection relay operation",
            "Mechanical pump seizure",
        ]

        actions = [
            "Verify the motor trip indication and protection relay status.",
            "Check motor current and winding temperature.",
            "Inspect the pump for mechanical blockage or seizure.",
            "Do not reset the trip until the cause is understood.",
            "Escalate to electrical and reliability engineering.",
        ]

    elif "compressor" in alarm_name:
        likely_causes = [
            "Downstream restriction",
            "High process demand",
            "Pressure control malfunction",
            "Compressor fouling or degradation",
        ]

        actions = [
            "Verify discharge pressure using the local instrument.",
            "Check downstream valve positions and process demand.",
            "Inspect compressor temperature, vibration, and current.",
            "Confirm pressure control and relief systems are available.",
            "Escalate if pressure continues to increase.",
        ]

    elif "low flow" in alarm_name:
        likely_causes = [
            "Insufficient suction flow",
            "Valve restriction",
            "Blocked suction strainer",
            "Pump degradation",
            "Instrument error",
        ]

        actions = [
            "Verify the alarm using the local flow indication.",
            "Check pump suction pressure and discharge pressure.",
            "Inspect for blocked suction strainers or closed valves.",
            "Confirm operation against the approved procedure.",
            "Escalate if the condition persists.",
        ]

    elif "pressure high" in alarm_name:
        likely_causes = [
            "Downstream restriction",
            "Closed or partially closed valve",
            "Pressure control malfunction",
            "Abnormal process demand",
        ]

        actions = [
            "Verify the pressure using an independent indication.",
            "Check downstream valve positions.",
            "Review pressure control loop operation.",
            "Confirm relief and protective systems are available.",
            "Notify the control room supervisor if pressure continues rising.",
        ]

    else:
        likely_causes = [
            "Process abnormality",
            "Equipment degradation",
            "Instrument error",
        ]

        actions = [
            "Verify the alarm using the local indication.",
            "Check relevant process and equipment conditions.",
            "Follow the approved operating procedure.",
            "Escalate if the alarm persists.",
        ]

    return {
        **trace_response(trace_id),
        "alarm_id": request.alarm_id,
        "recommended_actions": actions,
        "likely_causes": likely_causes,
        "safety_note": (
            "Do not bypass interlocks or enter restricted areas "
            "without authorization."
        ),
    }

@app.post("/alarms/trends")
def alarm_trends(
    request: TrendsRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    asset_map = {
        asset["asset_id"]: asset
        for asset in ASSETS
    }

    matching_alarms = []

    for alarm in ALARMS:
        asset = asset_map.get(alarm["asset_id"], {})

        if request.asset_ids:
            if alarm["asset_id"] not in request.asset_ids:
                continue

        if request.site and asset.get("site") != request.site:
            continue

        if request.unit and asset.get("unit") != request.unit:
            continue

        matching_alarms.append(alarm)

    buckets = {}

    for alarm in matching_alarms:
        bucket_key = alarm["start_time"][:10]
        buckets.setdefault(bucket_key, []).append(alarm)

    points = []

    for bucket_key, alarms in sorted(buckets.items()):
        points.append(
            {
                "bucket": bucket_key,
                "alarm_count": len(alarms),
                "avg_ack_delay": 4.0,
                "critical_count": sum(
                    1
                    for alarm in alarms
                    if alarm["severity"] == "critical"
                ),
                "high_count": sum(
                    1
                    for alarm in alarms
                    if alarm["severity"] == "high"
                ),
            }
        )

    return {
        **trace_response(trace_id),
        "bucket": request.bucket,
        "metrics": request.metrics,
        "points": points,
        "total_points": len(points),
    }


@app.post("/alarms/flood-analysis")
def flood_analysis(
    request: FloodAnalysisRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    asset_map = {
        asset["asset_id"]: asset
        for asset in ASSETS
    }

    matching_alarms = []

    for alarm in ALARMS:
        asset = asset_map.get(alarm["asset_id"], {})

        if request.unit and asset.get("unit") != request.unit:
            continue

        if request.site and asset.get("site") != request.site:
            continue

        matching_alarms.append(
            {
                **alarm,
                "asset_name": asset.get("asset_name"),
            }
        )

    flood_windows = []

    if len(matching_alarms) >= request.threshold_count:
        flood_windows.append(
            {
                "start": min(
                    alarm["start_time"]
                    for alarm in matching_alarms
                ),
                "end": max(
                    alarm["start_time"]
                    for alarm in matching_alarms
                ),
                "alarm_count": len(matching_alarms),
                "rolling_window_minutes": (
                    request.rolling_window_minutes
                ),
            }
        )

    return {
        **trace_response(trace_id),
        "unit": request.unit,
        "site": request.site,
        "threshold_count": request.threshold_count,
        "flood_windows": flood_windows,
        "total_alarms": len(matching_alarms),
    }


@app.post("/alarms/rationalization-candidates")
def rationalization_candidates(
    request: RationalizationRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    asset_map = {
        asset["asset_id"]: asset
        for asset in ASSETS
    }

    candidates = []

    for alarm in ALARMS:
        asset = asset_map.get(alarm["asset_id"], {})

        if request.asset_ids and alarm["asset_id"] not in request.asset_ids:
            continue

        if request.site and asset.get("site") != request.site:
            continue

        if request.unit and asset.get("unit") != request.unit:
            continue

        recurrence = alarm.get("occurrence_count", 0)

        if recurrence >= request.recurrence_threshold:
            candidates.append(
                {
                    "alarm_id": alarm["alarm_id"],
                    "asset_id": alarm["asset_id"],
                    "asset_name": asset.get("asset_name"),
                    "alarm_name": alarm["alarm_name"],
                    "severity": alarm["severity"],
                    "status": alarm["status"],
                    "occurrence_count": recurrence,
                    "reason": "Alarm recurrence exceeds threshold",
                    "recommended_review": [
                        "Review alarm set point and deadband.",
                        "Check instrument calibration.",
                        "Review operating procedure.",
                        "Assess whether rationalization is appropriate.",
                    ],
                }
            )

    return {
        **trace_response(trace_id),
        "recurrence_threshold": request.recurrence_threshold,
        "stale_minutes_threshold": request.stale_minutes_threshold,
        "candidates": candidates,
        "count": len(candidates),
    }

@app.post("/calculation-code/generate")
def generate_calculation(
    request: CalculationGenerateRequest,
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    if not request.calculation_type.strip():
        raise HTTPException(
            status_code=422,
            detail="calculation_type must not be empty",
        )

    calculation_id = str(uuid4())

    CALCULATIONS[calculation_id] = {
        "calculation_id": calculation_id,
        "calculation_type": request.calculation_type,
        "filters": request.filters,
    }

    return {
        "calculation_id": calculation_id,
        "calculation_type": request.calculation_type,
        "status": "generated",
        "filters": request.filters,
    }


@app.post("/calculation-code/execute")
def execute_calculation(
    request: CalculationExecuteRequest,
    authorization: Optional[str] = Header(default=None),
    trace_id: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    calculation = CALCULATIONS.get(request.calculation_id)

    if not calculation:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found",
        )

    filters = {
        **calculation.get("filters", {}),
        **request.filters,
    }

    calculation_type = calculation["calculation_type"]

    asset_map = {
        asset["asset_id"]: asset
        for asset in ASSETS
    }

    matching_alarms = []

    for alarm in ALARMS:
        asset = asset_map.get(alarm["asset_id"], {})

        if filters.get("site") and asset.get("site") != filters["site"]:
            continue

        if filters.get("unit") and asset.get("unit") != filters["unit"]:
            continue

        matching_alarms.append(alarm)

    total_alarms = len(matching_alarms)

    critical_count = sum(
        1
        for alarm in matching_alarms
        if alarm["severity"] == "critical"
    )

    high_count = sum(
        1
        for alarm in matching_alarms
        if alarm["severity"] == "high"
    )

    total_occurrences = sum(
        alarm.get("occurrence_count", 0)
        for alarm in matching_alarms
    )

    if calculation_type == "critical_alarm_density":
        value = (
            critical_count / total_alarms
            if total_alarms
            else 0.0
        )

    elif calculation_type == "alarm_flood_index":
        value = (
            total_occurrences / total_alarms
            if total_alarms
            else 0.0
        )

    elif calculation_type == "nuisance_alarm_score":
        value = (
            total_occurrences / total_alarms
            if total_alarms
            else 0.0
        )

    elif calculation_type == "operator_response_efficiency":
        value = 96.0 if total_alarms else 0.0

    else:
        value = 0.0

    return {
        **trace_response(trace_id),
        "calculation_id": request.calculation_id,
        "calculation_type": calculation_type,
        "status": "executed",
        "filters": filters,
        "result": {
            "value": round(value, 4),
            "total_alarms": total_alarms,
            "critical_count": critical_count,
            "high_count": high_count,
            "total_occurrences": total_occurrences,
        },
    }



@app.get("/analytics/kpi-definitions")
def kpi_definitions(
    authorization: Optional[str] = Header(default=None),
):
    authenticate(authorization)

    return {
        "definitions": [
            {
                "name": "alarm_count",
                "display_name": "Alarm Count",
                "description": "Total number of alarms in the selected scope.",
                "unit": "count",
            },
            {
                "name": "critical_count",
                "display_name": "Critical Alarm Count",
                "description": "Number of critical-severity alarms.",
                "unit": "count",
            },
            {
                "name": "recurring_rate",
                "display_name": "Recurring Rate",
                "description": "Average recurrence count for matching alarms.",
                "unit": "count per alarm",
            },
            {
                "name": "avg_ack_delay",
                "display_name": "Average Acknowledgement Delay",
                "description": "Average time taken to acknowledge alarms.",
                "unit": "minutes",
            },
            {
                "name": "alarm_flood_index",
                "display_name": "Alarm Flood Index",
                "description": "Average occurrence volume per matching alarm.",
                "unit": "occurrences per alarm",
            },
            {
                "name": "critical_alarm_density",
                "display_name": "Critical Alarm Density",
                "description": "Ratio of critical alarms to total alarms.",
                "unit": "ratio",
            },
            {
                "name": "nuisance_alarm_score",
                "display_name": "Nuisance Alarm Score",
                "description": "Recurrence-based nuisance alarm indicator.",
                "unit": "score",
            },
            {
                "name": "operator_response_efficiency",
                "display_name": "Operator Response Efficiency",
                "description": "Synthetic operator response efficiency measure.",
                "unit": "percentage",
            },
        ]
    }

