"""
External Validation Framework.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class ExternalValidator:
    """Framework for external validation."""
    
    def validate(
        self,
        model: Any,
        test_data: pd.DataFrame,
        target_col: str,
        feature_cols: List[str]
    ) -> Dict[str, float]:
        """
        Validate model on external dataset.
        
        Args:
            model: Trained model
            test_data: Test dataset
            target_col: Target column name
            feature_cols: Feature column names
            
        Returns:
            Dictionary of validation metrics
        """
        X_test = test_data[feature_cols]
        y_test = test_data[target_col]
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Compute metrics (simplified)
        from sklearn.metrics import accuracy_score, roc_auc_score
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred)
        }
        
        # Try AUROC if probabilities available
        try:
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            metrics['auroc'] = roc_auc_score(y_test, y_pred_proba)
        except:
            pass
        
        return metrics
    
    def subgroup_analysis(
        self,
        model: Any,
        test_data: pd.DataFrame,
        subgroup_col: str,
        target_col: str,
        feature_cols: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Perform subgroup analysis.
        
        Args:
            model: Trained model
            test_data: Test dataset
            subgroup_col: Column defining subgroups
            target_col: Target column name
            feature_cols: Feature column names
            
        Returns:
            Dictionary mapping subgroups to metrics
        """
        results = {}
        
        for subgroup in test_data[subgroup_col].unique():
            subgroup_data = test_data[test_data[subgroup_col] == subgroup]
            metrics = self.validate(model, subgroup_data, target_col, feature_cols)
            results[subgroup] = metrics
        
        return results



