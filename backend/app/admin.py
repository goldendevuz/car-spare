from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from .config import settings
from .models import City, Shop, Part, SearchLog, SearchResultLog, Feedback


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        if username == settings.admin_username and password == settings.admin_password:
            request.session.update({"admin_authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_authenticated"))


class CityAdmin(ModelView, model=City):
    column_list = [City.id, City.name, City.is_active]
    name_plural = "Cities"


class ShopAdmin(ModelView, model=Shop):
    column_list = [Shop.id, Shop.name, Shop.phone, Shop.city, Shop.status, Shop.seller_token]
    column_searchable_list = [Shop.name, Shop.phone]
    name_plural = "Shops"


class PartAdmin(ModelView, model=Part):
    column_list = [Part.id, Part.shop, Part.car_model, Part.name, Part.price, Part.in_stock, Part.created_at]
    column_searchable_list = [Part.car_model, Part.name]
    name_plural = "Parts"


class SearchLogAdmin(ModelView, model=SearchLog):
    column_list = [SearchLog.id, SearchLog.telegram_id, SearchLog.city, SearchLog.query_text, SearchLog.results_count, SearchLog.created_at]
    name_plural = "Search logs"
    can_create = False
    can_edit = False


class SearchResultLogAdmin(ModelView, model=SearchResultLog):
    column_list = [SearchResultLog.id, SearchResultLog.search_log_id, SearchResultLog.shop, SearchResultLog.rank, SearchResultLog.score]
    name_plural = "Search result logs"
    can_create = False
    can_edit = False


class FeedbackAdmin(ModelView, model=Feedback):
    column_list = [Feedback.id, Feedback.telegram_id, Feedback.role, Feedback.city, Feedback.message, Feedback.status, Feedback.created_at]
    name_plural = "Feedback"


def setup_admin(app, engine):
    admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key=settings.admin_secret_key))
    admin.add_view(CityAdmin)
    admin.add_view(ShopAdmin)
    admin.add_view(PartAdmin)
    admin.add_view(SearchLogAdmin)
    admin.add_view(SearchResultLogAdmin)
    admin.add_view(FeedbackAdmin)
    return admin
