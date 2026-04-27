import 'package:flutter/material.dart';
import '../pages/history_page.dart';

class HistoryItemCard extends StatelessWidget {
  final HistoryItem item;
  final VoidCallback onTap;

  const HistoryItemCard({
    super.key,
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Type icon
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getTypeColor(item.type).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _getTypeIcon(item.type),
                  color: _getTypeColor(item.type),
                  size: 24,
                ),
              ),
              
              const SizedBox(width: 16),
              
              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Title
                    Text(
                      item.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    
                    const SizedBox(height: 4),
                    
                    // Subtitle
                    Text(
                      item.subtitle,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    
                    const SizedBox(height: 8),
                    
                    // Metadata
                    Row(
                      children: [
                        // Type badge
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getTypeColor(item.type).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            _getTypeLabel(item.type),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: _getTypeColor(item.type),
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        
                        const SizedBox(width: 8),
                        
                        // Timestamp
                        Text(
                          _formatTimestamp(item.timestamp),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                          ),
                        ),
                        
                        const Spacer(),
                        
                        // Additional info based on type
                        if (item.type == HistoryItemType.chat && item.data['messages'] != null)
                          _buildChatInfo(context, item.data['messages'])
                        else if (item.type == HistoryItemType.analysis && item.data['confidence'] != null)
                          _buildAnalysisInfo(context, item.data['confidence'])
                        else if (item.type == HistoryItemType.voice && item.data['duration'] != null)
                          _buildVoiceInfo(context, item.data['duration']),
                      ],
                    ),
                  ],
                ),
              ),
              
              const SizedBox(width: 8),
              
              // Arrow icon
              Icon(
                Icons.arrow_forward_ios,
                size: 16,
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildChatInfo(BuildContext context, int messageCount) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.message,
          size: 14,
          color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
        ),
        const SizedBox(width: 4),
        Text(
          '$messageCount',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
  
  Widget _buildAnalysisInfo(BuildContext context, double confidence) {
    final percentage = (confidence * 100).toInt();
    final color = _getConfidenceColor(confidence);
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.verified,
          size: 14,
          color: color,
        ),
        const SizedBox(width: 4),
        Text(
          '$percentage%',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
  
  Widget _buildVoiceInfo(BuildContext context, String duration) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.access_time,
          size: 14,
          color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
        ),
        const SizedBox(width: 4),
        Text(
          duration,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
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
        return Icons.chat_bubble;
      case HistoryItemType.analysis:
        return Icons.analytics;
      case HistoryItemType.voice:
        return Icons.mic;
    }
  }
  
  String _getTypeLabel(HistoryItemType type) {
    switch (type) {
      case HistoryItemType.chat:
        return 'Chat';
      case HistoryItemType.analysis:
        return 'Analysis';
      case HistoryItemType.voice:
        return 'Voice';
    }
  }
  
  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.6) return Colors.orange;
    return Colors.red;
  }
  
  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final difference = now.difference(timestamp);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}h ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${timestamp.day}/${timestamp.month}';
    }
  }
}