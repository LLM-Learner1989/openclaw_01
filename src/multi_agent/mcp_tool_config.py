from langchain_mcp_adapters.client import MultiServerMCPClient

# 数据分析报表的MCP服务端（工具的配置）
analysis_mcp_server_config = {
    "url": "https://mcp.api-inference.modelscope.net/fe48341e18ef4c/mcp",
    "transport": "streamable_http",
}

# 创建一个mcp的客户端
mcp_client = MultiServerMCPClient({
    "fenxi": analysis_mcp_server_config,
})
