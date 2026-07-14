"""
Modelo de dominio Empleado.
Solo datos y validaciones básicas. Sin lógica de negocio ni persistencia.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
from models.domain.configuracion import ConfiguracionNomina
from models.domain.enums import TipoCuenta, TipoDocumento


@dataclass
class Empleado:
    """Modelo de dominio puro — solo datos y validaciones básicas."""
    id: Optional[int] = None
    nombre: str = ""
    apellido: str = ""
    cargo: str = ""
    salario: float = 0.0
    correo: str = ""
    telefono: str = ""
    numero_cuenta: str = ""
    eps: str = ""
    afp: str = ""
    sede_laboral: str = ""
    cedula: str = ""
    fecha_ingreso: Optional[datetime] = None
    horas_extra: float = 0.0
    recibe_auxilio_transporte: bool = True
    activo: bool = True
    # Campos bancarios — necesarios para Excel banco
    codigo_banco: str = ""
    tipo_cuenta: str = TipoCuenta.AHORROS.value
    tipo_documento: str = TipoDocumento.CC.value

    def validar(self) -> tuple[bool, str]:
        if not self.nombre or not self.apellido:
            return False, "Nombre y apellido son obligatorios"
        if not self.cargo:
            return False, "Cargo es obligatorio"
        if self.salario <= 0:
            return False, "Salario debe ser positivo"
        return True, ""

    def get_nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}".strip()

    def debe_recibir_auxilio(self, config: ConfiguracionNomina) -> bool:
        """El valor del auxilio siempre viene de ConfiguracionNomina — fuente única."""
        return (
            self.recibe_auxilio_transporte
            and self.salario <= (2 * config.salario_minimo_mensual)
        )

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
            "cedula": self.cedula,
            "fecha_ingreso": self.fecha_ingreso,
            "horas_extra": self.horas_extra,
            "recibe_auxilio_transporte": self.recibe_auxilio_transporte,
            "activo": self.activo,
            "codigo_banco": self.codigo_banco,
            "tipo_cuenta": self.tipo_cuenta,
            "tipo_documento": self.tipo_documento,
        }
