#importar las librerias necesarias
import os
from dataclasses import dataclass
from redis import Redis
from dotenv import load_dotenv


# Cargar variables de entorno (.env o Secrets de GitHub)
load_dotenv()


@dataclass(frozen=True)
class ConfiguracionRedis:
    url: str


def obtener_configuracion() -> ConfiguracionRedis:
    """
    Lee la configuración de Redis desde las variables de entorno.

    Retorna una instancia inmutable de ConfiguracionRedis con la URL.
    Usa REDIS_URL o el valor por defecto redis://localhost:6379/0.
    """
    url = os.getenv("REDIS_URL", "redis://default:*******@redis-11308.c257.us-east-1-3.ec2.cloud.redislabs.com:11308")
    return ConfiguracionRedis(url=url)


def obtener_conexion() -> Redis:
    """
    Crea y devuelve una conexión Redis usando la configuración.

    Realiza un ping() para verificar la conexión antes de retornarla.
    Lanza excepciones si no se puede conectar.
    """
    config = obtener_configuracion()
    conexion = Redis.from_url(config.url, decode_responses=True)

    # Verificar conexión
    conexion.ping()

    return conexion

