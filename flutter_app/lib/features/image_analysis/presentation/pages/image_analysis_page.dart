/// Image analysis page — Premium UI redesign.
library;

import 'dart:io';
import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../providers/analysis_provider.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/analysis_repository.dart';

class ImageAnalysisPage extends ConsumerWidget {
  const ImageAnalysisPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(analysisProvider);
    final notifier = ref.read(analysisProvider.notifier);
    
    // Determine active theme colors based on selected analysis type
    final activeColor = _getActiveColor(state.analysisType);

    return Scaffold(
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: const Text('AI Analysis'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        flexibleSpace: ClipRect(
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
            child: Container(
              color: Theme.of(context).scaffoldBackgroundColor.withOpacity(0.8),
            ),
          ),
        ),
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              activeColor.withOpacity(0.1),
              Theme.of(context).scaffoldBackgroundColor,
            ],
            stops: const [0.0, 0.3],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Horizontal Type Selector
                _AnalysisTypeSelector(
                  selected: state.analysisType,
                  onChanged: notifier.setAnalysisType,
                ),
                const SizedBox(height: 24),

                // Premium Image Preview Card
                _ImagePreviewCard(
                  imageBytes: state.imageBytes,
                  imagePath: state.selectedImage?.path,
                  analysisType: state.analysisType,
                  activeColor: activeColor,
                  onCameraTap: () => notifier.pickImage(ImageSource.camera),
                  onGalleryTap: () => notifier.pickImage(ImageSource.gallery),
                ),
                
                const SizedBox(height: 24),

                // Analyze Button (Hero action)
                if (state.hasImage)
                  _AnalyzeButton(
                    isAnalysing: state.isAnalysing,
                    activeColor: activeColor,
                    onTap: () => notifier.analyze(),
                  ),
                  
                if (state.hasImage) const SizedBox(height: 24),

                // Rich Result Display
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 500),
                  child: state.result.when(
                    data: (result) => result != null 
                        ? _RichResultCard(result: result, activeColor: activeColor) 
                        : const SizedBox.shrink(),
                    loading: () => _LoadingSkeleton(activeColor: activeColor),
                    error: (e, _) => _ErrorCard(message: e.toString()),
                  ),
                ),
                
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getActiveColor(String type) {
    switch (type) {
      case 'skin': return AppTheme.errorColor;
      case 'food': return AppTheme.successColor;
      case 'eye': return const Color(0xFF667EEA);
      case 'wellness': return AppTheme.primaryColor;
      default: return AppTheme.primaryColor;
    }
  }
}

// ─── Sub-widgets ──────────────────────────

class _AnalysisTypeSelector extends StatelessWidget {
  final String selected;
  final ValueChanged<String> onChanged;

  const _AnalysisTypeSelector({required this.selected, required this.onChanged});

  static const _types = [
    ('skin', 'Skin', Icons.face, [Color(0xFFFF6B6B), Color(0xFFFF8E8E)]),
    ('food', 'Food', Icons.restaurant, [Color(0xFF4ECDC4), Color(0xFF44A08D)]),
    ('eye', 'Eye', Icons.visibility, [Color(0xFF667EEA), Color(0xFF764BA2)]),
    ('wellness', 'Wellness', Icons.favorite, [Color(0xFF43E97B), Color(0xFF38F9D7)]),
    ('emotion', 'Emotion', Icons.psychology, [Color(0xFFF6D365), Color(0xFFFDA085)]),
  ];

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 50,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        itemCount: _types.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final t = _types[index];
          final isSelected = selected == t.$1;
          return GestureDetector(
            onTap: () => onChanged(t.$1),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              curve: Curves.easeInOut,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                gradient: isSelected ? LinearGradient(colors: t.$4) : null,
                color: isSelected ? null : Theme.of(context).cardColor,
                borderRadius: BorderRadius.circular(25),
                boxShadow: isSelected
                    ? [BoxShadow(color: t.$4[0].withOpacity(0.4), blurRadius: 8, offset: const Offset(0, 4))]
                    : [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 4)],
                border: Border.all(
                  color: isSelected ? Colors.transparent : Colors.grey.withOpacity(0.2),
                ),
              ),
              child: Row(
                children: [
                  Icon(t.$3, color: isSelected ? Colors.white : Colors.grey[600], size: 20),
                  const SizedBox(width: 8),
                  Text(
                    t.$2,
                    style: TextStyle(
                      color: isSelected ? Colors.white : Colors.grey[700],
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _ImagePreviewCard extends StatelessWidget {
  final Uint8List? imageBytes;
  final String? imagePath;
  final String analysisType;
  final Color activeColor;
  final VoidCallback onCameraTap;
  final VoidCallback onGalleryTap;

  const _ImagePreviewCard({
    this.imageBytes,
    this.imagePath,
    required this.analysisType,
    required this.activeColor,
    required this.onCameraTap,
    required this.onGalleryTap,
  });

  @override
  Widget build(BuildContext context) {
    final hasImage = imageBytes != null || imagePath != null;

    return Container(
      width: double.infinity,
      height: 280,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: activeColor.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
        border: Border.all(color: activeColor.withOpacity(0.1), width: 2),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(22),
        child: Stack(
          fit: StackFit.expand,
          children: [
            // Image or placeholder
            if (hasImage)
              kIsWeb
                  ? Image.memory(imageBytes!, fit: BoxFit.cover)
                  : Image.file(File(imagePath!), fit: BoxFit.cover)
            else
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: activeColor.withOpacity(0.1),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(Icons.add_photo_alternate, size: 50, color: activeColor),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Upload Image for Analysis',
                    style: TextStyle(color: Colors.grey[600], fontSize: 16, fontWeight: FontWeight.w500),
                  ),
                ],
              ),

            // Glassmorphic action bar at bottom
            Positioned(
              left: 12,
              right: 12,
              bottom: 12,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: BackdropFilter(
                  filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.black.withOpacity(0.4),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white.withOpacity(0.2)),
                    ),
                    child: Row(
                      children: [
                        // Type Badge
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: activeColor.withOpacity(0.8),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            analysisType.toUpperCase(),
                            style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                          ),
                        ),
                        const Spacer(),
                        // Action Buttons
                        _IconButton(
                          icon: Icons.camera_alt,
                          onTap: onCameraTap,
                        ),
                        const SizedBox(width: 8),
                        _IconButton(
                          icon: Icons.photo_library,
                          onTap: onGalleryTap,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _IconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _IconButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white.withOpacity(0.2),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(10),
          child: Icon(icon, color: Colors.white, size: 22),
        ),
      ),
    );
  }
}

class _AnalyzeButton extends StatelessWidget {
  final bool isAnalysing;
  final Color activeColor;
  final VoidCallback onTap;

  const _AnalyzeButton({
    required this.isAnalysing,
    required this.activeColor,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 60,
      child: ElevatedButton(
        onPressed: isAnalysing ? null : onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: activeColor,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          elevation: 8,
          shadowColor: activeColor.withOpacity(0.5),
        ),
        child: isAnalysing
            ? const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3),
                  ),
                  SizedBox(width: 16),
                  Text('Analyzing with AI...', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.auto_awesome, size: 24),
                  SizedBox(width: 12),
                  Text('Analyze Image', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ],
              ),
      ),
    );
  }
}

class _RichResultCard extends StatelessWidget {
  final AnalysisResult result;
  final Color activeColor;

  const _RichResultCard({required this.result, required this.activeColor});

  @override
  Widget build(BuildContext context) {
    // Parse result text for severity
    String severity = 'LOW';
    Color severityColor = Colors.green;
    
    if (result.result.contains('Severity: HIGH')) {
      severity = 'HIGH';
      severityColor = Colors.red;
    } else if (result.result.contains('Severity: MEDIUM') || result.result.contains('Health Score')) {
      // Use orange for medium or food health scores
      severity = 'MEDIUM';
      severityColor = Colors.orange;
    }

    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: activeColor.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
        border: Border.all(color: activeColor.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with AI Method
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            decoration: BoxDecoration(
              color: activeColor.withOpacity(0.1),
              borderRadius: const BorderRadius.only(topLeft: Radius.circular(24), topRight: Radius.circular(24)),
            ),
            child: Row(
              children: [
                Icon(Icons.psychology, color: activeColor, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    result.analysisMethod ?? 'AI Analysis',
                    style: TextStyle(color: activeColor, fontWeight: FontWeight.bold, fontSize: 12),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (result.type == 'skin' || result.type == 'food')
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: severityColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      severity,
                      style: TextStyle(color: severityColor, fontWeight: FontWeight.bold, fontSize: 10),
                    ),
                  ),
              ],
            ),
          ),
          
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Main Result Text (Cleaned up a bit if it contains raw markdown)
                Text(
                  result.result.replaceAll(RegExp(r'#+\s'), ''), 
                  style: const TextStyle(fontSize: 15, height: 1.5),
                ),
                const SizedBox(height: 24),
                
                // Confidence Gauge
                Row(
                  children: [
                    Stack(
                      alignment: Alignment.center,
                      children: [
                        SizedBox(
                          width: 60,
                          height: 60,
                          child: CircularProgressIndicator(
                            value: result.confidence,
                            backgroundColor: Colors.grey[200],
                            color: activeColor,
                            strokeWidth: 6,
                          ),
                        ),
                        Text(
                          '${(result.confidence * 100).toInt()}%',
                          style: TextStyle(fontWeight: FontWeight.bold, color: activeColor, fontSize: 16),
                        ),
                      ],
                    ),
                    const SizedBox(width: 20),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('AI Confidence Level', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          const SizedBox(height: 4),
                          Text(
                            'Probability of correct classification based on training data.',
                            style: TextStyle(color: Colors.grey[600], fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 20),
                  child: Divider(),
                ),
                
                // Recommendations
                const Text('Recommendations', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                const SizedBox(height: 12),
                ...result.recommendations.map((rec) => Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        margin: const EdgeInsets.only(top: 2),
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: activeColor.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: Icon(Icons.check, size: 14, color: activeColor),
                      ),
                      const SizedBox(width: 12),
                      Expanded(child: Text(rec, style: const TextStyle(height: 1.4))),
                    ],
                  ),
                )).toList(),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LoadingSkeleton extends StatelessWidget {
  final Color activeColor;
  
  const _LoadingSkeleton({required this.activeColor});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
      ),
      child: Column(
        children: [
          const SizedBox(height: 20),
          SizedBox(
            width: 80, 
            height: 80,
            child: CircularProgressIndicator(
              color: activeColor,
              strokeWidth: 4,
            ),
          ),
          const SizedBox(height: 24),
          const Text('Analyzing image...', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text('Extracting features and running models', style: TextStyle(color: Colors.grey[500])),
          const SizedBox(height: 30),
          _buildShimmer(height: 20, width: double.infinity),
          const SizedBox(height: 12),
          _buildShimmer(height: 20, width: 200),
          const SizedBox(height: 24),
          _buildShimmer(height: 60, width: double.infinity),
        ],
      ),
    );
  }
  
  Widget _buildShimmer({required double height, required double width}) {
    return Container(
      height: height,
      width: width,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        borderRadius: BorderRadius.circular(8),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  final String message;
  const _ErrorCard({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.red[50],
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.red[200]!),
      ),
      child: Column(
        children: [
          const Icon(Icons.error_outline, color: Colors.red, size: 48),
          const SizedBox(height: 16),
          const Text('Analysis Failed', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.red)),
          const SizedBox(height: 8),
          Text(message, textAlign: TextAlign.center, style: TextStyle(color: Colors.red[700])),
        ],
      ),
    );
  }
}