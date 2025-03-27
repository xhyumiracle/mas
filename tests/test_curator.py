def test_tool_curator():
    from mas.curator.tool_curator import ToolCurator
    tool_curator = ToolCurator()
    tools = ["duckduckgo", "google_search", "duckduckgo", "wikipedia"]
    curated_tools = tool_curator.curate_tools(tools)
    assert set(curated_tools) == set(["duckduckgo", "google_search", "wikipedia"])