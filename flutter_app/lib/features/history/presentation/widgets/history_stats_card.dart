import 'package:flutter/material.dart';

class HistoryStatsCard extends StatelessWidget {
  final int totalInteractions;
  final int chatMessages;
  final int imageAnalyses;
  final int voiceInteractions;
  final String timeRange;

  const HistoryStatsCard({
    super.key,
    required this.totalInteractions,
    required this.chatMessages,
    required this.imageAnalyses,
    required this.voiceInteractions,
    required this.timeRange,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Theme.of(context).colorScheme.primary.withOpacity(0.1),
            Theme.of(context).colorScheme.secondary.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.2),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Activity Summary',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    _getTimeRangeLabel(timeRange),
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                    ),
                  ),
                ],
              ),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.trending_up,
                  color: Theme.of(context).colorScheme.primary,
                  size: 24,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Total interactions
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).dividerColor,
              ),
            ),
            child: Column(
              children: [
                Text(
                  totalInteractions.toString(),
                  style: Theme.of(context).textTheme.displaySmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
                Text(
                  'Total Interactions',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 16),
          
          // Breakdown
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  context,
                  'Chats',
                  chatMessages,
                  Icons.chat,
                  Colors.green,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatItem(
                  context,
                  'Analysis',
                  imageAnalyses,
                  Icons.analytics,
                  Colors.blue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildStatItem(
                  context,
                  'Voice',
                  voiceInteractions,
                  Icons.mic,
                  Colors.orange,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Progress indicators
          _buildProgressSection(context),
        ],
      ),
    );
  }
  
  Widget _buildStatItem(
    BuildContext context,
    String label,
    int value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 20,
          ),
          const SizedBox(height: 8),
          Text(
            value.toString(),
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildProgressSection(BuildContext context) {
    final total = totalInteractions;
    if (total == 0) return const SizedBox();
    
    final chatPercentage = chatMessages / total;
    final analysisPercentage = imageAnalyses / total;
    final voicePercentage = voiceInteractions / total;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Activity Distribution',
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // Chat progress
        _buildProgressBar(
          context,
          'Chats',
          chatPercentage,
          Colors.green,
          '${(chatPercentage * 100).toInt()}%',
        ),
        
        const SizedBox(height: 8),
        
        // Analysis progress
        _buildProgressBar(
          context,
          'Analysis',
          analysisPercentage,
          Colors.blue,
          '${(analysisPercentage * 100).toInt()}%',
        ),
        
        const SizedBox(height: 8),
        
        // Voice progress
        _buildProgressBar(
          context,
          'Voice',
          voicePercentage,
          Colors.orange,
          '${(voicePercentage * 100).toInt()}%',
        ),
      ],
    );
  }
  
  Widget _buildProgressBar(
    BuildContext context,
    String label,
    double progress,
    Color color,
    String percentage,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
            Text(
              percentage,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: progress,
          backgroundColor: Colors.grey[300],
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }
  
  String _getTimeRangeLabel(String timeRange) {
    switch (timeRange) {
      case 'day':
        return 'Today';
      case 'week':
        return 'This Week';
      case 'month':
        return 'This Month';
      case 'year':
        return 'This Year';
      case 'all':
        return 'All Time';
      default:
        return 'This Week';
    }
  }
}