import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from typing import Dict
import logging, json

async def crawl_content_async(start_url: str, titles: bool = True, paragraphs: bool = False, 
                            code: bool = True, tables: bool = True, max_requests: int = 5, 
                            headless: bool = False) -> Dict:
    """
    Asynchronously crawl a website and extract specified content.
    Uses the current event loop (no manual loop management).
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

    results_dict = {}
    visited_urls = set()
    processed_count = 0
    
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext):
        nonlocal processed_count
        url = context.request.url

        if url in visited_urls:
            return
        
        processed_count += 1
        visited_urls.add(url)
        
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

def crawl_content(start_url: str, titles: bool = True, paragraphs: bool = False, 
                 code: bool = True, tables: bool = True, max_requests: int = 5, 
                 headless: bool = True) -> Dict:
    """
    Synchronous wrapper for crawling a website.
    Uses asyncio.run() to manage the event loop properly.
    """
    return asyncio.run(
        crawl_content_async(start_url, titles, paragraphs, code, tables, max_requests, headless)
    )

if __name__ == "__main__":
    TEST_URL = "https://ai.google.dev/gemini-api/docs/document-processing?lang=python"
    
    # Test sync version multiple times
    for i in range(2):
        print(f"\nRun {i + 1}:")
        sync_result = crawl_content(
            start_url=TEST_URL,
            titles=True,
            paragraphs=True,
            code=True,
            tables=True,
            max_requests=3,
            headless=True
        )
        print("\nSync Crawler Results:")
        print(json.dumps(sync_result, indent=2))
    
    print("\nTest completed!")