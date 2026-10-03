import random
import math
import tkinter as tk
from tkinter import ttk, messagebox


class SimuladorMM1:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtema 4.3.1 - Líneas de Espera (Sistema M/M/1 en Python)")
        self.root.geometry("850x580")

        # --- Panel Superior: Parámetros ---
        frame_params = ttk.LabelFrame(self.root, text="Parámetros del Sistema M/M/1", padding=10)
        frame_params.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_params, text="Tasa Llegada λ (clientes/min):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_lambda = ttk.Entry(frame_params, width=8)
        self.entry_lambda.insert(0, "0.5")
        self.entry_lambda.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_params, text="Tasa Servicio μ (clientes/min):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_mu = ttk.Entry(frame_params, width=8)
        self.entry_mu.insert(0, "0.8")
        self.entry_mu.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_params, text="Tiempo Simulación (min):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_tiempo = ttk.Entry(frame_params, width=8)
        self.entry_tiempo.insert(0, "480.0")
        self.entry_tiempo.grid(row=0, column=5, padx=5, pady=5)

        btn_ejecutar = ttk.Button(frame_params, text="Simular Sistema", command=self.ejecutar_simulacion)
        btn_ejecutar.grid(row=0, column=6, padx=10, pady=5)

        # --- Panel Central: Tabla Comparativa ---
        frame_tabla = ttk.LabelFrame(self.root, text="Comparativa: Simulación vs. Teoría Analítica M/M/1", padding=10)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = ("Métrica de Desempeño", "Valor Simulado", "Valor Teórico (M/M/1)")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)
        
        self.tree.heading("Métrica de Desempeño", text="Métrica de Desempeño")
        self.tree.column("Métrica de Desempeño", anchor="w", width=320)
        
        self.tree.heading("Valor Simulado", text="Valor Simulado")
        self.tree.column("Valor Simulado", anchor="center", width=200)
        
        self.tree.heading("Valor Teórico (M/M/1)", text="Valor Teórico (M/M/1)")
        self.tree.column("Valor Teórico (M/M/1)", anchor="center", width=200)

        self.tree.pack(fill="both", expand=True)

        # --- Panel Inferior: Resumen de Ejecución ---
        frame_resumen = ttk.LabelFrame(self.root, text="Resumen de Ejecución", padding=10)
        frame_resumen.pack(fill="x", padx=10, pady=5)

        self.lbl_resumen = ttk.Label(frame_resumen, text="Ingrese los parámetros y haga clic en 'Simular Sistema'.", font=("Consolas", 10))
        self.lbl_resumen.pack(anchor="w")

    def generar_exp(self, tasa):
        return -math.log(1 - random.random()) / tasa

    def ejecutar_simulacion(self):
        try:
            lam = float(self.entry_lambda.get())
            mu = float(self.entry_mu.get())
            t_limite = float(self.entry_tiempo.get())

            if lam >= mu:
                messagebox.showwarning("Advertencia", "La tasa de llegada (λ) debe ser menor a la tasa de servicio (μ) para estabilidad (ρ < 1).")

            reloj = 0.0
            servidor_ocupado = False
            cola_espera = []  # Almacena los tiempos de llegada de los clientes en cola

            clientes_ingresados = 0
            clientes_atendidos = 0

            sum_espera_cola = 0.0
            sum_tiempo_sistema = 0.0
            tiempo_servidor_ocupado = 0.0
            ultimo_evento_tiempo = 0.0
            area_lq = 0.0

            fel = []  # Lista de eventos futuros (tiempo, tipo, t_llegada)

            # Primera llegada
            fel.append((self.generar_exp(lam), "LLEGADA", 0.0))

            while fel:
                fel.sort(key=lambda x: x[0])
                t_evento, tipo_evento, t_llegada_cliente = fel.pop(0)

                if t_evento > t_limite:
                    break

                # Acumuladores integrales
                dt = t_evento - ultimo_evento_tiempo
                area_lq += len(cola_espera) * dt
                if servidor_ocupado:
                    tiempo_servidor_ocupado += dt

                ultimo_evento_tiempo = t_evento
                reloj = t_evento

                if tipo_evento == "LLEGADA":
                    clientes_ingresados += 1
                    if not servidor_ocupado:
                        servidor_ocupado = True
                        t_servicio = self.generar_exp(mu)
                        fel.append((reloj + t_servicio, "SALIDA", reloj))
                    else:
                        cola_espera.append(reloj)

                    # Siguiente llegada
                    fel.append((reloj + self.generar_exp(lam), "LLEGADA", 0.0))

                elif tipo_evento == "SALIDA":
                    clientes_atendidos += 1
                    t_espera = reloj - t_servicio_inicio if 't_servicio_inicio' in locals() else 0.0
                    
                    # Tiempo de permanencia total
                    t_espera_cola = reloj - t_llegada_cliente - (reloj - t_llegada_cliente) # Atendido inmediatamente o tras cola
                    sum_tiempo_sistema += (reloj - t_llegada_cliente)

                    if cola_espera:
                        t_llegada_siguiente = cola_espera.pop(0)
                        sum_espera_cola += (reloj - t_llegada_siguiente)
                        t_servicio = self.generar_exp(mu)
                        fel.append((reloj + t_servicio, "SALIDA", t_llegada_siguiente))
                    else:
                        servidor_ocupado = False

            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)

            if clientes_atendidos > 0:
                # Métricas Simuladas
                Wq_sim = sum_espera_cola / clientes_atendidos
                W_sim = sum_tiempo_sistema / clientes_atendidos
                Lq_sim = area_lq / reloj
                rho_sim = tiempo_servidor_ocupado / reloj
                L_sim = Lq_sim + rho_sim

                # Métricas Teóricas
                rho_teo = lam / mu
                L_teo = rho_teo / (1 - rho_teo)
                Lq_teo = (rho_teo ** 2) / (1 - rho_teo)
                W_teo = 1 / (mu - lam)
                Wq_teo = lam / (mu * (mu - lam))

                metricas = [
                    ("Factor de Utilización (ρ)", f"{rho_sim:.4f}", f"{rho_teo:.4f}"),
                    ("Tiempo Medio en Cola Wq (min)", f"{Wq_sim:.4f}", f"{Wq_teo:.4f}"),
                    ("Tiempo Medio en Sistema W (min)", f"{W_sim:.4f}", f"{W_teo:.4f}"),
                    ("Clientes Promedio en Cola (Lq)", f"{Lq_sim:.4f}", f"{Lq_teo:.4f}"),
                    ("Clientes Promedio en Sistema (L)", f"{L_sim:.4f}", f"{L_teo:.4f}")
                ]

                for row in metricas:
                    self.tree.insert("", "end", values=row)

                self.lbl_resumen.config(
                    text=f"Tiempo Simulado: {reloj:.2f} min | Clientes Ingresados: {clientes_ingresados} | Clientes Atendidos: {clientes_atendidos} | En Cola Final: {len(cola_espera)}"
                )

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorMM1(root)
    root.mainloop()