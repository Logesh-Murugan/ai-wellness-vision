/// Chat page — uses [chatProvider] for all state.
///
/// Zero setState(). Messages, typing indicator, and send logic are
/// all driven by the [ChatNotifier].
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../providers/chat_provider.dart';
import '../../data/chat_repository.dart';
import '../../../../core/theme/app_theme.dart';

class ChatPage extends ConsumerStatefulWidget {
  const ChatPage({super.key});

  @override
  ConsumerState<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends ConsumerState<ChatPage> {
  final _controller = TextEditingController();
  final _scrollCtrl = ScrollController();

  @override
  void dispose() {
    _controller.dispose();
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    ref.read(chatProvider.notifier).sendMessage(text);
    _controller.clear();

    // Scroll to bottom after frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent + 80,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final chatState = ref.watch(chatProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Health Assistant'),
        backgroundColor: AppTheme.successColor,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Quick questions (shown only when empty)
          if (chatState.messages.isEmpty)
            SizedBox(
              height: 60,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.all(10),
                children: [
                  _QuickChip('How to sleep better?', onTap: _sendQuick),
                  _QuickChip('Healthy diet tips?', onTap: _sendQuick),
                  _QuickChip('Exercise routine?', onTap: _sendQuick),
                  _QuickChip('Stress management?', onTap: _sendQuick),
                ],
              ),
            ),

          // Messages
          Expanded(
            child: ListView.builder(
              controller: _scrollCtrl,
              padding: const EdgeInsets.all(15),
              itemCount:
                  chatState.messages.length + (chatState.isTyping ? 1 : 0),
              itemBuilder: (context, index) {
                if (index == chatState.messages.length && chatState.isTyping) {
                  return _TypingBubble();
                }
                return _MessageBubble(message: chatState.messages[index]);
              },
            ),
          ),

          // Input bar
          _InputBar(
            controller: _controller,
            onSend: _send,
          ),
        ],
      ),
    );
  }

  void _sendQuick(String question) {
    _controller.text = question;
    _send();
  }
}

// ─── Sub-widgets ──────────────────────────

class _QuickChip extends StatelessWidget {
  final String label;
  final void Function(String) onTap;

  const _QuickChip(this.label, {required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 10),
      child: ActionChip(
        label: Text(label),
        onPressed: () => onTap(label),
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMessage message;
  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(15),
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        decoration: BoxDecoration(
          color: isUser ? AppTheme.primaryColor : Colors.grey[200],
          borderRadius: BorderRadius.circular(15),
        ),
        child: Text(
          message.content,
          style: TextStyle(color: isUser ? Colors.white : Colors.black),
        ),
      ),
    );
  }
}

class _TypingBubble extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(15),
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(15),
        ),
        child: const Text('AI is typing...'),
      ),
    );
  }
}

class _InputBar extends StatelessWidget {
  final TextEditingController controller;
  final VoidCallback onSend;

  const _InputBar({required this.controller, required this.onSend});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
              color: Colors.black.withOpacity(0.08),
              blurRadius: 5,
              offset: const Offset(0, -2)),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              decoration: InputDecoration(
                hintText: 'Ask about your health...',
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(25)),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              ),
              onSubmitted: (_) => onSend(),
            ),
          ),
          const SizedBox(width: 10),
          FloatingActionButton(
            onPressed: onSend,
            mini: true,
            child: const Icon(Icons.send),
          ),
        ],
      ),
    );
  }
}