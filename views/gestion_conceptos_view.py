import customtkinter as ctk
from tkinter import messagebox
from controllers.main_controller import MainController


class GestionConceptosView:
    def __init__(self, content_frame: ctk.CTkFrame, controller: MainController):
        self.content_frame = content_frame
        self.controller = controller
        self.frame = None
        self.scroll_conceptos = None
        self.scroll_asignaciones = None
        self.empleado_select = None

    def crear_frame(self) -> ctk.CTkFrame:
        self.frame = ctk.CTkFrame(self.content_frame, corner_radius=20)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(self.frame, text="Gestión de Conceptos de Nómina", font=ctk.CTkFont(size=24, weight="bold"))
        header.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # Catalogo
        catalog_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=12)
        catalog_frame.grid(row=1, column=0, padx=20, pady=(0, 12), sticky="nsew")
        catalog_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(catalog_frame, text="Catálogo de Conceptos", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=12)

        btn_frame = ctk.CTkFrame(catalog_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=0, sticky="e", padx=12)
        ctk.CTkButton(btn_frame, text="➕ Nuevo Concepto", command=self._abrir_modal_nuevo_concepto, fg_color="#10b981").grid(row=0, column=0)

        self.scroll_conceptos = ctk.CTkScrollableFrame(catalog_frame, corner_radius=8, fg_color="#111827")
        self.scroll_conceptos.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.scroll_conceptos.grid_columnconfigure(0, weight=1)

        # Asignaciones
        asign_frame = ctk.CTkFrame(self.frame, fg_color="#1f2937", corner_radius=12)
        asign_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        asign_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(asign_frame, text="Asignaciones a Empleados", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=12, pady=12)

        empleados = self.controller.obtener_empleados()
        empleados_opts = [f"{e['id']} - {e['nombre']} {e['apellido']}" for e in empleados]
        self.empleado_select = ctk.CTkOptionMenu(asign_frame, values=empleados_opts)
        if empleados_opts:
            self.empleado_select.set(empleados_opts[0])
        self.empleado_select.grid(row=0, column=0, padx=12, pady=(0, 12), sticky="w")

        btn_asign = ctk.CTkButton(asign_frame, text="➕ Asignar Concepto", command=self._abrir_modal_asignar)
        btn_asign.grid(row=0, column=0, padx=12, pady=(0, 12), sticky="e")

        self.scroll_asignaciones = ctk.CTkScrollableFrame(asign_frame, corner_radius=8, fg_color="#111827")
        self.scroll_asignaciones.grid(row=1, column=0, padx=12, pady=12, sticky="nsew")
        self.scroll_asignaciones.grid_columnconfigure(0, weight=1)

        # Inicializar datos
        self._actualizar_catalogo()
        self._actualizar_asignaciones()

        return self.frame

    def _actualizar_catalogo(self):
        for w in self.scroll_conceptos.winfo_children():
            w.destroy()
        conceptos = self.controller.obtener_conceptos_disponibles()
        if not conceptos:
            ctk.CTkLabel(self.scroll_conceptos, text="No hay conceptos", text_color="#9ca3af").grid(pady=12)
            return
        for i, c in enumerate(conceptos):
            f = ctk.CTkFrame(self.scroll_conceptos, fg_color="#1f2937", corner_radius=8)
            f.grid(row=i, column=0, padx=8, pady=8, sticky="ew")
            f.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(f, text=f"{c['id']} - {c['nombre']} ({c.get('naturaleza','devengado')})").grid(row=0, column=0, sticky="w", padx=12, pady=10)
            btns = ctk.CTkFrame(f, fg_color="transparent")
            btns.grid(row=0, column=1, sticky="e", padx=12)
            ctk.CTkButton(btns, text="✎ Editar", width=80, command=lambda cid=c['id']: self._editar_concepto(cid)).grid(row=0, column=0, padx=6)
            ctk.CTkButton(btns, text="✕ Desactivar", width=80, fg_color="#ef4444", command=lambda cid=c['id']: self._desactivar_concepto(cid)).grid(row=0, column=1, padx=6)

    def _actualizar_asignaciones(self):
        for w in self.scroll_asignaciones.winfo_children():
            w.destroy()
        sel = self.empleado_select.get() if self.empleado_select else None
        if not sel:
            ctk.CTkLabel(self.scroll_asignaciones, text="Seleccione un empleado arriba", text_color="#9ca3af").grid(pady=12)
            return
        empleado_id = int(sel.split(" - ")[0])
        asigns = self.controller.obtener_conceptos_de_empleado(empleado_id)
        if not asigns:
            ctk.CTkLabel(self.scroll_asignaciones, text="No hay asignaciones", text_color="#9ca3af").grid(pady=12)
            return
        for i, a in enumerate(asigns):
            f = ctk.CTkFrame(self.scroll_asignaciones, fg_color="#1f2937", corner_radius=8)
            f.grid(row=i, column=0, padx=8, pady=8, sticky="ew")
            f.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(f, text=f"{a['id']} - {a['nombre']} ({a.get('naturaleza','devengado')})").grid(row=0, column=0, sticky="w", padx=12, pady=10)
            ctk.CTkButton(f, text="✕ Quitar", width=80, fg_color="#ef4444", command=lambda aid=a['id']: self._quitar_asignacion(aid)).grid(row=0, column=1, padx=12)

    def _abrir_modal_nuevo_concepto(self):
        modal = ctk.CTkToplevel(self.frame)
        modal.title("Nuevo Concepto")
        modal.geometry("480x320")

        ctk.CTkLabel(modal, text="Nombre:").pack(padx=12, pady=(12, 4), anchor="w")
        entrada_nombre = ctk.CTkEntry(modal)
        entrada_nombre.pack(padx=12, fill="x")

        ctk.CTkLabel(modal, text="Tipo (fijo/variable/porcentaje):").pack(padx=12, pady=(8, 4), anchor="w")
        entrada_tipo = ctk.CTkEntry(modal)
        entrada_tipo.pack(padx=12, fill="x")

        ctk.CTkLabel(modal, text="Naturaleza (devengado/deduccion):").pack(padx=12, pady=(8, 4), anchor="w")
        entrada_nat = ctk.CTkEntry(modal)
        entrada_nat.pack(padx=12, fill="x")

        ctk.CTkLabel(modal, text="Valor (opcional):").pack(padx=12, pady=(8, 4), anchor="w")
        entrada_val = ctk.CTkEntry(modal)
        entrada_val.pack(padx=12, fill="x")

        def crear():
            nombre = entrada_nombre.get().strip()
            tipo = entrada_tipo.get().strip() or 'fijo'
            naturaleza = entrada_nat.get().strip() or 'devengado'
            valor = None
            try:
                v = entrada_val.get().strip()
                if v:
                    valor = float(v)
            except Exception:
                messagebox.showerror("Error", "Valor inválido")
                return
            resp = self.controller.crear_concepto(nombre, tipo, naturaleza, valor)
            if resp.get('success'):
                modal.destroy()
                self._actualizar_catalogo()
                messagebox.showinfo("Éxito", "Concepto creado")
            else:
                messagebox.showerror("Error", resp.get('error', 'Error'))

        ctk.CTkButton(modal, text="Crear", command=crear).pack(padx=12, pady=12)

    def _abrir_modal_asignar(self):
        sel = self.empleado_select.get() if self.empleado_select else None
        if not sel:
            messagebox.showerror("Error", "Seleccione un empleado")
            return
        empleado_id = int(sel.split(" - ")[0])

        modal = ctk.CTkToplevel(self.frame)
        modal.title("Asignar Concepto")
        modal.geometry("480x260")

        conceptos = self.controller.obtener_conceptos_disponibles()
        opciones = [f"{c['id']} - {c['nombre']}" for c in conceptos]
        ctk.CTkLabel(modal, text="Concepto:").pack(padx=12, pady=(12,4), anchor="w")
        combo = ctk.CTkOptionMenu(modal, values=opciones)
        if opciones:
            combo.set(opciones[0])
        combo.pack(padx=12, fill="x")

        ctk.CTkLabel(modal, text="Valor personalizado (opcional):").pack(padx=12, pady=(8,4), anchor="w")
        entrada_val = ctk.CTkEntry(modal)
        entrada_val.pack(padx=12, fill="x")

        def asignar():
            selc = combo.get()
            concepto_id = int(selc.split(" - ")[0])
            val = entrada_val.get().strip()
            valor_personalizado = None
            if val:
                try:
                    valor_personalizado = float(val)
                except Exception:
                    messagebox.showerror("Error", "Valor inválido")
                    return
            resp = self.controller.asignar_concepto_a_empleado(empleado_id, concepto_id=concepto_id, valor_personalizado=valor_personalizado)
            if resp.get('success'):
                modal.destroy()
                self._actualizar_asignaciones()
                messagebox.showinfo("Éxito", "Asignación creada")
            else:
                messagebox.showerror("Error", resp.get('error', 'Error'))

        ctk.CTkButton(modal, text="Asignar", command=asignar).pack(padx=12, pady=12)

    def _editar_concepto(self, concepto_id: int):
        messagebox.showinfo("Editar", f"Editar concepto {concepto_id} (pendiente)")

    def _desactivar_concepto(self, concepto_id: int):
        # Soft-delete: reutilizar repo_conceptos.eliminar
        try:
            ok = self.controller.repo_conceptos.eliminar(concepto_id)
            if ok:
                self._actualizar_catalogo()
                messagebox.showinfo("Éxito", "Concepto desactivado")
            else:
                messagebox.showerror("Error", "No se pudo desactivar")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _quitar_asignacion(self, asign_id: int):
        try:
            ok = self.controller.repo_conceptos_emp.desasignar(asign_id)
            if ok:
                self._actualizar_asignaciones()
                messagebox.showinfo("Éxito", "Asignación removida")
            else:
                messagebox.showerror("Error", "No se pudo remover asignación")
        except Exception as e:
            messagebox.showerror("Error", str(e))
