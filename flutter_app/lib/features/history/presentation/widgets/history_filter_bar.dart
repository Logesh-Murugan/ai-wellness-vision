import 'package:flutter/material.dart';

class HistoryFilterBar extends StatelessWidget {
  final String selectedFilter;
  final String selectedTimeRange;
  final Function(String) onFilterChanged;
  final Function(String) onTimeRangeChanged;

  const HistoryFilterBar({
    super.key,
    required this.selectedFilter,
    required this.selectedTimeRange,
    required this.onFilterChanged,
    required this.onTimeRangeChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        border: Border(
          bottom: BorderSide(
            color: Theme.of(context).dividerColor,
          ),
        ),
      ),
      child: Row(
        children: [
          // Filter dropdown
          Expanded(
            child: _buildFilterDropdown(context),
          ),
          
          const SizedBox(width: 16),
          
          // Time range dropdown
          Expanded(
            child: _buildTimeRangeDropdown(context),
          ),
        ],
      ),
    );
  }
  
  Widget _buildFilterDropdown(BuildContext context) {
    final filters = {
      'all': 'All Types',
      'chat': 'Chat Only',
      'analysis': 'Analysis Only',
      'voice': 'Voice Only',
    };
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.3),
        ),
      ),
      child: DropdownButton<String>(
        value: selectedFilter,
        underline: const SizedBox(),
        isDense: true,
        isExpanded: true,
        icon: Icon(
          Icons.keyboard_arrow_down,
          color: Theme.of(context).colorScheme.primary,
        ),
        items: filters.entries.map((entry) {
          return DropdownMenuItem(
            value: entry.key,
            child: Row(
              children: [
                Icon(
                  _getFilterIcon(entry.key),
                  size: 16,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  entry.value,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.primary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
        onChanged: (value) {
          if (value != null) {
            onFilterChanged(value);
          }
        },
      ),
    );
  }
  
  Widget _buildTimeRangeDropdown(BuildContext context) {
    final timeRanges = {
      'day': 'Today',
      'week': 'This Week',
      'month': 'This Month',
      'year': 'This Year',
      'all': 'All Time',
    };
    
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.secondary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Theme.of(context).colorScheme.secondary.withOpacity(0.3),
        ),
      ),
      child: DropdownButton<String>(
        value: selectedTimeRange,
        underline: const SizedBox(),
        isDense: true,
        isExpanded: true,
        icon: Icon(
          Icons.keyboard_arrow_down,
          color: Theme.of(context).colorScheme.secondary,
        ),
        items: timeRanges.entries.map((entry) {
          return DropdownMenuItem(
            value: entry.key,
            child: Row(
              children: [
                Icon(
                  Icons.schedule,
                  size: 16,
                  color: Theme.of(context).colorScheme.secondary,
                ),
                const SizedBox(width: 8),
                Text(
                  entry.value,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.secondary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
        onChanged: (value) {
          if (value != null) {
            onTimeRangeChanged(value);
          }
        },
      ),
    );
  }
  
  IconData _getFilterIcon(String filter) {
    switch (filter) {
      case 'all':
        return Icons.all_inclusive;
      case 'chat':
        return Icons.chat;
      case 'analysis':
        return Icons.analytics;
      case 'voice':
        return Icons.mic;
      default:
        return Icons.filter_list;
    }
  }
}