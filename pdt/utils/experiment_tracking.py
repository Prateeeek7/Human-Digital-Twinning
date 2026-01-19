"""
Experiment Tracking - MLflow or Weights & Biases integration.
"""

from typing import Dict, Optional, Any
import os


class ExperimentTracker:
    """Experiment tracking interface."""
    
    def __init__(self, backend: str = "mlflow"):
        """
        Initialize experiment tracker.
        
        Args:
            backend: Tracking backend ('mlflow' or 'wandb')
        """
        self.backend = backend
        self.initialized = False
        
        if backend == "mlflow":
            try:
                import mlflow
                self.mlflow = mlflow
                self.initialized = True
            except ImportError:
                print("MLflow not available. Install with: pip install mlflow")
        elif backend == "wandb":
            try:
                import wandb
                self.wandb = wandb
                self.initialized = True
            except ImportError:
                print("Weights & Biases not available. Install with: pip install wandb")
    
    def start_run(self, experiment_name: str, run_name: Optional[str] = None):
        """Start experiment run."""
        if not self.initialized:
            return
        
        if self.backend == "mlflow":
            self.mlflow.set_experiment(experiment_name)
            self.mlflow.start_run(run_name=run_name)
        elif self.backend == "wandb":
            self.wandb.init(project=experiment_name, name=run_name)
    
    def log_params(self, params: Dict[str, Any]):
        """Log parameters."""
        if not self.initialized:
            return
        
        if self.backend == "mlflow":
            self.mlflow.log_params(params)
        elif self.backend == "wandb":
            self.wandb.config.update(params)
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Log metrics."""
        if not self.initialized:
            return
        
        if self.backend == "mlflow":
            self.mlflow.log_metrics(metrics, step=step)
        elif self.backend == "wandb":
            self.wandb.log(metrics, step=step)
    
    def end_run(self):
        """End experiment run."""
        if not self.initialized:
            return
        
        if self.backend == "mlflow":
            self.mlflow.end_run()
        elif self.backend == "wandb":
            self.wandb.finish()



