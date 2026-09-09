import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str) -> list[int]:
    raw = (raw or "").strip().strip("[]")
    if not raw:
        return []
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


@dataclass
class Settings:
    bot_token: str
    api_base: str
    shop_create_path: str
    part_create_path: str
    admin_ids: list[int] = field(default_factory=list)

    @property
    def shop_create_url(self) -> str:
        return self.api_base.rstrip("/") + self.shop_create_path

    @property
    def part_create_url(self) -> str:
        return self.api_base.rstrip("/") + self.part_create_path

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_ids


settings = Settings(
    bot_token=os.getenv("BOT_TOKEN", ""),
    api_base=os.getenv("API_BASE", "http://127.0.0.1:8000"),
    shop_create_path=os.getenv("SHOP_CREATE_PATH", "/shops/create/"),
    part_create_path=os.getenv("PART_CREATE_PATH", "/parts/create/"),
    admin_ids=_parse_admin_ids(os.getenv("TG_ADMIN_IDS", "")),
)