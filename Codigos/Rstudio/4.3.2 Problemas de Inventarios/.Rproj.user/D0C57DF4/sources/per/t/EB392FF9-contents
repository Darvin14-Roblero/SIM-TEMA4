library(shiny)
library(ggplot2)
library(dplyr)

# ----------------------------------------------------------------------
# 1. INTERFAZ DE USUARIO (UI)
# ----------------------------------------------------------------------
ui <- fluidPage(
  theme = bslib::bs_theme(bootswatch = "flatly"),
  titlePanel("Subtema 4.3.2 - Sistemas de Inventarios (Política s, Q en R)"),
  
  sidebarLayout(
    sidebarPanel(
      h4("Parámetros de la Política (s, Q)"),
      numericInput("inv_init", "Inventario Inicial:", value = 100, min = 10, step = 10),
      numericInput("s_reorden", "Punto de Reorden (s):", value = 30, min = 0, step = 5),
      numericInput("q_lote", "Lote de Pedido (Q):", value = 80, min = 10, step = 10),
      numericInput("lead_time", "Tiempo de Entrega (Días):", value = 3, min = 1, step = 1),
      numericInput("dias_sim", "Días a Simular:", value = 30, min = 10, step = 5),
      
      actionButton("run_inv", "Simular Inventario", class = "btn-primary w-100", icon = icon("boxes-stacked")),
      hr(),
      helpText("Demanda diaria ~ N(μ=15, σ=5). Evalúa el Fill Rate y la evolución del stock.")
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Gráfico de Comportamiento", 
                 br(),
                 plotOutput("plot_inventario", height = "380px"),
                 hr(),
                 verbatimTextOutput("resumen_inventario")),
        tabPanel("Tabla Diario", 
                 br(),
                 tableOutput("tabla_diaria"))
      )
    )
  )
)

# ----------------------------------------------------------------------
# 2. LÓGICA DEL SERVIDOR (SERVER)
# ----------------------------------------------------------------------
server <- function(input, output) {
  
  simular_sistema <- eventReactive(input$run_inv, {
    set.seed(123) # Para reproducibilidad
    
    inv_actual <- input$inv_init
    s <- input$s_reorden
    Q <- input$q_lote
    L <- input$lead_time
    dias <- input$dias_sim
    
    orden_en_transito <- 0
    dia_llegada <- -1
    
    registros <- vector("list", dias)
    
    total_demanda <- 0
    total_ventas <- 0
    total_faltantes <- 0
    total_ordenes <- 0
    
    for (d in 1:dias) {
      inv_comienzo <- inv_actual
      orden_recibida <- 0
      
      # Recepción de pedido programado
      if (orden_en_transito > 0 && d == dia_llegada) {
        inv_actual <- inv_actual + orden_en_transito
        orden_recibida <- orden_en_transito
        orden_en_transito <- 0
        dia_llegada <- -1
      }
      
      # Generar demanda aleatoria
      demanda <- max(0, round(rnorm(1, mean = 15, sd = 5)))
      total_demanda <- total_demanda + demanda
      
      # Atender demanda
      if (inv_actual >= demanda) {
        inv_actual <- inv_actual - demanda
        ventas <- demanda
        faltantes <- 0
      } else {
        ventas <- inv_actual
        faltantes <- demanda - inv_actual
        inv_actual <- 0
      }
      
      total_ventas <- total_ventas + ventas
      total_faltantes <- total_faltantes + faltantes
      
      # Evaluación de Reorden (Posición de inventario)
      posicion <- inv_actual + orden_en_transito
      if (posicion <= s && orden_en_transito == 0) {
        orden_en_transito <- Q
        dia_llegada <- d + L
        total_ordenes <- total_ordenes + 1
      }
      
      registros[[d]] <- data.frame(
        Dia = d,
        InvInicial = inv_comienzo,
        Demanda = demanda,
        InvFinal = inv_actual,
        Faltantes = faltantes,
        OrdenRecibida = orden_recibida,
        EnTransito = orden_en_transito
      )
    }
    
    df_res <- bind_rows(registros)
    
    list(
      df = df_res,
      s = s,
      dias = dias,
      total_demanda = total_demanda,
      total_ventas = total_ventas,
      total_faltantes = total_faltantes,
      total_ordenes = total_ordenes,
      inv_prom = mean(df_res$InvFinal),
      fill_rate = (total_ventas / total_demanda) * 100
    )
  }, ignoreNULL = FALSE)
  
  # Gráfico del nivel de inventario
  output$plot_inventario <- renderPlot({
    res <- simular_sistema()
    df <- res$df
    
    ggplot(df, aes(x = Dia, y = InvFinal)) +
      geom_line(color = "#2c3e50", size = 1.2) +
      geom_point(color = "#2980b9", size = 3) +
      geom_hline(yintercept = res$s, linetype = "dashed", color = "#e74c3c", size = 1) +
      annotate("text", x = 2, y = res$s + 4, label = paste("Punto de Reorden (s =", res$s, ")"), color = "#e74c3c") +
      labs(title = "Nivel de Inventario Físico al Final del Día",
           x = "Día",
           y = "Unidades en Almacén") +
      theme_minimal(base_size = 14)
  })
  
  # Tabla Diaria
  output$tabla_diaria <- renderTable({
    simular_sistema()$df
  }, striped = TRUE, hover = TRUE, bordered = TRUE)
  
  # Resumen
  output$resumen_inventario <- renderText({
    res <- simular_sistema()
    
    paste0(
      "--- RESUMEN DE EJECUCIÓN ---\n",
      "Días Simulados: ", res$dias, "\n",
      "Demanda Total Solicitada: ", res$total_demanda, " unidades\n",
      "Demanda Satisfecha: ", res$total_ventas, " unidades\n",
      "Faltantes (Ventas Perdidas): ", res$total_faltantes, " unidades\n",
      "Órdenes Colocadas (Q): ", res$total_ordenes, "\n",
      "Inventario Promedio Diario: ", round(res$inv_prom, 2), " unidades\n",
      "Nivel de Servicio (Fill Rate): ", round(res$fill_rate, 2), "%\n"
    )
  })
}

# ----------------------------------------------------------------------
# 3. LANZAMIENTO DE LA APP
# ----------------------------------------------------------------------
shinyApp(ui = ui, server = server)