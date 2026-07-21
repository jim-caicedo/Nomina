"""
Vista de Liquidación Final de Contrato en CustomTkinter.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date

class LiquidacionView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.empleados_map = {}  # { "Nombre (Cedula)": dict_emp }
        self.calculo_actual = None

        self._crear_ui()
        self._cargar_empleados()

    def _crear_ui(self):
        # Título
        lbl_titulo = ctk.CTkLabel(self, text="Liquidación Final de Contrato", font=("Arial", 20, "bold"))
        lbl_titulo.pack(pady=10, padx=10, anchor="w")

        # Contenedor Principal (2 Columnas)
        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        # --- COLUMNA IZQUIERDA: FORMULARIO Y PARÁMETROS ---
        form_frame = ctk.CTkFrame(grid_frame)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Parámetros de Liquidación", font=("Arial", 14, "bold")).pack(pady=5)

        # Selector Empleado
        ctk.CTkLabel(form_frame, text="Seleccionar Empleado:").pack(anchor="w", padx=10)
        self.combo_empleados = ctk.CTkOptionMenu(form_frame, values=[], command=self._on_empleado_selected)
        self.combo_empleados.pack(fill="x", padx=10, pady=5)

        # Fecha Ingreso (Auto-completada / Readonly)
        ctk.CTkLabel(form_frame, text="Fecha de Ingreso:").pack(anchor="w", padx=10)
        self.entry_ingreso = ctk.CTkEntry(form_frame, placeholder_text="YYYY-MM-DD")
        self.entry_ingreso.pack(fill="x", padx=10, pady=5)

        # Fecha Retiro
        ctk.CTkLabel(form_frame, text="Fecha de Retiro (YYYY-MM-DD):").pack(anchor="w", padx=10)
        self.entry_retiro = ctk.CTkEntry(form_frame)
        self.entry_retiro.insert(0, str(date.today()))
        self.entry_retiro.pack(fill="x", padx=10, pady=5)

        # Motivo Retiro
        ctk.CTkLabel(form_frame, text="Motivo de Retiro:").pack(anchor="w", padx=10)
        self.combo_motivo = ctk.CTkOptionMenu(form_frame, values=[
            "RENUNCIA", 
            "DESPIDO_SIN_JUSTA_CAUSA", 
            "DESPIDO_CON_JUSTA_CAUSA", 
            "FIN_CONTRATO"
        ])
        self.combo_motivo.pack(fill="x", padx=10, pady=5)

        # Vacaciones Tomadas
        ctk.CTkLabel(form_frame, text="Días de Vacaciones Tomadas:").pack(anchor="w", padx=10)
        self.entry_vac_tomadas = ctk.CTkEntry(form_frame)
        self.entry_vac_tomadas.insert(0, "0.0")
        self.entry_vac_tomadas.pack(fill="x", padx=10, pady=5)

        # Deducciones Varias
        ctk.CTkLabel(form_frame, text="Otras Deducciones ($):").pack(anchor="w", padx=10)
        self.entry_deducciones = ctk.CTkEntry(form_frame)
        self.entry_deducciones.insert(0, "0.0")
        self.entry_deducciones.pack(fill="x", padx=10, pady=5)

        # Botón Calcular
        btn_calcular = ctk.CTkButton(form_frame, text="🔍 Simular / Calcular", fg_color="green", command=self._calcular)
        btn_calcular.pack(fill="x", padx=10, pady=15)

        # --- COLUMNA DERECHA: RESUMEN DE CÁLCULO ---
        self.resumen_frame = ctk.CTkFrame(grid_frame)
        self.resumen_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        ctk.CTkLabel(self.resumen_frame, text="Resumen de Previsualización", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.txt_resumen = ctk.CTkTextbox(self.resumen_frame, width=300, height=320)
        self.txt_resumen.pack(fill="both", expand=True, padx=10, pady=5)

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(
            self.resumen_frame, 
            text="💾 Procesar y Guardar Liquidación", 
            state="disabled", 
            command=self._guardar
        )
        self.btn_guardar.pack(fill="x", padx=10, pady=10)

    def _cargar_empleados(self):
        empleados = self.controller.obtener_empleados_activos()
        if not empleados:
            self.combo_empleados.configure(values=["Sin empleados activos"])
            return

        self.empleados_map = {f"{e['nombre_completo']} ({e['cedula']})": e for e in empleados}
        opciones = list(self.empleados_map.keys())
        self.combo_empleados.configure(values=opciones)
        self.combo_empleados.set(opciones[0])
        self._on_empleado_selected(opciones[0])

    def _on_empleado_selected(self, seleccion):
        emp = self.empleados_map.get(seleccion)
        if emp:
            self.entry_ingreso.delete(0, "end")
            self.entry_ingreso.insert(0, emp.get("fecha_ingreso", ""))

    def _calcular(self):
        emp_info = self.empleados_map.get(self.combo_empleados.get())
        if not emp_info:
            messagebox.showerror("Error", "Seleccione un empleado válido.")
            return

        try:
            vac_tomadas = float(self.entry_vac_tomadas.get() or 0)
            deducciones = float(self.entry_deducciones.get() or 0)
            
            res = self.controller.calcular_previsualizacion(
                empleado_id=emp_info["id"],
                fecha_retiro_str=self.entry_retiro.get().strip(),
                motivo_retiro=self.combo_motivo.get(),
                dias_vacaciones_tomadas=vac_tomadas,
                deducciones_varias=deducciones
            )
            
            self.calculo_actual = res
            self._renderizar_resumen(res)
            self.btn_guardar.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error de Cálculo", str(e))

    def _renderizar_resumen(self, r: dict):
        self.txt_resumen.delete("1.0", "end")
        texto = f"""
========================================
  LIQUIDACIÓN DEFINITIVA
========================================
Empleado: {r['empleado_nombre']}
Días Trabajados Totales: {r['dias_totales']}
Base Prestaciones: ${r['base_prestaciones']:,.2f}
----------------------------------------
DEVENGADOS PRESTACIONALES:
 - Cesantías ({r['dias_cesantias']} días): ${r['valor_cesantias']:,.2f}
 - Int. Cesantías: ${r['valor_intereses']:,.2f}
 - Prima de Servicios ({r['dias_prima']} días): ${r['valor_prima']:,.2f}
 - Vacaciones ({r['dias_vacaciones']:.1f} días): ${r['valor_vacaciones']:,.2f}
 - Indemnización: ${r['valor_indemnizacion']:,.2f}

TOTAL DEVENGADO: ${r['total_devengado']:,.2f}
DEDUCCIONES: ${r['total_deducciones']:,.2f}
----------------------------------------
NETO A PAGAR: ${r['neto_a_pagar']:,.2f}
========================================
        """
        self.txt_resumen.insert("1.0", texto)

    def _guardar(self):
        if not self.calculo_actual:
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro de liquidar y desactivar a este empleado?"):
            exito = self.controller.procesar_y_guardar(self.calculo_actual)
            if exito:
                messagebox.showinfo("Éxito", "Liquidación guardada correctamente.")
                self.btn_guardar.configure(state="disabled")
                self._cargar_empleados()  # Recargar lista de activos
            else:
                messagebox.showerror("Error", "No se pudo guardar la liquidación.")