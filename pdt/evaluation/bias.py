"""
Bias Analysis - Performance across subgroups.
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, accuracy_score


class BiasAnalyzer:
    """Analyze model bias across subgroups."""
    
    def analyze_subgroups(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        subgroups: pd.Series
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze performance across subgroups.
        
        Args:
            predictions: Model predictions
            true_labels: True labels
            subgroups: Subgroup labels
            
        Returns:
            Dictionary mapping subgroups to metrics
        """
        results = {}
        
        for subgroup in subgroups.unique():
            mask = subgroups == subgroup
            subgroup_pred = predictions[mask]
            subgroup_true = true_labels[mask]
            
            if len(subgroup_pred) > 0:
                try:
                    auroc = roc_auc_score(subgroup_true, subgroup_pred)
                    accuracy = accuracy_score(subgroup_true, (subgroup_pred > 0.5).astype(int))
                    
                    results[subgroup] = {
                        'auroc': auroc,
                        'accuracy': accuracy,
                        'n_samples': len(subgroup_pred)
                    }
                except:
                    pass
        
        return results
    
    def compute_fairness_metrics(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        protected_attribute: pd.Series
    ) -> Dict[str, float]:
        """
        Compute fairness metrics.
        
        Args:
            predictions: Model predictions
            true_labels: True labels
            protected_attribute: Protected attribute (e.g., sex, race)
            
        Returns:
            Fairness metrics
        """
        results = {}
        
        # Equalized odds difference
        groups = protected_attribute.unique()
        if len(groups) == 2:
            group1, group2 = groups
            
            mask1 = protected_attribute == group1
            mask2 = protected_attribute == group2
            
            # True positive rates
            tpr1 = ((predictions[mask1] > 0.5) & (true_labels[mask1] == 1)).sum() / (true_labels[mask1] == 1).sum()
            tpr2 = ((predictions[mask2] > 0.5) & (true_labels[mask2] == 1)).sum() / (true_labels[mask2] == 1).sum()
            
            # False positive rates
            fpr1 = ((predictions[mask1] > 0.5) & (true_labels[mask1] == 0)).sum() / (true_labels[mask1] == 0).sum()
            fpr2 = ((predictions[mask2] > 0.5) & (true_labels[mask2] == 0)).sum() / (true_labels[mask2] == 0).sum()
            
            results['tpr_difference'] = abs(tpr1 - tpr2)
            results['fpr_difference'] = abs(fpr1 - fpr2)
            results['equalized_odds_difference'] = max(abs(tpr1 - tpr2), abs(fpr1 - fpr2))
        
        return results



