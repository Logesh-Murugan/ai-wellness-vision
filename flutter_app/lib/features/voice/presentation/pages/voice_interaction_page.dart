/// Voice interaction page — microphone button, transcription, AI response.
///
/// Uses Riverpod [StateNotifier] for all state. Zero setState().
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';


// ─── Voice state + notifier ───────────────
class VoiceState {
  final bool isListening;
  final bool isProcessing;
  final String transcribedText;
  final String aiResponse;

  const VoiceState({
    this.isListening = false,
    this.isProcessing = false,
    this.transcribedText = '',
    this.aiResponse = '',
  });

  VoiceState copyWith({
    bool? isListening,
    bool? isProcessing,
    String? transcribedText,
    String? aiResponse,
  }) =>
      VoiceState(
        isListening: isListening ?? this.isListening,
        isProcessing: isProcessing ?? this.isProcessing,
        transcribedText: transcribedText ?? this.transcribedText,
        aiResponse: aiResponse ?? this.aiResponse,
      );
}

class VoiceNotifier extends StateNotifier<VoiceState> {
  VoiceNotifier() : super(const VoiceState());

  void toggleListening() {
    if (state.isProcessing) return;
    if (state.isListening) {
      state = state.copyWith(isListening: false);
    } else {
      state = state.copyWith(isListening: true);
      _startListening();
    }
  }

  void _startListening() {
    Future.delayed(const Duration(seconds: 3), () {
      if (!state.isListening) return;
      state = state.copyWith(
        transcribedText: 'How can I improve my sleep quality?',
        isListening: false,
        isProcessing: true,
      );
      _processInput();
    });
  }

  void _processInput() {
    Future.delayed(const Duration(seconds: 2), () {
      state = state.copyWith(
        aiResponse:
            'To improve sleep quality, maintain a consistent sleep schedule, '
            'create a relaxing bedtime routine, keep your bedroom cool and dark, '
            'and avoid caffeine before bedtime.',
        isProcessing: false,
      );
    });
  }

  void clear() {
    state = const VoiceState();
  }
}

final voiceProvider = StateNotifierProvider<VoiceNotifier, VoiceState>(
  (ref) => VoiceNotifier(),
);

// ─── Page ─────────────────────────────────
class VoiceInteractionPage extends ConsumerWidget {
  const VoiceInteractionPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final voice = ref.watch(voiceProvider);
    final notifier = ref.read(voiceProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Voice Assistant'),
        backgroundColor: Colors.purple,
        foregroundColor: Colors.white,
        actions: [
          if (voice.transcribedText.isNotEmpty || voice.aiResponse.isNotEmpty)
            IconButton(
                onPressed: notifier.clear, icon: const Icon(Icons.clear)),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Mic button
            Expanded(
              flex: 2,
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    GestureDetector(
                      onTap: notifier.toggleListening,
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: voice.isListening
                              ? Colors.purple
                              : voice.isProcessing
                                  ? Colors.orange
                                  : Colors.grey,
                          boxShadow: voice.isListening
                              ? [
                                  BoxShadow(
                                    color: Colors.purple.withValues(alpha: 0.3),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ]
                              : null,
                        ),
                        child: Icon(
                          voice.isListening
                              ? Icons.mic
                              : voice.isProcessing
                                  ? Icons.hourglass_empty
                                  : Icons.mic_none,
                          size: 50,
                          color: Colors.white,
                        ),
                      ),
                    ),
                    const SizedBox(height: 30),
                    Text(
                      voice.isListening
                          ? 'Listening...'
                          : voice.isProcessing
                              ? 'Processing...'
                              : 'Tap to speak',
                      style: const TextStyle(
                          fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),

            // Conversation display
            Expanded(
              flex: 3,
              child: SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (voice.transcribedText.isNotEmpty)
                      _InfoCard(
                        title: 'You said:',
                        body: voice.transcribedText,
                        color: Colors.blue[50]!,
                      ),
                    if (voice.isProcessing)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(15),
                        margin: const EdgeInsets.only(bottom: 15),
                        decoration: BoxDecoration(
                          color: Colors.orange[50],
                          borderRadius: BorderRadius.circular(15),
                        ),
                        child: const Row(children: [
                          CircularProgressIndicator(),
                          SizedBox(width: 15),
                          Text('AI is processing...'),
                        ]),
                      ),
                    if (voice.aiResponse.isNotEmpty)
                      _InfoCard(
                        title: 'AI Assistant:',
                        body: voice.aiResponse,
                        color: Colors.green[50]!,
                      ),
                  ],
                ),
              ),
            ),

            // Action button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: voice.isProcessing ? null : notifier.toggleListening,
                icon: Icon(voice.isListening ? Icons.stop : Icons.mic),
                label: Text(
                    voice.isListening ? 'Stop Listening' : 'Start Voice Chat'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: voice.isListening ? Colors.red : Colors.purple,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final String body;
  final Color color;

  const _InfoCard(
      {required this.title, required this.body, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(15),
      margin: const EdgeInsets.only(bottom: 15),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text(body),
        ],
      ),
    );
  }
}