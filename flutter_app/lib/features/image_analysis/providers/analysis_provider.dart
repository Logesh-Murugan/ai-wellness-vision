import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';
import 'package:ai_wellness_vision/features/auth/providers/auth_provider.dart';

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

    // Check if we are in demo mode
    final isDemo = ref.read(authNotifierProvider).valueOrNull?.id == 'demo-id';
    if (isDemo) {
      await Future.delayed(const Duration(seconds: 2));
      final mockResult = state.analysisType == 'skin'
          ? const AnalysisResult(
              id: 'mock-skin-analysis',
              type: 'skin',
              result: 'Mild contact dermatitis / dryness detected. The skin barrier shows signs of slight irritation.',
              confidence: 0.89,
              recommendations: [
                'Keep the area clean and moisturize with a gentle, fragrance-free cream.',
                'Avoid harsh soaps or chemicals.',
                'Apply aloe vera gel to soothe the itchiness.',
                'Consult a dermatologist if symptoms persist for more than a week.'
              ],
              timestamp: '2026-05-24T12:00:00Z',
            )
          : const AnalysisResult(
              id: 'mock-food-analysis',
              type: 'food',
              result: 'Fresh garden salad with mixed greens and avocado. High in fiber, healthy monounsaturated fats, vitamins A and C.',
              confidence: 0.94,
              recommendations: [
                'Excellent choice for a low-glycemic, nutrient-dense lunch.',
                'Add grilled chicken, tofu, or chickpeas to increase protein content.',
                'Go light on the dressing (prefer olive oil and lemon juice).',
                'Great for promoting cardiovascular health and skin vitality.'
              ],
              timestamp: '2026-05-24T12:00:00Z',
            );
      state = state.copyWith(
        isAnalysing: false,
        result: AsyncData(mockResult),
      );
      return;
    }

    final dio = ref.read(apiClientProvider);
    try {
      final imageBytes = await state.selectedImage!.readAsBytes();
      final formData = FormData.fromMap({
        'analysis_type': state.analysisType,
        'image': MultipartFile.fromBytes(
          imageBytes,
          filename: state.selectedImage!.name,
        ),
      });

      final response = await dio.post(
        '/api/v1/analysis/image',
        data: formData,
        queryParameters: {'analysis_type': state.analysisType},
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
    final data = response.data;
    if (data is Map && data.containsKey('results')) {
      return List<Map<String, dynamic>>.from(data['results'] ?? []);
    }
    return List<Map<String, dynamic>>.from(data ?? []);
  } catch (_) {
    return [];
  }
}
