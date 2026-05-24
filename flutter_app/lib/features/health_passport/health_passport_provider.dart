import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../core/services/dio_client.dart';

// ─── State ────────────────────────────────────────────────────────────────────

enum PassportStatus { idle, loading, success, error }

class PassportState {
  final PassportStatus status;
  final String? errorMessage;
  final String? filePath;

  const PassportState({
    this.status = PassportStatus.idle,
    this.errorMessage,
    this.filePath,
  });

  PassportState copyWith({
    PassportStatus? status,
    String? errorMessage,
    String? filePath,
  }) =>
      PassportState(
        status: status ?? this.status,
        errorMessage: errorMessage ?? this.errorMessage,
        filePath: filePath ?? this.filePath,
      );
}

// ─── Notifier ─────────────────────────────────────────────────────────────────

class HealthPassportNotifier extends StateNotifier<PassportState> {
  HealthPassportNotifier() : super(const PassportState());

  Future<void> generateAndDownload({int periodDays = 7}) async {
    state = state.copyWith(status: PassportStatus.loading, errorMessage: null, filePath: null);

    try {
      // Read token from SharedPreferences (DioClient uses SharedPreferences)
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('access_token');

      final dio = Dio(BaseOptions(
        baseUrl: const String.fromEnvironment(
          'API_BASE_URL',
          defaultValue: 'http://localhost:8000',
        ),
        receiveTimeout: const Duration(seconds: 60),
        sendTimeout: const Duration(seconds: 30),
      ));

      if (token != null) {
        dio.options.headers['Authorization'] = 'Bearer $token';
      }

      final response = await dio.get(
        '/api/v1/health-passport/generate',
        queryParameters: {'period_days': periodDays},
        options: Options(responseType: ResponseType.bytes),
      );

      // Save bytes to app documents directory
      final dir = await getApplicationDocumentsDirectory();
      final filename =
          'health_passport_${DateTime.now().millisecondsSinceEpoch}.pdf';
      final file = File('${dir.path}/$filename');
      await file.writeAsBytes(response.data as List<int>);

      state = state.copyWith(
        status: PassportStatus.success,
        filePath: file.path,
      );

      // Auto-open the PDF on device
      await OpenFilex.open(file.path);
    } on DioException catch (e) {
      state = state.copyWith(
        status: PassportStatus.error,
        errorMessage: e.message ?? 'Failed to generate passport. Please try again.',
      );
    } catch (e) {
      state = state.copyWith(
        status: PassportStatus.error,
        errorMessage: 'Unexpected error: $e',
      );
    }
  }

  void reset() => state = const PassportState();
}

// ─── Provider ────────────────────────────────────────────────────────────────

final healthPassportProvider =
    StateNotifierProvider<HealthPassportNotifier, PassportState>(
  (ref) => HealthPassportNotifier(),
);
