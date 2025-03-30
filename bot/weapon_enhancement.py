import random
import logging

logger = logging.getLogger(__name__)


class WeaponEnhancement:
    def __init__(self):
        # 强化概率配置 (等级: 成功率)
        self.enhancement_rates = {
            0: 100,  # 0->1 100%
            1: 95,   # 1->2 95%
            2: 90,   # 2->3 90%
            3: 85,   # 3->4 85%
            4: 80,   # 4->5 80%
            5: 75,   # 5->6 75%
            6: 70,   # 6->7 70%
            7: 65,   # 7->8 65%
            8: 60,   # 8->9 60%
            9: 55,   # 9->10 55%
            10: 50,  # 10->11 50%
            11: 30,  # 11->12 35%
            12: 20,  # 12->13 20%
            13: 10,  # 13->14 10%
            14: 5,  # 14->15 5%
            15: 4,
            16: 3,
            17: 3,
            18: 2,
            19: 1,
            20: 1
        }
        
        # 强化费用配置 (等级: 灵石数量)
        self.enhancement_costs = {
            0: 100,    # 0->1 100灵石
            1: 200,    # 1->2 200灵石
            2: 300,    # 2->3 300灵石
            3: 450,    # 3->4 450灵石
            4: 600,    # 4->5 600灵石
            5: 800,    # 5->6 800灵石
            6: 1000,   # 6->7 1000灵石
            7: 1500,   # 7->8 1500灵石
            8: 2000,   # 8->9 2000灵石
            9: 2500,   # 9->10 2500灵石
            10: 3000,  # 10->11 3000灵石
            11: 4000,  # 11->12 4000灵石
            12: 5000,  # 12->13 5000灵石
            13: 7000,  # 13->14 7000灵石
            14: 10000, # 14->15 10000灵石
            15: 15000,
            16: 20000,
            17: 25000,
            18: 30000,
            19: 35000,
            20: 40000
        }
        
        # 强化攻击力加成 (等级: 攻击力加成)
        self.enhancement_attack_bonus = {
            1: 10,     # +1 增加10攻击
            2: 25,     # +2 增加25攻击
            3: 45,     # +3 增加45攻击
            4: 70,     # +4 增加70攻击
            5: 100,    # +5 增加100攻击
            6: 135,    # +6 增加135攻击
            7: 175,    # +7 增加175攻击
            8: 220,    # +8 增加220攻击
            9: 270,    # +9 增加270攻击
            10: 325,   # +10 增加325攻击
            11: 385,   # +11 增加385攻击
            12: 450,   # +12 增加450攻击
            13: 520,   # +13 增加520攻击
            14: 595,   # +14 增加595攻击
            15: 675,   # +15 增加675攻击
            16: 760,   # +16 增加760攻击
            17: 850,   # +17 增加850攻击
            18: 945,   # +18 增加945攻击
            19: 1045,  # +19 增加1045攻击
            20: 1150   # +20 增加1150攻击
        }

    async def enhance_weapon(self, player, update_player, weapon_name: str) -> str:
        """强化武器"""
        try:
            if 'weapons' not in player.items:
                return "你还没有任何武器！"

            if weapon_name not in player.items['weapons']:
                return f"你没有名为 {weapon_name} 的武器！"

            weapon = player.items['weapons'][weapon_name]

            # 检查武器是否已达到最高强化等级
            current_enhancement = weapon.enhancement_level
            if current_enhancement >= 20:
                return f"【{weapon_name}】已达到最高强化等级+20!"

            # 获取强化费用和成功率
            cost = self.enhancement_costs[current_enhancement]
            success_rate = self.enhancement_rates[current_enhancement]

            # 检查灵石是否足够
            materials = player.items.get("materials", {})
            spirit_stones = materials.get('灵石', 0)

            if spirit_stones < cost:
                return f"灵石不足！强化到+{current_enhancement + 1}需要{cost}灵石，当前灵石：{spirit_stones}"

            # 扣除灵石
            materials["灵石"] -= cost

            # 随机判断是否强化成功
            if random.randint(1, 100) <= success_rate:
                # 强化成功
                new_level = current_enhancement + 1
                old_attack = weapon.attack
                attack_bonus = self.enhancement_attack_bonus[new_level]

                # 更新武器数据
                weapon.enhancement_level = new_level
                weapon.attack = old_attack + attack_bonus
                player.items['weapons'][weapon_name] = weapon

                # 更新玩家数据
                await update_player(player)

                return (
                    f"✨ 强化成功！\n"
                    f"武器：{weapon_name}\n"
                    f"等级：+{current_enhancement} → +{new_level}\n"
                    f"攻击力：{old_attack} → {old_attack + attack_bonus}\n"
                    f"消耗灵石：{cost}\n"
                    f"剩余灵石：{materials.get('灵石', 0)}"
                )
            else:
                # 强化失败
                await update_player(player)
                return (
                    f"💔 强化失败！\n"
                    f"武器：{weapon_name}\n"
                    f"等级：+{current_enhancement}\n"
                    f"消耗灵石：{cost}\n"
                    f"剩余灵石：{materials.get('灵石', 0)}"
                )
        except Exception as e:
            logger.error(f"强化武器失败: {e}")
            return "强化过程出现异常，请稍后再试。"
        

    # 添加查看武器信息的功能
    async def check_weapon(
        self,
        player,
        weapon_name: str = None
    ) -> str:
        """查看武器信息"""
        try:
            
            if 'weapons' not in player.items:
                return "你还没有任何武器！"
                
            if weapon_name:
                # 查看指定武器
                if weapon_name not in player.items['weapons']:
                    return f"你没有名为 {weapon_name} 的武器！"
                    
                weapon = player.items['weapons'][weapon_name]
                current_level = weapon.enhancement_level
                
                # 如果不是最高等级，显示下一级强化信息
                next_level_info = ""
                if current_level < 15:
                    next_level_info = (
                        f"\n━━━ 下一级强化信息 ━━━\n"
                        f"强化费用：{self.enhancement_costs[current_level]}灵石\n"
                        f"成功概率：{self.enhancement_rates[current_level]}%\n"
                        f"攻击加成：+{self.enhancement_attack_bonus[current_level + 1]}"
                    )
                
                return (
                    f"🗡️ 武器信息\n"
                    f"名称：{weapon_name}\n"
                    f"等级：+{current_level}\n"
                    f"攻击力：{weapon.attack}"
                    f"{next_level_info}"
                )
            else:
                # 查看所有武器
                if not player.items['weapons']:
                    return "你还没有任何武器！"
                    
                weapons_info = ["📚 武器列表："]
                for name, weapon in player.items['weapons'].items():
                    weapons_info.append(
                        f"\n{name}: \n"
                        f"等级：+{weapon.enhancement_level}\n"
                        f"攻击力：{weapon.attack}"
                    )
                
                return "\n".join(weapons_info)
                
        except Exception as e:
            logger.error(f"查看武器信息失败: {e}")
            return "获取武器信息失败，请稍后再试。"