from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.browserbase import BrowserbaseTools
from agno.tools.youtube import YouTubeTools
from agno.tools.website import WebsiteTools 
from agno.tools.csv_toolkit import CsvTools
from agno.tools.file import FileTools
from agno.tools.calculator import CalculatorTools
from agno.tools.arxiv import ArxivTools

TOOLS = {
    'duckduckgo': DuckDuckGoTools(), 
    'wikipedia': WikipediaTools(),
    'browser': BrowserbaseTools(),
    'youtube': YouTubeTools(),
    'website': WebsiteTools(), 
    'csv': CsvTools(),
    'file': FileTools(),
    'calculator': CalculatorTools(),
    'arxiv': ArxivTools(),
}
