import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AplicacionSimulacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Integrado de Simulación y Análisis Estadístico")
        self.root.geometry("900x700")  # Corregido: "900x700" con 'x'

        # Contenedor principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear pestañas
        self.tab_colas = ttk.Frame(self.notebook)
        self.tab_inventarios = ttk.Frame(self.notebook)
        self.tab_parametrica = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_colas, text="4.3.1 Líneas de Espera (M/M/1)")
        self.notebook.add(self.tab_inventarios, text="4.3.2 Inventarios (EOQ)")
        self.notebook.add(self.tab_parametrica, text="4.4.1 Pruebas Paramétricas (t-Student)")

        # Inicializar contenido de cada pestaña
        self.crear_tab_colas()
        self.crear_tab_inventarios()
        self.crear_tab_parametrica()

    # =========================================================================
    # 4.3.1 PROBLEMAS CON LÍNEAS DE ESPERA (Simulación M/M/1 con Monte Carlo)
    # =========================================================================
    def crear_tab_colas(self):
        panel_top = ttk.LabelFrame(self.tab_colas, text=" Parámetros de la Cola ", padding=10)
        panel_top.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        ttk.Label(panel_top, text="Tasa de llegada (λ clientes/hora):").grid(row=0, column=0, sticky=tk.W, pady=2)
        entry_lambda = ttk.Entry(panel_top, width=15)
        entry_lambda.insert(0, "4.0")
        entry_lambda.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(panel_top, text="Tasa de servicio (μ clientes/hora):").grid(row=1, column=0, sticky=tk.W, pady=2)
        entry_mu = ttk.Entry(panel_top, width=15)
        entry_mu.insert(0, "6.0")
        entry_mu.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(panel_top, text="Número de clientes a simular:").grid(row=2, column=0, sticky=tk.W, pady=2)
        entry_n = ttk.Entry(panel_top, width=15)
        entry_n.insert(0, "100")
        entry_n.grid(row=2, column=1, padx=5, pady=2)

        panel_bottom = ttk.Frame(self.tab_colas)
        panel_bottom.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        txt_res = tk.Text(panel_bottom, width=35, font=("Courier", 10))
        txt_res.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        frame_plot = ttk.LabelFrame(panel_bottom, text=" Tiempo de Espera por Cliente ", padding=5)
        frame_plot.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def simular_cola():
            try:
                lam = float(entry_lambda.get())
                mu = float(entry_mu.get())
                n = int(entry_n.get())

                if lam >= mu:
                    messagebox.showwarning("Atención", "Para un sistema estable, λ debe ser menor a μ.")

                # Simulación Monte Carlo
                llegadas = np.random.exponential(1.0 / lam, n)
                t_llegadas = np.cumsum(llegadas)
                t_servicios = np.random.exponential(1.0 / mu, n)

                t_inicio = np.zeros(n)
                t_fin = np.zeros(n)

                t_inicio[0] = t_llegadas[0]
                t_fin[0] = t_inicio[0] + t_servicios[0]

                for i in range(1, n):
                    t_inicio[i] = max(t_llegadas[i], t_fin[i - 1])
                    t_fin[i] = t_inicio[i] + t_servicios[i]

                t_espera = t_inicio - t_llegadas
                t_sistema = t_fin - t_llegadas

                txt_res.delete("1.0", tk.END)
                res_str = (
                    f"=== SIMULACIÓN COLA M/M/1 ===\n\n"
                    f"Clientes simulados: {n}\n"
                    f"Tiempo prom. en cola (Wq):\n  {np.mean(t_espera)*60:.2f} min\n"
                    f"Tiempo prom. en sistema (W):\n  {np.mean(t_sistema)*60:.2f} min\n"
                    f"Utilización (ρ):\n  {(lam/mu)*100:.2f} %\n"
                )
                txt_res.insert(tk.END, res_str)

                # Graficar
                for widget in frame_plot.winfo_children():
                    widget.destroy()

                fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
                ax.plot(t_espera * 60, color="#2980b9", marker="o", markersize=3, linestyle="-")
                ax.axhline(np.mean(t_espera) * 60, color="red", linestyle="--", label="Espera Promedio")
                ax.set_title("Espera por Cliente (minutos)")
                ax.set_xlabel("Número de Cliente")
                ax.set_ylabel("Tiempo (min)")
                ax.legend()
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=frame_plot)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            except ValueError:
                messagebox.showerror("Error", "Ingresa números válidos en los campos.")

        btn_run = ttk.Button(panel_top, text="Ejecutar Simulación", command=simular_cola)
        btn_run.grid(row=3, column=0, columnspan=2, pady=5)

    # =========================================================================
    # 4.3.2 SISTEMAS DE INVENTARIOS (Modelo EOQ)
    # =========================================================================
    def crear_tab_inventarios(self):
        panel_top = ttk.LabelFrame(self.tab_inventarios, text=" Parámetros del Inventario ", padding=10)
        panel_top.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        ttk.Label(panel_top, text="Demanda Anual (D):").grid(row=0, column=0, sticky=tk.W, pady=2)
        entry_d = ttk.Entry(panel_top, width=15)
        entry_d.insert(0, "1000")
        entry_d.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(panel_top, text="Costo por Pedido (S $):").grid(row=1, column=0, sticky=tk.W, pady=2)
        entry_s = ttk.Entry(panel_top, width=15)
        entry_s.insert(0, "50")
        entry_s.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(panel_top, text="Costo Mantenimiento (H $/unid/año):").grid(row=2, column=0, sticky=tk.W, pady=2)
        entry_h = ttk.Entry(panel_top, width=15)
        entry_h.insert(0, "2.5")
        entry_h.grid(row=2, column=1, padx=5, pady=2)

        panel_bottom = ttk.Frame(self.tab_inventarios)
        panel_bottom.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        txt_res = tk.Text(panel_bottom, width=35, font=("Courier", 10))
        txt_res.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        frame_plot = ttk.LabelFrame(panel_bottom, text=" Curva de Costos ", padding=5)
        frame_plot.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def calcular_eoq():
            try:
                D = float(entry_d.get())
                S = float(entry_s.get())
                H = float(entry_h.get())

                q_opt = np.sqrt((2 * D * S) / H)
                num_pedidos = D / q_opt
                c_pedir = num_pedidos * S
                c_manten = (q_opt / 2) * H
                c_total = c_pedir + c_manten

                txt_res.delete("1.0", tk.END)
                res_str = (
                    f"=== MODELO EOQ ===\n\n"
                    f"Lote Óptimo (Q*):\n  {q_opt:.2f} unidades\n"
                    f"N° de Pedidos/Año:\n  {num_pedidos:.2f}\n"
                    f"Costo Pedir:\n  ${c_pedir:.2f}\n"
                    f"Costo Mantenimiento:\n  ${c_manten:.2f}\n"
                    f"--------------------\n"
                    f"COSTO TOTAL MÍNIMO:\n  ${c_total:.2f}\n"
                )
                txt_res.insert(tk.END, res_str)

                # Graficar curvas de costo
                for widget in frame_plot.winfo_children():
                    widget.destroy()

                q_vals = np.linspace(max(10, q_opt - 300), q_opt + 300, 200)
                costo_pedir = (D / q_vals) * S
                costo_manten = (q_vals / 2) * H
                costo_tot = costo_pedir + costo_manten

                fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
                ax.plot(q_vals, costo_tot, color="black", label="Costo Total", linewidth=2)
                ax.plot(q_vals, costo_pedir, color="blue", linestyle="--", label="Costo Pedido")
                ax.plot(q_vals, costo_manten, color="green", linestyle="--", label="Costo Mantenimiento")
                ax.axvline(q_opt, color="red", linestyle=":", label=f"Q*={q_opt:.1f}")
                ax.set_title("Optimización de Costos EOQ")
                ax.set_xlabel("Tamaño del Lote (Q)")
                ax.set_ylabel("Costo ($)")
                ax.legend(fontsize=8)
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=frame_plot)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            except ValueError:
                messagebox.showerror("Error", "Ingresa números válidos en los campos.")

        btn_run = ttk.Button(panel_top, text="Calcular EOQ", command=calcular_eoq)
        btn_run.grid(row=3, column=0, columnspan=2, pady=5)

    # =========================================================================
    # 4.4.1 PRUEBAS PARAMÉTRICAS (Prueba t de Student para 1 Muestra)
    # =========================================================================
    def crear_tab_parametrica(self):
        panel_top = ttk.LabelFrame(self.tab_parametrica, text=" Datos de la Muestra ", padding=10)
        panel_top.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        ttk.Label(panel_top, text="Media Poblacional Teórica (μ₀):").grid(row=0, column=0, sticky=tk.W, pady=2)
        entry_mu0 = ttk.Entry(panel_top, width=45)
        entry_mu0.insert(0, "70.0")
        entry_mu0.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(panel_top, text="Muestra (separada por comas):").grid(row=1, column=0, sticky=tk.W, pady=2)
        entry_data = ttk.Entry(panel_top, width=45)
        entry_data.insert(0, "72.5, 68.1, 75.0, 71.3, 69.8, 74.2, 73.0, 70.5")
        entry_data.grid(row=1, column=1, padx=5, pady=2)

        panel_bottom = ttk.Frame(self.tab_parametrica)
        panel_bottom.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        txt_res = tk.Text(panel_bottom, width=35, font=("Courier", 10))
        txt_res.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        frame_plot = ttk.LabelFrame(panel_bottom, text=" Distribución y Estadístico t ", padding=5)
        frame_plot.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        def ejecutar_prueba_t():
            try:
                mu0 = float(entry_mu0.get())
                raw_data = entry_data.get().split(",")
                datos = np.array([float(x.strip()) for x in raw_data if x.strip() != ""])

                n = len(datos)
                if n < 2:
                    messagebox.showerror("Error", "Ingresa al menos 2 datos.")
                    return

                # Cálculo de prueba t
                t_stat, p_val = stats.ttest_1samp(datos, mu0)
                media_m = np.mean(datos)
                std_m = np.std(datos, ddof=1)

                txt_res.delete("1.0", tk.END)
                res_str = (
                    f"=== PRUEBA t STUDENT ===\n\n"
                    f"Muestra (n): {n}\n"
                    f"Media Muestral: {media_m:.4f}\n"
                    f"Desv. Estándar: {std_m:.4f}\n"
                    f"--------------------\n"
                    f"Estadístico t:  {t_stat:.4f}\n"
                    f"p-valor:        {p_val:.6f}\n"
                    f"--------------------\n"
                    f"Decisión (α = 0.05):\n"
                )
                if p_val < 0.05:
                    res_str += "Se RECHAZA H₀:\nExiste diferencia significativa."
                else:
                    res_str += "NO se rechaza H₀:\nNo hay suficiente evidencia de diferencia."

                txt_res.insert(tk.END, res_str)

                # Graficar distribución t y valor observado
                for widget in frame_plot.winfo_children():
                    widget.destroy()

                df = n - 1
                x = np.linspace(-4, 4, 200)
                y = stats.t.pdf(x, df)

                fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
                ax.plot(x, y, color="black", label=f"t-Student (df={df})")
                ax.axvline(t_stat, color="red", linestyle="--", label=f"t obs = {t_stat:.2f}")

                # Límites críticos α = 0.05 dos colas
                t_crit = stats.t.ppf(0.975, df)
                ax.axvline(-t_crit, color="blue", linestyle=":", label="Límite Crítico")
                ax.axvline(t_crit, color="blue", linestyle=":")

                ax.set_title("Densidad t y Regiones Críticas")
                ax.set_xlabel("Valor t")
                ax.set_ylabel("Densidad")
                ax.legend(fontsize=7)
                fig.tight_layout()

                canvas = FigureCanvasTkAgg(fig, master=frame_plot)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            except ValueError:
                messagebox.showerror("Error", "Comprueba que la muestra contenga solo valores numéricos.")

        btn_run = ttk.Button(panel_top, text="Ejecutar Prueba t", command=ejecutar_prueba_t)
        btn_run.grid(row=2, column=0, columnspan=2, pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionSimulacion(root)
    root.mainloop()