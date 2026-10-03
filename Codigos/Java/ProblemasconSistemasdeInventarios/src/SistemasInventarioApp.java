import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class SistemasInventarioApp extends JFrame {

    private JTextField txtInventarioInicial, txtReorden, txtLoteQ, txtLeadTime, txtDias;
    private JButton btnSimular;
    private JTable tablaRegistro;
    private DefaultTableModel modelTabla;
    private JTextArea txtResumen;

    static class RegistroDia {
        int dia;
        int inventarioInicial;
        int demanda;
        int inventarioFinal;
        int faltantes;
        int ordenRecibida;
        String estadoOrden;

        public RegistroDia(int dia, int inventarioInicial, int demanda, int inventarioFinal, int faltantes, int ordenRecibida, String estadoOrden) {
            this.dia = dia;
            this.inventarioInicial = inventarioInicial;
            this.demanda = demanda;
            this.inventarioFinal = inventarioFinal;
            this.faltantes = faltantes;
            this.ordenRecibida = ordenRecibida;
            this.estadoOrden = estadoOrden;
        }
    }

    public SistemasInventarioApp() {
        setTitle("Subtema 4.3.2 - Sistemas de Inventarios (Política s, Q en Java)");
        setSize(900, 650);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        // Panel de Controles
        JPanel panelInput = new JPanel(new GridLayout(3, 4, 10, 10));
        panelInput.setBorder(BorderFactory.createTitledBorder("Parámetros del Sistema de Inventario (s, Q)"));

        panelInput.add(new JLabel("Inventario Inicial:"));
        txtInventarioInicial = new JTextField("100");
        panelInput.add(txtInventarioInicial);

        panelInput.add(new JLabel("Punto de Reorden (s):"));
        txtReorden = new JTextField("30");
        panelInput.add(txtReorden);

        panelInput.add(new JLabel("Cantidad a Pedir (Q):"));
        txtLoteQ = new JTextField("80");
        panelInput.add(txtLoteQ);

        panelInput.add(new JLabel("Tiempo de Entrega (Días):"));
        txtLeadTime = new JTextField("3");
        panelInput.add(txtLeadTime);

        panelInput.add(new JLabel("Días a Simular:"));
        txtDias = new JTextField("30");
        panelInput.add(txtDias);

        btnSimular = new JButton("Simular Inventario");
        btnSimular.setBackground(new Color(52, 152, 219));
        btnSimular.setForeground(Color.WHITE);
        panelInput.add(btnSimular);

        add(panelInput, BorderLayout.NORTH);

        // Panel Central - Tabla y Resumen
        String[] columnas = {"Día", "Inv. Inicial", "Demanda", "Inv. Final", "Faltantes", "Orden Recibida", "Estado de Pedido"};
        modelTabla = new DefaultTableModel(columnas, 0);
        tablaRegistro = new JTable(modelTabla);

        txtResumen = new JTextArea(6, 50);
        txtResumen.setEditable(false);
        txtResumen.setFont(new Font("Monospaced", Font.PLAIN, 12));

        JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT,
                new JScrollPane(tablaRegistro),
                new JScrollPane(txtResumen));
        splitPane.setResizeWeight(0.65);

        add(splitPane, BorderLayout.CENTER);

        btnSimular.addActionListener(e -> ejecutarSimulacion());
    }

    private void ejecutarSimulacion() {
        try {
            int invInicial = Integer.parseInt(txtInventarioInicial.getText());
            int s = Integer.parseInt(txtReorden.getText());
            int Q = Integer.parseInt(txtLoteQ.getText());
            int leadTime = Integer.parseInt(txtLeadTime.getText());
            int totalDias = Integer.parseInt(txtDias.getText());

            Random random = new Random();
            modelTabla.setRowCount(0);

            int inventarioActual = invInicial;
            int ordenEnTransito = 0;
            int diaLlegadaOrden = -1;

            int totalDemanda = 0;
            int totalVentas = 0;
            int totalFaltantes = 0;
            int totalOrdenesColocadas = 0;
            double sumaInventarioDiario = 0;

            for (int dia = 1; dia <= totalDias; dia++) {
                int invComienzoDia = inventarioActual;
                int ordenRecibidaHoy = 0;
                String estadoPedidoStr = "SIN PEDIDO";

                // Check si llega pedido hoy
                if (ordenEnTransito > 0 && dia == diaLlegadaOrden) {
                    inventarioActual += ordenEnTransito;
                    ordenRecibidaHoy = ordenEnTransito;
                    ordenEnTransito = 0;
                    diaLlegadaOrden = -1;
                    estadoPedidoStr = "PEDIDO RECIBIDO";
                }

                // Generar demanda diaria (Distribución Poisson / Normal aproximada via Gaussiana)
                int demandaHoy = Math.max(0, (int) Math.round(15 + random.nextGaussian() * 5)); // Media 15, Desv 5
                totalDemanda += demandaHoy;

                int faltantesHoy = 0;
                if (inventarioActual >= demandaHoy) {
                    inventarioActual -= demandaHoy;
                    totalVentas += demandaHoy;
                } else {
                    totalVentas += inventarioActual;
                    faltantesHoy = demandaHoy - inventarioActual;
                    inventarioActual = 0;
                    totalFaltantes += faltantesHoy;
                }

                // Evaluación de Reorden al final del día (Posición de inventario)
                int posicionInventario = inventarioActual + ordenEnTransito;

                if (posicionInventario <= s && ordenEnTransito == 0) {
                    ordenEnTransito = Q;
                    diaLlegadaOrden = dia + leadTime;
                    totalOrdenesColocadas++;
                    estadoPedidoStr = (ordenRecibidaHoy > 0) ? "RECIBIDO Y REORDENADO" : "ORDEN COLOCADA (Llega día " + diaLlegadaOrden + ")";
                }

                sumaInventarioDiario += inventarioActual;

                modelTabla.addRow(new Object[]{
                        dia,
                        invComienzoDia,
                        demandaHoy,
                        inventarioActual,
                        faltantesHoy,
                        ordenRecibidaHoy,
                        estadoPedidoStr
                });
            }

            double invPromedio = sumaInventarioDiario / totalDias;
            double nivelServicio = ((double) totalVentas / totalDemanda) * 100.0;

            txtResumen.setText(String.format(
                    "--- RESUMEN DE LA SIMULACIÓN DE INVENTARIO ---\n" +
                            "Días Simulados: %d\n" +
                            "Demanda Total Solicitada: %d unidades\n" +
                            "Demanda Total Satisfecha: %d unidades\n" +
                            "Faltantes Totales (Ventas Perdidas): %d unidades\n" +
                            "Órdenes de Reabastecimiento Emitidas: %d\n" +
                            "Inventario Promedio Diario: %.2f unidades\n" +
                            "Nivel de Servicio (Fill Rate): %.2f%%\n",
                    totalDias, totalDemanda, totalVentas, totalFaltantes, totalOrdenesColocadas, invPromedio, nivelServicio
            ));

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Por favor ingrese valores numéricos enteros válidos.", "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SistemasInventarioApp().setVisible(true));
    }
}