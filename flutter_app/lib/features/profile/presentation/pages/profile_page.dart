/// Profile page — user info, health stats, menu.
///
/// Uses [ConsumerWidget] + [authProvider] for user data.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../auth/providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(authProvider);
    final user = auth.user;
    final name = user?.name ?? 'User';
    final email = user?.email ?? 'user@email.com';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        backgroundColor: AppTheme.accentColor,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(25),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppTheme.accentColor, AppTheme.accentColor.withOpacity(0.7)],
                ),
                borderRadius: BorderRadius.circular(15),
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 40,
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, size: 40, color: AppTheme.accentColor),
                  ),
                  const SizedBox(height: 15),
                  Text(name,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold)),
                  Text(email,
                      style: const TextStyle(color: Colors.white70, fontSize: 16)),
                ],
              ),
            ),
            const SizedBox(height: 30),

            // Stats
            _HealthStats(),
            const SizedBox(height: 30),

            // Menu
            _MenuItem(
              title: 'Personal Information',
              icon: Icons.person_outline,
              onTap: () => _showInfo(context, 'Personal Information',
                  'Name: $name\nEmail: $email'),
            ),
            _MenuItem(
              title: 'Health Profile',
              icon: Icons.health_and_safety_outlined,
              onTap: () => _showInfo(context, 'Health Profile',
                  'Blood Type: O+\nAllergies: None'),
            ),
            _MenuItem(
              title: 'Settings',
              icon: Icons.settings_outlined,
              onTap: () => context.go('/settings'),
            ),
            _MenuItem(
              title: 'Help & Support',
              icon: Icons.help_outline,
              onTap: () => _showInfo(context, 'Help & Support',
                  'Email: support@aiwellnessvision.com'),
            ),
            const SizedBox(height: 20),

            // Logout
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () async {
                  await ref.read(authProvider.notifier).logout();
                  if (context.mounted) context.go('/login');
                },
                icon: const Icon(Icons.logout, color: Colors.red),
                label: const Text('Logout', style: TextStyle(color: Colors.red)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.red),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showInfo(BuildContext context, String title, String content) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}

class _HealthStats extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Health Overview',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 15),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _Stat(icon: Icons.analytics, value: '24', label: 'Analyses'),
              _Stat(icon: Icons.chat, value: '156', label: 'Chats'),
              _Stat(icon: Icons.favorite, value: '87%', label: 'Score'),
            ],
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _Stat({required this.icon, required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Icon(icon, color: AppTheme.accentColor, size: 30),
      const SizedBox(height: 5),
      Text(value,
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
      Text(label, style: const TextStyle(color: Colors.grey)),
    ]);
  }
}

class _MenuItem extends StatelessWidget {
  final String title;
  final IconData icon;
  final VoidCallback onTap;

  const _MenuItem(
      {required this.title, required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(icon, color: AppTheme.accentColor),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        tileColor: Theme.of(context).cardColor,
      ),
    );
  }
}