import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MembresiaScreen extends StatefulWidget {
  final int idCliente;

  const MembresiaScreen({super.key, required this.idCliente});

  @override
  State<MembresiaScreen> createState() => _MembresiaScreenState();
}

class _MembresiaScreenState extends State<MembresiaScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> membresias;

  @override
  void initState() {
    super.initState();
    membresias = api.obtenerMembresia(widget.idCliente);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: membresias,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No tienes membresía asignada"));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: data.length,
          itemBuilder: (context, index) {
            final m = data[index];

            return Card(
              child: ListTile(
                leading: const Icon(Icons.card_membership, color: Colors.indigo),
                title: Text(
                  m["nombre_membresia"] ?? "Membresía #${m["id_membresia"]}",
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                subtitle: Text(
                  "Inicio: ${m["fecha_inicio"] ?? "-"}\n"
                  "Fin: ${m["fecha_fin"] ?? "-"}\n"
                  "Precio: S/ ${(m["precio_asignado"] ?? 0.0).toStringAsFixed(2)}",
                ),
                trailing: Chip(
                  label: Text(m["estado"] ?? ""),
                  backgroundColor: m["estado"] == "ACTIVA"
                      ? Colors.green.shade50
                      : Colors.orange.shade50,
                  labelStyle: TextStyle(
                    color: m["estado"] == "ACTIVA"
                        ? Colors.green
                        : Colors.orange,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}