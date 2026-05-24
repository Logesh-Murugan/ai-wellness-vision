import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';

/// Simple record for history list items.
class HistoryRecord {
  final String id;
  final String type;
  final String createdAt;

  HistoryRecord({required this.id, required this.type, required this.createdAt});

  factory HistoryRecord.fromJson(Map<String, dynamic> json) => HistoryRecord(
        id: json['id'] ?? '',
        type: json['analysis_type'] ?? '',
        createdAt: json['created_at'] ?? '',
      );
}

final analysisHistoryProvider =
    FutureProvider.autoDispose<List<HistoryRecord>>((ref) async {
  final dio = ref.watch(apiClientProvider);
  try {
    final response = await dio.get('/api/v1/analysis/history',
        queryParameters: {'limit': 20, 'offset': 0});
    final list = response.data as List? ?? [];
    return list.map((e) => HistoryRecord.fromJson(e)).toList();
  } catch (_) {
    return [];
  }
});
