// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Telugu (`te`).
class AppLocalizationsTe extends AppLocalizations {
  AppLocalizationsTe([String locale = 'te']) : super(locale);

  @override
  String get appTitle => 'AI వెల్నెస్‌విజన్';

  @override
  String get appTagline => 'మీ ఆరోగ్యం, మీ భాషలో';

  @override
  String welcomeMessage(String name) {
    return 'తిరిగి స్వాగతం, $name!';
  }

  @override
  String get imageAnalysis => 'చిత్ర విశ్లేషణ';

  @override
  String get aiChat => 'AI ఆరోగ్య చాట్';

  @override
  String get voiceAssistant => 'వాయిస్ అసిస్టెంట్';

  @override
  String get history => 'చరిత్ర';

  @override
  String get profile => 'ప్రొఫైల్';

  @override
  String get settings => 'సెట్టింగులు';

  @override
  String get analysisPending => 'మీ చిత్రాన్ని విశ్లేషిస్తున్నాం...';

  @override
  String get analysisComplete => 'విశ్లేషణ పూర్తయింది';

  @override
  String get analysisError => 'విశ్లేషణ విఫలమైంది. దయచేసి మళ్ళీ ప్రయత్నించండి.';

  @override
  String get chatPlaceholder => 'మీ ఆరోగ్యం గురించి అడగండి...';

  @override
  String get chatDisclaimer =>
      'AI సమాధానాలు కేవలం సమాచారం కోసం మాత్రమే. వైద్య సలహా కోసం డాక్టర్‌ని సంప్రదించండి.';

  @override
  String get emergencyTitle => 'వైద్య అత్యవసరమా?';

  @override
  String get emergencyInfo =>
      'అంబులెన్స్ కోసం 108 లేదా అత్యవసర సేవలకు 112 కి కాల్ చేయండి';

  @override
  String get skinAnalysis => 'చర్మ విశ్లేషణ';

  @override
  String get eyeAnalysis => 'కంటి ఆరోగ్యం';

  @override
  String get foodAnalysis => 'ఆహారం మరియు పోషణ';

  @override
  String get emotionDetection => 'భావోద్వేగ ఆరోగ్యం';

  @override
  String get healthScore => 'ఆరోగ్య స్కోర్';

  @override
  String get recommendations => 'సిఫార్సులు';

  @override
  String get noHistoryYet =>
      'ఇంకా విశ్లేషణ చరిత్ర లేదు.\nమీ మొదటి విశ్లేషణ ప్రారంభించడానికి + నొక్కండి.';

  @override
  String get darkMode => 'డార్క్ మోడ్';

  @override
  String get changeLanguage => 'భాష మార్చండి';

  @override
  String get logout => 'లాగ్ అవుట్';

  @override
  String get deleteAccount => 'ఖాతా తొలగించు';

  @override
  String get confirmLogout => 'మీరు నిజంగా లాగ్ అవుట్ చేయాలనుకుంటున్నారా?';

  @override
  String get cancel => 'రద్దు చేయి';

  @override
  String get confirm => 'నిర్ధారించు';

  @override
  String get loading => 'లోడవుతోంది...';

  @override
  String get retry => 'మళ్ళీ ప్రయత్నించు';

  @override
  String get noInternetConnection =>
      'ఇంటర్నెట్ కనెక్షన్ లేదు. కొన్ని ఫీచర్లు అందుబాటులో ఉండకపోవచ్చు.';
}
