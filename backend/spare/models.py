import uuid
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Shop(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACTIVE = "active"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACTIVE, "Active"),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)

    # City admin paneldan boshqariladi, seller tanlaydi
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="shops")

    latitude = models.FloatField()
    longitude = models.FloatField()
    landmark = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    seller_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class Part(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="parts")
    car_model = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    price = models.IntegerField(null=True, blank=True)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.car_model} - {self.name}"


class SearchLog(models.Model):
    telegram_id = models.BigIntegerField()
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name="search_logs")

    query_text = models.CharField(max_length=255)
    normalized_query = models.CharField(max_length=255, blank=True)

    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.telegram_id} | {self.city.name} | {self.query_text}"


class SearchResultLog(models.Model):
    search_log = models.ForeignKey(SearchLog, on_delete=models.CASCADE, related_name="results")
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="search_result_logs")
    rank = models.IntegerField()  # 1..N
    best_part = models.ForeignKey(Part, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.FloatField(default=0.0)

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"{self.search_log_id} -> {self.shop.name} #{self.rank}"


class Feedback(models.Model):
    ROLE_USER = "user"
    ROLE_SELLER = "seller"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_SELLER, "Seller"),
    ]

    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_RESOLVED = "resolved"
    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_RESOLVED, "Resolved"),
    ]

    telegram_id = models.BigIntegerField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)

    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedbacks")
    message = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.role} {self.telegram_id}: {self.message[:30]}"