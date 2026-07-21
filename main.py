import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from config import BOT_TOKEN, ADMIN_IDS
from db import init_db, add_keyword, remove_keyword, get_all_keywords

# 初始化数据库
init_db()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ================= 保活网页 =================
app = Flask(__name__)
@app.route('/')
def home():
    return "监听机器人运行中！"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ================= 管理员指令 =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return  # 陌生人私聊直接无视
    await update.message.reply_text(
        "🤖 关键词监听机器人已启动。\n\n"
        "常用指令：\n"
        "/addkeyword 词 - 添加监听词\n"
        "/delkeyword 词 - 删除监听词\n"
        "/listkeyword - 查看当前所有监听词"
    )

async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("❌ 格式错误。示例：/addkeyword 杭州")
        return
    word = " ".join(context.args)
    add_keyword(word)
    await update.message.reply_text(f"✅ 已成功添加监听词：{word}")

async def del_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    if not context.args:
        await update.message.reply_text("❌ 格式错误。示例：/delkeyword 杭州")
        return
    word = " ".join(context.args)
    if remove_keyword(word):
        await update.message.reply_text(f"✅ 已删除监听词：{word}")
    else:
        await update.message.reply_text(f"❌ 关键词 {word} 不存在。")

async def list_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS: return
    words = get_all_keywords()
    if not words:
        await update.message.reply_text("📭 当前还没有任何监听关键词。")
        return
    await update.message.reply_text("📋 当前监听关键词列表：\n\n" + "\n".join(words))

# ================= 群组监听核心逻辑 =================
async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 只有群聊消息才会被处理
    if update.message.chat.type not in ['group', 'supergroup']:
        return

    user_id = update.effective_user.id
    text = update.message.text
    if not text:
        return

    keywords = get_all_keywords()
    if not keywords:
        return

    # 检测消息是否包含任何关键词
    matched = False
    for kw in keywords:
        if kw in text:
            matched = True
            break

    if matched:
        chat_title = update.message.chat.title or f"群组{update.message.chat.id}"
        username = update.effective_user.username or f"用户{user_id}"
        alert_msg = (
            f"🚨 **群聊关键词触发**\n"
            f"📍 来源群：{chat_title}\n"
            f"👤 发送者：@{username}\n"
            f"💬 消息内容：{text}"
        )
        # 将监听结果私信发给所有管理员
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=admin_id, text=alert_msg, parse_mode='Markdown')
            except:
                pass

# ================= 启动机器人 =================
def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addkeyword", add_keyword))
    application.add_handler(CommandHandler("delkeyword", del_keyword))
    application.add_handler(CommandHandler("listkeyword", list_keywords))
    
    # 只监听群聊里的文字消息
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, handle_group_message))

    logging.info("✅ 监听机器人已上线！")
    application.run_polling()

if __name__ == "__main__":
    main()
