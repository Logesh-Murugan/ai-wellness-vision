import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';

part 'auth_provider.g.dart';

// Dummy User model for demonstration purposes
class User {
  final String id;
  final String email;
  final String firstName;
  final String? lastName;

  User({
    required this.id,
    required this.email,
    required this.firstName,
    this.lastName,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      firstName: json['first_name'] ?? json['name'] ?? '',
      lastName: json['last_name'],
    );
  }
}

@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  FutureOr<User?> build() async {
    // Attempt to restore session on initialization
    return _checkAuthStatus();
  }

  Future<User?> _checkAuthStatus() async {
    final storage = ref.read(secureStorageProvider);
    final token = await storage.read(key: 'access_token');
    
    if (token == null) return null;
    if (token == 'demo-token') {
      return User(id: 'demo-id', email: 'demo@wellnessvision.ai', firstName: 'Demo User');
    }

    try {
      final dio = ref.read(apiClientProvider);
      // Assuming a /me endpoint exists to fetch current user profile
      final response = await dio.get('/api/v1/auth/me');
      return User.fromJson(response.data);
    } catch (e) {
      // If token validation fails, clear storage
      await storage.deleteAll();
      return null;
    }
  }

  Future<void> loginAsDemo() async {
    final storage = ref.read(secureStorageProvider);
    await storage.write(key: 'access_token', value: 'demo-token');
    state = AsyncData(User(id: 'demo-id', email: 'demo@wellnessvision.ai', firstName: 'Demo User'));
  }

  Future<void> login(String email, String password) async {
    state = const AsyncLoading();
    
    state = await AsyncValue.guard(() async {
      final dio = ref.read(apiClientProvider);
      final storage = ref.read(secureStorageProvider);

      final response = await dio.post(
        '/api/v1/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );
      
      final data = response.data;
      await storage.write(key: 'access_token', value: data['access_token']);
      await storage.write(key: 'refresh_token', value: data['refresh_token']);

      // Fetch user profile immediately after login
      final profileResponse = await dio.get('/api/v1/auth/me');
      return User.fromJson(profileResponse.data);
    });
  }

  Future<void> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final dio = ref.read(apiClientProvider);
      final storage = ref.read(secureStorageProvider);
      final response = await dio.post('/api/v1/auth/register', data: {
        'email': email,
        'password': password,
        'first_name': firstName,
        'last_name': lastName,
      });
      final data = response.data;
      await storage.write(key: 'access_token', value: data['access_token']);
      await storage.write(key: 'refresh_token', value: data['refresh_token']);
      return User.fromJson(data['user'] ?? data);
    });
  }

  Future<void> logout() async {
    final storage = ref.read(secureStorageProvider);
    final dio = ref.read(apiClientProvider);
    try {
      await dio.post('/api/v1/auth/logout');
    } catch (_) {
    } finally {
      await storage.deleteAll();
      state = const AsyncData(null);
    }
  }
}

@riverpod
bool isAuthenticated(IsAuthenticatedRef ref) {
  // Watch the user state, if it has data and is not null, they are authenticated
  final authState = ref.watch(authNotifierProvider);
  return authState.valueOrNull != null;
}
