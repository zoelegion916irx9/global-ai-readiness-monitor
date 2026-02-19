# ICAIRE Global AI Readiness Monitor — V2 Brief

## Vision
Transform the MENA RAM Dashboard into the **world's first comprehensive, interactive Global AI Readiness Monitor** that aggregates and compares data from ALL major AI readiness indices and assessments. Make UNESCO (and others) follow ICAIRE's work.

## Data Sources to Integrate

### 1. UNESCO RAM (Readiness Assessment Methodology)
- **Coverage:** 70+ countries (completed + in process)
- **Dimensions:** Legal & Regulatory, Social & Cultural, Economic, Scientific & Educational, Technological & Infrastructural
- **Data:** Qualitative findings + policy recommendations per country
- **Source:** https://www.unesco.org/ethics-ai/en/global-hub
- **Country profiles:** https://www.unesco.org/ethics-ai/en/{country}

### 2. Stanford HAI AI Index / Global AI Vibrancy Tool
- **Coverage:** Global, multiple countries
- **Key metrics:** R&D, economy, education, diversity, policy, public opinion
- **Vibrancy Tool:** Interactive cross-country comparison with longitudinal data
- **Source:** https://aiindex.stanford.edu/report/ and https://hai.stanford.edu/research/the-global-ai-vibrancy-tool-2024

### 3. Tortoise Global AI Index
- **Coverage:** 83 countries
- **Indicators:** 122 indicators from 24 data sources
- **Pillars:** Talent, Infrastructure, Operating Environment, Research, Development, Government Strategy, Commercial
- **Source:** https://www.tortoisemedia.com/data/global-ai
- **Methodology:** https://www.tortoisemedia.com/_app/immutable/assets/AI-Methodology-2409.BGTLUPC-.pdf

### 4. Oxford Insights Government AI Readiness Index
- **Coverage:** 188 countries
- **Pillars:** Government, Technology Sector, Data & Infrastructure (40 indicators)
- **Source:** https://oxfordinsights.com/ai-readiness/ai-readiness-index/

### 5. GIRAI (Global Index on Responsible AI)
- **Coverage:** 138 countries
- **Dimensions:** Human rights & AI, Responsible AI governance, Responsible AI capabilities (19 thematic areas)
- **Source:** https://www.global-index.ai/
- **UNESCO endorsed (IRCAI Top 100)**

### 6. IMF AI Preparedness Index (AIPI)
- **Coverage:** 174 economies
- **Dimensions:** Digital infrastructure, Human capital & labor market, Innovation & economic integration, Regulation
- **Dashboard:** https://www.imf.org/external/datamapper/datasets/AIPI
- **Methodology:** https://www.imf.org/external/datamapper/AIPINote.pdf

### 7. World Bank Digital Progress & Trends Report 2025
- **Focus:** AI foundations in developing countries
- **Framework:** 4Cs — Connectivity, Compute, Competencies, Compatibility
- **Source:** https://www.worldbank.org/en/publication/dptr2025-ai-foundations

### 8. ICESCO AI Index for the Islamic World
- **Coverage:** 9 leading OIC countries (expanding)
- **Context:** Implements Riyadh Charter on AI for Islamic World
- **Source:** https://icesco.org
- **Launched:** December 2025

### 9. OECD AI Policy Observatory
- **Coverage:** OECD members + partners (~70 countries)
- **Data:** Policy tracking, AI incidents, compute metrics
- **Source:** https://oecd.ai

## Regional Filters
- **MENA / Arab States** (Arab League members)
- **Africa** (AU members)
- **Asia & Pacific**
- **Europe**
- **Americas** (North + Latin America & Caribbean)
- **Small Island Developing States (SIDS)**

## International Organization Filters
- **OECD members**
- **ICESCO / OIC members**
- **EU members**
- **G20**
- **G7**
- **GPAI members**
- **BRICS+**
- **GCC**
- **ASEAN**
- **African Union**
- **UNESCO Category 2 Centers (AI-related)**

## Features

### Core Dashboard
1. **Global Map View** — Interactive world map, color-coded by composite readiness score
2. **Country Cards** — Click any country for detailed profile aggregating all indices
3. **Index Selector** — Toggle which indices to display/compare (UNESCO RAM, Stanford, Tortoise, Oxford, GIRAI, IMF, World Bank, ICESCO)
4. **Regional Filter Bar** — Filter by region or international org membership
5. **Dynamic Comparison Charts:**
   - Radar/spider charts (select any N countries to overlay)
   - Bar charts (rank countries on any single metric)
   - Scatter plots (correlate two metrics, e.g. AI investment vs. ethics readiness)
   - Timeline charts (track country progress over years)
6. **Composite Score** — ICAIRE's own weighted composite combining all indices (methodology documented)

### Advanced Features
7. **Gap Analysis** — Which countries are assessed by which indices? Where are blind spots?
8. **Cross-Index Correlation** — How do different indices agree/disagree on a country?
9. **Regional Insights** — Auto-generated comparative analysis per region
10. **Download/Export** — CSV, PDF export of any view
11. **Embed Widget** — Embeddable chart widgets for other websites

### Tracking Over Time
12. **Historical Data** — Store yearly snapshots of all indices
13. **Progress Tracker** — Show how countries improve/decline over time
14. **New Assessment Alerts** — Flag when a country completes a new assessment

## Technical Architecture

### Option A: Static Site (MVP — fast to build)
- Single HTML/JS app reading from JSON data files
- Chart.js + D3.js for visualizations
- Leaflet.js for world map
- JSON data files organized by source
- GitHub Pages deployment
- Update: edit JSON, push to git

### Option B: Full Stack (Production)
- Frontend: React + Vite + Tailwind
- Backend: FastAPI (Python) or Express
- Database: SQLite → PostgreSQL
- Data pipeline: Python scrapers + scheduled updates
- API: Public REST API for researchers
- Deploy: Vercel/Railway

### Recommendation: Start with Option A (MVP), migrate to B later

## File Structure (MVP)
```
/
├── index.html          # Main dashboard
├── css/
│   └── styles.css      # ICAIRE-branded styles  
├── js/
│   ├── app.js          # Main application logic
│   ├── charts.js       # Chart configurations
│   ├── map.js          # World map logic
│   └── filters.js      # Regional/org filtering
├── data/
│   ├── countries.json  # Master country list with regions, org memberships
│   ├── unesco-ram.json  # UNESCO RAM data
│   ├── stanford-hai.json # Stanford HAI data
│   ├── tortoise.json   # Tortoise Global AI Index
│   ├── oxford.json     # Oxford Insights data
│   ├── girai.json      # GIRAI data
│   ├── imf-aipi.json   # IMF AI Preparedness
│   ├── world-bank.json # World Bank 4Cs
│   ├── icesco.json     # ICESCO AI Index
│   └── oecd.json       # OECD data
├── README.md           # Documentation
└── serve.sh            # Local dev server
```

## Design
- Match ICAIRE website exactly (DIN + Cairo fonts, green palette)
- Professional, institutional, UN-adjacent
- Responsive (mobile-friendly)
- Dark hero, clean data sections
- ICAIRE branding throughout

## Priority Order
1. First: Build the dashboard shell with map + filters + charts framework
2. Second: Populate UNESCO RAM data (we already have this)
3. Third: Add IMF AIPI data (publicly available via datamapper)
4. Fourth: Add Oxford/Tortoise/Stanford summary data
5. Fifth: Add GIRAI, ICESCO, World Bank, OECD
6. Sixth: Time-series tracking

## What Makes This Unique (ICAIRE's Value-Add)
- **No one else aggregates ALL these indices in one place**
- **Cross-index comparison** is completely new
- **Regional organization filters** (ICESCO, GCC, ASEAN) don't exist elsewhere
- **Arabic language support** — no other global AI dashboard has this
- **Ethics-first lens** — curated by a UNESCO ethics center
- **Open, accessible** — free tool for policymakers worldwide
