from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


ESTADOS_VALIDOS = ("Aprobado", "Con observaciones", "Corregido")


@dataclass
class CodeReview:
    programmer_name: str
    reviewer_name: str
    reviewed_task: str
    observations: str
    status: str
    review_date: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "programmer_name": self.programmer_name,
            "reviewer_name": self.reviewer_name,
            "reviewed_task": self.reviewed_task,
            "observations": self.observations,
            "status": self.status,
            "review_date": self.review_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
