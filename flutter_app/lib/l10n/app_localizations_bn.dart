// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Bengali Bangla (`bn`).
class AppLocalizationsBn extends AppLocalizations {
  AppLocalizationsBn([String locale = 'bn']) : super(locale);

  @override
  String get appTitle => 'AI ওয়েলনেসভিশন';

  @override
  String get appTagline => 'আপনার স্বাস্থ্য, আপনার ভাষায়';

  @override
  String welcomeMessage(String name) {
    return 'ফিরে স্বাগতম, $name!';
  }

  @override
  String get imageAnalysis => 'ছবি বিশ্লেষণ';

  @override
  String get aiChat => 'AI স্বাস্থ্য চ্যাট';

  @override
  String get voiceAssistant => 'ভয়েস অ্যাসিস্ট্যান্ট';

  @override
  String get history => 'ইতিহাস';

  @override
  String get profile => 'প্রোফাইল';

  @override
  String get settings => 'সেটিংস';

  @override
  String get analysisPending => 'আপনার ছবি বিশ্লেষণ করা হচ্ছে...';

  @override
  String get analysisComplete => 'বিশ্লেষণ সম্পন্ন';

  @override
  String get analysisError => 'বিশ্লেষণ ব্যর্থ হয়েছে। আবার চেষ্টা করুন।';

  @override
  String get chatPlaceholder => 'আপনার স্বাস্থ্য সম্পর্কে জিজ্ঞেস করুন...';

  @override
  String get chatDisclaimer =>
      'AI উত্তর শুধুমাত্র তথ্যের জন্য। চিকিৎসা পরামর্শের জন্য ডাক্তারের সাথে পরামর্শ করুন।';

  @override
  String get emergencyTitle => 'চিকিৎসা জরুরি অবস্থা?';

  @override
  String get emergencyInfo =>
      'অ্যাম্বুলেন্সের জন্য 108 অথবা জরুরি সেবার জন্য 112 তে কল করুন';

  @override
  String get skinAnalysis => 'ত্বক বিশ্লেষণ';

  @override
  String get eyeAnalysis => 'চোখের স্বাস্থ্য';

  @override
  String get foodAnalysis => 'খাবার ও পুষ্টি';

  @override
  String get emotionDetection => 'আবেগীয় সুস্থতা';

  @override
  String get healthScore => 'স্বাস্থ্য স্কোর';

  @override
  String get recommendations => 'সুপারিশ';

  @override
  String get noHistoryYet =>
      'এখনও কোনো বিশ্লেষণ ইতিহাস নেই।\nপ্রথম বিশ্লেষণ শুরু করতে + চাপুন।';

  @override
  String get darkMode => 'ডার্ক মোড';

  @override
  String get changeLanguage => 'ভাষা পরিবর্তন করুন';

  @override
  String get logout => 'লগ আউট';

  @override
  String get deleteAccount => 'অ্যাকাউন্ট মুছুন';

  @override
  String get confirmLogout => 'আপনি কি সত্যিই লগ আউট করতে চান?';

  @override
  String get cancel => 'বাতিল করুন';

  @override
  String get confirm => 'নিশ্চিত করুন';

  @override
  String get loading => 'লোড হচ্ছে...';

  @override
  String get retry => 'আবার চেষ্টা করুন';

  @override
  String get noInternetConnection =>
      'ইন্টারনেট সংযোগ নেই। কিছু সুবিধা অনুপলব্ধ হতে পারে।';
}
