import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_filex/open_filex.dart';
import 'package:path_provider/path_provider.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';

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
  final Ref ref;
  VoiceNotifier(this.ref) : super(const VoiceState());

  Future<void> processTextQuery(String text) async {
    state = state.copyWith(
      transcribedText: text,
      isListening: false,
      isProcessing: true,
      aiResponse: '',
    );

    try {
      final dio = ref.read(apiClientProvider);

      // 1. Send query to chat message endpoint to get response
      final convsResponse = await dio.get('/api/v1/chat/conversations');
      final List convs = convsResponse.data ?? [];
      String conversationId;
      if (convs.isNotEmpty) {
        conversationId = convs.first['id'] as String;
      } else {
        final createResponse = await dio.post(
          '/api/v1/chat/conversations',
          data: {'title': 'Voice Assistant Chat'},
        );
        conversationId = createResponse.data['id'] as String;
      }

      final chatResponse = await dio.post(
        '/api/v1/chat/message',
        data: {
          'message': text,
          'conversation_id': conversationId,
        },
      );

      final String assistantReply = chatResponse.data['content'] ?? 'Sorry, I could not understand.';

      state = state.copyWith(
        aiResponse: assistantReply,
        isProcessing: false,
      );

      // 2. Synthesize response to speech
      final formData = FormData.fromMap({
        'text': assistantReply,
        'language': 'en',
      });

      final synthResponse = await dio.post(
        '/voice/synthesize',
        data: formData,
        options: Options(responseType: ResponseType.bytes),
      );

      // 3. Save audio file locally and play it using OpenFilex
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/assistant_response_${DateTime.now().millisecondsSinceEpoch}.mp3');
      await file.writeAsBytes(synthResponse.data as List<int>);

      await OpenFilex.open(file.path);

    } catch (e) {
      state = state.copyWith(
        aiResponse: 'Error: Failed to communicate with the voice backend.',
        isProcessing: false,
      );
    }
  }

  void clear() {
    state = const VoiceState();
  }
}

final voiceProvider = StateNotifierProvider<VoiceNotifier, VoiceState>(
  (ref) => VoiceNotifier(ref),
);

// ─── Page ─────────────────────────────────
class VoiceInteractionPage extends ConsumerWidget {
  const VoiceInteractionPage({super.key});

  void _showVoiceInputDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Speak to AI Assistant'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            hintText: 'Type your question here...',
            border: OutlineInputBorder(),
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final text = controller.text.trim();
              if (text.isNotEmpty) {
                ref.read(voiceProvider.notifier).processTextQuery(text);
              }
              Navigator.pop(context);
            },
            child: const Text('Send'),
          ),
        ],
      ),
    );
  }

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
                      onTap: voice.isProcessing ? null : () => _showVoiceInputDialog(context, ref),
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
                                    color: Colors.purple.withOpacity(0.3),
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
                onPressed: voice.isProcessing ? null : () => _showVoiceInputDialog(context, ref),
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