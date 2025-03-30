from mas.tool.pool import ToolPool
ToolPool.initialize()

from mas.tool.tools.urlreader import read_url  # Import after initialization

#result = read_url("https://platform.openai.com/docs/guides/pdf-files?api-mode=chat") # failed to crawl Client error '403 forbidden'
url = 'https://www.zhenhunxiaoshuo.com/5719.html'
result = read_url(url)
print(result)