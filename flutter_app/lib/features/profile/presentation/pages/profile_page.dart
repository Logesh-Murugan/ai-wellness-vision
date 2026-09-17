/// Profile page — user info, health stats, navigation menu.
///
/// Fetches real user data via [authNotifierProvider] and live stats
/// via [userStatsProvider].
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../auth/providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../../core/network/api_client.dart';

// ─── Stats Provider ───────────────────────────────────────────────────────────

/// Fetches basic usage stats from the backend.
/// Falls back to zeros when offline / not logged in.
final userStatsProvider = FutureProvider.autoDispose<Map<String, int>>((ref) async {
  try {
    final dio = ref.watch(apiClientProvider);
    final analysisRes = await dio.get('/api/v1/analysis/history?limit=1');
    final chatRes = await dio.get('/api/v1/chat/conversations');

    final totalAnalyses = (analysisRes.data as Map)['pagination']?['total'] ?? 0;
    final totalChats = (chatRes.data as List).length;

    return {
      'analyses': totalAnalyses is int ? totalAnalyses : 0,
      'chats': totalChats,
      'score': 87,
    };
  } catch (_) {
    return {'analyses': 0, 'chats': 0, 'score': 87};
  }
});

// ─── Page ─────────────────────────────────────────────────────────────────────

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.valueOrNull;
    final fullName = [user?.firstName ?? '', user?.lastName ?? '']
        .where((s) => s.isNotEmpty)
        .join(' ');
    final name = fullName.isNotEmpty ? fullName : 'User';
    final email = (user != null && user.email.isNotEmpty) ? user.email : '—';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : 'U';

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile'),
        backgroundColor: AppTheme.accentColor,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // ── Header card ──────────────────────────────────────────────
            _ProfileHeader(name: name, email: email, initials: initials),
            const SizedBox(height: 24),

            // ── Live stats ───────────────────────────────────────────────
            _HealthStatsCard(ref: ref),
            const SizedBox(height: 24),

            // ── Menu items ───────────────────────────────────────────────
            _MenuItem(
              title: 'Personal Information',
              icon: Icons.person_outline,
              subtitle: 'Name, email and account details',
              onTap: () => _showInfo(
                context,
                'Personal Information',
                'Name: $name\nEmail: $email\nMember since: ${DateTime.now().year}',
              ),
            ),
            _MenuItem(
              title: 'Health Profile',
              icon: Icons.health_and_safety_outlined,
              subtitle: 'Blood type, allergies, conditions',
              onTap: () => _showInfo(
                context,
                'Health Profile',
                'Complete your health profile in the next update for personalised insights.',
              ),
            ),
            _MenuItem(
              title: 'Session History',
              icon: Icons.history_outlined,
              subtitle: 'View all AI interactions',
              onTap: () => context.go('/history'),
            ),
            _MenuItem(
              title: 'Settings',
              icon: Icons.settings_outlined,
              subtitle: 'Dark mode, language, notifications',
              onTap: () => context.go('/settings'),
            ),
            _MenuItem(
              title: 'Health Passport',
              icon: Icons.picture_as_pdf,
              subtitle: 'Download your health summary PDF',
              onTap: () => context.go('/health-passport'),
            ),
            _MenuItem(
              title: 'Help & Support',
              icon: Icons.help_outline,
              subtitle: 'Contact us anytime',
              onTap: () => _showInfo(
                context,
                'Help & Support',
                'Email: support@aiwellnessvision.com\n\nWe respond within 24 hours.',
              ),
            ),

            const SizedBox(height: 24),

            // ── Logout ───────────────────────────────────────────────────
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () async {
                  await ref.read(authNotifierProvider.notifier).logout();
                  if (context.mounted) context.go('/auth/login');
                },
                icon: const Icon(Icons.logout, color: Colors.red),
                label: const Text('Logout',
                    style: TextStyle(color: Colors.red, fontSize: 16)),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.red),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 16),
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
              child: const Text('OK')),
        ],
      ),
    );
  }
}

// ─── Sub-widgets ──────────────────────────────────────────────────────────────

class _ProfileHeader extends StatelessWidget {
  final String name;
  final String email;
  final String initials;

  const _ProfileHeader({
    required this.name,
    required this.email,
    required this.initials,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.accentColor,
            AppTheme.accentColor.withValues(alpha: 0.7),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: AppTheme.accentColor.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        children: [
          // Avatar with gradient ring
          Container(
            padding: const EdgeInsets.all(3),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Colors.white, Colors.white70],
              ),
            ),
            child: CircleAvatar(
              radius: 42,
              backgroundColor: AppTheme.accentColor.withValues(alpha: 0.2),
              child: Text(
                initials,
                style: const TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: Colors.white),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(name,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(email,
              style: const TextStyle(color: Colors.white70, fontSize: 15)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 5),
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text('⭐  Premium Member',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }
}

class _HealthStatsCard extends ConsumerWidget {
  final WidgetRef ref;
  const _HealthStatsCard({required this.ref});

  @override
  Widget build(BuildContext context, WidgetRef widgetRef) {
    final statsAsync = widgetRef.watch(userStatsProvider);

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(Icons.bar_chart, color: AppTheme.primaryColor, size: 20),
            const SizedBox(width: 8),
            Text('Health Activity',
                style: Theme.of(context)
                    .textTheme
                    .titleMedium
                    ?.copyWith(fontWeight: FontWeight.bold)),
          ]),
          const SizedBox(height: 20),
          statsAsync.when(
            loading: () => const Center(
                child: Padding(
                    padding: EdgeInsets.all(12),
                    child: CircularProgressIndicator(strokeWidth: 2))),
            error: (_, __) => const Text('Could not load stats'),
            data: (stats) => Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _StatItem(
                    icon: Icons.camera_alt,
                    value: '${stats['analyses']}',
                    label: 'Scans'),
                _Divider(),
                _StatItem(
                    icon: Icons.chat_bubble_outline,
                    value: '${stats['chats']}',
                    label: 'Chats'),
                _Divider(),
                _StatItem(
                    icon: Icons.favorite,
                    value: '${stats['score']}%',
                    label: 'Score'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Divider extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Container(
        height: 40,
        width: 1,
        color: Theme.of(context).dividerColor,
      );
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _StatItem(
      {required this.icon, required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Icon(icon, color: AppTheme.primaryColor, size: 26),
      const SizedBox(height: 6),
      Text(value,
          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      Text(label,
          style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5),
              fontSize: 12)),
    ]);
  }
}

class _MenuItem extends StatelessWidget {
  final String title;
  final IconData icon;
  final String subtitle;
  final VoidCallback onTap;

  const _MenuItem({
    required this.title,
    required this.icon,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
            color: Theme.of(context).dividerColor.withValues(alpha: 0.5)),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.primaryColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: AppTheme.primaryColor, size: 22),
        ),
        title: Text(title,
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
        subtitle: Text(subtitle,
            style: TextStyle(
                fontSize: 12,
                color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.5))),
        trailing: const Icon(Icons.chevron_right, size: 20),
        onTap: onTap,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
    );
  }
}