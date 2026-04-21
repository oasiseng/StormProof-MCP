# StormProof MCP Server

**Address-specific hurricane and storm weather verification for Claude, Cursor, and other MCP-compatible clients.**

Look up historical NOAA wind speeds, wind gusts, and storm surge for any U.S. address on any date — directly from a conversation with your AI assistant. Built on top of the [StormProof API](https://hurricaneinspections.com) maintained by a Licensed Professional Engineer with 250+ forensic hurricane investigations.

---

## What this is

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes NOAA-sourced hurricane weather data as a tool your AI assistant can call. Ask Claude:

> *"What was the peak wind speed at 1234 Main St, Tampa FL on October 9, 2024?"*

…and it will call `stormproof_lookup` under the hood, returning wind/gust ranges, storm surge if a NOAA tide gauge is within range, and the weather stations that observed the event.

This is the *free preview tier* — it returns ranges and summary data. For exact peak values, PE-authored narratives, NWS alerts, storm events, citations, and a claim-ready PDF report, visit [hurricaneinspections.com/stormproof](https://hurricaneinspections.com/stormproof).

---

## Why it exists

Homeowners filing hurricane insurance claims lose money because their adjuster claims "the storm wasn't strong at your address" — without evidence, there's no counter-argument. This MCP server puts authoritative NOAA data one question away from anyone using an AI assistant. No more hunting through weather.gov archives or decoding METAR reports.

It's useful for:

- **Homeowners** checking whether a storm actually produced claimable wind at their address
- **Public adjusters** gathering evidence for claim packets
- **Contractors** confirming whether observed roof damage aligns with storm-day wind loads
- **Forensic engineers** doing quick sanity checks on peak conditions
- **Journalists and researchers** verifying storm intensity at specific locations

---

## Installation

### Claude Desktop

Add the following to your `claude_desktop_config.json` (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "stormproof": {
      "command": "uvx",
      "args": ["stormproof-mcp"]
    }
  }
}
```

Restart Claude Desktop. The `stormproof_lookup` tool will be available in any conversation.

### From source

```bash
git clone https://github.com/oasiseng/stormproof-mcp.git
cd stormproof-mcp
pip install -e .
stormproof-mcp
```

Or run without installing:

```bash
pip install mcp httpx
python -m stormproof_mcp
```

---

## Usage

Once installed, just ask your assistant:

> *"Check NOAA data for 789 Bayshore Blvd, Tampa FL 33606 on August 30, 2023."*

The assistant will call `stormproof_lookup` and return something like:

```json
{
  "address": "789 Bayshore Blvd, Tampa, FL 33606",
  "stormDate": "2023-08-30",
  "windRange": "50-60",
  "gustRange": "70-80",
  "surgeData": {
    "peakSurgeFt": 4.2,
    "stationName": "St. Petersburg, FL",
    "distanceMiles": 8.1
  },
  "stationCount": 5,
  "closestStation": { "name": "KTPA", "distanceMiles": 3.4 },
  "farthestStation": { "name": "KPIE", "distanceMiles": 12.9 }
}
```

The tool scans a ±3 day window around the storm date across the 5 nearest NOAA stations, plus the nearest tide gauge within 30 miles for storm surge.

---

## Tool reference

### `stormproof_lookup(address, date)`

**Parameters:**

- `address` *(string, required)*: Full street address, e.g. `"1234 Main St, Tampa, FL 33601"`
- `date` *(string, required)*: Storm date in `YYYY-MM-DD` format

**Returns:** A JSON object with `windRange`, `gustRange`, `surgeData`, `stationCount`, `closestStation`, `farthestStation`, and `address` fields.

---

## Data sources

All data is sourced from public NOAA endpoints:

- **Weather observations:** [ASOS/AWOS](https://www.weather.gov/asos/) via the [Iowa Environmental Mesonet](https://mesonet.agron.iastate.edu/) download API
- **Tide gauges / storm surge:** [NOAA CO-OPS](https://tidesandcurrents.noaa.gov/) water level and prediction APIs
- **Station metadata:** [NOAA NWS station network](https://www.weather.gov/documentation/services-web-api)

Observed surge is computed as `observed_water_level − predicted_tide`, rounded to nearest 0.01 ft, with a 0.5 ft detection threshold.

---

## The full StormProof report

The free tier returns ranges. The [full StormProof report](https://hurricaneinspections.com/stormproof) ($29 one-time) adds:

- **Exact peak values** (not ranges) for wind, gust, rainfall, pressure, and surge
- **All nearby stations** cross-referenced (not just 5)
- **NWS alert history** — every watch, warning, and advisory that covered the property
- **NOAA Storm Events** — tornadoes, floods, wind damage events in the county
- **AI-authored narrative** (3–5 paragraphs) explaining date-of-loss evidence
- **Confidence score** with per-source attribution
- **Aerial satellite map** with red pin at the property + weather station network map
- **Full citations** — every data point linked to its NOAA source URL
- **Claim-ready PDF** — multi-page, ready to hand to an adjuster

Plus the [48-page Storm Claim Preparation Guide](https://hurricaneinspections.com), the Damage Documentation Kit, and free Pre-Storm Baseline Photos.

---

## Limitations and honesty

- **±3 day preview window.** If the storm arrived earlier or later, peaks may be under-reported in the free tier. The full report uses a wider agentic search.
- **Not legal or insurance advice.** This tool surfaces public NOAA data; it does not interpret your policy or guarantee claim outcomes.
- **Station coverage varies.** Rural and offshore addresses may have sparse coverage. The full report handles these cases more gracefully.
- **Storm surge requires a tide gauge within ~30 miles.** Inland addresses will not return surge data.

---

## About

Built and maintained by **Enrique Lairet, PE** — Licensed Professional Engineer with 250+ forensic hurricane damage investigations across Florida, Louisiana, Texas, and the Carolinas. StormProof exists because homeowners lose claims they should win, and adjusters win arguments they shouldn't, whenever the weather evidence isn't on the table.

- Website: [hurricaneinspections.com](https://hurricaneinspections.com)
- Full report: [hurricaneinspections.com/stormproof](https://hurricaneinspections.com/stormproof)
- Free pre-storm baseline tool: [hurricaneinspections.com/baseline](https://hurricaneinspections.com/baseline)

---

## License

MIT. See [LICENSE](LICENSE).

---

## Contributing

Issues and PRs welcome, especially for:

- Additional MCP client configuration examples (Cursor, Zed, Cline, Continue, etc.)
- Better error messages for sparse-coverage addresses
- Translation of tool descriptions into Spanish

Not accepting PRs that modify the upstream API contract — that lives in the private StormProof backend.
