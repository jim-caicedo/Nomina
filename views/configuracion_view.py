"""
Vista de configuración legal de nómina.
Permite al usuario configurar y guardar parámetros legales vigentes.
"""

import customtkinter as ctk
from tkinter import messagebox
from controllers.configuracion_controller import ConfiguracionController
from utils.ui_theme import COLORES


class ConfiguracionView:
    """Vista para la configuración legal de nómina."""

    def __init__(self, content_frame: ctk.CTkFrame, controller: ConfiguracionController):
        self.content_frame = content_frame
        self.controller = controller
        self.frame = None

        # Variables de entrada
        self.var_anio = None
        self.var_salario_minimo = None
        self.var_auxilio_transporte = None
        self.var_porcentaje_afp = None
        self.var_porcentaje_eps = None

    def crear_frame(self) -> ctk.CTkFrame:
        """Crea el frame principal de configuración legal."""
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # ========== ENCABEZADO ==========
        header = ctk.CTkLabel(
            self.frame,
            text="⚙️ Configuración Legal de Nómina",
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # ========== FORMULARIO ==========
        form_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="new")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        # Fila 1: Año Vigente
        ctk.CTkLabel(
            form_frame, text="Año Vigente:", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
        self.var_anio = ctk.StringVar(value="")
        entry_anio = ctk.CTkEntry(form_frame, textvariable=self.var_anio, height=36)
        entry_anio.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        # Fila 2: Salario Mínimo Mensual
        ctk.CTkLabel(
            form_frame, text="Salario Mínimo Mensual ($):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=2, column=0, padx=16, pady=(8, 4), sticky="w")
        self.var_salario_minimo = ctk.StringVar(value="")
        entry_salario = ctk.CTkEntry(form_frame, textvariable=self.var_salario_minimo, height=36)
        entry_salario.grid(row=3, column=0, padx=16, pady=(0, 12), sticky="ew")

        # Fila 3: Auxilio de Transporte Mensual
        ctk.CTkLabel(
            form_frame, text="Auxilio Transporte Mensual ($):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=4, column=0, padx=16, pady=(8, 4), sticky="w")
        self.var_auxilio_transporte = ctk.StringVar(value="")
        entry_auxilio = ctk.CTkEntry(form_frame, textvariable=self.var_auxilio_transporte, height=36)
        entry_auxilio.grid(row=5, column=0, padx=16, pady=(0, 12), sticky="ew")

        # Fila 4: Porcentaje AFP
        ctk.CTkLabel(
            form_frame, text="% AFP (Pensión):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=16, pady=(16, 4), sticky="w")
        self.var_porcentaje_afp = ctk.StringVar(value="")
        entry_afp = ctk.CTkEntry(form_frame, textvariable=self.var_porcentaje_afp, height=36)
        entry_afp.grid(row=1, column=1, padx=16, pady=(0, 12), sticky="ew")

        # Fila 5: Porcentaje EPS
        ctk.CTkLabel(
            form_frame, text="% EPS (Salud):", font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=2, column=1, padx=16, pady=(8, 4), sticky="w")
        self.var_porcentaje_eps = ctk.StringVar(value="")
        entry_eps = ctk.CTkEntry(form_frame, textvariable=self.var_porcentaje_eps, height=36)
        entry_eps.grid(row=3, column=1, padx=16, pady=(0, 12), sticky="ew")

        # Label informativo
        label_info = ctk.CTkLabel(
            form_frame,
            text="⚠️ Estos valores se aplicarán a todas las liquidaciones desde que se guarden.",
            font=ctk.CTkFont(size=11),
            text_color="#f59e0b",
            wraplength=400,
        )
        label_info.grid(row=4, column=1, padx=16, pady=(8, 12), sticky="w")

        # Botones de acción
        botones_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        botones_frame.grid(row=6, column=0, columnspan=2, padx=16, pady=(0, 16), sticky="ew")
        botones_frame.grid_columnconfigure((0, 1, 2), weight=1)

        btn_guardar = ctk.CTkButton(
            botones_frame,
            text="💾 Guardar Configuración",
            command=self._guardar_configuracion,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["success"],
        )
        btn_guardar.grid(row=0, column=0, padx=6, sticky="ew")

        btn_restaurar = ctk.CTkButton(
            botones_frame,
            text="🔄 Restaurar Valores 2026",
            command=self._restaurar_defaults,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["warning"],
        )
        btn_restaurar.grid(row=0, column=1, padx=6, sticky="ew")

        btn_historial = ctk.CTkButton(
            botones_frame,
            text="📋 Ver Historial (Próximamente)",
            command=self._mostrar_historial,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLORES["neutral"],
            state="disabled",
        )
        btn_historial.grid(row=0, column=2, padx=6, sticky="ew")

        # ========== INFORMACIÓN ACTUAL ==========
        info_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=16)
        info_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)

        info_header = ctk.CTkLabel(
            info_frame, text="Configuración Actual", font=ctk.CTkFont(size=16, weight="bold")
        )
        info_header.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 12))

        # Cargar configuración actual al iniciar
        self._cargar_configuracion_actual()

        return self.frame

    def _cargar_configuracion_actual(self):
        """Carga la configuración actual en los campos del formulario."""
        try:
            resultado = self.controller.cargar_configuracion()

            if resultado["success"]:
                config = resultado["config"]
                self.var_anio.set(str(config["anio_vigente"]))
                self.var_salario_minimo.set(f"{config['salario_minimo_mensual']:,.0f}")
                self.var_auxilio_transporte.set(f"{config['auxilio_transporte_mensual']:,.0f}")
                self.var_porcentaje_afp.set(f"{config['porcentaje_afp'] * 100:.2f}")
                self.var_porcentaje_eps.set(f"{config['porcentaje_eps'] * 100:.2f}")
            else:
                messagebox.showerror("Error", resultado["error"])
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar configuración: {str(e)}")

    def _guardar_configuracion(self):
        """Guarda la configuración ingresada por el usuario."""
        try:
            # Obtener y limpiar valores
            anio_str = self.var_anio.get().strip()
            salario_str = self.var_salario_minimo.get().strip().replace(",", "")
            auxilio_str = self.var_auxilio_transporte.get().strip().replace(",", "")
            afp_str = self.var_porcentaje_afp.get().strip()
            eps_str = self.var_porcentaje_eps.get().strip()

            # Validar que no estén vacíos
            if not all([anio_str, salario_str, auxilio_str, afp_str, eps_str]):
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return

            # Convertir a tipos adecuados
            try:
                anio = int(anio_str)
                salario_minimo = float(salario_str)
                auxilio_transporte = float(auxilio_str)
                porcentaje_afp = float(afp_str)
                porcentaje_eps = float(eps_str)
            except ValueError:
                messagebox.showerror("Error", "Los valores deben ser numéricos.")
                return

            # Llamar al controlador
            resultado = self.controller.guardar_configuracion(
                anio=anio,
                salario_minimo=salario_minimo,
                auxilio_transporte=auxilio_transporte,
                porcentaje_afp=porcentaje_afp,
                porcentaje_eps=porcentaje_eps,
            )

            if resultado["success"]:
                messagebox.showinfo(
                    "Éxito",
                    f"{resultado['mensaje']}\n\n"
                    f"Los nuevos valores se aplicarán en los próximos cálculos de nómina.",
                )
            else:
                messagebox.showerror("Error", resultado["error"])

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")

    def _restaurar_defaults(self):
        """Restaura los valores por defecto de 2026."""
        try:
            confirmacion = messagebox.askyesno(
                "Confirmar",
                "¿Estás seguro de restaurar los valores por defecto de 2026?",
            )

            if not confirmacion:
                return

            resultado = self.controller.restaurar_defaults_2026()

            if resultado["success"]:
                messagebox.showinfo("Éxito", resultado["mensaje"])
                self._cargar_configuracion_actual()
            else:
                messagebox.showerror("Error", resultado["error"])

        except Exception as e:
            messagebox.showerror("Error", f"Error al restaurar configuración: {str(e)}")

    def _mostrar_historial(self):
        """Muestra el historial de configuraciones en una ventana modal."""
        # Crear ventana modal
        ventana_historial = ctk.CTkToplevel(self.content_frame)
        ventana_historial.title("Historial de Configuraciones")
        ventana_historial.geometry("900x500")
        ventana_historial.resizable(True, True)
        ventana_historial.grid_rowconfigure(1, weight=1)
        ventana_historial.grid_columnconfigure(0, weight=1)

        # Encabezado
        ctk.CTkLabel(
            ventana_historial,
            text="📋 Historial de Configuraciones",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10))

        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(ventana_historial)
        tabla_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        # Crear tabla con scrollbar
        from tkinter import ttk
        
        tabla = ttk.Treeview(
            tabla_frame,
            columns=(
                "Año",
                "SMMLV",
                "Auxilio",
                "AFP",
                "EPS",
                "Fecha",
                "Estado",
            ),
            height=15,
            show="headings",
        )

        # Configurar columnas
        tabla.column("#0", width=0, stretch=False)
        tabla.column("Año", anchor="center", width=60)
        tabla.column("SMMLV", anchor="right", width=150)
        tabla.column("Auxilio", anchor="right", width=120)
        tabla.column("AFP", anchor="center", width=60)
        tabla.column("EPS", anchor="center", width=60)
        tabla.column("Fecha", anchor="center", width=180)
        tabla.column("Estado", anchor="center", width=80)

        tabla.heading("Año", text="Año")
        tabla.heading("SMMLV", text="SMMLV")
        tabla.heading("Auxilio", text="Auxilio Transporte")
        tabla.heading("AFP", text="AFP %")
        tabla.heading("EPS", text="EPS %")
        tabla.heading("Fecha", text="Fecha Creación")
        tabla.heading("Estado", text="Estado")

        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar_y.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=tabla.xview)
        tabla.configure(xscroll=scrollbar_x.set)
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        tabla.grid(row=0, column=0, sticky="nsew")

        # Llenar tabla con datos
        configuraciones = self.controller.obtener_historial_configuraciones()
        for config in configuraciones:
            estado = "✓ Activa" if config["activa"] else "Inactiva"
            tabla.insert(
                "",
                "end",
                values=(
                    config["anio_vigente"],
                    f"${config['salario_minimo_mensual']:,.0f}",
                    f"${config['auxilio_transporte_mensual']:,.0f}",
                    f"{config['porcentaje_afp'] * 100:.1f}%",
                    f"{config['porcentaje_eps'] * 100:.1f}%",
                    config["fecha_creacion"],
                    estado,
                ),
            )

        # Frame de botones
        btn_frame = ctk.CTkFrame(ventana_historial, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=(10, 20))

        ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=ventana_historial.destroy,
            fg_color=COLORES["danger"],
            hover_color="#b91c1c",
        ).pack(side="right", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Ver Cambios Detallados",
            command=lambda: self._mostrar_cambios_detallados(ventana_historial),
            fg_color=COLORES["secondary"],
            hover_color="#1e40af",
        ).pack(side="right", padx=10)

    def _mostrar_cambios_detallados(self, parent_window):
        """Muestra el historial detallado de cambios."""
        # Crear nueva ventana modal
        ventana_cambios = ctk.CTkToplevel(parent_window)
        ventana_cambios.title("Historial de Cambios")
        ventana_cambios.geometry("900x500")
        ventana_cambios.resizable(True, True)
        ventana_cambios.grid_rowconfigure(1, weight=1)
        ventana_cambios.grid_columnconfigure(0, weight=1)

        # Encabezado
        ctk.CTkLabel(
            ventana_cambios,
            text="📝 Historial de Cambios Detallado",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10))

        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(ventana_cambios)
        tabla_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        tabla_frame.grid_rowconfigure(0, weight=1)
        tabla_frame.grid_columnconfigure(0, weight=1)

        # Crear tabla con scrollbar
        from tkinter import ttk
        
        tabla = ttk.Treeview(
            tabla_frame,
            columns=("Campo", "Valor Anterior", "Valor Nuevo", "Fecha", "Usuario"),
            height=15,
            show="headings",
        )

        # Configurar columnas
        tabla.column("#0", width=0, stretch=False)
        tabla.column("Campo", anchor="w", width=180)
        tabla.column("Valor Anterior", anchor="right", width=200)
        tabla.column("Valor Nuevo", anchor="right", width=200)
        tabla.column("Fecha", anchor="center", width=180)
        tabla.column("Usuario", anchor="center", width=100)

        tabla.heading("Campo", text="Campo Modificado")
        tabla.heading("Valor Anterior", text="Valor Anterior")
        tabla.heading("Valor Nuevo", text="Valor Nuevo")
        tabla.heading("Fecha", text="Fecha del Cambio")
        tabla.heading("Usuario", text="Usuario")

        # Scrollbar vertical
        scrollbar_y = ttk.Scrollbar(tabla_frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar_y.set)
        scrollbar_y.grid(row=0, column=1, sticky="ns")

        # Scrollbar horizontal
        scrollbar_x = ttk.Scrollbar(tabla_frame, orient="horizontal", command=tabla.xview)
        tabla.configure(xscroll=scrollbar_x.set)
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        tabla.grid(row=0, column=0, sticky="nsew")

        # Llenar tabla con datos
        cambios = self.controller.obtener_historial_cambios()
        for cambio in cambios:
            tabla.insert(
                "",
                "end",
                values=(
                    cambio["campo_cambiado"],
                    cambio["valor_anterior"],
                    cambio["valor_nuevo"],
                    cambio["fecha_cambio"],
                    cambio["usuario"],
                ),
            )

        # Frame de botones
        btn_frame = ctk.CTkFrame(ventana_cambios, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=(10, 20))

        ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=ventana_cambios.destroy,
            fg_color=COLORES["danger"],
            hover_color="#b91c1c",
        ).pack(side="right", padx=10)
