import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:ai_wellness_vision/core/network/api_client.dart';
import 'package:ai_wellness_vision/features/auth/providers/auth_provider.dart';
import 'package:uuid/uuid.dart';

part 'chat_provider.g.dart';

// Dummy model
class ChatMessage {
  final String id;
  final String role;
  final String content;

  ChatMessage({required this.id, required this.role, required this.content});

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? const Uuid().v4(),
      role: json['role'] ?? 'user',
      content: json['content'] ?? '',
    );
  }
}

@riverpod
class ChatNotifier extends _$ChatNotifier {
  @override
  List<ChatMessage> build() {
    return [];
  }

  Future<void> sendMessage(String content, {String language = 'en'}) async {
    // Optimistic update: immediately show user's message in UI
    final userMessage = ChatMessage(
      id: const Uuid().v4(),
      role: 'user',
      content: content,
    );
    
    // Create a new list instance to trigger Riverpod state rebuild
    state = [...state, userMessage];

    // Check if we are in demo mode
    final isDemo = ref.read(authNotifierProvider).valueOrNull?.id == 'demo-id';
    if (isDemo) {
      await Future.delayed(const Duration(seconds: 1));
      final botMessage = ChatMessage(
        id: const Uuid().v4(),
        role: 'assistant',
        content: 'Hi! I am your AI wellness assistant. In Demo Mode, I will respond to your queries with helpful, pre-configured advice. For example: to stay healthy, ensure you get 7-8 hours of sleep, exercise regularly, and drink plenty of water.',
      );
      state = [...state, botMessage];
      return;
    }

    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.post(
        '/api/v1/chat/message',
        data: {
          'message': content,
          'language': language,
        },
      );

      // Backend usually returns the assistant's reply object
      // (or we parse it from response.data['response'])
      final String assistantReply = response.data['response'] ?? 'Sorry, I could not understand.';
      
      final botMessage = ChatMessage(
        id: const Uuid().v4(),
        role: 'assistant',
        content: assistantReply,
      );

      // Append bot response
      state = [...state, botMessage];
      
    } catch (e) {
      // Revert optimistic update or append an error message
      final errorMessage = ChatMessage(
        id: const Uuid().v4(),
        role: 'assistant',
        content: 'Error: Failed to reach the AI wellness assistant.',
      );
      state = [...state, errorMessage];
    }
  }

  void clearHistory() {
    state = [];
  }
}
