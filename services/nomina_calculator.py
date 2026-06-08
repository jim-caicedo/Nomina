"""
Servicio de cálculo de nómina quincenal.
Implementa las fórmulas exactas de nómina ley colombiana.

Fórmulas:
- Ordinario Diurno: (salario_base_mensual / 30) * dias_laborados
- Auxilio Transporte: (auxilio_transporte_mensual / 30) * dias_laborados
- Horas Extras: valor_hora_extra * numero_horas_extra
- Total Devengado: Ordinario + Auxilio + Horas Extras
- AFP (Pensión): salario_base_periodo * porcentaje_afp (SOLO sobre ordinario, NO auxilio)
- EPS (Salud): salario_base_periodo * porcentaje_eps (SOLO sobre ordinario, NO auxilio)
- Total Deducciones: AFP + EPS + Otros Descuentos
- Salario Neto: Total Devengado - Total Deducciones
"""

from datetime import date
from typing import Dict, Optional
from config.constants import DIAS_MES_PROMEDIO
from models.configuracion import ConfiguracionNomina
from models.conceptos.concepto_empleado_repository import ConceptoEmpleadoRepositorySQLite
from models.conceptos.concepto_repository import ConceptoRepositorySQLite
from models.conceptos.concepto_factory import ConceptoFactory
from typing import List


class LiquidadorNomina:
    """Clase responsable de calcular nómina quincenal según ley colombiana."""

    @staticmethod
    def liquidar(
        empleado,
        fecha_inicio: date,
        fecha_cierre: date,
        dias_laborados: int,
        horas_extras: int = 0,
        otros_descuentos: float = 0.0,
        config: Optional[ConfiguracionNomina] = None,
    ) -> Dict[str, float]:
        """
        Calcula la nómina para un empleado en un período específico.

        Args:
            empleado: Objeto Empleado con salario_base y auxilio_transporte_mensual
            fecha_inicio: Fecha de inicio del período (date)
            fecha_cierre: Fecha de cierre del período (date)
            dias_laborados: Número de días laborados en el período (1-30)
            horas_extras: Número de horas extras trabajadas (default 0)
            otros_descuentos: Otros descuentos adicionales (default 0)
            config: ConfiguracionNomina con parámetros legales vigentes

        Returns:
            Diccionario con todos los valores calculados de la nómina

        Raises:
            ValueError: Si los datos no son válidos
        """
        # Validaciones
        if dias_laborados < 1 or dias_laborados > 30:
            raise ValueError("Los días laborados deben estar entre 1 y 30.")
        if horas_extras < 0:
            raise ValueError("Las horas extras no pueden ser negativas.")
        if empleado.salario <= 0:
            raise ValueError("El salario del empleado debe ser positivo.")

        # Si no se proporciona config, usar valores por defecto de 2026
        if config is None:
            config = ConfiguracionNomina.crear_default_2026()

        # Validar que el salario no sea inferior al mínimo (advertencia, no bloquear)
        if empleado.salario < config.salario_minimo_mensual:
            import warnings
            warnings.warn(
                f"El salario del empleado ${empleado.salario:,.2f} es inferior "
                f"al salario mínimo vigente ${config.salario_minimo_mensual:,.2f}"
            )

        # ========== CÁLCULOS DE DEVENGADOS ==========
        # 1. Ordinario Diurno: (salario_base_mensual / 30) * dias_laborados
        salario_diario = empleado.salario / DIAS_MES_PROMEDIO
        ordinario = round(salario_diario * dias_laborados, 2)

        # 2. Auxilio Transporte: (auxilio_transporte_mensual / 30) * dias_laborados
        # Usar el auxilio del empleado, si no tiene, usar el de la configuración
        auxilio_mensual = getattr(
            empleado, "auxilio_transporte_mensual", config.auxilio_transporte_mensual
        )
        auxilio_diario = auxilio_mensual / DIAS_MES_PROMEDIO
        auxilio_transporte = round(auxilio_diario * dias_laborados, 2)

        # 3. Horas Extras: valor_hora_extra * numero_horas_extra
        valor_hora_extra = 25.0  # Valor colombiano estándar
        horas_extras_total = round(valor_hora_extra * horas_extras, 2)

        # 4. Total Devengado = Ordinario + Auxilio + Horas Extras
        total_devengado = round(ordinario + auxilio_transporte + horas_extras_total, 2)

        # ========== CÁLCULOS DE DEDUCCIONES ==========
        # IMPORTANTE: Las deducciones se calculan SOLO sobre el salario ordinario
        # NO se incluye auxilio transporte ni horas extras
        salario_base_periodo = ordinario

        # 1. AFP (Pensión): porcentaje_afp del salario_base_periodo
        descuento_afp = round(salario_base_periodo * config.porcentaje_afp, 2)

        # 2. EPS (Salud): porcentaje_eps del salario_base_periodo
        descuento_eps = round(salario_base_periodo * config.porcentaje_eps, 2)

        # 3. Otros Descuentos (si existen)
        otros_descuentos = round(otros_descuentos, 2)

        # ======== CONCEPTOS ASIGNADOS (DEVENGADOS / DEDUCCIONES) ========
        conceptos_aplicados: List[dict] = []
        suma_conceptos_devengado = 0.0
        suma_conceptos_deduccion = 0.0

        try:
            asign_repo = ConceptoEmpleadoRepositorySQLite()
            plantilla_repo = ConceptoRepositorySQLite()
            asignaciones = asign_repo.obtener_por_empleado(getattr(empleado, "id", None)) or []

            for asign in asignaciones:
                try:
                    plantilla = None
                    if asign.concepto_id:
                        plantilla = plantilla_repo.obtener_por_id(asign.concepto_id)

                    tipo_estrategia = (plantilla.tipo if plantilla and plantilla.tipo else asign.tipo)
                    nombre_concepto = (plantilla.nombre if plantilla and plantilla.nombre else asign.nombre)
                    naturaleza = (plantilla.naturaleza if plantilla and getattr(plantilla, 'naturaleza', None) else getattr(asign, 'naturaleza', 'devengado'))

                    valor_base = asign.valor_personalizado if asign.valor_personalizado is not None else (plantilla.valor if plantilla else 0.0)
                    porcentaje = asign.porcentaje_personalizado if asign.porcentaje_personalizado is not None else (plantilla.porcentaje if plantilla else 0.0)
                    base_calculo = asign.base_calculo or (plantilla.base_calculo if plantilla else "salario")

                    estrategia = ConceptoFactory.crear(tipo_estrategia, nombre_concepto, valor=valor_base, porcentaje=porcentaje, base_calculo=base_calculo)
                    valor_calc = round(estrategia.calcular(empleado, fecha_inicio, fecha_cierre, valor_ingresado=0.0), 2)

                    conceptos_aplicados.append({
                        "nombre": nombre_concepto,
                        "tipo_estrategia": tipo_estrategia,
                        "naturaleza": naturaleza,
                        "valor": valor_calc,
                    })

                    if naturaleza and naturaleza.lower() == "deduccion":
                        suma_conceptos_deduccion += valor_calc
                    else:
                        suma_conceptos_devengado += valor_calc

                except Exception as e:
                    print(f"Error aplicando concepto para empleado {getattr(empleado,'id',None)}: {e}")
                    continue
        except Exception as e:
            print(f"Error consultando asignaciones de conceptos: {e}")

        # Añadir devengados de conceptos al total devengado
        total_devengado = round(total_devengado + suma_conceptos_devengado, 2)

        # 4. Total Deducciones (incluye conceptos que son deducciones)
        otros_descuentos = round(otros_descuentos + suma_conceptos_deduccion, 2)
        total_deducciones = round(descuento_afp + descuento_eps + otros_descuentos, 2)

        # ========== SALARIO NETO ==========
        salario_neto = round(total_devengado - total_deducciones, 2)

        # Retornar diccionario con todos los valores
        return {
            "ordinario": ordinario,
            "auxilio_transporte": auxilio_transporte,
            "horas_extras": horas_extras_total,
            "total_devengado": total_devengado,
            "salario_base_periodo": salario_base_periodo,
            "descuento_afp": descuento_afp,
            "descuento_eps": descuento_eps,
            "otros_descuentos": otros_descuentos,
            "total_deducciones": total_deducciones,
            "salario_neto": salario_neto,
            "conceptos_aplicados": conceptos_aplicados,
        }

    @staticmethod
    def validar_periodo(fecha_inicio: date, fecha_cierre: date) -> bool:
        """
        Valida que el período sea válido (fecha_inicio < fecha_cierre).

        Args:
            fecha_inicio: Fecha de inicio
            fecha_cierre: Fecha de cierre

        Returns:
            True si es válido, False en caso contrario
        """
        return fecha_inicio < fecha_cierre
