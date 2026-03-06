import re
import difflib
from django.db.models import F, Value
from django.db.models.functions import Concat, Greatest
from django.contrib.postgres.search import TrigramSimilarity

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotFound

from .models import City, Shop, Part, SearchLog, SearchResultLog, Feedback
from .serializers import (
    CitySerializer,
    ShopCreateSerializer,
    PartSerializer,
    FeedbackCreateSerializer,
)


# ---------------- helpers ----------------
def get_seller_token(request) -> str | None:
    return request.headers.get("X-SELLER-TOKEN")


def normalize_query(q: str) -> str:
    q = q.lower().strip()
    q = re.sub(r"\s+", " ", q)
    return q


def extract_first_token(q: str) -> str:
    # "cobilt fara" -> "cobilt"
    if not q:
        return ""
    return q.split(" ", 1)[0].strip()


def remove_first_token(q: str) -> str:
    # "cobilt fara" -> "fara"
    if not q:
        return ""
    parts = q.split(" ", 1)
    return parts[1].strip() if len(parts) == 2 else ""


COMMON_MODELS = [
    "cobalt", "jentra", "spark", "nexia", "lacetti", "malibu", "gentra",
    "matiz", "damas", "tracker", "captiva", "onix", "epica",
]

def guess_model_token(token: str) -> str | None:
    """
    token: 'cobilt' bo'lsa ham 'cobalt' qaytarishga harakat qiladi.
    """
    token = (token or "").lower().strip()
    if not token:
        return None
    if token in COMMON_MODELS:
        return token

    # typo tolerant (stdlib)
    matches = difflib.get_close_matches(token, COMMON_MODELS, n=1, cutoff=0.75)
    return matches[0] if matches else None



# ---------------- City ----------------
class CityListAPIView(APIView):
    def get(self, request):
        qs = City.objects.filter(is_active=True).order_by("name")
        return Response(CitySerializer(qs, many=True).data, status=status.HTTP_200_OK)


# ---------------- Shop ----------------
class ShopDetailAPIView(APIView):
    def get(self, request, shop_id: int):
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            raise NotFound("Do'kon topilmadi")
        return Response(ShopCreateSerializer(shop).data, status=status.HTTP_200_OK)


class ShopCreateAPIView(APIView):
    def post(self, request):
        serializer = ShopCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop = serializer.save()
        return Response(ShopCreateSerializer(shop).data, status=status.HTTP_201_CREATED)


# ---------------- Part CRUD (seller token bilan) ----------------
class PartCreateAPIView(APIView):
    def post(self, request):
        token = get_seller_token(request)
        if not token:
            raise PermissionDenied("X-SELLER-TOKEN header kerak")

        serializer = PartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shop_id = serializer.validated_data["shop"].id

        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            raise NotFound("Shop topilmadi")

        if str(shop.seller_token) != str(token):
            raise PermissionDenied("Token noto‘g‘ri")

        part = serializer.save()
        return Response(PartSerializer(part).data, status=status.HTTP_201_CREATED)


class PartDetailAPIView(APIView):
    def get(self, request, part_id: int):
        try:
            part = Part.objects.select_related("shop").get(id=part_id)
        except Part.DoesNotExist:
            raise NotFound("Part topilmadi")
        return Response(PartSerializer(part).data, status=status.HTTP_200_OK)

    def patch(self, request, part_id: int):
        token = get_seller_token(request)
        if not token:
            raise PermissionDenied("X-SELLER-TOKEN header kerak")

        try:
            part = Part.objects.select_related("shop").get(id=part_id)
        except Part.DoesNotExist:
            raise NotFound("Part topilmadi")

        if str(part.shop.seller_token) != str(token):
            raise PermissionDenied("Token noto‘g‘ri")

        serializer = PartSerializer(part, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        part = serializer.save()
        return Response(PartSerializer(part).data, status=status.HTTP_200_OK)

    def delete(self, request, part_id: int):
        token = get_seller_token(request)
        if not token:
            raise PermissionDenied("X-SELLER-TOKEN header kerak")

        try:
            part = Part.objects.select_related("shop").get(id=part_id)
        except Part.DoesNotExist:
            raise NotFound("Part topilmadi")

        if str(part.shop.seller_token) != str(token):
            raise PermissionDenied("Token noto‘g‘ri")

        part.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_200_OK)


class SellerPartsByShopAPIView(APIView):
    """
    GET /shops/<shop_id>/parts/seller/
    Header: X-SELLER-TOKEN
    """
    def get(self, request, shop_id: int):
        token = get_seller_token(request)
        if not token:
            raise PermissionDenied("X-SELLER-TOKEN header kerak")

        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            raise NotFound("Shop topilmadi")

        if str(shop.seller_token) != str(token):
            raise PermissionDenied("Token noto‘g‘ri")

        parts = Part.objects.filter(shop_id=shop_id).order_by("-created_at")
        return Response(PartSerializer(parts, many=True).data, status=status.HTTP_200_OK)



# ---------------- Search (public) + logs ----------------
class SearchAPIView(APIView):
    """
    GET /search/?city_id=1&q=...&page=1&page_size=3&telegram_id=123

    Features:
      ✅ Active shop filter (status=active)
      ✅ Fuzzy search (TrigramSimilarity)
      ✅ Synonyms + translit (фара/fara/headlight -> "fara", amort/mortizator -> "amortizator")
      ✅ Model detection anywhere (cobilt -> cobalt) + STRICT:
           - agar user model aytsa va city ichida u model yo'q bo'lsa => 0 natija qaytadi (boshqa modelga ketmaydi)
      ✅ Pagination + grouping (har do‘kondan eng mos 1 ta natija)
      ✅ Logging (SearchLog + SearchResultLog)
    """

    COMMON_MODELS = [
        "cobalt", "jentra", "spark", "nexia", "lacetti", "malibu", "gentra",
        "matiz", "damas", "tracker", "captiva", "onix", "epica",
    ]

    # ---------------- helpers ----------------
    def normalize_query(self, q: str) -> str:
        q = (q or "").lower().strip()
        q = re.sub(r"\s+", " ", q)
        return q

    def translit_ru_to_lat(self, text: str) -> str:
        mapping = {
            "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "j", "з": "z",
            "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
            "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sh",
            "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
            "қ": "q", "ғ": "g", "ў": "o", "ҳ": "h", "і": "i",
        }
        out = []
        for ch in (text or "").lower():
            out.append(mapping.get(ch, ch))
        return "".join(out)

    def canonicalize_synonyms(self, q: str) -> str:
        q = (q or "").lower()

        rules = [
            # FARA
            (r"\b(фара|fara|far|headlight|lamp|lampa)\b", "fara"),
            (r"\b(old\s*fara|old\s*far|old\s*headlight|стар(ый|ая)\s*фара)\b", "old fara"),
            (r"\b(orqa\s*fara|rear\s*light|tail\s*light|задн(яя|ий)\s*фара)\b", "orqa fara"),

            # AMORTIZATOR
            (r"\b(амортизатор|amortizator|amort|mortizator|стойка)\b", "amortizator"),

            # Optional examples:
            (r"\b(шина|tire|tyre)\b", "shina"),
            (r"\b(диск|disk|wheel)\b", "disk"),
        ]

        for pattern, repl in rules:
            q = re.sub(pattern, repl, q)

        q = re.sub(r"\s+", " ", q).strip()
        return q

    def build_query_variants(self, raw_q: str) -> list[str]:
        """
        Qidiruv uchun 2-4 variant:
          - normal
          - synonym canonical
          - translit
          - translit + synonym
        """
        v = []
        a = self.normalize_query(raw_q)
        b = self.canonicalize_synonyms(a)
        c = self.normalize_query(self.translit_ru_to_lat(a))
        d = self.canonicalize_synonyms(c)

        for x in (a, b, c, d):
            if x and x not in v:
                v.append(x)

        return v[:4]

    def guess_model_token(self, token: str) -> str | None:
        token = (token or "").lower().strip()
        if not token:
            return None
        if token in self.COMMON_MODELS:
            return token
        # typo tolerant
        matches = difflib.get_close_matches(token, self.COMMON_MODELS, n=1, cutoff=0.70)
        return matches[0] if matches else None

    def detect_model_anywhere(self, nq: str) -> tuple[str | None, str, float]:
        """
        Query ichidan modelni topadi (har qayerda bo'lishi mumkin).
        Returns:
          detected_model_token, remaining_query_text, confidence(0..1)
        """
        tokens = [t for t in nq.split(" ") if t]
        if not tokens:
            return None, nq, 0.0

        best_model = None
        best_conf = 0.0
        best_idx = None

        for i, tok in enumerate(tokens):
            m = self.guess_model_token(tok)
            if m:
                conf = 1.0 if tok == m else 0.85
                if conf > best_conf:
                    best_model = m
                    best_conf = conf
                    best_idx = i

        if not best_model:
            return None, nq, 0.0

        remaining = " ".join([t for j, t in enumerate(tokens) if j != best_idx]).strip()
        return best_model, remaining, best_conf

    # ---------------- main ----------------
    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        city_id = request.query_params.get("city_id")
        telegram_id = request.query_params.get("telegram_id")

        if not q or not city_id or not telegram_id:
            return Response(
                {"detail": "q, city_id, telegram_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            city = City.objects.get(id=int(city_id), is_active=True)
        except Exception:
            raise NotFound("City topilmadi")

        try:
            telegram_id_int = int(telegram_id)
        except Exception:
            return Response({"detail": "telegram_id must be int"}, status=status.HTTP_400_BAD_REQUEST)

        page = int(request.query_params.get("page") or 1)
        page_size = int(request.query_params.get("page_size") or 3)
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 20:
            page_size = 3

        nq = self.normalize_query(q)

        # Only active shops for public search
        active_shops = Shop.objects.filter(status=Shop.STATUS_ACTIVE, city=city)

        # -------- Model detect (anywhere) + STRICT --------
        forced_model_token, remaining_query, model_conf = self.detect_model_anywhere(nq)

        detected_model = None
        detected_model_sim = 0.0

        if forced_model_token:
            # City + active shops ichida shu model umuman bormi?
            db_model = (
                Part.objects.filter(shop__in=active_shops)
                .filter(car_model__iexact=forced_model_token)
                .values_list("car_model", flat=True)
                .first()
            )
            if db_model:
                detected_model = db_model
                detected_model_sim = model_conf
            else:
                # STRICT: user model aytdi -> boshqa modelga ketmaymiz
                SearchLog.objects.create(
                    telegram_id=telegram_id_int,
                    city=city,
                    query_text=q,
                    normalized_query=nq,
                    results_count=0,
                )
                return Response(
                    {
                        "count": 0,
                        "page": page,
                        "page_size": page_size,
                        "results": [],
                        "model_detected": forced_model_token,
                        "model_detected_sim": round(model_conf, 3),
                        "hint": f"Bu hududda '{forced_model_token.title()}' bo‘yicha zapchast topilmadi.",
                    },
                    status=status.HTTP_200_OK,
                )

        # Qidiruv matni:
        # model topilgan bo'lsa -> remaining_query (masalan "old fara")
        # model yo'q bo'lsa -> nq (masalan "fara")
        search_text = remaining_query if (detected_model and remaining_query) else nq

        # -------- Parts queryset --------
        parts_qs = Part.objects.filter(shop__in=active_shops, in_stock=True)
        if detected_model:
            parts_qs = parts_qs.filter(car_model__iexact=detected_model)

        # -------- Variants (synonym + translit) --------
        variants = self.build_query_variants(search_text)

        parts_qs = parts_qs.annotate(full_text=Concat("car_model", Value(" "), "name"))

        if len(variants) == 1:
            parts_qs = parts_qs.annotate(score=TrigramSimilarity("full_text", variants[0]))
        else:
            parts_qs = parts_qs.annotate(score1=TrigramSimilarity("full_text", variants[0]))
            parts_qs = parts_qs.annotate(score2=TrigramSimilarity("full_text", variants[1]))
            parts_qs = parts_qs.annotate(score3=TrigramSimilarity("full_text", variants[2]) if len(variants) >= 3 else Value(0.0))
            parts_qs = parts_qs.annotate(score4=TrigramSimilarity("full_text", variants[3]) if len(variants) >= 4 else Value(0.0))
            parts_qs = parts_qs.annotate(score=Greatest("score1", "score2", "score3", "score4"))

        parts = (
            parts_qs
            .filter(score__gt=0.10)
            .select_related("shop")
            .order_by("-score")[:1200]
        )

        # -------- Group by shop (best match per shop) --------
        best = {}
        for p in parts:
            sid = p.shop_id
            if sid not in best or p.score > best[sid]["score"]:
                best[sid] = {
                    "shop_id": p.shop_id,
                    "shop_name": p.shop.name,
                    "phone": p.shop.phone,
                    "landmark": p.shop.landmark,
                    "latitude": p.shop.latitude,
                    "longitude": p.shop.longitude,
                    "best_part_id": p.id,
                    "best_part": f"{p.car_model} — {p.name}",
                    "score": float(p.score),
                }

        results_all = sorted(best.values(), key=lambda x: x["score"], reverse=True)
        count = len(results_all)

        # pagination slice
        start = (page - 1) * page_size
        end = start + page_size
        results_page = results_all[start:end]

        # -------- Logs --------
        log = SearchLog.objects.create(
            telegram_id=telegram_id_int,
            city=city,
            query_text=q,
            normalized_query=nq,
            results_count=count,
        )

        for idx, r in enumerate(results_all[:20], start=1):
            best_part = Part.objects.filter(id=r["best_part_id"]).first() if r.get("best_part_id") else None
            SearchResultLog.objects.create(
                search_log=log,
                shop_id=r["shop_id"],
                rank=idx,
                best_part=best_part,
                score=r["score"],
            )

        return Response(
            {
                "count": count,
                "page": page,
                "page_size": page_size,
                "results": results_page,
                "model_detected": detected_model,
                "model_detected_sim": round(detected_model_sim, 3),
            },
            status=status.HTTP_200_OK,
        )

# ---------------- Feedback (public) ----------------
class FeedbackCreateAPIView(APIView):
    """
    POST /feedback/
    {
      "telegram_id": 123,
      "role": "user"|"seller",
      "city": 1 (optional),
      "message": "..."
    }
    """
    def post(self, request):
        serializer = FeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fb = serializer.save()
        return Response(FeedbackCreateSerializer(fb).data, status=status.HTTP_201_CREATED)