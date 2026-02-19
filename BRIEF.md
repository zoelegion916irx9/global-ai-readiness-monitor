# MENA AI Readiness (RAM) Comparative Dashboard

## What to Build
A single-page web application (HTML/CSS/JS, no build tools) that presents a comparative analysis of UNESCO's AI Readiness Assessment Methodology (RAM) results for MENA/Arab countries. This is for ICAIRE (International Center for AI Research and Ethics), a UNESCO Category 2 Center in Riyadh.

## Design
- Modern, clean, professional — suitable for an international organization
- ICAIRE branding: use blues/teals + white
- Responsive (mobile-friendly)
- Single HTML file with embedded CSS/JS (easy to deploy anywhere)
- Use Chart.js for any visualizations (CDN)
- Arabic/English labels where appropriate

## Sections

### 1. Hero / Header
- Title: "MENA AI Readiness Monitor"
- Subtitle: "UNESCO RAM Comparative Analysis — Curated by ICAIRE"
- Brief explanation of what RAM is

### 2. Status Tracker Map/Grid
Visual showing ALL Arab League countries with their RAM status:
- ✅ Completed: Saudi Arabia, Egypt, Morocco
- 🔄 In Process: Bahrain, Oman, Palestine
- 📋 In Preparation: Tunisia, Djibouti
- ❌ Not Started: UAE, Qatar, Kuwait, Jordan, Iraq, Libya, Lebanon, Syria, Yemen, Sudan, Somalia, Algeria, Mauritania, Comoros

### 3. Country Cards (Completed Countries)
Side-by-side comparison cards for Saudi Arabia, Egypt, Morocco with:

**Saudi Arabia — Key Findings:**
- Unique SDAIA (Data & AI Authority) leading strategy, policymaking, regulation
- Governance framework still under development — opportunity to shape it
- Need for AI-specific regulatory sandboxes
- Critical talent gap — need to attract/retain internationally competitive talent
- Educational reform underway but need to integrate ethics + human-centric design
- Women empowerment in STEM essential
- AI ecosystem maturity pivotal for global competitiveness
- Sustainability must be cornerstone of AI infrastructure
- Cross-pollination needed between private/public, international/local
- Need cohesive, tightly-knit ecosystem

**Egypt — Key Findings:**
- Ranked 1st in Africa, 7th in MENA (Oxford Insights Government AI Readiness 2024)
- National Council for AI (NCAI) established 2019
- AI Strategy: 1st edition 2021, 2nd edition (2025-2030) launched Jan 2025
- Charter for Responsible AI adopted 2023
- Legal: Cybercrimes Law (2018) + Data Protection Law (2020)
- Leads Arab region in AI research publications per capita (0.28 per 1,000 people)
- Top in citations per capita (0.45 per 1,000)
- 92 AI institutes (27 public, 20 private, 20 national, 10 international, 15 high institutes)
- 500,000+ people trained annually in digital skills
- #2 in MENA Startup Ecosystem for Knowledge (Startup Genome)
- Startup funding surged $190M (2020) → $517M (2022)
- 9 innovation hubs
- 6,000+ km fiber optic network; 16x broadband speed increase (2017-2025)
- 1,458 villages connected to high-speed internet

**Morocco — Key Findings:**
- Favorable ecosystem for holistic, responsible AI vision
- Assets in research, training, regulation, data governance, e-inclusion
- Most significant gaps: technological infrastructure
- Internet penetration improved; Inclusive Internet Index ranked 52nd (2022)
- Negligible gender gap in internet access
- One of highest rates globally for female engineering graduates (2018)
- 27% STEM graduates (2022)
- Educational institutions dedicated exclusively to AI training
- R&D investment relatively low at 0.75% of GDP
- NO national AI strategy (only digital strategy)
- Legal frameworks need adaptation for AI (personal data, cyberspace)
- Need liability regime + public procurement regulations for responsible AI
- Lack of linguistic diversification in digital services
- AI investments increased 2020-2023 but moderate vs neighbors
- Key sectors: health/biotech, media/marketing, IT infrastructure
- ITU Cybersecurity Index: 50th globally
- Open Data Index: 35th out of 195
- E-Government Index improved from 0.5729 (2020) to 0.5915 (2022), ranked 101st

### 4. Comparison Table
A sortable/filterable table comparing countries across dimensions:
- Legal & Regulatory framework
- AI Strategy (yes/no, year)
- Dedicated AI Authority (yes/no)
- Data Protection Law (yes/no)
- Cybersecurity framework
- AI Research output
- Infrastructure readiness
- AI Education/Training
- Startup ecosystem
- Gender inclusion
- Environmental considerations

### 5. RAM Dimensions Radar Chart
Radar/spider chart comparing the 3 completed countries across the 5 RAM dimensions (qualitative assessment based on the findings):
- Legal & Regulatory
- Social & Cultural
- Economic
- Scientific & Educational
- Technological & Infrastructural

Use a 1-5 scale based on the qualitative findings.

### 6. Gap Analysis — ICAIRE Opportunity
Section highlighting:
- Which countries haven't started RAM
- Where ICAIRE can add value as regional knowledge partner
- Comparison with India's model (Ikigai Law partnership)
- Call to action for ICAIRE's role

### 7. Data Sources & Links
- UNESCO Global AI Ethics Observatory: https://www.unesco.org/ethics-ai/en
- UNESCO Global Hub (all RAM countries): https://www.unesco.org/ethics-ai/en/global-hub
- Individual country profiles:
  - Saudi Arabia: https://www.unesco.org/ethics-ai/en/saudiarabia
  - Egypt: https://www.unesco.org/ethics-ai/en/egypt
  - Morocco: https://www.unesco.org/ethics-ai/en/morocco
  - India (reference): https://www.unesco.org/ethics-ai/en/india

### 8. Update Mechanism
- Include a JSON data file (data.json) that stores all country data
- The HTML reads from this JSON
- To update: just edit the JSON file
- Include clear comments showing where to add new countries
- Include a "Last Updated" timestamp
- Include instructions in a README.md for how to update

## Technical
- Single `index.html` with embedded styles
- `data.json` for country data (separated for easy updates)
- Chart.js from CDN for visualizations
- No build tools, no npm, no frameworks
- Must work by just opening index.html in a browser (or simple HTTP server)
- README.md with update instructions

## Files to Create
1. `index.html` — main dashboard
2. `data.json` — all country data
3. `README.md` — how to update/maintain
4. `serve.sh` — simple script to serve locally (python -m http.server)
