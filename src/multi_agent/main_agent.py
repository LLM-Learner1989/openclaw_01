import asyncio
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
import yaml

from multi_agent.mcp_tool_config import mcp_client
from agent.my_llm import llm
from agent.my_tools import web_search

EXAMPLE_DIR = Path(__file__).parent
print(f'当前代码执行的工作目录为：{EXAMPLE_DIR}')


async def load_subagents(config_path: str):
    """通过读取配置文件，加载子Agent"""
    # 将工具名称映射到实际工具对象
    # xsct_tools = await mcp_client.get_tools(server_name="xsct")
    chart_tools = await mcp_client.get_tools(server_name="fenxi")
    # print(xsct_tools)
    available_tools = {
        # "xsct": xsct_tools,
        "fenxi": chart_tools,
        "web_search": [web_search],
    }

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    subagents = []
    for name, spec in config.items():
        subagent = {
            "name": name,
            "description": spec["description"],
            "system_prompt": spec["system_prompt"],
        }
        if "model" in spec:
            subagent["model"] = spec["model"]
        if "tools" in spec:
            tools = [available_tools[t] for t in spec["tools"]]
            print(tools)
            subagent["tools"] = tools[0]

        # subagent['middleware'] = ToolCallLimitMiddleware(tool_name="execute_python", run_limit=3) # 限制代码执行最多3次
        subagents.append(subagent)
    return subagents


async def crete():
    sub_agent = await load_subagents(EXAMPLE_DIR / 'subagents.yaml')
    return create_deep_agent(  # create_agent
        model=llm,
        memory=['/AGENTS.md'],  # 由MemoryMiddleware加载, 主Agent的系统提示词
        tools=[web_search],
        backend=FilesystemBackend(root_dir=EXAMPLE_DIR, virtual_mode=True),
        subagents=sub_agent,
    )


agent = asyncio.run(crete())
