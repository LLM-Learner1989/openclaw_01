import os
import sys

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, LocalShellBackend
from langgraph.checkpoint.memory import InMemorySaver

from agent.my_llm import llm
from agent.my_tools import web_search

checkpointer = InMemorySaver()

# 创建一个临时目录作为代理的“沙盒”
temp_workspace = "./agent_workspace"
os.makedirs(temp_workspace, exist_ok=True)

agent = create_deep_agent(  # create_agent
    model=llm,
    tools=[web_search],
    checkpointer=checkpointer,
    backend=LocalShellBackend(
        root_dir=temp_workspace,
        virtual_mode=True,  # 防止Agent，通过`../../` 跳出跟目录
        timeout=30,  # 命令执行超时时间（秒）
        max_output_bytes=50000,  # 命令输出最大字节数
        # 设置环境变量，包含编码相关的配置
        env={
            # 获取当前Python解释器的完整路径
            "PATH": f"{os.path.dirname(sys.executable)};{os.environ.get('PATH', '')}",
        },
    ),
    system_prompt='你是一个助手，请根据用户输入的指令，进行相应的操作。'
)