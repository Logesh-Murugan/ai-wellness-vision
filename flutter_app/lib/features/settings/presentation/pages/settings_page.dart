import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../shared/presentation/widgets/custom_app_bar.dart';
import '../widgets/settings_section.dart';
import '../widgets/settings_tile.dart';
import '../../providers/settings_provider.dart';
import '../../../auth/providers/auth_provider.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch all settings from persisted provider
    final settingsAsync = ref.watch(settingsProvider);

    return settingsAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(body: Center(child: Text('Error: $e'))),
      data: (settings) => _buildPage(context, ref, settings),
    );
  }

  Widget _buildPage(BuildContext context, WidgetRef ref, SettingsState settings) {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.valueOrNull;

    return Scaffold(
      appBar: const CustomAppBar(
        title: 'Settings',
        showBackButton: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Profile Section
            _buildProfileSection(context, user),

            const SizedBox(height: 24),

            // General Settings
            SettingsSection(
              title: 'General',
              children: [
                SettingsTile(
                  title: 'Language',
                  subtitle: AppConstants.languageNames[settings.language] ?? 'English',
                  leading: const Icon(Icons.language),
                  onTap: () => _showLanguageSelector(context, ref, settings.language),
                ),
                SettingsTile(
                  title: 'Dark Mode',
                  subtitle: settings.darkMode ? 'On' : 'Off',
                  leading: const Icon(Icons.dark_mode),
                  trailing: Switch(
                    value: settings.darkMode,
                    onChanged: (value) =>
                        ref.read(settingsProvider.notifier).setDarkMode(value),
                  ),
                ),
                SettingsTile(
                  title: 'Notifications',
                  subtitle: settings.notifications ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.notifications),
                  trailing: Switch(
                    value: settings.notifications,
                    onChanged: (value) =>
                        ref.read(settingsProvider.notifier).setNotifications(value),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Voice Settings
            SettingsSection(
              title: 'Voice & Audio',
              children: [
                SettingsTile(
                  title: 'Voice Features',
                  subtitle: settings.voiceEnabled ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.mic),
                  trailing: Switch(
                    value: settings.voiceEnabled,
                    onChanged: (value) =>
                        ref.read(settingsProvider.notifier).setVoiceEnabled(value),
                  ),
                ),
                if (settings.voiceEnabled) ...[
                  SettingsTile(
                    title: 'Voice Speed',
                    subtitle: '${settings.voiceSpeed.toStringAsFixed(1)}x',
                    leading: const Icon(Icons.speed),
                    onTap: () => _showVoiceSpeedSlider(context, ref, settings.voiceSpeed),
                  ),
                ],
              ],
            ),

            const SizedBox(height: 24),

            // Privacy Settings
            SettingsSection(
              title: 'Privacy & Security',
              children: [
                SettingsTile(
                  title: 'Analytics',
                  subtitle: settings.analytics ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.analytics),
                  trailing: Switch(
                    value: settings.analytics,
                    onChanged: (value) =>
                        ref.read(settingsProvider.notifier).setAnalytics(value),
                  ),
                ),
                SettingsTile(
                  title: 'Clear All Data',
                  subtitle: 'Reset settings to defaults',
                  leading: const Icon(Icons.delete_outline),
                  onTap: () => _showClearHistoryDialog(context, ref),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // About Section
            SettingsSection(
              title: 'About',
              children: [
                SettingsTile(
                  title: 'Version',
                  subtitle: AppConstants.appVersion,
                  leading: const Icon(Icons.info),
                ),
                SettingsTile(
                  title: 'Privacy Policy',
                  subtitle: 'View our privacy policy',
                  leading: const Icon(Icons.privacy_tip),
                  onTap: () => _showInfo(context, 'Privacy Policy',
                      'Your health data is stored securely and never shared with third parties without your consent.'),
                ),
                SettingsTile(
                  title: 'Terms of Service',
                  subtitle: 'View terms and conditions',
                  leading: const Icon(Icons.description),
                  onTap: () => _showInfo(context, 'Terms of Service',
                      'By using this app you agree to our terms. This app provides AI-based wellness insights for informational purposes only.'),
                ),
                SettingsTile(
                  title: 'Help & Support',
                  subtitle: 'Contact us',
                  leading: const Icon(Icons.help),
                  onTap: () => _showInfo(
                      context, 'Help & Support', 'Email: support@aiwellnessvision.com\nWe typically respond within 24 hours.'),
                ),
              ],
            ),

            const SizedBox(height: 32),

            // Medical Disclaimer
            _buildMedicalDisclaimer(context),

            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileSection(BuildContext context, dynamic user) {
    final name = user != null
        ? '${user.firstName} ${user.lastName}'.trim()
        : 'Demo User';
    final email = user?.email ?? 'demo@wellnessvision.ai';
    final initials = name.isNotEmpty ? name[0].toUpperCase() : 'D';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary.withValues(alpha: 0.12),
            Theme.of(context).colorScheme.secondary.withValues(alpha: 0.12),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 30,
            backgroundColor: Theme.of(context).colorScheme.primary,
            child: Text(
              initials,
              style: const TextStyle(
                  color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name,
                    style: Theme.of(context)
                        .textTheme
                        .titleLarge
                        ?.copyWith(fontWeight: FontWeight.bold)),
                const SizedBox(height: 2),
                Text(email,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context)
                            .colorScheme
                            .onSurface
                            .withValues(alpha: 0.6))),
                const SizedBox(height: 8),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text('Active Member',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.green[700],
                          fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMedicalDisclaimer(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border:
            Border.all(color: Colors.orange.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber, color: Colors.orange[700], size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Medical Disclaimer',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        color: Colors.orange[800],
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(AppConstants.medicalDisclaimer,
                    style: Theme.of(context)
                        .textTheme
                        .bodySmall
                        ?.copyWith(color: Colors.orange[800])),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showLanguageSelector(
      BuildContext context, WidgetRef ref, String currentLang) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Select Language',
                style: Theme.of(ctx)
                    .textTheme
                    .titleLarge
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            ...AppConstants.languageNames.entries.map((entry) => ListTile(
                  title: Text(entry.value),
                  leading: Radio<String>(
                    value: entry.key,
                    groupValue: currentLang,
                    onChanged: (v) {
                      if (v != null) {
                        ref.read(settingsProvider.notifier).setLanguage(v);
                        Navigator.pop(ctx);
                      }
                    },
                  ),
                  onTap: () {
                    ref.read(settingsProvider.notifier).setLanguage(entry.key);
                    Navigator.pop(ctx);
                  },
                )),
          ],
        ),
      ),
    );
  }

  void _showVoiceSpeedSlider(
      BuildContext context, WidgetRef ref, double currentSpeed) {
    double speed = currentSpeed;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Voice Speed'),
        content: StatefulBuilder(
          builder: (ctx2, setS) => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('${speed.toStringAsFixed(1)}x',
                  style: Theme.of(ctx2).textTheme.headlineSmall),
              Slider(
                value: speed,
                min: 0.5,
                max: 2.0,
                divisions: 6,
                label: '${speed.toStringAsFixed(1)}x',
                onChanged: (v) => setS(() => speed = v),
                onChangeEnd: (v) =>
                    ref.read(settingsProvider.notifier).setVoiceSpeed(v),
              ),
              Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('0.5x',
                        style: Theme.of(ctx2).textTheme.bodySmall),
                    Text('2.0x',
                        style: Theme.of(ctx2).textTheme.bodySmall),
                  ]),
            ],
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Done')),
        ],
      ),
    );
  }

  void _showClearHistoryDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Reset Settings'),
        content: const Text(
            'Reset all settings to defaults? This will clear your preferences.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await ref.read(settingsProvider.notifier).resetAll();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Settings reset to defaults')));
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }

  void _showInfo(BuildContext context, String title, String content) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: Text(content),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('Close')),
        ],
      ),
    );
  }
}