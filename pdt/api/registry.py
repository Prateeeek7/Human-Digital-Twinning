"""
Model Registry - Version management and model loading.
"""

from typing import Dict, Optional, Any
import torch
import joblib
from pathlib import Path
import json


class ModelRegistry:
    """Registry for managing model versions."""
    
    def __init__(self, registry_path: str = "models/registry"):
        """
        Initialize model registry.
        
        Args:
            registry_path: Path to registry directory
        """
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict] = {}
    
    def register_model(
        self,
        name: str,
        model: Any,
        version: str = "1.0",
        metadata: Optional[Dict] = None
    ):
        """
        Register a model.
        
        Args:
            name: Model name
            model: Model object
            version: Model version
            metadata: Additional metadata
        """
        model_key = f"{name}_v{version}"
        self.models[model_key] = model
        
        model_metadata = {
            "name": name,
            "version": version,
            "metadata": metadata or {}
        }
        self.metadata[model_key] = model_metadata
        
        # Save metadata
        metadata_file = self.registry_path / f"{model_key}_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(model_metadata, f, indent=2)
    
    def load_model(self, name: str, version: Optional[str] = None) -> Any:
        """
        Load a model.
        
        Args:
            name: Model name
            version: Model version (if None, loads latest)
            
        Returns:
            Loaded model
        """
        if version is None:
            # Find latest version
            versions = [k for k in self.models.keys() if k.startswith(f"{name}_v")]
            if not versions:
                raise ValueError(f"Model {name} not found")
            version = max(versions, key=lambda x: float(x.split('_v')[1]))
        
        model_key = f"{name}_v{version}"
        
        if model_key in self.models:
            return self.models[model_key]
        
        # Try to load from file
        model_file = self.registry_path / f"{model_key}.pth"
        if model_file.exists():
            model = torch.load(model_file)
            self.models[model_key] = model
            return model
        
        raise ValueError(f"Model {model_key} not found")
    
    def save_model(self, name: str, version: str, model: Any):
        """
        Save a model to disk.
        
        Args:
            name: Model name
            version: Model version
            model: Model object
        """
        model_key = f"{name}_v{version}"
        model_file = self.registry_path / f"{model_key}.pth"
        
        if isinstance(model, torch.nn.Module):
            torch.save(model.state_dict(), model_file)
        else:
            joblib.dump(model, model_file)
    
    def list_models(self) -> Dict[str, List[str]]:
        """
        List all registered models.
        
        Returns:
            Dictionary mapping model names to versions
        """
        models_dict = {}
        for key in self.models.keys():
            name, version = key.rsplit('_v', 1)
            if name not in models_dict:
                models_dict[name] = []
            models_dict[name].append(version)
        
        return models_dict



