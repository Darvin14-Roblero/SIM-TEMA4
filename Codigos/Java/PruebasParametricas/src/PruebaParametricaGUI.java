import javax.swing.*;
import java.awt.*;
import java.util.Arrays;

public class PruebaParametricaGUI extends JFrame {

    private JTextField txtValorPoblacional;
    private JTextArea txtDatos;
    private JTextArea txtResultado;

    public PruebaParametricaGUI() {
        setTitle("Prueba Paramétrica - t de Student (1 Muestra)");
        setSize(550, 480);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout(10, 10));

        // Panel superior (Entradas)
        JPanel panelEntrada = new JPanel(new GridLayout(3, 2, 8, 8));
        panelEntrada.setBorder(BorderFactory.createTitledBorder("Parámetros de Entrada"));

        panelEntrada.add(new JLabel("Media Teórica / Poblacional (μ₀):"));
        txtValorPoblacional = new JTextField("70.0");
        panelEntrada.add(txtValorPoblacional);

        panelEntrada.add(new JLabel("Muestra (separada por comas):"));
        txtDatos = new JTextArea("72.5, 68.1, 75.0, 71.3, 69.8, 74.2, 73.0, 70.5", 2, 20);
        txtDatos.setLineWrap(true);
        panelEntrada.add(new JScrollPane(txtDatos));

        JButton btnCalcular = new JButton("Ejecutar Prueba t");
        btnCalcular.setBackground(new Color(41, 128, 185));
        btnCalcular.setForeground(Color.WHITE);
        panelEntrada.add(new JLabel()); // Espacio en blanco
        panelEntrada.add(btnCalcular);

        add(panelEntrada, BorderLayout.NORTH);

        // Panel inferior (Resultados)
        JPanel panelResultado = new JPanel(new BorderLayout());
        panelResultado.setBorder(BorderFactory.createTitledBorder("Resultados del Análisis"));

        txtResultado = new JTextArea();
        txtResultado.setEditable(false);
        txtResultado.setFont(new Font("Monospaced", Font.PLAIN, 13));
        panelResultado.add(new JScrollPane(txtResultado), BorderLayout.CENTER);

        add(panelResultado, BorderLayout.CENTER);

        // Evento del botón
        btnCalcular.addActionListener(e -> calcularPruebaT());
    }

    private void calcularPruebaT() {
        try {
            double mu0 = Double.parseDouble(txtValorPoblacional.getText().trim());
            String[] tokens = txtDatos.getText().split(",");

            double[] muestra = Arrays.stream(tokens)
                    .map(String::trim)
                    .filter(s -> !s.isEmpty())
                    .mapToDouble(Double::parseDouble)
                    .toArray();

            int n = muestra.length;
            if (n < 2) {
                JOptionPane.showMessageDialog(this, "Ingresa al menos 2 datos.", "Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            // 1. Media muestral (x̄)
            double suma = 0;
            for (double val : muestra) suma += val;
            double media = suma / n;

            // 2. Desviación estándar muestral (s)
            double sumaCuadrados = 0;
            for (double val : muestra) {
                sumaCuadrados += Math.pow(val - media, 2);
            }
            double desviacionEstandar = Math.sqrt(sumaCuadrados / (n - 1));

            // 3. Error estándar de la media (SE)
            double errorEstandar = desviacionEstandar / Math.sqrt(n);

            // 4. Estadística t
            double estadisticoT = (media - mu0) / errorEstandar;

            // Mostrar resultados
            StringBuilder sb = new StringBuilder();
            sb.append(String.format("Tamaño de la Muestra (n):  %d\n", n));
            sb.append(String.format("Media de la Muestra (x̄):  %.4f\n", media));
            sb.append(String.format("Desviación Estándar (s):   %.4f\n", desviacionEstandar));
            sb.append(String.format("Error Estándar (SE):       %.4f\n", errorEstandar));
            sb.append("------------------------------------------\n");
            sb.append(String.format("Estadístico t observado:   %.4f\n", estadisticoT));
            sb.append(String.format("Grados de Libertad (df):   %d\n", n - 1));
            sb.append("------------------------------------------\n");
            sb.append("Interpretación rápida:\n");
            sb.append("Compara |t| con el valor crítico t (p. ej. t_crítico ≈ 2.365 para α=0.05 y df=7).\n");
            if (Math.abs(estadisticoT) > 2.365) {
                sb.append("Resultado: Se RECHAZA la hipótesis nula (H₀). Diferencia significativa.");
            } else {
                sb.append("Resultado: NO se rechaza H₀. No hay suficiente evidencia de diferencia.");
            }

            txtResultado.setText(sb.toString());

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Verifica que los números estén formateados correctamente.", "Error de Formato", JOptionPane.ERROR_MESSAGE);
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new PruebaParametricaGUI().setVisible(true));
    }
}