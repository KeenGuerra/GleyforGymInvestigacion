import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProgresoScreen extends StatefulWidget {
  final int idCliente;

  const ProgresoScreen({super.key, required this.idCliente});

  @override
  State<ProgresoScreen> createState() => _ProgresoScreenState();
}

class _ProgresoScreenState extends State<ProgresoScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> progresos;

  @override
  void initState() {
    super.initState();
    progresos = api.obtenerProgreso(widget.idCliente);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: progresos,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No tienes progreso registrado"));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: data.length,
          itemBuilder: (context, index) {
            final p = data[index];

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.show_chart, color: Colors.indigo),
                        const SizedBox(width: 8),
                        Text(
                          "Registro: ${p["fecha_registro"] ?? "-"}",
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const Divider(),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text("Peso: ${p["peso"] ?? "-"} kg", style: const TextStyle(fontWeight: FontWeight.bold)),
                        Text("Grasa: ${p["porcentaje_grasa"] ?? "-"} %"),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text("Masa Magra: ${p["masa_magra"] ?? "-"} kg"),
                        Text("Masa Grasa: ${p["masa_grasa"] ?? "-"} kg"),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      "Medidas Corporales",
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.indigo),
                    ),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text("Pecho: ${p["medida_pecho"] ?? "-"} cm", style: const TextStyle(fontSize: 11)),
                        ),
                        Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text("Cintura: ${p["medida_cintura"] ?? "-"} cm", style: const TextStyle(fontSize: 11)),
                        ),
                        Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text("Brazo I/D: ${p["medida_brazo_izquierdo"] ?? "-"} / ${p["medida_brazo_derecho"] ?? "-"} cm", style: const TextStyle(fontSize: 11)),
                        ),
                        Chip(
                          visualDensity: VisualDensity.compact,
                          label: Text("Pierna I/D: ${p["medida_pierna_izquierda"] ?? "-"} / ${p["medida_pierna_derecha"] ?? "-"} cm", style: const TextStyle(fontSize: 11)),
                        ),
                      ],
                    ),
                    if (p["observacion"] != null && p["observacion"].toString().trim().isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text(
                        "Observación: ${p["observacion"]}",
                        style: TextStyle(fontStyle: FontStyle.italic, color: Colors.grey.shade700, fontSize: 12),
                      ),
                    ],
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }
}