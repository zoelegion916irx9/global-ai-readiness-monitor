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


def get_full_text(pages):
    """Concatenate all page text into one string."""
    return "\n\n".join(p["text"] for p in pages)


def detect_language(pages):
    """Detect report language from content."""
    sample = get_full_text(pages[:20]).lower()
    
    fr_markers = ["recommandation", "chapitre", "résumé", "éthique", "intelligence artificielle",
                  "gouvernance", "l'unesco", "stratégie", "développement"]
    pt_markers = ["recomendação", "recomendações", "inteligência artificial", "estratégia",
                  "governação", "capacitação", "regulamentação", "relatório"]
    
    fr_count = sum(1 for m in fr_markers if m in sample)
    pt_count = sum(1 for m in pt_markers if m in sample)
    
    if fr_count >= 3:
        return "fr"
    if pt_count >= 3:
        return "pt"
    return "en"


def detect_chapters(pages):
    """Detect chapter boundaries and titles."""
    chapters = []
    # Support English, French, Portuguese chapter headers
    chapter_pattern = re.compile(
        r'(?:CHAPTER|Chapter|Chapitre|CHAPITRE|Capítulo|CAPÍTULO)\s+(\d+)[:\s]*\n*(.*?)(?:\n|$)',
        re.IGNORECASE
    )
    
    for page_data in pages:
        text = page_data["text"]
        page = page_data["page"]
        
        for match in chapter_pattern.finditer(text):
            ch_num = int(match.group(1))
            ch_title = match.group(2).strip()
            ch_title = re.sub(r'\s+', ' ', ch_title).strip()
            if ch_title:
                chapters.append({
                    "chapter": ch_num,
                    "title": ch_title,
                    "start_page": page
                })
    
    seen = set()
    unique = []
    for ch in chapters:
        key = ch["chapter"]
        if key not in seen:
            seen.add(key)
            unique.append(ch)
    
    return unique


def extract_recommendations(pages):
    """Extract policy recommendations using all known formats.
    Tries all extractors and returns the one with the most results.
    """
    all_results = []
    
    # Try each extractor
    extractors = [
        ("table_sa", _extract_table_recommendations),
        ("paragraph_in", _extract_paragraph_recommendations),
        ("numbered_policy", _extract_numbered_policy_recommendations),
        ("dimension_numbered", _extract_dimension_numbered_recommendations),
        ("french_numbered", _extract_french_numbered_recommendations),
        ("portuguese_numbered", _extract_portuguese_numbered_recommendations),
        ("table_bw", _extract_table_bw_recommendations),
        ("dimension_prose", _extract_dimension_prose_recommendations),
        ("bullet_dimension", _extract_bullet_dimension_recommendations),
        ("dimension_tab_numbered", _extract_dimension_tab_numbered_recommendations),
        ("xy_hierarchical", _extract_xy_hierarchical_recommendations),
        ("spanish_recomendaciones", _extract_spanish_recomendaciones),
        ("french_dash_bullets", _extract_french_dash_bullet_recommendations),
        ("nl_prose_recs", _extract_nl_prose_recommendations),
        ("titled_prose_recs", _extract_titled_prose_recommendations),
    ]
    
    for name, extractor in extractors:
        try:
            recs = extractor(pages)
            if recs:
                all_results.append((name, recs))
        except Exception as e:
            print(f"   ⚠ Extractor {name} failed: {e}")
    
    if not all_results:
        return []
    
    # Pick the extractor that found the most recommendations
    best_name, best_recs = max(all_results, key=lambda x: len(x[1]))
    print(f"   Using extractor: {best_name} ({len(best_recs)} recs)")
    return best_recs


def _extract_table_recommendations(pages):
    """Extract recommendations from a table format (Saudi style).
    Pattern: dimension | number (X.Y) | recommendation text | timeline | priority
    """
    recommendations = []
    
    table_text = ""
    in_table = False
    
    for page_data in pages:
        text = page_data["text"]
        if re.search(r'List of recommendations|RECOMMENDATION.*TIMELINE.*PRIORITY', text, re.IGNORECASE):
            in_table = True
        if in_table:
            table_text += "\n" + text
            if re.search(r'^\s*(?:References|Endnotes)\s*$', text, re.MULTILINE):
                break
    
    if not table_text:
        return []
    
    dim_names = {
        "1": "Laws and Regulation",
        "2": "Institutional Frameworks and Governance",
        "3": "Capacity Building",
        "4": "Responsible Technologies and Innovation",
        "5": "Inclusion and Well-being",
        "6": "Investment Ecosystem"
    }
    
    num_positions = list(re.finditer(r'(?:^|\n)\s*(\d+\.\d+)\s', table_text))
    
    for idx, match in enumerate(num_positions):
        rec_num = match.group(1)
        start = match.end()
        end = num_positions[idx + 1].start() if idx + 1 < len(num_positions) else len(table_text)
        
        segment = table_text[start:end].strip()
        
        tp_match = re.search(r'(20\d{2}[-–]20\d{2}|20\d{2})\s+(High|Medium|Low)', segment, re.IGNORECASE)
        timeline = ""
        priority = ""
        rec_title = segment
        
        if tp_match:
            timeline = tp_match.group(1)
            priority = tp_match.group(2)
            rec_title = segment[:tp_match.start()].strip()
        
        rec_title = re.sub(r'\s+', ' ', rec_title).strip()
        
        dim_num = rec_num.split('.')[0]
        
        recommendations.append({
            "number": rec_num,
            "title": rec_title,
            "text": "",
            "dimension": dim_names.get(dim_num, f"Dimension {dim_num}"),
            "timeline": timeline,
            "priority": priority,
            "start_page": 0
        })
    
    return recommendations


def _extract_paragraph_recommendations(pages):
    """Extract recommendations from paragraph format (India style).
    Pattern: RECOMMENDATION 1, RECOMMENDATION 2, etc.
    """
    recommendations = []
    in_recs = False
    all_rec_text = ""
    rec_start_page = 0
    page_breaks = {}
    
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
    
    rec_pattern = re.compile(r'RECOMMENDATION\s*\n?\s*(\d+)', re.IGNORECASE)
    matches = list(rec_pattern.finditer(all_rec_text))
    
    if not matches:
        return []
    
    for idx, match in enumerate(matches):
        rec_num = int(match.group(1))
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(all_rec_text)
        
        rec_content = all_rec_text[start:end].strip()
        
        pre_start = matches[idx - 1].end() if idx > 0 else 0
        pre_text = all_rec_text[pre_start:match.start()].strip()
        
        title = ""
        pre_lines = [l.strip() for l in pre_text.split('\n') if l.strip()]
        for line in reversed(pre_lines):
            if len(line) > 20 and not re.match(r'^\d+$', line):
                title = line
                break
        
        if not title:
            for line in rec_content.split('\n'):
                clean = line.strip()
                if len(clean) > 20 and not clean[0].isdigit():
                    title = clean
                    break
        
        page_num = rec_start_page
        for offset, pg in sorted(page_breaks.items()):
            if offset <= match.start():
                page_num = pg
        
        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_content[:2000],
            "start_page": page_num
        })
    
    for rec in recommendations:
        if not rec["title"] and rec.get("text"):
            for line in rec["text"].split('\n'):
                clean = line.strip()
                if len(clean) > 20 and not clean[0].isdigit():
                    rec["title"] = clean
                    break
    
    seen = {}
    for rec in recommendations:
        key = rec["number"]
        if key not in seen or len(rec.get("text", "")) > len(seen[key].get("text", "")):
            seen[key] = rec
    recommendations = sorted(seen.values(), key=lambda r: r["number"])
    
    return recommendations


def _extract_numbered_policy_recommendations(pages):
    """Extract numbered policy recommendations (Kenya, South Africa, Indonesia, Mozambique, Namibia style).
    Pattern: 'POLICY RECOMMENDATIONS' section followed by numbered items 1. 2. 3. etc.
    Sometimes with subsection headers (Al Governance, Capacity-Building, etc.)
    """
    full_text = get_full_text(pages)
    
    # Find the POLICY RECOMMENDATIONS section (use last occurrence, not TOC)
    section_matches = list(re.finditer(
        r'(?:POLICY\s+RECOMMENDATIONS(?:\s+AND\s+ROADMAPS?\s+FOR\s+ACTION)?|Policy\s+Recommendations|KEY\s+RECOMMENDATIONS\s+(?:OF\s+THIS\s+REPORT|FOR\s+STRENGTHENING)|Key\s+recommendations\s+for\s+(?:the\s+findings|strengthening))\s*\n',
        full_text, re.IGNORECASE
    ))
    if not section_matches:
        return []
    
    section_match = section_matches[-1]
    section_start = section_match.end()
    end_match = re.search(
        r'\n\s*(?:REFERENCES|References|ENDNOTES|Endnotes|ANNEXE|Annex|BIBLIOGRAPHY)\s*\n',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else len(full_text)
    section_text = full_text[section_start:section_end]
    
    recommendations = []
    current_dimension = ""
    
    # Split by numbered items: "1." or "1. " at start of line
    # Handle both "1. \n" and "1. \nText" patterns
    rec_pattern = re.compile(r'(?:^|\n)\s*(\d+)\.\s*\n?(.*?)(?=\n\s*\d+\.\s|\Z)', re.DOTALL)
    
    # Also detect dimension headers (all caps or title case lines before numbered items)
    lines = section_text.split('\n')
    rebuilt_text = ""
    for line in lines:
        stripped = line.strip()
        # Detect dimension headers (lines that are dimension-like headings)
        if stripped and not re.match(r'^\d+\.', stripped):
            # Check if this looks like a section header
            if (stripped.isupper() or re.match(r'^[A-Z][a-z]+(?:\s+[A-Za-z]+)*$', stripped)) and len(stripped) < 100:
                if not re.match(r'^[•■\-]', stripped) and len(stripped) > 5:
                    # Could be a dimension header
                    pass
        rebuilt_text += line + "\n"
    
    # Extract dimension headers and numbered items
    dim_pattern = re.compile(
        r'(?:^|\n)\s*([A-Z][A-Za-z,\s&\-]+(?:and\s+[A-Za-z\-]+)?)\s*\n\s*(?=\d+\.\s)',
        re.MULTILINE
    )
    dim_matches = {m.start(): m.group(1).strip() for m in dim_pattern.finditer(section_text)}
    
    for match in rec_pattern.finditer(section_text):
        rec_num = int(match.group(1))
        rec_text = match.group(2).strip()
        
        # Check if there's a dimension header before this recommendation
        match_pos = match.start()
        for pos in sorted(dim_matches.keys()):
            if pos < match_pos:
                candidate = dim_matches[pos]
                # Filter out OCR garbage
                if len(candidate) > 3 and len(candidate) < 80:
                    current_dimension = candidate
        
        # Clean up text
        rec_text = re.sub(r'\s+', ' ', rec_text).strip()
        
        # Title is first sentence or first ~150 chars
        title = rec_text[:200]
        period_pos = title.find('.')
        if period_pos > 20:
            title = title[:period_pos + 1]
        elif len(title) > 150:
            # Cut at last space before 150
            title = title[:150].rsplit(' ', 1)[0] + "..."
        
        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_text[:2000],
            "dimension": current_dimension,
            "start_page": 0
        })
    
    return recommendations


def _extract_dimension_numbered_recommendations(pages):
    """Extract recommendations grouped by dimension with X.Y numbering (Thailand, Egypt style).
    Pattern: 
    - Thailand: HIGH LEVEL RECOMMENDATIONS -> 1. LAW AND REGULATION -> 1.1, 1.2, etc.
    - Egypt: MAIN POLICY RECOMMENDATIONS -> REGULATION -> .1, .2 etc.
    """
    full_text = get_full_text(pages)
    
    # Find the recommendations section (use the LAST occurrence, not the TOC one)
    section_matches = list(re.finditer(
        r'(?:HIGH\s+LEVEL\s+RECOMMENDATIONS|MAIN\s+POLICY\s+RECOMMENDATIONS)\s*\n',
        full_text, re.IGNORECASE
    ))
    if not section_matches:
        return []
    
    # Use last occurrence (the actual content, not TOC)
    section_match = section_matches[-1]
    section_start = section_match.end()
    
    # Find end - look for summary table, government response, references, etc.
    end_match = re.search(
        r'\n\s*(?:REFERENCES|References|ENDNOTES|GOVERNMENT\s+RESPONSE|Government\s+Response|ANNEXE|Annex|'
        r'Table\s+\d+\s+provides?\s+a\s+summary)\s',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 30000, len(full_text))
    section_text = full_text[section_start:section_end]
    
    recommendations = []
    current_dimension = ""
    
    # Detect dimension headers (numbered: "1. LAW AND REGULATION" or caps: "REGULATION")
    dim_pattern = re.compile(
        r'(?:^|\n)\s*(?:\d+\.\s+)?([A-Z][A-Z\s,&]+(?:AND\s+[A-Z\s]+)?)\s*\n',
        re.MULTILINE
    )
    
    # Try X.Y pattern first (Thailand: 1.1, 1.2, 2.1, etc.)
    xy_pattern = re.compile(
        r'(?:^|\n)\s*(\d+\.\d+)\s+(.+?)(?=\n\s*\d+\.\d+\s|\n\s*\d+\.\s+[A-Z]|\Z)',
        re.DOTALL
    )
    xy_matches = list(xy_pattern.finditer(section_text))
    
    if xy_matches:
        # Build dimension map
        dim_matches = list(dim_pattern.finditer(section_text))
        dim_map = []
        for m in dim_matches:
            name = m.group(1).strip()
            if len(name) > 5 and name not in ("HIGH LEVEL RECOMMENDATIONS", "MAIN POLICY RECOMMENDATIONS"):
                dim_map.append((m.start(), name))
        
        for match in xy_matches:
            rec_num = match.group(1)
            rec_text = match.group(2).strip()
            
            # Find dimension
            for pos, name in reversed(dim_map):
                if pos < match.start():
                    current_dimension = name.title()
                    break
            
            # Extract title (first line or up to "Timeline:")
            lines = rec_text.split('\n')
            title = lines[0].strip() if lines else rec_text[:150]
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Extract timeline and priority if present
            timeline = ""
            priority = ""
            tp = re.search(r'Timeline:\s*(20\d{2}[-–]20\d{2}|20\d{2})', rec_text, re.IGNORECASE)
            if tp:
                timeline = tp.group(1)
            pr = re.search(r'Priority:\s*(High|Medium|Low)', rec_text, re.IGNORECASE)
            if pr:
                priority = pr.group(1)
            
            rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
            
            recommendations.append({
                "number": rec_num,
                "title": title[:200],
                "text": rec_text_clean[:2000],
                "dimension": current_dimension,
                "timeline": timeline,
                "priority": priority,
                "start_page": 0
            })
        return recommendations
    
    # Try Egypt style: .\t1, .\t2 or just numbered .1 .2 under dimension headers
    egypt_pattern = re.compile(
        r'(?:^|\n)\s*\.?\s*(\d+)\s*\n(.+?)(?=\n\s*\.?\s*\d+\s*\n|\n\s*(?:REGULATION|INSTITUTIONAL|CAPACITY|INVESTMENT|INCLUSION)\b|\Z)',
        re.DOTALL
    )
    egypt_matches = list(egypt_pattern.finditer(section_text))
    
    if egypt_matches and len(egypt_matches) >= 5:
        dim_matches = list(dim_pattern.finditer(section_text))
        dim_map = []
        for m in dim_matches:
            name = m.group(1).strip()
            if len(name) > 5:
                dim_map.append((m.start(), name))
        
        for match in egypt_matches:
            rec_num = int(match.group(1))
            rec_text = match.group(2).strip()
            rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
            
            for pos, name in reversed(dim_map):
                if pos < match.start():
                    current_dimension = name.title()
                    break
            
            title = rec_text_clean[:200]
            period_pos = title.find('.')
            if period_pos > 20:
                title = title[:period_pos + 1]
            
            recommendations.append({
                "number": rec_num,
                "title": title,
                "text": rec_text_clean[:2000],
                "dimension": current_dimension,
                "start_page": 0
            })
        return recommendations
    
    return []


def _extract_french_numbered_recommendations(pages):
    """Extract French-language recommendations (Morocco, Chad, Gabon style).
    Patterns:
    - Morocco: 'Recommandation 1 :', 'Recommandation 2 :', etc.
    - Chad: Table with numbered recommendations under 'Recommandations'
    - Gabon: Numbered list under recommendation sections
    """
    full_text = get_full_text(pages)
    recommendations = []
    
    # Pattern 1: Morocco style - "Recommandation N : title"
    rec_pattern = re.compile(
        r'Recommandation\s+(\d+)\s*:\s*(.+?)(?=Recommandation\s+\d+\s*:|Tableau\s+\d+|$)',
        re.DOTALL | re.IGNORECASE
    )
    matches = list(rec_pattern.finditer(full_text))
    
    if matches and len(matches) >= 3:
        for match in matches:
            rec_num = int(match.group(1))
            rec_text = match.group(2).strip()
            
            # Title is first line/sentence
            lines = rec_text.split('\n')
            title = lines[0].strip() if lines else rec_text[:200]
            title = re.sub(r'\s+', ' ', title).strip()
            
            rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
            
            recommendations.append({
                "number": rec_num,
                "title": title[:300],
                "text": rec_text_clean[:2000],
                "language": "fr",
                "start_page": 0
            })
        return recommendations
    
    # Pattern 2: Chad/Gabon style - table with numbered recommendations
    # Find the recommendations section
    section_match = re.search(
        r'(?:Principales\s+recommandations|Champs\s+d\'action\s+et\s+recommandations|recommandations\s+sont\s+formul)',
        full_text, re.IGNORECASE
    )
    if section_match:
        section_start = section_match.start()
        # Look for numbered recommendations after this
        section_text = full_text[section_start:section_start + 15000]
        
        # Try numbered pattern
        num_pattern = re.compile(
            r'(?:^|\n)\s*(\d+)\.\s*(.+?)(?=\n\s*\d+\.\s|\n\s*(?:À\s+court|À\s+moyen|À\s+long|SITOGRAPHIE|Références|Annexe)|\Z)',
            re.DOTALL
        )
        num_matches = list(num_pattern.finditer(section_text))
        
        if num_matches:
            for match in num_matches:
                rec_num = int(match.group(1))
                rec_text = match.group(2).strip()
                rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
                
                title = rec_text_clean[:200]
                period_pos = title.find('.')
                if 20 < period_pos < 180:
                    title = title[:period_pos + 1]
                
                recommendations.append({
                    "number": rec_num,
                    "title": title,
                    "text": rec_text_clean[:2000],
                    "language": "fr",
                    "start_page": 0
                })
            
            if recommendations:
                return recommendations
    
    # Pattern 3: Recommendations in table (Chad style with Recommandations column)
    table_match = re.search(r'Recommandations\s*\n\s*Phase', full_text, re.IGNORECASE)
    if table_match:
        table_start = table_match.start()
        table_text = full_text[table_start:table_start + 10000]
        
        # Extract numbered items from table
        num_pattern = re.compile(
            r'(\d+)\.\s+(.+?)(?=\n\s*\d+\.\s|\n\s*(?:Court|Moyen|Long)\s+terme|\Z)',
            re.DOTALL
        )
        for match in num_pattern.finditer(table_text):
            rec_num = int(match.group(1))
            rec_text = match.group(2).strip()
            rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
            
            # Clean out phase/timeline markers
            rec_text_clean = re.sub(r'\s*(?:Court|Moyen|Long)\s+terme\s*', '', rec_text_clean)
            
            recommendations.append({
                "number": rec_num,
                "title": rec_text_clean[:200],
                "text": rec_text_clean[:2000],
                "language": "fr",
                "start_page": 0
            })
    
    return recommendations


def _extract_portuguese_numbered_recommendations(pages):
    """Extract Portuguese-language recommendations (São Tomé style).
    Pattern: RECOMENDAÇÕES POLÍTICAS section with numbered items.
    """
    full_text = get_full_text(pages)
    
    # Find the recommendations section
    section_match = re.search(
        r'(?:RECOMENDAÇÕES\s+POLÍTICAS|ROTEIRO\s+COM\s+PRINCIPAIS\s+RECOMENDAÇÕES|PRINCIPAIS\s+RECOMENDAÇÕES)',
        full_text, re.IGNORECASE
    )
    if not section_match:
        return []
    
    section_start = section_match.end()
    
    # Find end
    end_match = re.search(
        r'\n\s*(?:Referências|REFERÊNCIAS|Figura\s+\d|Tabela\s+\d|ROTEIRO\s+DAS\s+PRINCIPAIS)',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 15000, len(full_text))
    section_text = full_text[section_start:section_end]
    
    recommendations = []
    current_dimension = ""
    
    # Detect dimension headers (all caps Portuguese)
    dim_keywords = [
        "REGULAMENTAÇÃO", "QUADRO INSTITUCIONAL", "CAPACITAÇÃO", "SENSIBILIZAÇÃO",
        "ESTRATÉGIA NACIONAL", "REGULAMENTAÇÃO E QUADRO"
    ]
    
    # Extract numbered items
    num_pattern = re.compile(
        r'(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.\s|\n\s*(?:REGULAMENTAÇÃO|CAPACITAÇÃO|ESTRATÉGIA|Instituições|Prazo)|\Z)',
        re.DOTALL
    )
    
    for match in num_pattern.finditer(section_text):
        rec_num = int(match.group(1))
        rec_text = match.group(2).strip()
        
        # Check for dimension header before this rec
        pre_text = section_text[:match.start()]
        for kw in dim_keywords:
            if kw in pre_text.upper():
                last_pos = pre_text.upper().rfind(kw)
                if last_pos >= 0:
                    # Get the full line
                    line_start = pre_text.rfind('\n', 0, last_pos) + 1
                    line_end = pre_text.find('\n', last_pos)
                    if line_end < 0:
                        line_end = len(pre_text)
                    current_dimension = pre_text[line_start:line_end].strip()
        
        rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
        
        title = rec_text_clean[:200]
        period_pos = title.find('.')
        if 20 < period_pos < 180:
            title = title[:period_pos + 1]
        
        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_text_clean[:2000],
            "dimension": current_dimension,
            "language": "pt",
            "start_page": 0
        })
    
    return recommendations


def _extract_table_bw_recommendations(pages):
    """Extract recommendations from Botswana-style table.
    Pattern: Dimension | No | Recommendations | Timeframe | Priority
    """
    full_text = get_full_text(pages)
    
    # Find the table
    table_match = re.search(
        r'(?:Table\s+\d+[:\.]?\s*Policy\s+recommendation|Dimension\s+No\s+Recommendations?\s+Timeframe\s+Priority)',
        full_text, re.IGNORECASE
    )
    if not table_match:
        return []
    
    table_start = table_match.end()
    # Find end of table (Conclusion, References, etc.)
    end_match = re.search(
        r'\n\s*(?:Conclusion|CONCLUSION|References|REFERENCES)\s',
        full_text[table_start:]
    )
    table_end = table_start + end_match.start() if end_match else min(table_start + 5000, len(full_text))
    table_text = full_text[table_start:table_end]
    
    recommendations = []
    current_dimension = ""
    
    # The table has dimension names, numbers, recommendation text, timeframe, priority
    # Parse line by line looking for numbered entries
    lines = table_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check for dimension header
        dim_match = re.match(r'^(Regulation|Institutional\s+Framework|Capacity\s+Building|Technology|Investment|Inclusion)', line, re.IGNORECASE)
        if dim_match:
            current_dimension = dim_match.group(1).strip()
        
        # Check for numbered recommendation
        num_match = re.match(r'^(\d+)\s*$', line)
        if num_match:
            rec_num = int(num_match.group(1))
            # Next line(s) should be the recommendation text
            rec_text = ""
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                # Check if this is a timeframe line
                if re.match(r'^\d+[-–]\d+\s+months', next_line, re.IGNORECASE):
                    timeframe = next_line.split()[0] + " months"
                    break
                # Check if this is a priority
                if next_line in ("High", "Medium", "Low"):
                    break
                # Check if this is next number
                if re.match(r'^\d+$', next_line) and int(next_line) == rec_num + 1:
                    break
                rec_text += " " + next_line
                i += 1
            
            rec_text = rec_text.strip()
            if rec_text:
                # Try to extract timeframe and priority
                timeframe = ""
                priority = ""
                tf_match = re.search(r'(\d+[-–]\s*\d+\s*months)', rec_text, re.IGNORECASE)
                if tf_match:
                    timeframe = tf_match.group(1)
                pr_match = re.search(r'\b(High|Medium|Low)\b', rec_text, re.IGNORECASE)
                if pr_match:
                    priority = pr_match.group(1)
                
                recommendations.append({
                    "number": rec_num,
                    "title": rec_text[:200],
                    "text": rec_text[:2000],
                    "dimension": current_dimension,
                    "timeline": timeframe,
                    "priority": priority,
                    "start_page": 0
                })
        i += 1
    
    # If table parsing didn't work well, try a different approach
    if not recommendations:
        # Look for pattern: number followed by text followed by timeframe
        rec_pattern = re.compile(
            r'(\d+)\n(.+?)\n(\d+[-–]\d+\s+months)\n(High|Medium|Low)',
            re.DOTALL | re.IGNORECASE
        )
        for match in rec_pattern.finditer(table_text):
            rec_num = int(match.group(1))
            rec_text = re.sub(r'\s+', ' ', match.group(2)).strip()
            timeframe = match.group(3)
            priority = match.group(4)
            
            recommendations.append({
                "number": rec_num,
                "title": rec_text[:200],
                "text": rec_text[:2000],
                "dimension": "",
                "timeline": timeframe,
                "priority": priority,
                "start_page": 0
            })
    
    return recommendations


def _extract_dimension_prose_recommendations(pages):
    """Extract recommendations from dimension-specific prose sections (Zimbabwe style).
    Pattern: Dimension headers followed by paragraph-style recommendations.
    """
    full_text = get_full_text(pages)
    
    # Find the recommendations section
    section_match = re.search(
        r'(?:dimension-specific\s+recommendations|following\s+dimension-specific|we\s+make\s+the\s+following.*?recommendations)',
        full_text, re.IGNORECASE
    )
    if not section_match:
        return []
    
    section_start = section_match.end()
    
    # Find end
    end_match = re.search(
        r'\n\s*(?:REFERENCES|References|ENDNOTES|ANNEXE|Annex)\s*\n',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 30000, len(full_text))
    section_text = full_text[section_start:section_end]
    
    # Look for bold/header-style recommendation topics
    # Zimbabwe uses descriptive headers like "Ethics and AI governance framework", "Open data directive", etc.
    # These are typically followed by detailed text
    
    # Pattern: Line that looks like a title (not too long, starts with capital, not a bullet)
    # followed by paragraph text
    recommendations = []
    current_dimension = ""
    
    # Detect dimension headers: "Laws and regulations", "Institutional Framework", etc.
    dim_pattern = re.compile(
        r'(?:^|\n)((?:Laws?\s+and\s+[Rr]egulation|Institutional\s+[Ff]ramework|Capacity\s+[Bb]uilding|'
        r'Inclusion|Investment|Technology|National\s+AI\s+Strategy)[^\n]*)\s*\n',
        re.MULTILINE
    )
    
    # Find topic headers: lines between 20-120 chars, title case, followed by paragraph
    topic_pattern = re.compile(
        r'(?:^|\n)([A-Z][A-Za-z\s,\-&\']+(?:framework|directive|strategy|governance|infrastructure|'
        r'literacy|training|investment|policy|development|protection|assessment|cooperation|'
        r'inclusion|innovation|standards|research|education|skills|data|AI|digital)[^\n]{0,50})\s*\n'
        r'(.+?)(?=\n[A-Z][A-Za-z\s,\-&\']*(?:framework|directive|strategy|governance|infrastructure|'
        r'literacy|training|investment|policy|development|protection|assessment|cooperation|'
        r'inclusion|innovation|standards|research|education|skills|data|AI|digital)|\Z)',
        re.DOTALL | re.IGNORECASE
    )
    
    matches = list(topic_pattern.finditer(section_text))
    
    if not matches:
        # Fallback: just extract dimension-based chunks
        dim_matches = list(dim_pattern.finditer(section_text))
        for idx, match in enumerate(dim_matches):
            dim_name = match.group(1).strip()
            start = match.end()
            end = dim_matches[idx + 1].start() if idx + 1 < len(dim_matches) else len(section_text)
            text = section_text[start:end].strip()
            text_clean = re.sub(r'\s+', ' ', text).strip()
            
            if len(text_clean) > 50:
                recommendations.append({
                    "number": idx + 1,
                    "title": dim_name,
                    "text": text_clean[:2000],
                    "dimension": dim_name,
                    "start_page": 0
                })
        return recommendations
    
    for idx, match in enumerate(matches):
        title = match.group(1).strip()
        text = match.group(2).strip()
        text_clean = re.sub(r'\s+', ' ', text).strip()
        
        # Find dimension
        for dm in dim_pattern.finditer(section_text):
            if dm.start() < match.start():
                current_dimension = dm.group(1).strip()
        
        # Extract timeline if present
        timeline = ""
        tl_match = re.search(r'Timeline:\s*(20\d{2}(?:[-–]20\d{2})?)', text, re.IGNORECASE)
        if tl_match:
            timeline = tl_match.group(1)
        
        recommendations.append({
            "number": idx + 1,
            "title": title,
            "text": text_clean[:2000],
            "dimension": current_dimension,
            "timeline": timeline,
            "start_page": 0
        })
    
    return recommendations


def _extract_bullet_dimension_recommendations(pages):
    """Extract bullet-point recommendations under dimension headers (Mozambique, Namibia style).
    Pattern: RECOMMENDATIONS section -> dimension headers (REGULATION, CAPACITY BUILDING, etc.)
    -> bullet points (», •, -) with bold-style titles
    """
    full_text = get_full_text(pages)
    
    # Find the recommendations section (multiple possible headers)
    section_matches = list(re.finditer(
        r'(?:ROADMAP\s+WITH\s+MAIN\s+POLICY\s+RECOMMENDATIONS|'
        r'The\s+following\s+recommendations\s+are\s+proposed[^\n]*|'
        r'key\s+recommendations\s+have\s+been\s+identified[^\n]*|'
        r'Overall\s+recommendations|'
        r'KEY\s+RECOMMENDATIONS(?:\s+OF\s+THIS\s+REPORT)?|'
        r'POLICY\s+RECOMMENDATIONS(?:\s+AND\s+ROADMAPS?\s+FOR\s+ACTION)?)\s*\n',
        full_text, re.IGNORECASE
    ))
    if not section_matches:
        return []
    
    # Use the last "major" section header, but prefer "the following recommendations" 
    # (inline marker) over sub-headers like "Overall recommendations" if available
    # For "ROADMAP" and "POLICY RECOMMENDATIONS" - use last occurrence (skip TOC)
    best_match = section_matches[-1]
    # Check if there's a "following" match - it's usually the best starting point
    following_matches = [m for m in section_matches if 'following' in m.group(0).lower() or 'identified' in m.group(0).lower()]
    if following_matches:
        best_match = following_matches[-1]
    else:
        # Use last occurrence of major headers (skip TOC entries which are early)
        major = [m for m in section_matches if any(k in m.group(0).lower() for k in ['roadmap', 'policy recommendations', 'key recommendations'])]
        if major:
            best_match = major[-1]
    section_match = best_match
    section_start = section_match.end()
    
    # Find end
    end_match = re.search(
        r'\n\s*(?:Conclusion|CONCLUSION|References|REFERENCES|ENDNOTES|ANNEXE|Annex)\s*\n',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 20000, len(full_text))
    section_text = full_text[section_start:section_end]
    
    recommendations = []
    current_dimension = ""
    rec_num = 0
    
    # Detect dimension headers
    dim_pattern = re.compile(
        r'(?:^|\n)\s*(REGULATIONS?|INSTITUTIONAL\s+FRAMEWORKS?|CAPACITY\s+(?:BUILDING|AND\s+TRAINING)|'
        r'Capacity\s+(?:building|and\s+training)|Regulations?|Investment|Technology|Inclusion|'
        r'Legal\s+and\s+regulatory|Social\s+and\s+cultural|Scientific\s+and\s+educational|'
        r'Economic|Technical\s+and\s+infrastructural|Overall\s+recommendations)[^\n]*\n',
        re.IGNORECASE
    )
    
    # Check if document uses » bullets (MZ style) - if so, use » as primary delimiter
    has_chevron = '»' in section_text
    has_bullet = '•' in section_text
    
    if has_chevron:
        # MZ style: » marks main recs, • marks sub-bullets (include in rec text)
        bullet_char = '»'
        bullet_pattern = re.compile(
            r'(?:^|\n)\s*»\s*\n?\s*(.+?)(?=\n\s*»\s|\n\s*(?:REGULATION|INSTITUTIONAL|CAPACITY|Conclusion|CONCLUSION)\b|\Z)',
            re.DOTALL
        )
    else:
        # NA style: • marks recs
        bullet_char = '•'
        bullet_pattern = re.compile(
            r'(?:^|\n)\s*•\s*\n?\s*(.+?)(?=\n\s*•\s|\n\s*(?:Regulation|REGULATION|INSTITUTIONAL|CAPACITY|Capacity|Conclusion|CONCLUSION|Overall|©)\b|\Z)',
            re.DOTALL
        )
    
    # Split into dimension sections
    dim_matches = list(dim_pattern.finditer(section_text))
    
    if not dim_matches:
        # No dimension headers - extract from full section
        sections = [("", 0, len(section_text))]
    else:
        sections = []
        for idx, dm in enumerate(dim_matches):
            dim_name = dm.group(1).strip().title()
            chunk_start = dm.end()
            chunk_end = dim_matches[idx + 1].start() if idx + 1 < len(dim_matches) else len(section_text)
            sections.append((dim_name, chunk_start, chunk_end))
    
    for dim_name, chunk_start, chunk_end in sections:
        chunk = section_text[chunk_start:chunk_end]
        
        for bm in bullet_pattern.finditer(chunk):
            rec_text = bm.group(1).strip()
            rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
            
            if len(rec_text_clean) < 30:
                continue
            
            rec_num += 1
            
            # Title: first sentence or bold-like text before ':'
            title = rec_text_clean[:200]
            colon_pos = title.find(':')
            if 5 < colon_pos < 100:
                title = title[:colon_pos]
            else:
                period_pos = title.find('.')
                if 20 < period_pos < 150:
                    title = title[:period_pos + 1]
            
            # Extract timeframe if present
            timeframe = ""
            tf_match = re.search(r'Timeframe:\s*(20\d{2}[-–]20\d{2})', rec_text_clean)
            if tf_match:
                timeframe = tf_match.group(1)
            
            recommendations.append({
                "number": rec_num,
                "title": title.strip(),
                "text": rec_text_clean[:2000],
                "dimension": dim_name if dim_name else current_dimension,
                "timeline": timeframe,
                "start_page": 0
            })
        
        # Fallback for paragraph-style recs (MZ institutional framework)
        # If no bullet recs found in this section, try "Title: text\nResponsible Institutions:" pattern
        bullet_found = any(True for bm in bullet_pattern.finditer(chunk) if len(bm.group(1).strip()) >= 30)
        if not bullet_found:
            # Split by "Responsible Institutions:" or "Timeframe:" as delimiters
            para_pattern = re.compile(
                r'([A-Z][^.]*?:\s+[A-Z].+?)(?=\nResponsible\s+Institutions:)',
                re.DOTALL
            )
            for pm in para_pattern.finditer(chunk):
                rec_text = pm.group(1).strip()
                rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()
                if len(rec_text_clean) < 30:
                    continue
                rec_num += 1
                title = rec_text_clean[:200]
                colon_pos = title.find(':')
                if 5 < colon_pos < 80:
                    title = title[:colon_pos]
                recommendations.append({
                    "number": rec_num,
                    "title": title.strip(),
                    "text": rec_text_clean[:2000],
                    "dimension": dim_name if dim_name else current_dimension,
                    "start_page": 0
                })
        
        if dim_name:
            current_dimension = dim_name
    
    return recommendations


def _extract_dimension_tab_numbered_recommendations(pages):
    """Extract recs from 'Recommendations – [Dimension]' sections with tab-numbered items (AG style).
    Pattern: 'Recommendations – Legal Dimension' followed by 1.\t text, 2.\t text, etc.
    Only uses headers that are followed by actual numbered recommendation content (not TOC).
    """
    full_text = get_full_text(pages)
    recommendations = []
    rec_num = 0

    # Find all "Recommendations – XYZ Dimension" headers
    dim_headers = list(re.finditer(
        r'(?:^|\n)\s*Recommendations?\s*[–—-]\s*(.+?)(?:Dimension)?\s*\n',
        full_text, re.IGNORECASE
    ))
    if not dim_headers:
        return []

    # Filter: only keep headers followed by numbered items (1.\t) within 500 chars
    # This filters out TOC entries which are followed by page numbers or other headers
    content_headers = []
    for m in dim_headers:
        after = full_text[m.end():m.end() + 500]
        # Check if numbered items follow within a reasonable distance
        if re.search(r'(?:^|\n)\s*1[\.\)]\s+\S', after):
            content_headers.append(m)

    if not content_headers:
        return []

    for idx, header in enumerate(content_headers):
        dim_name = header.group(1).strip()
        start = header.end()
        end = content_headers[idx + 1].start() if idx + 1 < len(content_headers) else min(start + 10000, len(full_text))
        section = full_text[start:end]

        # Extract numbered items: "1.\t" or "1.  " at start of line
        num_pattern = re.compile(
            r'(?:^|\n)\s*(\d+)[\.\)]\s+(.+?)(?=\n\s*\d+[\.\)]\s+\S|\n\s*(?:###\s+Page|Recommendations?\s*[–—-])|\Z)',
            re.DOTALL
        )
        for m in num_pattern.finditer(section):
            rec_text = re.sub(r'\s+', ' ', m.group(2)).strip()
            # Skip very short items or page artifacts
            if len(rec_text) < 20:
                continue
            rec_num += 1
            title = rec_text[:200]
            period_pos = title.find('.')
            if 20 < period_pos < 180:
                title = title[:period_pos + 1]

            recommendations.append({
                "number": rec_num,
                "title": title,
                "text": rec_text[:2000],
                "dimension": dim_name,
                "start_page": 0
            })

    return recommendations


def _extract_xy_hierarchical_recommendations(pages):
    """Extract X.Y or X.Y.Z hierarchical recs under numbered section headers (CU, DO, PE style).
    Pattern: '1. REGULATION' or '1. IMPLEMENTATION' followed by 1.1.\t, 1.2.\t, etc.
    Also handles X.Y.Z sub-numbering.
    """
    full_text = get_full_text(pages)

    # Find recommendation section - look for last occurrence of RECOMMENDATIONS header
    section_matches = list(re.finditer(
        r'(?:^|\n)\s*(?:RECOMMENDATIONS|RECOMENDACIONES\s+(?:PRINCIPALES|DE\s+POL[ÍI]TICA)|'
        r'(?:III\.?\s*\t?\s*)?Recomendaciones\s+de\s+Pol[ií]tica)\s*\n',
        full_text, re.IGNORECASE
    ))
    if not section_matches:
        return []

    section_match = section_matches[-1]
    section_start = section_match.end()

    end_match = re.search(
        r'\n\s*(?:REFERENCES|References|ENDNOTES|ANEXO|Anexo|BIBLIOGRAF[ÍI]A|Bibliograf[ií]a|'
        r'That\s+is\s+why\s+UNESCO|Por\s+eso\s+la\s+UNESCO)\s',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 80000, len(full_text))
    section_text = full_text[section_start:section_end]

    recommendations = []
    current_dimension = ""

    # Find X.Y. or X.Y.Z patterns - text may be on same line or next line
    xy_pattern = re.compile(
        r'(?:^|\n)\s*(\d+\.\d+(?:\.\d+)?)\s*\.?\s*\n?\s*(.+?)(?=\n\s*\d+\.\d+(?:\.\d+)?\s*\.?\s|\n\s*\d+\.\s+[A-ZÁÉÍÓÚÑ]|\Z)',
        re.DOTALL
    )
    xy_matches = list(xy_pattern.finditer(section_text))

    if len(xy_matches) < 3:
        return []

    # Find dimension headers: "1. REGULATION" or "1. IMPLEMENTATION..."
    dim_pattern = re.compile(
        r'(?:^|\n)\s*(\d+)\.\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,]+(?:\s+(?:DE|Y|E|LA|EL|DEL|EN|PARA|AND|OF|THE)\s+[A-ZÁÉÍÓÚÑ\s,]+)*)\s*\n',
        re.MULTILINE
    )
    dim_map = []
    for m in dim_pattern.finditer(section_text):
        name = m.group(2).strip()
        if len(name) > 3:
            dim_map.append((m.start(), name.title()))

    for match in xy_matches:
        rec_num = match.group(1)
        rec_text = match.group(2).strip()
        rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()

        # Find dimension
        for pos, name in reversed(dim_map):
            if pos < match.start():
                current_dimension = name
                break

        title = rec_text_clean[:250]
        period_pos = title.find('.')
        if 20 < period_pos < 200:
            title = title[:period_pos + 1]
        elif len(title) > 150:
            title = title[:150].rsplit(' ', 1)[0] + "..."

        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_text_clean[:2000],
            "dimension": current_dimension,
            "start_page": 0
        })

    return recommendations


def _extract_spanish_recomendaciones(pages):
    """Extract Spanish recommendations from table format (MX style).
    Pattern: 'RECOMENDACIONES PRINCIPALES' or 'Tabla X. Resumen de recomendaciones'
    followed by X.Y or X.Y.Z numbered items under RUBRO headers.
    """
    full_text = get_full_text(pages)

    section_matches = list(re.finditer(
        r'(?:Tabla\s+\d+\.?\s*Resumen\s+de\s+recomendaciones|RECOMENDACIONES\s+PRINCIPALES)\s*\n',
        full_text, re.IGNORECASE
    ))
    if not section_matches:
        return []

    section_match = section_matches[-1]
    section_start = section_match.end()

    end_match = re.search(
        r'\n\s*(?:Por\s+eso\s+la\s+UNESCO|BIBLIOGRAF[ÍI]A|ANEXO|Fuente|Figura\s+\d+\.\s)',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 30000, len(full_text))
    section_text = full_text[section_start:section_end]

    recommendations = []
    current_dimension = ""

    # Find X.Y or X.Y.Z patterns
    xy_pattern = re.compile(
        r'(?:^|\n)\s*(\d+\.\d+(?:\.\d+)?)\s+(.+?)(?=\n\s*\d+\.\d+(?:\.\d+)?\s|\n\s*\d+\.\s+[A-ZÁÉÍÓÚÑ]|\Z)',
        re.DOTALL
    )
    xy_matches = list(xy_pattern.finditer(section_text))

    if len(xy_matches) < 3:
        return []

    # Find dimension/RUBRO headers
    dim_pattern = re.compile(
        r'(?:^|\n)\s*(\d+)\.\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,]+(?:\s+(?:DE|Y|E|LA|EL|DEL|EN|PARA)\s+[A-ZÁÉÍÓÚÑ\s,]+)*)\s*\n',
        re.MULTILINE
    )
    dim_map = []
    for m in dim_pattern.finditer(section_text):
        name = m.group(2).strip()
        if len(name) > 3:
            dim_map.append((m.start(), name.title()))

    for match in xy_matches:
        rec_num = match.group(1)
        rec_text = match.group(2).strip()
        rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()

        for pos, name in reversed(dim_map):
            if pos < match.start():
                current_dimension = name
                break

        title = rec_text_clean[:250]
        period_pos = title.find('.')
        if 20 < period_pos < 200:
            title = title[:period_pos + 1]
        elif len(title) > 150:
            title = title[:150].rsplit(' ', 1)[0] + "..."

        recommendations.append({
            "number": rec_num,
            "title": title,
            "text": rec_text_clean[:2000],
            "dimension": current_dimension,
            "language": "es",
            "start_page": 0
        })

    return recommendations


def _extract_french_dash_bullet_recommendations(pages):
    """Extract French recommendations with -- or – dash bullets under section headers (SN style).
    Pattern: 'RECOMMANDATIONS SUR/RELATIVES/EN MATIÈRE...' followed by -- bullet items.
    """
    full_text = get_full_text(pages)

    # Find all RECOMMANDATIONS section headers (use last occurrences)
    section_headers = list(re.finditer(
        r'(?:^|\n)\s*[A-Z]\.?\s+RECOMMANDATIONS?\s+(?:SUR|RELATIVES?|EN\s+MATIÈRE|POUR|DANS|D\'UN)\s+[^\n]+\n',
        full_text, re.IGNORECASE
    ))
    # Also try lettered headers like "K.    RECOMMANDATIONS..."
    if not section_headers:
        section_headers = list(re.finditer(
            r'(?:^|\n)\s*(?:[A-Z]\.?\s+)?RECOMMANDATIONS?\s+(?:SUR|RELATIVES?|EN\s+MATIÈRE|POUR|DANS|D\'UN)\s+[^\n]+\n',
            full_text, re.IGNORECASE
        ))
    if not section_headers:
        return []

    # Find the chapter-level header for recommendations
    chapter_match = list(re.finditer(
        r'(?:^|\n)\s*(?:[IVXLCDM]+\.?\s+)?RECOMMANDATIONS?\s+POUR\s+ACCOMPAGNER[^\n]+\n',
        full_text, re.IGNORECASE
    ))

    # Use sub-section headers that come after the chapter header
    if chapter_match:
        chapter_pos = chapter_match[-1].start()
        section_headers = [h for h in section_headers if h.start() >= chapter_pos]

    if not section_headers:
        return []

    recommendations = []
    rec_num = 0

    for idx, header in enumerate(section_headers):
        dim_name = header.group(0).strip()
        # Clean dimension name
        dim_name = re.sub(r'^[A-Z]\.?\s+', '', dim_name).strip()
        dim_name = re.sub(r'^RECOMMANDATIONS?\s+', '', dim_name, flags=re.IGNORECASE).strip()

        start = header.end()
        end = section_headers[idx + 1].start() if idx + 1 < len(section_headers) else min(start + 10000, len(full_text))
        section = full_text[start:end]

        # Extract -- or – bullet items
        bullet_pattern = re.compile(
            r'(?:^|\n)\s*(?:--|–)\s*\n?\s*(.+?)(?=\n\s*(?:--|–)\s|\n\s*(?:[A-Z]\.?\s+)?(?:RECOMMANDATION|Ces\s+recommandations|XI\.|###\s+Page)|\Z)',
            re.DOTALL
        )
        for bm in bullet_pattern.finditer(section):
            rec_text = re.sub(r'\s+', ' ', bm.group(1)).strip()
            if len(rec_text) < 20:
                continue
            rec_num += 1

            title = rec_text[:200]
            period_pos = title.find('.')
            semicolon_pos = title.find(';')
            cut = min(p for p in [period_pos, semicolon_pos, 200] if p > 15)
            if cut < 200:
                title = title[:cut + 1] if cut == period_pos else title[:cut]

            recommendations.append({
                "number": rec_num,
                "title": title.strip(),
                "text": rec_text[:2000],
                "dimension": dim_name,
                "language": "fr",
                "start_page": 0
            })

    return recommendations


def _extract_nl_prose_recommendations(pages):
    """Extract prose recommendations under dimension headers with government responses (NL style).
    Pattern: 'RECOMMENDATIONS' section -> 'LAWS AND REGULATION' -> bold rec title paragraph -> 
    'Government response' -> next rec or next dimension.
    """
    full_text = get_full_text(pages)

    # Find the RECOMMENDATIONS section (last occurrence)
    section_matches = list(re.finditer(
        r'(?:^|\n)\s*RECOMMENDATIONS\s*\n',
        full_text
    ))
    if not section_matches:
        return []

    section_match = section_matches[-1]
    section_start = section_match.end()

    end_match = re.search(
        r'\n\s*(?:CONCLUSION|Conclusion|REFERENCES|References|ENDNOTES|That\s+is\s+why\s+UNESCO)\s',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 40000, len(full_text))
    section_text = full_text[section_start:section_end]

    recommendations = []
    rec_num = 0
    current_dimension = ""

    # Detect dimension headers (all-caps lines like "LAWS AND REGULATION")
    dim_pattern = re.compile(
        r'(?:^|\n)\s*((?:LAWS?\s+AND\s+REGULATION|INSTITUTIONAL\s+FRAMEWORK|CAPACITY\s+BUILDING|'
        r'TECHNOLOGY\s+AND\s+INNOVATION|INVESTMENT\s+ECOSYSTEM|INCLUSION\s+AND\s+WELL|'
        r'RESPONSIBLE\s+TECHNOLOGIES?|SCIENTIFIC\s+AND\s+EDUCATIONAL|'
        r'SOCIAL\s+AND\s+CULTURAL|ECONOMIC|TECHNICAL\s+AND\s+INFRASTRUCTURAL)[^\n]*)\s*\n',
        re.IGNORECASE
    )

    # Split by "Government response" blocks - each rec is followed by a gov response
    # The rec text is between dimension header (or prev gov response end) and next "Government response"
    gov_response_positions = [m.start() for m in re.finditer(r'\nGovernment\s+response\s*\n', section_text, re.IGNORECASE)]

    if not gov_response_positions:
        # Try splitting by paragraph blocks instead
        # Each recommendation starts with a bold/emphasized sentence
        return []

    # For each government response, the recommendation text is between
    # the previous gov response end (or section start) and the current gov response
    prev_end = 0
    for gr_pos in gov_response_positions:
        rec_block = section_text[prev_end:gr_pos].strip()

        # Find dimension header in this block
        dm = dim_pattern.search(rec_block)
        if dm:
            current_dimension = dm.group(1).strip().title()
            rec_block = rec_block[dm.end():].strip()

        # Skip empty blocks
        if len(rec_block) < 50:
            # Find end of government response
            next_content = section_text[gr_pos:]
            gr_end_match = re.search(r'\n\s*\n\s*(?=[A-Z])', next_content[20:])
            prev_end = gr_pos + 20 + gr_end_match.start() if gr_end_match else gr_pos + 500
            continue

        rec_num += 1
        rec_text_clean = re.sub(r'\s+', ' ', rec_block).strip()

        # Title: first sentence or bold-like opening
        title = rec_text_clean[:300]
        # Look for the main recommendation statement (often first paragraph)
        newline_pos = rec_block.find('\n')
        if 20 < newline_pos < 200:
            title = re.sub(r'\s+', ' ', rec_block[:newline_pos]).strip()
        else:
            period_pos = title.find('.')
            if 20 < period_pos < 250:
                title = title[:period_pos + 1]

        recommendations.append({
            "number": rec_num,
            "title": title[:250],
            "text": rec_text_clean[:2000],
            "dimension": current_dimension,
            "start_page": 0
        })

        # Find end of government response section
        next_content = section_text[gr_pos:]
        gr_end_match = re.search(r'\n\s*\n\s*(?=[A-Z])', next_content[20:])
        prev_end = gr_pos + 20 + gr_end_match.start() if gr_end_match else gr_pos + 500

    return recommendations


def _extract_titled_prose_recommendations(pages):
    """Extract prose recommendations with bold titles (LA style).
    Pattern: Bold/emphasized title line followed by description paragraph.
    Found in RECOMMENDATIONS section without numbering.
    """
    full_text = get_full_text(pages)

    # Find RECOMMENDATIONS section - pick the one followed by substantial prose content
    section_matches = list(re.finditer(
        r'(?:^|\n)\s*RECOMMENDATIONS\s*\n',
        full_text
    ))
    if not section_matches:
        return []

    # Score each match: prefer ones followed by prose (not tables/TOC)
    best_match = None
    best_score = 0
    for m in section_matches:
        after = full_text[m.end():m.end() + 2000]
        # Skip if followed by table headers (PHASE, KEY ACTIONS, etc.)
        if re.match(r'\s*(?:PHASE|KEY\s+ACTIONS|CATEGORY|RECOMMENDED)', after):
            continue
        # Skip TOC-like entries (tab-separated numbers)
        if re.match(r'\s*\d+\s*\n', after):
            continue
        # Score by prose content length (lines > 50 chars)
        prose_lines = [l for l in after.split('\n') if len(l.strip()) > 50]
        score = len(prose_lines)
        if score > best_score:
            best_score = score
            best_match = m

    if not best_match:
        # Fallback to last match
        best_match = section_matches[-1]

    section_match = best_match
    section_start = section_match.end()

    end_match = re.search(
        r'\n\s*(?:PHASING\s+OF\s+RECOMMENDATIONS|CONCLUSION|Conclusion|REFERENCES|References|'
        r'ENDNOTES|That\s+is\s+why\s+UNESCO|ANNEXE|Annex)\s',
        full_text[section_start:]
    )
    section_end = section_start + end_match.start() if end_match else min(section_start + 15000, len(full_text))
    section_text = full_text[section_start:section_end]

    # Check if this section has numbered items (if so, other extractors handle it)
    if len(re.findall(r'(?:^|\n)\s*\d+\.\d+\s', section_text)) > 3:
        return []

    recommendations = []
    rec_num = 0
    current_dimension = ""

    # Detect dimension sub-headers
    dim_pattern = re.compile(
        r'(?:^|\n)\s*((?:Institutional\s+Frameworks?|Capacity\s+Building|Laws?\s+and\s+Regulation|'
        r'Regulation|Technology|Investment|Inclusion)[^\n]*)\s*\n',
        re.IGNORECASE
    )

    # Pattern: title-like line (short, title-case or mixed) followed by paragraph
    # Title lines are typically 30-150 chars, don't start with common prose words
    lines = section_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Check for dimension header
        dm = dim_pattern.match('\n' + line + '\n')
        if dm:
            candidate = dm.group(1).strip()
            if len(candidate) < 60:
                current_dimension = candidate
                i += 1
                continue

        # Check if this looks like a recommendation title
        # Title characteristics: 30-150 chars, starts with capital, action-oriented
        if (30 < len(line) < 200 and
            re.match(r'^[A-Z]', line) and
            not re.match(r'^(?:The|This|These|In|For|A|An|It|As|On|To|With|However|Although|While|Furthermore|Moreover|Similarly|Based)\s', line) and
            not re.match(r'^###', line) and
            not line.endswith(',') and
            not re.match(r'^\d', line)):

            # Collect following paragraph text
            desc_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    if i < len(lines) and lines[i].strip():
                        # Check if next non-empty line is a new title
                        peek = lines[i].strip()
                        if (30 < len(peek) < 200 and
                            re.match(r'^[A-Z]', peek) and
                            not re.match(r'^(?:The|This|These|In|For|A|An|It|As|On|To|With)\s', peek)):
                            break
                        desc_lines.append(peek)
                        i += 1
                    continue
                if re.match(r'^###\s+Page', next_line):
                    i += 1
                    continue
                # Check for dimension header
                if dim_pattern.match('\n' + next_line + '\n') and len(next_line) < 60:
                    break
                # Check if this is a new title (short action line)
                if (30 < len(next_line) < 200 and
                    re.match(r'^[A-Z]', next_line) and
                    not re.match(r'^(?:The|This|These|In|For|A|An|It|As|On|To|With|However|Although|While)\s', next_line) and
                    not next_line.endswith(',') and
                    len(desc_lines) > 0):
                    break
                desc_lines.append(next_line)
                i += 1

            desc = ' '.join(desc_lines).strip()
            if len(desc) > 30 or len(line) > 50:
                rec_num += 1
                rec_text = (line + ' ' + desc).strip()
                rec_text_clean = re.sub(r'\s+', ' ', rec_text).strip()

                recommendations.append({
                    "number": rec_num,
                    "title": line[:200],
                    "text": rec_text_clean[:2000],
                    "dimension": current_dimension,
                    "start_page": 0
                })
            continue
        i += 1

    return recommendations


def extract_executive_summary(pages, language="en"):
    """Extract the executive summary text. Handles English, French, and Portuguese."""
    summary_lines = []
    in_summary = False
    
    # Multi-language patterns for summary start
    summary_patterns = [
        r'Executive\s+[Ss]ummary',
        r'EXECUTIVE\s+SUMMARY',
        r'Résumé\s+exécutif',
        r'RÉSUMÉ\s+EXÉCUTIF',
        r'Résumé',
        r'Resumo\s+executivo',
        r'RESUMO\s+EXECUTIVO',
    ]
    summary_regex = re.compile('|'.join(summary_patterns), re.IGNORECASE)
    
    # Multi-language patterns for summary end  
    end_patterns = [
        r'CHAPTER\s+1\b',
        r'Chapter\s+1\b',
        r'Chapitre\s+1\b',
        r'CHAPITRE\s+1\b',
        r'Capítulo\s+1\b',
        r'TABLE\s+OF\s+CONTENTS',
        r'Table\s+of\s+[Cc]ontents',
        r'TABLE\s+DES\s+MATIÈRES',
        r'ÍNDICE',
    ]
    end_regex = re.compile('|'.join(end_patterns), re.IGNORECASE)
    
    for page_data in pages:
        text = page_data["text"]
        
        if summary_regex.search(text):
            in_summary = True
        
        if in_summary:
            # Stop at Chapter 1 or TOC (but only after we've collected some text)
            if page_data["page"] > 5 and end_regex.search(text):
                break
            summary_lines.append(text)
            # Don't go past 10 pages of summary
            if len(summary_lines) > 10:
                break
    
    return "\n\n".join(summary_lines).strip()


def extract_metadata(doc, pages):
    """Extract report metadata."""
    metadata = {
        "page_count": doc.page_count,
        "creation_date": None,
        "modification_date": None,
    }
    
    pdf_meta = doc.metadata
    if pdf_meta:
        metadata["creation_date"] = pdf_meta.get("creationDate", "")
        metadata["modification_date"] = pdf_meta.get("modDate", "")
    
    for page_data in pages[:10]:
        text = page_data["text"]
        country_match = re.search(
            r'^([A-Z]{2,}(?:\s+[A-Z]+)*)\s*$',
            text, re.MULTILINE
        )
        if country_match:
            candidate = country_match.group(1).strip()
            if candidate not in ["ACKNOWLEDGEMENTS", "UNESCO", "FOREWORD", "CHAPTER",
                                  "EXECUTIVE", "SUMMARY", "RECOMMENDATION", "TABLE",
                                  "RÉSUMÉ", "CHAPITRE", "REMERCIEMENTS"]:
                metadata["country_name"] = candidate
                break
    
    return metadata


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


###############################################################################
# NEW: Dimension-level structured extraction
###############################################################################

# Dimension header patterns in EN / FR / PT (fuzzy)
DIMENSION_PATTERNS = {
    "legal_regulatory": [
        r"legal\s+and\s+regulatory",
        r"legal\s*[/&]\s*regulatory",
        r"axe\s+juridique",
        r"dimension\s+juridique",
        r"juridique\s+et\s+r[ée]glementaire",
        r"dimensão\s+jur[ií]dica",
        r"regulamentar",
    ],
    "social_cultural": [
        r"social\s+and\s+cultural",
        r"social\s*[/&]\s*cultural",
        r"axe\s+social\s+et\s+culturel",
        r"dimension\s+sociale",
        r"sociale\s+et\s+culturelle",
        r"dimensão\s+social",
    ],
    "scientific_educational": [
        r"scientific\s+and\s+educational",
        r"scientific\s*[/&]\s*educational",
        r"axe\s+scientifique",
        r"dimension\s+scientifique",
        r"scientifique\s+et\s+[ée]ducation",
        r"dimensão\s+cient[ií]fica",
    ],
    "economic": [
        r"economic\s+dimension",
        r"economic\s+impact",
        r"axe\s+[ée]conomique",
        r"dimension\s+[ée]conomique",
        r"dimensão\s+econ[oô]mica",
        r"\beconomic\b",
    ],
    "technological_infrastructural": [
        r"techni(?:cal|que)\s+and\s+infrastructural",
        r"technical\s*[/&]\s*infrastructural",
        r"technological\s+and\s+infrastructural",
        r"axe\s+technique\s+et\s+infrastructur",
        r"dimension\s+technologique",
        r"technique\s+et\s+infrastructur",
        r"dimensão\s+tecnol[oó]gica",
    ],
}

# Titles for output
DIMENSION_TITLES = {
    "legal_regulatory": "Legal and Regulatory",
    "social_cultural": "Social and Cultural",
    "scientific_educational": "Scientific and Educational",
    "economic": "Economic",
    "technological_infrastructural": "Technological and Infrastructural",
}


def _find_dimension_sections(full_text):
    """Find text sections for each of the 5 scored dimensions using fuzzy header matching.
    Returns dict: dim_key -> section_text
    """
    # Collect all candidate header positions
    candidates = []  # (position, dim_key, matched_text)

    for dim_key, patterns in DIMENSION_PATTERNS.items():
        for pat in patterns:
            for m in re.finditer(pat, full_text, re.IGNORECASE):
                # Only match if it looks like a header (near start of line or after newline)
                pre = full_text[max(0, m.start() - 30):m.start()]
                # Accept if near line start, page marker, or chapter marker
                if re.search(r'(?:^|\n|###\s*Page\s+\d+)\s*$', pre) or \
                   re.search(r'(?:chapter|chapitre|capítulo)\s+\d+', pre, re.IGNORECASE) or \
                   re.search(r'\n\s*$', pre):
                    candidates.append((m.start(), dim_key, m.group()))

    if not candidates:
        return {}

    # Sort by position
    candidates.sort(key=lambda x: x[0])

    # Strategy: find dimension headers that start actual content sections (not TOC).
    # A real section header is followed by substantial text (>500 chars) before the next dim header.
    # TOC entries are clustered together with minimal text between them.
    text_len = len(full_text)

    # Group candidates by dim_key, sorted by position
    from collections import defaultdict
    dim_candidates = defaultdict(list)
    for pos, dim_key, matched in candidates:
        dim_candidates[dim_key].append(pos)

    # For each dimension, find the occurrence that's followed by the most text
    # before another dimension header appears
    all_dim_positions = sorted(set(pos for pos, _, _ in candidates))

    dim_positions = {}
    for dim_key, positions in dim_candidates.items():
        best_pos = None
        best_content_len = 0
        for pos in positions:
            # Find next dimension header position after this one
            next_positions = [p for p in all_dim_positions if p > pos + 50]
            next_dim_pos = next_positions[0] if next_positions else text_len
            content_len = min(next_dim_pos - pos, 50000)
            if content_len > best_content_len:
                best_content_len = content_len
                best_pos = pos
        if best_pos is not None and best_content_len > 200:
            dim_positions[dim_key] = best_pos

    if len(dim_positions) < 2:
        return {}

    # Sort dimensions by position
    sorted_dims = sorted(dim_positions.items(), key=lambda x: x[1])

    # Extract text between consecutive dimension headers
    sections = {}
    for i, (dim_key, start_pos) in enumerate(sorted_dims):
        # Find end: next dimension start or end of text (capped)
        if i + 1 < len(sorted_dims):
            end_pos = sorted_dims[i + 1][1]
        else:
            # For last dimension, cap at recommendations section or +30k chars
            rec_match = re.search(
                r'\n\s*(?:RECOMMENDATIONS|Recommendations|RECOMMANDATIONS|Recommandations|'
                r'RECOMENDAÇÕES|MAIN\s+POLICY|HIGH\s+LEVEL\s+RECOMMENDATIONS|'
                r'Multi-?[Ss]takeholder\s+[Cc]onsultations|'
                r'Chapitre\s+(?:II|III|2|3)|Chapter\s+(?:7|8))\s',
                full_text[start_pos:]
            )
            end_pos = start_pos + rec_match.start() if rec_match else min(start_pos + 30000, text_len)

        section_text = full_text[start_pos:end_pos]
        sections[dim_key] = section_text

    return sections


def _extract_strengths_gaps_findings(text, language="en"):
    """Extract strengths, gaps, and general findings from a dimension section."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Clean sentences
    sentences = [re.sub(r'\s+', ' ', s).strip() for s in sentences if len(s.strip()) > 30]

    strengths = []
    gaps = []
    findings = []

    strength_indicators = [
        r'\b(?:established|adopted|launched|enacted|ranks?\s+\d|leading|significant\s+progress|'
        r'notable\s+(?:progress|strides|achievement)|successfully|impressive|strong\s+commitment|'
        r'pioneering|innovative|advanced|robust|comprehensive|well-?developed|commendable|'
        r'a\s+mis\s+en\s+place|adopté|lancé|significati[fv]|remarquable|notável|avançad[oa])\b'
    ]
    gap_indicators = [
        r'\b(?:lack(?:s|ing)?|absence|no\s+dedicated|gap|challenge|limited|inadequate|'
        r'insufficient|not\s+yet|does\s+not|remains?\s+(?:low|weak|limited|absent)|'
        r'need(?:s|ed)?\s+(?:to|for)|urgent|lacune|manque|défi|limité|ausência|desafio|'
        r'however|although|despite|yet\s+to|still\s+(?:lack|need|require))\b'
    ]

    for sent in sentences[:200]:  # Cap to avoid processing huge texts
        if len(sent) < 40 or len(sent) > 500:
            continue
        # Skip footnotes, references, page markers
        if re.match(r'^\d+\s*$|^###|^\d+\s*[A-Z]', sent):
            continue

        is_strength = any(re.search(p, sent, re.IGNORECASE) for p in strength_indicators)
        is_gap = any(re.search(p, sent, re.IGNORECASE) for p in gap_indicators)

        if is_strength and not is_gap:
            if len(strengths) < 10:
                strengths.append(sent[:300])
        elif is_gap and not is_strength:
            if len(gaps) < 10:
                gaps.append(sent[:300])
        elif is_strength or is_gap:
            # Mixed - add to findings
            if len(findings) < 8:
                findings.append(sent[:300])
        else:
            # General observation with substantive content
            if len(findings) < 8 and re.search(r'\b(?:AI|artificial intelligence|IA|data|strateg|policy|law|regulation)\b', sent, re.IGNORECASE):
                findings.append(sent[:300])

    return findings, strengths, gaps


def _extract_key_stats(text):
    """Extract key statistics (numbers with context) from a dimension section."""
    stats = []
    seen = set()

    # Pattern: number with unit/context
    patterns = [
        # Percentages
        (r'(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?([A-Za-z\s]{3,30})', 'percent'),
        # Currency amounts
        (r'(?:\$|USD|EUR|SAR|EGP)\s*(\d+(?:\.\d+)?)\s*(billion|million|trillion|B|M)', 'currency'),
        (r'(\d+(?:\.\d+)?)\s*(billion|million|trillion)\s*(?:dollars?|USD|EUR)', 'currency'),
        # Counts with context
        (r'(\d{2,})\s+(AI\s+(?:startups?|companies|institutes?|cent(?:er|re)s?|researchers?|publications?))',
         'count'),
        (r'(\d{2,})\s+(universit(?:y|ies)|institutions?|(?:data\s+)?cent(?:er|re)s?)', 'count'),
        # Rankings
        (r'rank(?:ed|s|ing)?\s+(\d+)(?:st|nd|rd|th)?\s+(?:globally|in\s+\w+|worldwide|out\s+of)', 'rank'),
        # Years with events
        (r'(20[12]\d)\s*[,:]?\s*(National\s+AI\s+Strategy|(?:data\s+)?protection\s+law|charter|'
         r'strategy|framework|law\s+(?:no|No)|Act\s+No)', 'year_event'),
        # Large numbers
        (r'(\d{1,3}(?:,\d{3})+)\s+(people|students?|trained|graduates?|workers?|jobs?|users?)', 'large_count'),
    ]

    for pat, stat_type in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            full_match = m.group(0)
            if full_match in seen:
                continue
            seen.add(full_match)

            # Get surrounding context (sentence)
            start = max(0, m.start() - 100)
            end = min(len(text), m.end() + 100)
            context = re.sub(r'\s+', ' ', text[start:end]).strip()

            stat_entry = {"stat": full_match.strip(), "context": context[:200]}

            if stat_type == 'percent':
                try:
                    stat_entry["value"] = float(m.group(1))
                    stat_entry["unit"] = "%"
                except (ValueError, IndexError):
                    pass
            elif stat_type == 'currency':
                try:
                    val = float(m.group(1))
                    unit = m.group(2).lower() if m.lastindex >= 2 else ""
                    if 'billion' in unit or unit == 'b':
                        val *= 1e9
                    elif 'million' in unit or unit == 'm':
                        val *= 1e6
                    stat_entry["value"] = val
                    stat_entry["unit"] = "USD"
                except (ValueError, IndexError):
                    pass
            elif stat_type == 'year_event':
                stat_entry["year"] = m.group(1)

            if len(stats) < 15:
                stats.append(stat_entry)

    return stats


def _extract_regulations(text):
    """Extract named regulations/laws from the legal dimension section."""
    regulations = []
    seen = set()

    # Pattern: "Law/Act/Regulation Name" + optional year + optional status
    patterns = [
        r'(?:the\s+)?((?:[A-Z][a-z]+\s+){0,4}(?:Law|Act|Regulation|Decree|Code|Bill|Charter|Policy|'
        r'Framework|Convention|Directive)(?:\s+(?:No|no|Number)\.?\s*\d+)?(?:\s+(?:of|de|du)\s+\d{4})?)',
        r'(?:Law|Loi|Lei)\s+(?:No|no|n°|nº)\.?\s*(\d+(?:[/-]\d+)?)\s+(?:of|de|du)\s+(\d{4})',
    ]

    # Process sentence by sentence to avoid catastrophic backtracking
    sentences = re.split(r'[.\n]', text)
    law_name_pat = re.compile(
        r'((?:[A-Z][A-Za-z]+\s+){1,5}(?:Law|Act|Charter|Policy|Framework|Code|Regulation))'
    )
    enacted_pat = re.compile(r'(?:enacted|adopted|passed|issued|promulgated|approved|entered into force)', re.IGNORECASE)
    year_pat = re.compile(r'(20[012]\d)')

    for sent in sentences:
        if len(sent) > 500 or len(sent) < 15:
            continue
        name_m = law_name_pat.search(sent)
        if name_m and enacted_pat.search(sent):
            year_m = year_pat.search(sent)
            if year_m:
                name = re.sub(r'\s+', ' ', name_m.group(1)).strip()
                year = year_m.group(1)
                key = name.lower()
                if key not in seen and len(name) > 8:
                    seen.add(key)
                    regulations.append({"name": name, "year": year, "status": "enacted"})

    # Broader: "Law No. X of YEAR"
    law_num = re.compile(
        r'(?:Law|Loi|Lei)\s+(?:No|no|n°|nº)\.?\s*(\d+(?:[/-]\d+)?)\s+(?:of|de|du)\s+(20[012]\d)',
        re.IGNORECASE
    )
    for m in law_num.finditer(text):
        name = m.group(0).strip()
        year = m.group(2)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            regulations.append({"name": name, "year": year, "status": "enacted"})

    # Named laws/acts with year in parentheses: "Personal Data Protection Law (2020)"
    paren_year = re.compile(
        r'((?:[A-Z][a-z]+\s+){1,5}(?:Law|Act|Charter|Code|Framework|Policy))\s*\((\d{4})\)',
    )
    for m in paren_year.finditer(text):
        name = m.group(1).strip()
        year = m.group(2)
        key = name.lower()
        if key not in seen and len(name) > 8:
            seen.add(key)
            regulations.append({"name": name, "year": year, "status": "enacted"})

    # Draft/proposed
    draft_pat = re.compile(
        r'(?:draft|proposed|pending|under\s+development)\s+((?:[A-Z][a-z]+\s+){1,5}(?:Law|Act|Bill|Framework|Policy))',
        re.IGNORECASE
    )
    for m in draft_pat.finditer(text):
        name = m.group(1).strip()
        key = name.lower()
        if key not in seen and len(name) > 8:
            seen.add(key)
            regulations.append({"name": name, "year": "", "status": "draft"})

    return regulations[:15]


def _extract_rankings_indices(full_text):
    """Extract index scores and international rankings from the full report text."""
    rankings = []
    seen = set()

    # Known index names for matching
    INDEX_NAMES = [
        r'Government\s+AI\s+Readiness\s+Index',
        r'Global\s+AI\s+Index',
        r'Tortoise\s+(?:Intelligence\s+)?Global\s+AI\s+Index',
        r'Global\s+Cybersecurity\s+Index',
        r'E-?Government\s+Development\s+Index',
        r'Online\s+Services?\s+Index',
        r'E-?Participation\s+Index',
        r'Global\s+Innovation\s+Index',
        r'Open\s+Data\s+Inventory(?:\s+Ranking)?',
        r'ODIN',
        r'Global\s+Gender\s+Gap\s+Index',
        r'Coursera\s+Global\s+Skills(?:\s+Report)?',
        r'Inclusive\s+Internet\s+Index',
        r'Network\s+Readiness\s+Index',
        r'ICT\s+Development\s+Index',
        r'Digital\s+Quality\s+of\s+Life\s+Index',
        r'Human\s+Development\s+Index',
        r'Global\s+Data\s+Barometer',
        r'Open\s+Government\s+Data\s+Index',
        r'GII',
        r'EGDI',
        r'OSI',
        r'EPI',
        r'GCI',
        r'Stanford\s+AI\s+Index',
        r'OECD\.?AI',
        r'Oxford\s+Insights',
    ]
    index_pattern = '|'.join(INDEX_NAMES)

    sentences = re.split(r'(?<=[.!?])\s+', full_text)

    # Pattern: "ranked Nth" or "ranks Nth" near an index name
    rank_num_pat = re.compile(
        r'rank(?:ed|s|ing)?\s+(\d+)(?:st|nd|rd|th)?', re.IGNORECASE
    )
    score_pat = re.compile(
        r'scor(?:ed|ing|e\s+of)\s+(\d+(?:\.\d+)?)', re.IGNORECASE
    )
    total_pat = re.compile(
        r'(?:out\s+of|among|of)\s+(\d+)\s+countries', re.IGNORECASE
    )
    year_pat = re.compile(r'(20[12]\d)')
    index_re = re.compile(index_pattern, re.IGNORECASE)

    for sent_raw in sentences:
        sent = re.sub(r'\s+', ' ', sent_raw).strip()
        if len(sent) < 25 or len(sent) > 500:
            continue

        # Must have a ranking/score pattern
        has_rank = rank_num_pat.search(sent)
        has_score = score_pat.search(sent)
        has_index = index_re.search(sent)

        if not (has_rank or has_score) or not has_index:
            continue

        key = sent[:80].lower()
        if key in seen:
            continue
        seen.add(key)

        entry = {"context": sent}

        if has_index:
            entry["index_name"] = has_index.group(0).strip()

        if has_rank:
            try:
                entry["rank"] = int(has_rank.group(1))
            except ValueError:
                pass

        if has_score:
            try:
                entry["score"] = float(has_score.group(1))
            except ValueError:
                pass

        total_m = total_pat.search(sent)
        if total_m:
            try:
                entry["total_countries"] = int(total_m.group(1))
            except ValueError:
                pass

        year_m = year_pat.search(sent)
        if year_m:
            entry["year"] = int(year_m.group(1))

        rankings.append(entry)

    return rankings


def _is_ranking_sentence(sent):
    """Check if a sentence is primarily about an index ranking/score (should go to rankings_indices)."""
    INDEX_NAMES = [
        'readiness index', 'global ai index', 'cybersecurity index', 'e-government',
        'online services index', 'e-participation index', 'innovation index',
        'open data inventory', 'odin', 'gender gap index', 'coursera',
        'inclusive internet', 'network readiness', 'ict development',
        'digital quality', 'human development index', 'data barometer',
        'open government data', 'gii', 'egdi', 'osi', 'epi', 'gci',
        'stanford ai index', 'oecd.ai', 'oxford insights', 'tortoise',
    ]
    lower = sent.lower()
    has_index = any(idx in lower for idx in INDEX_NAMES)
    has_rank = bool(re.search(r'rank(?:ed|s|ing)?\s+\d', lower))
    has_score = bool(re.search(r'scor(?:ed|ing|e\s+of)\s+\d', lower))
    has_out_of = bool(re.search(r'out\s+of\s+\d+\s+countries', lower))

    # If it mentions an index AND has a rank/score, it's a ranking sentence
    if has_index and (has_rank or has_score or has_out_of):
        return True
    # If it's purely "ranked Nth" with "out of N countries" - ranking
    if has_rank and has_out_of:
        return True
    return False


def _extract_achievements(full_text):
    """Extract REAL achievements from the full report text.
    Filters OUT: index rankings, generic scores, numerical stats.
    Keeps: awards, firsts, programs launched, institutions established, partnerships.
    """
    achievements = []
    seen = set()

    sentences = re.split(r'(?<=[.!?])\s+', full_text)

    # Keywords for real achievements
    achievement_kw = re.compile(
        r'(?:(?:first|1st)\s+(?:country\s+)?in\s+(?:Africa|MENA|the\s+world|the\s+region|globally|the\s+Arab)|'
        r'(?:first|1st)\s+(?:to\s+|in\s+the\s+)|'
        r'award(?:ed)?|won\s+(?:the|a)|recognition|recogni[sz]ed|'
        r'launched\s+(?:the\s+)?(?:first|national|a\s+)|'
        r'established\s+(?:the\s+)?(?:first|national|a\s+)|'
        r'created\s+(?:the\s+)?(?:first|national|a\s+)|'
        r'inaugurated|founded|'
        r'developed\s+(?:the\s+)?(?:first|national|a\s+)|'
        r'deployed|built\s+(?:the\s+)?|implemented\s+(?:the\s+)?|'
        r'signed\s+(?:a\s+)?(?:partnership|agreement|MoU)|'
        r'hosted\s+(?:the\s+)?(?:first|global|international))',
        re.IGNORECASE
    )

    for sent_raw in sentences:
        if len(achievements) >= 25:
            break
        sent = re.sub(r'\s+', ' ', sent_raw).strip()
        if len(sent) < 30 or len(sent) > 500:
            continue
        if not achievement_kw.search(sent):
            continue

        # Filter OUT ranking/index sentences
        if _is_ranking_sentence(sent):
            continue

        # Filter out footnote references, pure citations, page headers, URLs
        if re.match(r'^\d+\s*["""]', sent) or re.match(r'^\d+\s*https?://', sent):
            continue
        if re.match(r'^###\s+Page\s+\d+', sent) or '### Page' in sent:
            continue
        if re.match(r'^\d+[A-Z]', sent) and 'https://' in sent:
            continue  # footnote with URL
        if sent.startswith('http') or re.match(r'^[\dA-Z]+\s+https?://', sent):
            continue
        # Filter out reference-style entries (journal citations, footnotes)
        if re.search(r'(?:Observer|Today|Pulse|Times),\s*"', sent):
            continue
        # Filter out sentences that are primarily about indices/rankings even without specific index name
        if re.search(r'\b(?:international\s+(?:AI\s+)?(?:rank|indices|index)|ranks?\s+\d+(?:st|nd|rd|th)\s+(?:overall|globally|worldwide))\b', sent, re.IGNORECASE):
            continue
        # Filter out sentences about gaps/needs/recommendations (not achievements)
        if re.search(r'\brequires?\s+updates?\b|\bneeds?\s+(?:to|for)\b|\bmust\s+be\b|\bmust\s+collaborate\b|\bit\s+is\s+vital\b', sent, re.IGNORECASE):
            continue
        # Filter out generic/aspirational sentences
        if re.search(r'\bcan\s+create\b|\bcan\s+inadvertently\b|\bto\s+address\s+these\b|\btargeted\s+strategies\s+must\b', sent, re.IGNORECASE):
            continue
        # Filter out timeline/priority markers from recommendations
        if re.match(r'^Timeline:\s+\d{4}', sent):
            continue
        # Filter Roman numerals or page artifacts
        if re.match(r'^[IVXLCDM]+\s+###', sent) or re.match(r'^LI[VX]?\s', sent):
            continue

        key = sent[:60].lower()
        if key not in seen:
            seen.add(key)
            dim = "overall"
            lower = sent.lower()
            if any(w in lower for w in ['legal', 'law', 'regulation', 'juridique']):
                dim = "legal_regulatory"
            elif any(w in lower for w in ['education', 'research', 'university', 'scientific']):
                dim = "scientific_educational"
            elif any(w in lower for w in ['economic', 'investment', 'startup', 'gdp']):
                dim = "economic"
            elif any(w in lower for w in ['infrastructure', 'internet', 'broadband', 'data center']):
                dim = "technological_infrastructural"
            elif any(w in lower for w in ['social', 'cultural', 'gender', 'inclusion']):
                dim = "social_cultural"

            achievements.append({"achievement": sent, "dimension": dim})

    return achievements


def _extract_key_numbers(full_text):
    """Extract key numerical indicators from the full report text."""
    numbers = []
    seen = set()

    patterns = [
        # Internet/broadband penetration
        (r'(?:internet|broadband|mobile)\s+(?:penetration|access|connectivity)[^.]{0,30}?(\d+(?:\.\d+)?)\s*%',
         lambda m: {"label": "Internet Penetration", "value": float(m.group(1)), "unit": "%",
                     "dimension": "technological_infrastructural"}),
        # R&D spending
        (r'(?:R&D|GERD|research.{0,20}development)\s+[^.]{0,30}?(\d+(?:\.\d+)?)\s*%\s*(?:of\s+)?GDP',
         lambda m: {"label": "R&D Spending (% GDP)", "value": float(m.group(1)), "unit": "% GDP",
                     "dimension": "economic"}),
        # AI companies/startups
        (r'(\d+)\s+AI\s+(?:startups?|companies|firms)',
         lambda m: {"label": "AI Companies", "value": int(m.group(1)), "unit": "count",
                     "dimension": "economic"}),
        # AI publications
        (r'(\d[\d,]+)\s+(?:AI\s+)?(?:research\s+)?publications?',
         lambda m: {"label": "AI Publications", "value": int(m.group(1).replace(',', '')), "unit": "count",
                     "dimension": "scientific_educational"}),
        # GDP
        (r'GDP\s+(?:of\s+)?(?:approximately\s+)?(?:\$|USD)?\s*(\d+(?:\.\d+)?)\s*(billion|trillion)',
         lambda m: {"label": "GDP", "value": float(m.group(1)), "unit": m.group(2),
                     "dimension": "economic"}),
        # Population
        (r'population\s+(?:of\s+)?(?:approximately\s+)?(\d+(?:\.\d+)?)\s*(million|billion)',
         lambda m: {"label": "Population", "value": float(m.group(1)), "unit": m.group(2),
                     "dimension": "overall"}),
    ]

    for pat, builder in patterns:
        for m in re.finditer(pat, full_text, re.IGNORECASE):
            try:
                entry = builder(m)
                key = entry["label"]
                if key not in seen:
                    seen.add(key)
                    numbers.append(entry)
            except (ValueError, IndexError):
                continue

    return numbers


def extract_structured_dimensions(full_text, language="en"):
    """Main function: extract structured per-dimension data from full text.
    Returns (dimensions_dict, achievements, key_numbers, rankings_indices).
    """
    sections = _find_dimension_sections(full_text)

    dimensions = {}
    for dim_key in DIMENSION_PATTERNS:
        section_text = sections.get(dim_key, "")
        if not section_text:
            dimensions[dim_key] = {
                "title": DIMENSION_TITLES[dim_key],
                "findings": [], "strengths": [], "gaps": [],
                "key_stats": [],
            }
            if dim_key == "legal_regulatory":
                dimensions[dim_key]["regulations"] = []
            continue

        findings, strengths, gaps = _extract_strengths_gaps_findings(section_text, language)
        key_stats = _extract_key_stats(section_text)

        dim_data = {
            "title": DIMENSION_TITLES[dim_key],
            "findings": findings,
            "strengths": strengths,
            "gaps": gaps,
            "key_stats": key_stats,
        }

        if dim_key == "legal_regulatory":
            dim_data["regulations"] = _extract_regulations(section_text)

        dimensions[dim_key] = dim_data

    achievements = _extract_achievements(full_text)
    key_numbers = _extract_key_numbers(full_text)
    rankings_indices = _extract_rankings_indices(full_text)

    return dimensions, achievements, key_numbers, rankings_indices


###############################################################################
# END: Dimension-level structured extraction
###############################################################################


def generate_full_text_md(country_code, metadata, pages, chapters, recommendations):
    """Generate a full-text markdown file for RAG/search."""
    lines = []
    lines.append(f"# UNESCO RAM Report: {metadata.get('country_name', country_code)}")
    lines.append(f"\nPages: {metadata['page_count']}")
    lines.append(f"Country Code: {country_code}")
    lines.append("")
    
    lines.append("## Structure")
    for ch in chapters:
        lines.append(f"- Chapter {ch['chapter']}: {ch['title']} (p.{ch['start_page']})")
    lines.append("")
    
    lines.append("## Recommendations")
    for rec in recommendations:
        lines.append(f"\n### Recommendation {rec['number']}: {rec['title']}")
        preview = rec.get('text', '')[:500].strip()
        if preview:
            lines.append(preview)
    lines.append("")
    
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
    
    print("📝 Extracting text...")
    pages = extract_full_text(doc)
    
    print("🌐 Detecting language...")
    language = detect_language(pages)
    print(f"   Language: {language}")
    
    print("🔍 Detecting metadata...")
    metadata = extract_metadata(doc, pages)
    metadata["language"] = language
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
        title_preview = rec['title'][:80] if rec.get('title') else '(untitled)'
        print(f"   #{rec['number']}: {title_preview}")
    
    print("📝 Extracting executive summary...")
    exec_summary = extract_executive_summary(pages, language)
    print(f"   Length: {len(exec_summary)} chars")
    
    print("🔬 Extracting structured dimension data...")
    full_text = get_full_text(pages)
    structured_dims, achievements, key_numbers, rankings_indices = extract_structured_dimensions(full_text, language)
    for dk, dv in structured_dims.items():
        n_f = len(dv.get("findings", []))
        n_s = len(dv.get("strengths", []))
        n_g = len(dv.get("gaps", []))
        n_st = len(dv.get("key_stats", []))
        n_r = len(dv.get("regulations", []))
        extras = f", {n_r} regulations" if "regulations" in dv else ""
        print(f"   ✓ {dv['title']}: {n_f} findings, {n_s} strengths, {n_g} gaps, {n_st} stats{extras}")
    print(f"   🏆 {len(achievements)} achievements, 📊 {len(key_numbers)} key numbers, 📈 {len(rankings_indices)} rankings")
    
    # Build output JSON
    output = {
        "country_code": country_code,
        "country_name": metadata.get("country_name", country_code),
        "language": language,
        "metadata": metadata,
        "chapters": chapters,
        "dimensions": dimensions,
        "structured_dimensions": structured_dims,
        "achievements": achievements,
        "key_numbers": key_numbers,
        "rankings_indices": rankings_indices,
        "executive_summary": exec_summary[:5000],
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


def enrich_from_fulltext():
    """Standalone mode: enrich existing extracted JSONs using full_text.md files.
    Usage: python extract_ram_pdf.py --enrich <country_code> [--output-dir <dir>]
           python extract_ram_pdf.py --enrich-all [--output-dir <dir>]
    """
    output_dir = "."
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        output_dir = sys.argv[idx + 1]

    if "--enrich-all" in sys.argv:
        # Find all full_text.md files
        codes = []
        for f in sorted(Path(output_dir).glob("*_full_text.md")):
            cc = f.stem.replace("_full_text", "").upper()
            codes.append(cc)
    else:
        idx = sys.argv.index("--enrich")
        codes = [sys.argv[idx + 1].upper()]

    for country_code in codes:
        md_path = os.path.join(output_dir, f"{country_code.lower()}_full_text.md")
        json_path = os.path.join(output_dir, f"{country_code.lower()}_extracted.json")

        if not os.path.exists(md_path):
            print(f"⚠ {md_path} not found, skipping {country_code}")
            continue

        print(f"\n📄 Enriching {country_code} from {md_path}...")

        # Read full text (skip the header/structure section, get raw text after "## Full Text")
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use everything (the dimension headers appear in both summary and full text sections)
        full_text = content

        # Detect language
        sample = full_text[:5000].lower()
        fr_count = sum(1 for m in ["recommandation", "chapitre", "résumé", "éthique", "intelligence artificielle"]
                       if m in sample)
        pt_count = sum(1 for m in ["recomendação", "inteligência artificial", "estratégia", "governação"]
                       if m in sample)
        language = "fr" if fr_count >= 3 else ("pt" if pt_count >= 3 else "en")

        structured_dims, achievements, key_numbers, rankings_indices = extract_structured_dimensions(full_text, language)

        for dk, dv in structured_dims.items():
            n_f = len(dv.get("findings", []))
            n_s = len(dv.get("strengths", []))
            n_g = len(dv.get("gaps", []))
            n_st = len(dv.get("key_stats", []))
            n_r = len(dv.get("regulations", []))
            extras = f", {n_r} regs" if "regulations" in dv else ""
            print(f"   ✓ {dv['title']}: {n_f}F/{n_s}S/{n_g}G/{n_st}St{extras}")
        print(f"   🏆 {len(achievements)} achievements, 📊 {len(key_numbers)} key numbers, 📈 {len(rankings_indices)} rankings")

        # Load existing JSON and merge
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"country_code": country_code}

        data["structured_dimensions"] = structured_dims
        data["achievements"] = achievements
        data["key_numbers"] = key_numbers
        data["rankings_indices"] = rankings_indices

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Saved: {json_path}")

    print("\n🎯 Enrichment complete!")


if __name__ == "__main__":
    if "--enrich" in sys.argv or "--enrich-all" in sys.argv:
        enrich_from_fulltext()
    else:
        main()
