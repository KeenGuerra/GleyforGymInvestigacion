import 'package:flutter/material.dart';
import '../services/api_service.dart';

class PagosScreen extends StatefulWidget {
  final int idCliente;

  const PagosScreen({super.key, required this.idCliente});

  @override
  State<PagosScreen> createState() => _PagosScreenState();
}

class _PagosScreenState extends State<PagosScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> pagos;

  @override
  void initState() {
    super.initState();
    pagos = api.obtenerPagos(widget.idCliente);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: pagos,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No tienes pagos registrados"));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: data.length,
          itemBuilder: (context, index) {
            final p = data[index];

            return Card(
              child: ListTile(
                leading: const Icon(Icons.payment),
                title: Text("S/ ${p["monto"]}"),
                subtitle: Text(
                  "Método: ${p["metodo_pago"] ?? "-"}\nFecha: ${p["fecha_pago"] ?? "-"}",
                ),
                trailing: Text(p["estado"] ?? ""),
              ),
            );
          },
        );
      },
    );
  }
}