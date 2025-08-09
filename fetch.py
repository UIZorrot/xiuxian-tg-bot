#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速获取Telegram群组ID和话题ID的工具脚本
使用方法：
1. 运行此脚本
2. 将Bot添加到目标群组
3. 在群组中发送任意消息
4. 脚本会显示群组ID和话题ID信息
5. 按Ctrl+C停止脚本
"""

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 存储已显示的群组，避免重复输出
shown_groups = set()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理接收到的消息，显示群组和话题信息"""
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    
    if chat.type in ['group', 'supergroup']:
        # 构建唯一标识
        thread_id = getattr(message, 'message_thread_id', None)
        group_key = (chat.id, thread_id)
        
        if group_key not in shown_groups:
            shown_groups.add(group_key)
            
            print("\n" + "="*60)
            print(f"📱 群组信息检测到！")
            print(f"群组名称: {chat.title}")
            print(f"群组ID: {chat.id}")
            
            if thread_id:
                print(f"话题ID: {thread_id}")
                print(f"\n📋 配置代码 (有话题):")
                print(f"ALLOWED_CHANNELS = {{")
                print(f"    {chat.id}: [{thread_id}]")
                print(f"}}")
                print(f"\nGAME_CHANNELS = {{")
                print(f"    {chat.id}: [{thread_id}]")
                print(f"}}")
            else:
                print(f"话题ID: 无 (普通群组)")
                print(f"\n📋 配置代码 (无话题):")
                print(f"ALLOWED_CHANNELS = {{")
                print(f"    {chat.id}: [0]  # 0表示整个群组")
                print(f"}}")
                print(f"\nGAME_CHANNELS = {{")
                print(f"    {chat.id}: [0]  # 0表示整个群组")
                print(f"}}")
            
            print(f"\n👤 触发用户: {user.first_name} (@{user.username})")
            print(f"💬 消息内容: {message.text[:50]}{'...' if len(message.text or '') > 50 else ''}")
            print("="*60)
    
    elif chat.type == 'private':
        await update.message.reply_text(
            "🤖 群组ID获取工具\n\n"
            "请将我添加到你想要配置的群组中，然后在群组里发送任意消息。\n\n"
            "我会自动显示群组ID和话题ID信息，方便你配置config.py文件。\n\n"
            "💡 提示：如果群组开启了话题功能，请在具体话题中发送消息。"
        )

def main():
    """主函数"""
    print("🚀 启动群组ID获取工具...")
    print(f"🤖 Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-10:]}")
    print("\n📝 使用说明:")
    print("1. 将Bot添加到目标群组")
    print("2. 在群组中发送任意消息")
    print("3. 查看控制台输出的群组ID信息")
    print("4. 复制配置代码到config.py")
    print("5. 按Ctrl+C停止工具")
    print("\n⏳ 等待群组消息...\n")
    
    # 创建应用
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.ALL, message_handler))
    
    try:
        # 启动Bot
        application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n\n👋 工具已停止，感谢使用！")
        print("\n💡 记得将获取到的群组ID配置到config.py文件中哦~")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("\n🔧 请检查:")
        print("1. Bot Token是否正确")
        print("2. 网络连接是否正常")
        print("3. Bot是否已创建并启用")

if __name__ == "__main__":
    main()