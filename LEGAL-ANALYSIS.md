# Legal Analysis: Aggregating AI Readiness Index Data for ICAIRE Dashboard

**Prepared for:** ICAIRE (International Center for AI Research and Ethics), UNESCO Category 2 Center, Riyadh  
**Date:** February 19, 2026  
**Purpose:** Legal rights and permissions analysis for aggregating publicly available AI readiness index data into a comparative dashboard

---

## Executive Summary

ICAIRE is well-positioned to aggregate AI readiness index data into a comparative dashboard. As a UNESCO Category 2 Center operating for non-commercial, research and policy purposes, most sources present **low to medium legal risk**. The majority of indices are published under open or permissive licenses (Creative Commons), or by international organizations with open data policies. The main exception is **Tortoise Global AI Index**, which explicitly restricts reproduction. For all sources, proper attribution is essential and sufficient in most cases.

**Key principle:** Factual data (rankings, scores, country-level statistics) is generally not copyrightable. Copyright protects the *expression* and *creative arrangement* of data, not the underlying facts. This is well-established in US law (*Feist v. Rural Telephone*) and broadly recognized internationally.

---

## Summary Table: Data Rights by Index

| # | Index | License / Terms | Third-Party Aggregation | Commercial Use | API/Download | Risk Level |
|---|-------|----------------|------------------------|---------------|-------------|------------|
| 1 | UNESCO RAM | CC BY 3.0 IGO (Open Access Policy) | ✅ Yes, with attribution | ✅ Allowed | Reports via UNESDOC | 🟢 **Low** |
| 2 | Stanford HAI AI Index | Open access report; data on GitHub | ✅ Yes, with citation | ✅ Academic/research encouraged | GitHub datasets, PDF | 🟢 **Low** |
| 3 | Tortoise Global AI Index | All rights reserved; "No part may be reproduced without permission" | ⚠️ Requires permission | ❌ Restricted | No public API; interactive tool only | 🔴 **High** |
| 4 | Oxford Insights Gov't AI Readiness | CC BY-SA 4.0 | ✅ Yes, with attribution + ShareAlike | ✅ Allowed (ShareAlike) | PDF report, data downloads | 🟢 **Low** |
| 5 | GIRAI | CC BY-SA-NC (NonCommercial) | ✅ Yes, non-commercial with attribution | ❌ Non-commercial only | Website explorer | 🟢 **Low** |
| 6 | IMF AIPI | IMF open data policy (free access & reuse) | ✅ Yes, with attribution | ✅ Allowed | DataMapper tool, downloadable | 🟢 **Low** |
| 7 | World Bank Digital Progress & Trends | CC BY 3.0 IGO / CC BY 4.0 (Open Data) | ✅ Yes, with attribution | ✅ Allowed | Open Data portal, API | 🟢 **Low** |
| 8 | ICESCO AI Index | No explicit open license found (new index, Dec 2025) | ⚠️ Seek permission | ❓ Unknown | Not yet publicly available as dataset | 🟡 **Medium** |
| 9 | OECD AI Policy Observatory | CC BY 4.0 (since July 2024 Open Access Policy) | ✅ Yes, with attribution | ✅ Allowed | OECD.AI portal, data explorer | 🟢 **Low** |

---

## Detailed Analysis by Index

### 1. UNESCO RAM (Readiness Assessment Methodology)

- **License:** CC BY 3.0 IGO. UNESCO's Open Access Policy (adopted April 2013) requires all publications since July 2013 to be released under Creative Commons IGO licenses.
- **Aggregation:** Fully permitted with attribution.
- **Attribution:** "Source: UNESCO" with full citation to the specific publication.
- **Commercial use:** Allowed under CC BY.
- **API/Download:** Reports available via [UNESDOC](https://unesdoc.unesco.org).
- **Special note:** As a UNESCO Category 2 Center, ICAIRE has an even stronger institutional basis for using UNESCO data. The relationship with UNESCO provides implicit authorization, though formal attribution remains required.
- **Terms URL:** https://en.unesco.org/open-access/
- **Risk: 🟢 LOW**

### 2. Stanford HAI AI Index / Global AI Vibrancy Tool

- **License:** The AI Index Report is published as an open-access academic resource. Historical data has been shared on [GitHub](https://github.com/ai-index-hai-stanford/AI-Index-2020). The report encourages wide citation and dissemination.
- **Aggregation:** Permitted with proper academic citation.
- **Attribution:** Cite as: "AI Index 2025 Annual Report, AI Index Steering Committee, Institute for Human-Centered AI, Stanford University, Stanford, CA, [Month] 2025."
- **Commercial use:** Primarily intended for academic/policy use; no explicit commercial restriction found, but contact recommended for commercial applications.
- **API/Download:** PDF report; GitHub data repositories for historical editions; Global AI Vibrancy Tool is interactive.
- **Terms URL:** https://hai.stanford.edu/ai-index
- **Risk: 🟢 LOW**

### 3. Tortoise Global AI Index

- **License:** **All rights reserved.** Methodology report explicitly states: *"© Tortoise Media 2024. No part of this index may be reproduced without permission."*
- **Aggregation:** **Not permitted without explicit written permission.** Terms prohibit reproduction, transmission, or provision of content to third parties.
- **Attribution:** N/A without permission.
- **Commercial use:** Prohibited.
- **API/Download:** No public API or downloadable dataset. Data viewable only through their interactive tool.
- **Terms URL:** https://www.tortoisemedia.com/policy/terms
- **Recommendation:** 
  - **Option A:** Contact Tortoise Media for a formal data-sharing agreement or license.
  - **Option B:** Link to their interactive tool rather than reproducing data.
  - **Option C:** Use only publicly visible rankings/scores with citation (arguable under factual data doctrine, but carries risk).
- **Risk: 🔴 HIGH**

### 4. Oxford Insights Government AI Readiness Index

- **License:** **CC BY-SA 4.0 International** (Creative Commons Attribution-ShareAlike 4.0).
- **Aggregation:** Fully permitted. Must share derivative works under same or compatible license.
- **Attribution:** "Source: Oxford Insights, Government AI Readiness Index [year]. Licensed under CC BY-SA 4.0."
- **Commercial use:** Allowed, but derivative works must also be CC BY-SA 4.0.
- **API/Download:** Full report PDF with data; contact research@oxfordinsights.com for datasets.
- **ShareAlike implication:** If the dashboard is considered a derivative work, the dashboard content incorporating this data should also be CC BY-SA 4.0. However, a dashboard that merely *displays* the data alongside other sources is likely a *collection* rather than a *derivative*, which reduces this concern.
- **Terms URL:** See report footer (2024 edition): https://oxfordinsights.com/wp-content/uploads/2024/12/2024-Government-AI-Readiness-Index-2.pdf
- **Risk: 🟢 LOW**

### 5. GIRAI - Global Index on Responsible AI

- **License:** **CC BY-SA-NC** (Creative Commons Attribution-ShareAlike-NonCommercial). Per their terms of use page.
- **Aggregation:** Permitted for non-commercial purposes with attribution.
- **Attribution:** "Source: Global Index on Responsible AI (GIRAI), [year]."
- **Commercial use:** **Not permitted** under NC clause. ICAIRE's non-commercial, research/policy purpose is fully compatible.
- **API/Download:** Interactive data explorer on website.
- **Terms URL:** https://www.global-index.ai/utility/terms-of-use
- **Risk: 🟢 LOW** (given ICAIRE's non-commercial status)

### 6. IMF AI Preparedness Index (AIPI)

- **License:** IMF Open Data Policy. IMF data is freely accessible and reusable with attribution. The policy states: *"Data obtained from IMF Sites may be distributed or reproduced, subject to attribution."*
- **Aggregation:** Fully permitted with source attribution.
- **Attribution:** "Source: International Monetary Fund." Must not imply IMF endorsement.
- **Commercial use:** Allowed for data; publications require permission via Copyright Clearance Center.
- **API/Download:** IMF DataMapper provides interactive access and data download at https://www.imf.org/external/datamapper/datasets/AIPI
- **Terms URL:** https://www.imf.org/en/about/copyright-and-terms
- **Risk: 🟢 LOW**

### 7. World Bank Digital Progress & Trends Report

- **License:** **CC BY 3.0 IGO** (report) / **CC BY 4.0** (Open Data portal datasets). The report explicitly states: *"Under the Creative Commons Attribution license, you are free to copy, distribute, transmit, and adapt this work, including for commercial purposes."*
- **Aggregation:** Fully permitted with attribution.
- **Attribution:** "Source: World Bank. [Full citation]. License: Creative Commons Attribution CC BY 3.0 IGO."
- **Commercial use:** Allowed.
- **API/Download:** World Bank Open Data portal (https://data.worldbank.org), Data360 (https://data360.worldbank.org). Full API available.
- **Terms URL:** https://data.worldbank.org/summary-terms-of-use
- **Risk: 🟢 LOW**

### 8. ICESCO AI Index for the Islamic World

- **License:** **No explicit open data license found.** The index was launched in December 2025 and is very new. Currently covers 9 countries. No publicly available dataset or terms of use for the data were identified.
- **Aggregation:** Seek formal permission from ICESCO. As a sister organization (both UNESCO-affiliated), a cooperation agreement is the natural path.
- **Attribution:** TBD pending agreement.
- **Commercial use:** Unknown.
- **API/Download:** Not yet publicly available as a downloadable dataset.
- **Recommendation:** Given ICESCO and ICAIRE's shared institutional ecosystem (both related to UNESCO/OIC), pursue a **formal MoU or data-sharing agreement**. ICESCO has signed cooperation agreements with SDAIA; a similar arrangement with ICAIRE would be appropriate.
- **Terms URL:** https://icesco.org (general)
- **Risk: 🟡 MEDIUM**

### 9. OECD AI Policy Observatory

- **License:** **CC BY 4.0** (since OECD Open Access Policy, July 2024). Most OECD written content is now freely reusable with attribution.
- **Aggregation:** Fully permitted with attribution.
- **Attribution:** "Source: OECD AI Policy Observatory (OECD.AI), [year]." Must not imply OECD endorsement.
- **Commercial use:** Allowed under CC BY 4.0.
- **API/Download:** OECD.AI portal (https://oecd.ai) with interactive dashboards and data explorer. OECD iLibrary for publications.
- **Terms URL:** https://www.oecd.org/en/about/terms-conditions.html
- **Risk: 🟢 LOW**

---

## Legal Framework for Data Aggregation

### Factual Data and Copyright

- **Facts are not copyrightable.** Country-level scores, rankings, and index values are factual data. Under both common law (*Feist Publications v. Rural Telephone*, US Supreme Court 1991) and civil law traditions, pure factual compilations receive minimal or no copyright protection.
- **Copyright protects expression**, not the underlying data. The *arrangement, selection, and creative presentation* of data may be protected, but the individual data points (e.g., "Country X scored 0.72 on AI readiness") are free to use.
- **Implication:** Even where an index is "all rights reserved," reproducing the *factual scores and rankings* in a different format/arrangement (your own dashboard) has strong legal footing, provided you cite the source.

### EU Database Rights (Sui Generis)

- The EU Database Directive grants rights to database creators who made "substantial investment" in obtaining, verifying, or presenting database contents.
- **Extraction of insubstantial parts** is permitted. Displaying country scores from an index is an insubstantial extraction.
- **ICAIRE's position:** As a Saudi-based UNESCO center, EU database rights do not directly apply. However, if serving EU users or using EU-based servers, awareness is prudent.
- **Mitigation:** Use only the aggregate scores/rankings (not the full underlying dataset), cite sources, and add value through your own analysis/comparison.

### Fair Use / Fair Dealing

- **Fair use (US):** Aggregating factual data for research, education, and policy purposes is strongly favored. All four factors support ICAIRE: (1) non-commercial/educational purpose, (2) factual nature of the work, (3) small proportion used, (4) no market substitution.
- **Fair dealing (UK/Commonwealth):** Research and private study exceptions apply. Non-commercial research with sufficient acknowledgment is permitted.
- **Saudi Arabia:** Copyright Law (Royal Decree M/41, 2003) provides exceptions for scientific research and quotation with attribution.

---

## How Similar Dashboards Handle Multi-Source Data

### Our World in Data
- Uses **CC BY 4.0** for their own content
- Always cites original data sources and their specific licenses
- States: *"Our work would not be possible without the data providers we rely on, so we ask you to always respect their license terms and cite them appropriately."*
- Transforms and adds value to source data (calculations, visualizations, commentary)
- **Key practice:** Each chart/dataset page includes a "Sources" tab with full attribution

### UN SDG Indicators Dashboard
- Aggregates data from 50+ UN agencies
- Uses standardized metadata and source attribution
- Operates under UN Open Data principles
- Disclaimer: data is provided "as is" without warranty

### Gapminder
- CC BY 4.0 license for their own work
- Always attributes original sources
- Provides methodology documentation
- Distinguishes between "Gapminder data" and "third-party data"

### Best Practices Pattern
1. **Always attribute** the original source prominently
2. **Add value** — don't just mirror; provide analysis, comparison, visualization
3. **Link back** to original sources
4. **Note data vintage** (year, version of each index)
5. **Distinguish** your analysis from source data
6. **Maintain** a clear data sources page

---

## Recommended Disclaimer Text

### Primary Dashboard Disclaimer

> **Data Sources & Disclaimer**
> 
> This dashboard aggregates publicly available data from multiple independent AI readiness and governance indices for comparative research and policy analysis purposes. It is produced by the International Center for AI Research and Ethics (ICAIRE), a UNESCO Category 2 Center based in Riyadh, Saudi Arabia.
> 
> **The data presented reflects the methodologies, timeframes, and assessments of each respective source organization.** ICAIRE does not endorse any particular index methodology and does not guarantee the accuracy, completeness, or timeliness of the data displayed. Each index employs different definitions, indicators, and scoring methodologies; direct numerical comparisons across indices should be made with caution.
> 
> The inclusion of data from any organization does not imply endorsement of this dashboard by that organization, nor does it imply any institutional affiliation beyond what is explicitly stated.
> 
> The designations employed and the presentation of material on this dashboard do not imply the expression of any opinion whatsoever on the part of ICAIRE or UNESCO concerning the legal status of any country, territory, city, or area, or of its authorities, or concerning the delimitation of its frontiers or boundaries.
> 
> This dashboard is provided for informational, research, and policy analysis purposes only. It is not intended as a definitive assessment of any country's AI capabilities or governance.
> 
> For the most current and authoritative data, users are encouraged to consult the original source publications directly.

### Territorial Disclaimer (Standard for International Organizations)

> The boundaries and names shown and the designations used on any maps or visualizations do not imply official endorsement or acceptance by ICAIRE, UNESCO, or the United Nations.

---

## Recommended Attribution Format

### Per-Index Attribution (on each visualization/data point)

```
Source: [Index Name] ([Year Edition]), [Organization Name]. [URL]
```

**Examples:**
- Source: Government AI Readiness Index 2024, Oxford Insights. Licensed under CC BY-SA 4.0. https://oxfordinsights.com/ai-readiness/ai-readiness-index/
- Source: AI Preparedness Index (AIPI), International Monetary Fund. https://www.imf.org/external/datamapper/datasets/AIPI
- Source: AI Index Report 2025, Stanford Institute for Human-Centered AI (HAI). https://hai.stanford.edu/ai-index

### Aggregated Sources Page

Maintain a dedicated "Data Sources & Methodology" page listing:
1. Full name and URL of each index
2. License type
3. Year/edition used
4. Any transformations applied to the data
5. Link to the index's own methodology documentation

---

## Risk Assessment Summary

| Risk Level | Indices | Action Required |
|-----------|---------|----------------|
| 🟢 **Low** | UNESCO RAM, Stanford HAI, Oxford Insights, IMF AIPI, World Bank, OECD, GIRAI | Standard attribution; comply with license terms |
| 🟡 **Medium** | ICESCO AI Index | Seek formal data-sharing agreement (MoU) |
| 🔴 **High** | Tortoise Global AI Index | Must obtain written permission or exclude/link only |

---

## Recommended Actions

### Immediate (Before Launch)

1. **Contact Tortoise Media** — Request formal permission to display their index data, or decide to exclude/link-only. Email their partnerships team explaining ICAIRE's non-commercial, UNESCO-affiliated research purpose.

2. **Contact ICESCO** — Pursue an MoU or data-sharing agreement. Given shared institutional ties (OIC/UNESCO ecosystem), this should be straightforward.

3. **Implement attribution system** — Build source attribution into the dashboard UI so every data point links to its source.

4. **Draft and publish the disclaimer** — Use the recommended text above, adapted to your specific dashboard design.

### Ongoing

5. **Monitor license changes** — Check annually whether source licenses have changed (especially OECD's recent shift to CC BY 4.0 and any changes at Tortoise).

6. **Maintain a data provenance log** — Document when data was retrieved, from which URL, under which version of terms.

7. **Respect ShareAlike** — For Oxford Insights (CC BY-SA 4.0) and GIRAI (CC BY-SA-NC), if your dashboard qualifies as a derivative work, your derived content should be released under a compatible license. A simple approach: release the dashboard under CC BY-SA-NC 4.0 (the most restrictive compatible license covering all sources).

### Legal Best Practices

8. **Add value, don't just mirror** — Provide your own analysis, MENA-focused insights, methodology comparisons, and visualizations. This strengthens fair use arguments and differentiates the dashboard.

9. **Use only aggregate scores** — Display country-level scores and rankings, not full underlying datasets. This keeps extraction "insubstantial" for database rights purposes.

10. **No implied endorsement** — Never suggest that source organizations endorse or are affiliated with the dashboard beyond the factual statement that their data is cited.

---

## Recommended Dashboard License

Given the mix of source licenses, the recommended license for the ICAIRE dashboard's own content is:

**CC BY-NC-SA 4.0** (Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International)

This is compatible with:
- CC BY sources (UNESCO, IMF, World Bank, OECD, Stanford HAI) — more restrictive is fine
- CC BY-SA sources (Oxford Insights) — ShareAlike satisfied
- CC BY-SA-NC sources (GIRAI) — both NC and SA satisfied
- ICAIRE's non-commercial institutional mandate

---

## References

| Source | Key URL |
|--------|---------|
| UNESCO Open Access Policy | https://en.unesco.org/open-access/ |
| Stanford HAI AI Index | https://hai.stanford.edu/ai-index |
| Tortoise Terms & Conditions | https://www.tortoisemedia.com/policy/terms |
| Tortoise AI Index Methodology | https://www.tortoisemedia.com/_app/immutable/assets/AI-Methodology-2409.BGTLUPC-.pdf |
| Oxford Insights AI Readiness Index | https://oxfordinsights.com/ai-readiness/ai-readiness-index/ |
| GIRAI Terms of Use | https://www.global-index.ai/utility/terms-of-use |
| IMF Copyright & Usage | https://www.imf.org/en/about/copyright-and-terms |
| World Bank Terms of Use | https://data.worldbank.org/summary-terms-of-use |
| ICESCO AI Index Announcement | https://icesco.org/en/2025/12/09/icesco-launches-ai-index-for-the-islamic-world/ |
| OECD Terms & Conditions | https://www.oecd.org/en/about/terms-conditions.html |
| Our World in Data FAQs | https://ourworldindata.org/faqs |

---

*This analysis is provided for informational purposes and does not constitute legal advice. For binding legal opinions, consult qualified legal counsel specializing in international intellectual property law.*
