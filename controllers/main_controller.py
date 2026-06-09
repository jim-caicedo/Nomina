"""
Controlador principal de la aplicación.
Maneja la lógica de negocio y coordina entre vistas y repositorios.
"""
from typing import List, Dict, Optional
from datetime import date
from models.empleado import Empleado
from models.empleado_repository import EmpleadoRepositorySQLite
from models.nomina_repository import NominaRepositorySQLite
from models.registro_nomina import RegistroNomina
from models.configuracion import ConfiguracionNomina
from services.nomina_calculator import LiquidadorNomina
from controllers.configuracion_controller import ConfiguracionController
from dataclasses import asdict

# Repositorios de conceptos
from models.conceptos.concepto_repository import ConceptoRepositorySQLite
from models.conceptos.concepto_empleado_repository import ConceptoEmpleadoRepositorySQLite
from models.conceptos.registro_conceptos_repository import RegistroConceptoRepositorySQLite
from models.conceptos.concepto_models import ConceptoNomina, ConceptoEmpleado, RegistroConceptoNomina


class MainController:
    """Controlador principal que coordina todas las operaciones."""
    
    def __init__(self):
        """Inicializa el controlador con repositorios SQLite."""
        # Repositorios con persistencia real en SQLite
        self.repo_empleados = EmpleadoRepositorySQLite()
        self.repo_nomina = NominaRepositorySQLite()
        
        # Controlador de configuración legal
        self.config_controller = ConfiguracionController()
        
        # Repositorios para conceptos
        self.repo_conceptos = ConceptoRepositorySQLite()
        self.repo_conceptos_emp = ConceptoEmpleadoRepositorySQLite()
        self.repo_registro_conceptos = RegistroConceptoRepositorySQLite()

    def obtener_empleados(self) -> List[Dict[str, object]]:
        """Obtiene lista de empleados como diccionarios."""
        return [empleado.to_dict() for empleado in self.repo_empleados.obtener_todos()]

    def buscar_empleado(self, empleado_id: int) -> Optional[Empleado]:
        """Busca un empleado por ID."""
        return self.repo_empleados.obtener_por_id(empleado_id)

    def generar_resumen_dashboard(self) -> Dict[str, object]:
        """Genera resumen para el dashboard con datos reales de SQLite."""
        empleados = self.repo_empleados.obtener_todos()
        
        if not empleados:
            return {
                "empleados_activos": 0,
                "gasto_total_mensual": 0.0,
                "salario_promedio": 0.0,
            }
        
        total_nomina = sum(e.salario for e in empleados)
        promedio_salario = round(total_nomina / len(empleados), 2)
        
        return {
            "empleados_activos": len(empleados),
            "gasto_total_mensual": round(total_nomina, 2),
            "salario_promedio": promedio_salario,
        }

    # ===== CRUD OPERATIONS =====

    def crear_empleado(
        self, 
        nombre: str, 
        apellido: str, 
        cargo: str, 
        salario: float, 
        correo: str = "", 
        telefono: str = "", 
        numero_cuenta: str = "",
        eps: str = "EPS por asignar",
        afp: str = "AFP por asignar",
        sede_laboral: str = "",
    ) -> Dict[str, object]:
        """Crea un nuevo empleado."""
        if not nombre or not apellido or not cargo or salario <= 0:
            return {"success": False, "error": "Datos inválidos. Verifica nombre, apellido, cargo y salario."}
        
        nuevo_empleado = Empleado(
            id=0, 
            nombre=nombre, 
            apellido=apellido, 
            cargo=cargo, 
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral=sede_laboral,
        )
        
        try:
            empleado_creado = self.repo_empleados.crear(nuevo_empleado)
            return {"success": True, "empleado": empleado_creado.to_dict()}
        except Exception as e:
            return {"success": False, "error": f"Error al crear empleado: {str(e)}"}

    def actualizar_empleado(
        self, 
        empleado_id: int, 
        nombre: str, 
        apellido: str, 
        cargo: str, 
        salario: float, 
        correo: str = "", 
        telefono: str = "", 
        numero_cuenta: str = "",
        eps: str = "EPS por asignar",
        afp: str = "AFP por asignar",
        sede_laboral: str = "",
    ) -> Dict[str, object]:
        """Actualiza un empleado existente."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}
        
        if not nombre or not apellido or not cargo or salario <= 0:
            return {"success": False, "error": "Datos inválidos. Verifica nombre, apellido, cargo y salario."}
        
        empleado = Empleado(
            id=empleado_id, 
            nombre=nombre, 
            apellido=apellido, 
            cargo=cargo, 
            salario=salario,
            correo=correo,
            telefono=telefono,
            numero_cuenta=numero_cuenta,
            eps=eps,
            afp=afp,
            sede_laboral=sede_laboral,
        )
        
        try:
            self.repo_empleados.actualizar(empleado)
            return {"success": True, "mensaje": f"Empleado {nombre} {apellido} actualizado exitosamente."}
        except Exception as e:
            return {"success": False, "error": f"Error al actualizar empleado: {str(e)}"}

    def eliminar_empleado(self, empleado_id: int) -> Dict[str, object]:
        """Elimina un empleado (soft delete)."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}
        
        try:
            self.repo_empleados.eliminar(empleado_id)
            return {"success": True, "mensaje": "Empleado eliminado exitosamente."}
        except Exception as e:
            return {"success": False, "error": f"Error al eliminar empleado: {str(e)}"}

    def listar_empleados(self) -> List[Dict[str, object]]:
        """Retorna lista de empleados."""
        return self.obtener_empleados()

    # ===== CONCEPTOS =====

    def obtener_conceptos_disponibles(self) -> List[Dict[str, object]]:
        """Retorna catálogo de conceptos activos."""
        conceptos = self.repo_conceptos.obtener_todos()
        return [asdict(c) for c in conceptos]

    def crear_concepto(
        self,
        nombre: str,
        tipo: str,
        naturaleza: str = "devengado",
        valor: Optional[float] = None,
        porcentaje: Optional[float] = None,
        base_calculo: Optional[str] = "salario",
    ) -> Dict[str, object]:
        """Crea una plantilla de concepto en el catálogo."""
        if not nombre or not tipo:
            return {"success": False, "error": "Nombre y tipo son requeridos."}

        concepto = ConceptoNomina(
            id=None,
            nombre=nombre,
            tipo=tipo,
            valor=valor,
            porcentaje=porcentaje,
            base_calculo=base_calculo,
            naturaleza=naturaleza,
            activo=True,
        )
        try:
            creado = self.repo_conceptos.crear(concepto)
            return {"success": True, "concepto": asdict(creado)}
        except Exception as e:
            return {"success": False, "error": f"Error al crear concepto: {e}"}

    def asignar_concepto_a_empleado(
        self,
        empleado_id: int,
        concepto_id: Optional[int] = None,
        nombre: Optional[str] = None,
        tipo: str = "fijo",
        naturaleza: str = "devengado",
        valor_personalizado: Optional[float] = None,
        porcentaje_personalizado: Optional[float] = None,
        base_calculo: Optional[str] = None,
    ) -> Dict[str, object]:
        """Asigna un concepto (plantilla o nuevo nombre) a un empleado."""
        if not self.repo_empleados.existe(empleado_id):
            return {"success": False, "error": "Empleado no encontrado."}

        plantilla = None
        if concepto_id:
            plantilla = self.repo_conceptos.obtener_por_id(concepto_id)
            if plantilla is None:
                return {"success": False, "error": "Concepto plantilla no encontrado."}

        # Si no se pasó nombre y hay plantilla, tomar nombre de plantilla
        nombre_final = nombre or (plantilla.nombre if plantilla else "")
        tipo_final = plantilla.tipo if plantilla and plantilla.tipo else tipo
        naturaleza_final = plantilla.naturaleza if plantilla and getattr(plantilla, 'naturaleza', None) else naturaleza
        valor_personalizado_final = valor_personalizado if valor_personalizado is not None else (plantilla.valor if plantilla else None)
        porcentaje_personalizado_final = porcentaje_personalizado if porcentaje_personalizado is not None else (plantilla.porcentaje if plantilla else None)
        base_calculo_final = base_calculo or (plantilla.base_calculo if plantilla else None)

        asign = ConceptoEmpleado(
            id=None,
            empleado_id=empleado_id,
            concepto_id=concepto_id,
            nombre=nombre_final,
            tipo=tipo_final,
            naturaleza=naturaleza_final,
            valor_personalizado=valor_personalizado_final,
            porcentaje_personalizado=porcentaje_personalizado_final,
            base_calculo=base_calculo_final,
            activo=True,
        )
        try:
            creado = self.repo_conceptos_emp.asignar(asign)
            return {"success": True, "asignacion": asdict(creado)}
        except Exception as e:
            return {"success": False, "error": f"Error al asignar concepto: {e}"}

    def obtener_conceptos_de_empleado(self, empleado_id: int) -> List[Dict[str, object]]:
        """Lista las asignaciones de conceptos de un empleado."""
        if not self.repo_empleados.existe(empleado_id):
            return []
        asignaciones = self.repo_conceptos_emp.obtener_por_empleado(empleado_id)
        return [asdict(a) for a in asignaciones]

    def obtener_historial_nominas(self) -> list:
        """
        Retorna todas las liquidaciones guardadas, agrupadas por período.
        Cada grupo contiene: periodo_inicio, periodo_cierre, cantidad_empleados,
        total_devengado, total_deducciones, total_neto, fecha_liquidacion.
        """
        try:
            todos = self.repo_nomina.obtener_todos()
            if not todos:
                return []

            # Agrupar por (periodo_inicio, periodo_cierre)
            grupos = {}
            for r in todos:
                clave = (r.periodo_inicio, r.periodo_cierre)
                if clave not in grupos:
                    grupos[clave] = {
                        "periodo_inicio": r.periodo_inicio.strftime("%d/%m/%Y"),
                        "periodo_cierre": r.periodo_cierre.strftime("%d/%m/%Y"),
                        "cantidad_empleados": 0,
                        "total_devengado": 0.0,
                        "total_deducciones": 0.0,
                        "total_neto": 0.0,
                        "fecha_liquidacion": r.fecha_liquidacion.strftime("%d/%m/%Y %H:%M") if r.fecha_liquidacion else "",
                    }
                grupos[clave]["cantidad_empleados"] += 1
                grupos[clave]["total_devengado"] += r.total_devengado
                grupos[clave]["total_deducciones"] += r.total_deducciones
                grupos[clave]["total_neto"] += r.salario_neto

            # Redondear totales y ordenar por fecha de cierre descendente
            resultado = []
            for clave, g in sorted(grupos.items(), key=lambda x: x[0][1], reverse=True):
                g["total_devengado"] = round(g["total_devengado"], 2)
                g["total_deducciones"] = round(g["total_deducciones"], 2)
                g["total_neto"] = round(g["total_neto"], 2)
                resultado.append(g)

            return resultado
        except Exception as e:
            print(f"Error al obtener historial de nóminas: {e}")
            return []

    def obtener_detalle_nomina_periodo(
        self, fecha_inicio_str: str, fecha_cierre_str: str
    ) -> list:
        """
        Retorna el detalle por empleado de una liquidación específica.
        Las fechas deben estar en formato DD/MM/YYYY.
        """
        from datetime import datetime
        try:
            fmt = "%d/%m/%Y"
            fecha_inicio = datetime.strptime(fecha_inicio_str, fmt).date()
            fecha_cierre = datetime.strptime(fecha_cierre_str, fmt).date()
            registros = self.repo_nomina.obtener_por_periodo(fecha_inicio, fecha_cierre)

            detalle = []
            for r in registros:
                empleado = self.repo_empleados.obtener_por_id(r.empleado_id)
                nombre = empleado.get_nombre_completo() if empleado else f"Empleado #{r.empleado_id}"
                cargo = empleado.cargo if empleado else ""
                detalle.append({
                    "empleado_id": r.empleado_id,
                    "nombre": nombre,
                    "cargo": cargo,
                    "dias_laborados": r.dias_laborados,
                    "salario_base_periodo": r.salario_base_periodo,
                    "auxilio_transporte": r.auxilio_transporte_periodo,
                    "total_devengado": r.total_devengado,
                    "descuento_afp": r.descuento_afp,
                    "descuento_eps": r.descuento_eps,
                    "total_deducciones": r.total_deducciones,
                    "salario_neto": r.salario_neto,
                })
            return detalle
        except Exception as e:
            print(f"Error al obtener detalle de nómina: {e}")
            return []

    # ===== LIQUIDACIÓN DE NÓMINA =====

    def liquidar_nomina_periodo(
        self,
        fecha_inicio: date,
        fecha_cierre: date,
        dias_laborados: int,
        horas_extras: int = 0,
    ) -> Dict[str, object]:
        """
        Liquida nómina para todos los empleados activos en un período.
        Guarda los registros en SQLite para persistencia.
        """
        try:
            # Validar período
            if not LiquidadorNomina.validar_periodo(fecha_inicio, fecha_cierre):
                return {
                    "success": False,
                    "error": "La fecha de inicio debe ser anterior a la fecha de cierre.",
                }

            # Obtener todos los empleados
            empleados = self.repo_empleados.obtener_todos()
            if not empleados:
                return {"success": False, "error": "No hay empleados registrados."}

            # Obtener configuración actual
            config_actual = self.config_controller.obtener_configuracion_obj()

            # Calcular nómina para cada empleado
            registros_liquidados = []
            total_devengado = 0.0
            total_deducciones = 0.0
            total_neto = 0.0

            for empleado in empleados:
                try:
                    # Calcular nómina usando el servicio con configuración actual
                    calculos = LiquidadorNomina.liquidar(
                        empleado=empleado,
                        fecha_inicio=fecha_inicio,
                        fecha_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        horas_extras=horas_extras,
                        config=config_actual,
                    )
                    calculos_dict = calculos.to_dict()

                    # Crear registro de nómina
                    registro = RegistroNomina(
                        id=0,  # Se asigna en el repositorio
                        empleado_id=empleado.id,
                        periodo_inicio=fecha_inicio,
                        periodo_cierre=fecha_cierre,
                        dias_laborados=dias_laborados,
                        salario_base_periodo=calculos_dict["salario_base_periodo"],
                        auxilio_transporte_periodo=calculos_dict["auxilio_transporte"],
                        horas_extras=horas_extras,
                        valor_horas_extras=calculos_dict["horas_extras"],
                        total_devengado=calculos_dict["total_devengado"],
                        descuento_afp=calculos_dict["descuento_afp"],
                        descuento_eps=calculos_dict["descuento_eps"],
                        otros_descuentos=calculos_dict["otros_descuentos"],
                        total_deducciones=calculos_dict["total_deducciones"],
                        salario_neto=calculos_dict["salario_neto"],
                    )

                    # Guardar registro en SQLite
                    registro_guardado = self.repo_nomina.guardar_registro(registro)
                    registros_liquidados.append(registro_guardado)

                    # Guardar desglose de conceptos aplicados (si los hay)
                    conceptos_aplicados = calculos_dict.get("conceptos_aplicados", [])
                    for c in conceptos_aplicados:
                        try:
                            reg_c = RegistroConceptoNomina(
                                id=0,
                                registro_nomina_id=registro_guardado.id,
                                concepto_nombre=c.get("nombre", ""),
                                tipo=c.get("tipo", ""),
                                naturaleza=c.get("naturaleza", "devengado"),
                                valor_calculado=c.get("valor", 0.0),
                                metadata=None,
                            )
                            self.repo_registro_conceptos.crear(reg_c)
                        except Exception as e:
                            print(f"Error guardando registro de concepto: {e}")
                    # Acumular totales
                    total_devengado += calculos_dict["total_devengado"]
                    total_deducciones += calculos_dict["total_deducciones"]
                    total_neto += calculos_dict["salario_neto"]

                except ValueError as e:
                    return {
                        "success": False,
                        "error": f"Error al calcular nómina de {empleado.get_nombre_completo()}: {str(e)}",
                    }

            # Retornar resultado exitoso
            return {
                "success": True,
                "registros": [r.to_dict() for r in registros_liquidados],
                "cantidad_empleados": len(registros_liquidados),
                "total_devengado": round(total_devengado, 2),
                "total_deducciones": round(total_deducciones, 2),
                "total_neto": round(total_neto, 2),
            }

        except Exception as e:
            return {"success": False, "error": f"Error general: {str(e)}"}