"""
Robustness Testing - Adversarial testing, sensitivity analysis.
"""

from typing import Dict, List
import numpy as np
import pandas as pd


class RobustnessTester:
    """Test model robustness."""
    
    def test_missing_data(
        self,
        model: Any,
        test_data: pd.DataFrame,
        feature_cols: List[str],
        missing_ratios: List[float] = [0.1, 0.2, 0.3, 0.5]
    ) -> Dict[float, float]:
        """
        Test model with missing data.
        
        Args:
            model: Trained model
            test_data: Test dataset
            feature_cols: Feature column names
            missing_ratios: Ratios of missing data to test
            
        Returns:
            Dictionary mapping missing ratios to accuracy
        """
        results = {}
        
        for ratio in missing_ratios:
            # Create corrupted data
            corrupted_data = test_data[feature_cols].copy()
            n_missing = int(len(corrupted_data) * len(feature_cols) * ratio)
            
            # Randomly set values to NaN
            indices = np.random.choice(corrupted_data.size, n_missing, replace=False)
            corrupted_data.values.flat[indices] = np.nan
            
            # Predict (model should handle missing data)
            try:
                predictions = model.predict(corrupted_data)
                # Compute accuracy if target available
                if 'target' in test_data.columns:
                    accuracy = (predictions == test_data['target']).mean()
                    results[ratio] = accuracy
            except:
                results[ratio] = np.nan
        
        return results
    
    def sensitivity_analysis(
        self,
        model: Any,
        test_data: pd.DataFrame,
        feature_cols: List[str],
        perturbation_size: float = 0.1
    ) -> Dict[str, float]:
        """
        Perform sensitivity analysis.
        
        Args:
            model: Trained model
            test_data: Test dataset
            feature_cols: Feature column names
            perturbation_size: Size of perturbation
            
        Returns:
            Dictionary of sensitivity scores per feature
        """
        sensitivities = {}
        baseline_pred = model.predict(test_data[feature_cols])
        
        for col in feature_cols:
            # Perturb feature
            perturbed_data = test_data[feature_cols].copy()
            perturbed_data[col] += perturbed_data[col] * perturbation_size
            
            perturbed_pred = model.predict(perturbed_data)
            
            # Compute sensitivity (change in predictions)
            sensitivity = np.mean(np.abs(perturbed_pred - baseline_pred))
            sensitivities[col] = sensitivity
        
        return sensitivities



