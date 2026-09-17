/// History providers — analysis + chat history from the backend.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';

// ─── Analysis History ─────────────────────────────────────────────────────────

class HistoryRecord {
  final String id;
  final String type;
  final String summary;
  final double confidence;
  final String createdAt;

  HistoryRecord({
    required this.id,
    required this.type,
    required this.summary,
    required this.confidence,
    required this.createdAt,
  });

  factory HistoryRecord.fromJson(Map<dynamic, dynamic> json) => HistoryRecord(
        id: (json['id'] ?? '').toString(),
        type: (json['type'] ?? json['analysis_type'] ?? 'analysis').toString(),
        summary: (json['result'] ?? json['result_text'] ?? '').toString(),
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        createdAt: (json['timestamp'] ?? json['created_at'] ?? '').toString(),
      );
}

final analysisHistoryProvider =
    FutureProvider.autoDispose<List<HistoryRecord>>((ref) async {
  final dio = ref.watch(apiClientProvider);
  try {
    final response = await dio.get('/api/v1/analysis/history',
        queryParameters: {'limit': 50, 'page': 1});
    final data = response.data;
    final List list = (data is Map ? data['results'] : data) as List? ?? [];
    return list.map((e) => HistoryRecord.fromJson(e as Map)).toList();
  } catch (_) {
    return [];
  }
});

// ─── Chat History ─────────────────────────────────────────────────────────────

class ConversationRecord {
  final String id;
  final String title;
  final String createdAt;
  final int messageCount;

  ConversationRecord({
    required this.id,
    required this.title,
    required this.createdAt,
    required this.messageCount,
  });

  factory ConversationRecord.fromJson(Map<dynamic, dynamic> json) =>
      ConversationRecord(
        id: (json['id'] ?? '').toString(),
        title: (json['title'] ?? 'Chat Session').toString(),
        createdAt: (json['created_at'] ?? '').toString(),
        messageCount: (json['message_count'] as num?)?.toInt() ?? 0,
      );
}

final chatHistoryProvider =
    FutureProvider.autoDispose<List<ConversationRecord>>((ref) async {
  final dio = ref.watch(apiClientProvider);
  try {
    final response = await dio.get('/api/v1/chat/conversations');
    final List list = (response.data as List?) ?? [];
    return list.map((e) => ConversationRecord.fromJson(e as Map)).toList();
  } catch (_) {
    return [];
  }
});
