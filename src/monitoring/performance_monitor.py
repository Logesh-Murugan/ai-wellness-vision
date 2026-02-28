#!/usr/bin/env python3
"""
Real-time Performance Monitoring for CNN Health Analysis
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path
import json
import threading

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor CNN system performance in real-time"""
    
    def __init__(self):
        self.metrics = {
            'analysis_count': 0,
            'total_processing_time': 0,
            'average_processing_time': 0,
            'cnn_success_rate': 0,
            'gemini_fallback_rate': 0,
            'error_rate': 0,
            'memory_usage': [],
            'cpu_usage': [],
            'analysis_history': []
        }
        
        self.start_time = datetime.now()
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Performance monitoring stopped")
    
    def _monitor_system(self):
        """Monitor system resources"""
        while self.monitoring:
            try:
                # Get system metrics
                memory_percent = psutil.virtual_memory().percent
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Store metrics (keep last 100 readings)
                self.metrics['memory_usage'].append({
                    'timestamp': datetime.now().isoformat(),
                    'value': memory_percent
                })
                self.metrics['cpu_usage'].append({
                    'timestamp': datetime.now().isoformat(),
                    'value': cpu_percent
                })
                
                # Keep only last 100 readings
                if len(self.metrics['memory_usage']) > 100:
                    self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
                if len(self.metrics['cpu_usage']) > 100:
                    self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-100:]
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(10)
    
    def record_analysis(self, analysis_type: str, processing_time: float, 
                       method: str, success: bool, confidence: float = 0.0):
        """Record analysis performance metrics"""
        
        self.metrics['analysis_count'] += 1
        self.metrics['total_processing_time'] += processing_time
        self.metrics['average_processing_time'] = (
            self.metrics['total_processing_time'] / self.metrics['analysis_count']
        )
        
        # Update success rates
        if method == 'CNN Deep Learning':
            cnn_analyses = len([h for h in self.metrics['analysis_history'] 
                              if h.get('method') == 'CNN Deep Learning'])
            self.metrics['cnn_success_rate'] = (cnn_analyses + 1) / self.metrics['analysis_count']
        elif method == 'Gemini Vision AI':
            gemini_analyses = len([h for h in self.metrics['analysis_history'] 
                                 if h.get('method') == 'Gemini Vision AI'])
            self.metrics['gemini_fallback_rate'] = (gemini_analyses + 1) / self.metrics['analysis_count']
        
        if not success:
            error_count = len([h for h in self.metrics['analysis_history'] if not h.get('success', True)])
            self.metrics['error_rate'] = (error_count + 1) / self.metrics['analysis_count']
        
        # Record analysis history
        analysis_record = {
            'timestamp': datetime.now().isoformat(),
            'type': analysis_type,
            'processing_time': processing_time,
            'method': method,
            'success': success,
            'confidence': confidence
        }
        
        self.metrics['analysis_history'].append(analysis_record)
        
        # Keep only last 1000 analyses
        if len(self.metrics['analysis_history']) > 1000:
            self.metrics['analysis_history'] = self.metrics['analysis_history'][-1000:]
    
    def get_performance_report(self) -> Dict:
        """Get comprehensive performance report"""
        
        uptime = datetime.now() - self.start_time
        
        # Calculate recent performance (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_analyses = [
            a for a in self.metrics['analysis_history']
            if datetime.fromisoformat(a['timestamp']) > one_hour_ago
        ]
        
        recent_avg_time = 0
        if recent_analyses:
            recent_avg_time = sum(a['processing_time'] for a in recent_analyses) / len(recent_analyses)
        
        # Get current system status
        current_memory = psutil.virtual_memory().percent
        current_cpu = psutil.cpu_percent()
        
        return {
            'system_status': {
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime),
                'current_memory_usage': current_memory,
                'current_cpu_usage': current_cpu,
                'status': 'healthy' if current_memory < 80 and current_cpu < 80 else 'warning'
            },
            'analysis_performance': {
                'total_analyses': self.metrics['analysis_count'],
                'average_processing_time': round(self.metrics['average_processing_time'], 2),
                'recent_average_time': round(recent_avg_time, 2),
                'cnn_success_rate': round(self.metrics['cnn_success_rate'] * 100, 1),
                'gemini_fallback_rate': round(self.metrics['gemini_fallback_rate'] * 100, 1),
                'error_rate': round(self.metrics['error_rate'] * 100, 1)
            },
            'recent_activity': {
                'analyses_last_hour': len(recent_analyses),
                'analysis_types': self._get_analysis_type_distribution(recent_analyses),
                'method_distribution': self._get_method_distribution(recent_analyses)
            },
            'resource_usage': {
                'memory_trend': self.metrics['memory_usage'][-10:],  # Last 10 readings
                'cpu_trend': self.metrics['cpu_usage'][-10:],
                'peak_memory': max([m['value'] for m in self.metrics['memory_usage']], default=0),
                'peak_cpu': max([c['value'] for c in self.metrics['cpu_usage']], default=0)
            }
        }
    
    def _get_analysis_type_distribution(self, analyses: List[Dict]) -> Dict:
        """Get distribution of analysis types"""
        distribution = {}
        for analysis in analyses:
            analysis_type = analysis.get('type', 'unknown')
            distribution[analysis_type] = distribution.get(analysis_type, 0) + 1
        return distribution
    
    def _get_method_distribution(self, analyses: List[Dict]) -> Dict:
        """Get distribution of processing methods"""
        distribution = {}
        for analysis in analyses:
            method = analysis.get('method', 'unknown')
            distribution[method] = distribution.get(method, 0) + 1
        return distribution
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            report = self.get_performance_report()
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Metrics exported to {filepath}")
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def get_performance_monitor():
    """Get global performance monitor instance"""
    return performance_monitor