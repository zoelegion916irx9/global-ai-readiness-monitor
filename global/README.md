# ICAIRE Global AI Readiness Monitor

The world's first comprehensive interactive dashboard aggregating **9 major AI readiness indices** into a single analytical tool.

**By ICAIRE** — UNESCO International Center for Artificial Intelligence Research & Ethics, Riyadh.

## Live Features

| Feature | Description |
|---------|-------------|
| **Interactive World Map** | Leaflet-powered map with UNESCO RAM status markers. Click any country for a detailed profile. |
| **Index Selector** | Toggle which of the 9 indices are active in the analysis. |
| **Regional & Org Filters** | Filter by region (MENA, Africa, Asia-Pacific, Europe, Americas, SIDS) or international org (OECD, OIC, EU, G20, G7, GPAI, BRICS+, GCC, ASEAN, AU, Arab League). |
| **Radar Comparison** | Search and select up to 10 countries to overlay on a radar chart across UNESCO RAM's 5 dimensions. |
| **Bar Rankings** | Rank all filtered countries by any single RAM dimension. |
| **Scatter Correlation** | Plot any two RAM dimensions against each other to find patterns. |
| **Gap Analysis** | Coverage matrix showing which indices assess which countries. |
| **Data Sources** | Links to all 9 source indices with metadata. |

## Data Sources

1. **UNESCO RAM** — 70+ countries, 5 qualitative dimensions
2. **Stanford HAI** — AI Index & Global Vibrancy Tool
3. **Tortoise Global AI Index** — 83 countries, 122 indicators
4. **Oxford Insights** — Government AI Readiness, 193 countries
5. **GIRAI** — Global Index on Responsible AI, 138 countries
6. **IMF AIPI** — AI Preparedness Index, 174 economies
7. **World Bank 4Cs** — Connectivity, Compute, Competencies, Compatibility
8. **ICESCO AI Index** — Islamic World focus, 9 countries
9. **OECD AI Observatory** — Policy tracking, ~70 countries

## Running Locally

```bash
cd global/
python3 -m http.server 8080
# Open http://localhost:8080
```

Or use any static file server (e.g., `npx serve .`).

## Tech Stack

- **Chart.js 4** — Radar, bar, scatter charts
- **Leaflet.js** — Interactive world map with CARTO tiles
- **Vanilla JS** — No framework dependencies, IIFE modules
- **Google Fonts** — DM Sans + Cairo (Arabic)

## Architecture

```
global/
├── index.html          # Main dashboard page
├── css/styles.css      # ICAIRE-branded stylesheet
├── js/
│   ├── app.js          # Main orchestrator — loads data, wires everything
│   ├── charts.js       # Chart.js radar/bar/scatter configs
│   ├── filters.js      # Region/org/index filter state machine
│   └── map.js          # Leaflet map initialization & markers
└── data/
    ├── countries.json   # Master list (193 countries, coords, memberships)
    ├── indices-meta.json # Index metadata (name, url, coverage, color)
    └── *.json           # Per-index country data
```

## Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Primary | `#1A5C3A` | Buttons, headings, active states |
| Accent | `#4DC88E` | Highlights, charts, badges |
| Dark | `#0D3D2A` | Text, dark sections |
| Darkest | `#091F16` | Hero, footer backgrounds |

## License

Dashboard code: MIT. All index data belongs to its respective publishers (UNESCO, Stanford, Tortoise, Oxford Insights, IRCAI, IMF, World Bank, ICESCO, OECD).
