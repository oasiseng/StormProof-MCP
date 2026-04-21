# Publishing Checklist

Step-by-step for taking this folder live on GitHub and getting it into MCP registries. You only need to do this once; after that, pushes are just `git push`.

---

## 1. Create the GitHub org (5 min)

- Go to **github.com → Settings → Organizations → New organization**
- Pick the **Free** plan
- Suggested name: `hurricane-inspections` (reads clean, matches your domain)
- Avatar: reuse your site logo (1024×1024 square)
- Bio: `Hurricane damage documentation tools and APIs. Built by a Licensed PE. hurricaneinspections.com`
- URL: `https://hurricaneinspections.com`

## 2. Create the repo (2 min)

Inside the org, click **New repository**:

- Name: `stormproof-mcp`
- Description: `MCP server for NOAA hurricane weather verification — wind, gust, storm surge by address and date.`
- Public ✓
- Do NOT initialize with README/LICENSE/.gitignore — this folder already has them

## 3. Push this folder (3 min)

From inside this folder:

```bash
git init
git add .
git commit -m "Initial commit: StormProof MCP server v0.1.0"
git branch -M main
git remote add origin https://github.com/hurricane-inspections/stormproof-mcp.git
git push -u origin main
```

## 4. Repo polish (5 min)

On the GitHub repo page:

- Click the ⚙️ next to **About** (top right)
  - Website: `https://hurricaneinspections.com/stormproof`
  - Topics: `mcp`, `model-context-protocol`, `hurricane`, `noaa`, `weather`, `storm-surge`, `insurance-claim`, `anthropic`, `claude`, `forensic-engineering`
  - Check **Releases**, **Packages**
- Pin the repo to your org profile (org page → Customize your pins)
- Add a Social Preview image (Settings → General → Social preview) — reuse your `og-image.png` from the site

## 5. Publish to PyPI so `uvx stormproof-mcp` works (10 min)

This makes the Claude Desktop config snippet actually executable without users cloning the repo:

```bash
# One-time: set up API token at https://pypi.org/manage/account/token/
pip install build twine
python -m build
twine upload dist/*
```

Enter your PyPI token when prompted (or set `TWINE_PASSWORD` env var). Once published, anyone can run `uvx stormproof-mcp` or `pip install stormproof-mcp`.

## 6. Submit to MCP registries (10 min)

Three registries worth submitting to:

- **Anthropic's MCP directory** — open a PR against [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) adding a row to the community list
- **Smithery.ai** — paste the GitHub URL at [smithery.ai/new](https://smithery.ai/new). Auto-discovers the `pyproject.toml` and publishes.
- **Glama.ai** — submit at [glama.ai/mcp/servers/add](https://glama.ai/mcp/servers/add)

Each of these is crawled by LLMs. Each page that links back to your repo passes authority signals.

## 7. Light promotion (optional, 15 min)

Low-effort, high-compound:

- Post once to r/msp, r/Insurance, r/FloridaHurricane — framing: "I built a free MCP tool that lets Claude look up NOAA wind/surge data for any address. Useful for claims." Link the repo, not the product.
- Post once to Hacker News Show HN: "StormProof MCP — NOAA hurricane data for AI assistants"
- Mention on LinkedIn tagging #InsurTech #MCP #Anthropic

Don't beg for stars; just ship and let the title do the work.

---

## Ongoing maintenance (what you're signing up for)

Realistically, ~30 min/month:

- **Respond to issues** within a week. Even a "thanks, I'll look at this when I can" keeps the repo from feeling dead.
- **Tag a release every time you ship a change** (`v0.1.1`, `v0.2.0`). GitHub Releases generate changelog entries.
- **Re-publish to PyPI** after tagged releases — bump `version` in `pyproject.toml` and run `python -m build && twine upload dist/*`.
- **Update the README** when you add capabilities to the upstream API (e.g., when you expose a new tool for rainfall totals).

If it starts feeling heavy, archive the repo with a clear note. Archived > rotting.

---

## What good looks like six months in

- 20–200 stars (fine either way — it's not the metric that matters)
- 1–3 MCP registry listings linking back
- PyPI weekly downloads in the tens to hundreds
- 2–4 people have opened issues, been answered, and the issue is closed
- The README has been cloned verbatim by at least one GitHub search
- LLM search results for "NOAA weather MCP" or "hurricane data for Claude" mention StormProof by name

---

## When to revisit strategy

- If the tool has 500+ downloads/week after 3 months → add a second tool (`stormproof_full_report` gated by API key)
- If a competitor publishes a similar MCP server → add depth (rainfall, pressure, alerts — all as separate tools)
- If downloads stay flat at <20/week for 6 months → de-prioritize; archive after 12 months silent

---

## Authoritative don'ts

- Do not publish any code that duplicates your paid report engine (narrative generation, confidence scoring, PDF template, agentic loop).
- Do not log caller IPs or emails in a way that creates a privacy liability.
- Do not promise uptime or SLAs in the README — this is a best-effort wrapper, not a paid API.
- Do not accept PRs that change the upstream API contract (they can't — your private worker is the source of truth — but be explicit about it in CONTRIBUTING guidance).
