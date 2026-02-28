#!/usr/bin/env python3
"""
Simple usage tracker for Gemini API calls
"""

import json
from datetime import datetime
from pathlib import Path

class UsageTracker:
    def __init__(self):
        self.usage_file = Path("gemini_usage.json")
        self.load_usage()
    
    def load_usage(self):
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        else:
            self.usage = {
                "total_requests": 0,
                "chat_requests": 0,
                "vision_requests": 0,
                "daily_usage": {}
            }
    
    def save_usage(self):
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def track_request(self, request_type="chat"):
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.usage["total_requests"] += 1
        self.usage[f"{request_type}_requests"] += 1
        
        if today not in self.usage["daily_usage"]:
            self.usage["daily_usage"][today] = 0
        self.usage["daily_usage"][today] += 1
        
        self.save_usage()
    
    def get_stats(self):
        return self.usage

# Global tracker instance
tracker = UsageTracker()