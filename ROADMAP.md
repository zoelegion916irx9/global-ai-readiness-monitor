# ICAIRE Global AI Readiness Monitor — Roadmap

## Architecture: 4 Tabs

### Tab 1: UNESCO RAM (Assessment)
- Not an index — it's a readiness ASSESSMENT
- Country profiles with qualitative findings
- 5 RAM dimensions (Legal, Social, Economic, Scientific, Tech)
- Status tracker (completed / in process / in preparation)
- Choropleth map as primary view
- Key findings per country
- Recommendations per country

### Tab 2: Global AI Indices
- All quantitative indices aggregated
- Currently: Oxford Insights, IMF AIPI, Tortoise, GIRAI, Stanford HAI, World Bank, ICESCO, OECD, Salesforce
- Scores, rankings, dimensional breakdowns
- Cross-index comparison charts
- Time series (track changes across years)
- Future: ICAIRE Composite Score (needs methodology paper)

### Tab 3: Policies & Regulations (V2)
- AI-specific laws and regulations by country
- Data protection laws
- Governance frameworks
- Timeline of policy adoption
- Compare policies across countries
- Links to original documents

### Tab 4: Strategies (V3)
- National AI strategies
- Compare strategies over time
- Track what has been achieved (public accountability)
- Strategy evolution timeline
- Links to strategy documents

---

## Phases

### Phase 1 (NOW): UNESCO RAM + Indices tabs
- [ ] Choropleth map (colored country regions, not dots)
- [ ] Tab navigation (RAM | Indices)
- [ ] UNESCO RAM tab: map + country cards + dimension analysis
- [ ] Indices tab: map + scores + rankings + charts
- [ ] Country selection via map clicks (not table)
- [ ] Time series charts per index
- [ ] Dynamic comparative charts
- [ ] Beta markers, disclaimers, ICAIRE branding
- [ ] Share with team for review
- **Celebrate this with UNESCO before moving to V2**

### Phase 2: Policies & Regulations tab
- [ ] Policy database (AI laws, data protection, governance frameworks)
- [ ] Policy comparison tools
- [ ] Timeline visualizations
- [ ] Document links

### Phase 3: Strategies tab
- [ ] National AI strategy database
- [ ] Strategy comparison over time
- [ ] Achievement tracking
- [ ] Strategy evolution timeline

### Phase 4: ICAIRE Composite Score
- [ ] Methodology paper (scientifically validated)
- [ ] Model selection (median, weighted, sum — need to validate)
- [ ] Peer review
- [ ] Name: TBD (AiAg, Σ-Score, N-Score, AI₀, GAIR, Σ AI)
- [ ] Methodology section on dashboard

---

## Key Design Decisions

- **Map-first**: Choropleth map is the primary interface
- **Tab-based**: UNESCO RAM separate from indices (different nature)
- **Audience**: Government + researchers + public (all three)
- **Not UNESCO-only**: Open hub for all indices (neutral positioning)
- **Arabic**: Not priority now, build eventually
- **ICAIRE Score**: Will build, needs different name + validated methodology
- **Data freshness**: Need strategy for keeping data up to date (TBD)

---

## Data Freshness Strategy (to solve)
- Automated scrapers for indices that publish regularly?
- GitHub PRs from community?
- Periodic review schedule (quarterly)?
- RSS/webhook monitoring for new publications?
- Cron job to check source URLs for updates?

---

*Created: Feb 19, 2026*
