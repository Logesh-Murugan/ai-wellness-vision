import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_app/features/auth/providers/auth_provider.dart';

part 'app_router.g.dart';

// Dummy placeholder screens to satisfy the router
class ScaffoldWithNavBar extends StatelessWidget {
  final Widget child;
  const ScaffoldWithNavBar({super.key, required this.child});
  @override
  Widget build(BuildContext context) => Scaffold(body: child, bottomNavigationBar: const BottomNavigationBar(items: []));
}
class SplashScreen extends StatelessWidget { const SplashScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class LoginScreen extends StatelessWidget { const LoginScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class RegisterScreen extends StatelessWidget { const RegisterScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class HomeScreen extends StatelessWidget { const HomeScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class AnalysisScreen extends StatelessWidget { const AnalysisScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class ChatScreen extends StatelessWidget { const ChatScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class VoiceScreen extends StatelessWidget { const VoiceScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class HistoryScreen extends StatelessWidget { const HistoryScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }
class ProfileScreen extends StatelessWidget { const ProfileScreen({super.key}); @override Widget build(BuildContext context) => const Scaffold(); }

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

@riverpod
GoRouter router(RouterRef ref) {
  // Watch the authentication status to dynamically trigger redirects
  final isAuthenticated = ref.watch(isAuthenticatedProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    // The redirect acts as our global navigation guard
    redirect: (context, state) {
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      final isSplashRoute = state.matchedLocation == '/splash';

      if (!isAuthenticated) {
        // If unauthenticated and not already on a public route, force them to login
        if (!isAuthRoute && !isSplashRoute) {
          return '/auth/login';
        }
      } else {
        // If authenticated but trying to access login/register/splash, redirect to home
        if (isAuthRoute || isSplashRoute) {
          return '/home';
        }
      }
      // No redirect needed
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/auth/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/register',
        builder: (context, state) => const RegisterScreen(),
      ),
      
      // ShellRoute wraps our main authenticated pages in a persistent Bottom Nav Bar
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          return ScaffoldWithNavBar(child: child);
        },
        routes: [
          GoRoute(
            path: '/home',
            builder: (context, state) => const HomeScreen(),
          ),
          GoRoute(
            path: '/analysis',
            builder: (context, state) => const AnalysisScreen(),
          ),
          GoRoute(
            path: '/chat',
            builder: (context, state) => const ChatScreen(),
          ),
          GoRoute(
            path: '/voice',
            builder: (context, state) => const VoiceScreen(),
          ),
          GoRoute(
            path: '/history',
            builder: (context, state) => const HistoryScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (context, state) => const ProfileScreen(),
          ),
        ],
      ),
    ],
  );
}