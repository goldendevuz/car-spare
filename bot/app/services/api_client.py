import requests
from typing import Any, Dict, List


class ApiClient:
    def __init__(self, shop_create_url: str, part_create_url: str, api_base: str):
        self.shop_create_url = shop_create_url
        self.part_create_url = part_create_url
        self.api_base = api_base.rstrip("/")

    # ----------- shops -----------
    def create_shop(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = requests.post(self.shop_create_url, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()

    def get_shop(self, shop_id: int) -> Dict[str, Any]:
        url = f"{self.api_base}/shops/{shop_id}/"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    def shop_exists(self, shop_id: int) -> bool:
        url = f"{self.api_base}/shops/{shop_id}/"
        r = requests.get(url, timeout=10)
        return r.status_code == 200

    # ----------- cities -----------
    def list_cities(self) -> List[Dict[str, Any]]:
        url = f"{self.api_base}/cities/"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()

    # ----------- parts -----------
    def create_part(self, payload: Dict[str, Any], seller_token: str) -> Dict[str, Any]:
        headers = {"X-SELLER-TOKEN": seller_token}
        r = requests.post(self.part_create_url, json=payload, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def list_parts_seller(self, shop_id: int, seller_token: str) -> List[Dict[str, Any]]:
        url = f"{self.api_base}/shops/{shop_id}/parts/seller/"
        headers = {"X-SELLER-TOKEN": seller_token}
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def get_part(self, part_id: int) -> Dict[str, Any]:
        url = f"{self.api_base}/parts/{part_id}/"
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()

    def patch_part(self, part_id: int, data: Dict[str, Any], seller_token: str) -> Dict[str, Any]:
        url = f"{self.api_base}/parts/{part_id}/"
        headers = {"X-SELLER-TOKEN": seller_token}
        r = requests.patch(url, json=data, headers=headers, timeout=20)
        r.raise_for_status()
        return r.json()

    def delete_part(self, part_id: int, seller_token: str) -> None:
        url = f"{self.api_base}/parts/{part_id}/"
        headers = {"X-SELLER-TOKEN": seller_token}
        r = requests.delete(url, headers=headers, timeout=20)
        r.raise_for_status()

    # ----------- search -----------
    def search(self, city_id: int, query: str, telegram_id: int, page: int = 1, page_size: int = 3) -> Dict[str, Any]:
        url = f"{self.api_base}/search/"
        params = {
            "city_id": city_id,
            "q": query,
            "telegram_id": telegram_id,
            "page": page,
            "page_size": page_size,
        }
        r = requests.get(url, params=params, timeout=25)
        r.raise_for_status()
        return r.json()

    # ----------- feedback -----------
    def create_feedback(self, telegram_id: int, role: str, message: str, city_id: int | None = None) -> Dict[str, Any]:
        url = f"{self.api_base}/feedback/"
        payload = {
            "telegram_id": telegram_id,
            "role": role,
            "message": message,
        }
        if city_id:
            payload["city"] = city_id

        r = requests.post(url, json=payload, timeout=20)
        r.raise_for_status()
        return r.json()