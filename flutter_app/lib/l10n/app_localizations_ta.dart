// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Tamil (`ta`).
class AppLocalizationsTa extends AppLocalizations {
  AppLocalizationsTa([String locale = 'ta']) : super(locale);

  @override
  String get appTitle => 'AI வெல்னெஸ்விஷன்';

  @override
  String get appTagline => 'உங்கள் ஆரோக்கியம், உங்கள் மொழியில்';

  @override
  String welcomeMessage(String name) {
    return 'மீண்டும் வரவேற்கிறோம், $name!';
  }

  @override
  String get imageAnalysis => 'படப் பகுப்பாய்வு';

  @override
  String get aiChat => 'AI சுகாதார அரட்டை';

  @override
  String get voiceAssistant => 'குரல் உதவியாளர்';

  @override
  String get history => 'வரலாறு';

  @override
  String get profile => 'சுயவிவரம்';

  @override
  String get settings => 'அமைப்புகள்';

  @override
  String get analysisPending => 'உங்கள் படம் பகுப்பாய்வு செய்யப்படுகிறது...';

  @override
  String get analysisComplete => 'பகுப்பாய்வு முடிந்தது';

  @override
  String get analysisError =>
      'பகுப்பாய்வு தோல்வியடைந்தது. மீண்டும் முயற்சிக்கவும்.';

  @override
  String get chatPlaceholder => 'உங்கள் ஆரோக்கியம் பற்றி கேளுங்கள்...';

  @override
  String get chatDisclaimer =>
      'AI பதில்கள் தகவல் மட்டுமே. மருத்துவ ஆலோசனைக்கு மருத்துவரை அணுகவும்.';

  @override
  String get emergencyTitle => 'மருத்துவ அவசரநிலையா?';

  @override
  String get emergencyInfo =>
      'ஆம்புலன்ஸுக்கு 108 அல்லது அவசர சேவைகளுக்கு 112 என்று அழைக்கவும்';

  @override
  String get skinAnalysis => 'தோல் பகுப்பாய்வு';

  @override
  String get eyeAnalysis => 'கண் ஆரோக்கியம்';

  @override
  String get foodAnalysis => 'உணவு மற்றும் ஊட்டச்சத்து';

  @override
  String get emotionDetection => 'உணர்ச்சி நலன்';

  @override
  String get healthScore => 'ஆரோக்கிய மதிப்பெண்';

  @override
  String get recommendations => 'பரிந்துரைகள்';

  @override
  String get noHistoryYet =>
      'இன்னும் பகுப்பாய்வு வரலாறு இல்லை.\nமுதல் பகுப்பாய்வை தொடங்க + அழுத்தவும்.';

  @override
  String get darkMode => 'இருண்ட முறை';

  @override
  String get changeLanguage => 'மொழியை மாற்றவும்';

  @override
  String get logout => 'வெளியேறு';

  @override
  String get deleteAccount => 'கணக்கை நீக்கு';

  @override
  String get confirmLogout => 'நீங்கள் வெளியேற விரும்புகிறீர்களா?';

  @override
  String get cancel => 'ரத்து செய்';

  @override
  String get confirm => 'உறுதிப்படுத்து';

  @override
  String get loading => 'ஏற்றுகிறது...';

  @override
  String get retry => 'மீண்டும் முயற்சி';

  @override
  String get noInternetConnection =>
      'இணைய இணைப்பு இல்லை. சில அம்சங்கள் கிடைக்காமல் போகலாம்.';
}
