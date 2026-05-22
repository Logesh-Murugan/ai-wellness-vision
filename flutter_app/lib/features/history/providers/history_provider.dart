import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_app/features/image_analysis/data/analysis_repository.dart';

part 'history_provider.g.dart';

@riverpod
Future<List<dynamic>> analysisHistory(AnalysisHistoryRef ref) async {
  // Use dynamic because AnalysisRecord is not explicitly defined in the provided context
  return ref.read(analysisRepositoryProvider).getHistory(limit: 20);
}
