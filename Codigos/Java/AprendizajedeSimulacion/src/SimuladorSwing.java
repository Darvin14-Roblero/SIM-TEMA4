import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.PriorityQueue;
import java.util.Random;

public class SimuladorSwing extends JFrame {

    // --- Componentes de la Interfaz ---
    private JTextField txtLlegadas, txtServicio, txtTiempoTotal;
    private JButton btnIniciar;
    private JTable tablaResultados;
    private DefaultTableModel modelTabla;
    private JLabel lblEstado;

    // --- Variables de la Simulación ---
    private Random random = new Random();

    // Clase Evento para la Lista de Eventos (FEL)
    static class Evento implements Comparable<Evento> {
        double tiempo;
        String tipo; // "LLEGADA" o "FIN_SERVICIO"

        public Evento(double tiempo, String tipo) {
            this.tiempo = tiempo;
            this.tipo = tipo;
        }

        @Override
        public int compareTo(Evento o) {
            return Double.compare(this.tiempo, o.tiempo);
        }
    }

    public SimuladorSwing() {
        // Configuración de la ventana principal
        setTitle("Simulador de Eventos Discretos (DES) - Tema 4.2");
        setSize(850, 550);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        // 1. Panel Superior (Parámetros)
        JPanel panelControles = new JPanel(new GridLayout(2, 4, 10, 10));
        panelControles.setBorder(BorderFactory.createTitledBorder("Parámetros de Simulación"));

        panelControles.add(new JLabel("T. Medio entre Llegadas (min):"));
        txtLlegadas = new JTextField("3.0");
        panelControles.add(txtLlegadas);

        panelControles.add(new JLabel("T. Medio de Servicio (min):"));
        txtServicio = new JTextField("2.0");
        panelControles.add(txtServicio);

        panelControles.add(new JLabel("Tiempo Total a Simular (min):"));
        txtTiempoTotal = new JTextField("30.0");
        panelControles.add(txtTiempoTotal);

        btnIniciar = new JButton("Ejecutar Simulación");
        btnIniciar.setBackground(new Color(41, 128, 185));
        btnIniciar.setForeground(Color.WHITE);
        btnIniciar.setFocusPainted(false);
        panelControles.add(btnIniciar);

        add(panelControles, BorderLayout.NORTH);

        // 2. Panel Central (Tabla de Registro de Eventos)
        String[] columnas = {"Reloj (min)", "Evento", "Cola de Espera", "Estado Servidor", "Atendidos"};
        modelTabla = new DefaultTableModel(columnas, 0);
        tablaResultados = new JTable(modelTabla);
        JScrollPane scrollTabla = new JScrollPane(tablaResultados);
        scrollTabla.setBorder(BorderFactory.createTitledBorder("Traza de Ejecución (Event Trace)"));
        add(scrollTabla, BorderLayout.CENTER);

        // 3. Panel Inferior (Barra de Estado / Resumen)
        JPanel panelEstado = new JPanel(new FlowLayout(FlowLayout.LEFT));
        lblEstado = new JLabel("Ingrese los parámetros y presione 'Ejecutar Simulación'.");
        lblEstado.setFont(new Font("SansSerif", Font.BOLD, 12));
        panelEstado.add(lblEstado);
        add(panelEstado, BorderLayout.SOUTH);

        // Evento del Botón
        btnIniciar.addActionListener(e -> ejecutarSimulacion());
    }

    private void ejecutarSimulacion() {
        try {
            // Leer parámetros
            double mediaLlegadas = Double.parseDouble(txtLlegadas.getText());
            double mediaServicio = Double.parseDouble(txtServicio.getText());
            double tiempoLimite = Double.parseDouble(txtTiempoTotal.getText());

            // Limpiar tabla anterior
            modelTabla.setRowCount(0);

            // Variables de Estado
            double reloj = 0.0;
            int cola = 0;
            boolean servidorOcupado = false;
            int clientesAtendidos = 0;

            // PriorityQueue funciona como la Lista de Eventos Futuros (FEL)
            PriorityQueue<Evento> fel = new PriorityQueue<>();

            // Agregamos el primer evento de llegada
            double primeraLlegada = generarExponencial(mediaLlegadas);
            fel.add(new Evento(primeraLlegada, "LLEGADA"));

            // Bucle principal del Motor de Simulación (DES)
            while (!fel.isEmpty()) {
                Evento eventoActual = fel.poll();

                if (eventoActual.tiempo > tiempoLimite) {
                    break; // Finalizar si supera el tiempo total
                }

                reloj = eventoActual.tiempo;

                if (eventoActual.tipo.equals("LLEGADA")) {
                    if (servidorOcupado) {
                        cola++;
                    } else {
                        servidorOcupado = true;
                        double tiempoAtencion = generarExponencial(mediaServicio);
                        fel.add(new Evento(reloj + tiempoAtencion, "FIN_SERVICIO"));
                    }
                    // Programar la siguiente llegada
                    double proximaLlegada = reloj + generarExponencial(mediaLlegadas);
                    fel.add(new Evento(proximaLlegada, "LLEGADA"));

                } else if (eventoActual.tipo.equals("FIN_SERVICIO")) {
                    clientesAtendidos++;
                    if (cola > 0) {
                        cola--;
                        double tiempoAtencion = generarExponencial(mediaServicio);
                        fel.add(new Evento(reloj + tiempoAtencion, "FIN_SERVICIO"));
                    } else {
                        servidorOcupado = false;
                    }
                }

                // Registrar el evento en la interfaz gráfica
                modelTabla.addRow(new Object[]{
                        String.format("%.2f", reloj),
                        eventoActual.tipo,
                        cola,
                        servidorOcupado ? "OCUPADO" : "LIBRE",
                        clientesAtendidos
                });
            }

            lblEstado.setText(String.format("Simulación finalizada. Tiempo transcurrido: %.2f min | Total atendidos: %d", reloj, clientesAtendidos));

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor ingrese valores numéricos válidos.", "Error de Input", JOptionPane.ERROR_MESSAGE);
        }
    }

    // Generador de variables aleatorias exponenciales
    private double generarExponencial(double media) {
        return -media * Math.log(1 - random.nextDouble());
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            new SimuladorSwing().setVisible(true);
        });
    }
}