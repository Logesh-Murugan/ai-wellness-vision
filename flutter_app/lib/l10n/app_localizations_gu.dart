// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Gujarati (`gu`).
class AppLocalizationsGu extends AppLocalizations {
  AppLocalizationsGu([String locale = 'gu']) : super(locale);

  @override
  String get appTitle => 'AI વેલનેસવિઝન';

  @override
  String get appTagline => 'તમારું સ્વાસ્થ્ય, તમારી ભાષામાં';

  @override
  String welcomeMessage(String name) {
    return 'પાછા સ્વાગત છે, $name!';
  }

  @override
  String get imageAnalysis => 'છબી વિશ્લેષણ';

  @override
  String get aiChat => 'AI આરોગ્ય ચેટ';

  @override
  String get voiceAssistant => 'વૉઇસ આસિસ્ટન્ટ';

  @override
  String get history => 'ઇતિહાસ';

  @override
  String get profile => 'પ્રોફાઇલ';

  @override
  String get settings => 'સેટિંગ્સ';

  @override
  String get analysisPending => 'તમારી છબીનું વિશ્લેષણ થઈ રહ્યું છે...';

  @override
  String get analysisComplete => 'વિશ્લેષણ પૂર્ણ';

  @override
  String get analysisError =>
      'વિશ્લેષણ નિષ્ફળ ગયું. કૃપા કરીને ફરી પ્રયાસ કરો.';

  @override
  String get chatPlaceholder => 'તમારા સ્વાસ્થ્ય વિશે પૂછો...';

  @override
  String get chatDisclaimer =>
      'AI ના જવાબો માત્ર માહિતી માટે છે. તબીબી સલાહ માટે ડૉક્ટરની સલાહ લો.';

  @override
  String get emergencyTitle => 'તબીબી કટોકટી?';

  @override
  String get emergencyInfo =>
      'એમ્બ્યુલન્સ માટે 108 અથવા કટોકટી સેવાઓ માટે 112 પર કૉલ કરો';

  @override
  String get skinAnalysis => 'ત્વચા વિશ્લેષણ';

  @override
  String get eyeAnalysis => 'આંખનું સ્વાસ્થ્ય';

  @override
  String get foodAnalysis => 'ખોરાક અને પોષણ';

  @override
  String get emotionDetection => 'ભાવનાત્મક સ્વાસ્થ્ય';

  @override
  String get healthScore => 'આરોગ્ય સ્કોર';

  @override
  String get recommendations => 'ભલામણો';

  @override
  String get noHistoryYet =>
      'હજી કોઈ વિશ્લેષણ ઇતિહાસ નથી.\nપ્રથમ વિશ્લેષણ શરૂ કરવા માટે + દબાવો.';

  @override
  String get darkMode => 'ડાર્ક મોડ';

  @override
  String get changeLanguage => 'ભાષા બદલો';

  @override
  String get logout => 'લૉગ આઉટ';

  @override
  String get deleteAccount => 'ખાતું કાઢી નાખો';

  @override
  String get confirmLogout => 'શું તમે ખરેખર લૉગ આઉટ કરવા માંગો છો?';

  @override
  String get cancel => 'રદ કરો';

  @override
  String get confirm => 'પુષ્ટિ કરો';

  @override
  String get loading => 'લોડ થઈ રહ્યું છે...';

  @override
  String get retry => 'ફરી પ્રયાસ કરો';

  @override
  String get noInternetConnection =>
      'ઇન્ટરનેટ કનેક્શન નથી. કેટલીક સુવિધાઓ અનુપલબ્ધ હોઈ શકે છે.';
}
