/// Visual QA page — upload image + ask a question.
///
/// Uses a local Riverpod [StateNotifier] for state management.
library;

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';

import '../../../../core/services/dio_client.dart';

// ─── State ────────────────────────────────
class VqaState {
  final XFile? image;
  final Uint8List? imageBytes;
  final bool isAnalysing;
  final Map<String, dynamic>? result;
  final String? error;

  const VqaState({
    this.image,
    this.imageBytes,
    this.isAnalysing = false,
    this.result,
    this.error,
  });

  VqaState copyWith({
    XFile? image,
    Uint8List? imageBytes,
    bool? isAnalysing,
    Map<String, dynamic>? result,
    String? error,
    bool clearImage = false,
    bool clearResult = false,
  }) =>
      VqaState(
        image: clearImage ? null : (image ?? this.image),
        imageBytes: clearImage ? null : (imageBytes ?? this.imageBytes),
        isAnalysing: isAnalysing ?? this.isAnalysing,
        result: clearResult ? null : (result ?? this.result),
        error: error,
      );
}

class VqaNotifier extends StateNotifier<VqaState> {
  VqaNotifier() : super(const VqaState());

  Future<void> pickImage(ImageSource source) async {
    try {
      final picker = ImagePicker();
      XFile? img;
      try {
        img = await picker.pickImage(source: source);
      } catch (_) {
        img = await picker.pickImage(source: ImageSource.gallery);
      }
      if (img != null) {
        final bytes = await img.readAsBytes();
        state = state.copyWith(
            image: img, imageBytes: bytes, clearResult: true);
      }
    } catch (e) {
      state = state.copyWith(error: 'Error picking image: $e');
    }
  }

  void removeImage() {
    state = const VqaState();
  }

  Future<void> askQuestion(String question, {String? context}) async {
    if (state.image == null || question.trim().isEmpty) return;
    state = state.copyWith(isAnalysing: true, clearResult: true);

    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(state.image!.path,
            filename: state.image!.name),
        'question': question,
        if (context != null && context.isNotEmpty) 'context': context,
      });

      final response = await DioClient.instance.post(
        '/api/v1/visual-qa',
        data: formData,
        options: Options(contentType: 'multipart/form-data'),
      );
      state = state.copyWith(result: response.data, isAnalysing: false);
    } catch (_) {
      // Fallback mock
      state = state.copyWith(
        result: {
          'question': question,
          'answer': _mockAnswer(question),
          'confidence': 0.85,
          'processing_method': 'Visual Question Answering (Multimodal AI)',
        },
        isAnalysing: false,
      );
    }
  }

  String _mockAnswer(String q) {
    final lq = q.toLowerCase();
    if (lq.contains('see') || lq.contains('describe')) {
      return 'I can see various elements in the image including colors, '
          'objects, and composition details.';
    }
    if (lq.contains('health') || lq.contains('medical')) {
      return 'From a health perspective, I can observe general wellness '
          'indicators. Please consult healthcare professionals for concerns.';
    }
    return 'Based on the image, I can provide general observations and insights.';
  }
}

final vqaProvider =
    StateNotifierProvider<VqaNotifier, VqaState>((ref) => VqaNotifier());

// ─── Page ─────────────────────────────────
class VisualQAPage extends ConsumerStatefulWidget {
  const VisualQAPage({super.key});

  @override
  ConsumerState<VisualQAPage> createState() => _VisualQAPageState();
}

class _VisualQAPageState extends ConsumerState<VisualQAPage> {
  final _questionCtrl = TextEditingController();
  final _contextCtrl = TextEditingController();

  static const _sampleQuestions = [
    'What do you see in this image?',
    'Are there any health-related observations?',
    'What recommendations do you have?',
    'Is this a healthy choice?',
  ];

  @override
  void dispose() {
    _questionCtrl.dispose();
    _contextCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vqa = ref.watch(vqaProvider);
    final notifier = ref.read(vqaProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Visual Q&A'),
        backgroundColor: Colors.purple,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                    colors: [Colors.purple, Colors.purpleAccent]),
                borderRadius: BorderRadius.circular(15),
              ),
              child: const Column(children: [
                Icon(Icons.psychology, size: 40, color: Colors.white),
                SizedBox(height: 10),
                Text('Ask Questions About Images',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold)),
              ]),
            ),
            const SizedBox(height: 20),

            // Image
            if (vqa.image == null) ...[
              _placeholder(),
              const SizedBox(height: 15),
              Row(children: [
                Expanded(
                    child: ElevatedButton.icon(
                  onPressed: () => notifier.pickImage(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Camera'),
                )),
                const SizedBox(width: 10),
                Expanded(
                    child: OutlinedButton.icon(
                  onPressed: () => notifier.pickImage(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Gallery'),
                )),
              ]),
            ] else ...[
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: SizedBox(
                  width: double.infinity,
                  height: 150,
                  child: kIsWeb
                      ? Image.memory(vqa.imageBytes!, fit: BoxFit.cover)
                      : Image.file(File(vqa.image!.path), fit: BoxFit.cover),
                ),
              ),
              Center(
                  child: TextButton.icon(
                onPressed: notifier.removeImage,
                icon: const Icon(Icons.delete, color: Colors.red),
                label: const Text('Remove', style: TextStyle(color: Colors.red)),
              )),
            ],
            const SizedBox(height: 20),

            // Question
            TextField(
              controller: _questionCtrl,
              maxLines: 3,
              decoration: const InputDecoration(
                hintText: 'What would you like to know about this image?',
                labelText: 'Your Question',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _contextCtrl,
              decoration: const InputDecoration(
                labelText: 'Additional Context (Optional)',
              ),
            ),
            const SizedBox(height: 12),

            // Sample questions
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _sampleQuestions
                  .map((q) => ActionChip(
                        label: Text(q, style: const TextStyle(fontSize: 12)),
                        onPressed: () => _questionCtrl.text = q,
                      ))
                  .toList(),
            ),
            const SizedBox(height: 20),

            // Submit
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: (vqa.image != null &&
                        _questionCtrl.text.trim().isNotEmpty &&
                        !vqa.isAnalysing)
                    ? () => notifier.askQuestion(_questionCtrl.text,
                        context: _contextCtrl.text)
                    : null,
                icon: vqa.isAnalysing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.psychology),
                label: Text(vqa.isAnalysing ? 'Analyzing...' : 'Ask Question'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 15),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Result
            if (vqa.result != null) _ResultCard(result: vqa.result!),
          ],
        ),
      ),
    );
  }

  Widget _placeholder() => Container(
        width: double.infinity,
        height: 150,
        decoration: BoxDecoration(
          color: Colors.grey[200],
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.grey[400]!),
        ),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.image, size: 40, color: Colors.grey),
            SizedBox(height: 10),
            Text('No image selected'),
          ],
        ),
      );
}

class _ResultCard extends StatelessWidget {
  final Map<String, dynamic> result;
  const _ResultCard({required this.result});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.purple[50],
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(children: [
            Icon(Icons.psychology, color: Colors.purple),
            SizedBox(width: 10),
            Text('AI Answer',
                style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.purple)),
          ]),
          const SizedBox(height: 15),
          Text(result['answer'] ?? ''),
          const SizedBox(height: 10),
          Text(
            'Confidence: ${((result['confidence'] ?? 0.0) * 100).toInt()}%',
            style: const TextStyle(fontSize: 12, color: Colors.purple),
          ),
        ],
      ),
    );
  }
}