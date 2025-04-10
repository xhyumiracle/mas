import json
import logging
from typing import List, Dict, Optional
import pycountry
from googlesearch import search
from langdetect import detect, DetectorFactory
from mas.tool.base import Toolkit
# Ensure consistent language detection
DetectorFactory.seed = 0

# Set up logging
logger = logging.getLogger(__name__)

class GoogleSearchTool(Toolkit):
    def __init__(self):
        super().__init__(
            name="google_search",
            description="Performs Google Search to retrieve real time information. Returns a list of search results, including their titles, URLs, and descriptions.",
            tools=[self.google_search]
        )

    @staticmethod
    def google_search(query: str, max_results: int = 5, language: Optional[str] = None, proxy: Optional[str] = None) -> str:
        """
        Searches Google for a specified query.

        Args:
            query (str): The query to search for.
            max_results (int, optional): The maximum number of results to return. Default is 5.
            language (Optional[str], optional): The language of the search results. If None, it will be auto-detected.
            proxy (Optional[str], optional): Proxy settings for the request.

        Returns:
            str: A JSON formatted string containing the search results.
        """
        # Auto-detect language if not provided
        if language is None:
            try:
                detected_lang = detect(query)  # Detect language from query
                if len(detected_lang) == 2:
                    language = detected_lang
                else:
                    language = "en"
            except:
                language = "en"  # Default to English if detection fails

        # Ensure language is in ISO 639-1 format
        if len(language) != 2:
            _language = pycountry.languages.get(name=language)
            language = _language.alpha_2 if _language else "en"

        logger.debug(f"Detected language: {language}. Searching Google for: {query}")

        # Perform Google search
        results = list(search(query, num_results=max_results, lang=language, proxy=proxy, advanced=True))

        # Collect the search results
        res: List[Dict[str, str]] = [{"title": r.title, "url": r.url, "description": r.description} for r in results]

        return json.dumps(res, indent=2)

