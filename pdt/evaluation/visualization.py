"""
Visualization - Trajectory plots, calibration curves, ROC curves.
"""

from typing import Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, precision_recall_curve


class EvaluationVisualizer:
    """Visualization utilities for model evaluation."""
    
    def __init__(self, style: str = 'seaborn', figsize: Tuple[int, int] = (10, 6)):
        """
        Initialize visualizer.
        
        Args:
            style: Matplotlib style
            figsize: Default figure size
        """
        plt.style.use(style)
        self.figsize = figsize
        sns.set_palette("husl")
    
    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        label: Optional[str] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot ROC curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            label: Label for the curve
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        auc = np.trapz(tpr, fpr)
        
        ax.plot(fpr, tpr, label=f'{label} (AUC = {auc:.3f})' if label else f'AUC = {auc:.3f}')
        ax.plot([0, 1], [0, 1], 'k--', label='Random')
        ax.set_xlabel('False Positive Rate')
        ax.set_ylabel('True Positive Rate')
        ax.set_title('ROC Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_pr_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        label: Optional[str] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot Precision-Recall curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            label: Label for the curve
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        precision, recall, _ = precision_recall_curve(y_true, y_pred_proba)
        ap = np.trapz(precision, recall)
        
        ax.plot(recall, precision, label=f'{label} (AP = {ap:.3f})' if label else f'AP = {ap:.3f}')
        ax.set_xlabel('Recall')
        ax.set_ylabel('Precision')
        ax.set_title('Precision-Recall Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_calibration_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10,
        label: Optional[str] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot calibration curve.
        
        Args:
            y_true: True binary labels
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins
            label: Label for the curve
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        from sklearn.calibration import calibration_curve
        
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_pred_proba, n_bins=n_bins
        )
        
        ax.plot(mean_predicted_value, fraction_of_positives, 's-', label=label or 'Model')
        ax.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
        ax.set_xlabel('Mean Predicted Probability')
        ax.set_ylabel('Fraction of Positives')
        ax.set_title('Calibration Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_trajectory(
        self,
        time: np.ndarray,
        values: np.ndarray,
        patient_ids: Optional[np.ndarray] = None,
        true_values: Optional[np.ndarray] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot patient trajectory over time.
        
        Args:
            time: Time points
            values: Predicted values
            patient_ids: Patient IDs (for multiple trajectories)
            true_values: True values (for comparison)
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        if patient_ids is not None:
            # Plot multiple trajectories
            unique_patients = np.unique(patient_ids)
            for pid in unique_patients:
                mask = patient_ids == pid
                ax.plot(time[mask], values[mask], alpha=0.6, linewidth=1.5)
        else:
            ax.plot(time, values, label='Predicted', linewidth=2)
        
        if true_values is not None:
            ax.scatter(time, true_values, label='True', alpha=0.7, s=50)
        
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')
        ax.set_title('Patient Trajectory')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax
    
    def plot_feature_importance(
        self,
        feature_names: List[str],
        importances: np.ndarray,
        top_n: Optional[int] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot feature importance.
        
        Args:
            feature_names: List of feature names
            importances: Importance values
            top_n: Show only top N features (if None, show all)
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        # Sort by importance
        indices = np.argsort(importances)[::-1]
        if top_n is not None:
            indices = indices[:top_n]
        
        sorted_names = [feature_names[i] for i in indices]
        sorted_importances = importances[indices]
        
        ax.barh(range(len(sorted_names)), sorted_importances)
        ax.set_yticks(range(len(sorted_names)))
        ax.set_yticklabels(sorted_names)
        ax.set_xlabel('Importance')
        ax.set_title('Feature Importance')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        return ax
    
    def plot_confusion_matrix(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        labels: Optional[List[str]] = None,
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot confusion matrix.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        from sklearn.metrics import confusion_matrix
        
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        cm = confusion_matrix(y_true, y_pred)
        
        if labels is None:
            labels = [f'Class {i}' for i in range(len(np.unique(y_true)))]
        
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=labels, yticklabels=labels,
            ax=ax
        )
        ax.set_xlabel('Predicted')
        ax.set_ylabel('True')
        ax.set_title('Confusion Matrix')
        
        return ax
    
    def plot_distribution_comparison(
        self,
        data1: np.ndarray,
        data2: np.ndarray,
        label1: str = 'Group 1',
        label2: str = 'Group 2',
        ax: Optional[plt.Axes] = None
    ) -> plt.Axes:
        """
        Plot distribution comparison.
        
        Args:
            data1: First dataset
            data2: Second dataset
            label1: Label for first dataset
            label2: Label for second dataset
            ax: Matplotlib axes (if None, creates new)
            
        Returns:
            Matplotlib axes
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=self.figsize)
        
        ax.hist(data1, alpha=0.5, label=label1, bins=30)
        ax.hist(data2, alpha=0.5, label=label2, bins=30)
        ax.set_xlabel('Value')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution Comparison')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        return ax



