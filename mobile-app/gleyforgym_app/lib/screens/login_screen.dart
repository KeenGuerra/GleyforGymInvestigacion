import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final ApiService api = ApiService();

  final TextEditingController correoController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  bool cargando = false;
  String error = "";

  Future<void> iniciarSesion() async {
    setState(() {
      cargando = true;
      error = "";
    });

    try {
      final data = await api.login(
        correoController.text.trim(),
        passwordController.text.trim(),
      );

      int idUsuario;

      if (data["usuario"] != null && data["usuario"]["id_usuario"] != null) {
        idUsuario = data["usuario"]["id_usuario"];
      } else if (data["id_usuario"] != null) {
        idUsuario = data["id_usuario"];
      } else {
        throw Exception("El backend no devuelve id_usuario");
      }

      final cliente = await api.obtenerClientePorUsuario(idUsuario);
      final int idCliente = cliente["id_cliente"];

      if (!mounted) return;

      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (_) => HomeScreen(idCliente: idCliente),
        ),
      );
    } catch (e) {
      setState(() {
        error = "Error: $e";
      });
    } finally {
      setState(() {
        cargando = false;
      });
    }
  }

  @override
  void dispose() {
    correoController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              children: [
                const Icon(Icons.fitness_center, size: 70, color: Colors.indigo),
                const SizedBox(height: 15),
                const Text(
                  "GLEYFORGYM",
                  style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 30),

                TextField(
                  controller: correoController,
                  decoration: const InputDecoration(
                    labelText: "Correo",
                    border: OutlineInputBorder(),
                  ),
                ),

                const SizedBox(height: 16),

                TextField(
                  controller: passwordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: "Contraseña",
                    border: OutlineInputBorder(),
                  ),
                ),

                const SizedBox(height: 16),

                if (error.isNotEmpty)
                  Text(error, style: const TextStyle(color: Colors.red)),

                const SizedBox(height: 20),

                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: cargando ? null : iniciarSesion,
                    child: cargando
                        ? const CircularProgressIndicator()
                        : const Text("Iniciar sesión"),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}