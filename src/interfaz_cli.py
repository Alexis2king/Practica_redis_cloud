# Interfaz de texto simple para usar en consola.
# Presenta un menú interactivo que llama a las funciones
# de modelo_usuario usando obtener_conexion().

import json
from typing import Any
from dotenv import load_dotenv

from cliente_redis import obtener_conexion
from modelo_usuario import (
    crear_usuario_json,
    leer_usuario_json,
    actualizar_usuario_json,
    eliminar_usuario,
    listar_usuarios,
)

# Cargar variables de entorno (.env)
load_dotenv()


def imprimir(obj: Any) -> None:
    # Imprime en formato JSON legible
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def prompt_json(prompt: str) -> str:
    # Solicita JSON y lo valida
    texto = input(prompt).strip()
    if not texto:
        raise ValueError("Entrada JSON vacía")

    # Validar que sea JSON válido
    json.loads(texto)

    return texto


def menu() -> None:
    try:
        conexion = obtener_conexion()
    except Exception as e:
        print(f"ERROR: no se pudo conectar a Redis: {e}")
        return

    while True:
        print("\n--- Menú usuarios Redis ---")
        print("1) Crear usuario (introduce JSON)")
        print("2) Leer usuario (id)")
        print("3) Actualizar usuario (id + JSON)")
        print("4) Eliminar usuario (id)")
        print("5) Listar usuarios")
        print("6) Salir")

        opcion = input("Selecciona opción: ").strip()

        try:
            if opcion == "1":
                try:
                    datos = prompt_json("JSON usuario: ")
                except Exception as e:
                    print(f"JSON inválido: {e}")
                    continue

                creado = crear_usuario_json(conexion, datos)
                imprimir({"creado": bool(creado)})

            elif opcion == "2":
                idu = input("id_usuario: ").strip()
                usuario = leer_usuario_json(conexion, idu)
                imprimir({"usuario": usuario})

            elif opcion == "3":
                idu = input("id_usuario: ").strip()

                try:
                    datos = prompt_json("JSON actualización: ")
                except Exception as e:
                    print(f"JSON inválido: {e}")
                    continue

                modo = input("modo (mezclar/reemplazar) [mezclar]: ").strip()
                if not modo:
                    modo = "mezclar"

                actualizado = actualizar_usuario_json(
                    conexion,
                    idu,
                    datos,
                    modo=modo
                )

                imprimir({"actualizado": bool(actualizado)})

            elif opcion == "4":
                idu = input("id_usuario: ").strip()
                eliminado = eliminar_usuario(conexion, idu)
                imprimir({"eliminado": bool(eliminado)})

            elif opcion == "5":
                usuarios = listar_usuarios(conexion)
                imprimir({
                    "total": len(usuarios),
                    "usuarios": usuarios
                })

            elif opcion == "6":
                print("Adiós")
                break

            else:
                print("Opción no reconocida")

        except Exception as e:
            print(f"ERROR: {e}")


def main() -> int:
    try:
        menu()
        return 0
    except KeyboardInterrupt:
        print("\nInterrumpido")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
