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
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return ConfiguracionRedis(url=url)

def obtener_conexion() -> Redis:
    config = obtener_configuracion()
    conexion = Redis.from_url(config.url, decode_responses=True)
    conexion.ping()  # Verifica conexión
    return conexion
