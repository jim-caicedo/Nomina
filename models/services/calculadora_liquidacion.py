"""
Servicio de cálculo de liquidación final de contrato (Primas, Cesantías, Vacaciones, Indemnizaciones).
Lógica de negocio pura. Sin persistencia.
"""
from __future__ import annotations
from datetime import date
from dataclasses import dataclass, field
from models.domain.empleado import Empleado
from models.domain.configuracion import ConfiguracionNomina


@dataclass
class ResultadoLiquidacionFinal:
    """DTO / Dataclass de salida para la liquidación final de contrato."""
    dias_totales_trabajados: int
    dias_cesantias: int
    dias_prima: int
    dias_vacaciones: float
    
    # Bases de cálculo
    salario_base: float
    auxilio_transporte: float
    base_prestaciones: float  # Salario + Auxilio
    
    # Valorcitos de Prestaciones
    valor_cesantias: float
    valor_intereses_cesantias: float
    valor_prima: float
    valor_vacaciones: float
    valor_indemnizacion: float
    
    # Totales
    total_devengado: float
    total_deducciones: float
    neto_a_pagar: float
    
    motivo_retiro: str


class CalculadoraLiquidacionFinal:
    """Servicio de cálculo de liquidación de prestaciones e indemnizaciones."""

    def __init__(self, config: ConfiguracionNomina):
        self.config = config

    @staticmethod
    def calcular_dias_360(fecha_inicio: date, fecha_fin: date) -> int:
        """
        Calcula días laborales usando el método comercial colombiano (30 días por mes, 360 por año).
        Inclusivo (suma el día inicial).
        """
        if fecha_fin < fecha_inicio:
            return 0
        
        dias = (fecha_fin.year - fecha_inicio.year) * 360 + \
               (fecha_fin.month - fecha_inicio.month) * 30 + \
               (fecha_fin.day - fecha_inicio.day) + 1
        return max(0, dias)

    def calcular_base_prestacional(self, empleado: Empleado, promedio_variables: float = 0.0) -> tuple[float, float, float]:
        """
        Devuelve (salario_base, auxilio_transporte, base_prestaciones).
        Incluye promedio de horas extras/recargos si el empleado tiene salario variable.
        """
        salario_base = empleado.salario + promedio_variables
        
        # El auxilio de transporte entra a la base de Primas y Cesantías si el salario base <= 2 SMLMV
        if empleado.debe_recibir_auxilio(self.config):
            auxilio = self.config.auxilio_transporte_mensual
        else:
            auxilio = 0.0
            
        base_prestaciones = salario_base + auxilio
        return round(salario_base, 2), round(auxilio, 2), round(base_prestaciones, 2)

    def calcular_cesantias(self, base_prestaciones: float, dias_trabajados: int) -> float:
        """Fórmula: (Base * Días) / 360"""
        return round((base_prestaciones * dias_trabajados) / 360, 2)

    def calcular_intereses_cesantias(self, cesantias: float, dias_trabajados: int) -> float:
        """Fórmula: (Cesantías * Días * 0.12) / 360"""
        return round((cesantias * dias_trabajados * 0.12) / 360, 2)

    def calcular_prima(self, base_prestaciones: float, dias_semestre: int) -> float:
        """Fórmula: (Base * Días Semestre) / 360"""
        return round((base_prestaciones * dias_semestre) / 360, 2)

    def calcular_vacaciones(self, salario_base: float, dias_trabajados: int) -> float:
        """
        Fórmula: (Salario Base [Sin Auxilio] * Días) / 720
        """
        return round((salario_base * dias_trabajados) / 720, 2)

    def calcular_indemnizacion(
        self, 
        empleado: Empleado, 
        fecha_fin: date, 
        motivo: str, 
        fecha_fin_contrato_fijo: date | None = None
    ) -> float:
        """Calcula indemnización por despido sin justa causa según ley colombiana."""
        if motivo != "DESPIDO_SIN_JUSTA_CAUSA":
            return 0.0

        tipo_contrato = getattr(empleado, 'tipo_contrato', 'INDEFINIDO').upper()
        dias_totales = self.calcular_dias_360(empleado.fecha_ingreso, fecha_fin)
        salario_diario = empleado.salario / 30

        if "FIJO" in tipo_contrato:
            if not fecha_fin_contrato_fijo or fecha_fin_contrato_fijo <= fecha_fin:
                return 0.0
            dias_restantes = self.calcular_dias_360(fecha_fin, fecha_fin_contrato_fijo) - 1
            return round(salario_diario * max(0, dias_restantes), 2)

        # Contrato Indefinido
        smlmv = self.config.salario_minimo
        es_menor_10_smlmv = empleado.salario <= (10 * smlmv)

        if dias_totales <= 360:
            dias_indemnizacion = 30 if es_menor_10_smlmv else 20
        else:
            dias_primer_ano = 30 if es_menor_10_smlmv else 20
            dias_adicionales_por_ano = 20 if es_menor_10_smlmv else 15
            
            dias_posteriores = dias_totales - 360
            dias_indemnizacion = dias_primer_ano + (dias_posteriores * dias_adicionales_por_ano / 360)

        return round(salario_diario * dias_indemnizacion, 2)

    def liquidar_final(
        self,
        empleado: Empleado,
        fecha_retiro: date,
        motivo_retiro: str = "RENUNCIA",
        dias_vacaciones_tomadas: float = 0.0,
        promedio_variables: float = 0.0,
        deducciones_varias: float = 0.0,
        fecha_fin_contrato_fijo: date | None = None
    ) -> ResultadoLiquidacionFinal:
        """
        Orquesta la liquidación definitiva completa de un empleado.
        """
        # 1. Días de cómputo
        dias_totales = self.calcular_dias_360(empleado.fecha_ingreso, fecha_retiro)
        
        # Días año actual para Cesantías
        inicio_ano = date(fecha_retiro.year, 1, 1)
        fecha_inicio_cesantias = max(empleado.fecha_ingreso, inicio_ano)
        dias_cesantias = self.calcular_dias_360(fecha_inicio_cesantias, fecha_retiro)
        
        # Días semestre actual para Prima (Semestre 1: Ene-Jun, Semestre 2: Jul-Dic)
        if fecha_retiro.month <= 6:
            inicio_semestre = date(fecha_retiro.year, 1, 1)
        else:
            inicio_semestre = date(fecha_retiro.year, 7, 1)
            
        fecha_inicio_prima = max(empleado.fecha_ingreso, inicio_semestre)
        dias_prima = self.calcular_dias_360(fecha_inicio_prima, fecha_retiro)
        
        # Días acumulados para vacaciones pendientes
        dias_vacaciones_netos = max(0.0, dias_totales - (dias_vacaciones_tomadas * (360 / 15)))

        # 2. Bases monetarias
        salario_base, auxilio, base_prestaciones = self.calcular_base_prestacional(empleado, promedio_variables)

        # 3. Cálculos de cada concepto
        v_cesantias = self.calcular_cesantias(base_prestaciones, dias_cesantias)
        v_intereses = self.calcular_intereses_cesantias(v_cesantias, dias_cesantias)
        v_prima = self.calcular_prima(base_prestaciones, dias_prima)
        v_vacaciones = self.calcular_vacaciones(salario_base, int(dias_vacaciones_netos))
        v_indemnizacion = self.calcular_indemnizacion(empleado, fecha_retiro, motivo_retiro, fecha_fin_contrato_fijo)

        # 4. Totales
        total_devengado = round(v_cesantias + v_intereses + v_prima + v_vacaciones + v_indemnizacion, 2)
        total_deducciones = round(deducciones_varias, 2)
        neto_a_pagar = round(total_devengado - total_deducciones, 2)

        return ResultadoLiquidacionFinal(
            dias_totales_trabajados=dias_totales,
            dias_cesantias=dias_cesantias,
            dias_prima=dias_prima,
            dias_vacaciones=round(dias_vacaciones_netos, 2),
            salario_base=salario_base,
            auxilio_transporte=auxilio,
            base_prestaciones=base_prestaciones,
            valor_cesantias=v_cesantias,
            valor_intereses_cesantias=v_intereses,
            valor_prima=v_prima,
            valor_vacaciones=v_vacaciones,
            valor_indemnizacion=v_indemnizacion,
            total_devengado=total_devengado,
            total_deducciones=total_deducciones,
            neto_a_pagar=neto_a_pagar,
            motivo_retiro=motivo_retiro
        )