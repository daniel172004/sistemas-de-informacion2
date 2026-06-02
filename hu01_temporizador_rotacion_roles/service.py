from __future__ import annotations

from typing import Dict, List, Optional, Set

from shared.exceptions import ValidationError
from .models import RotationRecord, RotationSession
from .repository import InMemoryRotationRepository, RotationRepository


class RotadorRoles:
    """Lógica de negocio de la HU: Temporizador de Rotación de Roles.

    La clase no depende directamente de Streamlit ni de Supabase. Eso permite
    probarla con pytest y reutilizarla desde cualquier interfaz.
    """

    def __init__(
        self,
        repository: Optional[RotationRepository] = None,
        developer_a: str = "dev1",
        developer_b: str = "dev2",
    ) -> None:
        self.repository = repository or InMemoryRotationRepository()
        self.developer_a = developer_a
        self.developer_b = developer_b
        self.intervalo: int = 0
        self.en_ejecucion: bool = False
        self.pausado: bool = False
        self.session_id: Optional[str] = None
        self.roles: Dict[str, str] = {developer_a: "Piloto", developer_b: "Copiloto"}
        self.confirmaciones: Set[str] = set()
        self.remaining_seconds: int = 0

    def configurar_intervalo(self, minutos: int) -> None:
        """Configura el intervalo de rotación en minutos."""
        if minutos <= 0:
            raise ValidationError("El intervalo debe ser mayor a cero minutos")
        self.intervalo = minutos
        self.remaining_seconds = minutos * 60

    def obtener_intervalo_visible(self) -> str:
        """Retorna el intervalo en formato amigable para ambos desarrolladores."""
        return f"Rotación cada {self.intervalo} minutos"

    def iniciar(self, piloto: Optional[str] = None, copiloto: Optional[str] = None) -> Dict[str, object]:
        if self.intervalo <= 0:
            raise ValidationError("Debe configurar el intervalo antes de iniciar")

        piloto = (piloto or self.developer_a).strip()
        copiloto = (copiloto or self.developer_b).strip()

        if not piloto or not copiloto:
            raise ValidationError("Debe registrar ambos integrantes")
        if piloto == copiloto:
            raise ValidationError("Piloto y Copiloto deben ser personas diferentes")

        self.developer_a = piloto
        self.developer_b = copiloto
        self.roles = {piloto: "Piloto", copiloto: "Copiloto"}
        self.en_ejecucion = True
        self.pausado = False
        self.confirmaciones.clear()
        self.remaining_seconds = self.intervalo * 60

        session = RotationSession(
            developer_a=piloto,
            developer_b=copiloto,
            interval_minutes=self.intervalo,
            current_piloto=piloto,
            current_copiloto=copiloto,
            status="en_ejecucion",
            remaining_seconds=self.remaining_seconds,
        )
        saved = self.repository.save_session(session)
        self.session_id = str(saved["id"])
        return saved

    def tiempo_cumplido(self, segundos_transcurridos: int) -> bool:
        return segundos_transcurridos >= self.intervalo * 60

    def intervalo_finalizado(self) -> bool:
        return self.en_ejecucion and self.remaining_seconds == 0

    def obtener_notificacion_rotacion(self, segundos_transcurridos: int) -> Dict[str, object]:
        """Genera el mensaje de rotación cuando el intervalo se cumple."""
        debe_rotar = self.tiempo_cumplido(segundos_transcurridos)
        piloto_actual = self._obtener_por_rol("Piloto")
        copiloto_actual = self._obtener_por_rol("Copiloto")

        return {
            "debe_rotar": debe_rotar,
            "mensaje": (
                f"Es momento de intercambiar roles: {copiloto_actual} será Piloto y "
                f"{piloto_actual} será Copiloto."
                if debe_rotar
                else "Aún no corresponde rotar roles."
            ),
            "nuevo_piloto": copiloto_actual if debe_rotar else piloto_actual,
            "nuevo_copiloto": piloto_actual if debe_rotar else copiloto_actual,
        }

    def confirmar_rotacion(self, desarrollador: str) -> bool:
        """Registra confirmación. Retorna True solo cuando ambos confirmaron."""
        if desarrollador not in self.roles:
            raise ValidationError("El desarrollador no pertenece a esta sesión")

        self.confirmaciones.add(desarrollador)
        if len(self.confirmaciones) < 2:
            return False

        self._intercambiar_roles()
        self.remaining_seconds = self.intervalo * 60
        record = RotationRecord(
            session_id=self._require_session_id(),
            piloto=self._obtener_por_rol("Piloto"),
            copiloto=self._obtener_por_rol("Copiloto"),
            confirmed_by=sorted(self.confirmaciones),
        )
        self.repository.save_rotation(record)
        self.repository.update_session(
            self._require_session_id(),
            {
                "current_piloto": record.piloto,
                "current_copiloto": record.copiloto,
                "status": "en_ejecucion",
                "remaining_seconds": self.remaining_seconds,
            },
        )
        self.confirmaciones.clear()
        return True

    def obtener_confirmaciones_pendientes(self) -> List[str]:
        return [dev for dev in self.roles if dev not in self.confirmaciones]

    def enviar_recordatorio_si_falta(self) -> str:
        faltantes = self.obtener_confirmaciones_pendientes()
        if not faltantes:
            return "No hay confirmaciones pendientes"
        return f"Recordatorio enviado a {', '.join(faltantes)}"

    def obtener_historial(self) -> List[Dict[str, object]]:
        return self.repository.list_rotations(self._require_session_id())

    def obtener_historial_acumulado(self) -> List[Dict[str, object]]:
        return self.repository.list_all_rotations()

    def obtener_sesiones(self) -> List[Dict[str, object]]:
        return self.repository.list_sessions()

    def pausar(self) -> None:
        self.en_ejecucion = False
        self.pausado = True
        if self.session_id:
            self.repository.update_session(self.session_id, {"status": "pausada", "remaining_seconds": self.remaining_seconds})

    def reanudar(self) -> None:
        if not self.pausado:
            raise ValidationError("Solo se puede reanudar una sesión pausada")
        self.en_ejecucion = True
        self.pausado = False
        if self.session_id:
            self.repository.update_session(self.session_id, {"status": "en_ejecucion", "remaining_seconds": self.remaining_seconds})

    def descontar_tiempo(self, segundos: int) -> None:
        if segundos < 0:
            raise ValidationError("Los segundos no pueden ser negativos")
        if self.pausado or not self.en_ejecucion:
            return
        self.remaining_seconds = max(0, self.remaining_seconds - segundos)
        if self.session_id:
            status = "esperando_confirmacion" if self.remaining_seconds == 0 else "en_ejecucion"
            self.repository.update_session(
                self.session_id,
                {"remaining_seconds": self.remaining_seconds, "status": status},
            )

    def finalizar_intervalo(self) -> None:
        """Deja el temporizador en cero para mostrar la etapa de confirmación."""
        self.descontar_tiempo(self.remaining_seconds)

    def _intercambiar_roles(self) -> None:
        for dev, rol in list(self.roles.items()):
            self.roles[dev] = "Copiloto" if rol == "Piloto" else "Piloto"

    def _obtener_por_rol(self, rol: str) -> str:
        for dev, current_role in self.roles.items():
            if current_role == rol:
                return dev
        raise ValidationError(f"No existe un desarrollador con rol {rol}")

    def _require_session_id(self) -> str:
        if not self.session_id:
            # Permite usar la clase en tests simples sin llamar a iniciar.
            session = RotationSession(
                developer_a=self.developer_a,
                developer_b=self.developer_b,
                interval_minutes=max(self.intervalo, 1),
                current_piloto=self._obtener_por_rol("Piloto"),
                current_copiloto=self._obtener_por_rol("Copiloto"),
            )
            saved = self.repository.save_session(session)
            self.session_id = str(saved["id"])
        return self.session_id
