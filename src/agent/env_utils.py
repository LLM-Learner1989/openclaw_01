import os

from dotenv import load_dotenv

# override=True 确保.env文件优先
load_dotenv(override=True)

# 从环境变量读取配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE")

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")

OPEN_SANDBOX_BASE_URL = os.getenv("OPEN_SANDBOX_BASE_URL")
