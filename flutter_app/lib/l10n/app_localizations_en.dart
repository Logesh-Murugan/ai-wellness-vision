// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'AI WellnessVision';

  @override
  String get appTagline => 'Your health, in your language';

  @override
  String welcomeMessage(String name) {
    return 'Welcome back, $name!';
  }

  @override
  String get imageAnalysis => 'Image Analysis';

  @override
  String get aiChat => 'AI Health Chat';

  @override
  String get voiceAssistant => 'Voice Assistant';

  @override
  String get history => 'History';

  @override
  String get profile => 'Profile';

  @override
  String get settings => 'Settings';

  @override
  String get analysisPending => 'Analyzing your image...';

  @override
  String get analysisComplete => 'Analysis Complete';

  @override
  String get analysisError => 'Analysis failed. Please try again.';

  @override
  String get chatPlaceholder => 'Ask me about your health...';

  @override
  String get chatDisclaimer =>
      'AI responses are for information only. Consult a doctor for medical advice.';

  @override
  String get emergencyTitle => 'Medical Emergency?';

  @override
  String get emergencyInfo =>
      'Call 108 for Ambulance or 112 for Emergency Services';

  @override
  String get skinAnalysis => 'Skin Analysis';

  @override
  String get eyeAnalysis => 'Eye Health';

  @override
  String get foodAnalysis => 'Food & Nutrition';

  @override
  String get emotionDetection => 'Emotional Wellness';

  @override
  String get healthScore => 'Health Score';

  @override
  String get recommendations => 'Recommendations';

  @override
  String get noHistoryYet =>
      'No analysis history yet.\nTap + to start your first analysis.';

  @override
  String get darkMode => 'Dark Mode';

  @override
  String get changeLanguage => 'Change Language';

  @override
  String get logout => 'Log Out';

  @override
  String get deleteAccount => 'Delete Account';

  @override
  String get confirmLogout => 'Are you sure you want to log out?';

  @override
  String get cancel => 'Cancel';

  @override
  String get confirm => 'Confirm';

  @override
  String get loading => 'Loading...';

  @override
  String get retry => 'Retry';

  @override
  String get noInternetConnection =>
      'No internet connection. Some features may be unavailable.';
}
