import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Flask(__name__)
@app.route('/')
def home():
    return "监听机器人运行中！"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🟢 收到 /start 指令！来自用户 ID: {update.effective_user.id}")
    await update.message.reply_text(
        "🤖 回复测试成功！\n\n"
        "你现在可以私聊发：\n"
        "/addkeyword 测试"
    )

async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"🟢 收到添加关键词指令！用户ID: {update.effective_user.id}")
    if not context.args:
        await update.message.reply_text("❌ 格式错误。示例：/addkeyword 杭州")
        return
    word = " ".join(context.args)
    await update.message.reply_text(f"✅ 已成功添加监听词：{word}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addkeyword", add_keyword))
    logging.info("✅ 纯净测试版已启动！")
    application.run_polling()

if __name__ == "__main__":
    main()
