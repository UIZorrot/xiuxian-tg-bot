from typing import Dict, Optional, List, Tuple

class WeaponShop:
    # 境界等级
    REALMS = ["练气期", "筑基期", "金丹期", "元婴期", "化神期", "炼虚期", "合体期", "大乘期", "渡劫期"]

    def __init__(self):
        # 武器商店数据
        self.weapons = {
            # 练气期
            "天青木剑": {
                "price": 150,
                "attack": 15,
                "description": "以天青古木精炼而成，轻便锋利。",
                "required_realm": "练气期",
                "type": "剑",
                "rarity": "普通",
                "enhancement_level": 0
            },
            "炎阳刀": {
                "price": 250,
                "attack": 20,
                "description": "刀锋炽热，似带炎阳之力。",
                "required_realm": "练气期",
                "type": "刀",
                "rarity": "精良",
                "enhancement_level": 0
            },
            "寒冰枪": {
                "price": 300,
                "attack": 25,
                "description": "枪尖凝霜，挥舞间寒气袭人。",
                "required_realm": "练气期",
                "type": "枪",
                "rarity": "稀有",
                "enhancement_level": 0
            },

            # 筑基期
            "裂山斧": {
                "price": 500,
                "attack": 40,
                "description": "沉重如山，传闻可裂地开山。",
                "required_realm": "筑基期",
                "type": "斧",
                "rarity": "普通",
                "enhancement_level": 0
            },
            "紫电剑": {
                "price": 700,
                "attack": 50,
                "description": "剑身闪烁紫电，出手时雷鸣阵阵。",
                "required_realm": "筑基期",
                "type": "剑",
                "rarity": "精良",
                "enhancement_level": 0
            },
            "烈焰戟": {
                "price": 800,
                "attack": 60,
                "description": "枪戟通红，似含烈焰焚烧之力。",
                "required_realm": "筑基期",
                "type": "戟",
                "rarity": "稀有",
                "enhancement_level": 0
            },

            # 金丹期
            "龙纹剑": {
                "price": 1200,
                "attack": 80,
                "description": "剑身刻有龙纹，挥动间龙吟隐现。",
                "required_realm": "金丹期",
                "type": "剑",
                "rarity": "精良",
                "enhancement_level": 0
            },
            "星陨锤": {
                "price": 1400,
                "attack": 90,
                "description": "以陨星炼制而成，力量强横。",
                "required_realm": "金丹期",
                "type": "锤",
                "rarity": "稀有",
                "enhancement_level": 0
            },
            "天罡枪": {
                "price": 1600,
                "attack": 100,
                "description": "枪势如罡风，震慑敌人。",
                "required_realm": "金丹期",
                "type": "枪",
                "rarity": "稀有",
                "enhancement_level": 0
            },

            # 元婴期
            "赤霄剑": {
                "price": 2000,
                "attack": 130,
                "description": "赤霄天火铸就，剑气如火焰焚烧。",
                "required_realm": "元婴期",
                "type": "剑",
                "rarity": "稀有",
                "enhancement_level": 0
            },
            "青虹刀": {
                "price": 2500,
                "attack": 150,
                "description": "刀芒如虹，青光直贯九霄。",
                "required_realm": "元婴期",
                "type": "刀",
                "rarity": "稀有",
                "enhancement_level": 0
            },
            "黑龙戟": {
                "price": 3000,
                "attack": 180,
                "description": "戟形似黑龙，气势滔天。",
                "required_realm": "元婴期",
                "type": "戟",
                "rarity": "史诗",
                "enhancement_level": 0
            },

            # 化神期
            "九阳剑": {
                "price": 4000,
                "attack": 200,
                "description": "剑意灼热如九阳，焚尽世间一切。",
                "required_realm": "化神期",
                "type": "剑",
                "rarity": "史诗",
                "enhancement_level": 0
            },
            "寒魄枪": {
                "price": 4500,
                "attack": 220,
                "description": "冰冷刺骨，贯穿虚空。",
                "required_realm": "化神期",
                "type": "枪",
                "rarity": "史诗",
                "enhancement_level": 0
            },
            "破天锤": {
                "price": 5000,
                "attack": 250,
                "description": "巨锤挥动，似可破碎苍穹。",
                "required_realm": "化神期",
                "type": "锤",
                "rarity": "传说",
                "enhancement_level": 0
            },

            # 炼虚期
            "混元剑": {
                "price": 6000,
                "attack": 300,
                "description": "剑意混元，无坚不摧。",
                "required_realm": "炼虚期",
                "type": "剑",
                "rarity": "传说",
                "enhancement_level": 0
            },
            "赤雷刀": {
                "price": 6500,
                "attack": 320,
                "description": "刀刃含雷火之威，劈开天地。",
                "required_realm": "炼虚期",
                "type": "刀",
                "rarity": "传说",
                "enhancement_level": 0
            },
            "玄光戟": {
                "price": 7000,
                "attack": 350,
                "description": "戟刃玄光流转，斩尽妖魔。",
                "required_realm": "炼虚期",
                "type": "戟",
                "rarity": "传说",
                "enhancement_level": 0
            },

            # 合体期
            "天道剑": {
                "price": 8000,
                "attack": 400,
                "description": "剑意合天道，挥剑即天地动荡。",
                "required_realm": "合体期",
                "type": "剑",
                "rarity": "传说",
                "enhancement_level": 0
            },
            "灭世刀": {
                "price": 8500,
                "attack": 450,
                "description": "刀势可灭世，霸气无双。",
                "required_realm": "合体期",
                "type": "刀",
                "rarity": "传说",
                "enhancement_level": 0
            },
            "苍穹锤": {
                "price": 9000,
                "attack": 500,
                "description": "巨锤挥动如天穹坠落。",
                "required_realm": "合体期",
                "type": "锤",
                "rarity": "传说",
                "enhancement_level": 0
            },

            # 大乘期
            "神霄剑": {
                "price": 10000,
                "attack": 600,
                "description": "剑芒如神霄雷霆，震慑万界。",
                "required_realm": "大乘期",
                "type": "剑",
                "rarity": "神品",
                "enhancement_level": 0
            },
            "万劫枪": {
                "price": 11000,
                "attack": 650,
                "description": "一枪出万劫，岁月无光。",
                "required_realm": "大乘期",
                "type": "枪",
                "rarity": "神品",
                "enhancement_level": 0
            },
            "乾坤戟": {
                "price": 12000,
                "attack": 700,
                "description": "戟势如乾坤翻覆，万物化虚。",
                "required_realm": "大乘期",
                "type": "戟",
                "rarity": "神品",
                "enhancement_level": 0
            },

            # 渡劫期
            "轮回剑": {
                "price": 15000,
                "attack": 800,
                "description": "剑意蕴轮回之力，可断生死。",
                "required_realm": "渡劫期",
                "type": "剑",
                "rarity": "神器",
                "enhancement_level": 0
            },
            "灭天刀": {
                "price": 16000,
                "attack": 850,
                "description": "刀意滔天，可灭苍穹。",
                "required_realm": "渡劫期",
                "type": "刀",
                "rarity": "神器",
                "enhancement_level": 0
            },
            "混沌锤": {
                "price": 17000,
                "attack": 900,
                "description": "混沌初开之力，锤碎乾坤。",
                "required_realm": "渡劫期",
                "type": "锤",
                "rarity": "神器",
                "enhancement_level": 0
            },
        }

    def get_weapon_info(self, weapon_name: str) -> Optional[Dict]:
        """获取武器信息"""
        return self.weapons.get(weapon_name)

    def check_requirements(self, player_realm: str, weapon_name: str) -> Tuple[bool, str]:
        """检查购买要求"""
        weapon = self.weapons.get(weapon_name)
        if not weapon:
            return False, f"未找到武器：{weapon_name}"

        if self.REALMS.index(player_realm) < self.REALMS.index(weapon["required_realm"]):
            return False, f"境界不足，需要 {weapon['required_realm']} 境界"

        return True, "满足要求"

    def get_price(self, weapon_name: str) -> int:
        """获取武器价格"""
        weapon = self.weapons.get(weapon_name)
        return weapon["price"] if weapon else 0

    def list_available_weapons(self, player_realm: str, player_spirit_stones: int = None) -> List[Dict]:
        """获取可用武器列表"""
        available_weapons = []
        for name, weapon in self.weapons.items():
            can_buy = self.REALMS.index(player_realm) >= self.REALMS.index(weapon["required_realm"])
            
            # 如果提供了灵石数量，只显示买得起的武器
            if player_spirit_stones is not None:
                can_afford = player_spirit_stones >= weapon["price"]
                if not (can_buy and can_afford):
                    continue
            
            weapon_info = weapon.copy()
            weapon_info["name"] = name
            weapon_info["can_buy"] = can_buy
            available_weapons.append(weapon_info)
        return available_weapons