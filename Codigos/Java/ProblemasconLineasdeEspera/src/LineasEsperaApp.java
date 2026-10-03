import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.LinkedList;
import java.util.PriorityQueue;
import java.util.Queue;
import java.util.Random;

public class LineasEsperaApp extends JFrame {

    private JTextField txtLambda, txtMu, txtTiempo;
    private JButton btnSimular;
    private JTable tablaMetricas;
    private DefaultTableModel modelMetricas;
    private JTextArea txtResultados;

    static class Evento implements Comparable<Evento> {
        double tiempo;
        String tipo; // "LLEGADA" o "SALIDA"

        public Evento(double tiempo, String tipo) {
            this.tiempo = tiempo;
            this.tipo = tipo;
        }

        @Override
        public int compareTo(Evento o) {
            return Double.compare(this.tiempo, o.tiempo);
        }
    }

    static class Cliente {
        int id;
        double tiempoLlegada;
        double tiempoInicioServicio;
        double tiempoSalida;

        public Cliente(int id, double tiempoLlegada) {
            this.id = id;
            this.tiempoLlegada = tiempoLlegada;
        }
    }

    public LineasEsperaApp() {
        setTitle("Subtema 4.3.1 - Problemas con Líneas de Espera (Sistema M/M/1)");
        setSize(850, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        // Panel de Controles
        JPanel panelInput = new JPanel(new GridLayout(2, 4, 10, 10));
        panelInput.setBorder(BorderFactory.createTitledBorder("Parámetros del Sistema de Colas"));

        panelInput.add(new JLabel("Tasa de Llegada λ (clientes/min):"));
        txtLambda = new JTextField("0.5"); // Ejemplo: 1 cliente cada 2 min
        panelInput.add(txtLambda);

        panelInput.add(new JLabel("Tasa de Servicio μ (clientes/min):"));
        txtMu = new JTextField("0.8"); // Ejemplo: atiende a 0.8 clientes por min
        panelInput.add(txtMu);

        panelInput.add(new JLabel("Tiempo de Simulación (min):"));
        txtTiempo = new JTextField("480.0"); // 8 horas de jornada
        panelInput.add(txtTiempo);

        btnSimular = new JButton("Simular Sistema M/M/1");
        btnSimular.setBackground(new Color(46, 204, 113));
        btnSimular.setForeground(Color.WHITE);
        panelInput.add(btnSimular);

        add(panelInput, BorderLayout.NORTH);

        // Panel Central - Tabla y Resumen
        String[] columnas = {"Métrica de Desempeño", "Valor Simulado", "Valor Teórico (M/M/1)"};
        modelMetricas = new DefaultTableModel(columnas, 0);
        tablaMetricas = new JTable(modelMetricas);

        txtResultados = new JTextArea(8, 50);
        txtResultados.setEditable(false);
        txtResultados.setFont(new Font("Monospaced", Font.PLAIN, 12));

        JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT,
                new JScrollPane(tablaMetricas),
                new JScrollPane(txtResultados));
        splitPane.setResizeWeight(0.5);

        add(splitPane, BorderLayout.CENTER);

        btnSimular.addActionListener(e -> ejecutarSimulacion());
    }

    private void ejecutarSimulacion() {
        try {
            double lambda = Double.parseDouble(txtLambda.getText());
            double mu = Double.parseDouble(txtMu.getText());
            double tiempoLimite = Double.parseDouble(txtTiempo.getText());

            if (lambda >= mu) {
                JOptionPane.showMessageDialog(this,
                        "Advertencia: λ debe ser menor que μ para evitar que la cola crezca indefinidamente (ρ < 1).",
                        "Sistema Inestable", JOptionPane.WARNING_MESSAGE);
            }

            Random random = new Random();
            PriorityQueue<Evento> fel = new PriorityQueue<>();
            Queue<Cliente> colaEspera = new LinkedList<>();

            double reloj = 0.0;
            boolean servidorOcupado = false;
            Cliente clienteEnServidor = null;

            int contadorClientes = 0;
            int clientesAtendidos = 0;

            double acumSumaTiemposEspera = 0.0;
            double acumSumaTiemposSistema = 0.0;
            double acumTiempoOcupadoServidor = 0.0;
            double ultimoTiempoCambioEstado = 0.0;
            double acumAreaLq = 0.0; // Para calcular Lq promedio

            // Primera llegada
            double tPrimeraLlegada = -Math.log(1 - random.nextDouble()) / lambda;
            fel.add(new Evento(tPrimeraLlegada, "LLEGADA"));

            while (!fel.isEmpty()) {
                Evento ev = fel.poll();
                if (ev.tiempo > tiempoLimite) break;

                // Actualizar acumulado de cola en el tiempo
                acumAreaLq += colaEspera.size() * (ev.tiempo - ultimoTiempoCambioEstado);
                if (servidorOcupado) {
                    acumTiempoOcupadoServidor += (ev.tiempo - ultimoTiempoCambioEstado);
                }
                ultimoTiempoCambioEstado = ev.tiempo;
                reloj = ev.tiempo;

                if (ev.tipo.equals("LLEGADA")) {
                    contadorClientes++;
                    Cliente nuevoCliente = new Cliente(contadorClientes, reloj);

                    if (!servidorOcupado) {
                        servidorOcupado = true;
                        clienteEnServidor = nuevoCliente;
                        clienteEnServidor.tiempoInicioServicio = reloj;

                        double tServicio = -Math.log(1 - random.nextDouble()) / mu;
                        fel.add(new Evento(reloj + tServicio, "SALIDA"));
                    } else {
                        colaEspera.add(nuevoCliente);
                    }

                    // Programar siguiente llegada
                    double tSiguienteLlegada = -Math.log(1 - random.nextDouble()) / lambda;
                    fel.add(new Evento(reloj + tSiguienteLlegada, "LLEGADA"));

                } else if (ev.tipo.equals("SALIDA")) {
                    clientesAtendidos++;
                    clienteEnServidor.tiempoSalida = reloj;

                    double tEspera = clienteEnServidor.tiempoInicioServicio - clienteEnServidor.tiempoLlegada;
                    double tSistema = clienteEnServidor.tiempoSalida - clienteEnServidor.tiempoLlegada;

                    acumSumaTiemposEspera += tEspera;
                    acumSumaTiemposSistema += tSistema;

                    if (!colaEspera.isEmpty()) {
                        clienteEnServidor = colaEspera.poll();
                        clienteEnServidor.tiempoInicioServicio = reloj;

                        double tServicio = -Math.log(1 - random.nextDouble()) / mu;
                        fel.add(new Evento(reloj + tServicio, "SALIDA"));
                    } else {
                        servidorOcupado = false;
                        clienteEnServidor = null;
                    }
                }
            }

            // Cálculo de Métricas Simuladas vs Teóricas
            double Wq_sim = acumSumaTiemposEspera / clientesAtendidos;
            double W_sim = acumSumaTiemposSistema / clientesAtendidos;
            double Lq_sim = acumAreaLq / reloj;
            double L_sim = Lq_sim + (acumTiempoOcupadoServidor / reloj);
            double rho_sim = acumTiempoOcupadoServidor / reloj;

            // Teoría M/M/1
            double rho_teo = lambda / mu;
            double L_teo = rho_teo / (1 - rho_teo);
            double Lq_teo = (rho_teo * rho_teo) / (1 - rho_teo);
            double W_teo = 1 / (mu - lambda);
            double Wq_teo = lambda / (mu * (mu - lambda));

            modelMetricas.setRowCount(0);
            modelMetricas.addRow(new Object[]{"Utilización del Servidor (ρ)", String.format("%.4f", rho_sim), String.format("%.4f", rho_teo)});
            modelMetricas.addRow(new Object[]{"Tiempo Medio en Cola Wq (min)", String.format("%.4f", Wq_sim), String.format("%.4f", Wq_teo)});
            modelMetricas.addRow(new Object[]{"Tiempo Medio en Sistema W (min)", String.format("%.4f", W_sim), String.format("%.4f", W_teo)});
            modelMetricas.addRow(new Object[]{"Clientes Promedio en Cola (Lq)", String.format("%.4f", Lq_sim), String.format("%.4f", Lq_teo)});
            modelMetricas.addRow(new Object[]{"Clientes Promedio en Sistema (L)", String.format("%.4f", L_sim), String.format("%.4f", L_teo)});

            txtResultados.setText(String.format(
                    "--- RESUMEN DE EJECUCIÓN ---\n" +
                            "Tiempo Simulado: %.2f min\n" +
                            "Total Clientes Ingresados: %d\n" +
                            "Total Clientes Atendidos: %d\n" +
                            "Clientes en Cola al Finalizar: %d\n",
                    reloj, contadorClientes, clientesAtendidos, colaEspera.size()
            ));

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor ingrese números válidos.", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new LineasEsperaApp().setVisible(true));
    }
}