/// Login page — uses [authProvider] for auth state, Riverpod for all UI state.
///
/// Zero setState(). Loading and password visibility are Riverpod providers.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../providers/auth_provider.dart';
import '../../../../core/theme/app_theme.dart';

// ─── Form-local providers ─────────────────
final _loginLoadingProvider = StateProvider.autoDispose<bool>((_) => false);
final _loginObscureProvider = StateProvider.autoDispose<bool>((_) => true);

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    ref.read(_loginLoadingProvider.notifier).state = true;
    try {
      await ref
          .read(authProvider.notifier)
          .login(_emailCtrl.text.trim(), _passwordCtrl.text);
      if (mounted) context.go('/home');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Login failed: $e')),
        );
      }
    } finally {
      if (mounted) ref.read(_loginLoadingProvider.notifier).state = false;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isLoading = ref.watch(_loginLoadingProvider);
    final obscure = ref.watch(_loginObscureProvider);

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
          child: Form(
            key: _formKey,
            child: Column(
              children: [
                // Logo
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Icon(Icons.health_and_safety,
                      size: 40, color: Colors.white),
                ),
                const SizedBox(height: 24),
                Text('Welcome Back',
                    style: theme.textTheme.headlineMedium),
                const SizedBox(height: 8),
                Text('Sign in to continue',
                    style: theme.textTheme.bodyMedium),
                const SizedBox(height: 40),

                // Email field
                TextFormField(
                  controller: _emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  validator: (v) =>
                      (v == null || !v.contains('@')) ? 'Valid email required' : null,
                ),
                const SizedBox(height: 16),

                // Password field
                TextFormField(
                  controller: _passwordCtrl,
                  obscureText: obscure,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    prefixIcon: const Icon(Icons.lock_outlined),
                    suffixIcon: IconButton(
                      icon: Icon(obscure
                          ? Icons.visibility_off
                          : Icons.visibility),
                      onPressed: () => ref
                          .read(_loginObscureProvider.notifier)
                          .state = !obscure,
                    ),
                  ),
                  validator: (v) => (v == null || v.length < 6)
                      ? 'Min 6 characters'
                      : null,
                ),
                const SizedBox(height: 32),

                // Login button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: isLoading ? null : _submit,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white),
                          )
                        : const Text('Sign In'),
                  ),
                ),
                const SizedBox(height: 16),

                // Register link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text("Don't have an account? "),
                    GestureDetector(
                      onTap: () => context.go('/register'),
                      child: Text('Sign Up',
                          style: TextStyle(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.bold,
                          )),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}