import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import stats
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class AppANOVA:
    def __init__(self, root):
        self.root = root
        self.root.title("Prueba Paramétrica - ANOVA de 1 Factor")
        self.root.geometry("850x650")

        # Configuración del contenedor principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel Superior: Entradas de datos
        input_frame = ttk.LabelFrame(main_frame, text=" Datos de los Grupos (valores separados por comas) ", padding="10")
        input_frame.pack(fill=tk.X, side=tk.TOP, pady=5)

        ttk.Label(input_frame, text="Grupo A:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.entry_g1 = ttk.Entry(input_frame, width=65)
        self.entry_g1.insert(0, "85, 88, 90, 78, 82, 89, 84")
        self.entry_g1.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Grupo B:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.entry_g2 = ttk.Entry(input_frame, width=65)
        self.entry_g2.insert(0, "70, 72, 75, 68, 71, 73, 69")
        self.entry_g2.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Grupo C:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_g3 = ttk.Entry(input_frame, width=65)
        self.entry_g3.insert(0, "92, 94, 89, 95, 91, 93, 90")
        self.entry_g3.grid(row=2, column=1, padx=5, pady=2)

        btn_calcular = ttk.Button(input_frame, text="Ejecutar ANOVA", command=self.calcular_anova)
        btn_calcular.grid(row=3, column=0, columnspan=2, pady=10)

        # Panel Inferior dividido: Resultados (izq) y Gráfico (der)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Texto de Resultados
        result_frame = ttk.LabelFrame(bottom_frame, text=" Resultados Estadísticos ", padding="10")
        result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.txt_resultados = tk.Text(result_frame, width=35, font=("Courier", 10))
        self.txt_resultados.pack(fill=tk.BOTH, expand=True)

        # Área del Gráfico Matplotlib
        self.plot_frame = ttk.LabelFrame(bottom_frame, text=" Visualización de Medias ", padding="10")
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.canvas = None

    def parse_input(self, text):
        return [float(x.strip()) for x in text.split(",") if x.strip() != ""]

    def calcular_anova(self):
        try:
            # Parsear datos de entrada
            g1 = self.parse_input(self.entry_g1.get())
            g2 = self.parse_input(self.entry_g2.get())
            g3 = self.parse_input(self.entry_g3.get())

            if len(g1) < 2 or len(g2) < 2 or len(g3) < 2:
                messagebox.showerror("Error", "Cada grupo debe contener al menos 2 valores.")
                return

            # 1. Ejecutar ANOVA con SciPy
            f_stat, p_val = stats.f_oneway(g1, g2, g3)

            # 2. Desplegar texto de resultados
            self.txt_resultados.delete("1.0", tk.END)
            res_text = (
                f"--- PRUEBA ANOVA ---\n\n"
                f"Estadístico F: {f_stat:.4f}\n"
                f"p-valor:        {p_val:.6f}\n\n"
                f"Promedios:\n"
                f" - Grupo A: {np.mean(g1):.2f}\n"
                f" - Grupo B: {np.mean(g2):.2f}\n"
                f" - Grupo C: {np.mean(g3):.2f}\n\n"
                f"--------------------\n"
                f"Decisión (α = 0.05):\n"
            )
            if p_val < 0.05:
                res_text += "Se RECHAZA H₀:\nExisten diferencias significativas entre al menos dos grupos."
            else:
                res_text += "NO se rechaza H₀:\nNo hay evidencia suficiente de diferencia entre medias."

            self.txt_resultados.insert(tk.END, res_text)

            # 3. Dibujar/Actualizar Gráfico
            self.mostrar_grafico([g1, g2, g3])

        except ValueError:
            messagebox.showerror("Error de Formato", "Asegúrate de ingresar solo números separados por comas.")

    def mostrar_grafico(self, datos):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        ax.boxplot(datos, labels=["Grupo A", "Grupo B", "Grupo C"], patch_artist=True,
                   boxprops=dict(facecolor="#3498db", color="#2c3e50"))
        
        ax.set_title("Comparación entre Grupos")
        ax.set_ylabel("Valores Observados")
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AppANOVA(root)
    root.mainloop()