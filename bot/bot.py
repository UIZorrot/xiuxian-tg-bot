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
sys.path.append('..')
from config import (
    TELEGRAM_BOT_TOKEN, GAME_CHANNELS, ALLOWED_CHANNELS, 
    ALLOWED_ANN, WITHDRAW_ANN, LOG_LEVEL, LOG_FORMAT
)
from database import init_db

from bot.weapon_enhancement import WeaponEnhancement
from bot.xianxia_game import XianXiaGame

# 配置日志
logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
logger = logging.getLogger(__name__)


# 初始化游戏组件（数据库将在main函数中初始化）
xianxia_game = None
weapon_enhancement = WeaponEnhancement()

# 创建Application实例
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Realtime功能已移除，使用SQLite本地数据库



async def send_announcement():
    """定期发送公告（暂时禁用，可根据需要重新实现）"""
    # 公告功能暂时禁用，因为不再使用Supabase
    # 如果需要公告功能，可以在SQLite中创建announcements表
    logger.info("公告功能已禁用")
    while True:
        await asyncio.sleep(3600)  # 保持任务运行但不执行任何操作


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理/start命令"""
    await update.message.reply_text("欢迎使用修仙机器人！\n\n发送 /xiuxian 开始你的修仙之旅！", parse_mode=ParseMode.HTML)


@bot.message_handler(commands=['xiuxian'])
async def start_cultivation(message):
    try:
        username = message.from_user.username or str(message.from_user.id)

        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        status = await xianxia_game.get_status(
            user_id=message.from_user.id,
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
            # await bot.reply_to(message, response)
            with open('./tgbot/videos/xiuxian.mp4', 'rb') as video:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=video,
                    caption=response,
                    reply_to_message_id=message.message_id,
                    # 可选参数
                    duration=16,  
                    width=1280,  
                    height=720, 
                    supports_streaming=True 
                )
        else:
            await bot.reply_to(message, "获取状态失败,请稍后重试。")
    except Exception as e:
        logger.error(f"修仙命令处理错误: {e}", exc_info=True)
        await bot.reply_to(message, f"发生错误: {str(e)}")


@bot.message_handler(commands=['dazuo'])
async def meditate_handler(message):
    try:
        username = message.from_user.username or str(message.from_user.id)
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        result = await xianxia_game.meditate(
            user_id=message.from_user.id,
            username=username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        
        if result:
            # await bot.reply_to(message, result)
            # with open('./tgbot/images/dazuo.jpg', 'rb') as photo:
            #     await bot.send_photo(
            #         message.chat.id,
            #         photo,
            #         caption=result,
            #         reply_to_message_id=message.message_id
            #     )
            with open('./tgbot/videos/dazuo.mp4', 'rb') as video:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=video,
                    caption=result,
                    reply_to_message_id=message.message_id,
                    # 可选参数
                    duration=4,  # 视频时长（秒）
                    width=1280,   # 视频宽度
                    height=720,   # 视频高度
                    supports_streaming=True  # 支持流媒体播放
                )
        else:
            await bot.reply_to(message, "打坐失败,请稍后重试。")
    except Exception as e:
        logger.error(f"打坐命令处理错误: {e}", exc_info=True)
        await bot.reply_to(message, f"打坐失败: {str(e)}")


@bot.message_handler(commands=['caiyao'])
async def gather_herbs_handler(message):
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        result = await xianxia_game.gather_herbs(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        # await bot.reply_to(message, result)
        # with open('./tgbot/images/caiyao.jpg', 'rb') as photo:
        #     await bot.send_photo(
        #         message.chat.id,
        #         photo,
        #         caption=result,
        #         reply_to_message_id=message.message_id
        #     )
        with open('./tgbot/videos/caiyao.mp4', 'rb') as video:
            await bot.send_video(
                chat_id=message.chat.id,
                video=video,
                caption=result,
                reply_to_message_id=message.message_id,
                # 可选参数
                duration=4,  
                width=1280,  
                height=720, 
                supports_streaming=True 
            )
    except Exception as e:
        await bot.reply_to(message, f"采药失败: {str(e)}")

@bot.message_handler(commands=['status'])
async def status_handler(message):
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        status = await xianxia_game.get_status(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        await bot.reply_to(message, status)
        # with open('./images/mine.jpg', 'rb') as photo:
        #     await bot.send_photo(
        #         message.chat.id,
        #         photo,
        #         caption=status,
        #         reply_to_message_id=message.message_id
        #     )
    except Exception as e:
        await bot.reply_to(message, f"查询状态失败: {str(e)}")


@bot.message_handler(commands=['beibao'])
async def inventory_handler(message):
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        inventory = await xianxia_game.get_inventory(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        # await bot.reply_to(message, inventory)
        with open('./tgbot/images/beibao.jpg', 'rb') as photo:
            await bot.send_photo(
                message.chat.id,
                photo,
                caption=inventory,
                reply_to_message_id=message.message_id
            )
    except Exception as e:
        await bot.reply_to(message, f"查询背包失败: {str(e)}")


@bot.message_handler(commands=['mine'])
async def mine(message):
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        result = await xianxia_game.mine(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )
        # await bot.reply_to(message, result)

        # with open('./tgbot/images/mine.jpg', 'rb') as photo:
        #     await bot.send_photo(
        #         message.chat.id,
        #         photo,
        #         caption=mine,
        #         reply_to_message_id=message.message_id
        #     )
        with open('./tgbot/videos/kuangdong.mp4', 'rb') as video:
            await bot.send_video(
                chat_id=message.chat.id,
                video=video,
                caption=result,
                reply_to_message_id=message.message_id,
                # 可选参数
                duration=4,  
                width=1280,  
                height=720, 
                supports_streaming=True 
            )
    except Exception as e:
        await bot.reply_to(message, f"挖矿失败: {str(e)}")


# 铁匠铺
@bot.message_handler(commands=['wuqi', 'wq'])
async def weapon_shop_command(message):
    """查看武器商店"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        player = await xianxia_game.get_or_create_player(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name
        )

        # 发送可用境界列表
        realms_text = (
            "欢迎来到铁匠铺!\n"
            "请使用以下命令查看对应境界的武器：\n\n"
            "🔸 /wql 练气期\n"
            "🔸 /wql 筑基期\n"
            "🔸 /wql 金丹期\n"
            "🔸 /wql 元婴期\n"
            "🔸 /wql 化神期\n"
            "🔸 /wql 炼虚期\n"
            "🔸 /wql 合体期\n"
            "🔸 /wql 大乘期\n"
            "🔸 /wql 渡劫期\n\n"
            "💡 当前境界可购买的武器会标记为 ✅"
        )

        # 发送商店图片
        with open('./tgbot/images/tiejiang.jpg', 'rb') as photo:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=realms_text,
                reply_to_message_id=message.message_id
            )
        
    except Exception as e:
        logger.error(f"查看武器商店失败: {e}")
        await bot.reply_to(message, "查看武器商店失败,请稍后再试。")


@bot.message_handler(commands=['wql'])
async def weapon_shop_by_realm(message):
    """查看特定境界的武器"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if not args:
            await bot.reply_to(message, "请指定要查看的境界。\n使用方法: /wql 练气期")
            return

        realm = ' '.join(args)
        weapons_list = await xianxia_game.list_weapons_by_realm(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            realm=realm
        )
        
        await bot.send_message(
            chat_id=message.chat.id,
            text=weapons_list,
            reply_to_message_id=message.message_id
        )
            
    except Exception as e:
        logger.error(f"查看境界武器失败: {e}")
        await bot.reply_to(message, "查看境界武器失败,请稍后再试。")


@bot.message_handler(commands=['maiwuqi', 'mwq'])
async def buy_weapon_command(message):
    """购买武器"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if not args:
            await bot.reply_to(message, "请指定要购买的武器名称。\n使用方法: /maiwuqi 天青木剑")
            return

        weapon_name = ' '.join(args)
        result = await xianxia_game.buy_weapon(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            weapon_name=weapon_name
        )
        
        await bot.reply_to(message, result)
        
    except Exception as e:
        logger.error(f"购买武器失败: {e}")
        await bot.reply_to(message, "购买武器失败,请稍后再试。")


@bot.message_handler(commands=['zhuangbei', 'zb'])
async def equip_weapon_command(message):
    """装备武器"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if not args:
            await bot.reply_to(message, "请指定要装备的武器名称。\n使用方法: /zhuangbei 天青木剑")
            return

        weapon_name = ' '.join(args)
        result = await xianxia_game.equip_weapon(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            weapon_name=weapon_name
        )
        
        await bot.reply_to(message, result)

    except Exception as e:
        logger.error(f"装备武器失败: {e}")
        await bot.reply_to(message, "装备武器失败,请稍后再试。")


@bot.message_handler(commands=['paihang'])
async def leaderboard_command(message):
    """显示修仙界排行榜"""
    try:

        # 获取排行榜数据
        leaderboard_text = await xianxia_game.get_leaderboard()
        
        # 发送排行榜
        await bot.reply_to(
            message,
            leaderboard_text,
            parse_mode=None 
        )
    except Exception as e:
        logger.error(f"排行榜命令处理错误: {e}")
        await bot.reply_to(message, "获取排行榜失败，请稍后再试。")


@bot.message_handler(commands=['zahuo'])
async def materials_shop(message):
    """杂货铺"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if len(args) == 1 and args[0] == "all":
            # 出售所有材料
            result = await xianxia_game.sell_all_materials(
                user_id=message.from_user.id,
                username=message.from_user.username,
                screen_name=full_name,
                chat_id=message.chat.id,
                message_thread_id=getattr(message, 'message_thread_id', None)
            )
            await bot.reply_to(message, result)
            return

        elif len(args) < 2:
            await bot.reply_to(
                message,
                "请指定要出售的材料名称和数量。\n"
                "使用方法: /zahuo [材料名称] [数量]\n"
                "例如: /zahuo 大道源石 1"
            )
            return
        
        else:
            # 分离材料名称和数量
            try:
                # 最后一个参数作为数量，其余的作为材料名称
                *name_parts, amount_str = args
                materials_name = ' '.join(name_parts)
                materials_amount = int(amount_str)

                # 检查数量是否有效
                if materials_amount <= 0:
                    await bot.reply_to(message, "请输入大于0的数量。")
                    return

            except ValueError:
                await bot.reply_to(
                    message, 
                    "请输入有效的数量。\n"
                    "使用方法: /zahuo [材料名称] [数量]\n"
                    "例如: /zahuo 大道源石 1"
                )
                return

            # 调用出售材料函数
            result = await xianxia_game.sell_materials(
                user_id=message.from_user.id,
                username=message.from_user.username,
                screen_name=full_name,
                materials_name=materials_name,
                materials_amount=materials_amount,
                chat_id=message.chat.id,
                message_thread_id=getattr(message, 'message_thread_id', None)
            )

            await bot.reply_to(message, result)

    except Exception as e:
        logger.error(f"出售材料失败: {e}")
        await bot.reply_to(message, "出售材料失败，请稍后再试。")


@bot.message_handler(commands=['elsevier'])
async def elsevier_command(message):
   
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if not args:
            # 显示副本信息
            dungeon_info = (
                "🏰 爱思唯尔秘境\n\n"
                "可挑战关卡：\n"
                "1. 道经殿 (练气期)\n"
                "2. 源天长廊 (筑基期)\n"
                "3. 帝经密室 (金丹期)\n"
                "4. 神王殿 (元婴期)\n"
                "5. 太古圣殿 (化神期)\n\n"
                "使用方法：/elsevier [关卡名称]\n"
                "例如：/elsevier 道经殿"
            )
            # await bot.reply_to(message, dungeon_info)
            with open('./tgbot/videos/fubenhome.mp4', 'rb') as video:
                await bot.send_video(
                    chat_id=message.chat.id,
                    video=video,
                    caption=dungeon_info,
                    reply_to_message_id=message.message_id,
                    # 可选参数
                    duration=4,  
                    width=1280,  
                    height=720, 
                    supports_streaming=True 
                )
            return

        stage_name = ' '.join(args)
        result = await xianxia_game.challenge_elsevier(
            user_id=message.from_user.id,
            username=message.from_user.username,
            screen_name=full_name,
            stage_name=stage_name,
            chat_id=message.chat.id,
            message_thread_id=getattr(message, 'message_thread_id', None)
        )

        with open('./tgbot/videos/attack.mp4', 'rb') as video:
            await bot.send_video(
                chat_id=message.chat.id,
                video=video,
                caption=result,
                reply_to_message_id=message.message_id,
                # 可选参数
                duration=4,  
                width=1280,  
                height=720, 
                supports_streaming=True 
            )
        # await bot.reply_to(message, "系统过载, 副本关闭!")

    except Exception as e:
        logger.error(f"爱思唯尔副本命令处理失败: {e}")
        await bot.reply_to(message, "副本挑战失败，请稍后再试。")



# 武器强化

@bot.message_handler(commands=['qianghua'])
async def handle_enhance(message):
    """处理强化命令"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        if not args:
            await bot.reply_to(message, "请指定要强化的武器名称！\n用法: /qianghua 武器名称")
            return
        
        player = await xianxia_game.get_or_create_player(message.from_user.id, message.from_user.username, full_name)

        weapon_name = " ".join(args)
        result = await weapon_enhancement.enhance_weapon(
            player,
            xianxia_game.update_player,
            weapon_name
        )
        
        # await bot.reply_to(message, result)
        with open('./tgbot/videos/qianghua.mp4', 'rb') as video:
            await bot.send_video(
                chat_id=message.chat.id,
                video=video,
                caption=result,
                reply_to_message_id=message.message_id,
                # 可选参数
                duration=4,  
                width=1280,  
                height=720, 
                supports_streaming=True 
            )
        
    except Exception as e:
        logger.error(f"处理强化命令失败: {e}")
        await bot.reply_to(message, "处理强化命令失败，请稍后再试。")


@bot.message_handler(commands=['check_weapon'])
async def handle_weapon(message):
    """处理查看武器信息命令"""
    try:
        full_name = message.from_user.first_name
        if message.from_user.last_name:
            full_name += f" {message.from_user.last_name}"

        args = message.text.split()[1:]
        weapon_name = " ".join(args) if args else None
        player = await xianxia_game.get_or_create_player(message.from_user.id, message.from_user.username, full_name)

        result = await weapon_enhancement.check_weapon(
            player,
            weapon_name
        )
        
        await bot.reply_to(message, result)
        
    except Exception as e:
        logger.error(f"处理查看武器命令失败: {e}")
        await bot.reply_to(message, "处理查看武器命令失败，请稍后再试。")


async def main():
    """主程序入口"""
    logger.info("启动机器人...")
    
    try:
        # 初始化数据库
        await init_db()
        
        # 初始化游戏组件
        global xianxia_game
        xianxia_game = XianXiaGame()
        
        tasks = [
            asyncio.create_task(start_bot()),
            # asyncio.create_task(send_announcement()),  # 暂时禁用公告功能
        ]
        
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logger.error(f"主程序发生错误: {e}", exc_info=True)
        raise

async def start_bot():
    """启动机器人"""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # 尝试删除 Webhook，如果失败则跳过
            try:
                logger.info("正在删除webhook...")
                await asyncio.wait_for(bot.delete_webhook(drop_pending_updates=True), timeout=10)
                logger.info("Webhook删除成功")
            except asyncio.TimeoutError:
                logger.warning("删除webhook超时，跳过此步骤")
            except Exception as e:
                logger.warning(f"删除webhook失败，跳过此步骤: {e}")
            
            # 启动轮询，使用基本配置
            logger.info("开始轮询消息...")
            await bot.polling(
                non_stop=True, 
                skip_pending=True, 
                timeout=20  # 基本超时时间
            )
            break  # 如果成功启动，跳出重试循环
            
        except Exception as e:
            logger.error(f"机器人运行错误 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"等待 {retry_delay} 秒后重试...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # 指数退避
            else:
                logger.error("所有重试都失败，机器人无法启动")
                raise

if __name__ == "__main__":
    try:
        # 运行主程序
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("收到退出信号, 正在停止Bot...")
    except Exception as e:
        logger.error(f"程序异常退出: {e}", exc_info=True)