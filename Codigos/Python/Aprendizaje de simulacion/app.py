import random
import math
import tkinter as tk
from tkinter import ttk, messagebox


class SimuladorDESBase:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Eventos Discretos - Tema 4.2 (Python)")
        self.root.geometry("850x600")

        # --- Panel Superior (Parámetros) ---
        frame_params = ttk.LabelFrame(self.root, text="Parámetros de Simulación", padding=10)
        frame_params.pack(fill="x", padx=10, pady=5)

        ttk.Label(frame_params, text="T. Medio Llegadas (min):").grid(row=0, column=0, padx=5, pady=5)
        self.entry_llegadas = ttk.Entry(frame_params, width=8)
        self.entry_llegadas.insert(0, "3.0")
        self.entry_llegadas.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_params, text="T. Medio Servicio (min):").grid(row=0, column=2, padx=5, pady=5)
        self.entry_servicio = ttk.Entry(frame_params, width=8)
        self.entry_servicio.insert(0, "2.0")
        self.entry_servicio.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_params, text="Tiempo Total (min):").grid(row=0, column=4, padx=5, pady=5)
        self.entry_tiempo = ttk.Entry(frame_params, width=8)
        self.entry_tiempo.insert(0, "60.0")
        self.entry_tiempo.grid(row=0, column=5, padx=5, pady=5)

        btn_ejecutar = ttk.Button(frame_params, text="Ejecutar Simulación", command=self.ejecutar_simulacion)
        btn_ejecutar.grid(row=0, column=6, padx=10, pady=5)

        # --- Panel Central (Tabla de Registro de Eventos) ---
        frame_tabla = ttk.LabelFrame(self.root, text="Traza de Ejecución (Event Trace)", padding=10)
        frame_tabla.pack(fill="both", expand=True, padx=10, pady=5)

        columnas = ("Reloj (min)", "Evento", "Cola de Espera", "Estado Servidor", "Atendidos")
        self.tree = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=15)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=130)

        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Panel Inferior (Barra de Estado) ---
        self.lbl_estado = ttk.Label(self.root, text="Ingrese los parámetros y presione 'Ejecutar Simulación'.", font=("Arial", 10, "bold"))
        self.lbl_estado.pack(fill="x", padx=10, pady=5)

    def generar_exponencial(self, media):
        return -media * math.log(1 - random.random())

    def ejecutar_simulacion(self):
        try:
            m_llegadas = float(self.entry_llegadas.get())
            m_servicio = float(self.entry_servicio.get())
            t_limite = float(self.entry_tiempo.get())

            # Limpiar tabla previa
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Variables del Motor DES
            reloj = 0.0
            cola = 0
            servidor_ocupado = False
            atendidos = 0

            # Lista de Eventos Futuros (FEL): lista de tuplas (tiempo, tipo)
            fel = []

            # Primer evento de llegada
            primera_llegada = self.generar_exponencial(m_llegadas)
            fel.append((primera_llegada, "LLEGADA"))

            while fel:
                # Ordenar FEL por tiempo (Next-Event Time Advance)
                fel.sort(key=lambda x: x[0])
                t_evento, tipo_evento = fel.pop(0)

                if t_evento > t_limite:
                    break

                reloj = t_evento

                if tipo_evento == "LLEGADA":
                    if servidor_ocupado:
                        cola += 1
                    else:
                        servidor_ocupado = True
                        t_atencion = self.generar_exponencial(m_servicio)
                        fel.append((reloj + t_atencion, "FIN_SERVICIO"))

                    # Programar siguiente llegada
                    prox_llegada = reloj + self.generar_exponencial(m_llegadas)
                    fel.append((prox_llegada, "LLEGADA"))

                elif tipo_evento == "FIN_SERVICIO":
                    atendidos += 1
                    if cola > 0:
                        cola -= 1
                        t_atencion = self.generar_exponencial(m_servicio)
                        fel.append((reloj + t_atencion, "FIN_SERVICIO"))
                    else:
                        servidor_ocupado = False

                # Insertar fila en la interfaz gráfica
                estado_str = "OCUPADO" if servidor_ocupado else "LIBRE"
                self.tree.insert("", "end", values=(f"{reloj:.2f}", tipo_evento, cola, estado_str, atendidos))

            self.lbl_estado.config(text=f"Simulación finalizada. Tiempo transcurrido: {reloj:.2f} min | Clientes Atendidos: {atendidos}")

        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorDESBase(root)
    root.mainloop()