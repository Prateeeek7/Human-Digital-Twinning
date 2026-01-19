"""
Evaluation Metrics - AUROC, AUPRC, C-index, Brier score, calibration.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.calibration import calibration_curve
from sksurv.metrics import concordance_index_censored
import warnings


class ClassificationMetrics:
    """Metrics for binary and multiclass classification."""
    
    @staticmethod
    def compute_auroc(y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Compute Area Under ROC Curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            
        Returns:
            AUROC score
        """
        try:
            return roc_auc_score(y_true, y_pred_proba)
        except ValueError as e:
            warnings.warn(f"AUROC computation failed: {e}")
            return np.nan
    
    @staticmethod
    def compute_auprc(y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Compute Area Under Precision-Recall Curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            
        Returns:
            AUPRC score
        """
        try:
            return average_precision_score(y_true, y_pred_proba)
        except ValueError as e:
            warnings.warn(f"AUPRC computation failed: {e}")
            return np.nan
    
    @staticmethod
    def compute_brier_score(y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """
        Compute Brier score (mean squared error of probabilities).
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            
        Returns:
            Brier score (lower is better)
        """
        try:
            return brier_score_loss(y_true, y_pred_proba)
        except ValueError as e:
            warnings.warn(f"Brier score computation failed: {e}")
            return np.nan
    
    @staticmethod
    def compute_all_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Compute all classification metrics.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            
        Returns:
            Dictionary of metric names and values
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0)
        }
        
        if y_pred_proba is not None:
            metrics['auroc'] = ClassificationMetrics.compute_auroc(y_true, y_pred_proba)
            metrics['auprc'] = ClassificationMetrics.compute_auprc(y_true, y_pred_proba)
            metrics['brier_score'] = ClassificationMetrics.compute_brier_score(y_true, y_pred_proba)
        
        return metrics


class SurvivalMetrics:
    """Metrics for survival analysis."""
    
    @staticmethod
    def compute_c_index(
        y_true_time: np.ndarray,
        y_true_event: np.ndarray,
        y_pred_risk: np.ndarray
    ) -> float:
        """
        Compute Harrell's C-index (concordance index).
        
        Args:
            y_true_time: Observed survival times
            y_true_event: Event indicators (1 if event occurred, 0 if censored)
            y_pred_risk: Predicted risk scores (higher = higher risk)
            
        Returns:
            C-index (0.5 = random, 1.0 = perfect)
        """
        try:
            c_index, _, _, _, _ = concordance_index_censored(
                y_true_event.astype(bool),
                y_true_time,
                y_pred_risk
            )
            return c_index
        except Exception as e:
            warnings.warn(f"C-index computation failed: {e}")
            return np.nan
    
    @staticmethod
    def compute_time_dependent_auc(
        y_true_time: np.ndarray,
        y_true_event: np.ndarray,
        y_pred_risk: np.ndarray,
        time_points: List[float]
    ) -> Dict[float, float]:
        """
        Compute time-dependent AUC at specified time points.
        
        Args:
            y_true_time: Observed survival times
            y_true_event: Event indicators
            y_pred_risk: Predicted risk scores
            time_points: List of time points to evaluate
            
        Returns:
            Dictionary mapping time points to AUC values
        """
        # Simplified implementation - full version would use sksurv
        results = {}
        for t in time_points:
            # Create binary outcome at time t
            y_binary = ((y_true_time <= t) & (y_true_event == 1)).astype(int)
            # Only evaluate on patients at risk at time t
            at_risk = y_true_time >= t
            if at_risk.sum() > 0:
                try:
                    auc = roc_auc_score(
                        y_binary[at_risk],
                        y_pred_risk[at_risk]
                    )
                    results[t] = auc
                except:
                    results[t] = np.nan
            else:
                results[t] = np.nan
        
        return results


class RegressionMetrics:
    """Metrics for regression tasks."""
    
    @staticmethod
    def compute_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Mean Absolute Error."""
        return np.mean(np.abs(y_true - y_pred))
    
    @staticmethod
    def compute_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute Root Mean Squared Error."""
        return np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    @staticmethod
    def compute_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Compute R-squared."""
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot > 0 else np.nan
    
    @staticmethod
    def compute_all_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute all regression metrics."""
        return {
            'mae': RegressionMetrics.compute_mae(y_true, y_pred),
            'rmse': RegressionMetrics.compute_rmse(y_true, y_pred),
            'r2': RegressionMetrics.compute_r2(y_true, y_pred)
        }


class CalibrationMetrics:
    """Metrics for probability calibration."""
    
    @staticmethod
    def compute_calibration_curve(
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute calibration curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins for calibration
            
        Returns:
            Tuple of (fraction_of_positives, mean_predicted_value) arrays
        """
        return calibration_curve(y_true, y_pred_proba, n_bins=n_bins)
    
    @staticmethod
    def compute_ece(
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Compute Expected Calibration Error (ECE).
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            ECE value
        """
        fraction_of_positives, mean_predicted_value = CalibrationMetrics.compute_calibration_curve(
            y_true, y_pred_proba, n_bins
        )
        
        # Compute ECE
        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        bin_lowers = bin_boundaries[:-1]
        bin_uppers = bin_boundaries[1:]
        
        ece = 0
        for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
            in_bin = (y_pred_proba > bin_lower) & (y_pred_proba <= bin_upper)
            prop_in_bin = in_bin.mean()
            
            if prop_in_bin > 0:
                accuracy_in_bin = y_true[in_bin].mean()
                avg_confidence_in_bin = mean_predicted_value[
                    np.argmin(np.abs(mean_predicted_value - (bin_lower + bin_upper) / 2))
                ]
                ece += np.abs(avg_confidence_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece


class ClinicalMetrics:
    """Clinical-specific evaluation metrics."""
    
    @staticmethod
    def compute_net_benefit(
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        threshold: float,
        prevalence: Optional[float] = None
    ) -> float:
        """
        Compute net benefit for decision curve analysis.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            threshold: Decision threshold
            prevalence: Disease prevalence (if None, uses observed)
            
        Returns:
            Net benefit
        """
        if prevalence is None:
            prevalence = y_true.mean()
        
        y_pred = (y_pred_proba >= threshold).astype(int)
        
        tp = ((y_true == 1) & (y_pred == 1)).sum()
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        n = len(y_true)
        
        net_benefit = (tp / n) - (fp / n) * (threshold / (1 - threshold))
        
        return net_benefit
    
    @staticmethod
    def compute_decision_curve(
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        thresholds: Optional[np.ndarray] = None
    ) -> pd.DataFrame:
        """
        Compute decision curve for various thresholds.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            thresholds: Thresholds to evaluate (if None, uses 0.01 to 0.99)
            
        Returns:
            DataFrame with threshold and net benefit
        """
        if thresholds is None:
            thresholds = np.arange(0.01, 1.0, 0.01)
        
        results = []
        for threshold in thresholds:
            net_benefit = ClinicalMetrics.compute_net_benefit(
                y_true, y_pred_proba, threshold
            )
            results.append({
                'threshold': threshold,
                'net_benefit': net_benefit
            })
        
        return pd.DataFrame(results)



