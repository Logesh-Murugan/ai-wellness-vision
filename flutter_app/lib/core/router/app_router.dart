import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_app/features/auth/providers/auth_provider.dart';

import 'package:flutter_app/features/home/presentation/home_page.dart';
import 'package:flutter_app/features/image_analysis/presentation/image_analysis_page.dart';
import 'package:flutter_app/features/chat/presentation/chat_page.dart';
import 'package:flutter_app/features/voice/presentation/voice_page.dart';
import 'package:flutter_app/features/profile/presentation/pages/profile_page.dart';
import 'package:flutter_app/features/auth/presentation/login_page.dart';
import 'package:flutter_app/features/auth/presentation/register_page.dart';

part 'app_router.g.dart';

// Splash page
class SplashPage extends StatelessWidget { 
  const SplashPage({super.key}); 
  @override 
  Widget build(BuildContext context) => const Scaffold(body: Center(child: CircularProgressIndicator())); 
}

class ScaffoldWithNavBar extends StatelessWidget {
  final Widget child;
  const ScaffoldWithNavBar({super.key, required this.child});
  
  @override
  Widget build(BuildContext context) {
    // Determine current index from route
    int currentIndex = 0;
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/home')) currentIndex = 0;
    if (location.startsWith('/analysis')) currentIndex = 1;
    if (location.startsWith('/chat')) currentIndex = 2;
    if (location.startsWith('/voice')) currentIndex = 3;
    if (location.startsWith('/profile')) currentIndex = 4;

    return Scaffold(
      body: child, 
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: currentIndex,
        type: BottomNavigationBarType.fixed,
        onTap: (index) {
          switch (index) {
            case 0: context.go('/home'); break;
            case 1: context.go('/analysis'); break;
            case 2: context.go('/chat'); break;
            case 3: context.go('/voice'); break;
            case 4: context.go('/profile'); break;
          }
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.camera_alt), label: 'Analysis'),
          BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Chat'),
          BottomNavigationBarItem(icon: Icon(Icons.mic), label: 'Voice'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
        ]
      )
    );
  }
}

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

@riverpod
GoRouter router(RouterRef ref) {
  final isAuthenticated = ref.watch(isAuthenticatedProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    redirect: (context, state) {
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      final isSplashRoute = state.matchedLocation == '/splash';

      if (!isAuthenticated) {
        if (!isAuthRoute && !isSplashRoute) {
          return '/auth/login';
        }
      } else {
        if (isAuthRoute || isSplashRoute) {
          return '/home';
        }
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashPage(),
      ),
      GoRoute(
        path: '/auth/login',
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: '/auth/register',
        builder: (context, state) => const RegisterPage(),
      ),
      
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          return ScaffoldWithNavBar(child: child);
        },
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const HomePage(),
          ),
          GoRoute(
            path: '/analysis',
            builder: (context, state) => const ImageAnalysisPage(),
          ),
          GoRoute(
            path: '/chat',
            builder: (context, state) => const ChatPage(),
          ),
          GoRoute(
            path: '/voice',
            builder: (context, state) => const VoicePage(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfilePage(),
          ),
        ],
      ),
    ],
  );
}