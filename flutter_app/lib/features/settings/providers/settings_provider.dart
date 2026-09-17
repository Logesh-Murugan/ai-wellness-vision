/// Settings provider with SharedPreferences persistence.
///
/// All settings survive app restarts.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

// ─── Keys ─────────────────────────────────────────────────────────────────────

const _kDarkMode = 'settings_dark_mode';
const _kNotifications = 'settings_notifications';
const _kLanguage = 'settings_language';
const _kVoiceEnabled = 'settings_voice_enabled';
const _kAnalytics = 'settings_analytics';
const _kVoiceSpeed = 'settings_voice_speed';

// ─── Settings State ───────────────────────────────────────────────────────────

class SettingsState {
  final bool darkMode;
  final bool notifications;
  final String language;
  final bool voiceEnabled;
  final bool analytics;
  final double voiceSpeed;

  const SettingsState({
    this.darkMode = false,
    this.notifications = true,
    this.language = 'en',
    this.voiceEnabled = true,
    this.analytics = true,
    this.voiceSpeed = 1.0,
  });

  SettingsState copyWith({
    bool? darkMode,
    bool? notifications,
    String? language,
    bool? voiceEnabled,
    bool? analytics,
    double? voiceSpeed,
  }) =>
      SettingsState(
        darkMode: darkMode ?? this.darkMode,
        notifications: notifications ?? this.notifications,
        language: language ?? this.language,
        voiceEnabled: voiceEnabled ?? this.voiceEnabled,
        analytics: analytics ?? this.analytics,
        voiceSpeed: voiceSpeed ?? this.voiceSpeed,
      );
}

// ─── Notifier ─────────────────────────────────────────────────────────────────

class SettingsNotifier extends AsyncNotifier<SettingsState> {
  late SharedPreferences _prefs;

  @override
  Future<SettingsState> build() async {
    _prefs = await SharedPreferences.getInstance();
    return SettingsState(
      darkMode: _prefs.getBool(_kDarkMode) ?? false,
      notifications: _prefs.getBool(_kNotifications) ?? true,
      language: _prefs.getString(_kLanguage) ?? 'en',
      voiceEnabled: _prefs.getBool(_kVoiceEnabled) ?? true,
      analytics: _prefs.getBool(_kAnalytics) ?? true,
      voiceSpeed: _prefs.getDouble(_kVoiceSpeed) ?? 1.0,
    );
  }

  Future<void> setDarkMode(bool value) async {
    await _prefs.setBool(_kDarkMode, value);
    state = AsyncData(state.value!.copyWith(darkMode: value));
  }

  Future<void> setNotifications(bool value) async {
    await _prefs.setBool(_kNotifications, value);
    state = AsyncData(state.value!.copyWith(notifications: value));
  }

  Future<void> setLanguage(String value) async {
    await _prefs.setString(_kLanguage, value);
    state = AsyncData(state.value!.copyWith(language: value));
  }

  Future<void> setVoiceEnabled(bool value) async {
    await _prefs.setBool(_kVoiceEnabled, value);
    state = AsyncData(state.value!.copyWith(voiceEnabled: value));
  }

  Future<void> setAnalytics(bool value) async {
    await _prefs.setBool(_kAnalytics, value);
    state = AsyncData(state.value!.copyWith(analytics: value));
  }

  Future<void> setVoiceSpeed(double value) async {
    await _prefs.setDouble(_kVoiceSpeed, value);
    state = AsyncData(state.value!.copyWith(voiceSpeed: value));
  }

  Future<void> resetAll() async {
    await _prefs.clear();
    state = const AsyncData(SettingsState());
  }
}

// ─── Providers ────────────────────────────────────────────────────────────────

/// Primary settings provider — use this everywhere.
final settingsProvider =
    AsyncNotifierProvider<SettingsNotifier, SettingsState>(SettingsNotifier.new);

// ── Convenience providers (backward compat + easy access) ──

/// Watch just the dark-mode flag. Falls back to false while loading.
final darkModeProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.darkMode,
        orElse: () => false,
      );
});

final notificationsProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.notifications,
        orElse: () => true,
      );
});

final selectedLanguageProvider = Provider<String>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.language,
        orElse: () => 'en',
      );
});

final voiceEnabledProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.voiceEnabled,
        orElse: () => true,
      );
});

final analyticsEnabledProvider = Provider<bool>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.analytics,
        orElse: () => true,
      );
});

final voiceSpeedProvider = Provider<double>((ref) {
  return ref.watch(settingsProvider).maybeWhen(
        data: (s) => s.voiceSpeed,
        orElse: () => 1.0,
      );
});
