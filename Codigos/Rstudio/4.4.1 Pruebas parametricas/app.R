# ----------------------------------------------------------
# Ejemplo de Prueba Paramétrica: Prueba t para 2 Muestras
# ----------------------------------------------------------

# 1. Generar o cargar datos de ejemplo (dos grupos de puntajes)
set.seed(123) # Para reproducibilidad

grupo_A <- rnorm(n = 30, mean = 75, sd = 10)  # Métodos de estudio A
grupo_B <- rnorm(n = 30, mean = 82, sd = 10)  # Métodos de estudio B

# Crear un dataframe
datos <- data.frame(
  Puntaje = c(grupo_A, grupo_B),
  Grupo = rep(c("Método A", "Método B"), each = 30)
)

# 2. Verificación del supuesto paramétrico (Prueba de Normalidad)
# H0: Los datos siguen una distribución normal
shapiro_A <- shapiro.test(grupo_A)
shapiro_B <- shapiro.test(grupo_B)

cat("--- VERIFICACIÓN DE NORMALIDAD (Shapiro-Wilk) ---\n")
cat("Grupo A (p-valor):", round(shapiro_A$p.value, 4), "\n")
cat("Grupo B (p-valor):", round(shapiro_B$p.value, 4), "\n\n")

# 3. Ejecución de la Prueba Paramétrica (Prueba t de Student)
# H0: La media del Método A es igual a la media del Método B
resultado_t <- t.test(Puntaje ~ Grupo, data = datos, var.equal = TRUE)

# Mostrar resultados detallados en consola
print(resultado_t)

# 4. Visualización gráfica de los datos
par(mfrow = c(1, 2)) # Dividir el panel de gráficos en 1 fila x 2 columnas

# Gráfico 1: Diagrama de cajas (Boxplot) para comparar los grupos
boxplot(Puntaje ~ Grupo, data = datos,
        col = c("#3498db", "#2ecc71"),
        main = "Comparación de Grupos",
        ylab = "Puntaje Obtenido",
        xlab = "Estrategia")

# Gráfico 2: Q-Q Plot para evaluar normalidad global
qqnorm(datos$Puntaje, main = "Q-Q Plot de Normalidad", col = "#e74c3c", pch = 19)
qqline(datos$Puntaje, col = "black", lwd = 2)

par(mfrow = c(1, 1)) # Restaurar panel gráfico