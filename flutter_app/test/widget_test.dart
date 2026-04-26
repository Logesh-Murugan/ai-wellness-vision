import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:ai_wellness_vision/main.dart';

void main() {
  testWidgets('App renders smoke test', (WidgetTester tester) async {
    // Build the app inside a ProviderScope (required by Riverpod).
    await tester.pumpWidget(
      const ProviderScope(child: AIWellnessApp()),
    );

    // Verify the app renders without errors.
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
