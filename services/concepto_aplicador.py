from datetime import date
from typing import Dict, List, Optional

from models.conceptos.concepto_empleado_repository import ConceptoEmpleadoRepositorySQLite
from models.conceptos.concepto_repository import ConceptoRepositorySQLite
from models.conceptos.concepto_factory import ConceptoFactory


class ConceptoAplicador:
    @staticmethod
    def aplicar(
        empleado,
        fecha_inicio: date,
        fecha_cierre: date,
    ) -> dict:
        resultado = {
            "devengados": [],
            "deducciones": [],
            "suma_devengados": 0.0,
            "suma_deducciones": 0.0,
            "omitidos": [],
        }

        try:
            asign_repo = ConceptoEmpleadoRepositorySQLite()
            plantilla_repo = ConceptoRepositorySQLite()
            asignaciones = asign_repo.obtener_por_empleado(getattr(empleado, "id", None)) or []

            for asign in asignaciones:
                nombre_concepto = getattr(asign, "nombre", "concepto desconocido")
                tipo_estrategia = getattr(asign, "tipo", "fijo")
                naturaleza = None

                try:
                    plantilla = None
                    if getattr(asign, "concepto_id", None):
                        plantilla = plantilla_repo.obtener_por_id(asign.concepto_id)

                    if plantilla:
                        naturaleza = getattr(plantilla, "naturaleza", None)
                    else:
                        naturaleza = getattr(asign, "naturaleza", None)

                    if not naturaleza:
                        resultado["omitidos"].append({
                            "nombre": nombre_concepto,
                            "razon": "naturaleza no definida",
                        })
                        continue

                    if plantilla and getattr(plantilla, "tipo", None):
                        tipo_estrategia = plantilla.tipo
                    nombre_concepto = plantilla.nombre if plantilla and getattr(plantilla, "nombre", None) else nombre_concepto

                    valor_base = (
                        asign.valor_personalizado
                        if getattr(asign, "valor_personalizado", None) is not None
                        else (plantilla.valor if plantilla else 0.0)
                    )
                    porcentaje = (
                        asign.porcentaje_personalizado
                        if getattr(asign, "porcentaje_personalizado", None) is not None
                        else (plantilla.porcentaje if plantilla else 0.0)
                    )
                    base_calculo = getattr(asign, "base_calculo", None) or (plantilla.base_calculo if plantilla else "salario")

                    estrategia = ConceptoFactory.crear(
                        tipo_estrategia,
                        nombre_concepto,
                        valor=valor_base,
                        porcentaje=porcentaje,
                        base_calculo=base_calculo,
                    )
                    valor_calc = round(
                        estrategia.calcular(empleado, fecha_inicio, fecha_cierre, valor_ingresado=0.0),
                        2,
                    )

                    concepto_dict = {
                        "nombre": nombre_concepto,
                        "tipo": tipo_estrategia,
                        "valor": valor_calc,
                    }

                    if str(naturaleza).strip().lower() == "deduccion":
                        resultado["deducciones"].append(concepto_dict)
                        resultado["suma_deducciones"] += valor_calc
                    else:
                        resultado["devengados"].append(concepto_dict)
                        resultado["suma_devengados"] += valor_calc

                except Exception as e:
                    resultado["omitidos"].append({
                        "nombre": nombre_concepto,
                        "razon": str(e),
                    })
                    continue

        except Exception as e:
            resultado["omitidos"].append({
                "nombre": "conceptos asignados",
                "razon": str(e),
            })

        return resultado
