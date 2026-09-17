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
  String? _conversationId;

  @override
  List<ChatMessage> build() {
    Future.microtask(() => _loadHistory());
    return [];
  }

  Future<void> _loadHistory() async {
    final isDemo = ref.read(authNotifierProvider).valueOrNull?.id == 'demo-id';
    if (isDemo) return;

    try {
      final dio = ref.read(apiClientProvider);
      final convsResponse = await dio.get('/api/v1/chat/conversations');
      final List convs = convsResponse.data ?? [];
      if (convs.isNotEmpty) {
        _conversationId = convs.first['id'] as String;
        final msgsResponse = await dio.get('/api/v1/chat/conversations/$_conversationId/messages');
        final List msgs = msgsResponse.data['messages'] ?? [];
        
        state = msgs.map((m) {
          final isUser = m['is_user'] as bool;
          return ChatMessage(
            id: m['id'] as String,
            role: isUser ? 'user' : 'assistant',
            content: m['content'] as String,
          );
        }).toList();
      }
    } catch (_) {}
  }

  Future<void> sendMessage(String content, {String language = 'en'}) async {
    final userMessage = ChatMessage(
      id: const Uuid().v4(),
      role: 'user',
      content: content,
    );
    
    state = [...state, userMessage];

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

      if (_conversationId == null) {
        final convsResponse = await dio.get('/api/v1/chat/conversations');
        final List convs = convsResponse.data ?? [];
        if (convs.isNotEmpty) {
          _conversationId = convs.first['id'] as String;
        } else {
          final createResponse = await dio.post(
            '/api/v1/chat/conversations',
            data: {'title': 'General Chat'},
          );
          _conversationId = createResponse.data['id'] as String;
        }
      }

      final response = await dio.post(
        '/api/v1/chat/message',
        data: {
          'message': content,
          'conversation_id': _conversationId,
        },
      );

      final String assistantReply = response.data['content'] ?? 'Sorry, I could not understand.';
      
      final botMessage = ChatMessage(
        id: response.data['id'] ?? const Uuid().v4(),
        role: 'assistant',
        content: assistantReply,
      );

      state = [...state, botMessage];
      
    } catch (e) {
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
    _conversationId = null;
  }
}
