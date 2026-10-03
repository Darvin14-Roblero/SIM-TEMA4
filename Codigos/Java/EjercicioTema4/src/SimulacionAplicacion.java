import javax.swing.*;
import java.awt.*;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.Queue;
import java.util.Random;

public class SimulacionAplicacion extends JFrame {

    public SimulacionAplicacion() {
        setTitle("Sistema Integrado de Simulación y Análisis");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // Crear contenedor con pestañas
        JTabbedPane tabbedPane = new JTabbedPane();

        // Agregar cada módulo/ejercicio
        tabbedPane.addTab("4.3.1 Líneas de Espera (M/M/1)", crearPanelLineasEspera());
        tabbedPane.addTab("4.3.2 Inventarios (EOQ Sim)", crearPanelInventarios());
        tabbedPane.addTab("4.4.1 Pruebas Paramétricas (t-Student)", crearPanelPruebaParametrica());

        add(tabbedPane);
    }

    // =========================================================================
    // 4.3.1 PROBLEMAS CON LÍNEAS DE ESPERA (Simulación M/M/1 con Monte Carlo)
    // =========================================================================
    private JPanel crearPanelLineasEspera() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JPanel pnlEntrada = new JPanel(new GridLayout(4, 2, 5, 5));
        JTextField txtTasaLlegada = new JTextField("4.0"); // clientes/hora (lambda)
        JTextField txtTasaServicio = new JTextField("6.0"); // clientes/hora (mu)
        JTextField txtNumClientes = new JTextField("100");

        pnlEntrada.add(new JLabel("Tasa de llegada (λ clientes/hora):"));
        pnlEntrada.add(txtTasaLlegada);
        pnlEntrada.add(new JLabel("Tasa de servicio (μ clientes/hora):"));
        pnlEntrada.add(txtTasaServicio);
        pnlEntrada.add(new JLabel("Número de clientes a simular:"));
        pnlEntrada.add(txtNumClientes);

        JButton btnSimular = new JButton("Ejecutar Simulación");
        pnlEntrada.add(new JLabel());
        pnlEntrada.add(btnSimular);

        JTextArea txtResultado = new JTextArea();
        txtResultado.setEditable(false);
        txtResultado.setFont(new Font("Monospaced", Font.PLAIN, 12));

        panel.add(pnlEntrada, BorderLayout.NORTH);
        panel.add(new JScrollPane(txtResultado), BorderLayout.CENTER);

        btnSimular.addActionListener(e -> {
            try {
                double lambda = Double.parseDouble(txtTasaLlegada.getText());
                double mu = Double.parseDouble(txtTasaServicio.getText());
                int n = Integer.parseInt(txtNumClientes.getText());

                if (lambda >= mu) {
                    JOptionPane.showMessageDialog(this, "Para estabilidad, la tasa de llegada (λ) debe ser menor a la de servicio (μ).", "Advertencia", JOptionPane.WARNING_MESSAGE);
                }

                Random rand = new Random();
                double reloj = 0.0;
                double tiempoEsperaTotal = 0.0;
                double tiempoSistemaTotal = 0.0;

                for (int i = 0; i < n; i++) {
                    // Generar tiempos exponenciales
                    double tLlegada = -Math.log(1 - rand.nextDouble()) / lambda;
                    double tServicio = -Math.log(1 - rand.nextDouble()) / mu;

                    reloj += tLlegada;
                    double tInicioServicio = Math.max(reloj, reloj + tiempoEsperaTotal);
                    double tEspera = tInicioServicio - reloj;
                    double tSistema = tEspera + tServicio;

                    tiempoEsperaTotal += tEspera;
                    tiempoSistemaTotal += tSistema;
                }

                StringBuilder sb = new StringBuilder();
                sb.append("=== RESULTADOS SIMULACIÓN LÍNEA DE ESPERA (M/M/1) ===\n\n");
                sb.append(String.format("Clientes simulados:            %d\n", n));
                sb.append(String.format("Tiempo promedio en cola (Wq):  %.4f horas (%.2f min)\n", (tiempoEsperaTotal / n), (tiempoEsperaTotal / n) * 60));
                sb.append(String.format("Tiempo promedio en sistema (W):%.4f horas (%.2f min)\n", (tiempoSistemaTotal / n), (tiempoSistemaTotal / n) * 60));
                sb.append(String.format("Factor de utilización (ρ):     %.2f%%\n", (lambda / mu) * 100));

                txtResultado.setText(sb.toString());
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Revisa los datos de entrada.", "Error", JOptionPane.ERROR_MESSAGE);
            }
        });

        return panel;
    }

    // =========================================================================
    // 4.3.2 PROBLEMAS CON SISTEMAS DE INVENTARIOS (Modelo EOQ y Simulación)
    // =========================================================================
    private JPanel crearPanelInventarios() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JPanel pnlEntrada = new JPanel(new GridLayout(4, 2, 5, 5));
        JTextField txtDemanda = new JTextField("1000");   // Demanda Anual (D)
        JTextField txtCostoPedido = new JTextField("50");  // Costo por Pedido (S)
        JTextField txtCostoManten = new JTextField("2.5"); // Costo Mantenimiento/unidad/año (H)

        pnlEntrada.add(new JLabel("Demanda Anual (D):"));
        pnlEntrada.add(txtDemanda);
        pnlEntrada.add(new JLabel("Costo de Pedir (S $):"));
        pnlEntrada.add(txtCostoPedido);
        pnlEntrada.add(new JLabel("Costo Mantenimiento (H $/unid/año):"));
        pnlEntrada.add(txtCostoManten);

        JButton btnCalcular = new JButton("Calcular Política de Inventario");
        pnlEntrada.add(new JLabel());
        pnlEntrada.add(btnCalcular);

        JTextArea txtResultado = new JTextArea();
        txtResultado.setEditable(false);
        txtResultado.setFont(new Font("Monospaced", Font.PLAIN, 12));

        panel.add(pnlEntrada, BorderLayout.NORTH);
        panel.add(new JScrollPane(txtResultado), BorderLayout.CENTER);

        btnCalcular.addActionListener(e -> {
            try {
                double D = Double.parseDouble(txtDemanda.getText());
                double S = Double.parseDouble(txtCostoPedido.getText());
                double H = Double.parseDouble(txtCostoManten.getText());

                // Lote Económico de Pedido (EOQ)
                double Q = Math.sqrt((2 * D * S) / H);
                double numPedidos = D / Q;
                double costoOrdenar = numPedidos * S;
                double costoMantener = (Q / 2) * H;
                double costoTotal = costoOrdenar + costoMantener;

                StringBuilder sb = new StringBuilder();
                sb.append("=== SISTEMA DE INVENTARIOS - MODELO EOQ ===\n\n");
                sb.append(String.format("Cantidad Óptima de Pedido (Q*): %.2f unidades\n", Q));
                sb.append(String.format("Número de pedidos al año:      %.2f pedidos\n", numPedidos));
                sb.append(String.format("Costo Anual de Ordenar:         $%.2f\n", costoOrdenar));
                sb.append(String.format("Costo Anual de Mantenimiento:   $%.2f\n", costoMantener));
                sb.append("--------------------------------------------------\n");
                sb.append(String.format("COSTO TOTAL OPTIMIZADO:         $%.2f\n", costoTotal));

                txtResultado.setText(sb.toString());
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Ingresa valores numéricos válidos.", "Error", JOptionPane.ERROR_MESSAGE);
            }
        });

        return panel;
    }

    // =========================================================================
    // 4.4.1 PRUEBAS PARAMÉTRICAS (Prueba t de Student para 1 Muestra)
    // =========================================================================
    private JPanel crearPanelPruebaParametrica() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        JPanel pnlEntrada = new JPanel(new GridLayout(3, 2, 5, 5));
        JTextField txtMu0 = new JTextField("70.0");
        JTextField txtMuestra = new JTextField("72.5, 68.1, 75.0, 71.3, 69.8, 74.2, 73.0, 70.5");

        pnlEntrada.add(new JLabel("Media Poblacional Teórica (μ₀):"));
        pnlEntrada.add(txtMu0);
        pnlEntrada.add(new JLabel("Muestra (datos sep. por comas):"));
        pnlEntrada.add(txtMuestra);

        JButton btnCalcular = new JButton("Ejecutar Prueba t");
        pnlEntrada.add(new JLabel());
        pnlEntrada.add(btnCalcular);

        JTextArea txtResultado = new JTextArea();
        txtResultado.setEditable(false);
        txtResultado.setFont(new Font("Monospaced", Font.PLAIN, 12));

        panel.add(pnlEntrada, BorderLayout.NORTH);
        panel.add(new JScrollPane(txtResultado), BorderLayout.CENTER);

        btnCalcular.addActionListener(e -> {
            try {
                double mu0 = Double.parseDouble(txtMu0.getText().trim());
                String[] tokens = txtMuestra.getText().split(",");
                double[] datos = Arrays.stream(tokens)
                        .map(String::trim)
                        .filter(s -> !s.isEmpty())
                        .mapToDouble(Double::parseDouble)
                        .toArray();

                int n = datos.length;
                if (n < 2) {
                    JOptionPane.showMessageDialog(this, "Debes ingresar al menos 2 datos.", "Error", JOptionPane.ERROR_MESSAGE);
                    return;
                }

                // Cálculos
                double suma = 0;
                for (double val : datos) suma += val;
                double media = suma / n;

                double sumaSq = 0;
                for (double val : datos) sumaSq += Math.pow(val - media, 2);
                double desvEstd = Math.sqrt(sumaSq / (n - 1));

                double se = desvEstd / Math.sqrt(n);
                double t = (media - mu0) / se;

                StringBuilder sb = new StringBuilder();
                sb.append("=== PRUEBA PARAMÉTRICA - t DE STUDENT (1 MUESTRA) ===\n\n");
                sb.append(String.format("Tamaño muestral (n):      %d\n", n));
                sb.append(String.format("Media Muestral (x̄):       %.4f\n", media));
                sb.append(String.format("Desviación Estándar (s):  %.4f\n", desvEstd));
                sb.append(String.format("Error Estándar (SE):      %.4f\n", se));
                sb.append("--------------------------------------------------\n");
                sb.append(String.format("Estadístico t Observado:  %.4f\n", t));
                sb.append(String.format("Grados de Libertad (df):  %d\n", n - 1));
                sb.append("--------------------------------------------------\n");
                sb.append("Decisión (α = 0.05, t_crit ≈ 2.365):\n");
                if (Math.abs(t) > 2.365) {
                    sb.append("--> Se RECHAZA H₀: La media difiere significativamente de μ₀.");
                } else {
                    sb.append("--> NO se rechaza H₀: No hay evidencia suficiente de diferencia.");
                }

                txtResultado.setText(sb.toString());
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Formato de datos no válido.", "Error", JOptionPane.ERROR_MESSAGE);
            }
        });

        return panel;
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SimulacionAplicacion().setVisible(true));
    }
}