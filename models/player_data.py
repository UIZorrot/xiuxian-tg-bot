from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from .weapon_data import WeaponData

@dataclass
class PlayerData:
    """玩家数据类"""
    user_id: int
    username: str
    screen_name: str
    realm: str = "练气期"
    exp: int = 0
    spiritual_power: int = 100
    max_spiritual_power: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 5
    items: Dict[str, Any] = field(default_factory=lambda: {
        "灵石": 0,
        "weapons": {},
        "materials": {}
    })
    equipped_weapon: Optional[str] = None
    last_meditation_time: Optional[datetime] = None
    last_herb_gathering_time: Optional[datetime] = None
    last_mining_time: Optional[datetime] = None
    last_challenge_time: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerData':
        """从字典创建实例"""
        cleaned_data = {
            'user_id': data.get('user_id'),
            'username': data.get('username'),
            'screen_name': data.get('screen_name'),
            'realm': data.get('realm', "练气期"),
            'exp': data.get('exp', 0),
            'spiritual_power': data.get('spiritual_power', 100),
            'max_hp': data.get('max_hp', 100),
            'max_spiritual_power': data.get('max_spiritual_power', 100),
            'attack': data.get('attack', 10),
            'defense': data.get('defense', 5),
            'items': data.get('items', {
                "灵石": 0,
                "weapons": {},
                "materials": {}
            }),
            'equipped_weapon': data.get('equipped_weapon'),
            'last_meditation_time': data.get('last_meditation_time'),
            'last_herb_gathering_time': data.get('last_herb_gathering_time'),
            'last_mining_time': data.get('last_mining_time'),
            'last_challenge_time': data.get('last_challenge_time'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at')
        }

        # 处理武器数据
        if 'weapons' in data:
            # 如果 weapons 是顶级字段
            weapons_data = data['weapons']
            if isinstance(weapons_data, dict):
                cleaned_data['items']['weapons'] = {
                    name: WeaponData.from_dict(weapon_data)
                    for name, weapon_data in weapons_data.items()
                }
        elif 'items' in data and isinstance(data['items'], dict):
            # 如果 weapons 在 items 字段中
            weapons_data = data['items'].get('weapons', {})
            if isinstance(weapons_data, dict):
                cleaned_data['items']['weapons'] = {
                    name: WeaponData.from_dict(weapon_data)
                    for name, weapon_data in weapons_data.items()
                }

        return cls(**cleaned_data)

    def __post_init__(self):
        """后初始化处理"""
        # 确保 items 是字典
        if self.items is None:
            self.items = {
                "灵石": 0,
                "weapons": {},
                "materials": {}
            }

        # 处理时间字段
        time_fields = [
            'last_meditation_time',
            'last_herb_gathering_time',
            'last_mining_time',
            'last_challenge_time',
            'created_at',
            'updated_at'
        ]
        
        for field_name in time_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    setattr(self, field_name, dt)
                except (ValueError, TypeError):
                    setattr(self, field_name, None)
            elif isinstance(value, datetime) and value.tzinfo is None:
                setattr(self, field_name, value.replace(tzinfo=timezone.utc))


    @property
    def total_attack(self) -> int:
        """计算总攻击力"""
        base_attack = self.attack
        if self.equipped_weapon and self.equipped_weapon in self.items["weapons"]:
            weapon = self.items["weapons"][self.equipped_weapon]
            base_attack += weapon.attack
        return base_attack


    def add_weapon(self, weapon: WeaponData) -> None:
        """添加武器到背包"""
        if "weapons" not in self.items:
            self.items["weapons"] = {}
        self.items["weapons"][weapon.name] = weapon


    def remove_weapon(self, weapon_name: str) -> Optional[WeaponData]:
        """从背包中移除武器"""
        if weapon_name in self.items["weapons"]:
            weapon = self.items["weapons"].pop(weapon_name)
            if self.equipped_weapon == weapon_name:
                self.equipped_weapon = None
            return weapon
        return None


    def get_weapon(self, weapon_name: str) -> Optional[WeaponData]:
        """获取背包中的武器"""
        return self.items["weapons"].get(weapon_name)


    def get_all_weapons(self) -> Dict[str, WeaponData]:
        """获取所有武器"""
        return self.items["weapons"]


    def equip_weapon(self, weapon_name: str) -> bool:
        """装备武器"""
        if weapon_name in self.items["weapons"]:
            self.equipped_weapon = weapon_name
            return True
        return False


    def unequip_weapon(self) -> Optional[str]:
        """卸下当前装备的武器"""
        previous_weapon = self.equipped_weapon
        self.equipped_weapon = None
        return previous_weapon


    def get_equipped_weapon(self) -> Optional[WeaponData]:
        """获取当前装备的武器"""
        if self.equipped_weapon:
            return self.items["weapons"].get(self.equipped_weapon)
        return None


    def has_enough_spirit_stones(self, amount: int) -> bool:
        """检查灵石是否足够"""
        return self.items.get("灵石", 0) >= amount


    def spend_spirit_stones(self, amount: int) -> bool:
        """消费灵石"""
        if self.has_enough_spirit_stones(amount):
            self.items["灵石"] = self.items.get("灵石", 0) - amount
            return True
        return False


    def add_spirit_stones(self, amount: int) -> None:
        """添加灵石"""
        self.items["灵石"] = self.items.get("灵石", 0) + amount


    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于保存到 Supabase"""
        data = {
            'user_id': self.user_id,
            'username': self.username,
            'screen_name': self.screen_name,
            'realm': self.realm,
            'exp': self.exp,
            'spiritual_power': self.spiritual_power,
            'max_hp': self.max_hp,
            'max_spiritual_power': self.max_spiritual_power,
            'attack': self.attack,
            'defense': self.defense,
            'equipped_weapon': self.equipped_weapon,
        }

        # 处理时间字段
        time_fields = [
            'last_meditation_time',
            'last_herb_gathering_time',
            'last_mining_time',
            'last_challenge_time',
            'created_at',
            'updated_at'
        ]
        
        for field in time_fields:
            value = getattr(self, field)
            if isinstance(value, datetime):
                if value.tzinfo is None:
                    value = value.replace(tzinfo=timezone.utc)
                data[field] = value.isoformat()
            else:
                data[field] = value

        # 处理 items JSONB 字段
        data['items'] = {
            "灵石": self.items.get("灵石", 0),
            "materials": self.items.get("materials", {}),
            "weapons": {}
        }

        # 处理武器数据
        weapons = self.items.get("weapons", {})
        for name, weapon in weapons.items():
            if hasattr(weapon, 'to_dict'):
                # 如果是 WeaponData 对象
                data['items']["weapons"][name] = weapon.to_dict()
            elif isinstance(weapon, dict):
                # 如果已经是字典格式
                data['items']["weapons"][name] = weapon
            else:
                # 其他情况，尝试转换为字典
                try:
                    data['items']["weapons"][name] = {
                        'name': getattr(weapon, 'name', name),
                        'type': getattr(weapon, 'type', '武器'),
                        'attack': getattr(weapon, 'attack', 0),
                        'rarity': getattr(weapon, 'rarity', '普通'),
                        'description': getattr(weapon, 'description', ''),
                        'required_realm': getattr(weapon, 'required_realm', '练气期'),
                        'enhancement_level': getattr(weapon, 'enhancement_level', 0)
                    }
                except Exception as e:
                    # 使用默认值
                    data['items']["weapons"][name] = {
                        'name': name,
                        'type': '武器',
                        'attack': 0,
                        'rarity': '普通',
                        'description': ''
                    }

        return data


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerData':
        """从字典创建实例，处理 Supabase JSONB 数据"""

        # 创建一个新的数据字典，只包含类所需的字段
        cleaned_data = {
            'user_id': data.get('user_id'),
            'username': data.get('username'),
            'screen_name': data.get('screen_name'),
            'realm': data.get('realm', "练气期"),
            'exp': data.get('exp', 0),
            'spiritual_power': data.get('spiritual_power', 100),
            'max_spiritual_power': data.get('max_spiritual_power', 100),
            'max_hp': data.get('max_hp', 100),
            'attack': data.get('attack', 10),
            'defense': data.get('defense', 5),
            'equipped_weapon': data.get('equipped_weapon'),
            'last_meditation_time': data.get('last_meditation_time'),
            'last_herb_gathering_time': data.get('last_herb_gathering_time'),
            'last_mining_time': data.get('last_mining_time'),
            'last_challenge_time': data.get('last_challenge_time'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at'),
        }

        # 初始化默认的 items 结构
        cleaned_data['items'] = {
            "灵石": 0,
            "weapons": {},
            "materials": {}
        }

        # 处理 JSONB items 字段
        if 'items' in data:
            db_items = data['items']
            if isinstance(db_items, dict):
                # 处理灵石
                if "灵石" in db_items:
                    cleaned_data['items']["灵石"] = db_items["灵石"]
                
                # 处理材料
                if "materials" in db_items:
                    cleaned_data['items']["materials"] = db_items["materials"]
                
                # 处理武器
                if "weapons" in db_items:
                    weapons_data = db_items["weapons"]
                    if isinstance(weapons_data, dict):
                        cleaned_data['items']["weapons"] = {}
                        for name, weapon_data in weapons_data.items():
                            try:
                                if isinstance(weapon_data, dict):
                                    # 尝试创建 WeaponData 对象
                                    weapon_data['name'] = weapon_data.get('name', name)
                                    weapon_data['price'] = weapon_data.get('price', 0)
                                    weapon_data['required_realm'] = weapon_data.get('required_realm', '练气期')
                                    weapon_data['enhancement_level'] = weapon_data.get('enhancement_level', 0)
                                    cleaned_data['items']["weapons"][name] = WeaponData.from_dict(weapon_data)
                                else:
                                    # 如果不是字典，保持原样
                                    cleaned_data['items']["weapons"][name] = weapon_data
                            except Exception as e:
                                # 创建默认武器数据
                                cleaned_data['items']["weapons"][name] = WeaponData(
                                    name=name,
                                    type='武器',
                                    attack=0,
                                    rarity='普通',
                                    description='',
                                    price=0,
                                    required_realm='练气期',
                                    enhancement_level=0
                                )

        # 移除不需要的字段
        if 'weapons' in data:
            data.pop('weapons', None)

        return cls(**cleaned_data)