# MENA AI Readiness Monitor

A single-page web dashboard presenting UNESCO's AI Readiness Assessment Methodology (RAM) results for MENA/Arab countries. Curated by ICAIRE (International Center for AI Research and Ethics), a UNESCO Category 2 Center in Riyadh.

## Quick Start

### Option 1: Simple HTTP Server (Recommended)
```bash
./serve.sh
```
Then open http://localhost:8000 in your browser.

### Option 2: Direct File Opening
Simply open `index.html` in a modern web browser. Note: Some browsers may block loading `data.json` due to CORS restrictions when opening files directly. Use the HTTP server method if you encounter issues.

### Option 3: Any HTTP Server
```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000

# Node.js (if http-server is installed)
npx http-server -p 8000

# PHP
php -S localhost:8000
```

## File Structure

```
mena-ram-dashboard/
├── index.html      # Main dashboard (HTML/CSS/JS embedded)
├── data.json       # All country data (edit this to update content)
├── README.md       # This file
└── serve.sh        # Quick-start server script
```

## Updating the Dashboard

All data is stored in `data.json`. To update the dashboard, simply edit this file.

### Adding a New Completed Country

1. Find the country in the `countries` array
2. Change its `status` from `"notStarted"`, `"inPreparation"`, or `"inProcess"` to `"completed"`
3. Add the required data fields:

```json
{
  "id": "country-id",
  "name": "Country Name",
  "nameAr": "الاسم بالعربية",
  "status": "completed",
  "ramUrl": "https://www.unesco.org/ethics-ai/en/countryname",
  "dimensions": {
    "legalRegulatory": 4,        // 1-5 scale
    "socialCultural": 3,
    "economic": 4,
    "scientificEducational": 4,
    "technologicalInfrastructural": 3
  },
  "comparison": {
    "aiStrategy": { "value": true, "note": "Strategy name/year" },
    "aiStrategyYear": 2024,
    "dedicatedAIAuthority": { "value": true, "note": "Authority name" },
    "dataProtectionLaw": { "value": true, "note": "Law name" },
    "cybersecurityFramework": { "value": true, "note": "Framework details" },
    "aiResearchOutput": "High",           // Very High, High, Moderate, Low
    "infrastructureReadiness": "High",
    "aiEducationTraining": "High",
    "startupEcosystem": "Growing",        // Strong, Growing, Developing
    "genderInclusion": "Moderate",        // Strong, Moderate, Developing
    "environmentalConsiderations": "Developing"
  },
  "keyFindings": [
    "First key finding",
    "Second key finding",
    "Add 6-10 key findings from the RAM report"
  ],
  "highlights": {
    "rank": "Optional ranking info",
    "keyMetrics": [
      { "label": "Metric 1", "value": "Value" },
      { "label": "Metric 2", "value": "Value" },
      { "label": "Metric 3", "value": "Value" }
    ]
  }
}
```

### Changing a Country's Status

Find the country and update the `status` field to one of:
- `"completed"` - RAM assessment is complete
- `"inProcess"` - RAM assessment is currently underway
- `"inPreparation"` - Preparation for RAM assessment has begun
- `"notStarted"` - No RAM activity yet

### Updating the Last Updated Date

Edit the `meta.lastUpdated` field at the top of `data.json`:

```json
{
  "meta": {
    "lastUpdated": "2026-02-19"
  }
}
```

### Adding a New Data Source

Add to the `sources` array:

```json
{
  "name": "Source Name",
  "url": "https://example.com/source"
}
```

## RAM Dimensions Scale

The radar chart uses a 1-5 scale for each dimension:

| Score | Interpretation |
|-------|----------------|
| 5 | Excellent - World-class capabilities |
| 4 | High - Strong capabilities with minor gaps |
| 3 | Moderate - Adequate with notable areas for improvement |
| 2 | Developing - Early stage with significant gaps |
| 1 | Limited - Minimal capabilities |

## Technical Notes

- **No build tools required** - Just HTML, CSS, and JavaScript
- **Chart.js** is loaded from CDN for visualizations
- **Responsive design** - Works on desktop, tablet, and mobile
- **Modern browsers** - Tested on Chrome, Firefox, Safari, Edge

## Troubleshooting

### "Failed to load data.json"
- Use an HTTP server instead of opening the file directly
- Check that `data.json` is in the same directory as `index.html`
- Verify `data.json` contains valid JSON (use a JSON validator)

### Charts not rendering
- Ensure you have internet connectivity (Chart.js loads from CDN)
- Check browser console for JavaScript errors
- Try a different browser

### Styling looks broken
- Clear browser cache
- Ensure CSS is not being blocked by browser extensions

## Credits

- **ICAIRE** - International Center for AI Research and Ethics, UNESCO Category 2 Center
- **UNESCO** - AI Readiness Assessment Methodology (RAM)
- **Chart.js** - Visualization library

## License

This dashboard is provided for informational purposes. Data sourced from UNESCO's Global AI Ethics Observatory.
