/// Dio HTTP client singleton with auth interceptor.
///
/// Provides [DioClient.instance] for all API calls. Automatically
/// injects the Bearer token and retries on 401 (token refresh).
library;

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _kAccessToken = 'access_token';
const _kRefreshToken = 'refresh_token';

class DioClient {
  static Dio? _dio;

  /// The shared Dio instance. Lazily created on first access.
  static Dio get instance {
    _dio ??= _createDio();
    return _dio!;
  }

  static Dio _createDio() {
    final dio = Dio(BaseOptions(
      baseUrl: const String.fromEnvironment(
        'API_BASE_URL',
        defaultValue: 'http://localhost:8000',
      ),
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      sendTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    dio.interceptors.addAll([
      _AuthInterceptor(),
      _ErrorInterceptor(),
      if (kDebugMode)
        LogInterceptor(
          requestBody: true,
          responseBody: true,
          error: true,
        ),
    ]);

    return dio;
  }

  /// Close and recreate the Dio instance (e.g. after logout).
  static void reset() {
    _dio?.close();
    _dio = null;
  }
}

// ─── Auth interceptor ─────────────────────
class _AuthInterceptor extends Interceptor {
  @override
  void onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    // Skip auth for login/register endpoints
    if (options.path.contains('/auth/login') ||
        options.path.contains('/auth/register')) {
      return handler.next(options);
    }

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString(_kAccessToken);
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      try {
        final prefs = await SharedPreferences.getInstance();
        final refreshToken = prefs.getString(_kRefreshToken);
        if (refreshToken != null) {
          final response = await Dio().post(
            '${err.requestOptions.baseUrl}/api/v1/auth/refresh',
            data: {'refresh_token': refreshToken},
          );
          final newToken = response.data['access_token'];
          await prefs.setString(_kAccessToken, newToken);

          // Retry the original request with new token
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          final retryResponse =
              await DioClient.instance.fetch(err.requestOptions);
          return handler.resolve(retryResponse);
        }
      } catch (_) {
        // Refresh failed — clear tokens, let error propagate
        final prefs = await SharedPreferences.getInstance();
        await prefs.remove(_kAccessToken);
        await prefs.remove(_kRefreshToken);
      }
    }
    handler.next(err);
  }
}

// ─── Error interceptor ────────────────────
class _ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    String message = 'An unexpected error occurred';

    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        message = 'Connection timeout. Check your internet connection.';
        break;
      case DioExceptionType.badResponse:
        message = _httpError(err.response?.statusCode, err.response?.data);
        break;
      case DioExceptionType.cancel:
        message = 'Request was cancelled';
        break;
      case DioExceptionType.connectionError:
        message = 'No internet connection.';
        break;
      default:
        message = err.message ?? message;
    }

    handler.next(DioException(
      requestOptions: err.requestOptions,
      error: ApiException(
        message: message,
        statusCode: err.response?.statusCode,
      ),
      type: err.type,
      response: err.response,
    ));
  }

  String _httpError(int? code, dynamic data) {
    final msg = data is Map ? data['message'] ?? data['detail'] : null;
    return switch (code) {
      400 => msg ?? 'Bad request',
      401 => 'Authentication failed. Please login again.',
      403 => 'Access denied.',
      404 => 'Resource not found.',
      422 => msg ?? 'Validation failed',
      429 => 'Too many requests. Try again later.',
      500 => 'Server error. Try again later.',
      _ => msg ?? 'An error occurred',
    };
  }
}

/// Exception thrown by the API layer.
class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException({required this.message, this.statusCode});

  @override
  String toString() => message;
}