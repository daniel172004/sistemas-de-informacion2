import pytest

from hu02_revision_codigo.repository import InMemoryCodeReviewRepository
from hu02_revision_codigo.service import RevisionCodigo
from shared.exceptions import ValidationError


@pytest.fixture
def revision():
    return RevisionCodigo(repository=InMemoryCodeReviewRepository())


def test_verificar_que_el_programador_revisor_tarea_observaciones_y_estado_se_guarden_correctamente(revision):
    review = revision.guardar(
        programador="Ana",
        revisor="Luis",
        tarea="Login",
        observaciones="Todo correcto",
        estado="Aprobado",
    )

    assert review["programmer_name"] == "Ana"
    assert review["reviewer_name"] == "Luis"
    assert review["reviewed_task"] == "Login"
    assert review["observations"] == "Todo correcto"
    assert review["status"] == "Aprobado"


def test_verificar_que_si_falta_un_campo_obligatorio_se_muestre_error(revision):
    with pytest.raises(ValidationError):
        revision.guardar(
            programador="Ana",
            revisor="",
            tarea="Login",
            observaciones="Todo correcto",
            estado="Aprobado",
        )


def test_verificar_que_no_se_acepte_un_estado_de_revision_invalido(revision):
    with pytest.raises(ValidationError):
        revision.guardar(
            programador="Ana",
            revisor="Luis",
            tarea="Login",
            observaciones="Observación",
            estado="Pendiente",
        )


def test_verificar_que_el_estado_con_observaciones_exija_registrar_observaciones(revision):
    with pytest.raises(ValidationError):
        revision.guardar(
            programador="Ana",
            revisor="Luis",
            tarea="Login",
            observaciones="",
            estado="Con observaciones",
        )


def test_verificar_que_la_lista_de_revisiones_muestre_tarea_programador_revisor_fecha_y_estado(revision):
    revision.guardar("Ana", "Luis", "Login", "Todo correcto", "Aprobado")

    lista = revision.listar_revisiones()

    assert len(lista) == 1
    assert lista[0]["reviewed_task"] == "Login"
    assert lista[0]["programmer_name"] == "Ana"
    assert lista[0]["reviewer_name"] == "Luis"
    assert lista[0]["review_date"]
    assert lista[0]["status"] == "Aprobado"


def test_verificar_que_al_cambiar_el_estado_a_corregido_se_actualice_correctamente(revision):
    revision.guardar("Ana", "Luis", "Login", "Falta validar campos", "Con observaciones")

    actualizado = revision.actualizar_estado("Corregido")

    assert actualizado["status"] == "Corregido"
    assert revision.estado == "Corregido"


def test_verificar_que_se_pueda_editar_la_tarea_revisada_las_observaciones_y_el_estado(revision):
    revision.guardar("Ana", "Luis", "Login", "Error menor", "Con observaciones")

    editado = revision.editar(
        tarea="Login con validaciones",
        observaciones="Validaciones corregidas",
        estado="Corregido",
    )

    assert editado["reviewed_task"] == "Login con validaciones"
    assert editado["observations"] == "Validaciones corregidas"
    assert editado["status"] == "Corregido"


def test_verificar_que_la_fecha_de_revision_se_genere_automaticamente_al_guardar(revision):
    review = revision.guardar("Ana", "Luis", "Login", "Todo correcto", "Aprobado")

    assert review["review_date"] is not None
    assert "T" in review["review_date"]
    assert revision.fecha_revision == review["review_date"]
