"""
Servicio de cálculo de nómina.
Lógica de negocio pura. Sin persistencia.
"""
from __future__ import annotations
from datetime import date
from models.domain.empleado import Empleado
from models.domain.configuracion import ConfiguracionNomina
from models.domain.nomina import RegistroNomina
from models.domain.nomina import ResultadoLiquidacion, ItemConcepto


class CalculadoraNomina:
    """Servicio de cálculo de nómina - lógica de negocio pura"""
    
    def __init__(self, config: ConfiguracionNomina):
        self.config = config
    @staticmethod
    def calcular_dias_laborados(fecha_inicio: date, fecha_cierre: date) -> int:
        """
        Calcula los días laborados de un período como días calendario inclusivos.
        Ej: del 1 al 15 -> 15 días. Del 16 al 30 -> 15 días.
        """
        return (fecha_cierre - fecha_inicio).days + 1
    
    @staticmethod
    def validar_periodo(fecha_inicio: date, fecha_cierre: date) -> bool:
        """Valida que el período sea válido"""
        return fecha_inicio < fecha_cierre
    
    def calcular_ordinario(self, empleado: Empleado, dias: int) -> float:
        """Calcula salario ordinario proporcional"""
        return (empleado.salario / 30) * dias
    
    def calcular_auxilio_transporte(self, empleado: Empleado, dias: int) -> float:
        """Calcula auxilio de transporte si aplica"""
        if not empleado.debe_recibir_auxilio(self.config):
            return 0.0
        return (self.config.auxilio_transporte_mensual / 30) * dias
    
    def calcular_horas_extras(self, empleado: Empleado, horas: int) -> float:
        """Calcula valor de horas extras"""
        valor_hora = empleado.salario / 240  # 240 horas mensuales
        return valor_hora * horas * 1.25  # 25% recargo
    
    def calcular_afp(self, base: float) -> float:
        """Calcula descuento AFP"""
        return base * self.config.porcentaje_afp
    
    def calcular_eps(self, base: float) -> float:
        """Calcula descuento EPS"""
        return base * self.config.porcentaje_eps
    
    def liquidar(
    self,
    empleado: Empleado,
    fecha_inicio: date,
    fecha_cierre: date,
    dias_laborados: int,
    horas_extras: int = 0,
    conceptos_aplicados: list[ItemConcepto] = None,
    conceptos_omitidos: list[dict] = None,
    ) -> ResultadoLiquidacion:
        """Liquidación completa de un empleado — todos los valores a 2 decimales."""
        if not self.validar_periodo(fecha_inicio, fecha_cierre):
            raise ValueError("Período inválido")

        ordinario = round(self.calcular_ordinario(empleado, dias_laborados), 2)
        auxilio = round(self.calcular_auxilio_transporte(empleado, dias_laborados), 2)
        valor_horas_extras = round(self.calcular_horas_extras(empleado, horas_extras), 2)

        total_devengado = ordinario + auxilio + valor_horas_extras

        total_conceptos_devengados = 0.0
        total_conceptos_deducciones = 0.0

        if conceptos_aplicados:
            for concepto in conceptos_aplicados:
                if concepto.naturaleza == "devengado":
                    total_conceptos_devengados += concepto.valor
                else:
                    total_conceptos_deducciones += concepto.valor

        total_conceptos_devengados = round(total_conceptos_devengados, 2)
        total_conceptos_deducciones = round(total_conceptos_deducciones, 2)
        total_devengado = round(total_devengado + total_conceptos_devengados, 2)

        # AFP y EPS se calculan sobre ordinario (regla actual — revisar si debe incluir HE)
        afp = round(self.calcular_afp(ordinario), 2)
        eps = round(self.calcular_eps(ordinario), 2)

        total_deducciones = round(afp + eps + total_conceptos_deducciones, 2)
        salario_neto = round(total_devengado - total_deducciones, 2)

        return ResultadoLiquidacion(
            ordinario=ordinario,
            auxilio_transporte=auxilio,
            horas_extras=valor_horas_extras,
            total_devengado=total_devengado,
            salario_base_periodo=ordinario,
            descuento_afp=afp,
            descuento_eps=eps,
            otros_descuentos=total_conceptos_deducciones,
            total_deducciones=total_deducciones,
            salario_neto=salario_neto,
            conceptos_aplicados=conceptos_aplicados or [],
            conceptos_omitidos=conceptos_omitidos or [],
        )