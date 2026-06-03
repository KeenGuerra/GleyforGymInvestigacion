import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:gleyforgym_app/main.dart';
import 'package:gleyforgym_app/screens/login_screen.dart';
import 'package:gleyforgym_app/screens/rutinas_screen.dart';
import 'package:gleyforgym_app/screens/nutricion_screen.dart';
import 'package:gleyforgym_app/screens/progreso_screen.dart';
import 'package:gleyforgym_app/screens/membresia_screen.dart';
import 'package:gleyforgym_app/screens/pagos_screen.dart';
import 'package:gleyforgym_app/screens/home_screen.dart';
import 'package:gleyforgym_app/screens/rutina_detalle_screen.dart';

void main() {
  testWidgets('Login screen rendering and elements smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const GleyforGymApp());

    // Verify that the title "GLEYFORGYM" is displayed.
    expect(find.text('GLEYFORGYM'), findsOneWidget);

    // Verify that the text fields for correo and password exist.
    expect(find.byType(TextField), findsNWidgets(2));
    expect(find.text('Correo'), findsOneWidget);
    expect(find.text('Contraseña'), findsOneWidget);

    // Verify that the "Iniciar sesión" button exists.
    expect(find.byType(ElevatedButton), findsOneWidget);
    expect(find.text('Iniciar sesión'), findsOneWidget);
  });

  testWidgets('Login screen typing and error message state test', (WidgetTester tester) async {
    // Build the login screen directly
    await tester.pumpWidget(const MaterialApp(
      home: LoginScreen(),
    ));

    // Type into Correo and Contraseña fields
    await tester.enterText(find.byWidgetPredicate((widget) =>
        widget is TextField && widget.decoration?.labelText == 'Correo'), 'test@gleyforgym.com');
    await tester.enterText(find.byWidgetPredicate((widget) =>
        widget is TextField && widget.decoration?.labelText == 'Contraseña'), '123456');

    await tester.pump();

    // Verify values were typed
    expect(find.text('test@gleyforgym.com'), findsOneWidget);
    expect(find.text('123456'), findsOneWidget);

    // Tap login button
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Since ApiService call fails in test environment, an error message starts with "Error:" should show
    expect(find.byWidgetPredicate((widget) =>
        widget is Text && widget.style?.color == Colors.red && widget.data!.startsWith('Error:')), findsOneWidget);
  });

  testWidgets('RutinasScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: RutinasScreen(idCliente: 1),
      ),
    ));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('NutricionScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: NutricionScreen(idCliente: 1),
      ),
    ));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('ProgresoScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: ProgresoScreen(idCliente: 1),
      ),
    ));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('MembresiaScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: MembresiaScreen(idCliente: 1),
      ),
    ));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('PagosScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: PagosScreen(idCliente: 1),
      ),
    ));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('HomeScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: HomeScreen(idCliente: 1),
    ));

    expect(find.text('GLEYFORGYM'), findsOneWidget);
    expect(find.byType(BottomNavigationBar), findsOneWidget);
    expect(find.text('Rutinas'), findsOneWidget);
    expect(find.text('Nutrición'), findsOneWidget);
    expect(find.text('Pagos'), findsOneWidget);
    expect(find.text('Progreso'), findsOneWidget);
    expect(find.text('Membresía'), findsOneWidget);
  });

  testWidgets('RutinaDetalleScreen rendering smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: RutinaDetalleScreen(
        idRutina: 1,
        nombreRutina: 'Mi Rutina Especial',
      ),
    ));

    expect(find.text('Mi Rutina Especial'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
