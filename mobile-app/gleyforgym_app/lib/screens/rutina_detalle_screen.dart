import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class RutinaDetalleScreen extends StatefulWidget {
  final int idRutina;
  final String nombreRutina;

  const RutinaDetalleScreen({
    super.key,
    required this.idRutina,
    required this.nombreRutina,
  });

  @override
  State<RutinaDetalleScreen> createState() => _RutinaDetalleScreenState();
}

class _RutinaDetalleScreenState extends State<RutinaDetalleScreen> {
  final ApiService api = ApiService();
  late Future<Map<String, dynamic>> detalle;

  @override
  void initState() {
    super.initState();
    detalle = api.obtenerDetalleRutina(widget.idRutina);
  }

  Future<void> _abrirVideo(String url) async {
    final Uri uri = Uri.parse(url);
    try {
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text("No se pudo abrir el video: $url")),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error al abrir video: $e")),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.nombreRutina),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: detalle,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(
                  "Error al cargar detalle: ${snapshot.error}",
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.red),
                ),
              ),
            );
          }

          final data = snapshot.data;
          if (data == null || data["ejercicios"] == null) {
            return const Center(child: Text("No hay ejercicios registrados en esta rutina"));
          }

          final List<dynamic> ejercicios = data["ejercicios"];

          if (ejercicios.isEmpty) {
            return const Center(child: Text("Esta rutina no contiene ejercicios."));
          }

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                color: Colors.indigo.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        data["nombre"] ?? widget.nombreRutina,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.indigo,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text("Objetivo: ${data["objetivo"] ?? "-"}"),
                      Text("Nivel: ${data["nivel"] ?? "-"}"),
                      Text("Días recomendados: ${data["dias_semana"] ?? "-"}"),
                      if (data["descripcion"] != null &&
                          data["descripcion"].toString().isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(
                          "Descripción: ${data["descripcion"]}",
                          style: TextStyle(color: Colors.grey.shade700),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                "Lista de Ejercicios",
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              ...ejercicios.map((ej) {
                final String nombre = ej["nombre"] ?? "Ejercicio";
                final String grupo = ej["grupo_muscular"] ?? "-";
                final int? series = ej["series"];
                final String reps = ej["repeticiones"]?.toString() ?? "-";
                final int? descanso = ej["descanso_segundos"];
                final String? dia = ej["dia_semana"];
                final String? videoUrl = ej["video_url"];
                final String? instrucciones = ej["instrucciones"];
                final String? descripcionEj = ej["descripcion"];

                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ExpansionTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.indigo.shade100,
                      child: Text(
                        ej["orden"]?.toString() ?? "",
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.indigo),
                      ),
                    ),
                    title: Text(
                      nombre,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text("$grupo • ${dia ?? 'General'}"),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text("Series x Reps", style: TextStyle(color: Colors.grey)),
                                    Text(
                                      "${series ?? '-'} x $reps",
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                    ),
                                  ],
                                ),
                                Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text("Descanso", style: TextStyle(color: Colors.grey)),
                                    Text(
                                      descanso != null ? "$descanso s" : "-",
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            if (descripcionEj != null && descripcionEj.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              const Text("Descripción", style: TextStyle(fontWeight: FontWeight.bold)),
                              const SizedBox(height: 4),
                              Text(descripcionEj),
                            ],
                            if (instrucciones != null && instrucciones.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              const Text("Instrucciones", style: TextStyle(fontWeight: FontWeight.bold)),
                              const SizedBox(height: 4),
                              Text(instrucciones),
                            ],
                            if (videoUrl != null && videoUrl.isNotEmpty) ...[
                              const SizedBox(height: 16),
                              SizedBox(
                                width: double.infinity,
                                child: ElevatedButton.icon(
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: Colors.indigo,
                                    foregroundColor: Colors.white,
                                  ),
                                  icon: const Icon(Icons.play_circle_fill),
                                  label: const Text("Ver Video de Demostración"),
                                  onPressed: () => _abrirVideo(videoUrl),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ],
          );
        },
      ),
    );
  }
}
