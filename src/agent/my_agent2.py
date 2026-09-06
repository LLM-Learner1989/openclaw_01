"""
删掉 checkpointer=checkpointer, langgraph dev 自动管理持久化
"""

import os

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend

from agent.my_llm import llm
from agent.my_tools import web_search

# 创建一个临时目录作为 Agent 的 “沙盒”
temp_workspace = "./agent_workspace"
os.makedirs(temp_workspace, exist_ok=True)

agent = create_deep_agent(
    model=llm,
    tools=[web_search],
    backend=FilesystemBackend(
        root_dir=temp_workspace,
        virtual_mode=True  # 关键！防止Agent使用 `../../` 跳出跟目录
    ),
    system_prompt='你是一个助手，请根据用户输入的指令，进行相应的操作。'
)
