"""
Vista para consultar nóminas ya liquidadas y guardadas en SQLite.
Muestra períodos agregados y detalle por empleado sin recalcular.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from controllers.main_controller import MainController
from config.constants import COLORES
from utils.excel_exporter import exportar_nomina_a_excel


class HistorialNominaView:
    def __init__(self, content_frame, controller: MainController):
        self.content_frame = content_frame
        self.controller = controller
        self.frame = None
        self.scroll_periodos = None
        self.scroll_detalle = None
        self.label_periodo_sel = None
        self.periodo_seleccionado = None  # dict con periodo_inicio y periodo_cierre

    def crear_frame(self) -> ctk.CTkFrame:
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self.frame, text="Historial de Nóminas", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Sección 1: Periodos liquidados
        periodos_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=12)
        periodos_frame.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="nsew")
        periodos_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(periodos_frame, text="Períodos Liquidados", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=12)

        btn_frame = ctk.CTkFrame(periodos_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="e", padx=12)
        # Exportar será por período, habilitado cuando se seleccione una fila
        self.btn_export_periodo = ctk.CTkButton(btn_frame, text="📥 Exportar Excel", command=self._exportar_periodo, fg_color=COLORES.get("primary", "#0ea5a4"))
        self.btn_export_periodo.grid(row=0, column=0)
        self.btn_export_periodo.configure(state="disabled")

        self.scroll_periodos = ctk.CTkScrollableFrame(periodos_frame, corner_radius=8, fg_color="#111827")
        self.scroll_periodos.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.scroll_periodos.grid_columnconfigure(0, weight=1)

        # Sección 2: Detalle del periodo seleccionado
        detalle_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=12)
        detalle_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        detalle_frame.grid_columnconfigure(0, weight=1)
        detalle_frame.grid_rowconfigure(1, weight=1)

        self.label_periodo_sel = ctk.CTkLabel(detalle_frame, text="Periodo seleccionado: Ninguno", font=ctk.CTkFont(size=14, weight="bold"))
        self.label_periodo_sel.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        btn_det_frame = ctk.CTkFrame(detalle_frame, fg_color="transparent")
        btn_det_frame.grid(row=0, column=0, sticky="e", padx=12)
        self.btn_export_detalle = ctk.CTkButton(btn_det_frame, text="📥 Exportar detalle", command=self._exportar_periodo, fg_color=COLORES.get("primary", "#0ea5a4"))
        self.btn_export_detalle.grid(row=0, column=0)
        self.btn_export_detalle.configure(state="disabled")

        self.scroll_detalle = ctk.CTkScrollableFrame(detalle_frame, corner_radius=8, fg_color="#111827")
        self.scroll_detalle.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.scroll_detalle.grid_columnconfigure(0, weight=1)

        # Inicializar
        self._cargar_periodos()

        return self.frame

    def _cargar_periodos(self):
        for w in self.scroll_periodos.winfo_children():
            w.destroy()

        periodos = self.controller.obtener_historial_nominas()
        if not periodos:
            ctk.CTkLabel(self.scroll_periodos, text="No hay liquidaciones registradas", text_color="#9ca3af").grid(pady=12)
            return

        # Encabezado de columnas
        headers = [
            "Período inicio",
            "Período cierre",
            "Empleados",
            "Total devengado",
            "Total deducciones",
            "Nómina neta",
            "Fecha liquidación",
        ]
        header_frame = ctk.CTkFrame(self.scroll_periodos, fg_color="#111827", corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)
        for col_idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
            lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

        # Filas
        for idx, p in enumerate(periodos, start=1):
            row_frame = ctk.CTkFrame(self.scroll_periodos, fg_color="#1f2937", corner_radius=8)
            row_frame.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            row_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

            datos = [
                p.get("periodo_inicio", ""),
                p.get("periodo_cierre", ""),
                str(p.get("cantidad_empleados", 0)),
                f"${p.get('total_devengado', 0.0):,.2f}",
                f"${p.get('total_deducciones', 0.0):,.2f}",
                f"${p.get('total_neto', 0.0):,.2f}",
                p.get("fecha_liquidacion", ""),
            ]

            for col_idx, val in enumerate(datos):
                lbl = ctk.CTkLabel(row_frame, text=val, font=ctk.CTkFont(size=10), anchor="w")
                lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

            # Hacer la fila clicable
            row_frame.bind("<Button-1>", lambda e, per=p: self._seleccionar_periodo(per))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, per=p: self._seleccionar_periodo(per))

    def _seleccionar_periodo(self, periodo: dict):
        self.periodo_seleccionado = periodo
        inicio = periodo.get("periodo_inicio", "")
        cierre = periodo.get("periodo_cierre", "")
        self.label_periodo_sel.configure(text=f"Periodo seleccionado: {inicio} - {cierre}")
        # Habilitar botones de exportar
        self.btn_export_periodo.configure(state="normal")
        self.btn_export_detalle.configure(state="normal")
        self._cargar_detalle()

    def _cargar_detalle(self):
        for w in self.scroll_detalle.winfo_children():
            w.destroy()

        if not self.periodo_seleccionado:
            ctk.CTkLabel(self.scroll_detalle, text="Selecciona un período arriba", text_color="#9ca3af").grid(pady=12)
            return

        inicio = self.periodo_seleccionado.get("periodo_inicio")
        cierre = self.periodo_seleccionado.get("periodo_cierre")
        detalle = self.controller.obtener_detalle_nomina_periodo(inicio, cierre)

        if not detalle:
            ctk.CTkLabel(self.scroll_detalle, text="No hay detalle para este período", text_color="#9ca3af").grid(pady=12)
            return

        headers = ["Nº", "Nombre", "Cargo", "Días", "Salario base", "Aux transp", "Total dev", "AFP", "EPS", "Total ded", "Neto"]
        header_frame = ctk.CTkFrame(self.scroll_detalle, fg_color="#111827", corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        header_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)
        for col_idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(header_frame, text=h, font=ctk.CTkFont(size=11, weight="bold"), anchor="w")
            lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

        for idx, row in enumerate(detalle, start=1):
            row_frame = ctk.CTkFrame(self.scroll_detalle, fg_color="#1f2937", corner_radius=12)
            row_frame.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            row_frame.grid_columnconfigure(tuple(range(len(headers))), weight=1)

            datos = [
                str(idx),
                row.get("nombre", ""),
                row.get("cargo", ""),
                str(row.get("dias_laborados", 0)),
                f"${row.get('salario_base_periodo', 0.0):,.2f}",
                f"${row.get('auxilio_transporte', 0.0):,.2f}",
                f"${row.get('total_devengado', 0.0):,.2f}",
                f"${row.get('descuento_afp', 0.0):,.2f}",
                f"${row.get('descuento_eps', 0.0):,.2f}",
                f"${row.get('total_deducciones', 0.0):,.2f}",
                f"${row.get('salario_neto', 0.0):,.2f}",
            ]

            for col_idx, val in enumerate(datos):
                lbl = ctk.CTkLabel(row_frame, text=val, font=ctk.CTkFont(size=10), anchor="w")
                lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")

    def _exportar_periodo(self):
        """Exporta el período seleccionado a Excel usando los registros reales de la BD."""
        if not self.periodo_seleccionado:
            messagebox.showerror("Error", "Selecciona un período primero")
            return

        try:
            fmt = "%d/%m/%Y"
            inicio = datetime.strptime(self.periodo_seleccionado.get("periodo_inicio"), fmt).date()
            cierre = datetime.strptime(self.periodo_seleccionado.get("periodo_cierre"), fmt).date()

            registros = self.controller.repo_nomina.obtener_por_periodo(inicio, cierre)
            if not registros:
                messagebox.showwarning("Sin datos", "No hay registros para este período")
                return

            ruta_archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Archivos Excel", "*.xlsx")],
                initialfile=f"nomina_{inicio.strftime('%Y%m%d')}_{cierre.strftime('%Y%m%d')}.xlsx",
            )
            if not ruta_archivo:
                return

            exportar_nomina_a_excel(registros, inicio, cierre, ruta_archivo)
            messagebox.showinfo("Éxito", f"Archivo exportado:\n{ruta_archivo}")
        except ImportError:
            messagebox.showerror("Error", "openpyxl no está instalado. Ejecuta: pip install openpyxl")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
