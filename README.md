<<<<<<< HEAD
# sistemas-de-informacion2
para la tarea del dia martes
=======
# ELEKTRON XP · Pair Programming

Proyecto académico en Python para dos historias de usuario XP:

- **HU1:** Temporizador de rotación de roles Piloto/Copiloto.
- **HU2:** Revisión de código en pareja.

Incluye:

- Interfaz amigable con Streamlit.
- Lógica separada por carpetas para cada HU.
- Repositorios en memoria para pruebas rápidas.
- Repositorios Supabase para persistencia real.
- 8 tests por HU usando pytest.

---

## 1. Instalar dependencias

Desde la carpeta principal del proyecto:

```bash
pip install -r requirements.txt
```

---

## 2. Ver la interfaz

```bash
streamlit run app.py
```

Luego abre el enlace que aparece en consola, normalmente:

```text
http://localhost:8501
```

### Mejora visual incluida

La interfaz tiene:

- Panel principal moderno.
- Tarjetas visuales para roles y revisiones.
- Métricas de revisiones.
- Tabs para separar registro, lista, edición e historial.
- Temporizador más claro: cuando llega a cero queda en **Esperando confirmación**, no parece infinito.
- Historial acumulado: si creas otra sesión o cambias integrantes, el historial anterior no se borra.

---

## 3. Ejecutar tests

Todos los tests:

```bash
pytest -v
```

Solo HU1:

```bash
pytest hu01_temporizador_rotacion_roles/tests -v
```

Solo HU2:

```bash
pytest hu02_revision_codigo/tests -v
```

Resultado esperado:

```text
16 passed
```

---

## 4. Usar Supabase

Primero crea las tablas ejecutando este archivo en el SQL Editor de Supabase:

```text
docs/supabase_schema.sql
```

Luego copia `.env.example` como `.env`:

```bash
cp .env.example .env
```

En Windows PowerShell puedes usar:

```powershell
Copy-Item .env.example .env
```

Configura tus credenciales:

```env
USE_SUPABASE=true
SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_KEY=TU_SUPABASE_KEY
```

Si `USE_SUPABASE=false`, la app funciona con memoria local para probar la interfaz sin base de datos.

---

## 5. Estructura del proyecto

```text
elektron_xp_supabase/
│
├── app.py
├── requirements.txt
├── pytest.ini
├── README.md
├── .env.example
│
├── shared/
│   ├── exceptions.py
│   └── supabase_client.py
│
├── hu01_temporizador_rotacion_roles/
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   ├── ui.py
│   └── tests/
│       └── test_rotador_roles.py
│
├── hu02_revision_codigo/
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   ├── ui.py
│   └── tests/
│       └── test_revision_codigo.py
│
└── docs/
    └── supabase_schema.sql
```
>>>>>>> 3968bc6 (Subida inicial del proyecto desde ZIP)
