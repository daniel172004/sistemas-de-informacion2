from __future__ import annotations

from collections import Counter
from typing import Dict, List

import streamlit as st

from .models import ESTADOS_VALIDOS
from .repository import InMemoryCodeReviewRepository, SupabaseCodeReviewRepository
from .service import RevisionCodigo
from shared.supabase_client import get_supabase_client, should_use_supabase


def _get_service() -> RevisionCodigo:
    if "hu02_repo" not in st.session_state:
        if should_use_supabase():
            st.session_state.hu02_repo = SupabaseCodeReviewRepository(get_supabase_client())
        else:
            st.session_state.hu02_repo = InMemoryCodeReviewRepository()

    if "hu02_service" not in st.session_state:
        st.session_state.hu02_service = RevisionCodigo(repository=st.session_state.hu02_repo)

    return st.session_state.hu02_service


def _status_class(status: str) -> str:
    if status == "Aprobado":
        return "xp-pill-success"
    if status == "Con observaciones":
        return "xp-pill-warning"
    if status == "Corregido":
        return "xp-pill-purple"
    return "xp-pill"


def _status_icon(status: str) -> str:
    if status == "Aprobado":
        return "✅"
    if status == "Con observaciones":
        return "⚠️"
    if status == "Corregido":
        return "🔧"
    return "📋"


def _tabla_revisiones(revisiones: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return [
        {
            "Tarea revisada": r.get("reviewed_task", ""),
            "Programador": r.get("programmer_name", ""),
            "Revisor": r.get("reviewer_name", ""),
            "Estado": r.get("status", ""),
            "Observaciones": r.get("observations", ""),
            "Fecha": r.get("review_date", ""),
            "ID": str(r.get("id", ""))[:8],
        }
        for r in revisiones
    ]


def _render_resumen(revisiones: List[Dict[str, object]]) -> None:
    conteo = Counter(str(r.get("status", "")) for r in revisiones)
    total = len(revisiones)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total revisiones", total)
    c2.metric("✅ Aprobadas", conteo.get("Aprobado", 0))
    c3.metric("⚠️ Con observaciones", conteo.get("Con observaciones", 0))
    c4.metric("🔧 Corregidas", conteo.get("Corregido", 0))


def _render_cards(revisiones: List[Dict[str, object]]) -> None:
    if not revisiones:
        st.info("Aún no existen revisiones registradas.")
        return

    for r in revisiones[:6]:
        status = str(r.get("status", ""))
        obs = r.get("observations", "") or "Sin observaciones"
        st.markdown(
            f"""
            <div class="xp-review-card">
                <h4>{_status_icon(status)} {r.get('reviewed_task', '')}</h4>
                <div style="margin: 0.5rem 0 0.75rem;">
                    <span class="xp-pill {_status_class(status)}">{status}</span>
                    <span class="xp-pill">👨‍💻 {r.get('programmer_name', '')}</span>
                    <span class="xp-pill xp-pill-purple">🔎 {r.get('reviewer_name', '')}</span>
                </div>
                <p class="xp-muted" style="margin: 0 0 0.3rem;"><b style="color:#94a3b8;">Observaciones:</b> {obs}</p>
                <p class="xp-muted" style="margin:0;"><b style="color:#94a3b8;">Fecha:</b> {r.get('review_date', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render() -> None:
    st.markdown("## 🧩 HU2 · Revisión de Código en Pareja")
    st.caption("Registra revisiones realizadas por dos integrantes, controla estados y documenta observaciones.")

    service = _get_service()
    revisiones = service.listar_revisiones()

    _render_resumen(revisiones)

    tab_registro, tab_lista, tab_edicion = st.tabs(["📝 Registrar revisión", "📋 Revisiones", "✏️ Editar / actualizar"])

    with tab_registro:
        left, right = st.columns([1.05, 0.95])
        with left:
            st.markdown(
                """
                <div class="xp-card">
                    <h3>📝 Nueva revisión</h3>
                    <div class="xp-muted">
                        Completa los datos obligatorios para guardar la revisión. Si el estado es "Con observaciones", describe qué debe corregirse.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("form_revision_codigo"):
                col1, col2 = st.columns(2)
                with col1:
                    programador = st.text_input("Programador que realizó el código", placeholder="Ejemplo: Ana")
                with col2:
                    revisor = st.text_input("Compañero que revisó", placeholder="Ejemplo: Luis")

                tarea = st.text_input("Tarea revisada", placeholder="Ejemplo: Login, Registro, Temporizador XP")
                estado = st.selectbox("Estado de revisión", list(ESTADOS_VALIDOS))
                observaciones = st.text_area(
                    "Observaciones",
                    placeholder="Describe errores, mejoras o indica 'Todo correcto'.",
                    height=140,
                )
                guardar = st.form_submit_button("💾 Guardar revisión", use_container_width=True)

            if guardar:
                try:
                    service.guardar(programador, revisor, tarea, observaciones, estado)
                    st.success("Revisión registrada correctamente.")
                    st.rerun()
                except Exception as exc:  # pragma: no cover - capa UI
                    st.error(str(exc))

        with right:
            st.markdown(
                """
                <div class="xp-card">
                    <h3>💡 Estados permitidos</h3>
                    <div style="margin-top:0.75rem;">
                        <p style="margin:0 0 0.6rem;">
                            <span class="xp-pill xp-pill-success">✅ Aprobado</span>
                            <span class="xp-muted"> Código sin errores importantes.</span>
                        </p>
                        <p style="margin:0 0 0.6rem;">
                            <span class="xp-pill xp-pill-warning">⚠️ Con observaciones</span>
                            <span class="xp-muted"> Requiere correcciones o mejoras.</span>
                        </p>
                        <p style="margin:0;">
                            <span class="xp-pill xp-pill-purple">🔧 Corregido</span>
                            <span class="xp-muted"> Las observaciones fueron solucionadas.</span>
                        </p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("#### Últimas revisiones")
            _render_cards(revisiones[:3])

    with tab_lista:
        st.markdown(
            """
            <div class="xp-card">
                <h3>📋 Lista de revisiones</h3>
                <div class="xp-muted">Aquí se visualiza tarea, programador, revisor, fecha, estado y observaciones.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        filtro = st.selectbox("Filtrar por estado", ["Todos", *list(ESTADOS_VALIDOS)])
        filtradas = revisiones if filtro == "Todos" else [r for r in revisiones if r.get("status") == filtro]
        if filtradas:
            st.dataframe(_tabla_revisiones(filtradas), use_container_width=True, hide_index=True)
            st.markdown("#### Vista tipo tarjetas")
            _render_cards(filtradas)
        else:
            st.info("No hay revisiones para el filtro seleccionado.")

    with tab_edicion:
        st.markdown(
            """
            <div class="xp-card">
                <h3>✏️ Editar revisión</h3>
                <div class="xp-muted">Permite modificar tarea, observaciones o estado cuando se registraron datos incorrectos o ya fueron corregidos.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not revisiones:
            st.info("Primero registra una revisión para poder editarla.")
            return

        opciones = {
            f"{r['reviewed_task']} · {r['programmer_name']} → {r['reviewer_name']} · {r['status']}": str(r["id"])
            for r in revisiones
        }
        seleccion = st.selectbox("Selecciona una revisión", list(opciones.keys()))
        review_id = opciones[seleccion]
        actual = next((r for r in revisiones if str(r["id"]) == review_id), None)

        col_estado, col_tarea = st.columns([0.85, 1.15])
        with col_estado:
            estado_actual = str(actual.get("status", "Aprobado")) if actual else "Aprobado"
            nuevo_estado = st.selectbox(
                "Nuevo estado",
                list(ESTADOS_VALIDOS),
                index=list(ESTADOS_VALIDOS).index(estado_actual) if estado_actual in ESTADOS_VALIDOS else 0,
                key="edit_estado",
            )
        with col_tarea:
            nueva_tarea = st.text_input(
                "Tarea revisada",
                value=str(actual.get("reviewed_task", "")) if actual else "",
                key="edit_tarea",
            )
        nuevas_obs = st.text_area(
            "Observaciones",
            value=str(actual.get("observations", "")) if actual else "",
            key="edit_obs",
            height=140,
        )

        if st.button("💾 Actualizar revisión", use_container_width=True):
            try:
                service.editar(
                    review_id=review_id,
                    tarea=nueva_tarea,
                    observaciones=nuevas_obs,
                    estado=nuevo_estado,
                )
                st.success("Revisión actualizada correctamente.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
