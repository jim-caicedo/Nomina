from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from models.configuracion import ConfiguracionNomina


@dataclass
class Empleado:
    """Modelo de Empleado con información laboral para nómina."""
    
    id: int
    nombre: str
    apellido: str
    cargo: str
    salario: float  # Salario base mensual
    correo: str = ""
    telefono: str = ""
    numero_cuenta: str = ""
    eps: str = "EPS por asignar"  # Nombre de la EPS
    afp: str = "AFP por asignar"  # Nombre de la AFP
    sede_laboral: str = ""
    auxilio_transporte_mensual: float = 161_916  # 2026
    fecha_ingreso: datetime = None
    horas_extra: float = 0.0
    recibe_auxilio_transporte: bool = True  # True si gana <= 2 SMMLV

    def get_nombre_completo(self) -> str:
        """Retorna el nombre completo (Nombre Apellido)."""
        return f"{self.nombre} {self.apellido}".strip()

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.get_nombre_completo(),
            "cargo": self.cargo,
            "salario": self.salario,
            "correo": self.correo,
            "telefono": self.telefono,
            "numero_cuenta": self.numero_cuenta,
            "eps": self.eps,
            "afp": self.afp,
            "sede_laboral": self.sede_laboral,
            "auxilio_transporte_mensual": self.auxilio_transporte_mensual,
            "fecha_ingreso": self.fecha_ingreso,
            "horas_extra": self.horas_extra,
            "recibe_auxilio_transporte": self.recibe_auxilio_transporte,
        }

    def debe_recibir_auxilio(self, config: Optional[ConfiguracionNomina] = None) -> bool:
        """
        Determina si el empleado debe recibir auxilio de transporte.
        
        Args:
            config: ConfiguracionNomina actual (opcional, usa defaults si no se proporciona)
        
        Returns:
            True si el empleado debe recibir auxilio, False en caso contrario
        """
        # Si config no se proporciona, usar defaults de 2026
        if config is None:
            config = ConfiguracionNomina.crear_default_2026()
        
        # El empleado recibe auxilio si:
        # 1. Tiene el flag activado manualmente
        # 2. Y su salario es <= 2 SMMLV
        return self.recibe_auxilio_transporte and self.salario <= (2 * config.salario_minimo_mensual)
