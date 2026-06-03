import 'package:flutter/material.dart';
import '../services/api_service.dart';

class NutricionScreen extends StatefulWidget {
  final int idCliente;

  const NutricionScreen({super.key, required this.idCliente});

  @override
  State<NutricionScreen> createState() => _NutricionScreenState();
}

class _NutricionScreenState extends State<NutricionScreen> {
  final ApiService api = ApiService();
  late Future<List<dynamic>> planes;

  @override
  void initState() {
    super.initState();
    planes = api.obtenerNutricion(widget.idCliente);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<dynamic>>(
      future: planes,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text("Error: ${snapshot.error}"));
        }

        final data = snapshot.data ?? [];

        if (data.isEmpty) {
          return const Center(child: Text("No tienes planes nutricionales"));
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: data.length,
          itemBuilder: (context, index) {
            final plan = data[index];
            final comidas = plan["comidas"] ?? [];

            return Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Plan nutricional #${plan["id_plan"]}",
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text("Objetivo: ${plan["objetivo"] ?? "-"}"),
                    Text("Calorías: ${plan["calorias_diarias"] ?? "-"}"),
                    Text("Proteínas: ${plan["proteinas"] ?? "-"} g"),
                    Text("Carbohidratos: ${plan["carbohidratos"] ?? "-"} g"),
                    Text("Grasas: ${plan["grasas"] ?? "-"} g"),
                    const SizedBox(height: 12),
                    const Text(
                      "Comidas",
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),

                    if (comidas.isEmpty)
                      const Text("No hay comidas registradas en este plan"),

                    ...comidas.map<Widget>((c) {
                      return Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.black12),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              c["tipo_comida"] ?? "Comida",
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(c["descripcion"] ?? ""),
                            Text("Calorías: ${c["calorias_aprox"] ?? "-"}"),
                            Text("Hora: ${c["hora_recomendada"] ?? "-"}"),
                          ],
                        ),
                      );
                    }).toList(),
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