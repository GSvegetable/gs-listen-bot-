import os

# 从 Railway 的环境变量里读取（以后换客户直接改变量，不用改代码）
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ⚠️ 只有你的这两个账号才能操控这个机器人（发指令、收监听）
ADMIN_IDS = [7857605443, 7867520461]
