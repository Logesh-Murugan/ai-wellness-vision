// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Marathi (`mr`).
class AppLocalizationsMr extends AppLocalizations {
  AppLocalizationsMr([String locale = 'mr']) : super(locale);

  @override
  String get appTitle => 'AI वेलनेसव्हिजन';

  @override
  String get appTagline => 'तुमचे आरोग्य, तुमच्या भाषेत';

  @override
  String welcomeMessage(String name) {
    return 'परत स्वागत आहे, $name!';
  }

  @override
  String get imageAnalysis => 'प्रतिमा विश्लेषण';

  @override
  String get aiChat => 'AI आरोग्य चॅट';

  @override
  String get voiceAssistant => 'व्हॉइस असिस्टंट';

  @override
  String get history => 'इतिहास';

  @override
  String get profile => 'प्रोफाइल';

  @override
  String get settings => 'सेटिंग्ज';

  @override
  String get analysisPending => 'तुमच्या प्रतिमेचे विश्लेषण होत आहे...';

  @override
  String get analysisComplete => 'विश्लेषण पूर्ण';

  @override
  String get analysisError =>
      'विश्लेषण अयशस्वी झाले. कृपया पुन्हा प्रयत्न करा.';

  @override
  String get chatPlaceholder => 'तुमच्या आरोग्याबद्दल विचारा...';

  @override
  String get chatDisclaimer =>
      'AI उत्तरे केवळ माहितीसाठी आहेत. वैद्यकीय सल्ल्यासाठी डॉक्टरांशी संपर्क साधा.';

  @override
  String get emergencyTitle => 'वैद्यकीय आणीबाणी?';

  @override
  String get emergencyInfo =>
      'रुग्णवाहिकेसाठी 108 किंवा आणीबाणी सेवांसाठी 112 वर कॉल करा';

  @override
  String get skinAnalysis => 'त्वचा विश्लेषण';

  @override
  String get eyeAnalysis => 'डोळ्यांचे आरोग्य';

  @override
  String get foodAnalysis => 'अन्न आणि पोषण';

  @override
  String get emotionDetection => 'भावनिक आरोग्य';

  @override
  String get healthScore => 'आरोग्य स्कोर';

  @override
  String get recommendations => 'शिफारसी';

  @override
  String get noHistoryYet =>
      'अद्याप कोणताही विश्लेषण इतिहास नाही.\nपहिले विश्लेषण सुरू करण्यासाठी + दाबा.';

  @override
  String get darkMode => 'डार्क मोड';

  @override
  String get changeLanguage => 'भाषा बदला';

  @override
  String get logout => 'लॉग आउट';

  @override
  String get deleteAccount => 'खाते हटवा';

  @override
  String get confirmLogout => 'तुम्हाला खरोखर लॉग आउट करायचे आहे का?';

  @override
  String get cancel => 'रद्द करा';

  @override
  String get confirm => 'पुष्टी करा';

  @override
  String get loading => 'लोड होत आहे...';

  @override
  String get retry => 'पुन्हा प्रयत्न करा';

  @override
  String get noInternetConnection =>
      'इंटरनेट कनेक्शन नाही. काही वैशिष्ट्ये अनुपलब्ध असू शकतात.';
}
