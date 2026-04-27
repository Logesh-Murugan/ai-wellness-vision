/// Bottom navigation shell — uses GoRouter location to synchronise index.
///
/// No setState() — the selected tab is derived from the current route.
library;

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class MainNavigationPage extends StatelessWidget {
  final Widget child;

  const MainNavigationPage({super.key, required this.child});

  static const _tabs = [
    _Tab(icon: Icons.home_outlined, activeIcon: Icons.home,
        label: 'Home', route: '/home'),
    _Tab(icon: Icons.camera_alt_outlined, activeIcon: Icons.camera_alt,
        label: 'Analyze', route: '/image-analysis'),
    _Tab(icon: Icons.chat_bubble_outline, activeIcon: Icons.chat_bubble,
        label: 'Chat', route: '/chat'),
    _Tab(icon: Icons.mic_none, activeIcon: Icons.mic,
        label: 'Voice', route: '/voice'),
    _Tab(icon: Icons.history_outlined, activeIcon: Icons.history,
        label: 'History', route: '/history'),
  ];

  int _indexFromLocation(String location) {
    for (int i = 0; i < _tabs.length; i++) {
      if (location.startsWith(_tabs[i].route)) return i;
    }
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    final currentIndex = _indexFromLocation(location);

    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (index) => context.go(_tabs[index].route),
        destinations: _tabs
            .map((t) => NavigationDestination(
                  icon: Icon(t.icon),
                  selectedIcon: Icon(t.activeIcon),
                  label: t.label,
                ))
            .toList(),
      ),
      floatingActionButton: currentIndex == 0
          ? FloatingActionButton(
              onPressed: () => _showQuickActions(context),
              child: const Icon(Icons.add),
            )
          : null,
    );
  }

  void _showQuickActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40, height: 4,
              decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2)),
            ),
            const SizedBox(height: 20),
            Text('Quick Actions',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _QuickBtn(Icons.camera_alt, 'Analyze', () {
                  Navigator.pop(context);
                  context.go('/image-analysis');
                }),
                _QuickBtn(Icons.chat, 'Chat', () {
                  Navigator.pop(context);
                  context.go('/chat');
                }),
                _QuickBtn(Icons.mic, 'Voice', () {
                  Navigator.pop(context);
                  context.go('/voice');
                }),
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }
}

class _Tab {
  final IconData icon;
  final IconData activeIcon;
  final String label;
  final String route;
  const _Tab({
    required this.icon,
    required this.activeIcon,
    required this.label,
    required this.route,
  });
}

class _QuickBtn extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _QuickBtn(this.icon, this.label, this.onTap);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 60, height: 60,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(30),
            ),
            child: Icon(icon,
                color: Theme.of(context).colorScheme.primary, size: 28),
          ),
          const SizedBox(height: 8),
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}