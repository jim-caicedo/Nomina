"""
Enumeraciones del dominio de NominaSG.
Un solo lugar para cambiar valores constantes compartidos entre capas.
"""
from enum import Enum


class TipoCuenta(str, Enum):
    AHORROS = "AHORROS"
    CORRIENTE = "CORRIENTE"


class TipoDocumento(str, Enum):
    CC = "CC"       # Cédula de ciudadanía
    CE = "CE"       # Cédula de extranjería
    NIT = "NIT"     # NIT empresa
    TI = "TI"       # Tarjeta de identidad
    PPT = "PPT"     # Permiso de protección temporal


class TipoHoraExtra(str, Enum):
    DIURNA = "DIURNA"                       # 6am-9pm    recargo 1.25
    NOCTURNA = "NOCTURNA"                   # 9pm-6am    recargo 1.75
    DOMINICAL_DIURNA = "DOMINICAL_DIURNA"   # festivo 6am-9pm  recargo 1.75
    DOMINICAL_NOCTURNA = "DOMINICAL_NOCTURNA"  # festivo 9pm-6am recargo 2.25


# Recargos legales Colombia (Decreto 1072/2015)
RECARGO_HORA_EXTRA: dict[TipoHoraExtra, float] = {
    TipoHoraExtra.DIURNA: 1.25,
    TipoHoraExtra.NOCTURNA: 1.75,
    TipoHoraExtra.DOMINICAL_DIURNA: 1.75,
    TipoHoraExtra.DOMINICAL_NOCTURNA: 2.25,
}
