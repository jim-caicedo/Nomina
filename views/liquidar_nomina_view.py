"""
Vista de liquidación de nómina quincenal.
Solo maneja interacción con el usuario - sin lógica de negocio.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
from controllers.nomina_controller import NominaController
from utils.ui_theme import COLORES, FORMATO_FECHA
from utils.excel_exporter import exportar_nomina_a_excel

try:
    from tkcalendar import DateEntry
    TKCALENDAR_DISPONIBLE = True
except ImportError:
    TKCALENDAR_DISPONIBLE = False
    print("⚠️ tkcalendar no está instalado. Ejecuta: pip install tkcalendar babel")


class SelectorCalendario(ctk.CTkFrame):
    """Selector de fecha con calendario desplegable visual."""
    
    def __init__(self, parent, label_text: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.label.pack(anchor="w", padx=0, pady=(0, 4))
        
        if TKCALENDAR_DISPONIBLE:
            self.date_entry = DateEntry(
                self,
                width=12,
                background='#1f2937',
                foreground='white',
                borderwidth=2,
                bordercolor='#374151',
                selectbackground='#3b82f6',
                selectforeground='white',
                othermonthforeground='#6b7280',
                othermonthweforeground='#4b5563',
                weekendbackground='#111827',
                weekendforeground='#9ca3af',
                headersbackground='#1f2937',
                headersforeground='#60a5fa',
                normalbackground='#1f2937',
                normalforeground='white',
                font=('Segoe UI', 11),
                date_pattern='dd/mm/yyyy',
                locale='es_CO',
                mindate=date(2024, 1, 1),
                maxdate=date(2030, 12, 31)
            )
            self.date_entry.pack(fill="x", padx=0, pady=0)
        else:
            self.fallback_entry = ctk.CTkEntry(
                self,
                placeholder_text="DD/MM/YYYY",
                height=36,
                font=ctk.CTkFont(size=12)
            )
            self.fallback_entry.pack(fill="x")
    
    def get_fecha(self) -> date:
        """Retorna la fecha seleccionada."""
        if TKCALENDAR_DISPONIBLE:
            return self.date_entry.get_date()
        else:
            fecha_str = self.fallback_entry.get().strip()
            if fecha_str:
                return datetime.strptime(fecha_str, FORMATO_FECHA).date()
            return date.today()
    
    def set_fecha(self, fecha: date):
        """Establece la fecha del selector."""
        if TKCALENDAR_DISPONIBLE:
            self.date_entry.set_date(fecha)
        else:
            self.fallback_entry.delete(0, 'end')
            self.fallback_entry.insert(0, fecha.strftime(FORMATO_FECHA))


class LiquidarNominaView:
    """Vista para la liquidación de nómina - Solo UI, sin lógica de negocio."""

    def __init__(
        self,
        content_frame: ctk.CTkFrame,
        controller: NominaController,
        empleado_controller=None,
    ):
        self.content_frame = content_frame
        self.controller = controller
        self.empleado_controller = empleado_controller
        self.frame = None

        # Selectores de calendario
        self.selector_fecha_inicio = None
        self.selector_fecha_cierre = None

        # Frame de resultados
        self.scroll_resultados = None
        self.label_totales = None
        self.label_omitidos = None
        self._omitidos_global = []
        
        # Último resultado calculado
        self.ultimo_resultado = None

    def crear_frame(self) -> ctk.CTkFrame:
        """Crea el frame principal de liquidación de nómina."""
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # ========== ENCABEZADO ==========
        header = ctk.CTkLabel(
            self.frame,
            text="Liquidación de Nómina Quincenal",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ========== FORMULARIO ==========
        form_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Fila 1: Selectores de calendario
        self.selector_fecha_inicio = SelectorCalendario(
            form_frame,
            label_text="📅 Fecha Inicio (Día 1 o 16):"
        )
        self.selector_fecha_inicio.grid(row=0, column=0, padx=12, pady=(16, 12), sticky="ew")
        
        self.selector_fecha_cierre = SelectorCalendario(
            form_frame,
            label_text="📅 Fecha Cierre (Día 15 o último día):"
        )
        self.selector_fecha_cierre.grid(row=0, column=1, padx=12, pady=(16, 12), sticky="ew")
        
        # Label informativo
        info_label = ctk.CTkLabel(
            form_frame,
            text="💡 Primera quincena: del 1 al 15 | Segunda quincena: del 16 al último día del mes",
            font=ctk.CTkFont(size=11),
            text_color="#60a5fa"
        )
        info_label.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="w")
        
        # Botones de acción
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.grid(row=4, column=0, columnspan=2, padx=12, pady=(0, 16), sticky="ew")
        botones_frame.grid_columnconfigure((0, 1), weight=1)

        btn_calcular = ctk.CTkButton(
            botones_frame,
            text="📊 Calcular Nómina",
            command=self._calcular_nomina,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["success"],
        )
        btn_calcular.grid(row=0, column=0, padx=6, sticky="ew")

        btn_exportar = ctk.CTkButton(
            botones_frame,
            text="📥 Exportar a Excel",
            command=self._exportar_excel,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["primary"],
        )
        btn_exportar.grid(row=0, column=1, padx=6, sticky="ew")

        # ========== RESULTADOS ==========
        resultados_header = ctk.CTkLabel(
            self.frame, text="Resultados de Liquidación", font=ctk.CTkFont(size=16, weight="bold")
        )
        resultados_header.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 12))

        # Tabla de resultados
        tabla_container = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        tabla_container.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        tabla_container.grid_columnconfigure(0, weight=1)
        tabla_container.grid_rowconfigure(0, weight=1)

        # Scroll con resultados
        self.scroll_resultados = ctk.CTkScrollableFrame(
            tabla_container, corner_radius=12, fg_color="#111827"
        )
        self.scroll_resultados.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_resultados.grid_columnconfigure(0, weight=1)

        # Label vacío para mostrar mensaje inicial
        label_empty = ctk.CTkLabel(
            self.scroll_resultados,
            text="Selecciona las fechas en el calendario y haz clic en 'Calcular Nómina'",
            font=ctk.CTkFont(size=14),
            text_color="#9ca3af",
        )
        label_empty.grid(row=0, column=0, pady=30)

        # Label de totales
        self.label_totales = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#10b981",
            wraplength=800,
        )
        self.label_totales.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

        self.label_omitidos = None

        return self.frame

    def _calcular_nomina(self):
        """Solo captura datos de UI y llama al controlador.

        Los días laborados y las horas extras ya no se capturan manualmente:
        el controlador los deriva a partir del período (fecha_inicio, fecha_cierre).
        """
        # Capturar datos de UI
        fecha_inicio = self.selector_fecha_inicio.get_fecha()
        fecha_cierre = self.selector_fecha_cierre.get_fecha()

        if fecha_inicio >= fecha_cierre:
            messagebox.showerror(
                "Error", "La fecha de inicio debe ser anterior a la fecha de cierre."
            )
            return

        # Llamar al controlador - TODO el procesamiento está ahí
        resultado = self.controller.liquidar_nomina_periodo(fecha_inicio, fecha_cierre)


        # Mostrar resultado según respuesta del controlador
        if not resultado["success"]:
            messagebox.showerror("Error", resultado["error"])
            return

        # Mostrar resultados
        self._mostrar_resultados(resultado)
        self.ultimo_resultado = resultado

    def _mostrar_resultados(self, resultado: dict):
        """Muestra los resultados de la liquidación en la UI."""
        # Limpiar scroll
        for widget in self.scroll_resultados.winfo_children():
            widget.destroy()

        registros = resultado["registros"]

        if not registros:
            label = ctk.CTkLabel(
                self.scroll_resultados,
                text="No hay registros para mostrar",
                font=ctk.CTkFont(size=14),
                text_color="#9ca3af",
            )
            label.grid(row=0, column=0, pady=30)
            return

        # Encabezados de tabla
        headers = [
            "Nº",
            "Nombre",
            "Cargo",
            "Ordinario",
            "Aux Transp",
            "Total Dev",
            "AFP",
            "EPS",
            "Total Ded",
            "Salario Neto",
        ]

        header_frame = ctk.CTkFrame(self.scroll_resultados, fg_color="#111827", corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w",
            )
            lbl.grid(row=0, column=col_idx, padx=8, pady=10, sticky="w")

        # Filas de datos
        for row_idx, registro in enumerate(registros, start=1):
            row_frame = ctk.CTkFrame(self.scroll_resultados, fg_color="#1f2937", corner_radius=12)
            row_frame.grid(row=row_idx, column=0, sticky="ew", padx=8, pady=4)
            row_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

            # Obtener datos del empleado
            empleado = (
                self.empleado_controller.buscar_empleado(registro["empleado_id"])
                if self.empleado_controller
                else None
            )
            nombre_completo = f"{empleado.nombre} {empleado.apellido}" if empleado else "N/A"

            datos = [
                str(row_idx),
                nombre_completo,
                empleado.cargo if empleado else "N/A",
                f"${registro['salario_base_periodo']:,.2f}",
                f"${registro['auxilio_transporte_periodo']:,.2f}",
                f"${registro['total_devengado']:,.2f}",
                f"${registro['descuento_afp']:,.2f}",
                f"${registro['descuento_eps']:,.2f}",
                f"${registro['total_deducciones']:,.2f}",
                f"${registro['salario_neto']:,.2f}",
            ]

            for col_idx, dato in enumerate(datos):
                lbl = ctk.CTkLabel(
                    row_frame, text=dato, font=ctk.CTkFont(size=10), anchor="w"
                )
                lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

        # Mostrar totales
        totales_text = (
            f"📊 TOTALES: {resultado['cantidad_empleados']} empleados | "
            f"Total Devengado: ${resultado['total_devengado']:,.2f} | "
            f"Total Deducciones: ${resultado['total_deducciones']:,.2f} | "
            f"Nómina Neta: ${resultado['total_neto']:,.2f}"
        )
        self.label_totales.configure(text=totales_text)

        # Mostrar aviso de conceptos omitidos si existen
        omitidos = []
        for registro in registros:
            conceptos_omitidos = registro.get("conceptos_omitidos") or []
            for omitido in conceptos_omitidos:
                omitidos.append({
                    "empleado_id": registro.get("empleado_id"),
                    "nombre": omitido.get("nombre", "N/A"),
                    "razon": omitido.get("razon", "Motivo desconocido"),
                })

        if self.label_omitidos:
            self.label_omitidos.destroy()
            self.label_omitidos = None

        if omitidos:
            self._omitidos_global = omitidos
            label_text = (
                f"⚠️ {len(omitidos)} concepto(s) no se aplicaron. "
                "Revisa la configuración de conceptos."
            )
            self.label_omitidos = ctk.CTkLabel(
                self.frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORES.get("warning", "#f59e0b"),
                wraplength=800,
            )
            self.label_omitidos.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))
            self.label_omitidos.bind("<Button-1>", self._mostrar_omitidos_modal)
        else:
            self._omitidos_global = []

    def _exportar_excel(self):
        """Solo solicita ruta y llama al controlador para exportar."""
        if not self.ultimo_resultado:
            messagebox.showwarning(
                "Sin datos",
                "No hay resultados de cálculo. Calcula la nómina primero.",
            )
            return

        # Obtener fechas de los selectores
        fecha_inicio = self.selector_fecha_inicio.get_fecha()
        fecha_cierre = self.selector_fecha_cierre.get_fecha()

        # Solicitar ubicación para guardar
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")],
            initialfile=f"nomina_{fecha_inicio.strftime('%Y%m%d')}_"
            f"{fecha_cierre.strftime('%Y%m%d')}.xlsx",
        )

        if not ruta_archivo:
            return  # Usuario canceló

        # Llamar al controlador para exportar
        resultado = self.controller.exportar_nomina_excel(
            fecha_inicio, fecha_cierre, ruta_archivo
        )

        if resultado["success"]:
            messagebox.showinfo(
                "Éxito",
                f"Archivo exportado exitosamente:\n{ruta_archivo}",
            )
        else:
            messagebox.showerror("Error", resultado["error"])

    def _mostrar_omitidos_modal(self, event=None):
        """Muestra una ventana modal con la lista de conceptos omitidos."""
        if not getattr(self, "_omitidos_global", None):
            return

        modal = ctk.CTkToplevel(self.frame)
        modal.title("Conceptos omitidos")
        modal.geometry("400x300")
        modal.grab_set()

        header = ctk.CTkLabel(
            modal,
            text=f"Conceptos omitidos ({len(self._omitidos_global)})",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        header.pack(padx=16, pady=(16, 8), anchor="w")

        contenido = ctk.CTkScrollableFrame(modal, corner_radius=12, fg_color="#111827")
        contenido.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for omitido in self._omitidos_global:
            item_frame = ctk.CTkFrame(contenido, fg_color="#1f2937", corner_radius=10)
            item_frame.pack(fill="x", padx=8, pady=6)
            item_frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                item_frame,
                text=f"Empleado ID: {omitido.get('empleado_id', 'N/A')}",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))
            ctk.CTkLabel(
                item_frame,
                text=f"Concepto: {omitido.get('nombre', 'N/A')}",
                font=ctk.CTkFont(size=11),
                anchor="w",
            ).grid(row=1, column=0, sticky="w", padx=10, pady=2)
            ctk.CTkLabel(
                item_frame,
                text=f"Razón: {omitido.get('razon', 'Sin motivo especificado')}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=COLORES.get("warning", "#f59e0b"),
            ).grid(row=2, column=0, sticky="w", padx=10, pady=(2, 8))