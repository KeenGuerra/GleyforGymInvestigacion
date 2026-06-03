import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'rutina_detalle_screen.dart';

class RutinasScreen extends StatefulWidget {
  final int idCliente;

  const RutinasScreen({super.key, required this.idCliente});

  @override
  State<RutinasScreen> createState() => _RutinasScreenState();
}

class _RutinasScreenState extends State<RutinasScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> rutinas;

  @override
  void initState() {
    super.initState();
    rutinas = api.obtenerRutinas(widget.idCliente);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: rutinas,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No tienes rutinas registradas"));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: data.length,
          itemBuilder: (context, index) {
            final r = data[index];

            return Card(
              child: ListTile(
                title: Text(r["nombre"] ?? "Rutina"),
                subtitle: Text(
                  "Objetivo: ${r["objetivo"] ?? "-"}\nNivel: ${r["nivel"] ?? "-"}",
                ),
                trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => RutinaDetalleScreen(
                        idRutina: r["id_rutina"],
                        nombreRutina: r["nombre"] ?? "Rutina",
                      ),
                    ),
                  );
                },
              ),
            );
          },
        );
      },
    );
  }
}