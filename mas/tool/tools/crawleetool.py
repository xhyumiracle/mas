import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from mas.tool.pool import ToolPool
from typing import Dict
from openai import OpenAI
import logging, json


async def crawl_content_async(start_url: str, titles: bool = True, paragraphs: bool = False, 
                             code: bool = True, tables: bool = True, max_requests: int = 5, 
                             headless: bool = False) -> Dict:
    """
    Asynchronously crawl a website and extract specified content.
    
    Args:
        start_url (str): The starting URL to crawl.
        titles (bool): Whether to extract page titles.
        paragraphs (bool): Whether to extract paragraph text.
        extract_code (bool): Whether to extract code blocks.
        tables (bool): Whether to extract table data.
        max_requests (int): Maximum number of pages to crawl.
        headless (bool): Whether to run the browser in headless mode.
    
    Returns:
        dict: A dictionary with URLs as keys and extracted data/output as values.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if not start_url:
        raise ValueError("No start_url provided")

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=max_requests,
        headless=headless,
        browser_type='firefox',
    )

    # Dictionary to store results with URL as key
    results_dict = {}
    # Set to track visited URLs
    visited_urls = set()
    processed_count = 0
    
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext):
        nonlocal processed_count
        url = context.request.url

        # Skip if URL already visited
        if url in visited_urls:
            return
        
        processed_count += 1
        visited_urls.add(url)
        
        # Initialize data and output for this URL
        data = {'url': url}
        output_lines = []

        try:
            await context.page.wait_for_load_state('networkidle')

            if titles:
                data['title'] = await context.page.title()
                output_lines.append(f"Title: {data['title']}")

            if paragraphs:
                paragraphs_list = await context.page.locator('p').all_text_contents()
                data['paragraphs'] = [p.strip() for p in paragraphs_list if p.strip()]
                output_lines.append("\nParagraphs:")
                output_lines.append("  None found" if not data['paragraphs'] else "")
                for i, para in enumerate(data['paragraphs'], 1):
                    output_lines.append(f"  {i}. {para}")

            if code:
                code_elements = await context.page.locator('pre:has(code)').all()
                code_blocks = []
                for element in code_elements:
                    code_content = await element.locator('code').text_content()
                    if code_content:
                        code_blocks.append(code_content.strip())
                data['code_blocks'] = code_blocks
                output_lines.append("\nCode Blocks:")
                output_lines.append("  None found" if not code_blocks else "")
                for i, block in enumerate(code_blocks, 1):
                    output_lines.append(f"  {i}. ```\n      {block}\n      ```")

            if tables:
                table_elements = await context.page.locator('table').all()
                tables_data = []
                for table in table_elements:
                    rows = await table.locator('tr').all()
                    table_content = []
                    for row in rows:
                        cells = await row.locator('td, th').all()
                        row_data = [await cell.text_content() for cell in cells if await cell.text_content()]
                        row_data = [cell.strip() for cell in row_data if cell.strip()]
                        if row_data:
                            table_content.append(row_data)
                    if table_content:
                        tables_data.append(table_content)
                data['tables'] = tables_data
                output_lines.append("\nTables:")
                output_lines.append("  None found" if not tables_data else "")
                for i, table in enumerate(tables_data, 1):
                    output_lines.append(f"  Table {i}:")
                    for row in table:
                        output_lines.append(f"    {' | '.join(row)}")

            # Store data and output for this URL
            results_dict[url] = {
                'data': data,
                'output': output_lines
            }

            if processed_count < max_requests:
                await context.enqueue_links()
            await context.push_data(data)

        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            results_dict[url] = {
                'data': data,
                'output': [f"Error processing {url}: {str(e)}"]
            }

    logger.info(f"Starting crawl from: {start_url}")
    logger.info(f"Maximum requests allowed: {max_requests}")
    await crawler.run([start_url])
    
    dataset = await crawler.get_data()
    logger.info("Crawl completed!")
    logger.info(f"Total unique pages processed: {len(results_dict)}")
    logger.info(f"Total pages attempted: {processed_count}")
    logger.info(f"Total items in dataset: {len(dataset.items)}")
    
    return results_dict


@ToolPool.register(
    name="crawlee",
    description="Read or crawl any website and extract specific content such as titles, code, paragraphs, or tables. Can handle both HTML and JavaScript."
)
def crawl_content(start_url: str, titles: bool = True, paragraphs: bool = False, 
                 code: bool = True, tables: bool = True, max_requests: int = 5, 
                 headless: bool = True) -> dict:
    """
    Read/crawl a website and extract specific content such as titles, code, paragraphs, or tables. Can handle both HTML and JavaScript.
    
    Args:
        start_url (str): The starting URL to crawl.
        titles (bool): Whether to extract page titles (default: True).
        paragraphs (bool): Whether to extract paragraph text (default: False).
        extract_code (bool): Whether to extract code blocks (default: True).
        tables (bool): Whether to extract table data (default: True).
        max_requests (int): Maximum number of pages to crawl (default: 5).
        headless (bool): Whether to run the browser in headless mode (default: True).
    
    Returns:
        dict: A dictionary with URLs as keys and extracted data/output as values.
    """
    return json.dumps(asyncio.run(crawl_content_async(start_url, titles, paragraphs, code, tables, max_requests, headless)))[0:10000]

