from datetime import datetime, timezone
import random
from typing import Optional, Dict, List
import logging
from bot.weapon_shop import WeaponShop
from models.player_data import PlayerData

# 导入新的数据库模块
import os
import sys
# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database import get_player, create_player, update_player, get_leaderboard
from config import GAME_CHANNELS

logger = logging.getLogger(__name__)


class XianXiaGame:
    def __init__(self, allowed_channels: Optional[Dict[int, List[int]]] = None):
        self.weapon_shop = WeaponShop()
        self.allowed_channels = allowed_channels or GAME_CHANNELS
        self.logger = logging.getLogger(__name__)

        # 境界设置
        self.realms = [
            "练气期", "筑基期", "金丹期", "元婴期", "化神期",
            "炼虚期", "合体期", "大乘期", "渡劫期"
        ]
        
        # 各境界所需经验
        self.realm_exp = {
            "练气期": 0,
            "筑基期": 1000,
            "金丹期": 5000,
            "元婴期": 20000,
            "化神期": 50000,
            "炼虚期": 100000,
            "合体期": 200000,
            "大乘期": 500000,
            "渡劫期": 1000000
        }

        # 采药地点设置
        self.herb_locations = {
            "凡人村落": {
                "herbs": ["普通药草", "灵气草", "青龙草", "白虎叶"],
                "min_realm": "练气期",
                "spiritual_power_cost": 20
            },
            "初级灵药园": {
                "herbs": ["低级灵药", "中级灵药", "紫阳花", "星辰草", "龙血草"],
                "min_realm": "筑基期",
                "spiritual_power_cost": 40
            },
            "中级灵药园": {
                "herbs": ["中级灵药", "高级灵药", "太阳神草", "月精草", "九叶天菊"],
                "min_realm": "金丹期",
                "spiritual_power_cost": 60
            },
            "高级灵药园": {
                "herbs": ["高级灵药", "极品灵药", "不死神药", "混沌青莲", "永生草"],
                "min_realm": "元婴期",
                "spiritual_power_cost": 80
            },
            "仙药园": {
                "herbs": ["仙药", "九转还魂草", "神王草", "不死神药", "混沌体草"],
                "min_realm": "化神期",
                "spiritual_power_cost": 100
            },
            "荒古禁地": {
                "herbs": ["荒古神药", "不死药", "神皇草", "太初神药", "混沌仙药"],
                "min_realm": "合体期",
                "spiritual_power_cost": 150
            },
            "仙域秘境": {
                "herbs": ["仙域神药", "长生草", "混沌神药", "大道宝药", "太初永生药"],
                "min_realm": "大乘期",
                "spiritual_power_cost": 200
            }
        }

        # 药材价值设置
        self.herb_values = {
            # 基础药材
            "普通药草": 10,
            "灵气草": 20,
            "青龙草": 30,
            "白虎叶": 40,
            # 初级灵药
            "低级灵药": 50,
            "中级灵药": 100,
            "紫阳花": 150,
            "星辰草": 200,
            "龙血草": 250,
            # 中级灵药
            "太阳神草": 300,
            "月精草": 400,
            "九叶天菊": 500,
            # 高级灵药
            "高级灵药": 500,
            "不死神药": 1000,
            "混沌青莲": 1500,
            "永生草": 2000,
            "极品灵药": 2000,
            "混沌体草": 2500,
            # 仙药级别
            "仙药": 3000,
            "九转还魂草": 4000,
            "神王草": 5000,
            # 荒古级别
            "荒古神药": 8000,
            "不死药": 10000,
            "神皇草": 12000,
            "太初神药": 15000,
            # 仙域级别
            "仙域神药": 20000,
            "长生草": 25000,
            "混沌神药": 30000,
            "大道宝药": 40000,
            "太初永生药": 50000,
            "灵石": 1,
            "下品灵石": 10,
            "中品灵石": 100,
            "上品灵石": 1000,
            "极品灵石": 10000,
            "神品灵石": 100000,
            "荒古神石": 1000000,
            "仙域神石": 10000000,
            # 特殊矿物
            "青铜源石": 50,
            "玄铁原石": 100,
            "精钢原石": 200,
            "星辰铁": 500,
            "太阳精金": 1000,
            "月华玉": 1500,
            "龙骨精金": 3000,
            "凤髓玉": 5000,
            "混沌石": 10000,
            "仙源矿": 20000,
            "不朽金": 50000,
            "永恒源质": 100000,
            "混沌神金": 200000,
            "大道源石": 500000
        }

        self.mining_locations = {
            "浅层矿洞": {
                "min_realm": "练气期",
                "spirit_cost": 15,
                "rewards": {
                    "灵石": (5, 15),
                    "下品灵石": (0, 2),
                    "青铜源石": (1, 3),
                    "玄铁原石": (0, 1)
                },
                "exp": (5, 10)
            },
            "中层矿洞": {
                "min_realm": "筑基期",
                "spirit_cost": 25,
                "rewards": {
                    "灵石": (15, 30),
                    "下品灵石": (2, 5),
                    "中品灵石": (0, 2),
                    "精钢原石": (1, 3),
                    "星辰铁": (0, 1)
                },
                "exp": (10, 20)
            },
            "深层矿洞": {
                "min_realm": "金丹期",
                "spirit_cost": 40,
                "rewards": {
                    "灵石": (30, 50),
                    "中品灵石": (2, 5),
                    "上品灵石": (0, 2),
                    "太阳精金": (0, 1),
                    "月华玉": (0, 1)
                },
                "exp": (20, 30)
            },
            "地心矿洞": {
                "min_realm": "元婴期",
                "spirit_cost": 60,
                "rewards": {
                    "灵石": (50, 100),
                    "上品灵石": (2, 5),
                    "极品灵石": (0, 2),
                    "龙骨精金": (0, 1),
                    "凤髓玉": (0, 1)
                },
                "exp": (30, 50)
            },
            "神秘矿洞": {
                "min_realm": "化神期",
                "spirit_cost": 80,
                "rewards": {
                    "极品灵石": (2, 5),
                    "神品灵石": (0, 2),
                    "混沌石": (0, 1),
                    "仙源矿": (0, 1)
                },
                "exp": (50, 80)
            },
            "荒古矿脉": {
                "min_realm": "合体期",
                "spirit_cost": 100,
                "rewards": {
                    "神品灵石": (2, 5),
                    "荒古神石": (0, 2),
                    "不朽金": (0, 1),
                    "永恒源质": (0, 1)
                },
                "exp": (80, 120)
            },
            "仙域矿境": {
                "min_realm": "大乘期",
                "spirit_cost": 150,
                "rewards": {
                    "荒古神石": (2, 5),
                    "仙域神石": (0, 2),
                    "混沌神金": (0, 1),
                    "大道源石": (0, 1)
                },
                "exp": (120, 200)
            }
        }

        # 矿物价值设置
        self.mineral_values = {
            # 基础矿物
            "灵石": 1,
            "下品灵石": 10,
            "中品灵石": 100,
            "上品灵石": 1000,
            "极品灵石": 10000,
            "神品灵石": 100000,
            "荒古神石": 1000000,
            "仙域神石": 10000000,
            # 特殊矿物
            "青铜源石": 50,
            "玄铁原石": 100,
            "精钢原石": 200,
            "星辰铁": 500,
            "太阳精金": 1000,
            "月华玉": 1500,
            "龙骨精金": 3000,
            "凤髓玉": 5000,
            "混沌石": 10000,
            "仙源矿": 20000,
            "不朽金": 50000,
            "永恒源质": 100000,
            "混沌神金": 200000,
            "大道源石": 500000
        }

        self.elsevier_dungeon = {
            "name": "爱思唯尔道场",
            "description": "这是一片蕴含着太古遗留下来的道法至宝的神秘空间，传说中藏有众多太古大帝的修行感悟。但要小心，太古神灵的意志会对入侵者发起猛烈的攻击。",
            
            "stages": {
                "道经殿": {
                    "min_realm": "练气期",
                    "spirit_cost": 30,
                    "monsters": [
                        {"name": "道经守卫", "hp": 100, "attack": 20, "defense": 10},
                        {"name": "太古道灵", "hp": 150, "attack": 25, "defense": 15}
                    ],
                    "rewards": {
                        "exp": (100, 200),
                        "items": {
                            "道源碎片": (1, 3),
                            "灵石": (50, 100),
                            "太古精华": (1, 2)
                        }
                    }
                },
                
                "源天长廊": {
                    "min_realm": "筑基期",
                    "spirit_cost": 50,
                    "monsters": [
                        {"name": "源天使者", "hp": 200, "attack": 35, "defense": 20},
                        {"name": "太古源灵", "hp": 250, "attack": 40, "defense": 25}
                    ],
                    "rewards": {
                        "exp": (200, 400),
                        "items": {
                            "源天之力": (1, 3),
                            "灵石": (100, 200),
                            "太古精华": (2, 4)
                        }
                    }
                },
                
                "帝经密室": {
                    "min_realm": "金丹期",
                    "spirit_cost": 80,
                    "monsters": [
                        {"name": "帝经守护者", "hp": 400, "attack": 60, "defense": 40},
                        {"name": "大帝意志", "hp": 500, "attack": 70, "defense": 45}
                    ],
                    "rewards": {
                        "exp": (400, 800),
                        "items": {
                            "帝经碎页": (1, 2),
                            "灵石": (200, 400),
                            "太古精华": (3, 6)
                        }
                    }
                },
                
                "神王殿": {
                    "min_realm": "元婴期",
                    "spirit_cost": 120,
                    "monsters": [
                        {"name": "神王使者", "hp": 800, "attack": 100, "defense": 70},
                        {"name": "太古神王", "hp": 1000, "attack": 120, "defense": 80}
                    ],
                    "rewards": {
                        "exp": (800, 1600),
                        "items": {
                            "神王之力": (1, 2),
                            "灵石": (400, 800),
                            "太古精华": (5, 10)
                        }
                    }
                },
                
                "太古圣殿": {
                    "min_realm": "化神期",
                    "spirit_cost": 200,
                    "boss": {
                        "name": "太古大帝",
                        "hp": 2000,
                        "attack": 200,
                        "defense": 150,
                        "skills": [
                            {"name": "大帝审判", "damage": 300},
                            {"name": "帝威压世", "damage": 250},
                            {"name": "太古神术", "damage": 400}
                        ]
                    },
                    "rewards": {
                        "exp": (2000, 4000),
                        "items": {
                            "大帝道果": (1, 1),
                            "灵石": (1000, 2000),
                            "太古精华": (10, 20),
                            "稀有道具": {
                                "太古神冠": 0.05,  # 5%概率
                                "帝道神兵": 0.03,  # 3%概率
                                "大帝道经": 0.02   # 2%概率
                            }
                        }
                    }
                }
            },
            
            # 特殊物品效果
            "special_items": {
                "太古神冠": {
                    "type": "equipment",
                    "slot": "head",
                    "effects": {
                        "spirit_power": 500,
                        "exp_bonus": 0.2  # 20%经验加成
                    }
                },
                "帝道神兵": {
                    "type": "weapon",
                    "attack": 300,
                    "effects": {
                        "spirit_power": 300,
                        "critical_chance": 0.15  # 15%暴击率
                    }
                },
                "大帝道经": {
                    "type": "artifact",
                    "effects": {
                        "spirit_power": 400,
                        "drop_rate": 0.1  # 10%掉落率提升
                    }
                }
            },
            
            # 材料合成配方
            "crafting": {
                "太古精华": {
                    "道源碎片": 5,
                    "源天之力": 3
                },
                "帝经碎页": {
                    "太古精华": 10,
                    "源天之力": 5
                }
            }
        }


        # 数据库连接由database模块管理
        self.logger.info("游戏系统初始化完成")

    # def get_or_create_player(self, user_id: int, username: str) -> PlayerData:
    #     """获取或创建玩家数据"""
    #     try:
    #         self.logger.info(f"尝试获取玩家数据 - user_id: {user_id}, username: {username}")
            
    #         # 查询现有玩家
    #         response = self.supabase.table('players').select("*").eq('user_id', user_id).execute()
            
    #         if response.data:
    #             self.logger.info("找到现有玩家")
    #             player_data = response.data[0]
    #             return PlayerData(**player_data)
            
    #         self.logger.info("未找到玩家，创建新玩家")
    #         # 创建新玩家
    #         new_player = PlayerData(user_id=user_id, username=username)
    #         insert_data = new_player.to_dict()
            
    #         # 移除时间戳字段，让数据库使用默认值
    #         insert_data.pop('created_at', None)
    #         insert_data.pop('updated_at', None)
            
    #         response = self.supabase.table('players').insert(insert_data).execute()
            
    #         if not response.data:
    #             raise Exception("创建玩家失败")
                
    #         return PlayerData(**response.data[0])
                
    #     except Exception as e:
    #         self.logger.error(f"获取/创建玩家数据错误: {e}", exc_info=True)
    #         raise

    def update_player(self, player: PlayerData) -> PlayerData:
        """更新玩家数据"""
        try:
            update_data = player.to_dict()
            # 移除不需要更新的字段
            for field in ['user_id', 'created_at', 'updated_at']:
                update_data.pop(field, None)
                
            self.logger.debug(f"准备更新数据: {update_data}")
            response = self.supabase.table('players').update(update_data).eq('user_id', player.user_id).execute()
            
            if not response.data:
                raise Exception("更新玩家数据失败")
                
            return PlayerData(**response.data[0])
            
        except Exception as e:
            self.logger.error(f"更新玩家数据错误: {e}", exc_info=True)
            raise

    def check_channel_permission(self, chat_id: int, message_thread_id: Optional[int] = None) -> bool:
        """检查是否在允许的频道和主题中"""
        self.logger.info(f"检查权限 - 聊天ID: {chat_id}, 主题ID: {message_thread_id}")
        
        if chat_id not in self.allowed_channels:
            self.logger.info(f"频道 {chat_id} 不在允许列表中")
            return False
        
        allowed_topics = self.allowed_channels[chat_id]
        
        if allowed_topics:
            if message_thread_id is None:
                self.logger.info("消息没有主题ID")
                return False
            result = message_thread_id in allowed_topics
            self.logger.info(f"主题ID {message_thread_id} {'在' if result else '不在'}允许列表中")
            return result
        
        return True


    def format_error_message(self, chat_id: int) -> str:
        """格式化错误消息"""
        return "该功能只能在指定的频道中使用。允许的主题ID: 🎮 Game | 凡人修仙传"


    async def get_or_create_player(self, user_id: int, username: str, screen_name: str) -> PlayerData:
        """异步获取或创建玩家数据，并处理灵力自动恢复"""
        try:
            self.logger.info(f"尝试获取玩家数据 - user_id: {user_id}, username: {username}")
            username = username or "unknown"

            # 查询现有玩家
            player_data = await get_player(user_id)
            
            if player_data:
                self.logger.info("找到现有玩家")
                player = player_data
                            
                # 处理灵力自动恢复
                now = datetime.now(timezone.utc)
                last_update = player.updated_at or player.created_at
                if last_update:
                    if last_update.tzinfo is None:
                        last_update = last_update.replace(tzinfo=timezone.utc)
                    
                    # 计算经过的时间和应该恢复的灵力
                    elapsed_seconds = int((now - last_update).total_seconds())
                    spirit_recovery = (elapsed_seconds // 5)  # 每5秒恢复1点
                    
                    if spirit_recovery > 0 and player.spiritual_power < player.max_spiritual_power:
                        # 计算新的灵力值
                        new_spirit = min(
                            player.max_spiritual_power,
                            player.spiritual_power + spirit_recovery
                        )
                        
                        if new_spirit != player.spiritual_power:
                            player.spiritual_power = new_spirit
                            # 更新数据库
                            await update_player(player)
                
                return player
            
            self.logger.info("未找到玩家，创建新玩家")
            new_player = PlayerData(user_id=user_id, username=username, screen_name=screen_name)
            
            # 创建新玩家
            created_player = await create_player(user_id, username, screen_name)
            if not created_player:
                raise Exception("创建玩家失败")
                
            return created_player
                
        except Exception as e:
            self.logger.error(f"获取/创建玩家数据错误: {e}", exc_info=True)
            raise


    async def update_player(self, player: PlayerData) -> PlayerData:
        """异步更新玩家数据"""
        try:
            self.logger.debug(f"准备更新玩家数据: {player.user_id}")
            updated_player = await update_player(player)
            
            if not updated_player:
                raise Exception("更新玩家数据失败")
                
            return updated_player
            
        except Exception as e:
            self.logger.error(f"更新玩家数据错误: {e}", exc_info=True)
            raise


    async def gather_herbs(
        self, 
        user_id: int, 
        username: str,
        screen_name: str,
        chat_id: int, 
        message_thread_id: Optional[int] = None
    ) -> str:
        """异步采集药材"""
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            player = await self.get_or_create_player(user_id, username, screen_name)
            now = datetime.now(timezone.utc)
            
            if player.last_herb_gathering_time:
                if player.last_herb_gathering_time.tzinfo is None:
                    player.last_herb_gathering_time = player.last_herb_gathering_time.replace(tzinfo=timezone.utc)
                cooldown = now - player.last_herb_gathering_time
                if cooldown.total_seconds() < 180:  # 3分钟冷却
                    remaining = 180 - int(cooldown.total_seconds())
                    return f"还需要等待{remaining}秒才能继续采药。"

            available_locations = [
                location for location, info in self.herb_locations.items()
                if self.realms.index(player.realm) >= self.realms.index(info["min_realm"])
            ]

            if not available_locations:
                return "当前境界无法采药。"

            location = random.choice(available_locations)
            location_info = self.herb_locations[location]

            if player.spiritual_power < location_info["spiritual_power_cost"]:
                return "灵力不足，无法采药。"

            # 增加采药数量
            herb = random.choice(location_info["herbs"])
            amount = random.randint(2, 5)  # 2-5个

            # 更新材料到新的数据结构
            if "materials" not in player.items:
                player.items["materials"] = {}
            player.items["materials"][herb] = player.items["materials"].get(herb, 0) + amount
            
            player.spiritual_power -= location_info["spiritual_power_cost"]
            player.last_herb_gathering_time = now

            # 随机获得额外经验
            exp_gain = random.randint(5, 15)
            player.exp += exp_gain

            await self.update_player(player)

            return (
                f"在{location}采药成功!\n"
                f"获得 {herb} x{amount}\n"
                f"意外获得{exp_gain}点经验\n"
                f"消耗灵力: {location_info['spiritual_power_cost']}\n"
                f"当前灵力: {player.spiritual_power}/{player.max_spiritual_power}"
            )

        except Exception as e:
            self.logger.error(f"采药错误: {e}", exc_info=True)
            raise

    async def meditate(self, user_id: int, username: str, screen_name: str, chat_id: int, message_thread_id: Optional[int] = None) -> str:
        """异步处理打坐"""
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            player = await self.get_or_create_player(user_id, username, screen_name)
            now = datetime.now(timezone.utc)
            
            if player.last_meditation_time:
                if player.last_meditation_time.tzinfo is None:
                    player.last_meditation_time = player.last_meditation_time.replace(tzinfo=timezone.utc)
                cooldown = now - player.last_meditation_time
                cooldown_seconds = cooldown.total_seconds()
                if cooldown_seconds < 60:  # 1分钟冷却
                    remaining = 60 - int(cooldown_seconds)
                    return f"还需要等待{remaining}秒才能继续打坐。"

            # 增加经验获取范围
            exp_gain = random.randint(15, 30)  # 提高经验获取
            player.exp += exp_gain
            
            # 减少灵力消耗
            spirit_cost = 5  # 从10降到5
            player.spiritual_power = max(0, player.spiritual_power - spirit_cost)
            player.last_meditation_time = now

            # 检查突破
            upgrade_message = ""
            current_realm_index = self.realms.index(player.realm)
            for i in range(current_realm_index + 1, len(self.realms)):
                next_realm = self.realms[i]
                if player.exp >= self.realm_exp[next_realm]:
                    player.realm = next_realm
                    player.max_spiritual_power += 50  # 突破时增加最大灵力
                    player.spiritual_power = player.max_spiritual_power  # 突破时恢复满灵力
                    upgrade_message = f"\n恭喜突破到{next_realm}!灵力上限提升至{player.max_spiritual_power}!"
                    break

            # 自动恢复一些灵力
            spirit_recovery = 0
            if not upgrade_message:  # 如果没有突破，则恢复一些灵力
                spirit_recovery = random.randint(2, 8)  # 随机恢复2-8点灵力
                player.spiritual_power = min(
                    player.max_spiritual_power,
                    player.spiritual_power + spirit_recovery
                )

            await self.update_player(player)

            # 构建基础响应
            response_parts = [
                f"打坐成功!获得{exp_gain}点经验。",
                f"消耗灵力: {spirit_cost}",
                f"恢复灵力: {spirit_recovery if not upgrade_message else player.max_spiritual_power}",
                f"当前灵力: {player.spiritual_power}/{player.max_spiritual_power}"
            ]

            # 添加突破信息
            if upgrade_message:
                response_parts.append(upgrade_message)

            # 添加距离下一境界的信息
            if current_realm_index < len(self.realms) - 1:
                next_realm = self.realms[current_realm_index + 1]
                exp_needed = self.realm_exp[next_realm] - player.exp
                response_parts.append(f"距离{next_realm}还需{exp_needed}经验")

            # 添加武器信息（如果有）
            if player.equipped_weapon:
                weapon = player.get_equipped_weapon()
                if weapon:
                    response_parts.append(
                        f"当前武器: {player.equipped_weapon}\n"
                        f"总攻击力: {player.total_attack} (基础{player.attack} + 武器{weapon.attack})"
                    )

            return "\n".join(response_parts)

        except Exception as e:
            self.logger.error(f"打坐错误: {e}", exc_info=True)
            raise

    async def get_status(self, user_id: int, username: str, screen_name: str, chat_id: int, message_thread_id: Optional[int] = None) -> str:
        """获取玩家状态"""
        if not self.check_channel_permission(chat_id, message_thread_id):
            return self.format_error_message(chat_id)

        try:
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 计算下一个境界所需经验
            current_realm_index = self.realms.index(player.realm)
            if current_realm_index < len(self.realms) - 1:
                next_realm = self.realms[current_realm_index + 1]
                exp_needed = self.realm_exp[next_realm] - player.exp
                next_realm_info = f"\n距离{next_realm}还需{exp_needed}经验"
            else:
                next_realm_info = "\n已达到最高境界"

            # 计算冷却时间信息
            now = datetime.now(timezone.utc)
            meditation_cd = ""
            herb_cd = ""
            
            if player.last_meditation_time:
                if player.last_meditation_time.tzinfo is None:
                    player.last_meditation_time = player.last_meditation_time.replace(tzinfo=timezone.utc)
                meditation_cooldown = now - player.last_meditation_time
                if meditation_cooldown.total_seconds() < 60:
                    remaining = 60 - int(meditation_cooldown.total_seconds())
                    meditation_cd = f"\n打坐冷却: 还需{remaining}秒"
                else:
                    meditation_cd = "\n打坐: 可用"
                    
            if player.last_herb_gathering_time:
                if player.last_herb_gathering_time.tzinfo is None:
                    player.last_herb_gathering_time = player.last_herb_gathering_time.replace(tzinfo=timezone.utc)
                herb_cooldown = now - player.last_herb_gathering_time
                if herb_cooldown.total_seconds() < 180:
                    remaining = 180 - int(herb_cooldown.total_seconds())
                    herb_cd = f"\n采药冷却: 还需{remaining}秒"
                else:
                    herb_cd = "\n采药: 可用"

            # 计算灵力恢复速度
            spirit_regen = "每5秒恢复1点灵力"
            if player.spiritual_power >= player.max_spiritual_power:
                spirit_regen = "灵力已满"

            # 添加武器信息
            weapon_info = ""
            if player.equipped_weapon:
                weapon = player.get_equipped_weapon()
                if weapon:
                    weapon_info = (
                        f"\n装备武器: {player.equipped_weapon}\n"
                        f"攻击力: {player.total_attack} (基础{player.attack} + 武器{weapon.attack})"
                    )
                else:
                    weapon_info = f"\n攻击力: {player.attack}"
            else:
                weapon_info = f"\n攻击力: {player.attack}"

            return (
                f"道友信息: \n"
                f"境界: {player.realm}\n"
                f"经验: {player.exp}{next_realm_info}\n"
                f"灵力: {player.spiritual_power}/{player.max_spiritual_power}\n"
                f"灵力恢复: {spirit_regen}{meditation_cd}{herb_cd}"
                f"{weapon_info}"
            )

        except Exception as e:
            logger.error(f"获取状态错误: {e}")
            raise


    async def get_inventory(self, user_id: int, username: str, screen_name: str, chat_id: int, message_thread_id: Optional[int] = None) -> str:
        """异步查看背包"""
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            player = await self.get_or_create_player(user_id, username, screen_name)
            # 检查背包是否为空
            if not player.items:
                return "背包是空的。"

            # 初始化灵石数量
            spirit_stones = 0

            # 计算材料价值
            materials = player.items.get("materials", {})
            total_material_value = 0
            material_list = []

            # 处理普通材料
            for item, amount in materials.items():
                if item == 'challenge':
                    continue  # 跳过副本材料，稍后处理
                if isinstance(amount, dict):
                    # 如果有嵌套结构，递归处理
                    for sub_item, sub_amount in amount.items():
                        value = self.herb_values.get(sub_item, 0) * sub_amount
                        if sub_item == '灵石':
                            spirit_stones += sub_amount
                        else:
                            if sub_amount != 0:
                                material_list.append(f"{sub_item} x{sub_amount} (价值: {value}灵石)")
                        total_material_value += value
                else:
                    value = self.herb_values.get(item, 0) * amount
                    if item == '灵石':
                        spirit_stones += amount
                    else:
                        if amount != 0:
                            material_list.append(f"{item} x{amount} (价值: {value}灵石)")
                    total_material_value += value

            # 处理副本材料
            challenge_materials = materials.get('challenge', {})
            challenge_material_list = []
            for item, amount in challenge_materials.items():
                value = self.herb_values.get(item, 0) * amount
                if amount != 0:
                    challenge_material_list.append(f"{item} x{amount} (价值: {value}灵石)")
                total_material_value += value

            # 获取武器列表
            weapons = player.items.get("weapons", {})
            weapon_list = []

            for weapon_name, weapon in weapons.items():
                equipped = "【已装备】" if player.equipped_weapon == weapon_name else ""
                weapon_list.append(
                    f"{weapon_name} {equipped}\n"
                    f" 品质: {weapon.rarity}\n"
                    f" 攻击力: {weapon.attack}\n"
                    f" 类型: {weapon.type}"
                )

            # 构建返回消息
            inventory_sections = []

            # 添加灵石信息
            inventory_sections.append(f"灵石: {spirit_stones}")
            # 添加普通材料信息
            if material_list:
                inventory_sections.append("\n材料: \n" + "\n".join(material_list))
            # 添加副本材料信息
            if challenge_material_list:
                inventory_sections.append("\n副本材料: \n" + "\n".join(challenge_material_list))
            # 添加武器信息
            if weapon_list:
                inventory_sections.append("\n武器: \n" + "\n".join(weapon_list))
            # 添加总价值
            total_value = total_material_value + spirit_stones
            inventory_sections.append(f"\n总价值: {total_value:,}灵石")

            return "背包内容: \n" + "\n".join(inventory_sections)

        except Exception as e:
            self.logger.error(f"查看背包错误: {e}", exc_info=True)
            raise



    async def mine(self, user_id: int, username: str, screen_name: str, chat_id: int, message_thread_id: Optional[int] = None) -> str:
        """采矿功能"""
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            player = await self.get_or_create_player(user_id, username, screen_name)
            now = datetime.now(timezone.utc)

            # 检查采矿冷却时间
            if player.last_mining_time:
                if player.last_mining_time.tzinfo is None:
                    player.last_mining_time = player.last_mining_time.replace(tzinfo=timezone.utc)
                cooldown = now - player.last_mining_time
                if cooldown.total_seconds() < 120:  # 2分钟冷却
                    remaining = 120 - int(cooldown.total_seconds())
                    return f"还需要等待{remaining}秒才能继续采矿。"

            # 根据境界决定可以去的矿区
            available_locations = [
                location for location, info in self.mining_locations.items()
                if self.realms.index(player.realm) >= self.realms.index(info["min_realm"])
            ]

            if not available_locations:
                return "当前境界无法采矿。"

            # 随机选择一个可用矿区
            location = random.choice(available_locations)
            location_info = self.mining_locations[location]

            # 检查灵力是否足够
            if player.spiritual_power < location_info["spirit_cost"]:
                return f"灵力不足，无法采矿。需要{location_info['spirit_cost']}点灵力。"

            # 消耗灵力
            player.spiritual_power -= location_info["spirit_cost"]
            player.last_mining_time = now

            # 计算获得的物品
            rewards_text = []
            if "materials" not in player.items:
                player.items["materials"] = {}

            for item, (min_amount, max_amount) in location_info["rewards"].items():
                if random.random() < 0.7:  # 70%概率获得物品
                    amount = random.randint(min_amount, max_amount)
                    if amount > 0:
                        player.items["materials"][item] = player.items["materials"].get(item, 0) + amount
                        rewards_text.append(f"{item} x{amount}")

            # 获得经验
            exp_gain = random.randint(*location_info["exp"])
            player.exp += exp_gain

            # 检查是否可以突破
            upgrade_message = ""
            current_realm_index = self.realms.index(player.realm)
            for i in range(current_realm_index + 1, len(self.realms)):
                next_realm = self.realms[i]
                if player.exp >= self.realm_exp[next_realm]:
                    player.realm = next_realm
                    player.max_spiritual_power += 50
                    player.spiritual_power = player.max_spiritual_power
                    upgrade_message = f"\n恭喜突破到{next_realm}!灵力上限提升至{player.max_spiritual_power}!"
                    break

            # 更新玩家数据
            await self.update_player(player)

            # 构建返回消息
            rewards_msg = "什么都没有获得" if not rewards_text else "获得: \n" + "\n".join(rewards_text)
            response_parts = [
                f"在{location}采矿成功!",
                rewards_msg,
                f"获得经验: {exp_gain}",
                f"消耗灵力: {location_info['spirit_cost']}",
                f"当前灵力: {player.spiritual_power}/{player.max_spiritual_power}"
            ]

            if upgrade_message:
                response_parts.append(upgrade_message)

            return "\n".join(response_parts)

        except Exception as e:
            self.logger.error(f"采矿错误: {e}", exc_info=True)
            raise
        

    # 铁匠铺
    async def buy_weapon(self, user_id: int, username: str, screen_name: str, weapon_name: str) -> str:
        """购买武器"""
        try:
            # 获取玩家数据
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 检查武器是否存在
            weapon_info = self.weapon_shop.get_weapon_info(weapon_name)
            if not weapon_info:
                return f"铁匠铺没有出售 {weapon_name} 这件武器。"

            # 检查购买要求
            can_buy, message = self.weapon_shop.check_requirements(player.realm, weapon_name)
            if not can_buy:
                return message

            # 检查灵石是否足够
            price = self.weapon_shop.get_price(weapon_name)
            all_materials = player.items.get("materials", {})

            for item, amount in all_materials.items():
                if item == "灵石":
                    if amount < price:
                        return f"灵石不足!购买 {weapon_name} 需要 {price} 灵石，你只有 {amount} 灵石。"

                    all_materials[item] = amount - price
                    break  

            # 更新玩家的材料
            player.items["materials"] = all_materials

            # 添加武器到背包
            if "weapons" not in player.items:
                player.items["weapons"] = {}
            player.items["weapons"][weapon_name] = weapon_info

            # 更新数据库
            await self.update_player(player)

            return (
                f"购买成功!\n"
                f"武器: {weapon_name}\n"
                f"品质: {weapon_info['rarity']}\n"
                f"攻击力: {weapon_info['attack']}\n"
                f"消耗灵石: {price}\n"
                f"剩余灵石: {player.items['灵石']}"
            )

        except Exception as e:
            logger.error(f"购买武器失败: {e}")
            return "购买武器失败，请稍后再试。"


    async def sell_materials(
        self, 
        user_id: int, 
        username: str, 
        screen_name: str,
        materials_name: str, 
        materials_amount: str,
        chat_id: int, 
        message_thread_id: Optional[int] = None
    ) -> str:
        """出售材料"""
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            # 获取玩家数据
            player = await self.get_or_create_player(user_id, username, screen_name)
            all_materials = player.items.get("materials", {})
            sell_value = 0
            value = 0

            for item, amount in all_materials.items():
                if item == materials_name:
                    if materials_amount > amount:
                        return f"材料不足! 你想要出售 {materials_name} x{materials_amount}, 但是你只有 {materials_name} x{amount}"
                    
                    sell_value = self.herb_values.get(item, 0) * materials_amount
                    value = self.herb_values.get(item, 0)
                    all_materials[item] = amount - materials_amount
                    all_materials["灵石"] += sell_value
                    break
            
            player.items["materials"] = all_materials

            await self.update_player(player)

            return (
                f"出售成功!\n"
                f"材料: {materials_name}\n"
                f"数量: {materials_amount}\n"
                f"价格: {value}\n"
                f"收入灵石: {sell_value}\n"
            )
        
        except Exception as e:
            logger.error(f"出售材料失败: {e}")
            return "出售材料失败，请稍后再试。"
        

    async def sell_all_materials(self, user_id: int, username: str, screen_name: str, chat_id: int, message_thread_id: Optional[int] = None) -> str:
        try:
            if not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            # 获取玩家数据
            player = await self.get_or_create_player(user_id, username, screen_name)
            materials = player.items.get("materials", {})
            total_sell_value = 0
            sold_items = []

            # 确保灵石键存在
            if "灵石" not in materials:
                materials["灵石"] = 0

            # 处理普通材料
            for item, amount in list(materials.items()):
                # 跳过副本材料、灵石和嵌套字典
                if item == 'challenge' or item == '灵石' or isinstance(amount, dict):
                    continue
                
                if amount > 0:
                    item_value = self.herb_values.get(item, 0)
                    sell_value = item_value * amount
                    total_sell_value += sell_value
                    sold_items.append((item, amount, item_value, sell_value))
                    materials[item] = 0

            # 增加灵石
            materials["灵石"] = materials.get("灵石", 0) + total_sell_value
            player.items["materials"] = materials

            # 更新玩家数据
            await self.update_player(player)

            # 构建返回消息
            if sold_items:
                sold_items_info = "\n".join(
                    [f"材料: {item}, 数量: {amount}, 单价: ||{item_value}||, 收入: ||{sell_value}||" 
                    for item, amount, item_value, sell_value in sold_items]
                )
                
                # 检查是否有副本材料
                if 'challenge' in materials and any(amount > 0 for amount in materials['challenge'].values()):
                    return (
                        f"出售普通材料成功!\n"
                        f"{sold_items_info}\n"
                        f"总收入灵石: {total_sell_value}\n"
                        f"\n注意：副本材料不可出售。"
                    )
                else:
                    return (
                        f"出售材料成功!\n"
                        f"{sold_items_info}\n"
                        f"总收入灵石: {total_sell_value}"
                    )
            else:
                # 检查是否只有副本材料
                if 'challenge' in materials and any(amount > 0 for amount in materials['challenge'].values()):
                    return "没有可出售的普通材料。\n注意：副本材料不可出售。"
                else:
                    return "没有可出售的材料。"

        except Exception as e:
            logger.error(f"出售材料失败: {e}")
            return "出售材料过程中出现异常，请稍后再试。"


    async def list_weapons(self, user_id: int, username: str, screen_name: str) -> str:
        """列出可购买的武器"""
        try:
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 获取玩家的灵石数量
            materials = player.items.get("materials", {})
            spirit_stones = materials.get('灵石', 0)
            
            # 只显示买得起的武器
            available_weapons = self.weapon_shop.list_available_weapons(player.realm, spirit_stones)
            
            weapon_list = [f"铁匠铺可出售的武器 (你的灵石: {spirit_stones}): \n"]
            
            if not available_weapons:
                weapon_list.append("暂无你能买得起的武器，努力修炼赚取灵石吧！")
            else:
                for weapon in available_weapons:
                    weapon_list.append(
                        f"✅ {weapon['name']}\n"
                        f"   品质: {weapon['rarity']}\n"
                        f"   攻击力: {weapon['attack']}\n"
                        f"   价格: {weapon['price']} 灵石\n"
                        f"   需求境界: {weapon['required_realm']}\n"
                        f"   描述: {weapon['description']}\n"
                    )

            return "\n".join(weapon_list)

        except Exception as e:
            logger.error(f"获取武器列表失败: {e}")
            return "获取武器列表失败，请稍后再试。"


    async def equip_weapon(self, user_id: int, username: str, screen_name: str, weapon_name: str) -> str:
        """装备武器"""
        try:
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 检查武器是否在背包中
            if "weapons" not in player.items or weapon_name not in player.items["weapons"]:
                return f"你没有 {weapon_name} 这件武器。"

            # 装备武器
            player.equipped_weapon = weapon_name
            await self.update_player(player)

            weapon = player.items["weapons"][weapon_name]
            return (
                f"成功装备 {weapon_name}\n"
                f"品质: {weapon.rarity}\n"
                f"攻击力: {weapon.attack}"
            )

        except Exception as e:
            logger.error(f"装备武器失败: {e}")
            return "装备武器失败，请稍后再试。"
        

    async def list_weapons_by_realm(self, user_id: int, username: str, screen_name: str, realm: str) -> str:
        """列出特定境界的武器"""
        try:
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 获取该境界的武器
            realm_weapons = [
                (name, weapon) for name, weapon in self.weapon_shop.weapons.items()
                if weapon["required_realm"] == realm
            ]
            
            if not realm_weapons:
                return f"没有找到 {realm} 的武器。"
            
            # 生成武器列表
            weapon_list = [f"{realm}可用武器: \n"]
            for name, weapon in realm_weapons:
                can_buy = self.weapon_shop.REALMS.index(player.realm) >= self.weapon_shop.REALMS.index(realm)
                status = "✅" if can_buy else "❌"
                
                weapon_list.append(
                    f"{status} {name}\n"
                    f"   品质: {weapon['rarity']}\n"
                    f"   类型: {weapon['type']}\n"
                    f"   攻击力: {weapon['attack']}\n"
                    f"   价格: {weapon['price']} 灵石\n"
                    f"   描述: {weapon['description']}\n"
                )
            
            return "\n".join(weapon_list)
            
        except Exception as e:
            logger.error(f"获取境界武器列表失败: {e}")
            return "获取武器列表失败，请稍后再试。"


    async def get_leaderboard(self) -> str:
        """获取排行榜前20名"""
        try:
            # 获取排行榜数据
            players = await get_leaderboard(limit=20)

            # 构建排行榜文本
            leaderboard_text = "🏆 修仙界排行榜 TOP20 🏆\n\n"
            
            for idx, player in enumerate(players, 1):
                username = player.get('screen_name', '无名修士')
                realm = player.get('realm', '练气期')
                exp = player.get('exp', 0)
                
                # 为前三名添加特殊标记
                rank_icon = {
                    1: "🥇",
                    2: "🥈",
                    3: "🥉"
                }.get(idx, f"{idx}.")

                # 添加玩家信息到排行榜
                leaderboard_text += (
                    f"{rank_icon} {username}\n"
                    f"境界: {realm} | 修为: {exp:,}\n"
                    f"{'─' * 20}\n"
                )

            return leaderboard_text

        except Exception as e:
            self.logger.error(f"获取排行榜失败: {e}")
            return "获取排行榜失败，请稍后再试。"


    # 艾斯维尔副本

    def check_realm_requirement(self, current_realm: str, required_realm: str) -> bool:
        """检查境界要求"""
        realm_levels = {
            "练气期": 1,
            "筑基期": 2,
            "金丹期": 3,
            "元婴期": 4,
            "化神期": 5,
            "炼虚期": 6,
            "合体期": 7,
            "大乘期": 8,
            "渡劫期": 9
        }
        
        # 获取当前境界和要求境界的等级
        current_level = realm_levels.get(current_realm, 0)
        required_level = realm_levels.get(required_realm, 0)
        
        # 如果找不到对应的境界等级，返回False
        if current_level == 0 or required_level == 0:
            return False
        
        # 返回当前境界是否大于等于要求境界
        return current_level >= required_level

    def get_realm_name(self, level: int) -> str:
        """根据等级获取境界名称"""
        realm_levels = {
            1: "练气期",
            2: "筑基期",
            3: "金丹期",
            4: "元婴期",
            5: "化神期",
            6: "炼虚期",
            7: "合体期",
            8: "大乘期",
            9: "渡劫期"
        }
        return realm_levels.get(level, "未知境界")


    async def challenge_elsevier(
        self,
        user_id: int,
        username: str,
        screen_name: str,
        stage_name: str = None,
        chat_id: int = None,
        message_thread_id: Optional[int] = None
    ) -> str:
        """挑战爱思唯尔秘境"""
        try:
            if chat_id and not self.check_channel_permission(chat_id, message_thread_id):
                return self.format_error_message(chat_id)

            # 获取玩家数据
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            # 如果没有指定副本名称，显示所有可用副本
            if not stage_name or stage_name.strip() == "":
                stage_list = ["🏛️ 爱思唯尔秘境 - 可用副本：\n"]
                
                for name, stage_info in self.elsevier_dungeon["stages"].items():
                    can_challenge = self.check_realm_requirement(player.realm, stage_info["min_realm"])
                    status = "✅" if can_challenge else "❌"
                    
                    # 获取副本类型描述
                    stage_type = "Boss战" if "boss" in stage_info else "普通副本"
                    
                    stage_list.append(
                        f"{status} {name}\n"
                        f"   需求境界: {stage_info['min_realm']}\n"
                        f"   消耗灵力: {stage_info['spirit_cost']}\n"
                        f"   类型: {stage_type}\n"
                    )
                
                stage_list.append("\n使用方法：/elsevier 副本名称")
                return "\n".join(stage_list)
            
            now = datetime.now(timezone.utc)

            # 检查冷却时间
            if player.last_challenge_time:
                if player.last_challenge_time.tzinfo is None:
                    player.last_challenge_time = player.last_challenge_time.replace(tzinfo=timezone.utc)
                cooldown = now - player.last_challenge_time
                if cooldown.total_seconds() < 600:  # 10分钟冷却
                    remaining = 600 - int(cooldown.total_seconds())
                    return f"还需要等待{remaining}秒才能继续挑战。"

            # 获取副本阶段信息
            stage = self.elsevier_dungeon["stages"].get(stage_name)
            if not stage:
                available_stages = "、".join(self.elsevier_dungeon["stages"].keys())
                return (
                    f"未找到名为 {stage_name} 的关卡。\n"
                    f"可用关卡：{available_stages}"
                )

            # 检查境界要求
            if not self.check_realm_requirement(player.realm, stage["min_realm"]):
                return (
                    f"境界不足！\n"
                    f"当前境界：{player.realm}\n"
                    f"需要境界：{stage['min_realm']} 及以上"
                )

            # 检查灵力值
            if player.spiritual_power < stage["spirit_cost"]:
                return f"灵力不足！需要 {stage['spirit_cost']} 灵力，当前灵力：{player.spiritual_power}"

            # 扣除灵力
            player.spiritual_power -= stage["spirit_cost"]
            player.last_challenge_time = now

            # 战斗逻辑
            battle_log = []
            player_hp = player.max_hp

            # 如果是boss关
            if "boss" in stage:
                boss = stage["boss"].copy()  # 创建副本避免修改原始数据
                battle_log.append(f"【Boss战】你遇到了 {boss['name']}!")
                
                while player_hp > 0 and boss["hp"] > 0:
                    # 玩家攻击
                    damage = max(1, int(player.total_attack) - boss["defense"])
                    boss["hp"] -= damage
                    battle_log.append(f"你对 {boss['name']} 造成了 {damage} 点伤害！")
                    
                    if boss["hp"] <= 0:
                        break
                    
                    # Boss技能攻击
                    skill = random.choice(boss["skills"])
                    damage = max(1, skill["damage"] - player.defense)
                    player_hp -= damage
                    battle_log.append(f"{boss['name']} 使用 {skill['name']}，对你造成了 {damage} 点伤害！")
            else:
                # 普通怪物战斗
                for monster in stage["monsters"]:
                    monster_hp = monster["hp"]
                    battle_log.append(f"你遇到了 {monster['name']}!")
                    
                    while player_hp > 0 and monster_hp > 0:
                        # 玩家攻击
                        damage = max(1, int(player.total_attack) - monster["defense"])
                        monster_hp -= damage
                        battle_log.append(f"你对 {monster['name']} 造成了 {damage} 点伤害！")
                        
                        if monster_hp <= 0:
                            break
                        
                        # 怪物攻击
                        damage = max(1, monster["attack"] - player.defense)
                        player_hp -= damage
                        battle_log.append(f"{monster['name']} 对你造成了 {damage} 点伤害！")

            # 战斗结果处理
            if player_hp <= 0:
                await self.update_player(player)
                return "挑战失败！\n" + "\n".join(battle_log)

            # 获取奖励
            rewards = self.get_stage_rewards(stage["rewards"])
            
            # 更新玩家数据
            player.exp += rewards["exp"]

            if 'materials' not in player.items:
                player.items['materials'] = {}
            if 'challenge' not in player.items['materials']:
                player.items['materials']['challenge'] = {}

            # 将奖励物品存入 'materials' -> 'challenge'
            for item, amount in rewards["items"].items():
                if item == "灵石":
                    player.items['materials']['灵石'] += amount
                else:
                    if item not in player.items['materials']['challenge']:
                        player.items['materials']['challenge'][item] = amount
                    else:
                        player.items['materials']['challenge'][item] += amount

            await self.update_player(player)

            # 构建返回消息
            reward_msg = []
            # 添加战斗日志
            reward_msg.extend(battle_log)
            # 添加奖励信息
            reward_msg.append("\n挑战成功!")
            reward_msg.append(f"获得经验：{rewards['exp']}")
            reward_msg.append("获得物品：")
            for item, amount in rewards["items"].items():
                reward_msg.append(f"- {item} x{amount}")

            return "\n".join(reward_msg)

        except Exception as e:
            logger.error(f"爱思唯尔副本挑战失败: {e}")
            return "副本挑战失败，请稍后再试。"


    def get_stage_rewards(self, reward_config):
        """获取副本奖励"""
        try:
            rewards = {
                "exp": random.randint(*reward_config["exp"]),
                "items": {}
            }

            # 处理物品奖励
            for item, value in reward_config["items"].items():
                # 跳过稀有道具键，稍后处理
                if item == "稀有道具":
                    continue
                    
                # 处理普通物品（数量范围元组）
                if isinstance(value, tuple) and len(value) == 2:
                    min_amount, max_amount = value
                    rewards["items"][item] = random.randint(min_amount, max_amount)

            # 处理稀有道具
            if "稀有道具" in reward_config["items"]:
                rare_items = reward_config["items"]["稀有道具"]
                for item, chance in rare_items.items():
                    if random.random() < chance:
                        rewards["items"][item] = 1

            return rewards
        except Exception as e:
            logger.error(f"获取副本奖励失败: {e}")
            logger.error(f"奖励配置: {reward_config}")
            # 返回默认奖励
            return {
                "exp": 0,
                "items": {}
            }

    async def visit_shop(self, user_id: int, username: str, screen_name: str) -> str:
        """访问杂货铺"""
        try:
            player = await self.get_or_create_player(user_id, username, screen_name)
            
            shop_items = {
                "回血丹": {"price": 50, "description": "恢复100点生命值"},
                "回气丹": {"price": 30, "description": "恢复50点法力值"},
                "经验丹": {"price": 100, "description": "获得50点经验值"},
                "灵石袋": {"price": 200, "description": "获得100灵石"}
            }
            
            materials = player.items.get("materials", {})
            spirit_stones = materials.get('灵石', 0)
            
            shop_msg = ["🏪 杂货铺"]
            shop_msg.append(f"你的灵石：{spirit_stones}")
            shop_msg.append("\n商品列表：")
            
            for item, info in shop_items.items():
                shop_msg.append(f"• {item} - {info['price']}灵石")
                shop_msg.append(f"  {info['description']}")
            
            shop_msg.append("\n使用方法：/buy 物品名称")
            
            return "\n".join(shop_msg)
            
        except Exception as e:
            logger.error(f"访问杂货铺失败: {e}")
            return "杂货铺暂时关闭，请稍后再试。"

    async def enhance_weapon(self, user_id: int, username: str, screen_name: str, weapon_name: str) -> str:
        """强化武器"""
        try:
            from bot.weapon_enhancement import WeaponEnhancement
            
            player = await self.get_or_create_player(user_id, username, screen_name)
            enhancement = WeaponEnhancement()
            
            result = await enhancement.enhance_weapon(player, self.update_player, weapon_name)
            return result
            
        except Exception as e:
            logger.error(f"强化武器失败: {e}")
            return "强化过程出现异常，请稍后再试。"

    async def check_weapon(self, user_id: int, username: str, screen_name: str) -> str:
        """查看武器信息"""
        try:
            from bot.weapon_enhancement import WeaponEnhancement
            
            player = await self.get_or_create_player(user_id, username, screen_name)
            enhancement = WeaponEnhancement()
            
            if 'weapons' not in player.items or not player.items['weapons']:
                return "你还没有任何武器！"
            
            # 显示所有武器信息
            weapon_info = ["🗡️ 你的武器："]
            
            for weapon_name, weapon in player.items['weapons'].items():
                equipped_mark = "⚔️" if weapon_name == player.equipped_weapon else "📦"
                weapon_info.append(f"{equipped_mark} {weapon_name}")
                weapon_info.append(f"  攻击力：{weapon.attack}")
                weapon_info.append(f"  强化等级：+{weapon.enhancement_level}")
                weapon_info.append(f"  品质：{weapon.quality}")
                weapon_info.append("")
            
            return "\n".join(weapon_info)
            
        except Exception as e:
            logger.error(f"查看武器失败: {e}")
            return "获取武器信息失败，请稍后再试。"