from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone

@dataclass
class WeaponData:
    name: str
    type: str = "武器"
    attack: int = 0
    rarity: str = "普通"
    description: str = ""
    price: int = 0  
    required_realm: str = "练气期"  
    enhancement_level: int = 0
    acquired_at: Optional[datetime] = None  

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeaponData':
        """从字典创建实例"""
        # 创建一个新的数据字典，包含所有可能的字段
        weapon_data = {
            'name': data.get('name', '未知武器'),
            'type': data.get('type', '武器'),
            'attack': data.get('attack', 0),
            'rarity': data.get('rarity', '普通'),
            'description': data.get('description', ''),
            'price': data.get('price', 0),
            'required_realm': data.get('required_realm', '练气期'),
            'enhancement_level': data.get('enhancement_level', 0)
        }

        # 处理获得时间
        acquired_at = data.get('acquired_at')
        if acquired_at:
            if isinstance(acquired_at, str):
                try:
                    acquired_at = datetime.fromisoformat(acquired_at.replace('Z', '+00:00'))
                except ValueError:
                    acquired_at = None
            weapon_data['acquired_at'] = acquired_at

        return cls(**weapon_data)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = {
            'name': self.name,
            'type': self.type,
            'attack': self.attack,
            'rarity': self.rarity,
            'description': self.description,
            'price': self.price,
            'required_realm': self.required_realm,
            'enhancement_level': self.enhancement_level
        }

        # 处理获得时间
        if self.acquired_at:
            if self.acquired_at.tzinfo is None:
                self.acquired_at = self.acquired_at.replace(tzinfo=timezone.utc)
            data['acquired_at'] = self.acquired_at.isoformat()

        return data