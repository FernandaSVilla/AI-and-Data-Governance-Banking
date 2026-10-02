"""evaluabilidad: auditoría de la puerta de entrada.

Mide, para cada perfil de entrada, si quienes intentan darse de alta llegan por igual a tener
cuenta, a ser evaluados por el modelo de crédito y a obtener crédito, e indica en qué etapa del
proceso se observa la primera diferencia (alta, llegada al modelo o decisión). Mide asociaciones, no causas.
"""
from .perfiles import PERFILES, REFERENCIA
from .metricas import (CAUSAS, UMBRAL, N_MINIMO, VISTAS, ETAPAS, preparar, validar, embudo, cocientes, diagnostico,
                       trazabilidad, causas_por_perfil, por_canal, calcular_todo, auditoria_convencional)
from .informe import generar_informe
from .representacion import representacion
from . import encuestas

__version__ = "0.4.0"
__all__ = ["PERFILES", "REFERENCIA", "CAUSAS", "UMBRAL", "N_MINIMO", "VISTAS", "ETAPAS", "preparar", "validar", "embudo", "cocientes",
           "diagnostico", "trazabilidad", "causas_por_perfil", "por_canal", "calcular_todo", "generar_informe", "representacion"]
