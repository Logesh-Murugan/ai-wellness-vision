// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Hindi (`hi`).
class AppLocalizationsHi extends AppLocalizations {
  AppLocalizationsHi([String locale = 'hi']) : super(locale);

  @override
  String get appTitle => 'AI वेलनेसविज़न';

  @override
  String get appTagline => 'आपका स्वास्थ्य, आपकी भाषा में';

  @override
  String welcomeMessage(String name) {
    return 'वापस स्वागत है, $name!';
  }

  @override
  String get imageAnalysis => 'छवि विश्लेषण';

  @override
  String get aiChat => 'AI स्वास्थ्य चैट';

  @override
  String get voiceAssistant => 'वॉयस असिस्टेंट';

  @override
  String get history => 'इतिहास';

  @override
  String get profile => 'प्रोफ़ाइल';

  @override
  String get settings => 'सेटिंग्स';

  @override
  String get analysisPending => 'आपकी छवि का विश्लेषण हो रहा है...';

  @override
  String get analysisComplete => 'विश्लेषण पूर्ण';

  @override
  String get analysisError => 'विश्लेषण विफल हुआ। कृपया पुनः प्रयास करें।';

  @override
  String get chatPlaceholder => 'अपने स्वास्थ्य के बारे में पूछें...';

  @override
  String get chatDisclaimer =>
      'AI उत्तर केवल जानकारी के लिए हैं। चिकित्सा सलाह के लिए डॉक्टर से मिलें।';

  @override
  String get emergencyTitle => 'चिकित्सा आपात स्थिति?';

  @override
  String get emergencyInfo =>
      'एम्बुलेंस के लिए 108 या आपातकालीन सेवाओं के लिए 112 पर कॉल करें';

  @override
  String get skinAnalysis => 'त्वचा विश्लेषण';

  @override
  String get eyeAnalysis => 'आँख का स्वास्थ्य';

  @override
  String get foodAnalysis => 'भोजन और पोषण';

  @override
  String get emotionDetection => 'भावनात्मक स्वास्थ्य';

  @override
  String get healthScore => 'स्वास्थ्य स्कोर';

  @override
  String get recommendations => 'सिफारिशें';

  @override
  String get noHistoryYet =>
      'अभी तक कोई विश्लेषण इतिहास नहीं।\nपहला विश्लेषण शुरू करने के लिए + दबाएं।';

  @override
  String get darkMode => 'डार्क मोड';

  @override
  String get changeLanguage => 'भाषा बदलें';

  @override
  String get logout => 'लॉग आउट';

  @override
  String get deleteAccount => 'खाता हटाएं';

  @override
  String get confirmLogout => 'क्या आप वाकई लॉग आउट करना चाहते हैं?';

  @override
  String get cancel => 'रद्द करें';

  @override
  String get confirm => 'पुष्टि करें';

  @override
  String get loading => 'लोड हो रहा है...';

  @override
  String get retry => 'पुनः प्रयास करें';

  @override
  String get noInternetConnection =>
      'इंटरनेट कनेक्शन नहीं है। कुछ सुविधाएँ अनुपलब्ध हो सकती हैं।';
}
