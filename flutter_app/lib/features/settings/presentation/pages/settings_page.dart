import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../shared/presentation/widgets/custom_app_bar.dart';
import '../widgets/settings_section.dart';
import '../widgets/settings_tile.dart';

class SettingsPage extends ConsumerStatefulWidget {
  const SettingsPage({super.key});

  @override
  ConsumerState<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends ConsumerState<SettingsPage> {
  String _selectedLanguage = 'en';
  String _selectedTheme = 'system';
  bool _notificationsEnabled = true;
  bool _voiceEnabled = true;
  bool _analyticsEnabled = true;
  double _voiceSpeed = 1.0;

  @override
  Widget build(BuildContext context) {
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
            _buildProfileSection(),
            
            const SizedBox(height: 24),
            
            // General Settings
            SettingsSection(
              title: 'General',
              children: [
                SettingsTile(
                  title: 'Language',
                  subtitle: AppConstants.languageNames[_selectedLanguage] ?? 'English',
                  leading: const Icon(Icons.language),
                  onTap: _showLanguageSelector,
                ),
                SettingsTile(
                  title: 'Theme',
                  subtitle: _getThemeLabel(_selectedTheme),
                  leading: const Icon(Icons.palette),
                  onTap: _showThemeSelector,
                ),
                SettingsTile(
                  title: 'Notifications',
                  subtitle: _notificationsEnabled ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.notifications),
                  trailing: Switch(
                    value: _notificationsEnabled,
                    onChanged: (value) {
                      setState(() {
                        _notificationsEnabled = value;
                      });
                    },
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
                  subtitle: _voiceEnabled ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.mic),
                  trailing: Switch(
                    value: _voiceEnabled,
                    onChanged: (value) {
                      setState(() {
                        _voiceEnabled = value;
                      });
                    },
                  ),
                ),
                if (_voiceEnabled) ...[
                  SettingsTile(
                    title: 'Voice Speed',
                    subtitle: '${_voiceSpeed.toStringAsFixed(1)}x',
                    leading: const Icon(Icons.speed),
                    onTap: _showVoiceSpeedSlider,
                  ),
                  SettingsTile(
                    title: 'Voice Type',
                    subtitle: 'Female',
                    leading: const Icon(Icons.person),
                    onTap: _showVoiceTypeSelector,
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
                  subtitle: _analyticsEnabled ? 'Enabled' : 'Disabled',
                  leading: const Icon(Icons.analytics),
                  trailing: Switch(
                    value: _analyticsEnabled,
                    onChanged: (value) {
                      setState(() {
                        _analyticsEnabled = value;
                      });
                    },
                  ),
                ),
                SettingsTile(
                  title: 'Data Export',
                  subtitle: 'Download your data',
                  leading: const Icon(Icons.download),
                  onTap: _exportData,
                ),
                SettingsTile(
                  title: 'Clear History',
                  subtitle: 'Remove all stored data',
                  leading: const Icon(Icons.delete_outline),
                  onTap: _showClearHistoryDialog,
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
                  onTap: _showPrivacyPolicy,
                ),
                SettingsTile(
                  title: 'Terms of Service',
                  subtitle: 'View terms and conditions',
                  leading: const Icon(Icons.description),
                  onTap: _showTermsOfService,
                ),
                SettingsTile(
                  title: 'Help & Support',
                  subtitle: 'Get help and contact support',
                  leading: const Icon(Icons.help),
                  onTap: _showHelpAndSupport,
                ),
              ],
            ),
            
            const SizedBox(height: 32),
            
            // Medical Disclaimer
            _buildMedicalDisclaimer(),
          ],
        ),
      ),
    );
  }
  
  Widget _buildProfileSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary.withOpacity(0.1),
            Theme.of(context).colorScheme.secondary.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          // Avatar
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.person,
              color: Colors.white,
              size: 32,
            ),
          ),
          
          const SizedBox(width: 16),
          
          // User info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Demo User',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'demo@wellnessvision.ai',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'Premium User',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.green,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          // Edit button
          IconButton(
            onPressed: _editProfile,
            icon: const Icon(Icons.edit),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMedicalDisclaimer() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.withOpacity(0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            Icons.warning_amber,
            color: Colors.orange[700],
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Medical Disclaimer',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    color: Colors.orange[800],
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  AppConstants.medicalDisclaimer,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.orange[800],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  void _showLanguageSelector() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select Language',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            ...AppConstants.languageNames.entries.map((entry) {
              return ListTile(
                title: Text(entry.value),
                leading: Radio<String>(
                  value: entry.key,
                  groupValue: _selectedLanguage,
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _selectedLanguage = value;
                      });
                      Navigator.pop(context);
                    }
                  },
                ),
                onTap: () {
                  setState(() {
                    _selectedLanguage = entry.key;
                  });
                  Navigator.pop(context);
                },
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
  
  void _showThemeSelector() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Select Theme',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            ...['light', 'dark', 'system'].map((theme) {
              return ListTile(
                title: Text(_getThemeLabel(theme)),
                leading: Radio<String>(
                  value: theme,
                  groupValue: _selectedTheme,
                  onChanged: (value) {
                    if (value != null) {
                      setState(() {
                        _selectedTheme = value;
                      });
                      Navigator.pop(context);
                    }
                  },
                ),
                onTap: () {
                  setState(() {
                    _selectedTheme = theme;
                  });
                  Navigator.pop(context);
                },
              );
            }).toList(),
          ],
        ),
      ),
    );
  }
  
  void _showVoiceSpeedSlider() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Voice Speed'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('${_voiceSpeed.toStringAsFixed(1)}x'),
            Slider(
              value: _voiceSpeed,
              min: 0.5,
              max: 2.0,
              divisions: 6,
              onChanged: (value) {
                setState(() {
                  _voiceSpeed = value;
                });
              },
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('0.5x', style: Theme.of(context).textTheme.bodySmall),
                Text('2.0x', style: Theme.of(context).textTheme.bodySmall),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }
  
  void _showVoiceTypeSelector() {
    // TODO: Implement voice type selector
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Voice type selector coming soon!')),
    );
  }
  
  void _exportData() {
    // TODO: Implement data export
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Data export feature coming soon!')),
    );
  }
  
  void _showClearHistoryDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear History'),
        content: const Text('Are you sure you want to clear all history? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('History cleared successfully')),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
  
  void _editProfile() {
    // TODO: Implement profile editing
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Profile editing coming soon!')),
    );
  }
  
  void _showPrivacyPolicy() {
    // TODO: Show privacy policy
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Privacy policy coming soon!')),
    );
  }
  
  void _showTermsOfService() {
    // TODO: Show terms of service
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Terms of service coming soon!')),
    );
  }
  
  void _showHelpAndSupport() {
    // TODO: Show help and support
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Help & support coming soon!')),
    );
  }
  
  String _getThemeLabel(String theme) {
    switch (theme) {
      case 'light':
        return 'Light';
      case 'dark':
        return 'Dark';
      case 'system':
        return 'System Default';
      default:
        return 'System Default';
    }
  }
}