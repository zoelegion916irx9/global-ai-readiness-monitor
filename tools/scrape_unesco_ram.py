#!/usr/bin/env python3
"""
UNESCO RAM Scraper
==================
Scrapes the UNESCO AI Ethics Observatory to build/update the RAM dashboard data.

The UNESCO site uses Imperva bot protection, so this scraper fetches pages via
Node.js (using undici fetch) which can bypass the TSPD challenge, or accepts
pre-fetched HTML/text from tools/cache/.

Usage:
    python3 scrape_unesco_ram.py --fetch --merge ../global/data/unesco-ram.json -o ../global/data/unesco-ram.json
    python3 scrape_unesco_ram.py --merge ../global/data/unesco-ram.json  # parse cache only
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / "cache"
BASE_URL = "https://www.unesco.org/ethics-ai/en/"
HUB_URL = BASE_URL + "global-hub"
REQUEST_DELAY = 3.0

# Country name → ISO 3166-1 alpha-2
COUNTRY_ISO = {
    "Angola": "AO", "Antigua and Barbuda": "AG", "Argentina": "AR",
    "Bahrain": "BH", "Bangladesh": "BD", "Belgium": "BE", "Belgium (Flanders)": "BE",
    "Botswana": "BW", "Brazil": "BR", "Cambodia": "KH",
    "Cameroon": "CM", "Canada": "CA", "Canada (Québec)": "CA", "Chad": "TD",
    "Chile": "CL", "Colombia": "CO", "Comoros": "KM",
    "Costa Rica": "CR", "Cuba": "CU", "Curacao": "CW", "Curaçao": "CW",
    "Côte d'Ivoire": "CI",
    "Democratic Republic of Congo": "CD", "Djibouti": "DJ",
    "Dominican Republic": "DO", "Ecuador": "EC", "Egypt": "EG",
    "El Salvador": "SV", "Ethiopia": "ET", "Gabon": "GA",
    "Georgia": "GE", "Germany": "DE", "Ghana": "GH", "Guatemala": "GT",
    "Honduras": "HN", "India": "IN", "Indonesia": "ID",
    "Jamaica": "JM", "Kazakhstan": "KZ", "Kenya": "KE",
    "Laos": "LA", "Lithuania": "LT", "Malawi": "MW",
    "Malaysia": "MY", "Maldives": "MV", "Mauritius": "MU",
    "Mexico": "MX", "Moldova": "MD", "Morocco": "MA",
    "Mozambique": "MZ", "Namibia": "NA", "Netherlands": "NL",
    "Nigeria": "NG", "Oman": "OM", "Palestine": "PS",
    "Panama": "PA", "Paraguay": "PY", "Peru": "PE", "Perú": "PE",
    "Philippines": "PH", "Poland": "PL",
    "Rwanda": "RW", "Saudi Arabia": "SA",
    "São Tomé and Príncipe": "ST", "Senegal": "SN",
    "Singapore": "SG", "Slovakia": "SK", "Slovenia": "SI",
    "Somalia": "SO", "South Africa": "ZA", "South Korea": "KR",
    "Sri Lanka": "LK", "Suriname": "SR",
    "Tanzania": "TZ", "Thailand": "TH",
    "Timor-Leste": "TL", "Timor Leste": "TL",
    "Trinidad and Tobago": "TT", "Tunisia": "TN",
    "Türkiye": "TR", "Turkey": "TR",
    "Uganda": "UG", "Ukraine": "UA", "United Kingdom": "GB",
    "Uruguay": "UY", "Uzbekistan": "UZ",
    "Viet Nam": "VN", "Vietnam": "VN",
    "Zambia": "ZM", "Zimbabwe": "ZW",
}

COUNTRY_SLUGS = {
    "Antigua and Barbuda": "antiguaandbarbuda",
    "Belgium (Flanders)": "belgium", "Canada (Québec)": "canada",
    "Costa Rica": "costarica", "Côte d'Ivoire": "cotedivoire",
    "Democratic Republic of Congo": "drcongo",
    "Dominican Republic": "dominicanrepublic",
    "El Salvador": "elsalvador", "Saudi Arabia": "saudiarabia",
    "São Tomé and Príncipe": "saotomeandprincipe",
    "South Africa": "southafrica", "South Korea": "southkorea",
    "Sri Lanka": "srilanka", "Timor-Leste": "timorleste",
    "Timor Leste": "timorleste", "Trinidad and Tobago": "trinidadandtobago",
    "United Kingdom": "unitedkingdom", "Viet Nam": "vietnam",
    "Türkiye": "turkiye",
}

# Status lists from the UNESCO Global Hub page (Oct 2025 update)
COMPLETED = [
    "Antigua and Barbuda", "Brazil", "Cambodia", "Chad", "Chile", "Cuba",
    "Curacao", "Dominican Republic", "Egypt", "Gabon", "Indonesia",
    "Kenya", "Malaysia", "Maldives", "Mexico", "Morocco", "Mozambique",
    "Namibia", "Netherlands", "Peru", "Philippines", "Saudi Arabia",
    "São Tomé and Príncipe", "Senegal", "South Africa", "Tanzania",
    "Thailand", "Zimbabwe",
]
IN_PROCESS = [
    "Bangladesh", "Bahrain", "Belgium (Flanders)", "Botswana", "Cameroon",
    "Colombia", "Costa Rica", "Côte d'Ivoire", "Democratic Republic of Congo",
    "Ecuador", "Ethiopia", "Georgia", "Ghana", "Guatemala", "India",
    "Jamaica", "Laos", "Malawi", "Mauritius", "Moldova", "Nigeria", "Oman",
    "Palestine", "Paraguay", "Rwanda", "Slovakia", "Slovenia",
    "Timor Leste", "Tunisia", "Türkiye", "Uruguay", "Uzbekistan", "Viet Nam",
]
IN_PREPARATION = [
    "Angola", "Argentina", "Canada (Québec)", "Comoros", "Djibouti",
    "El Salvador", "Honduras", "Kazakhstan", "Panama", "Poland",
    "Somalia", "Sri Lanka", "Suriname", "Trinidad and Tobago",
    "Ukraine", "Uganda", "Zambia",
]

REGION_MAP = {
    "AO": "Africa", "BW": "Africa", "CM": "Africa", "TD": "Africa",
    "CI": "Africa", "CD": "Africa", "EG": "Africa", "ET": "Africa",
    "GA": "Africa", "GH": "Africa", "KE": "Africa", "MW": "Africa",
    "MU": "Africa", "MA": "Africa", "MZ": "Africa", "NA": "Africa",
    "NG": "Africa", "RW": "Africa", "ST": "Africa", "SN": "Africa",
    "SO": "Africa", "ZA": "Africa", "TZ": "Africa", "UG": "Africa",
    "ZM": "Africa", "ZW": "Africa", "KM": "Africa",
    "BH": "Arab States", "DJ": "Arab States", "OM": "Arab States",
    "PS": "Arab States", "SA": "Arab States", "TN": "Arab States",
    "BD": "Asia and the Pacific", "KH": "Asia and the Pacific",
    "IN": "Asia and the Pacific", "ID": "Asia and the Pacific",
    "LA": "Asia and the Pacific", "MY": "Asia and the Pacific",
    "MV": "Asia and the Pacific", "PH": "Asia and the Pacific",
    "SG": "Asia and the Pacific", "KR": "Asia and the Pacific",
    "LK": "Asia and the Pacific", "TH": "Asia and the Pacific",
    "TL": "Asia and the Pacific", "VN": "Asia and the Pacific",
    "KZ": "Asia and the Pacific", "UZ": "Asia and the Pacific",
    "BE": "Europe", "GE": "Europe", "LT": "Europe", "MD": "Europe",
    "NL": "Europe", "PL": "Europe", "SK": "Europe", "SI": "Europe",
    "TR": "Europe", "UA": "Europe", "GB": "Europe", "DE": "Europe",
    "AG": "LAC", "AR": "LAC", "BR": "LAC", "CA": "LAC",
    "CL": "LAC", "CO": "LAC", "CR": "LAC", "CU": "LAC",
    "CW": "LAC", "DO": "LAC", "EC": "LAC", "SV": "LAC",
    "GT": "LAC", "HN": "LAC", "JM": "LAC", "MX": "LAC",
    "PA": "LAC", "PY": "LAC", "PE": "LAC", "SR": "LAC",
    "TT": "LAC", "UY": "LAC",
}


def get_slug(name):
    return COUNTRY_SLUGS.get(name, name.lower().replace(" ", "").replace("'", "").replace("é", "e"))


def fetch_page_via_node(url, output_file):
    """Fetch URL using Node.js https module and write directly to file."""
    js = f"""
const https = require('https');
const fs = require('fs');
const url = {json.dumps(url)};
const outFile = {json.dumps(str(output_file))};
const options = {{
  headers: {{
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'identity',
    'Cache-Control': 'no-cache',
  }}
}};
function doGet(u, depth) {{
  if (depth > 3) {{ process.exit(1); return; }}
  https.get(u, options, (res) => {{
    if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {{
      doGet(res.headers.location, depth + 1);
      return;
    }}
    const chunks = [];
    res.on('data', c => chunks.push(c));
    res.on('end', () => {{
      const data = Buffer.concat(chunks);
      fs.writeFileSync(outFile, data);
      console.log(data.length);
      process.exit(res.statusCode >= 400 ? 1 : 0);
    }});
  }}).on('error', (e) => {{ console.error(e.message); process.exit(1); }});
}}
doGet(url, 0);
"""
    try:
        result = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True
    except Exception as e:
        log.error("Node fetch error: %s", e)
    return False


def fetch_and_cache_pages(delay=REQUEST_DELAY):
    """Fetch completed country pages to cache."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    succeeded = 0
    failed = 0
    
    for i, name in enumerate(sorted(COMPLETED)):
        slug = get_slug(name)
        cache_file = CACHE_DIR / f"{slug}.html"
        
        # Skip if recently cached
        if cache_file.exists() and cache_file.stat().st_size > 5000:
            age_h = (time.time() - cache_file.stat().st_mtime) / 3600
            if age_h < 24:
                log.info("  ⏭ %s — cached (%.1fh old)", name, age_h)
                succeeded += 1
                continue
        
        url = BASE_URL + slug
        log.info("  Fetching %s...", name)
        
        if fetch_page_via_node(url, cache_file):
            html = cache_file.read_text(errors="replace")
            if "bobcmn" in html[:3000]:
                log.warning("  ✗ %s — TSPD challenge", name)
                cache_file.unlink(missing_ok=True)
                failed += 1
            elif "Request Rejected" in html or len(html) < 1000:
                log.warning("  ✗ %s — rejected/empty", name)
                cache_file.unlink(missing_ok=True)
                failed += 1
            else:
                log.info("  ✓ %s — %d bytes", name, len(html))
                succeeded += 1
        else:
            log.warning("  ✗ %s — fetch failed", name)
            failed += 1
        
        if i < len(COMPLETED) - 1:
            time.sleep(delay)
    
    log.info("Fetch complete: %d succeeded, %d failed", succeeded, failed)


def extract_key_findings_from_html(html):
    """Extract key findings from raw HTML using BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    findings = []
    
    # Try id="key-insights"
    ki_div = soup.find(id="key-insights")
    if ki_div:
        for li in ki_div.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 20:
                findings.append(_trunc(text))
    
    # Fallback: h2 containing "Key Insight"
    if not findings:
        for h2 in soup.find_all("h2"):
            if "Key Insight" in h2.get_text():
                parent = h2.find_parent("div", class_="paragraph")
                if parent:
                    for li in parent.find_all("li"):
                        text = li.get_text(strip=True)
                        if text and len(text) > 20:
                            findings.append(_trunc(text))
                break
    
    return findings[:5]


def extract_region_from_html(html):
    """Extract region from article data-region attribute."""
    m = re.search(r'data-region="([^"]+)"', html)
    if m:
        return m.group(1).split(";")[0].strip()
    return None


def _trunc(text, max_len=200):
    if len(text) <= max_len:
        return text
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences[0] if sentences else text[:max_len]


def parse_all_cached():
    """Parse all cached country pages and return details dict."""
    details = {}
    for name in COMPLETED:
        slug = get_slug(name)
        cache_file = CACHE_DIR / f"{slug}.html"
        
        if not cache_file.exists():
            continue
        
        html = cache_file.read_text(errors="replace")
        if "bobcmn" in html[:3000] or "Request Rejected" in html or len(html) < 1000:
            continue
        
        findings = extract_key_findings_from_html(html)
        region = extract_region_from_html(html)
        iso = COUNTRY_ISO.get(name, "")
        
        details[name] = {
            "ramUrl": BASE_URL + slug,
            "keyFindings": findings,
            "region": region or REGION_MAP.get(iso),
        }
        
        log.info("  ✓ %s — %d findings", name, len(findings))
    
    return details


def build_output(country_details, existing_data=None):
    """Build final JSON matching the dashboard format."""
    existing_map = {}
    if existing_data and "countries" in existing_data:
        for c in existing_data["countries"]:
            existing_map[c["iso"]] = c

    countries = []
    seen = set()

    all_countries = {}
    for name in COMPLETED:
        all_countries[name] = "completed"
    for name in IN_PROCESS:
        all_countries[name] = "inProcess"
    for name in IN_PREPARATION:
        all_countries[name] = "inPreparation"

    for name, status in sorted(all_countries.items()):
        iso = COUNTRY_ISO.get(name)
        if not iso or iso in seen:
            continue
        seen.add(iso)

        old = existing_map.get(iso, {})
        new = country_details.get(name, {})
        slug = get_slug(name)

        entry = {
            "iso": iso,
            "status": status,
            "ramUrl": new.get("ramUrl") or old.get("ramUrl") or (
                BASE_URL + slug if status == "completed" else None
            ),
            "dimensions": old.get("dimensions"),  # Always preserve — not on website
            "keyFindings": new.get("keyFindings") or old.get("keyFindings"),
        }

        if status != "completed" and not entry["dimensions"]:
            entry["dimensions"] = None
        if status != "completed" and not entry["keyFindings"]:
            entry["keyFindings"] = None

        countries.append(entry)

    # Include extra countries from existing (e.g. SG, KR, GB, DE, LT, MU, TT)
    for iso, old in existing_map.items():
        if iso not in seen:
            countries.append(old)
            seen.add(iso)

    order = {"completed": 0, "inProcess": 1, "inPreparation": 2}
    countries.sort(key=lambda c: (order.get(c["status"], 9), c["iso"]))

    return {
        "meta": {
            "source": "UNESCO AI Readiness Assessment Methodology (RAM)",
            "url": HUB_URL,
            "lastUpdated": date.today().isoformat(),
            "dimensions": [
                "Legal & Regulatory", "Social & Cultural", "Economic",
                "Scientific & Educational", "Technological & Infrastructural",
            ],
        },
        "countries": countries,
    }


def main():
    p = argparse.ArgumentParser(description="Scrape UNESCO RAM data")
    p.add_argument("--output", "-o", help="Output file (default: stdout)")
    p.add_argument("--merge", "-m", help="Existing JSON to preserve dimension scores from")
    p.add_argument("--fetch", action="store_true", help="Fetch country pages to cache first")
    p.add_argument("--delay", type=float, default=REQUEST_DELAY)
    p.add_argument("--cache-dir", type=Path, default=CACHE_DIR)
    args = p.parse_args()

    if args.fetch:
        log.info("=== Fetching country pages ===")
        fetch_and_cache_pages(delay=args.delay)

    log.info("=== Parsing cached pages ===")
    details = parse_all_cached()
    log.info("Parsed %d countries with data", len(details))

    existing = None
    if args.merge:
        with open(args.merge) as f:
            existing = json.load(f)
        log.info("Merging with existing data (%d countries)", len(existing.get("countries", [])))

    output = build_output(details, existing)
    result = json.dumps(output, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(result + "\n")
        log.info("Written %d countries to %s", len(output["countries"]), args.output)
    else:
        print(result)


if __name__ == "__main__":
    main()
