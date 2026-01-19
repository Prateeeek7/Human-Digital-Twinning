"""
Metrics Collection - Prediction latency, accuracy drift.
"""

from typing import Dict, List, Optional
import time
from collections import defaultdict
import numpy as np


class MetricsCollector:
    """Collect metrics for monitoring."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, List] = defaultdict(list)
        self.timestamps: List[float] = []
    
    def record_prediction(
        self,
        latency: float,
        task: str,
        accuracy: Optional[float] = None
    ):
        """
        Record prediction metrics.
        
        Args:
            latency: Prediction latency in seconds
            task: Task name
            accuracy: Prediction accuracy (optional)
        """
        self.metrics[f"{task}_latency"].append(latency)
        self.timestamps.append(time.time())
        
        if accuracy is not None:
            self.metrics[f"{task}_accuracy"].append(accuracy)
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistics for all metrics.
        
        Returns:
            Dictionary of metric statistics
        """
        stats = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                stats[metric_name] = {
                    "mean": np.mean(values),
                    "std": np.std(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "count": len(values)
                }
        
        return stats
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
        self.timestamps.clear()

