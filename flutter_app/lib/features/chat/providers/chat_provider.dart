import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:flutter_app/core/network/api_client.dart';
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
