import json
import re
from typing import Optional, List, Dict, Any
from redis import Redis

# Prefijo para las claves en Redis
PREFIJO_USUARIO = "usuario:"


def validar_id_usuario(id_usuario: str) -> None:
    # Verifica que `id_usuario` cumpla el patrón permitido.
    # Lanza `ValueError` si no coincide con 3-40 caracteres alfanuméricos, _ o -
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,40}", id_usuario):
        raise ValueError(
            "id_usuario inválido. Usa 3-40 caracteres alfanuméricos, _ o -"
        )


def construir_clave_usuario(id_usuario: str) -> str:
    # Construye la clave Redis con el prefijo
    return f"{PREFIJO_USUARIO}{id_usuario}"


def normalizar_id_usuario(datos: Dict[str, Any]) -> str:
    # Extrae y valida el id_usuario desde un diccionario
    id_usuario = datos.get("id_usuario", datos.get("id"))
    if id_usuario is None:
        raise ValueError("El JSON debe incluir 'id_usuario' o 'id'.")

    id_usuario = str(id_usuario).strip()
    validar_id_usuario(id_usuario)
    return id_usuario


def crear_usuario_json(conexion: Redis, usuario_json: str) -> bool:
    # Crea un usuario en Redis usando SET con NX
    datos = json.loads(usuario_json)

    if not isinstance(datos, dict):
        raise ValueError("El JSON debe ser un objeto.")

    id_usuario = normalizar_id_usuario(datos)
    datos["id_usuario"] = id_usuario

    clave = construir_clave_usuario(id_usuario)
    valor = json.dumps(datos, ensure_ascii=False)

    creado = conexion.set(clave, valor, nx=True)
    return bool(creado)


def leer_usuario_json(conexion: Redis, id_usuario: str) -> Optional[Dict[str, Any]]:
    # Lee un usuario desde Redis
    id_usuario = str(id_usuario).strip()
    validar_id_usuario(id_usuario)

    valor = conexion.get(construir_clave_usuario(id_usuario))
    if valor is None:
        return None

    datos = json.loads(valor)

    if isinstance(datos, dict) and "id_usuario" not in datos:
        datos["id_usuario"] = id_usuario

    return datos


def actualizar_usuario_json(
    conexion: Redis,
    id_usuario: str,
    json_actualizacion: str,
    modo: str = "mezclar"
) -> bool:
    # Actualiza un usuario existente

    actual = leer_usuario_json(conexion, id_usuario)
    if actual is None:
        return False

    nuevos_datos = json.loads(json_actualizacion)
    if not isinstance(nuevos_datos, dict):
        raise ValueError("El JSON de actualización debe ser un objeto.")

    if modo == "reemplazar":
        resultado = nuevos_datos
    elif modo == "mezclar":
        resultado = dict(actual)
        resultado.update(nuevos_datos)
    else:
        raise ValueError("Modo inválido. Usa 'mezclar' o 'reemplazar'.")

    resultado["id_usuario"] = id_usuario

    conexion.set(
        construir_clave_usuario(id_usuario),
        json.dumps(resultado, ensure_ascii=False)
    )

    return True


def eliminar_usuario(conexion: Redis, id_usuario: str) -> bool:
    # Elimina un usuario por id
    eliminado = conexion.delete(construir_clave_usuario(id_usuario))
    return eliminado == 1


def listar_usuarios(conexion: Redis) -> List[Dict[str, Any]]:
    # Lista todos los usuarios almacenados
    ids = sorted(conexion.keys("*"))
    resultado = []

    for clave in ids:
        if clave.startswith(PREFIJO_USUARIO):
            id_usuario = clave.replace(PREFIJO_USUARIO, "")
            datos = leer_usuario_json(conexion, id_usuario)
            if datos:
                resultado.append(datos)

    return resultado
