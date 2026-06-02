from __future__ import annotations

from typing import Dict, List, Optional

from shared.exceptions import ValidationError
from .models import CodeReview, ESTADOS_VALIDOS
from .repository import CodeReviewRepository, InMemoryCodeReviewRepository


class RevisionCodigo:
    """Lógica de negocio de la HU: Revisión de Código en Pareja."""

    def __init__(self, repository: Optional[CodeReviewRepository] = None) -> None:
        self.repository = repository or InMemoryCodeReviewRepository()
        self.current_review_id: Optional[str] = None

        # Atributos de conveniencia para tests/uso simple.
        self.programador: str = ""
        self.revisor: str = ""
        self.tarea: str = ""
        self.observaciones: str = ""
        self.estado: str = ""
        self.fecha_revision: str = ""

    def guardar(
        self,
        programador: str,
        revisor: str,
        tarea: str,
        observaciones: str,
        estado: str,
    ) -> Dict[str, object]:
        self._validar_revision(programador, revisor, tarea, observaciones, estado)

        review = CodeReview(
            programmer_name=programador.strip(),
            reviewer_name=revisor.strip(),
            reviewed_task=tarea.strip(),
            observations=observaciones.strip(),
            status=estado.strip(),
        )
        saved = self.repository.save(review)
        self._sincronizar_estado_local(saved)
        return saved

    def listar_revisiones(self) -> List[Dict[str, object]]:
        return self.repository.list_all()

    def actualizar_estado(self, estado: str, review_id: Optional[str] = None) -> Dict[str, object]:
        review_id = review_id or self._require_current_review_id()
        if estado not in ESTADOS_VALIDOS:
            raise ValidationError("El estado de revisión no es válido")

        updated = self.repository.update(review_id, {"status": estado})
        self._sincronizar_estado_local(updated)
        return updated

    def editar(
        self,
        review_id: Optional[str] = None,
        tarea: Optional[str] = None,
        observaciones: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> Dict[str, object]:
        review_id = review_id or self._require_current_review_id()
        current = self.repository.get(review_id)
        if not current:
            raise ValidationError("La revisión no existe")

        payload: Dict[str, object] = {}
        if tarea is not None:
            if not tarea.strip():
                raise ValidationError("La tarea revisada es obligatoria")
            payload["reviewed_task"] = tarea.strip()
        if observaciones is not None:
            payload["observations"] = observaciones.strip()
        if estado is not None:
            if estado not in ESTADOS_VALIDOS:
                raise ValidationError("El estado de revisión no es válido")
            payload["status"] = estado

        estado_final = str(payload.get("status", current["status"]))
        observaciones_final = str(payload.get("observations", current.get("observations", "")))
        if estado_final == "Con observaciones" and not observaciones_final.strip():
            raise ValidationError("Debe registrar observaciones cuando el estado es 'Con observaciones'")

        updated = self.repository.update(review_id, payload)
        self._sincronizar_estado_local(updated)
        return updated

    def _validar_revision(
        self,
        programador: str,
        revisor: str,
        tarea: str,
        observaciones: str,
        estado: str,
    ) -> None:
        if not programador.strip() or not revisor.strip() or not tarea.strip() or not estado.strip():
            raise ValidationError("Debe completar todos los datos requeridos")
        if estado not in ESTADOS_VALIDOS:
            raise ValidationError("El estado de revisión no es válido")
        if estado == "Con observaciones" and not observaciones.strip():
            raise ValidationError("Debe registrar observaciones cuando el estado es 'Con observaciones'")
        if programador.strip() == revisor.strip():
            raise ValidationError("El programador y el revisor deben ser personas diferentes")

    def _sincronizar_estado_local(self, review: Dict[str, object]) -> None:
        self.current_review_id = str(review["id"])
        self.programador = str(review["programmer_name"])
        self.revisor = str(review["reviewer_name"])
        self.tarea = str(review["reviewed_task"])
        self.observaciones = str(review.get("observations", ""))
        self.estado = str(review["status"])
        self.fecha_revision = str(review["review_date"])

    def _require_current_review_id(self) -> str:
        if not self.current_review_id:
            raise ValidationError("Primero debe registrar una revisión")
        return self.current_review_id
