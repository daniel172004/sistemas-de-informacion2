"""Cliente de Supabase centralizado.

La app lee SUPABASE_URL y SUPABASE_KEY desde variables de entorno o archivo .env.
Los tests no dependen de Supabase; usan repositorios en memoria.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    """Retorna un cliente Supabase configurado.

    Raises:
        RuntimeError: si faltan SUPABASE_URL o SUPABASE_KEY.
    """
    load_dotenv()
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key:
        raise RuntimeError(
            "Faltan SUPABASE_URL o SUPABASE_KEY. Copia .env.example como .env y configura tus credenciales."
        )

    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("Instala dependencias con: pip install -r requirements.txt") from exc

    return create_client(url, key)


def should_use_supabase() -> bool:
    """Indica si la interfaz debe guardar datos en Supabase."""
    load_dotenv()
    return os.getenv("USE_SUPABASE", "false").strip().lower() == "true"
