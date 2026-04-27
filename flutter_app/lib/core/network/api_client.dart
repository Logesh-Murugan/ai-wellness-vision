import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'api_client.g.dart';

class ApiClient {
  final Dio _dio;
  final FlutterSecureStorage _storage;

  ApiClient({
    required String baseUrl,
    required FlutterSecureStorage storage,
  })  : _storage = storage,
        _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: const Duration(seconds: 30),
            receiveTimeout: const Duration(seconds: 120),
            headers: {'Content-Type': 'application/json'},
          ),
        ) {
    _dio.interceptors.addAll([
      _AuthInterceptor(_storage),
      _RefreshInterceptor(_dio, _storage, baseUrl),
    ]);
  }

  Dio get client => _dio;
}

class _AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;

  _AuthInterceptor(this._storage);

  @override
  Future<void> onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return handler.next(options);
  }
}

class _RefreshInterceptor extends Interceptor {
  final Dio _dio;
  final FlutterSecureStorage _storage;
  final String _baseUrl;
  bool _isRefreshing = false;

  _RefreshInterceptor(this._dio, this._storage, this._baseUrl);

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401 && !_isRefreshing) {
      _isRefreshing = true;
      try {
        final refreshToken = await _storage.read(key: 'refresh_token');
        if (refreshToken == null) {
          return handler.next(err);
        }

        // Attempt to refresh the token using a dedicated dio instance to avoid interceptor loops
        final tokenDio = Dio(BaseOptions(baseUrl: _baseUrl));
        final response = await tokenDio.post(
          '/api/v1/auth/refresh',
          options: Options(headers: {'Authorization': 'Bearer $refreshToken'}),
        );

        final newAccessToken = response.data['access_token'];
        if (newAccessToken != null) {
          await _storage.write(key: 'access_token', value: newAccessToken);
          
          // Update the original request header
          err.requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
          
          // Retry the original request
          final retryResponse = await _dio.fetch(err.requestOptions);
          return handler.resolve(retryResponse);
        }
      } catch (e) {
        // Refresh failed, clear storage to force logout
        await _storage.deleteAll();
      } finally {
        _isRefreshing = false;
      }
    }
    return handler.next(err);
  }
}

// ---------------------------------------------------------
// Riverpod Providers
// ---------------------------------------------------------

@riverpod
FlutterSecureStorage secureStorage(SecureStorageRef ref) {
  return const FlutterSecureStorage();
}

@riverpod
Dio apiClient(ApiClientRef ref) {
  // In production, this would be loaded from flutter_dotenv
  const baseUrl = 'http://localhost:8000';
  final storage = ref.watch(secureStorageProvider);
  
  return ApiClient(baseUrl: baseUrl, storage: storage).client;
}
