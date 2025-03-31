import requests
from bs4 import BeautifulSoup
from mas.tool.pool import ToolPool

@ToolPool.register(
    name="urlreader",
    description="Reads the content of a given URL and extracts the main text from the webpage. Only retrieves text from html content and does not work for javascript."
)
def fetch_url(url: str, timeout: int = 10, headers: dict = None) -> str:
    """
    Fetch and extract the main content from a webpage, including text from paragraphs, headings, tables, and buttons.

    Args:
        url (str): The URL of the webpage to fetch.
        timeout (int, optional): Timeout for the request in seconds. Default is 10.
        headers (dict, optional): Custom headers for the request. Default is a basic User-Agent.

    Returns:
        str: Extracted main content from the webpage, or an error message if failed.
    """
    headers = headers or {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove unwanted elements (scripts, styles, nav, header, footer)
        for unwanted in soup(["script", "style", "nav", "header", "footer"]):
            unwanted.decompose()

        # Look for main content in common tags
        main_content = None
        for tag in ["article", "main"]:
            main_content = soup.find(tag)
            if main_content:
                break

        # If no <article> or <main>, look for divs with common content classes/IDs
        if not main_content:
            for class_name in ["content", "main-content", "article-content", "post", "entry-content"]:
                main_content = soup.find("div", class_=class_name)
                if main_content:
                    break

        # Fallback: Use the body and filter out remaining unwanted sections
        if not main_content:
            main_content = soup.find("body")
            if main_content:
                for aside in main_content.find_all("aside"):
                    aside.decompose()
                for div in main_content.find_all("div", class_=["sidebar", "menu", "widget"]):
                    div.decompose()

        if not main_content:
            return "No main content found."

        # Extract text from relevant elements
        elements = main_content.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "button"])
        paragraphs = [elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)]
        
        # Format text with paragraph breaks
        text = "\n".join(paragraphs)
        
        # Limit content length (e.g., 2000 chars)
        return text
    except Exception as e:
        print(f"Failed to fetch content from {url}: {str(e)}")
        return f"Error fetching content: {str(e)}"

'''
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Mercedes_Sosa"
    content = fetch_url(url)
    print(content)
'''