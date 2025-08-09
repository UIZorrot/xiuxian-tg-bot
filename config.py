# -*- coding: utf-8 -*-
"""
修仙Telegram机器人配置文件
将所有环境变量改为Python常数配置
"""

import os
from typing import Dict, List

# =============================================================================
# Telegram Bot 配置
# =============================================================================

# Telegram Bot Token - 请在这里填入你的机器人Token
TELEGRAM_BOT_TOKEN = "7959010529:AAFNsquVMC_IrYyoD_b4uAflWxMl3nIVheg"  # 替换为你的实际Token

# 如果你想保留从环境变量读取的选项，可以使用下面的方式：
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "your_default_token_here")

# =============================================================================
# 数据库配置
# =============================================================================

# SQLite 数据库文件路径
DATABASE_PATH = "xiuxian_game.db"

# 数据库连接池配置
DB_POOL_SIZE = 10
DB_TIMEOUT = 30.0

# =============================================================================
# 频道和权限配置
# =============================================================================

# 允许的频道配置
ALLOWED_CHANNELS: Dict[int, List[int]] = {
    -1002749451494: [5]
}

# 游戏频道配置
GAME_CHANNELS: Dict[int, List[int]] = {
    -1002749451494: [5]
}

# 公告频道配置
ALLOWED_ANN: Dict[int, List[int]] = {
    -1002309536226: [1]
}

# 提现公告频道配置
WITHDRAW_ANN: Dict[int, List[int]] = {
    -1002309536226: [1, 141108]
}

# =============================================================================
# 游戏配置
# =============================================================================

# 冷却时间配置（秒）
COOLDOWN_TIMES = {
    "meditation": 60,      # 打坐冷却时间
    "herb_gathering": 180, # 采药冷却时间
    "mining": 120,         # 采矿冷却时间
    "challenge": 600       # 副本挑战冷却时间
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# =============================================================================
# 开发配置
# =============================================================================

# 是否启用调试模式
DEBUG_MODE = False

# 是否启用详细日志
VERBOSE_LOGGING = False

# =============================================================================
# 配置验证函数
# =============================================================================

def validate_config() -> bool:
    """
    验证配置是否正确
    """
    if TELEGRAM_BOT_TOKEN == "your_bot_token_here":
        print("⚠️  警告: 请在config.py中设置正确的TELEGRAM_BOT_TOKEN")
        return False
    
    if not DATABASE_PATH:
        print("⚠️  警告: 数据库路径不能为空")
        return False
    
    return True

def get_config_info() -> str:
    """
    获取配置信息摘要
    """
    return f"""
🔧 修仙机器人配置信息:
📱 Bot Token: {'已配置' if TELEGRAM_BOT_TOKEN != 'your_bot_token_here' else '未配置'}
💾 数据库: {DATABASE_PATH}
🎮 游戏频道数: {len(GAME_CHANNELS)}
⏰ 调试模式: {'开启' if DEBUG_MODE else '关闭'}
"""

if __name__ == "__main__":
    print(get_config_info())
    if validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")