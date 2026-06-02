from __future__ import annotations

import time
from typing import Dict, List

import streamlit as st

from .repository import InMemoryRotationRepository, SupabaseRotationRepository
from .service import RotadorRoles
from shared.supabase_client import get_supabase_client, should_use_supabase


def _get_service() -> RotadorRoles:
    if "hu01_repo" not in st.session_state:
        if should_use_supabase():
            st.session_state.hu01_repo = SupabaseRotationRepository(get_supabase_client())
        else:
            st.session_state.hu01_repo = InMemoryRotationRepository()

    if "hu01_service" not in st.session_state:
        st.session_state.hu01_service = RotadorRoles(repository=st.session_state.hu01_repo)

    return st.session_state.hu01_service


def _crear_nueva_sesion(dev_a: str, dev_b: str, intervalo: int) -> RotadorRoles:
    repo = st.session_state.hu01_repo
    service = RotadorRoles(repository=repo, developer_a=dev_a.strip(), developer_b=dev_b.strip())
    service.configurar_intervalo(int(intervalo))
    service.iniciar(piloto=dev_a, copiloto=dev_b)
    st.session_state.hu01_service = service
    st.session_state.hu01_last_tick = time.time()
    return service


def _format_seconds(seconds: int) -> str:
    seconds = max(0, int(seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def _estado_visual(service: RotadorRoles) -> tuple[str, str]:
    if service.intervalo_finalizado():
        return "Esperando confirmación", "xp-pill-danger"
    if service.pausado:
        return "Pausado", "xp-pill-warning"
    if service.en_ejecucion:
        return "En ejecución", "xp-pill-success"
    return "Configurando", "xp-pill"


def _aplicar_tick_reloj(service: RotadorRoles) -> None:
    now = time.time()
    last_tick = st.session_state.get("hu01_last_tick", now)

    if service.en_ejecucion and not service.pausado and service.remaining_seconds > 0:
        elapsed = int(now - last_tick)
        if elapsed > 0:
            service.descontar_tiempo(elapsed)
            st.session_state.hu01_last_tick = now
    else:
        st.session_state.hu01_last_tick = now


def _preparar_historial(rotaciones: List[Dict[str, object]]) -> List[Dict[str, object]]:
    return [
        {
            "Fecha / hora": item.get("rotated_at", ""),
            "Nuevo Piloto": item.get("piloto", ""),
            "Nuevo Copiloto": item.get("copiloto", ""),
            "Confirmado por": ", ".join(item.get("confirmed_by", [])),
            "Sesión": str(item.get("session_id", ""))[:8],
        }
        for item in rotaciones
    ]


def _render_form_inicio(titulo: str, submit_label: str, expander: bool = False) -> None:
    contenedor = st.expander(titulo, expanded=not expander) if expander else st.container()
    with contenedor:
        st.markdown(
            """
            <div class="xp-card">
                <h3>🧑‍💻 Crear sesión de Pair Programming</h3>
                <div class="xp-muted">
                    Inicia una nueva sesión de rotación. El historial acumulado se conserva intacto entre sesiones.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form(f"form_inicio_rotacion_{submit_label}"):
            col1, col2, col3 = st.columns([1.2, 1.2, 1])
            with col1:
                dev_a = st.text_input("Primer integrante", value="Ana", key=f"dev_a_{submit_label}")
            with col2:
                dev_b = st.text_input("Segundo integrante", value="Luis", key=f"dev_b_{submit_label}")
            with col3:
                intervalo = st.selectbox(
                    "Intervalo de rotación",
                    [15, 20, 30, 45, 60],
                    index=0,
                    format_func=lambda x: f"{x} min",
                    key=f"intervalo_{submit_label}",
                )
            iniciar = st.form_submit_button(submit_label, use_container_width=True)

        if iniciar:
            try:
                _crear_nueva_sesion(dev_a, dev_b, int(intervalo))
                st.success("Sesión iniciada correctamente. El historial anterior se mantiene guardado.")
                st.rerun()
            except Exception as exc:  # pragma: no cover - capa UI
                st.error(str(exc))


def _render_sesion_activa(service: RotadorRoles) -> None:
    _aplicar_tick_reloj(service)
    estado, clase_estado = _estado_visual(service)
    piloto_actual = service._obtener_por_rol("Piloto")
    copiloto_actual = service._obtener_por_rol("Copiloto")
    total = max(service.intervalo * 60, 1)
    progreso = min(max(1 - (service.remaining_seconds / total), 0), 1)

    st.markdown(
        f"""
        <div class="xp-card">
            <h3>⏱️ Sesión activa</h3>
            <span class="xp-pill {clase_estado}">{estado}</span>
            <span class="xp-pill xp-pill-purple">{service.obtener_intervalo_visible()}</span>
            <span class="xp-pill">ID {str(service.session_id)[:8]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 1])

    with left:
        st.markdown(
            f"""
            <div class="xp-timer">
                <div class="xp-timer-number">{_format_seconds(service.remaining_seconds)}</div>
                <div class="xp-timer-label">Tiempo restante · próxima rotación</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(progreso, text=f"Progreso del intervalo: {int(progreso * 100)}%")

        if service.intervalo_finalizado():
            aviso = service.obtener_notificacion_rotacion(service.intervalo * 60)
            st.markdown(
                f"""
                <div class="xp-alert-finished">
                    🔔 Tiempo finalizado &mdash; {aviso['mensaje']}<br>
                    <span style="font-weight:400; font-size:0.85rem; opacity:0.8;">
                    El temporizador queda detenido hasta que ambos integrantes confirmen la rotación.
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("Usa el reloj automático o los botones de simulación para pruebas rápidas en clase.")

        auto = st.toggle("Actualizar contador automáticamente", value=False, help="Hace avanzar el contador cada segundo mientras la sesión esté activa.")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🔄 Actualizar", use_container_width=True):
            st.rerun()
        if c2.button("+1 min", use_container_width=True, disabled=service.intervalo_finalizado() or service.pausado):
            service.descontar_tiempo(60)
            st.rerun()
        if c3.button("+5 min", use_container_width=True, disabled=service.intervalo_finalizado() or service.pausado):
            service.descontar_tiempo(300)
            st.rerun()
        if c4.button("⏭ Finalizar", use_container_width=True, disabled=service.intervalo_finalizado() or service.pausado):
            service.finalizar_intervalo()
            st.rerun()

        pa, re, _ = st.columns(3)
        if pa.button("⏸ Pausar", use_container_width=True, disabled=service.pausado or service.intervalo_finalizado()):
            service.pausar()
            st.rerun()
        if re.button("▶ Reanudar", use_container_width=True, disabled=not service.pausado):
            try:
                service.reanudar()
                st.rerun()
            except Exception as exc:
                st.warning(str(exc))

    with right:
        st.markdown(
            f"""
            <div class="xp-card">
                <h3>👥 Roles actuales</h3>
                <div style="margin: 1rem 0;">
                    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;">
                        <span class="xp-pill xp-pill-success">✈ Piloto</span>
                        <b style="font-size:1.05rem; color:#f8fafc;">{piloto_actual}</b>
                    </div>
                    <div style="display:flex; align-items:center; gap:0.75rem;">
                        <span class="xp-pill xp-pill-purple">🔭 Copiloto</span>
                        <b style="font-size:1.05rem; color:#f8fafc;">{copiloto_actual}</b>
                    </div>
                </div>
                <div class="xp-muted">
                    Cuando el contador llegue a cero, ambos integrantes deben confirmar la rotación para reiniciar el temporizador.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if service.intervalo_finalizado():
            pendientes = service.obtener_confirmaciones_pendientes()
            st.markdown("#### 🤝 Confirmación de rotación")
            st.caption("El historial se registra solamente cuando ambos confirman.")

            cols = st.columns(len(service.roles))
            for index, dev in enumerate(service.roles.keys()):
                ya_confirmo = dev in service.confirmaciones
                label = f"✅ {dev} confirmó" if ya_confirmo else f"Confirmar {dev}"
                if cols[index].button(label, disabled=ya_confirmo, use_container_width=True):
                    completo = service.confirmar_rotacion(dev)
                    if completo:
                        st.success("Ambos confirmaron. Roles intercambiados y temporizador reiniciado.")
                    else:
                        st.info(service.enviar_recordatorio_si_falta())
                    st.rerun()

            if pendientes:
                st.warning(f"Falta confirmar: {', '.join(pendientes)}")
            else:
                st.success("Todas las confirmaciones fueron registradas.")

            if st.button("✔ Confirmar ambos ahora", use_container_width=True):
                for dev in list(service.roles.keys()):
                    if dev in service.roles:
                        completo = service.confirmar_rotacion(dev)
                        if completo:
                            break
                st.success("Rotación registrada correctamente.")
                st.rerun()

            if st.button("📣 Enviar recordatorio", use_container_width=True):
                st.info(service.enviar_recordatorio_si_falta())

    if auto and service.en_ejecucion and not service.pausado and service.remaining_seconds > 0:
        time.sleep(1)
        st.rerun()


def render() -> None:
    st.markdown("## ⏱️ HU1 · Temporizador de Rotación de Roles")
    st.caption("Rotación justa entre Piloto y Copiloto con confirmaciones, pausa/reanudación e historial persistente.")

    service = _get_service()

    if not service.session_id:
        _render_form_inicio("Crear sesión", "Iniciar sesión")
    else:
        _render_sesion_activa(service)
        _render_form_inicio("➕ Crear nueva sesión sin borrar historial", "Iniciar nueva sesión", expander=True)

    st.markdown("### 📚 Historial de rotaciones")
    tab_actual, tab_acumulado, tab_sesiones = st.tabs(["Esta sesión", "Historial acumulado", "Sesiones"])

    with tab_actual:
        historial_actual = service.obtener_historial() if service.session_id else []
        if historial_actual:
            st.dataframe(_preparar_historial(historial_actual), use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay rotaciones registradas en esta sesión.")

    with tab_acumulado:
        historial_total = service.obtener_historial_acumulado()
        if historial_total:
            st.dataframe(_preparar_historial(historial_total), use_container_width=True, hide_index=True)
        else:
            st.info("Todavía no hay historial acumulado.")

    with tab_sesiones:
        sesiones = service.obtener_sesiones()
        if sesiones:
            filas = [
                {
                    "Sesión": str(item.get("id", ""))[:8],
                    "Integrante A": item.get("developer_a", ""),
                    "Integrante B": item.get("developer_b", ""),
                    "Piloto actual": item.get("current_piloto", ""),
                    "Copiloto actual": item.get("current_copiloto", ""),
                    "Intervalo": f"{item.get('interval_minutes', '')} min",
                    "Estado": item.get("status", ""),
                    "Creada": item.get("created_at", ""),
                }
                for item in sesiones
            ]
            st.dataframe(filas, use_container_width=True, hide_index=True)
        else:
            st.info("No existen sesiones registradas.")
