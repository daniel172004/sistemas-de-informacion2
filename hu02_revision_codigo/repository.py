from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from .models import CodeReview, utc_now_iso


class CodeReviewRepository(Protocol):
    def save(self, review: CodeReview) -> Dict[str, object]: ...
    def list_all(self) -> List[Dict[str, object]]: ...
    def update(self, review_id: str, data: Dict[str, object]) -> Dict[str, object]: ...
    def get(self, review_id: str) -> Optional[Dict[str, object]]: ...


class InMemoryCodeReviewRepository:
    """Repositorio local para tests y modo demo sin Supabase."""

    def __init__(self) -> None:
        self.reviews: Dict[str, Dict[str, object]] = {}

    def save(self, review: CodeReview) -> Dict[str, object]:
        data = review.to_dict()
        self.reviews[review.id] = data
        return data

    def list_all(self) -> List[Dict[str, object]]:
        return sorted(self.reviews.values(), key=lambda item: str(item["review_date"]), reverse=True)

    def update(self, review_id: str, data: Dict[str, object]) -> Dict[str, object]:
        if review_id not in self.reviews:
            raise KeyError("La revisión no existe")
        self.reviews[review_id].update(data)
        self.reviews[review_id]["updated_at"] = utc_now_iso()
        return self.reviews[review_id]

    def get(self, review_id: str) -> Optional[Dict[str, object]]:
        return self.reviews.get(review_id)


class SupabaseCodeReviewRepository:
    """Repositorio real para Supabase."""

    def __init__(self, client) -> None:
        self.client = client

    def save(self, review: CodeReview) -> Dict[str, object]:
        response = self.client.table("xp_code_reviews").insert(review.to_dict()).execute()
        return response.data[0] if response.data else review.to_dict()

    def list_all(self) -> List[Dict[str, object]]:
        response = (
            self.client.table("xp_code_reviews")
            .select("*")
            .order("review_date", desc=True)
            .execute()
        )
        return response.data or []

    def update(self, review_id: str, data: Dict[str, object]) -> Dict[str, object]:
        payload = dict(data)
        payload["updated_at"] = utc_now_iso()
        response = (
            self.client.table("xp_code_reviews")
            .update(payload)
            .eq("id", review_id)
            .select("*")
            .execute()
        )
        return response.data[0] if response.data else payload

    def get(self, review_id: str) -> Optional[Dict[str, object]]:
        response = (
            self.client.table("xp_code_reviews")
            .select("*")
            .eq("id", review_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None
