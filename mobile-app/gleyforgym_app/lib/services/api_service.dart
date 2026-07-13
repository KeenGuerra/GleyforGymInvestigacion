import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final String baseUrl = const String.fromEnvironment('API_URL', defaultValue: "http://127.0.0.1:8000");
  String? token;

  Map<String, String> get _headers {
    final headers = {"Content-Type": "application/json"};
    if (token != null) {
      headers["Authorization"] = "Bearer $token";
    }
    return headers;
  }

  Future<Map<String, dynamic>> login(String correo, String password) async {
    final response = await http.post(
      Uri.parse("$baseUrl/usuarios/login"),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "correo": correo,
        "password": password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      token = data["token"];
      return data;
    }

    throw Exception("Credenciales incorrectas");
  }

  Future<dynamic> _get(String path, String errorMsg) async {
    final response = await http.get(
      Uri.parse("$baseUrl$path"),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }

    throw Exception(errorMsg);
  }

  Future<Map<String, dynamic>> obtenerClientePorUsuario(int idUsuario) async {
    final data = await _get("/clientes/usuario/$idUsuario", "No se encontró cliente para este usuario");
    return data as Map<String, dynamic>;
  }

  Future<List<dynamic>> obtenerRutinas(int idCliente) async {
    final data = await _get("/rutinas/cliente/$idCliente", "Error al obtener rutinas");
    return data as List<dynamic>;
  }

  Future<List<dynamic>> obtenerNutricion(int idCliente) async {
    final data = await _get("/nutricion/cliente/$idCliente", "Error al obtener nutrición");
    return data as List<dynamic>;
  }

  Future<List<dynamic>> obtenerPagos(int idCliente) async {
    final data = await _get("/pagos/cliente/$idCliente", "Error al obtener pagos");
    return data as List<dynamic>;
  }

  Future<List<dynamic>> obtenerProgreso(int idCliente) async {
    final data = await _get("/progreso/cliente/$idCliente", "Error al obtener progreso");
    return data as List<dynamic>;
  }

  Future<List<dynamic>> obtenerMembresia(int idCliente) async {
    final data = await _get("/cliente-membresias/cliente/$idCliente", "Error al obtener membresía");
    return data as List<dynamic>;
  }

  Future<Map<String, dynamic>> obtenerDetalleRutina(int idRutina) async {
    final data = await _get("/rutinas/$idRutina/detalle", "Error al obtener detalle de rutina");
    return data as Map<String, dynamic>;
  }

  Future<List<dynamic>> obtenerProductos() async {
    final data = await _get("/productos/disponibles", "Error al obtener productos");
    return data as List<dynamic>;
  }
}