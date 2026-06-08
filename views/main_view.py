import customtkinter as ctk
from tkinter import StringVar
from controllers.main_controller import MainController
from views.crud_empleado_view import CrudEmpleadoView
from views.liquidar_nomina_view import LiquidarNominaView
from views.configuracion_view import ConfiguracionView
from views.gestion_conceptos_view import GestionConceptosView


class MainView:
    def __init__(self, controller: MainController):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.controller = controller
        self.root = ctk.CTk()
        self.root.title("Gestión de Nómina")
        self.root.geometry("1024x680")
        self.root.minsize(940, 640)

        self.sidebar = None
        self.content_frame = None
        self.frames = {}
        self._frame_factories = {}  # Diccionario de fábricas para lazy loading
        self.empleado_seleccionado = StringVar()
        self.horas_extra_var = StringVar(value="0")

        self._build_ui()

    def _build_ui(self):
        # Configuración responsive del root
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Sidebar (scrollable) fija a la izquierda
        # Usamos CTkScrollableFrame para permitir scroll si la ventana es pequeña
        try:
            self.sidebar = ctk.CTkScrollableFrame(self.root, width=240, corner_radius=0)
        except Exception:
            # Fallback: si la versión de customtkinter no tiene CTkScrollableFrame, usar CTkFrame
            self.sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0)

        self.sidebar.grid(row=0, column=0, sticky="nsw")
        # Dejar que el contenido pueda expandirse y en versiones con scroll
        self.sidebar.grid_rowconfigure(0, weight=1)
        # Algunas versiones de CTkScrollableFrame no aceptan argumentos en grid_propagate.
        # Llamamos de forma segura comprobando la firma y probando alternativas.
        try:
            import inspect

            if hasattr(self.sidebar, "grid_propagate"):
                sig = inspect.signature(self.sidebar.grid_propagate)
                # Si la firma solo incluye 'self' (1 parámetro), llamamos sin args
                if len(sig.parameters) <= 1:
                    try:
                        self.sidebar.grid_propagate()
                    except Exception:
                        # Si falla, intentar ignorar y continuar
                        pass
                else:
                    try:
                        self.sidebar.grid_propagate(False)
                    except Exception:
                        try:
                            self.sidebar.grid_propagate()
                        except Exception:
                            pass
        except Exception:
            # En caso de cualquier error de introspección, ignoramos y seguimos
            pass

        title = ctk.CTkLabel(
            self.sidebar,
            text="Nómina Pro",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(24, 8), sticky="w")

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Gestión moderna",
            font=ctk.CTkFont(size=13)
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 24), sticky="w")

        # Botones del sidebar
        btn_dashboard = ctk.CTkButton(
            self.sidebar,
            text="Dashboard",
            command=lambda: self._show_frame("dashboard"),
            anchor="w"
        )
        btn_dashboard.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        btn_empleados = ctk.CTkButton(
            self.sidebar,
            text="Empleados",
            command=lambda: self._show_frame("empleados"),
            anchor="w"
        )
        btn_empleados.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        btn_crud = ctk.CTkButton(
            self.sidebar,
            text="Gestionar Empleados",
            command=lambda: self._show_frame("crud"),
            anchor="w"
        )
        btn_crud.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        btn_liquidar_nomina = ctk.CTkButton(
            self.sidebar,
            text="Liquidar Nómina",
            command=lambda: self._show_frame("liquidar_nomina"),
            anchor="w"
        )
        btn_liquidar_nomina.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        btn_configuracion = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Configuración Legal",
            command=lambda: self._show_frame("configuracion"),
            anchor="w"
        )
        btn_configuracion.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        btn_conceptos = ctk.CTkButton(
            self.sidebar,
            text="📋 Conceptos de Nómina",
            command=lambda: self._show_frame("conceptos"),
            anchor="w"
        )
        btn_conceptos.grid(row=7, column=0, padx=20, pady=8, sticky="ew")

        btn_liquidar = ctk.CTkButton(
            self.sidebar,
            text="Liquidar (Old)",
            command=lambda: self._show_frame("liquidar"),
            anchor="w"
        )
        # Mover a la siguiente fila para evitar solapamiento con el botón de conceptos
        btn_liquidar.grid(row=8, column=0, padx=20, pady=8, sticky="ew")

        # Content frame que ocupa TODO el espacio restante
        self.content_frame = ctk.CTkFrame(self.root)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # ============================================================
        # LAZY LOADING - Registrar fábricas (NO crear vistas aún)
        # ============================================================
        self._frame_factories = {
            "dashboard": self._create_dashboard_frame,
            "empleados": self._create_empleados_frame,
            "crud": self._create_crud_frame,
            "liquidar_nomina": self._create_liquidar_nomina_frame,
            "configuracion": self._create_configuracion_frame,
            "conceptos": self._create_gestion_conceptos_frame,
            "liquidar": self._create_liquidar_frame,
        }

        # Precargar solo dashboard para inicio rápido
        self.frames["dashboard"] = self._create_dashboard_frame()

        # Mostrar dashboard inicial
        self._show_frame("dashboard")

    # ============================================================
    # DASHBOARD - Layout Responsive
    # ============================================================
    def _create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Cards container
        cards_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        cards_frame.grid(row=1, column=0, sticky="new", padx=20, pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="cards")

        resumen = self.controller.generar_resumen_dashboard()

        card1 = self._create_stat_card(
            cards_frame,
            "Empleados activos",
            str(resumen["empleados_activos"])
        )
        card1.grid(row=0, column=0, padx=10, pady=20, sticky="nsew")

        card2 = self._create_stat_card(
            cards_frame,
            "Gasto total mensual",
            f"${resumen['gasto_total_mensual']:,.2f}"
        )
        card2.grid(row=0, column=1, padx=10, pady=20, sticky="nsew")

        card3 = self._create_stat_card(
            cards_frame,
            "Salario promedio",
            f"${resumen['salario_promedio']:,.2f}"
        )
        card3.grid(row=0, column=2, padx=10, pady=20, sticky="nsew")

        # Descripción
        descripcion = ctk.CTkLabel(
            frame,
            text="Sistema de nómina con flujo básico para visualizar empleados y calcular liquidaciones. Usa datos de prueba sin conexión a base de datos.",
            wraplength=760,
            justify="left",
            font=ctk.CTkFont(size=14),
        )
        descripcion.grid(row=2, column=0, sticky="nw", padx=20, pady=(0, 20))

        return frame

    def _create_stat_card(self, parent, title: str, value: str):
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        label_title = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14)
        )
        label_title.grid(row=0, column=0, padx=16, pady=(16, 6), sticky="w")

        label_value = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        label_value.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        return card

    # ============================================================
    # EMPLEADOS - Layout Responsive
    # ============================================================
    def _create_empleados_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Empleados",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Contenedor de la tabla
        table_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        table_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Header de la tabla
        headers = ["Nombre", "Cargo", "Salario"]
        header_container = ctk.CTkFrame(
            table_frame,
            fg_color="#111827",
            corner_radius=12
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header_container.grid_columnconfigure((0, 1, 2), weight=1)

        for index, label in enumerate(headers):
            ctk.CTkLabel(
                header_container,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            ).grid(row=0, column=index, padx=12, pady=12, sticky="ew")

        # ScrollableFrame
        scroll = ctk.CTkScrollableFrame(
            table_frame,
            corner_radius=16,
            fg_color="#111827"
        )
        scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid_columnconfigure(0, weight=1)

        empleados = self.controller.obtener_empleados()
        for index, empleado in enumerate(empleados):
            row_frame = ctk.CTkFrame(
                scroll,
                fg_color="#1f2937",
                corner_radius=12
            )
            row_frame.grid(row=index, column=0, padx=8, pady=6, sticky="ew")
            row_frame.grid_columnconfigure((0, 1, 2), weight=1)

            ctk.CTkLabel(
                row_frame,
                text=empleado["nombre"],
                anchor="w"
            ).grid(row=0, column=0, padx=12, pady=12, sticky="ew")

            ctk.CTkLabel(
                row_frame,
                text=empleado["cargo"],
                anchor="w"
            ).grid(row=0, column=1, padx=12, pady=12, sticky="ew")

            ctk.CTkLabel(
                row_frame,
                text=f"${empleado['salario']:,.2f}",
                anchor="e"
            ).grid(row=0, column=2, padx=12, pady=12, sticky="ew")

        return frame

    # ============================================================
    # CRUD EMPLEADOS
    # ============================================================
    def _create_crud_frame(self):
        """Crea el frame del CRUD de empleados."""
        crud_view = CrudEmpleadoView(self.content_frame, self.controller)
        return crud_view.crear_frame()

    # ============================================================
    # LIQUIDAR NÓMINA
    # ============================================================
    def _create_liquidar_nomina_frame(self):
        """Crea el frame de liquidación de nómina quincenal."""
        liquidar_view = LiquidarNominaView(self.content_frame, self.controller)
        return liquidar_view.crear_frame()

    # ============================================================
    # CONFIGURACIÓN
    # ============================================================
    def _create_configuracion_frame(self):
        """Crea el frame de configuración legal de nómina."""
        configuracion_view = ConfiguracionView(
            self.content_frame,
            self.controller.config_controller
        )
        return configuracion_view.crear_frame()

    def _create_gestion_conceptos_frame(self):
        gestion_view = GestionConceptosView(self.content_frame, self.controller)
        return gestion_view.crear_frame()

    # ============================================================
    # LIQUIDAR (Old)
    # ============================================================
    def _create_liquidar_frame(self):
        frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            frame,
            text="Liquidar Nómina",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Form frame
        form_frame = ctk.CTkFrame(frame, fg_color="#1f2937", corner_radius=16)
        form_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="new")
        form_frame.grid_columnconfigure(1, weight=1)

        empleado_options = [
            f"{e['id']} - {e['nombre']}"
            for e in self.controller.obtener_empleados()
        ]
        if empleado_options:
            self.empleado_seleccionado.set(empleado_options[0])

        ctk.CTkLabel(
            form_frame,
            text="Selecciona un empleado:",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=16, pady=(16, 8), sticky="w")

        ctk.CTkOptionMenu(
            form_frame,
            values=empleado_options,
            variable=self.empleado_seleccionado,
            width=300
        ).grid(row=0, column=1, padx=16, pady=(16, 8), sticky="ew")

        ctk.CTkLabel(
            form_frame,
            text="Horas extra:",
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, padx=16, pady=8, sticky="w")

        ctk.CTkEntry(
            form_frame,
            textvariable=self.horas_extra_var,
            width=120
        ).grid(row=1, column=1, padx=16, pady=8, sticky="w")

        ctk.CTkButton(
            form_frame,
            text="Calcular",
            command=self._calcular_nomina
        ).grid(row=2, column=0, columnspan=2, padx=16, pady=12)

        # Resultado
        self.resultado_label = ctk.CTkLabel(
            form_frame,
            text="",
            wraplength=700,
            justify="left",
            font=ctk.CTkFont(size=13)
        )
        self.resultado_label.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=16,
            pady=(12, 16),
            sticky="nw"
        )

        return frame

    # ============================================================
    # NAVEGACIÓN CON LAZY LOADING
    # ============================================================
    def _show_frame(self, name: str):
        """Muestra un frame, creándolo bajo demanda si no existe."""
        # Crear vista bajo demanda si no existe (lazy loading)
        if name not in self.frames:
            if name in self._frame_factories:
                # Crear la vista solo cuando se necesite
                self.frames[name] = self._frame_factories[name]()

        # Ocultar todas las vistas existentes
        for key, frame in self.frames.items():
            frame.grid_remove()

        # Mostrar la vista solicitada
        if name in self.frames:
            self.frames[name].grid(row=0, column=0, sticky="nsew")

    # ============================================================
    # CÁLCULO DE NÓMINA (Old)
    # ============================================================
    def _calcular_nomina(self):
        try:
            seleccionado = int(self.empleado_seleccionado.get().split(" - ")[0])
            horas_extra = float(self.horas_extra_var.get())
        except ValueError:
            self.resultado_label.configure(
                text="Ingrese valores válidos para el empleado y las horas extra."
            )
            return

        resultado = self.controller.liquidar_nomina(seleccionado, horas_extra)
        if "error" in resultado:
            self.resultado_label.configure(text=resultado["error"])
            return

        empleado = resultado["empleado"]
        nomina = resultado["nomina"]
        texto = (
            f"Liquidación para {empleado['nombre']} ({empleado['cargo']}):\n"
            f"Salario base: ${nomina['salario_base']:,.2f}\n"
            f"Horas extra: {horas_extra} -> ${nomina['total_extra']:,.2f}\n"
            f"Descuentos aproximados: ${nomina['descuentos']:,.2f}\n"
            f"Pago neto estimado: ${nomina['neto']:,.2f}"
        )
        self.resultado_label.configure(text=texto)

    # ============================================================
    # EJECUCIÓN
    # ============================================================
    def run(self):
        self.root.mainloop()