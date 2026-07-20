import customtkinter as ctk
from tkinter import messagebox
from controllers.concepto_controller import ConceptoController
from controllers.empleado_controller import EmpleadoController


class GestionConceptosView:
    def __init__(self, content_frame: ctk.CTkFrame, controller: ConceptoController):
        self.content_frame = content_frame
        self.concepto_controller = controller
        self.empleado_controller = EmpleadoController()
        self.frame = None
        self.scroll_conceptos = None
        self.scroll_asignaciones = None
        self.empleado_select = None

    def crear_frame(self) -> ctk.CTkFrame:
        # Frame principal con fondo oscuro elegante
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20, fg_color="#0f172a") # Slate 900
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        # Header principal estilizado
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 15))
        
        header = ctk.CTkLabel(
            header_frame, 
            text="Gestión de Conceptos de Nómina", 
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color="#f8fafc" # Slate 50
        )
        header.pack(side="left")

        # Contenedor Grid de Dos Filas Verticales
        main_grid = ctk.CTkFrame(self.frame, fg_color="transparent")
        main_grid.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 25))
        main_grid.grid_columnconfigure(0, weight=1) # Una sola columna
        main_grid.grid_rowconfigure(0, weight=1, uniform="row") # Fila 1: Catálogo
        main_grid.grid_rowconfigure(1, weight=1, uniform="row") # Fila 2: Asignaciones

        # ==========================================
        # COLUMNA (FILA) SUPERIOR: CATÁLOGO DE CONCEPTOS
        # ==========================================
        catalog_frame = ctk.CTkFrame(main_grid, fg_color="#1e293b", corner_radius=16, border_width=1, border_color="#334155")
        catalog_frame.grid(row=0, column=0, padx=0, pady=(0, 15), sticky="nsew") # Cambiado row=0, pady inferior
        catalog_frame.grid_rowconfigure(2, weight=1)
        catalog_frame.grid_columnconfigure(0, weight=1)

        # Encabezado del catálogo
        cat_header_f = ctk.CTkFrame(catalog_frame, fg_color="transparent")
        cat_header_f.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            cat_header_f, 
            text="Catálogo de Conceptos", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#f1f5f9"
        ).pack(side="left")

        ctk.CTkButton(
            cat_header_f, 
            text="➕ Nuevo Concepto", 
            command=self._abrir_modal_nuevo_concepto, 
            fg_color="#10b981", # Emerald 500
            hover_color="#059669",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=32,
            corner_radius=8
        ).pack(side="right")

        # Scroll de conceptos
        self.scroll_conceptos = ctk.CTkScrollableFrame(catalog_frame, corner_radius=12, fg_color="#0f172a")
        self.scroll_conceptos.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scroll_conceptos.grid_columnconfigure(0, weight=1)

        # ==========================================
        # COLUMNA (FILA) INFERIOR: ASIGNACIONES A EMPLEADOS
        # ==========================================
        asign_frame = ctk.CTkFrame(main_grid, fg_color="#1e293b", corner_radius=16, border_width=1, border_color="#334155")
        asign_frame.grid(row=1, column=0, padx=0, pady=(15, 0), sticky="nsew") # Cambiado row=1, pady superior
        asign_frame.grid_rowconfigure(2, weight=1)
        asign_frame.grid_columnconfigure(0, weight=1)

        # Encabezado de asignaciones
        asign_header_f = ctk.CTkFrame(asign_frame, fg_color="transparent")
        asign_header_f.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        ctk.CTkLabel(
            asign_header_f, 
            text="Asignación a Empleados", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#f1f5f9"
        ).pack(side="left")

        ctk.CTkButton(
            asign_header_f, 
            text="➕ Asignar Concepto", 
            command=self._abrir_modal_asignar,
            fg_color="#3b82f6", # Blue 500
            hover_color="#2563eb",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=32,
            corner_radius=8
        ).pack(side="right")

        # Selector de Empleados moderno
        selector_f = ctk.CTkFrame(asign_frame, fg_color="transparent")
        selector_f.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(
            selector_f, 
            text="Seleccionar Empleado:", 
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#94a3b8"
        ).pack(side="left", padx=(0, 10))

        empleados = self.empleado_controller.obtener_empleados()
        empleados_opts = [f"{e['id']} - {e['nombre']} {e['apellido']}" for e in empleados]
        self.empleado_select = ctk.CTkOptionMenu(
            selector_f,
            values=empleados_opts,
            command=lambda _: self._actualizar_asignaciones(),
            fg_color="#334155",
            button_color="#475569",
            button_hover_color="#64748b",
            corner_radius=8,
            width=220
        )
        if empleados_opts:
            self.empleado_select.set(empleados_opts[0])
        self.empleado_select.pack(side="left")

        # Scroll de asignaciones
        self.scroll_asignaciones = ctk.CTkScrollableFrame(asign_frame, corner_radius=12, fg_color="#0f172a")
        self.scroll_asignaciones.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.scroll_asignaciones.grid_columnconfigure(0, weight=1)

        # Cargar datos iniciales
        self._actualizar_catalogo()
        self._actualizar_asignaciones()

        return self.frame

    def _actualizar_catalogo(self):
        for w in self.scroll_conceptos.winfo_children():
            w.destroy()
        conceptos = self.concepto_controller.obtener_conceptos_disponibles()
        if not conceptos:
            ctk.CTkLabel(self.scroll_conceptos, text="No hay conceptos en el catálogo.", text_color="#64748b", font=ctk.CTkFont(family="Inter", size=13, slant="italic")).grid(pady=30)
            return
            
        for i, c in enumerate(conceptos):
            f = ctk.CTkFrame(self.scroll_conceptos, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
            f.grid(row=i, column=0, padx=8, pady=6, sticky="ew")
            f.grid_columnconfigure(0, weight=1)
            
            # Formatear el badge de tipo/naturaleza
            naturaleza = c.get('naturaleza') or 'devengado'
            tipo = c.get('tipo', 'fijo')
            badge_color = "#10b981" if naturaleza == "devengado" else "#ef4444"
            
            info_text = f"{c['id']} • {c['nombre']}\nTipo: {tipo.capitalize()} | {naturaleza.upper()}"
            
            label_info = ctk.CTkLabel(
                f, 
                text=info_text, 
                font=ctk.CTkFont(family="Inter", size=13, weight="normal"), # <- CAMBIADO de "medium" a "normal"
                text_color="#e2e8f0",
                justify="left"
            )
            label_info.grid(row=0, column=0, sticky="w", padx=15, pady=12)
            
            # Botones de Acción minimalistas
            btns = ctk.CTkFrame(f, fg_color="transparent")
            btns.grid(row=0, column=1, sticky="e", padx=15)
            
            ctk.CTkButton(
                btns, 
                text="✎ Editar", 
                width=70, 
                height=26,
                fg_color="#3b82f6",
                hover_color="#2563eb",
                corner_radius=6,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                command=lambda cid=c['id']: self._editar_concepto(cid)
            ).grid(row=0, column=0, padx=4)
            
            ctk.CTkButton(
                btns, 
                text="✕ Desactivar", 
                width=80, 
                height=26,
                fg_color="#b91c1c",
                hover_color="#ef4444",
                corner_radius=6,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                command=lambda cid=c['id']: self._desactivar_concepto(cid)
            ).grid(row=0, column=1, padx=4)

    def _actualizar_asignaciones(self):
        for w in self.scroll_asignaciones.winfo_children():
            w.destroy()
            
        empleados = self.empleado_controller.obtener_empleados()
        empleados_opts = [f"{e['id']} - {e['nombre']} {e['apellido']}" for e in empleados]
        if self.empleado_select:
            try:
                valor_actual = self.empleado_select.get()
            except Exception:
                valor_actual = None
            if empleados_opts:
                self.empleado_select.configure(values=empleados_opts)
                if valor_actual in empleados_opts:
                    self.empleado_select.set(valor_actual)
                else:
                    self.empleado_select.set(empleados_opts[0])
            else:
                self.empleado_select.configure(values=[])
                try:
                    self.empleado_select.set("")
                except Exception:
                    pass

        sel = self.empleado_select.get() if self.empleado_select else None
        if not sel:
            ctk.CTkLabel(self.scroll_asignaciones, text="Seleccione un empleado para ver asignaciones.", text_color="#64748b", font=ctk.CTkFont(family="Inter", size=13, slant="italic")).grid(pady=30)
            return
            
        empleado_id = int(sel.split(" - ")[0])
        asigns = self.concepto_controller.obtener_conceptos_de_empleado(empleado_id)
        if not asigns:
            ctk.CTkLabel(self.scroll_asignaciones, text="Sin conceptos asignados para este periodo.", text_color="#64748b", font=ctk.CTkFont(family="Inter", size=13, slant="italic")).grid(pady=30)
            return
            
        for i, a in enumerate(asigns):
            f = ctk.CTkFrame(self.scroll_asignaciones, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#334155")
            f.grid(row=i, column=0, padx=8, pady=6, sticky="ew")
            f.grid_columnconfigure(0, weight=1)
            
            valor_display = ""
            if a.get('tipo') == 'fijo' and a.get('valor_personalizado') is not None:
                valor_display = f" | Valor: ${a['valor_personalizado']:,.2f}"
            elif a.get('tipo') == 'porcentaje' and a.get('porcentaje_personalizado') is not None:
                valor_display = f" | Porcentaje: {a['porcentaje_personalizado']}%"
            elif a.get('tipo') == 'variable':
                valor_display = f" | Variable: ${a.get('valor_personalizado', 0.0):,.2f}"

            label_asig = ctk.CTkLabel(
                f, 
                text=f"{a['nombre'].upper()}\n({a.get('naturaleza','devengado').capitalize()}{valor_display})", 
                font=ctk.CTkFont(family="Inter", size=13, weight="normal"), # <- CAMBIADO de "medium" a "normal"
                text_color="#e2e8f0",
                justify="left"
            )
            label_asig.grid(row=0, column=0, sticky="w", padx=15, pady=12)
            
            ctk.CTkButton(
                f, 
                text="✕ Quitar", 
                width=80, 
                height=26,
                fg_color="#b91c1c", 
                hover_color="#ef4444",
                corner_radius=6,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                command=lambda aid=a['id']: self._quitar_asignacion(aid)
            ).grid(row=0, column=1, padx=15)

    def _abrir_modal_nuevo_concepto(self):
        # Desactivamos el foco temporalmente de la ventana principal para mantener el Modal modal
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Crear Nuevo Concepto de Nómina")
        modal.geometry("520x460")
        modal.configure(fg_color="#0f172a")
        modal.transient(self.frame)
        modal.wait_visibility()  # Espera a que la ventana sea visible antes de hacer grab_set
        modal.grab_set()

        # Título del Modal
        ctk.CTkLabel(
            modal, 
            text="Datos del Nuevo Concepto", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#f1f5f9"
        ).pack(padx=20, pady=(20, 15), anchor="w")

        # --- CAMPO: NOMBRE ---
        ctk.CTkLabel(modal, text="Nombre del concepto:", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8").pack(padx=20, anchor="w")
        entrada_nombre = ctk.CTkEntry(modal, placeholder_text="Ej. Auxilio de Transporte", fg_color="#1e293b", border_color="#334155", corner_radius=8)
        entrada_nombre.pack(padx=20, pady=(4, 12), fill="x")

        # --- GRID PARA SELECTORES (TIPO Y NATURALEZA) ---
        selectors_f = ctk.CTkFrame(modal, fg_color="transparent")
        selectors_f.pack(padx=20, fill="x")
        selectors_f.grid_columnconfigure(0, weight=1)
        selectors_f.grid_columnconfigure(1, weight=1)

        # Selectores restrictivos para evitar violaciones de tipo
        ctk.CTkLabel(selectors_f, text="Tipo de Concepto:", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8").grid(row=0, column=0, sticky="w", padx=(0, 10))
        combo_tipo = ctk.CTkOptionMenu(
            selectors_f, 
            values=["fijo", "variable", "porcentaje"], # Valores directos del dominio
            fg_color="#1e293b", 
            button_color="#334155", 
            corner_radius=8
        )
        combo_tipo.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 12))

        ctk.CTkLabel(selectors_f, text="Naturaleza:", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8").grid(row=0, column=1, sticky="w", padx=(10, 0))
        combo_nat = ctk.CTkOptionMenu(
            selectors_f, 
            values=["devengado", "deduccion"], # Valores directos del dominio
            fg_color="#1e293b", 
            button_color="#334155", 
            corner_radius=8
        )
        combo_nat.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 12))

        # --- SECCIÓN DINÁMICA: VALOR, PORCENTAJE Y BASE DE CÁLCULO ---
        container_dinamico = ctk.CTkFrame(modal, fg_color="#1e293b", corner_radius=12, border_width=1, border_color="#334155")
        container_dinamico.pack(padx=20, pady=10, fill="x")

        lbl_dinamico = ctk.CTkLabel(container_dinamico, text="Valor Fijo ($):", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8")
        lbl_dinamico.pack(padx=15, pady=(10, 2), anchor="w")
        entrada_val = ctk.CTkEntry(container_dinamico, placeholder_text="Monto numérico (ej. 140000)", fg_color="#0f172a", border_color="#334155", corner_radius=8)
        entrada_val.pack(padx=15, pady=(0, 15), fill="x")

        # Comportamiento Reactivo del Modal en base al Tipo Seleccionado
        def alternar_campos_por_tipo(seleccion):
            # Limpiamos el valor ingresado previamente
            entrada_val.delete(0, 'end')
            if seleccion == "fijo":
                lbl_dinamico.configure(text="Valor Fijo ($):")
                entrada_val.configure(placeholder_text="Monto numérico (ej. 140000)", state="normal")
            elif seleccion == "porcentaje":
                lbl_dinamico.configure(text="Porcentaje (%):")
                entrada_val.configure(placeholder_text="Escriba el % sin el signo (ej. 4)", state="normal")
            else: # Variable
                lbl_dinamico.configure(text="Valor Variable ($) - Se asigna en planilla:")
                entrada_val.configure(placeholder_text="Opcional. Valor por defecto (ej. 0)", state="normal")

        combo_tipo.configure(command=alternar_campos_por_tipo)

        # --- ACCIÓN GUARDAR ---
        def crear():
            nombre = entrada_nombre.get().strip()
            tipo = combo_tipo.get()
            naturaleza = combo_nat.get()
            raw_val = entrada_val.get().strip()

            if not nombre:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return

            # Inicialización de las propiedades del Dominio
            valor = None
            porcentaje = None
            base_calculo = "salario"

            try:
                if tipo == "fijo":
                    if not raw_val:
                        messagebox.showerror("Error", "Los conceptos de tipo Fijo requieren un valor numérico.")
                        return
                    valor = float(raw_val)
                elif tipo == "porcentaje":
                    if not raw_val:
                        messagebox.showerror("Error", "Los conceptos de tipo Porcentaje requieren un porcentaje numérico.")
                        return
                    porcentaje = float(raw_val)
                elif tipo == "variable":
                    valor = float(raw_val) if raw_val else 0.0
            except ValueError:
                messagebox.showerror("Error", "El valor o porcentaje debe ser un número válido.")
                return

            # Pasar datos procesados y saneados al Controlador
            resp = self.concepto_controller.crear_concepto(
                nombre=nombre, 
                tipo=tipo, 
                naturaleza=naturaleza, 
                valor=valor,
                porcentaje=porcentaje,
                base_calculo=base_calculo if tipo == "porcentaje" else None
            )

            if resp.get('success'):
                modal.destroy()
                self._actualizar_catalogo()
                messagebox.showinfo("Éxito", "Concepto de nómina guardado de forma limpia en el catálogo.")
            else:
                messagebox.showerror("Error", resp.get('error', 'No se pudo crear el concepto.'))

        btn_guardar = ctk.CTkButton(
            modal, 
            text="Guardar Concepto", 
            command=crear,
            fg_color="#10b981",
            hover_color="#059669",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=38,
            corner_radius=8
        )
        btn_guardar.pack(padx=20, pady=20, fill="x")

    def _abrir_modal_asignar(self):
        sel = self.empleado_select.get() if self.empleado_select else None
        if not sel:
            messagebox.showerror("Error", "Seleccione un empleado")
            return
        empleado_id = int(sel.split(" - ")[0])

        modal = ctk.CTkToplevel(self.frame)
        modal.title("Asignar Concepto a Empleado")
        modal.geometry("500x320")
        modal.configure(fg_color="#0f172a")
        modal.transient(self.frame)
        modal.wait_visibility()  # Espera a que la ventana sea visible antes de hacer grab_set
        modal.grab_set()

        ctk.CTkLabel(
            modal, 
            text="Asignar Concepto Personalizado", 
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#f1f5f9"
        ).pack(padx=20, pady=(20, 15), anchor="w")

        conceptos = self.concepto_controller.obtener_conceptos_disponibles()
        opciones = [f"{c['id']} - {c['nombre']} ({c.get('tipo', 'fijo')})" for c in conceptos]
        
        ctk.CTkLabel(modal, text="Seleccione el concepto:", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8").pack(padx=20, anchor="w")
        combo = ctk.CTkOptionMenu(modal, values=opciones, fg_color="#1e293b", button_color="#334155", corner_radius=8)
        if opciones:
            combo.set(opciones[0])
        combo.pack(padx=20, pady=(4, 12), fill="x")

        # Campo dinámico de valor personalizado
        ctk.CTkLabel(modal, text="Valor personalizado (dejar vacío para usar valor del catálogo):", font=ctk.CTkFont(family="Inter", size=12), text_color="#94a3b8").pack(padx=20, anchor="w")
        entrada_val = ctk.CTkEntry(modal, placeholder_text="Monto o porcentaje personalizado", fg_color="#1e293b", border_color="#334155", corner_radius=8)
        entrada_val.pack(padx=20, pady=(4, 20), fill="x")

        def asignar():
            selc = combo.get()
            if not selc:
                messagebox.showerror("Error", "No hay conceptos seleccionados")
                return
            concepto_id = int(selc.split(" - ")[0])
            val = entrada_val.get().strip()
            
            valor_personalizado = None
            porcentaje_personalizado = None

            # Encontrar el tipo de concepto seleccionado del catálogo para mapear bien
            concepto_seleccionado = next((c for c in conceptos if c['id'] == concepto_id), None)
            tipo_concepto = concepto_seleccionado.get('tipo', 'fijo') if concepto_seleccionado else 'fijo'

            if val:
                try:
                    num_val = float(val)
                    if tipo_concepto == "porcentaje":
                        porcentaje_personalizado = num_val
                    else:
                        valor_personalizado = num_val
                except ValueError:
                    messagebox.showerror("Error", "El valor personalizado debe ser un número válido.")
                    return

            resp = self.concepto_controller.asignar_concepto_a_empleado(
                empleado_id=empleado_id, 
                concepto_id=concepto_id, 
                valor_personalizado=valor_personalizado,
                porcentaje_personalizado=porcentaje_personalizado
            )

            if resp.get('success'):
                modal.destroy()
                self._actualizar_asignaciones()
                messagebox.showinfo("Éxito", "Concepto asignado con éxito al empleado.")
            else:
                messagebox.showerror("Error", resp.get('error', 'Error al asignar el concepto.'))

        btn_asignar = ctk.CTkButton(
            modal, 
            text="Confirmar Asignación", 
            command=asignar,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=38,
            corner_radius=8
        )
        btn_asignar.pack(padx=20, fill="x")

    def _editar_concepto(self, concepto_id: int):
        messagebox.showinfo("Editar", f"Editar concepto {concepto_id} (Pendiente de implementación)")

    def _desactivar_concepto(self, concepto_id: int):
        confirmar = messagebox.askyesno("Confirmar", "¿Está seguro de que desea desactivar este concepto del catálogo?")
        if not confirmar:
            return
        try:
            ok = self.concepto_controller.repo_conceptos.eliminar(concepto_id)
            if ok:
                self._actualizar_catalogo()
                self._actualizar_asignaciones()
                messagebox.showinfo("Éxito", "Concepto desactivado de forma lógica en la base de datos.")
            else:
                messagebox.showerror("Error", "No se pudo desactivar.")
        except Exception as e:
            messagebox.showerror("Error", f"Error de persistencia: {e}")

    def _quitar_asignacion(self, asign_id: int):
        confirmar = messagebox.askyesno("Confirmar", "¿Desea remover la asignación de este concepto para el empleado?")
        if not confirmar:
            return
        try:
            ok = self.concepto_controller.repo_conceptos_emp.desasignar(asign_id)
            if ok:
                self._actualizar_asignaciones()
                messagebox.showinfo("Éxito", "Asignación desactivada (Borrado lógico ejecutado).")
            else:
                messagebox.showerror("Error", "No se pudo remover la asignación.")
        except Exception as e:
            messagebox.showerror("Error", f"Error de persistencia: {e}")