import 'package:flutter_riverpod/flutter_riverpod.dart';

final darkModeProvider = StateProvider<bool>((ref) => false);
final notificationsProvider = StateProvider<bool>((ref) => true);
final selectedLanguageProvider = StateProvider<String>((ref) => 'en');
final voiceEnabledProvider = StateProvider<bool>((ref) => true);
final analyticsEnabledProvider = StateProvider<bool>((ref) => true);
final voiceSpeedProvider = StateProvider<double>((ref) => 1.0);
