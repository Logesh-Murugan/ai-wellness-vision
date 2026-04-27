import 'package:flutter/material.dart';

class SettingsTile extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool enabled;

  const SettingsTile({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(
        title,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
          color: enabled 
              ? Theme.of(context).colorScheme.onSurface
              : Theme.of(context).disabledColor,
        ),
      ),
      subtitle: subtitle != null
          ? Text(
              subtitle!,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: enabled
                    ? Theme.of(context).colorScheme.onSurface.withOpacity(0.7)
                    : Theme.of(context).disabledColor,
              ),
            )
          : null,
      leading: leading != null
          ? IconTheme(
              data: IconThemeData(
                color: enabled
                    ? Theme.of(context).colorScheme.primary
                    : Theme.of(context).disabledColor,
              ),
              child: leading!,
            )
          : null,
      trailing: trailing ?? (onTap != null
          ? Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: enabled
                  ? Theme.of(context).colorScheme.onSurface.withOpacity(0.5)
                  : Theme.of(context).disabledColor,
            )
          : null),
      onTap: enabled ? onTap : null,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
    );
  }
}