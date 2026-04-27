import 'package:dio/dio.dart';
import 'package:image_picker/image_picker.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_app/core/network/api_client.dart';

part 'analysis_provider.g.dart';

// Dummy models for strict typing
class AnalysisResult {
  final String id;
  final String type;
  final Map<String, dynamic> data;

  AnalysisResult({required this.id, required this.type, required this.data});

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      id: json['id'] ?? '',
      type: json['analysis_type'] ?? '',
      data: json['result_json'] ?? {},
    );
  }
}

class AnalysisRecord {
  final String id;
  final String type;
  final String createdAt;

  AnalysisRecord({required this.id, required this.type, required this.createdAt});

  factory AnalysisRecord.fromJson(Map<String, dynamic> json) {
    return AnalysisRecord(
      id: json['id'] ?? '',
      type: json['analysis_type'] ?? '',
      createdAt: json['created_at'] ?? '',
    );
  }
}

@riverpod
class ImageAnalysisNotifier extends _$ImageAnalysisNotifier {
  @override
  FutureOr<AnalysisResult?> build() {
    return null; // Equivalent to AsyncData(null) internally
  }

  Future<void> analyzeImage(XFile file, String type) async {
    state = const AsyncLoading();
    
    state = await AsyncValue.guard(() async {
      final dio = ref.read(apiClientProvider);

      final formData = FormData.fromMap({
        'analysis_type': type,
        'file': await MultipartFile.fromFile(
          file.path,
          filename: file.name,
        ),
      });

      final response = await dio.post(
        '/api/v1/analysis/image',
        data: formData,
      );
      
      return AnalysisResult.fromJson(response.data);
    });
  }

  void reset() {
    state = const AsyncData(null);
  }
}

@riverpod
Future<List<AnalysisRecord>> analysisHistory(AnalysisHistoryRef ref, {int limit = 10, int offset = 0}) async {
  final dio = ref.read(apiClientProvider);
  
  final response = await dio.get(
    '/api/v1/analysis/history',
    queryParameters: {
      'limit': limit,
      'offset': offset,
    },
  );
  
  final List<dynamic> rawList = response.data;
  return rawList.map((item) => AnalysisRecord.fromJson(item)).toList();
}
