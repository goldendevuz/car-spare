from django.urls import path
from .views import (
    CityListAPIView,
    ShopCreateAPIView,
    ShopDetailAPIView,
    PartCreateAPIView,
    PartDetailAPIView,
    SellerPartsByShopAPIView,
    SearchAPIView,
    FeedbackCreateAPIView,
)

urlpatterns = [
    # Cities
    path("cities/", CityListAPIView.as_view()),

    # Shops
    path("shops/create/", ShopCreateAPIView.as_view()),
    path("shops/<int:shop_id>/", ShopDetailAPIView.as_view()),
    path("shops/<int:shop_id>/parts/seller/", SellerPartsByShopAPIView.as_view()),

    # Parts
    path("parts/create/", PartCreateAPIView.as_view()),
    path("parts/<int:part_id>/", PartDetailAPIView.as_view()),

    # Search (public)
    path("search/", SearchAPIView.as_view()),

    # Feedback
    path("feedback/", FeedbackCreateAPIView.as_view()),
]