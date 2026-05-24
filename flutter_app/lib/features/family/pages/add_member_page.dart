import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/family_provider.dart';

class AddMemberPage extends ConsumerStatefulWidget {
  const AddMemberPage({super.key});

  @override
  ConsumerState<AddMemberPage> createState() => _AddMemberPageState();
}

class _AddMemberPageState extends ConsumerState<AddMemberPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();

  String _relationship = 'other';
  String _language = 'en';
  int? _age;

  static const _relationships = [
    'self', 'father', 'mother', 'spouse', 'sibling', 'child', 'other',
  ];

  static const _languageOptions = {
    'en': 'English',
    'hi': 'हिंदी',
    'ta': 'தமிழ்',
    'te': 'తెలుగు',
    'bn': 'বাংলা',
    'gu': 'ગુજરાતી',
    'mr': 'मराठी',
  };

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    await ref.read(familyActionsProvider.notifier).addMember(
      name: _nameController.text.trim(),
      relationship: _relationship,
      age: _age,
      languagePreference: _language,
    );

    final actionsState = ref.read(familyActionsProvider);
    if (!mounted) return;

    if (actionsState is AsyncData) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅  Family member added!'),
          backgroundColor: Color(0xFF10B981),
          behavior: SnackBarBehavior.floating,
        ),
      );
      Navigator.pop(context);
    } else if (actionsState is AsyncError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(actionsState.error.toString()),
          backgroundColor: Colors.redAccent,
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final actionsState = ref.watch(familyActionsProvider);
    final isLoading = actionsState is AsyncLoading;

    return Scaffold(
      backgroundColor: const Color(0xFF0F1117),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: const Text(
          'Add Family Member',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Name ──────────────────────────────────────────────
              _label('Full Name *'),
              TextFormField(
                controller: _nameController,
                style: const TextStyle(color: Colors.white),
                decoration: _inputDec('e.g. Amma, Papa, Rahul'),
                textCapitalization: TextCapitalization.words,
                validator: (v) =>
                    (v == null || v.trim().isEmpty) ? 'Name is required' : null,
              ),

              const SizedBox(height: 20),

              // ── Relationship ──────────────────────────────────────
              _label('Relationship'),
              DropdownButtonFormField<String>(
                value: _relationship,
                dropdownColor: const Color(0xFF1E2130),
                style: const TextStyle(color: Colors.white),
                decoration: _inputDec(''),
                items: _relationships.map((r) {
                  final label = '${r[0].toUpperCase()}${r.substring(1)}';
                  return DropdownMenuItem(
                    value: r,
                    child: Text(label, style: const TextStyle(color: Colors.white)),
                  );
                }).toList(),
                onChanged: (v) => setState(() => _relationship = v ?? 'other'),
              ),

              const SizedBox(height: 20),

              // ── Age (optional) ────────────────────────────────────
              _label('Age (optional)'),
              TextFormField(
                style: const TextStyle(color: Colors.white),
                decoration: _inputDec('e.g. 45'),
                keyboardType: TextInputType.number,
                onSaved: (v) =>
                    _age = (v != null && v.trim().isNotEmpty) ? int.tryParse(v.trim()) : null,
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return null;
                  final n = int.tryParse(v.trim());
                  if (n == null || n < 0 || n > 150) return 'Enter a valid age (0–150)';
                  return null;
                },
              ),

              const SizedBox(height: 20),

              // ── Language preference ───────────────────────────────
              _label('Language Preference'),
              DropdownButtonFormField<String>(
                value: _language,
                dropdownColor: const Color(0xFF1E2130),
                style: const TextStyle(color: Colors.white),
                decoration: _inputDec(''),
                items: _languageOptions.entries.map((e) {
                  return DropdownMenuItem(
                    value: e.key,
                    child: Text(e.value, style: const TextStyle(color: Colors.white)),
                  );
                }).toList(),
                onChanged: (v) => setState(() => _language = v ?? 'en'),
              ),

              const SizedBox(height: 36),

              // ── Submit button ─────────────────────────────────────
              SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF10B981),
                    foregroundColor: Colors.white,
                    disabledBackgroundColor: const Color(0xFF10B981).withOpacity(0.5),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    elevation: 0,
                  ),
                  onPressed: isLoading ? null : _submit,
                  child: isLoading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Text(
                          'Add Member',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _label(String text) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(
          text,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
      );

  InputDecoration _inputDec(String hint) => InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white30),
        filled: true,
        fillColor: const Color(0xFF1E2130),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D3247)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF2D3247)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Color(0xFF10B981)),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.redAccent),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.redAccent),
        ),
      );
}
