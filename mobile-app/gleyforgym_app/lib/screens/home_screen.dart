import 'package:flutter/material.dart';
import 'rutinas_screen.dart';
import 'nutricion_screen.dart';
import 'pagos_screen.dart';
import 'progreso_screen.dart';
import 'membresia_screen.dart';
import 'productos_screen.dart';

class HomeScreen extends StatefulWidget {
  final int idCliente;

  const HomeScreen({super.key, required this.idCliente});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int indice = 0;

  @override
  Widget build(BuildContext context) {
    final pantallas = [
      RutinasScreen(idCliente: widget.idCliente),
      NutricionScreen(idCliente: widget.idCliente),
      PagosScreen(idCliente: widget.idCliente),
      ProgresoScreen(idCliente: widget.idCliente),
      MembresiaScreen(idCliente: widget.idCliente),
      const ProductosScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text("GLEYFORGYM"),
        centerTitle: true,
      ),
      body: pantallas[indice],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: indice,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Colors.indigo,
        onTap: (value) {
          setState(() {
            indice = value;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.fitness_center),
            label: "Rutinas",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.restaurant),
            label: "Nutrición",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.payment),
            label: "Pagos",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart),
            label: "Progreso",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.card_membership),
            label: "Membresía",
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_bag),
            label: "Tienda",
          ),
        ],
      ),
    );
  }
}