import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProductosScreen extends StatefulWidget {
  const ProductosScreen({super.key});

  @override
  State<ProductosScreen> createState() => _ProductosScreenState();
}

class _ProductosScreenState extends State<ProductosScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> productos;

  @override
  void initState() {
    super.initState();
    productos = api.obtenerProductos();
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: productos,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No hay productos disponibles"));
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
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            p["nombre"] ?? "Producto",
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        Text(
                          "S/ ${(p["precio_venta"] ?? 0).toStringAsFixed(2)}",
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.indigo,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    if (p["nombre_categoria"] != null)
                      Text(
                        "Categoría: ${p["nombre_categoria"]}",
                        style: TextStyle(color: Colors.grey[600], fontSize: 13),
                      ),
                    if (p["descripcion"] != null && p["descripcion"].toString().isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Text(
                          p["descripcion"],
                          style: TextStyle(color: Colors.grey[500], fontSize: 13),
                        ),
                      ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _infoChip("Stock", "${p["stock_actual"] ?? 0}"),
                        const SizedBox(width: 8),
                        _infoChip("Unidad", p["unidad_medida"] ?? "UNIDAD"),
                      ],
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _infoChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.indigo.withAlpha(20),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        "$label: $value",
        style: const TextStyle(fontSize: 12),
      ),
    );
  }
}
