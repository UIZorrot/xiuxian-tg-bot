#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修仙Telegram机器人 - 使用python-telegram-bot库重写
解决网络连接问题
"""

import os
import asyncio
import logging
from typing import Dict
import requests
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode

# 导入新的配置和数据库模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from config import (
    TELEGRAM_BOT_TOKEN, GAME_CHANNELS, ALLOWED_CHANNELS, 
    ALLOWED_ANN, WITHDRAW_ANN, LOG_LEVEL, LOG_FORMAT
)
from database import init_db, get_player, create_player, update_player
from xianxia_game import XianXiaGame
from weapon_enhancement import WeaponEnhancement

# 配置日志
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# 初始化游戏组件（数据库将在main函数中初始化）
xianxia_game = None
weapon_enhancement = WeaponEnhancement()

# 创建Application实例
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/start命令"""
    await update.message.reply_text("欢迎使用修仙机器人！\n\n发送 /xiuxian 开始你的修仙之旅！", parse_mode=ParseMode.HTML)

async def xiuxian_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/xiuxian命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        status = await xianxia_game.get_status(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        if status:
            response = (
                f"{status}\n\n"
                f"修仙指南: \n"
                f"/dazuo - 打坐修炼\n"
                f"/caiyao - 采集药材\n"
                f"/mine - 矿洞采矿\n"
                f"/elsevier - 爱思唯尔副本\n"
                f"/wuqi - 铁匠铺\n"
                f"/zahuo - 杂货铺\n"
                f"/maiwuqi - 购买武器\n"
                f"/zhuangbei - 装备武器\n"
                f"/qianghua - 强化武器\n"
                f"/check_weapon - 查看武器\n"
                f"/paihang - 排行榜\n"
                f"/status - 查看状态\n"
                f"/beibao - 查看背包\n"
            )
            
            # 尝试发送视频，如果失败则发送文本
            try:
                with open('./videos/xiuxian.mp4', 'rb') as video:
                    await message.reply_video(
                        video=video,
                        caption=response,
                        parse_mode=ParseMode.HTML
                    )
            except Exception as video_error:
                logger.warning(f"发送视频失败，改为发送文本: {video_error}")
                await message.reply_text(response, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text("获取状态失败,请稍后重试。")
    except Exception as e:
        logger.error(f"修仙命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def dazuo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/dazuo命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.meditate(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        if result:
            # 尝试发送视频，如果失败则发送文本
            try:
                with open('./videos/dazuo.mp4', 'rb') as video:
                    await message.reply_video(
                        video=video,
                        caption=result,
                        parse_mode=ParseMode.HTML
                    )
            except Exception as video_error:
                logger.warning(f"发送视频失败，改为发送文本: {video_error}")
                await message.reply_text(result, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text("打坐失败,请稍后重试。")
    except Exception as e:
        logger.error(f"打坐命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/status命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        status = await xianxia_game.get_status(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        if status:
            await message.reply_text(status, parse_mode=ParseMode.HTML)
        else:
            await message.reply_text("获取状态失败,请稍后重试。")
    except Exception as e:
        logger.error(f"状态命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def caiyao_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/caiyao命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.gather_herbs(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"采药命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def mine_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/mine命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.mine(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"挖矿命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def beibao_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/beibao命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.get_inventory(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"背包命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def paihang_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/paihang命令"""
    try:
        message = update.message
        
        result = await xianxia_game.get_leaderboard()
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"排行榜命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def maiwuqi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/maiwuqi命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        # 获取武器名称参数
        args = context.args
        if not args:
            await message.reply_text("请指定要购买的武器名称，例如：/maiwuqi 铁剑")
            return
            
        weapon_name = " ".join(args)
        result = await xianxia_game.buy_weapon(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            weapon_name=weapon_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"购买武器命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def zhuangbei_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/zhuangbei命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        # 获取武器名称参数
        args = context.args
        if not args:
            await message.reply_text("请指定要装备的武器名称，例如：/zhuangbei 铁剑")
            return
            
        weapon_name = " ".join(args)
        result = await xianxia_game.equip_weapon(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            weapon_name=weapon_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"装备武器命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def wuqi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/wuqi命令 - 查看武器列表"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.list_weapons(
            user_id=user.id,
            username=username,
            screen_name=full_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"武器列表命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def elsevier_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/elsevier命令"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        # 获取副本名称参数
        args = context.args
        stage_name = " ".join(args) if args else None
        
        result = await xianxia_game.challenge_elsevier(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            stage_name=stage_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"副本挑战命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def zahuo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/zahuo命令 - 杂货铺"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.visit_shop(
            user_id=user.id,
            username=username,
            screen_name=full_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"杂货铺命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def qianghua_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/qianghua命令 - 强化武器"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        # 获取武器名称参数
        args = context.args
        if not args:
            await message.reply_text("请指定要强化的武器名称，例如：/qianghua 铁剑")
            return
            
        weapon_name = " ".join(args)
        result = await xianxia_game.enhance_weapon(
            user_id=user.id,
            username=username,
            screen_name=full_name,
            weapon_name=weapon_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"强化武器命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

async def check_weapon_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/check_weapon命令 - 查看武器详情"""
    try:
        message = update.message
        user = message.from_user
        username = user.username or str(user.id)
        full_name = user.first_name
        if user.last_name:
            full_name += f" {user.last_name}"

        result = await xianxia_game.check_weapon(
            user_id=user.id,
            username=username,
            screen_name=full_name
        )
        
        await message.reply_text(result, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"查看武器命令处理错误: {e}", exc_info=True)
        await message.reply_text(f"发生错误: {str(e)}")

def main():
    """主函数"""
    try:
        print("[DEBUG] 程序开始启动...")
        logger.info("启动机器人...")
        
        # 初始化数据库（同步方式）
        print("[DEBUG] 初始化数据库...")
        asyncio.run(init_db())
        print("[DEBUG] 数据库初始化完成")
        logger.info("数据库初始化完成")
        
        # 初始化游戏系统
        print("[DEBUG] 初始化游戏系统...")
        global xianxia_game
        xianxia_game = XianXiaGame()
        print("[DEBUG] 游戏系统初始化完成")
        logger.info("游戏系统初始化完成")
        
        # 注册命令处理器
        print("[DEBUG] 注册命令处理器...")
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(CommandHandler("xiuxian", xiuxian_handler))
        application.add_handler(CommandHandler("dazuo", dazuo_handler))
        application.add_handler(CommandHandler("status", status_handler))
        application.add_handler(CommandHandler("caiyao", caiyao_handler))
        application.add_handler(CommandHandler("mine", mine_handler))
        application.add_handler(CommandHandler("beibao", beibao_handler))
        application.add_handler(CommandHandler("paihang", paihang_handler))
        application.add_handler(CommandHandler("maiwuqi", maiwuqi_handler))
        application.add_handler(CommandHandler("zhuangbei", zhuangbei_handler))
        application.add_handler(CommandHandler("wuqi", wuqi_handler))
        application.add_handler(CommandHandler("elsevier", elsevier_handler))
        application.add_handler(CommandHandler("zahuo", zahuo_handler))
        application.add_handler(CommandHandler("qianghua", qianghua_handler))
        application.add_handler(CommandHandler("check_weapon", check_weapon_handler))
        print("[DEBUG] 命令处理器注册完成")
        
        # 启动机器人（需要在事件循环中运行）
        print("[DEBUG] 开始轮询消息...")
        logger.info("开始轮询消息...")
        
        # 创建并设置事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 在事件循环中运行轮询
            application.run_polling(drop_pending_updates=True)
        finally:
            # 清理事件循环
            loop.close()
        
    except Exception as e:
        print(f"[DEBUG] 主函数错误: {e}")
        logger.error(f"主函数错误: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("收到退出信号, 正在停止Bot...")
    except Exception as e:
        logger.error(f"Bot运行出错: {e}", exc_info=True)