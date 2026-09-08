import asyncio
from pathlib import Path

from deepagents import create_deep_agent
import yaml

from multi_agent.mcp_tool_config import mcp_client
from agent.my_llm import llm
from agent.my_tools import web_search
from sandbox.custom_opensandbox import OpenSandboxBackend
from sandbox.opensandbox_opt import get_or_create_sandbox, config, sync_skills_to_sandbox

EXAMPLE_DIR = Path(__file__).parent
print(f'当前代码执行的工作目录为：{EXAMPLE_DIR}')


async def load_subagents(config_path: str):
    """通过读取配置文件，加载子Agent"""

    # 将工具名称映射到实际工具对象
    chart_tools = await mcp_client.get_tools(server_name="fenxi")

    available_tools = {
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
            subagent["tools"] = tools[0]

        # subagent['middleware'] = ToolCallLimitMiddleware(tool_name="execute_python", run_limit=3) # 限制代码执行最多3次
        subagents.append(subagent)
    return subagents


async def crete():
    sub_agent = await load_subagents(EXAMPLE_DIR / 'subagents.yaml')

    # 创建OpenSandbox 沙箱
    sandbox = get_or_create_sandbox(config)

    # 创建OpenSandbox后端
    backend = OpenSandboxBackend(sandbox=sandbox)

    # 本地技能目录
    local_skills_path = str(EXAMPLE_DIR / "skills")

    # 沙箱中的技能目录
    sandbox_skills_path = "/workspace/skills"

    # 智能同步技能到沙箱
    uploaded_count = sync_skills_to_sandbox(backend, local_skills_path, sandbox_skills_path)

    with open(str(EXAMPLE_DIR / "AGENTS.md"), 'r', encoding='utf-8') as f:
        content = f.read()

    # 上传到沙箱
    result = backend.upload_files([('/AGENTS.md', content.encode("utf-8"))])

    if uploaded_count > 0:
        print(f"✅ 成功上传了 {uploaded_count} 个新技能到沙箱")
    else:
        print("✅ 所有技能已存在于沙箱中，无需上传")

    return create_deep_agent(  # create_agent
        model=llm,
        skills=[sandbox_skills_path],
        memory=['/AGENTS.md'],  # 由MemoryMiddleware加载, 主Agent的系统提示词
        tools=[web_search],
        backend=backend,
        subagents=sub_agent,
    )


agent = asyncio.run(crete())
