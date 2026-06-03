import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const GleyforGymApp());
}

class GleyforGymApp extends StatelessWidget {
  const GleyforGymApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GLEYFORGYM',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.indigo,
      ),
      home: const LoginScreen(),
    );
  }
}