import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/family_repository_dart.dart';

// ─── Data model ──────────────────────────────────────────────────────────────

class FamilyMember {
  final String id;
  final String name;
  final String relationship;
  final int? age;
  final String languagePreference;

  const FamilyMember({
    required this.id,
    required this.name,
    required this.relationship,
    this.age,
    this.languagePreference = 'en',
  });

  factory FamilyMember.fromJson(Map<String, dynamic> json) => FamilyMember(
        id: json['id'] as String,
        name: json['name'] as String,
        relationship: json['relationship'] as String,
        age: json['age'] as int?,
        languagePreference: (json['language_preference'] as String?) ?? 'en',
      );

  /// Returns first letter of each word (max 2 chars), e.g. "Rahul Sharma" → "RS".
  String get initials {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }
}

// ─── Active member ────────────────────────────────────────────────────────────

final activeFamilyMemberProvider = StateProvider<FamilyMember?>((ref) => null);

// ─── Members list ─────────────────────────────────────────────────────────────

final familyMembersProvider = FutureProvider<List<FamilyMember>>((ref) async {
  final repo = ref.read(familyRepositoryDartProvider);
  return repo.getMembers();
});

// ─── Actions notifier ────────────────────────────────────────────────────────

class FamilyActions extends StateNotifier<AsyncValue<void>> {
  final FamilyRepositoryDart _repo;
  final Ref _ref;

  FamilyActions(this._repo, this._ref) : super(const AsyncData(null));

  Future<void> addMember({
    required String name,
    required String relationship,
    int? age,
    String languagePreference = 'en',
  }) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.createMember(
        name: name,
        relationship: relationship,
        age: age,
        languagePreference: languagePreference,
      );
      _ref.invalidate(familyMembersProvider);
    });
  }

  Future<void> deleteMember(String memberId) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      await _repo.deleteMember(memberId);
      // Clear active if it was the deleted member
      final active = _ref.read(activeFamilyMemberProvider);
      if (active?.id == memberId) {
        _ref.read(activeFamilyMemberProvider.notifier).state = null;
      }
      _ref.invalidate(familyMembersProvider);
    });
  }
}

final familyActionsProvider =
    StateNotifierProvider<FamilyActions, AsyncValue<void>>((ref) {
  final repo = ref.read(familyRepositoryDartProvider);
  return FamilyActions(repo, ref);
});
