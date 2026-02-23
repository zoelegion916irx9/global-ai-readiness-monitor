#!/usr/bin/env python3
"""
UNESCO RAM Report PDF Extractor
Extracts structured data from RAM assessment reports for the Global RAM Monitor dashboard.

Usage:
    python extract_ram_pdf.py <pdf_path> <country_code> [--output-dir <dir>]

Outputs:
    - <country_code>_extracted.json  (structured data for dashboard)
    - <country_code>_full_text.md    (full text for RAG/search)
"""

import fitz  # PyMuPDF
import json
import re
import sys
import os
from pathlib import Path


def extract_full_text(doc):
    """Extract all text from PDF, page by page."""
    pages = []
    for i in range(doc.page_count):
        text = doc[i].get_text()
        if text.strip():
            pages.append({
                "page": i + 1,
                "text": text.strip()
            })
    return pages


def detect_chapters(pages):
    """Detect chapter boundaries and titles."""
    chapters = []
    chapter_pattern = re.compile(
        r'(?:CHAPTER|Chapter)\s+(\d+)[:\s]*\n*(.*?)(?:\n|$)',
        re.IGNORECASE
    )
    
    for page_data in pages:
        text = page_data["text"]
        page = page_data["page"]
        
        for match in chapter_pattern.finditer(text):
            ch_num = int(match.group(1))
            ch_title = match.group(2).strip()
            # Clean up title
            ch_title = re.sub(r'\s+', ' ', ch_title).strip()
            if ch_title:
                chapters.append({
                    "chapter": ch_num,
                    "title": ch_title,
                    "start_page": page
                })
    
    # Deduplicate (same chapter might appear in TOC and actual content)
    seen = set()
    unique = []
    for ch in chapters:
        key = ch["chapter"]
        if key not in seen:
            seen.add(key)
            unique.append(ch)
    
    return unique


def extract_recommendations(pages):
    """Extract policy recommendations from the report.
    Handles two formats:
    - Style A (India): RECOMMENDATION 1/2/3... with paragraph text
    - Style B (Saudi): Table with dimension, number, recommendation, timeline, priority
    """
    recommendations = []
    
    # --- Try Style B first: table-based (Saudi format) ---
    recommendations = _extract_table_recommendations(pages)
    if recommendations:
        return recommendations
    
    # --- Style A: paragraph-based (India format) ---
    return _extract_paragraph_recommendations(pages)


def _extract_table_recommendations(pages):
    """Extract recommendations from a table format (Saudi style).
    Pattern: dimension | number (X.Y) | recommendation text | timeline | priority
    """
    recommendations = []
    
    # Look for the recommendations table
    table_text = ""
    in_table = False
    
    for page_data in pages:
        text = page_data["text"]
        if re.search(r'List of recommendations|RECOMMENDATION.*TIMELINE.*PRIORITY', text, re.IGNORECASE):
            in_table = True
        if in_table:
            table_text += "\n" + text
            # Stop at references/endnotes
            if re.search(r'^\s*(?:References|Endnotes)\s*$', text, re.MULTILINE):
                break
    
    if not table_text:
        return []
    
    # Parse numbered recommendations (X.Y pattern)
    rec_pattern = re.compile(
        r'(\d+\.\d+)\s*\n(.*?)(?=\d+\.\d+\s*\n|References|Endnotes|$)',
        re.DOTALL
    )
    
    # Also try inline pattern
    inline_pattern = re.compile(
        r'(\d+\.\d+)\s+(.+?)(?:\s+(20\d{2}[-–]\d{4}|20\d{2}))\s+(High|Medium|Low)',
        re.IGNORECASE
    )
    
    # Try inline first (cleaner)
    matches = inline_pattern.findall(table_text)
    if matches:
        # Map dimension numbers to names
        dim_names = {
            "1": "Laws and Regulation",
            "2": "Institutional Frameworks and Governance",
            "3": "Capacity Building",
            "4": "Responsible Technologies and Innovation",
            "5": "Inclusion and Well-being",
            "6": "Investment Ecosystem"
        }
        
        for num, title, timeline, priority in matches:
            dim_num = num.split('.')[0]
            recommendations.append({
                "number": num,
                "title": title.strip(),
                "text": "",
                "dimension": dim_names.get(dim_num, f"Dimension {dim_num}"),
                "timeline": timeline.strip(),
                "priority": priority.strip(),
                "start_page": 0
            })
        return recommendations
    
    # Try multiline pattern
    lines = table_text.split('\n')
    current_dim = ""
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for dimension headers
        dim_match = re.match(r'^(Laws and|Institutional|Capacity|Responsible|Inclusion|Investment)', line, re.IGNORECASE)
        if dim_match:
            current_dim = line
            # May span multiple lines
            while i + 1 < len(lines) and not re.match(r'^\d+\.\d+', lines[i+1].strip()):
                i += 1
                next_line = lines[i].strip()
                if next_line and not re.match(r'^\d+', next_line):
                    current_dim += " " + next_line
        
        # Check for recommendation number
        num_match = re.match(r'^(\d+\.\d+)\s*$', line)
        if num_match:
            rec_num = num_match.group(1)
            # Next lines are the recommendation text, timeline, priority
            rec_text = ""
            timeline = ""
            priority = ""
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                # Check if it's timeline/priority
                time_match = re.match(r'(20\d{2}[-–]20\d{2}|20\d{2})\s+(High|Medium|Low)', next_line, re.IGNORECASE)
                if time_match:
                    timeline = time_match.group(1)
                    priority = time_match.group(2)
                    break
                # Check if next rec number
                if re.match(r'^\d+\.\d+\s*$', next_line):
                    break
                rec_text += " " + next_line
                i += 1
            
            dim_num = rec_num.split('.')[0]
            dim_names = {
                "1": "Laws and Regulation",
                "2": "Institutional Frameworks and Governance",
                "3": "Capacity Building",
                "4": "Responsible Technologies and Innovation",
                "5": "Inclusion and Well-being",
                "6": "Investment Ecosystem"
            }
            
            recommendations.append({
                "number": rec_num,
                "title": rec_text.strip(),
                "text": "",
                "dimension": current_dim or dim_names.get(dim_num, ""),
                "timeline": timeline,
                "priority": priority,
                "start_page": 0
            })
        
        i += 1
    
    return recommendations


def _extract_paragraph_recommendations(pages):
    """Extract recommendations from paragraph format (India style)."""
    recommendations = []
    in_recs = False
    current_rec = None
    rec_text_lines = []
    
    # Collect all text from recommendations chapter onwards
    all_rec_text = ""
    rec_start_page = 0
    in_recs = False
    page_breaks = {}  # char offset -> page number
    
    for page_data in pages:
        text = page_data["text"]
        page = page_data["page"]
        
        if re.search(r'(?:CHAPTER\s+\d+[:\s]*)?(?:Policy\s+)?[Rr]ecommendations', text):
            in_recs = True
            if not rec_start_page:
                rec_start_page = page
        
        if not in_recs:
            continue
        
        if re.search(r'^(?:Endnotes|ENDNOTES|References|REFERENCES)\s*$', text, re.MULTILINE):
            break
        
        page_breaks[len(all_rec_text)] = page
        all_rec_text += "\n" + text
    
    # Find all RECOMMENDATION N patterns (number may be on same or next line)
    rec_pattern = re.compile(r'RECOMMENDATION\s*\n?\s*(\d+)', re.IGNORECASE)
    matches = list(rec_pattern.finditer(all_rec_text))
    
    for idx, match in enumerate(matches):
        rec_num = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(all_rec_text)
        
        rec_content = all_rec_text[start:end].strip()
        
        # Try to extract title: look for the heading text BEFORE the RECOMMENDATION keyword
        # (In India format, title is on lines before "RECOMMENDATION\n1")
        pre_start = matches[idx - 1].end() if idx > 0 else 0
        pre_text = all_rec_text[pre_start:match.start()].strip()
        
        # Title is usually the last substantial line(s) before RECOMMENDATION
        title = ""
        pre_lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
        # Look backwards for title-like text (long enough, not a page number)
        for line in reversed(pre_lines):
            if len(line) > 20 and not re.match(r'^\d+$', line):
                title = line
                break
        
        # If no pre-title, take first substantial line from content
        if not title:
            for line in rec_content.split('\n'):
                clean = line.strip()
                if len(clean) > 20 and not clean[0].isdigit():
                    title = clean
                    break
        
        # Find page number
        page_num = rec_start_page
        for offset, pg in sorted(page_breaks.items()):
            if offset <= match.start():
                page_num = pg
        
        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_content[:2000],  # Cap text length
            "start_page": page_num
        })
    
    # Clean up titles
    for rec in recommendations:
        if not rec["title"] and rec.get("text"):
            for line in rec["text"].split('\n'):
                clean = line.strip()
                if len(clean) > 20 and not clean[0].isdigit():
                    rec["title"] = clean
                    break
    
    # Deduplicate: if same number appears multiple times, keep the one with most text
    seen = {}
    for rec in recommendations:
        key = rec["number"]
        if key not in seen or len(rec.get("text", "")) > len(seen[key].get("text", "")):
            seen[key] = rec
    recommendations = sorted(seen.values(), key=lambda r: (r["number"] if isinstance(r["number"], int) else int(str(r["number"]).replace(".", ""))))
    
    return recommendations


def extract_sub_recommendations(rec_text):
    """Extract sub-recommendations (action items) from recommendation text."""
    sub_recs = []
    
    # Look for bold-style headers or bullet patterns
    patterns = [
        # "Consider establishing..." style headers
        re.compile(r'^([A-Z][^.]+(?:may|should|could|to)[^.]+\.)', re.MULTILINE),
        # Numbered sub-items
        re.compile(r'^\s*(\d+\.\s+.+?)(?=\n\s*\d+\.|\n\n|$)', re.MULTILINE | re.DOTALL),
    ]
    
    for pattern in patterns:
        matches = pattern.findall(rec_text)
        if matches:
            sub_recs.extend([m.strip() for m in matches if len(m.strip()) > 30])
    
    return sub_recs[:20]  # Cap at 20


def extract_dimension_content(pages, dimension_name, start_page, end_page):
    """Extract content for a specific RAM dimension."""
    content = []
    for page_data in pages:
        if start_page <= page_data["page"] <= end_page:
            content.append(page_data["text"])
    return "\n\n".join(content)


def map_ram_dimensions(chapters):
    """Map chapters to standard RAM dimensions."""
    dimension_map = {
        2: "Legal and Regulatory",
        3: "Social and Cultural", 
        4: "Scientific and Educational",
        5: "Economic",
        6: "Technical and Infrastructural"
    }
    
    dimensions = {}
    for ch in chapters:
        if ch["chapter"] in dimension_map:
            dimensions[dimension_map[ch["chapter"]]] = {
                "chapter": ch["chapter"],
                "title": ch["title"],
                "start_page": ch["start_page"]
            }
    
    return dimensions


def extract_executive_summary(pages):
    """Extract the executive summary text."""
    summary_lines = []
    in_summary = False
    
    for page_data in pages:
        text = page_data["text"]
        
        if re.search(r'Executive\s+summary', text, re.IGNORECASE):
            in_summary = True
        
        if in_summary:
            # Stop at Chapter 1
            if re.search(r'CHAPTER\s+1', text) and page_data["page"] > 5:
                break
            summary_lines.append(text)
    
    return "\n\n".join(summary_lines).strip()


def extract_metadata(doc, pages):
    """Extract report metadata."""
    metadata = {
        "page_count": doc.page_count,
        "creation_date": None,
        "modification_date": None,
    }
    
    # From PDF metadata
    pdf_meta = doc.metadata
    if pdf_meta:
        metadata["creation_date"] = pdf_meta.get("creationDate", "")
        metadata["modification_date"] = pdf_meta.get("modDate", "")
    
    # Try to find country name from first pages
    for page_data in pages[:10]:
        text = page_data["text"]
        # Look for country name in large text (title pages)
        country_match = re.search(
            r'^([A-Z]{2,}(?:\s+[A-Z]+)*)\s*$',
            text, re.MULTILINE
        )
        if country_match:
            candidate = country_match.group(1).strip()
            # Filter out common non-country words
            if candidate not in ["ACKNOWLEDGEMENTS", "UNESCO", "FOREWORD", "CHAPTER", 
                                  "EXECUTIVE", "SUMMARY", "RECOMMENDATION", "TABLE"]:
                metadata["country_name"] = candidate
                break
    
    return metadata


def generate_full_text_md(country_code, metadata, pages, chapters, recommendations):
    """Generate a full-text markdown file for RAG/search."""
    lines = []
    lines.append(f"# UNESCO RAM Report: {metadata.get('country_name', country_code)}")
    lines.append(f"\nPages: {metadata['page_count']}")
    lines.append(f"Country Code: {country_code}")
    lines.append("")
    
    # Chapters
    lines.append("## Structure")
    for ch in chapters:
        lines.append(f"- Chapter {ch['chapter']}: {ch['title']} (p.{ch['start_page']})")
    lines.append("")
    
    # Recommendations summary
    lines.append("## Recommendations")
    for rec in recommendations:
        lines.append(f"\n### Recommendation {rec['number']}: {rec['title']}")
        # First 500 chars of text
        preview = rec['text'][:500].strip()
        if preview:
            lines.append(preview)
    lines.append("")
    
    # Full text by page
    lines.append("\n---\n## Full Text\n")
    for page_data in pages:
        lines.append(f"\n### Page {page_data['page']}\n")
        lines.append(page_data["text"])
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_ram_pdf.py <pdf_path> <country_code> [--output-dir <dir>]")
        print("Example: python extract_ram_pdf.py report.pdf SA --output-dir ./extracted")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    country_code = sys.argv[2].upper()
    
    output_dir = "."
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        output_dir = sys.argv[idx + 1]
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📄 Opening: {pdf_path}")
    doc = fitz.open(pdf_path)
    print(f"   Pages: {doc.page_count}")
    
    # Extract
    print("📝 Extracting text...")
    pages = extract_full_text(doc)
    
    print("🔍 Detecting metadata...")
    metadata = extract_metadata(doc, pages)
    print(f"   Country: {metadata.get('country_name', 'Unknown')}")
    
    print("📑 Detecting chapters...")
    chapters = detect_chapters(pages)
    for ch in chapters:
        print(f"   Ch.{ch['chapter']}: {ch['title']} (p.{ch['start_page']})")
    
    print("🗺️  Mapping RAM dimensions...")
    dimensions = map_ram_dimensions(chapters)
    for dim_name, dim_info in dimensions.items():
        print(f"   ✓ {dim_name} (Ch.{dim_info['chapter']}, p.{dim_info['start_page']})")
    
    print("📋 Extracting recommendations...")
    recommendations = extract_recommendations(pages)
    print(f"   Found {len(recommendations)} recommendations")
    for rec in recommendations:
        title_preview = rec['title'][:80] if rec['title'] else '(untitled)'
        print(f"   #{rec['number']}: {title_preview}")
    
    print("📝 Extracting executive summary...")
    exec_summary = extract_executive_summary(pages)
    print(f"   Length: {len(exec_summary)} chars")
    
    # Build output JSON
    output = {
        "country_code": country_code,
        "country_name": metadata.get("country_name", country_code),
        "metadata": metadata,
        "chapters": chapters,
        "dimensions": dimensions,
        "executive_summary": exec_summary[:2000],  # Cap for JSON size
        "recommendations": recommendations,
        "recommendation_count": len(recommendations),
        "page_count": doc.page_count,
    }
    
    # Write JSON
    json_path = os.path.join(output_dir, f"{country_code.lower()}_extracted.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON: {json_path}")
    
    # Write full text MD
    md_path = os.path.join(output_dir, f"{country_code.lower()}_full_text.md")
    md_content = generate_full_text_md(country_code, metadata, pages, chapters, recommendations)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✅ Full text: {md_path} ({len(md_content)} chars)")
    
    print(f"\n🎯 Done! {country_code} report extracted successfully.")
    return output


if __name__ == "__main__":
    main()
