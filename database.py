# -*- coding: utf-8 -*-
"""
修仙Telegram机器人数据库层
使用SQLite替换Supabase，提供异步数据库操作
"""

import aiosqlite
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from models.player_data import PlayerData
from config import DATABASE_PATH, DB_TIMEOUT

logger = logging.getLogger(__name__)

class Database:
    """
    异步SQLite数据库管理类
    """
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.timeout = DB_TIMEOUT
        
    async def init_database(self) -> None:
        """
        初始化数据库，创建必要的表
        """
        try:
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                # 创建玩家表
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        screen_name TEXT NOT NULL,
                        realm TEXT DEFAULT '练气期',
                        exp INTEGER DEFAULT 0,
                        spiritual_power INTEGER DEFAULT 100,
                        max_spiritual_power INTEGER DEFAULT 100,
                        max_hp INTEGER DEFAULT 100,
                        attack INTEGER DEFAULT 10,
                        defense INTEGER DEFAULT 5,
                        items TEXT DEFAULT '{}',  -- JSON格式存储物品
                        equipped_weapon TEXT,
                        last_meditation_time TEXT,
                        last_herb_gathering_time TEXT,
                        last_mining_time TEXT,
                        last_challenge_time TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建索引以提高查询性能
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_players_username 
                    ON players(username)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_players_realm 
                    ON players(realm)
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_players_exp 
                    ON players(exp DESC)
                """)
                
                await db.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    async def get_player(self, user_id: int) -> Optional[PlayerData]:
        """
        根据用户ID获取玩家数据
        """
        try:
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM players WHERE user_id = ?", 
                    (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                if row:
                    # 转换为字典
                    data = dict(row)
                    
                    # 解析JSON字段
                    if data['items']:
                        try:
                            data['items'] = json.loads(data['items'])
                        except json.JSONDecodeError:
                            data['items'] = {"灵石": 0, "weapons": {}, "materials": {}}
                    else:
                        data['items'] = {"灵石": 0, "weapons": {}, "materials": {}}
                    
                    return PlayerData.from_dict(data)
                    
                return None
                
        except Exception as e:
            logger.error(f"获取玩家数据失败 (user_id: {user_id}): {e}")
            return None
    
    async def create_player(self, user_id: int, username: str, screen_name: str) -> PlayerData:
        """
        创建新玩家
        """
        try:
            now = datetime.now(timezone.utc).isoformat()
            default_items = json.dumps({"灵石": 0, "weapons": {}, "materials": {}})
            
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                await db.execute("""
                    INSERT INTO players (
                        user_id, username, screen_name, realm, exp, 
                        spiritual_power, max_spiritual_power, max_hp, 
                        attack, defense, items, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, username, screen_name, "练气期", 0,
                    100, 100, 100, 10, 5, default_items, now, now
                ))
                await db.commit()
                
            logger.info(f"创建新玩家: {username} (ID: {user_id})")
            
            # 返回新创建的玩家数据
            player = await self.get_player(user_id)
            return player
            
        except Exception as e:
            logger.error(f"创建玩家失败 (user_id: {user_id}): {e}")
            raise
    
    async def update_player(self, player: PlayerData) -> PlayerData:
        """
        更新玩家数据
        """
        try:
            now = datetime.now(timezone.utc).isoformat()
            
            # 将玩家数据转换为数据库格式
            player_dict = player.to_dict()
            items_json = json.dumps(player_dict['items'])
            
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                await db.execute("""
                    UPDATE players SET
                        username = ?,
                        screen_name = ?,
                        realm = ?,
                        exp = ?,
                        spiritual_power = ?,
                        max_spiritual_power = ?,
                        max_hp = ?,
                        attack = ?,
                        defense = ?,
                        items = ?,
                        equipped_weapon = ?,
                        last_meditation_time = ?,
                        last_herb_gathering_time = ?,
                        last_mining_time = ?,
                        last_challenge_time = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    player.username,
                    player.screen_name,
                    player.realm,
                    player.exp,
                    player.spiritual_power,
                    player.max_spiritual_power,
                    player.max_hp,
                    player.attack,
                    player.defense,
                    items_json,
                    player.equipped_weapon,
                    player_dict.get('last_meditation_time'),
                    player_dict.get('last_herb_gathering_time'),
                    player_dict.get('last_mining_time'),
                    player_dict.get('last_challenge_time'),
                    now,
                    player.user_id
                ))
                await db.commit()
                
            logger.debug(f"更新玩家数据: {player.username} (ID: {player.user_id})")
            return player
            
        except Exception as e:
            logger.error(f"更新玩家数据失败 (user_id: {player.user_id}): {e}")
            raise
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取排行榜数据
        """
        try:
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT user_id, username, screen_name, realm, exp
                    FROM players
                    ORDER BY exp DESC
                    LIMIT ?
                """, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            return []
    
    async def get_player_count(self) -> int:
        """
        获取玩家总数
        """
        try:
            async with aiosqlite.connect(self.db_path, timeout=self.timeout) as db:
                async with db.execute("SELECT COUNT(*) FROM players") as cursor:
                    result = await cursor.fetchone()
                    return result[0] if result else 0
                    
        except Exception as e:
            logger.error(f"获取玩家总数失败: {e}")
            return 0
    
    async def backup_database(self, backup_path: str) -> bool:
        """
        备份数据库
        """
        try:
            async with aiosqlite.connect(self.db_path) as source:
                async with aiosqlite.connect(backup_path) as backup:
                    await source.backup(backup)
                    
            logger.info(f"数据库备份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return False
    
    async def close(self):
        """
        关闭数据库连接（SQLite不需要显式关闭，但保留接口兼容性）
        """
        logger.info("数据库连接已关闭")

# 全局数据库实例
database = Database()

# 便捷函数
async def init_db():
    """初始化数据库"""
    await database.init_database()

async def get_player(user_id: int) -> Optional[PlayerData]:
    """获取玩家数据"""
    return await database.get_player(user_id)

async def create_player(user_id: int, username: str, screen_name: str) -> PlayerData:
    """创建玩家"""
    return await database.create_player(user_id, username, screen_name)

async def update_player(player: PlayerData) -> PlayerData:
    """更新玩家数据"""
    return await database.update_player(player)

async def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """获取排行榜"""
    return await database.get_leaderboard(limit)

async def get_player_count() -> int:
    """获取玩家总数"""
    return await database.get_player_count()