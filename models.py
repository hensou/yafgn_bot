from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Game:
    title: str
    url: str
    platform: str
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

    def to_message(self) -> str:
        message = f"🎮 *{self.title}*\n"
        message += f"🎯 Platform: {self.platform}\n"
        if self.description:
            message += f"📝 {self.description}\n"
        if self.end_date:
            message += f"⏰ Available until: {self.end_date.strftime('%Y-%m-%d %H:%M UTC')}\n"
        message += f"🔗 [Get it here]({self.url})"
        return message
