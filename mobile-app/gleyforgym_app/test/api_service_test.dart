import 'package:flutter_test/flutter_test.dart';
import 'package:gleyforgym_app/services/api_service.dart';

void main() {
  group('ApiService Tests', () {
    test('instance creation returns singleton', () {
      final api1 = ApiService();
      final api2 = ApiService();
      expect(identical(api1, api2), isTrue);
    });

    test('token getter/setter works', () {
      final api = ApiService();
      api.token = 'test_token';
      expect(api.token, equals('test_token'));
      api.token = null;
    });

    test('baseUrl is defined', () {
      final api = ApiService();
      expect(api.baseUrl, isNotEmpty);
    });
  });
}
