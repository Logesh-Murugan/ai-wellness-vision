import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/family_provider.dart';
import '../pages/add_member_page.dart';

/// Horizontal scrollable row of family member avatars for the HomePage.
/// Height: 80 px.
class FamilySelectorWidget extends ConsumerWidget {
  const FamilySelectorWidget({super.key});

  static const _avatarColors = [
    Color(0xFF10B981),
    Color(0xFF3B82F6),
    Color(0xFFF59E0B),
    Color(0xFF8B5CF6),
    Color(0xFFEF4444),
    Color(0xFF06B6D4),
  ];

  static Color _colorFor(String name) {
    final hash = name.codeUnits.fold(0, (a, b) => a + b);
    return _avatarColors[hash % _avatarColors.length];
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final membersAsync = ref.watch(familyMembersProvider);
    final active = ref.watch(activeFamilyMemberProvider);

    return SizedBox(
      height: 80,
      child: membersAsync.when(
        loading: () => const Center(
          child: SizedBox(
            width: 22,
            height: 22,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              color: Color(0xFF10B981),
            ),
          ),
        ),
        error: (_, __) => const SizedBox.shrink(),
        data: (members) => ListView(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          children: [
            // Member avatars
            ...members.map((m) {
              final isActive = active?.id == m.id;
              final color = _colorFor(m.name);
              // Truncated display name
              final displayName = m.name.length > 6
                  ? '${m.name.substring(0, 6)}..'
                  : m.name;

              return GestureDetector(
                onTap: () {
                  ref.read(activeFamilyMemberProvider.notifier).state =
                      isActive ? null : m;
                },
                child: Padding(
                  padding: const EdgeInsets.only(right: 14),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 200),
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          color: color,
                          shape: BoxShape.circle,
                          border: Border.all(
                            color: isActive ? Colors.white : Colors.transparent,
                            width: 2.5,
                          ),
                          boxShadow: isActive
                              ? [
                                  BoxShadow(
                                    color: color.withOpacity(0.55),
                                    blurRadius: 12,
                                    spreadRadius: 2,
                                  )
                                ]
                              : const [],
                        ),
                        child: Center(
                          child: Text(
                            m.initials,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        displayName,
                        style: TextStyle(
                          color: isActive ? Colors.white : Colors.white54,
                          fontSize: 10,
                          fontWeight: isActive ? FontWeight.w700 : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }),

            // "+" Add button
            GestureDetector(
              onTap: () async {
                await Navigator.push<void>(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const AddMemberPage(),
                  ),
                );
                // Refresh list after returning
                ref.invalidate(familyMembersProvider);
              },
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 48,
                    height: 48,
                    decoration: BoxDecoration(
                      color: const Color(0xFF1E2130),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xFF2D3247),
                        width: 1.5,
                        // Dashed border via strokeAlign workaround — plain solid here
                      ),
                    ),
                    child: const Icon(
                      Icons.add,
                      color: Color(0xFF10B981),
                      size: 22,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Add',
                    style: TextStyle(color: Colors.white38, fontSize: 10),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}