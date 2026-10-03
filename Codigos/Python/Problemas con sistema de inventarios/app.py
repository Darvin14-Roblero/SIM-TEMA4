import random
import tkinter as tk
from tkinter import ttk, messagebox


class SimuladorInventario:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtema 4.3.2 - Sistemas de Inventarios (Política s, Q en Python)")
        self.root.geometry("880x620")

        # --- Panel Superior: Parámetros ---
        frame_params = ttk.LabelFrame(self.root, text="Parámetros de la Política (s, Q)", padding=10)
        frame_params.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_params, text="Inv. Inicial:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_inv_init = ttk.Entry(frame_params, width=8)
        self.entry_inv_init.insert(0, "100")
        self.entry_inv_init.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_params, text="Reorden (s):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_s = ttk.Entry(frame_params, width=8)
        self.entry_s.insert(0, "30")
        self.entry_s.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_params, text="Lote (Q):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_q = ttk.Entry(frame_params, width=8)
        self.entry_q.insert(0, "80")
        self.entry_q.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(frame_params, text="Lead Time (Días):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_lead = ttk.Entry(frame_params, width=8)
        self.entry_lead.insert(0, "3")
        self.entry_lead.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(frame_params, text="Días Simulación:").grid(row=1, column=2, padx=5, pady=5)
        self.entry_dias = ttk.Entry(frame_params, width=8)
        self.entry_dias.insert(0, "30")
        self.entry_dias.grid(row=1, column=3, padx=5, pady=5)

        btn_ejecutar = ttk.Button(frame_params, text="Simular Inventario", command=self.ejecutar_simulacion)
        btn_ejecutar.grid(row=1, column=4, columnspan=2, padx=10, pady=5, sticky="we")

        # --- Panel Central: Tabla Diario ---
        frame_tabla = ttk.LabelFrame(self.root, text="Registro Diario del Inventario", padding=10)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = ("Día", "Inv. Inicial", "Demanda", "Inv. Final", "Faltantes", "Orden Recibida", "Estado de Pedido")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)

        anchos = [50, 90, 80, 90, 80, 110, 220]
        for col, ancho in zip(columnas, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=ancho)

        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Panel Inferior: Resumen ---
        frame_resumen = ttk.LabelFrame(self.root, text="Resumen del Sistema", padding=10)
        frame_resumen.pack(fill="x", padx=10, pady=5)

        self.lbl_resumen = ttk.Label(frame_resumen, text="Configure parámetros y haga clic en 'Simular Inventario'.", font=("Consolas", 10))
        self.lbl_resumen.pack(anchor="w")

    def ejecutar_simulacion(self):
        try:
            inv_actual = int(self.entry_inv_init.get())
            s = int(self.entry_s.get())
            Q = int(self.entry_q.get())
            lead_time = int(self.entry_lead.get())
            total_dias = int(self.entry_dias.get())

            random.seed(42)  # Para reproducibilidad de la demanda

            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            orden_en_transito = 0
            dia_llegada_orden = -1

            total_demanda = 0
            total_ventas = 0
            total_faltantes = 0
            total_ordenes = 0
            suma_inv_diario = 0

            for dia in range(1, total_dias + 1):
                inv_inicial_dia = inv_actual
                orden_recibida_hoy = 0
                estado_str = "SIN PEDIDO"

                # 1. Llega pedido en tránsito
                if orden_en_transito > 0 and dia == dia_llegada_orden:
                    inv_actual += orden_en_transito
                    orden_recibida_hoy = orden_en_transito
                    orden_en_transito = 0
                    dia_llegada_orden = -1
                    estado_str = "PEDIDO RECIBIDO"

                # 2. Generar demanda diaria estocástica ~ N(μ=15, σ=5)
                demanda_hoy = max(0, int(round(random.gauss(15, 5))))
                total_demanda += demanda_hoy

                # 3. Satisfacer demanda
                if inv_actual >= demanda_hoy:
                    inv_actual -= demanda_hoy
                    total_ventas += demanda_hoy
                    faltantes_hoy = 0
                else:
                    total_ventas += inv_actual
                    faltantes_hoy = demanda_hoy - inv_actual
                    inv_actual = 0
                    total_faltantes += faltantes_hoy

                # 4. Revisión de inventario (Posición = Físico + Tránsito)
                posicion_inv = inv_actual + orden_en_transito
                if posicion_inv <= s and orden_en_transito == 0:
                    orden_en_transito = Q
                    dia_llegada_orden = dia + lead_time
                    total_ordenes += 1
                    if orden_recibida_hoy > 0:
                        estado_str = f"RECIBIDO Y REORDENADO (Llega día {dia_llegada_orden})"
                    else:
                        estado_str = f"ORDEN COLOCADA (Llega día {dia_llegada_orden})"

                suma_inv_diario += inv_actual

                # Agregar a tabla
                row = (dia, inv_inicial_dia, demanda_hoy, inv_actual, faltantes_hoy, orden_recibida_hoy, estado_str)
                self.tree.insert("", "end", values=row)

            inv_promedio = suma_inv_diario / total_dias
            fill_rate = (total_ventas / total_demanda * 100) if total_demanda > 0 else 0.0

            resumen_txt = (
                f"Días Simulados: {total_dias} | Demanda Total: {total_demanda} | Ventas: {total_ventas} | Faltantes: {total_faltantes}\n"
                f"Órdenes Emitidas: {total_ordenes} | Inv. Promedio Diario: {inv_promedio:.2f} unidades | Nivel de Servicio (Fill Rate): {fill_rate:.2f}%"
            )
            self.lbl_resumen.config(text=resumen_txt)

        except ValueError:
            messagebox.showerror("Error", "Ingrese números enteros válidos en todos los campos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorInventario(root)
    root.mainloop()