import json
from typing import List
import wikipedia
from bs4 import BeautifulSoup
import re
from mas.tool.pool import ToolPool
import logging

logger = logging.getLogger(__name__)

def fetch_wikipedia_clean(titles: List[str], lang: str = "en") -> dict:
    wikipedia.set_lang(lang)

    last_exception = None
    for title in titles:
        logger.info(f"Searching wikipedia for: {title}")
        try:
            page = wikipedia.page(title, auto_suggest=False, redirect=True)
            html = page.html()
            break
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
            logger.warning(f"Failed to search wikipedia for: {title}, retrying...")
            last_exception = e
    if last_exception:
        raise last_exception
    
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'sup', 'img']):
        tag.decompose()

    # ===== INFObox =====
    infobox = soup.find('table', {'class': 'infobox'})
    infobox_text = _clean_table(infobox) if infobox else ""
    if infobox: infobox.decompose()

    # ===== Main Sections =====
    sections = []
    current_heading = "Introduction"
    current_content = []

    for tag in soup.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
        if tag.name in ['h2', 'h3']:
            if current_content:
                sections.append({"heading": current_heading, "text": "\n".join(current_content).strip()})
                current_content = []
            current_heading = tag.get_text(strip=True)
        else:
            text = tag.get_text(strip=True)
            if text:
                current_content.append(re.sub(r'\s+', ' ', text))
    if current_content:
        sections.append({"heading": current_heading, "text": "\n".join(current_content).strip()})

    # ===== All Wikitable =====
    tables = []
    for table in soup.find_all('table', {'class': 'wikitable'}):
        heading = _find_previous_heading(table)
        rows = []
        for row in table.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            rows.append([col.get_text(strip=True) for col in cols])
        if rows:
            tables.append({"section": heading or "Unknown", "rows": rows})

    return {
        "title": title,
        "url": page.url,
        "infobox": infobox_text.strip(),
        "sections": sections,
        "tables": tables
    }

def _clean_table(table):
    if not table: return ""
    rows = []
    for row in table.find_all('tr'):
        cols = row.find_all(['th', 'td'])
        line = " | ".join(col.get_text(strip=True) for col in cols)
        if line:
            rows.append(line)
    return "\n".join(rows)

def _find_previous_heading(tag):
    while tag:
        tag = tag.find_previous()
        if tag and tag.name in ['h2', 'h3']:
            return tag.get_text(strip=True)
    return None

@ToolPool.register(
    name="wikipedia_search_text",
    description="Searches Wikipedia for a given topic. Use carefully, only when necessary. Truncated by [0:10000]" #  and returns the cleaned text-only content as a dictionary.
)
def wikipedia_search_text(query: str, lang: str = "en") -> str:
    titles = wikipedia.search(query, results=3, suggestion=False)
    return json.dumps(fetch_wikipedia_clean(titles, lang))[:10000]