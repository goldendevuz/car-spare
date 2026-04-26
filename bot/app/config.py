import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    bot_token: str
    api_base: str
    shop_create_path: str
    part_create_path: str

    @property
    def shop_create_url(self) -> str:
        return self.api_base.rstrip("/") + self.shop_create_path

    @property
    def part_create_url(self) -> str:
        return self.api_base.rstrip("/") + self.part_create_path


settings = Settings(
    bot_token=os.getenv("BOT_TOKEN", ""),
    api_base=os.getenv("API_BASE", "http://127.0.0.1:8001"),
    shop_create_path=os.getenv("SHOP_CREATE_PATH", "/shops/create/"),
    part_create_path=os.getenv("PART_CREATE_PATH", "/parts/create/"),
)