import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'features/settings/providers/settings_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  runApp(const ProviderScope(child: AIWellnessApp()));
}

/// Theme-mode provider — toggle light / dark / system.
final themeModeProvider = StateProvider<ThemeMode>((_) => ThemeMode.system);

class AIWellnessApp extends ConsumerWidget {
  const AIWellnessApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    // Sync Settings dark-mode toggle → app-level ThemeMode
    final isDark = ref.watch(darkModeProvider);
    final themeMode = isDark ? ThemeMode.dark : ThemeMode.light;

    return MaterialApp.router(
      title: 'AI Wellness Vision',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}