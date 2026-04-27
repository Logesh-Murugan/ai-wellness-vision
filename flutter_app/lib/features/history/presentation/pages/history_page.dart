import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/constants/app_constants.dart';
import '../../../../shared/presentation/widgets/custom_app_bar.dart';
import '../widgets/history_filter_bar.dart';
import '../widgets/history_item_card.dart';
import '../widgets/history_stats_card.dart';

class HistoryPage extends ConsumerStatefulWidget {
  const HistoryPage({super.key});

  @override
  ConsumerState<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends ConsumerState<HistoryPage>
    with TickerProviderStateMixin {
  late TabController _tabController;
  String _selectedFilter = 'all';
  String _selectedTimeRange = 'week';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(
        title: 'History & Reports',
        showBackButton: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.download),
            onPressed: _exportData,
            tooltip: 'Export Data',
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _showClearHistoryDialog,
            tooltip: 'Clear History',
          ),
        ],
      ),
      body: Column(
        children: [
          // Stats Overview
          _buildStatsSection(),
          
          // Filter Bar
          HistoryFilterBar(
            selectedFilter: _selectedFilter,
            selectedTimeRange: _selectedTimeRange,
            onFilterChanged: (filter) {
              setState(() {
                _selectedFilter = filter;
              });
            },
            onTimeRangeChanged: (timeRange) {
              setState(() {
                _selectedTimeRange = timeRange;
              });
            },
          ),
          
          // Tabs
          _buildTabBar(),
          
          // Content
          Expanded(
            child: _buildTabContent(),
          ),
        ],
      ),
    );
  }
  
  Widget _buildStatsSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: HistoryStatsCard(
        totalInteractions: 45,
        chatMessages: 28,
        imageAnalyses: 12,
        voiceInteractions: 5,
        timeRange: _selectedTimeRange,
      ),
    );
  }
  
  Widget _buildTabBar() {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
          ),
        ),
      ),
      child: TabBar(
        controller: _tabController,
        labelColor: Theme.of(context).colorScheme.primary,
        unselectedLabelColor: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
        indicatorColor: Theme.of(context).colorScheme.primary,
        tabs: const [
          Tab(
            icon: Icon(Icons.all_inclusive),
            text: 'All',
          ),
          Tab(
            icon: Icon(Icons.chat),
            text: 'Chats',
          ),
          Tab(
            icon: Icon(Icons.camera_alt),
            text: 'Analysis',
          ),
          Tab(
            icon: Icon(Icons.mic),
            text: 'Voice',
          ),
        ],
      ),
    );
  }
  
  Widget _buildTabContent() {
    return TabBarView(
      controller: _tabController,
      children: [
        _buildAllHistoryTab(),
        _buildChatHistoryTab(),
        _buildAnalysisHistoryTab(),
        _buildVoiceHistoryTab(),
      ],
    );
  }
  
  Widget _buildAllHistoryTab() {
    final allItems = _getAllHistoryItems();
    
    if (allItems.isEmpty) {
      return _buildEmptyState('No history available', 'Start using the app to see your activity here');
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: allItems.length,
      itemBuilder: (context, index) {
        return HistoryItemCard(
          item: allItems[index],
          onTap: () => _showItemDetails(allItems[index]),
        );
      },
    );
  }
  
  Widget _buildChatHistoryTab() {
    final chatItems = _getChatHistoryItems();
    
    if (chatItems.isEmpty) {
      return _buildEmptyState('No chat history', 'Start a conversation with the AI assistant');
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: chatItems.length,
      itemBuilder: (context, index) {
        return HistoryItemCard(
          item: chatItems[index],
          onTap: () => _showItemDetails(chatItems[index]),
        );
      },
    );
  }
  
  Widget _buildAnalysisHistoryTab() {
    final analysisItems = _getAnalysisHistoryItems();
    
    if (analysisItems.isEmpty) {
      return _buildEmptyState('No analysis history', 'Upload an image to start analyzing');
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: analysisItems.length,
      itemBuilder: (context, index) {
        return HistoryItemCard(
          item: analysisItems[index],
          onTap: () => _showItemDetails(analysisItems[index]),
        );
      },
    );
  }
  
  Widget _buildVoiceHistoryTab() {
    final voiceItems = _getVoiceHistoryItems();
    
    if (voiceItems.isEmpty) {
      return _buildEmptyState('No voice history', 'Try the voice interaction feature');
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: voiceItems.length,
      itemBuilder: (context, index) {
        return HistoryItemCard(
          item: voiceItems[index],
          onTap: () => _showItemDetails(voiceItems[index]),
        );
      },
    );
  }
  
  Widget _buildEmptyState(String title, String subtitle) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 80,
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
          ),
          const SizedBox(height: 16),
          Text(
            title,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            subtitle,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  List<HistoryItem> _getAllHistoryItems() {
    // Mock data - in real app, this would come from a provider/repository
    return [
      HistoryItem(
        id: '1',
        type: HistoryItemType.chat,
        title: 'Health Consultation',
        subtitle: 'Asked about sleep quality and stress management',
        timestamp: DateTime.now().subtract(const Duration(hours: 2)),
        data: {'messages': 5, 'duration': '8 minutes'},
      ),
      HistoryItem(
        id: '2',
        type: HistoryItemType.analysis,
        title: 'Skin Analysis',
        subtitle: 'Healthy skin detected with 87% confidence',
        timestamp: DateTime.now().subtract(const Duration(hours: 5)),
        data: {'result': 'Healthy Skin', 'confidence': 0.87},
      ),
      HistoryItem(
        id: '3',
        type: HistoryItemType.voice,
        title: 'Voice Consultation',
        subtitle: 'Discussed nutrition and exercise recommendations',
        timestamp: DateTime.now().subtract(const Duration(days: 1)),
        data: {'duration': '3:45', 'transcription': 'What are some healthy breakfast options?'},
      ),
      HistoryItem(
        id: '4',
        type: HistoryItemType.analysis,
        title: 'Food Recognition',
        subtitle: 'Apple identified with nutritional information',
        timestamp: DateTime.now().subtract(const Duration(days: 2)),
        data: {'food': 'Apple', 'calories': 95, 'health_score': 9},
      ),
    ];
  }
  
  List<HistoryItem> _getChatHistoryItems() {
    return _getAllHistoryItems().where((item) => item.type == HistoryItemType.chat).toList();
  }
  
  List<HistoryItem> _getAnalysisHistoryItems() {
    return _getAllHistoryItems().where((item) => item.type == HistoryItemType.analysis).toList();
  }
  
  List<HistoryItem> _getVoiceHistoryItems() {
    return _getAllHistoryItems().where((item) => item.type == HistoryItemType.voice).toList();
  }
  
  void _showItemDetails(HistoryItem item) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _buildItemDetailsSheet(item),
    );
  }
  
  Widget _buildItemDetailsSheet(HistoryItem item) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _getTypeColor(item.type).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getTypeIcon(item.type),
                  color: _getTypeColor(item.type),
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.title,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      _formatTimestamp(item.timestamp),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Content
          Text(
            item.subtitle,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          
          const SizedBox(height: 16),
          
          // Data
          if (item.data.isNotEmpty) ...[
            Text(
              'Details:',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            ...item.data.entries.map((entry) => Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Text(
                    '${entry.key.replaceAll('_', ' ').toUpperCase()}: ',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Text(
                    entry.value.toString(),
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            )).toList(),
          ],
          
          const SizedBox(height: 24),
          
          // Actions
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pop();
                    // TODO: Share item
                  },
                  icon: const Icon(Icons.share),
                  label: const Text('Share'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(context).pop();
                    // TODO: Export item
                  },
                  icon: const Icon(Icons.download),
                  label: const Text('Export'),
                ),
              ),
            ],
          ),
          
          // Safe area padding
          SizedBox(height: MediaQuery.of(context).padding.bottom),
        ],
      ),
    );
  }
  
  void _exportData() {
    // TODO: Implement data export
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Export feature coming soon!'),
      ),
    );
  }
  
  void _showClearHistoryDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear History'),
        content: const Text('Are you sure you want to clear all history? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // TODO: Clear history
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('History cleared successfully'),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
            ),
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }
  
  Color _getTypeColor(HistoryItemType type) {
    switch (type) {
      case HistoryItemType.chat:
        return Colors.green;
      case HistoryItemType.analysis:
        return Colors.blue;
      case HistoryItemType.voice:
        return Colors.orange;
    }
  }
  
  IconData _getTypeIcon(HistoryItemType type) {
    switch (type) {
      case HistoryItemType.chat:
        return Icons.chat;
      case HistoryItemType.analysis:
        return Icons.analytics;
      case HistoryItemType.voice:
        return Icons.mic;
    }
  }
  
  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes} minutes ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours} hours ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${timestamp.day}/${timestamp.month}/${timestamp.year}';
    }
  }
}

enum HistoryItemType { chat, analysis, voice }

class HistoryItem {
  final String id;
  final HistoryItemType type;
  final String title;
  final String subtitle;
  final DateTime timestamp;
  final Map<String, dynamic> data;
  
  HistoryItem({
    required this.id,
    required this.type,
    required this.title,
    required this.subtitle,
    required this.timestamp,
    required this.data,
  });
}