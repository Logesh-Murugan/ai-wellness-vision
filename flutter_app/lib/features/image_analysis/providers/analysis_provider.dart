import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';

part 'analysis_provider.g.dart';

// ─── Result model ────────────────────────────────────────────────────────────

class AnalysisResult {
  final String id;
  final String type;
  final String result;
  final double confidence;
  final List<String> recommendations;
  final String timestamp;
  final String? imagePath;
  final String? analysisMethod;

  const AnalysisResult({
    required this.id,
    required this.type,
    required this.result,
    required this.confidence,
    required this.recommendations,
    required this.timestamp,
    this.imagePath,
    this.analysisMethod,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) => AnalysisResult(
        id: json['id'] ?? '',
        type: json['analysis_type'] ?? json['type'] ?? '',
        result: json['result'] ?? '',
        confidence: (json['confidence'] ?? 0.0).toDouble(),
        recommendations:
            List<String>.from(json['recommendations'] ?? []),
        timestamp: json['timestamp'] ?? json['created_at'] ?? '',
        imagePath: json['image_path'],
        analysisMethod: json['analysis_method'],
      );
}

// ─── State ───────────────────────────────────────────────────────────────────

class AnalysisState {
  final String analysisType;
  final XFile? selectedImage;
  final Uint8List? imageBytes;
  final bool isAnalysing;
  final AsyncValue<AnalysisResult?> result;

  const AnalysisState({
    this.analysisType = 'skin',
    this.selectedImage,
    this.imageBytes,
    this.isAnalysing = false,
    this.result = const AsyncData(null),
  });

  bool get hasImage => selectedImage != null || imageBytes != null;

  AnalysisState copyWith({
    String? analysisType,
    XFile? selectedImage,
    Uint8List? imageBytes,
    bool? isAnalysing,
    AsyncValue<AnalysisResult?>? result,
  }) =>
      AnalysisState(
        analysisType: analysisType ?? this.analysisType,
        selectedImage: selectedImage ?? this.selectedImage,
        imageBytes: imageBytes ?? this.imageBytes,
        isAnalysing: isAnalysing ?? this.isAnalysing,
        result: result ?? this.result,
      );
}

// ─── Notifier ────────────────────────────────────────────────────────────────

@riverpod
class AnalysisNotifier extends _$AnalysisNotifier {
  @override
  AnalysisState build() => const AnalysisState();

  void setAnalysisType(String type) {
    state = state.copyWith(analysisType: type);
  }

  Future<void> pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final file = await picker.pickImage(source: source, imageQuality: 85);
    if (file == null) return;

    Uint8List? bytes;
    if (kIsWeb) {
      bytes = await file.readAsBytes();
    }
    state = state.copyWith(
      selectedImage: file,
      imageBytes: bytes,
      result: const AsyncData(null),
    );
  }

  Future<void> analyze() async {
    if (state.selectedImage == null) return;
    state = state.copyWith(isAnalysing: true);

    final dio = ref.read(apiClientProvider);
    try {
      final formData = FormData.fromMap({
        'analysis_type': state.analysisType,
        'file': await MultipartFile.fromFile(
          state.selectedImage!.path,
          filename: state.selectedImage!.name,
        ),
      });

      final response = await dio.post(
        '/api/v1/analysis/image',
        data: formData,
      );

      state = state.copyWith(
        isAnalysing: false,
        result: AsyncData(AnalysisResult.fromJson(response.data)),
      );
    } catch (e, st) {
      state = state.copyWith(
        isAnalysing: false,
        result: AsyncError(e, st),
      );
    }
  }

  void reset() {
    state = const AnalysisState();
  }
}

// Keep backward-compatible alias used by history_provider
@riverpod
Future<List<Map<String, dynamic>>> analysisHistory(
    AnalysisHistoryRef ref, {int limit = 10, int offset = 0}) async {
  final dio = ref.read(apiClientProvider);
  try {
    final response = await dio.get(
      '/api/v1/analysis/history',
      queryParameters: {'limit': limit, 'offset': offset},
    );
    return List<Map<String, dynamic>>.from(response.data ?? []);
  } catch (_) {
    return [];
  }
}
