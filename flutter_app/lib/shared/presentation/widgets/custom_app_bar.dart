import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final bool showBackButton;
  final VoidCallback? onBackPressed;
  final Widget? leading;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? elevation;
  final bool centerTitle;

  const CustomAppBar({
    super.key,
    required this.title,
    this.actions,
    this.showBackButton = true,
    this.onBackPressed,
    this.leading,
    this.backgroundColor,
    this.foregroundColor,
    this.elevation,
    this.centerTitle = true,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Text(title),
      actions: actions,
      leading: leading ?? (showBackButton ? _buildBackButton(context) : null),
      backgroundColor: backgroundColor,
      foregroundColor: foregroundColor,
      elevation: elevation,
      centerTitle: centerTitle,
      automaticallyImplyLeading: showBackButton,
    );
  }

  Widget? _buildBackButton(BuildContext context) {
    if (!showBackButton) return null;
    
    return IconButton(
      icon: const Icon(Icons.arrow_back_ios),
      onPressed: onBackPressed ?? () => Navigator.of(context).pop(),
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}