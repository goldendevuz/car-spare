from django.contrib import admin
from .models import City, Shop, Part, SearchLog, SearchResultLog, Feedback


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_display_links = ('name', )
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "phone", "status")
    list_display_links = ("name", )
    search_fields = ("name", "phone", "landmark")
    list_filter = ("status", "city")


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("id", "shop", "car_model", "name", "in_stock", "price", "created_at")
    list_display_links = ("name", )
    search_fields = ("car_model", "name", "shop__name")
    list_filter = ("in_stock", "shop__city")


class SearchResultLogInline(admin.TabularInline):
    model = SearchResultLog
    extra = 0
    readonly_fields = ("rank", "shop", "best_part", "score")


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "city", "query_text", "results_count", "created_at")
    list_display_links = ("telegram_id",)
    search_fields = ("query_text", "telegram_id")
    list_filter = ("city", "created_at")
    inlines = [SearchResultLogInline]


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "role", "city", "status", "message", "created_at")
    list_display_links = ("telegram_id", )
    search_fields = ("telegram_id", "message")
    list_filter = ("role", "status", "city", "created_at")