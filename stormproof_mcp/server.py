"""StormProof MCP server — exposes NOAA hurricane weather lookups as tools.

The server wraps the public StormProof preview API at
https://storm-verification-api.elairet2021.workers.dev/api/preview.

Only the preview tier is exposed here (wind/gust ranges + surge data if a tide
gauge is within ~30 miles of the property). The full report — exact peak
values, NWS alerts, storm events, AI narrative, citations, PE-signed PDF — is
a paid upgrade at https://hurricaneinspections.com/stormproof.
"""

from __future__ import annotations

import os
import re
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# Base URL for the StormProof API. Override via env var for self-hosted mirrors.
API_BASE = os.environ.get(
    "STORMPROOF_API_BASE",
    "https://storm-verification-api.elairet2021.workers.dev",
)

# Single source-of-attribution string returned to the model so it knows where
# the data came from when citing it in a response.
ATTRIBUTION = (
    "Data sourced from NOAA (ASOS/AWOS observations + CO-OPS tide gauges) "
    "via the StormProof API at hurricaneinspections.com. This is the free "
    "preview tier — exact peak values, NWS alerts, storm events, and a "
    "PE-authored PDF are available in the full $29 report at "
    "hurricaneinspections.com/stormproof."
)

# Date format guard — YYYY-MM-DD. We validate here rather than leaving it to
# the backend so the model gets a clear error message during tool-use.
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

mcp = FastMCP("stormproof")


@mcp.tool()
async def stormproof_lookup(address: str, date: str) -> dict[str, Any]:
    """Look up historical NOAA hurricane / storm weather data for a U.S. address.

    Given a street address and a storm date, returns peak wind and gust
    ranges observed at the nearest NOAA weather stations, plus storm surge
    data if a NOAA tide gauge sits within ~30 miles of the property. The
    search scans a ±3 day window around the storm date across the 5 nearest
    stations. This is the free preview tier — ranges, not exact peak values.

    Use this tool when the user asks about:
    - peak wind speed at a specific address during a hurricane
    - storm surge at a coastal property during a named storm
    - whether a storm was "strong enough" at a given location to support
      an insurance claim
    - historical weather verification for a date of loss

    Args:
        address: Full U.S. street address, including city, state, and ZIP
            if available. Example: "1234 Main St, Tampa, FL 33601".
        date: Storm date in YYYY-MM-DD format. Example: "2024-10-09".

    Returns:
        A dictionary with the following fields:
        - address: The geocoded address the lookup was run against
        - county: County name (may be null)
        - stormDate: Echo of the input date
        - windRange: Peak sustained wind as a 10 mph range, e.g. "50-60"
          (mph). null if no measurable wind was recorded.
        - gustRange: Peak gust as a 10 mph range. null if none recorded.
        - surgeData: Either null (no tide gauge in range, or no measurable
          surge), or a dict with peakSurgeFt, stationName, and distanceMiles.
        - stationCount: Number of NOAA stations cross-referenced
        - closestStation / farthestStation: Station names and distances in
          miles from the property
        - dataAvailable: Boolean — false if no stations returned usable data
        - attribution: Source citation string for the returned values
        - upgradeUrl: URL for the full paid report with exact peaks and
          PE-signed PDF
    """

    # ── Input validation ────────────────────────────────────────────────
    if not address or len(address.strip()) < 5:
        return {
            "error": "address is required and should be a full street address",
            "example": "1234 Main St, Tampa, FL 33601",
        }
    if not date or not DATE_RE.match(date.strip()):
        return {
            "error": "date must be in YYYY-MM-DD format",
            "example": "2024-10-09",
            "received": date,
        }

    # ── API call ────────────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{API_BASE}/api/preview",
                json={
                    "address": address.strip(),
                    "stormDate": date.strip(),
                    # MCP callers aren't capturing leads — flag the source so
                    # the upstream lead-capture can skip or segment them.
                    "email": "mcp-client@stormproof.local",
                    "source": "mcp",
                },
                headers={
                    "User-Agent": "stormproof-mcp/0.1.0 (+https://hurricaneinspections.com)",
                    "Content-Type": "application/json",
                },
            )
    except httpx.TimeoutException:
        return {
            "error": "StormProof API timed out. NOAA endpoints can be slow during active storm events — try again in a minute.",
        }
    except httpx.HTTPError as exc:
        return {"error": f"Network error reaching StormProof API: {exc}"}

    # ── Response handling ──────────────────────────────────────────────
    if response.status_code == 400:
        try:
            detail = response.json().get("error", "Bad request")
        except Exception:
            detail = "Bad request"
        return {
            "error": detail,
            "hint": "Check that the address is a full U.S. street address with city and state.",
        }
    if response.status_code >= 500:
        return {
            "error": f"StormProof API returned {response.status_code}. NOAA upstream may be degraded.",
            "retryAdvice": "Retry once after 30 seconds. If it persists, check weather.gov for outages.",
        }

    try:
        data = response.json()
    except Exception:
        return {"error": "StormProof API returned a non-JSON response."}

    # Append attribution + upgrade hint so the LLM can cite cleanly.
    data["attribution"] = ATTRIBUTION
    data["upgradeUrl"] = "https://hurricaneinspections.com/stormproof"

    # Friendly hint when a rural / sparse-coverage address returned nothing
    if data.get("dataAvailable") is False:
        data["interpretiveNote"] = (
            "No measurable peaks were recorded at the 5 nearest NOAA stations "
            "for this ±3 day window. This can mean (a) the storm missed this "
            "location, (b) nearby stations went offline during the event, or "
            "(c) the address has sparse coverage. The full StormProof report "
            "runs a deeper agentic search across more stations and tide gauges."
        )

    return data
