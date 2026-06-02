import pytest

from hu01_temporizador_rotacion_roles.repository import InMemoryRotationRepository
from hu01_temporizador_rotacion_roles.service import RotadorRoles
from shared.exceptions import ValidationError


@pytest.fixture
def rotador():
    repo = InMemoryRotationRepository()
    service = RotadorRoles(repository=repo, developer_a="Ana", developer_b="Luis")
    service.configurar_intervalo(15)
    service.iniciar(piloto="Ana", copiloto="Luis")
    return service


def test_verificar_que_el_intervalo_configurado_se_guarde_correctamente(rotador):
    assert rotador.intervalo == 15
    assert rotador.obtener_intervalo_visible() == "Rotación cada 15 minutos"


def test_verificar_que_no_se_permita_un_intervalo_invalido():
    rotador = RotadorRoles(repository=InMemoryRotationRepository())
    with pytest.raises(ValidationError):
        rotador.configurar_intervalo(0)


def test_verificar_que_al_iniciar_la_sesion_se_asignen_piloto_y_copiloto(rotador):
    assert rotador.en_ejecucion is True
    assert rotador.roles["Ana"] == "Piloto"
    assert rotador.roles["Luis"] == "Copiloto"


def test_verificar_que_la_notificacion_indique_quien_asume_cada_nuevo_rol(rotador):
    aviso = rotador.obtener_notificacion_rotacion(segundos_transcurridos=15 * 60)
    assert aviso["debe_rotar"] is True
    assert aviso["nuevo_piloto"] == "Luis"
    assert aviso["nuevo_copiloto"] == "Ana"
    assert "Luis será Piloto" in aviso["mensaje"]


def test_verificar_que_una_sola_confirmacion_no_reinicie_la_rotacion(rotador):
    resultado = rotador.confirmar_rotacion("Ana")
    assert resultado is False
    assert rotador.roles["Ana"] == "Piloto"
    assert rotador.roles["Luis"] == "Copiloto"


def test_verificar_que_al_confirmar_ambos_se_intercambien_los_roles_y_se_registre_historial(rotador):
    rotador.confirmar_rotacion("Ana")
    resultado = rotador.confirmar_rotacion("Luis")

    historial = rotador.obtener_historial()
    assert resultado is True
    assert rotador.roles["Ana"] == "Copiloto"
    assert rotador.roles["Luis"] == "Piloto"
    assert len(historial) == 1
    assert historial[0]["piloto"] == "Luis"
    assert historial[0]["copiloto"] == "Ana"


def test_verificar_que_se_envie_recordatorio_si_un_integrante_no_confirma(rotador):
    rotador.confirmar_rotacion("Ana")
    mensaje = rotador.enviar_recordatorio_si_falta()
    assert mensaje == "Recordatorio enviado a Luis"


def test_verificar_que_el_temporizador_pueda_pausarse_y_reanudarse_sin_perder_el_progreso(rotador):
    rotador.descontar_tiempo(120)
    restante_antes_de_pausar = rotador.remaining_seconds

    rotador.pausar()
    assert rotador.en_ejecucion is False
    assert rotador.pausado is True
    assert rotador.remaining_seconds == restante_antes_de_pausar

    rotador.reanudar()
    assert rotador.en_ejecucion is True
    assert rotador.pausado is False
    assert rotador.remaining_seconds == restante_antes_de_pausar
