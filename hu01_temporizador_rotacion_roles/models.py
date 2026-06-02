from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RotationSession:
    developer_a: str
    developer_b: str
    interval_minutes: int
    current_piloto: str
    current_copiloto: str
    status: str = "configurada"
    remaining_seconds: int = 0
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "developer_a": self.developer_a,
            "developer_b": self.developer_b,
            "interval_minutes": self.interval_minutes,
            "current_piloto": self.current_piloto,
            "current_copiloto": self.current_copiloto,
            "status": self.status,
            "remaining_seconds": self.remaining_seconds,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class RotationRecord:
    session_id: str
    piloto: str
    copiloto: str
    confirmed_by: List[str]
    rotated_at: str = field(default_factory=utc_now_iso)
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "piloto": self.piloto,
            "copiloto": self.copiloto,
            "confirmed_by": list(self.confirmed_by),
            "rotated_at": self.rotated_at,
        }
