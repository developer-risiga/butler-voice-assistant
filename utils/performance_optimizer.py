import time
import logging
from functools import wraps
from config.settings import CONFIG

class PerformanceOptimizer:
    def __init__(self):
        self.latency_stats = {
            "wake_word": [],
            "stt": [],
            "llm": [],
            "tts": [],
            "total": []
        }
        
    def measure_latency(self, func_name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                latency = end_time - start_time
                self.latency_stats[func_name].append(latency)
                
                if latency > CONFIG["target_latency"]:
                    logging.warning(f"High latency in {func_name}: {latency:.2f}s")
                else:
                    logging.info(f"{func_name} latency: {latency:.2f}s")
                    
                return result
            return wrapper
        return decorator
    
    def get_statistics(self):
        stats = {}
        for category, latencies in self.latency_stats.items():
            if latencies:
                stats[category] = {
                    "avg": sum(latencies) / len(latencies),
                    "max": max(latencies),
                    "min": min(latencies),
                    "count": len(latencies)
                }
            else:
                stats[category] = {"avg": 0, "max": 0, "min": 0, "count": 0}
        return stats
    
    def print_performance_report(self):
        stats = self.get_statistics()
        logging.info("PERFORMANCE REPORT")
        for category, data in stats.items():
            if data["count"] > 0:
                logging.info(f"  {category:10} | Avg: {data['avg']:.2f}s | Count: {data['count']}")

performance_monitor = PerformanceOptimizer()
