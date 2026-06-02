from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from .models import RotationRecord, RotationSession, utc_now_iso


class RotationRepository(Protocol):
    def save_session(self, session: RotationSession) -> Dict[str, object]: ...
    def update_session(self, session_id: str, data: Dict[str, object]) -> Dict[str, object]: ...
    def get_session(self, session_id: str) -> Optional[Dict[str, object]]: ...
    def list_sessions(self) -> List[Dict[str, object]]: ...
    def save_rotation(self, record: RotationRecord) -> Dict[str, object]: ...
    def list_rotations(self, session_id: str) -> List[Dict[str, object]]: ...
    def list_all_rotations(self) -> List[Dict[str, object]]: ...


class InMemoryRotationRepository:
    """Repositorio local para tests y modo demo sin Supabase."""

    def __init__(self) -> None:
        self.sessions: Dict[str, Dict[str, object]] = {}
        self.rotations: List[Dict[str, object]] = []

    def save_session(self, session: RotationSession) -> Dict[str, object]:
        data = session.to_dict()
        self.sessions[session.id] = data
        return data

    def update_session(self, session_id: str, data: Dict[str, object]) -> Dict[str, object]:
        if session_id not in self.sessions:
            raise KeyError("La sesión de rotación no existe")
        self.sessions[session_id].update(data)
        self.sessions[session_id]["updated_at"] = utc_now_iso()
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Dict[str, object]]:
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, object]]:
        return sorted(self.sessions.values(), key=lambda item: str(item["created_at"]), reverse=True)

    def save_rotation(self, record: RotationRecord) -> Dict[str, object]:
        data = record.to_dict()
        self.rotations.append(data)
        return data

    def list_rotations(self, session_id: str) -> List[Dict[str, object]]:
        return [r for r in self.rotations if r["session_id"] == session_id]

    def list_all_rotations(self) -> List[Dict[str, object]]:
        return sorted(self.rotations, key=lambda item: str(item["rotated_at"]), reverse=True)


class SupabaseRotationRepository:
    """Repositorio real para Supabase."""

    def __init__(self, client) -> None:
        self.client = client

    def save_session(self, session: RotationSession) -> Dict[str, object]:
        response = self.client.table("xp_role_rotation_sessions").insert(session.to_dict()).execute()
        return response.data[0] if response.data else session.to_dict()

    def update_session(self, session_id: str, data: Dict[str, object]) -> Dict[str, object]:
        payload = dict(data)
        payload["updated_at"] = utc_now_iso()
        response = (
            self.client.table("xp_role_rotation_sessions")
            .update(payload)
            .eq("id", session_id)
            .select("*")
            .execute()
        )
        return response.data[0] if response.data else payload

    def get_session(self, session_id: str) -> Optional[Dict[str, object]]:
        response = (
            self.client.table("xp_role_rotation_sessions")
            .select("*")
            .eq("id", session_id)
            .limit(1)
            .execute()
        )
        return response.data[0] if response.data else None

    def list_sessions(self) -> List[Dict[str, object]]:
        response = (
            self.client.table("xp_role_rotation_sessions")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []

    def save_rotation(self, record: RotationRecord) -> Dict[str, object]:
        response = self.client.table("xp_role_rotation_history").insert(record.to_dict()).execute()
        return response.data[0] if response.data else record.to_dict()

    def list_rotations(self, session_id: str) -> List[Dict[str, object]]:
        response = (
            self.client.table("xp_role_rotation_history")
            .select("*")
            .eq("session_id", session_id)
            .order("rotated_at", desc=False)
            .execute()
        )
        return response.data or []

    def list_all_rotations(self) -> List[Dict[str, object]]:
        response = (
            self.client.table("xp_role_rotation_history")
            .select("*")
            .order("rotated_at", desc=True)
            .execute()
        )
        return response.data or []
