"""
Validation Pipeline - Cross-validation, temporal splits, etc.
"""

from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np
import pandas as pd
from sklearn.model_selection import (
    KFold, StratifiedKFold, TimeSeriesSplit,
    train_test_split
)
from sklearn.base import BaseEstimator
import warnings


class ValidationPipeline:
    """Pipeline for model validation with various splitting strategies."""
    
    def __init__(
        self,
        strategy: str = 'kfold',
        n_splits: int = 5,
        random_state: int = 42,
        shuffle: bool = True
    ):
        """
        Initialize validation pipeline.
        
        Args:
            strategy: Validation strategy ('kfold', 'stratified', 'temporal', 'holdout')
            n_splits: Number of splits for cross-validation
            random_state: Random seed
            shuffle: Whether to shuffle data
        """
        self.strategy = strategy
        self.n_splits = n_splits
        self.random_state = random_state
        self.shuffle = shuffle
        self.splits: List[Tuple[np.ndarray, np.ndarray]] = []
    
    def create_splits(
        self,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        groups: Optional[np.ndarray] = None,
        time_col: Optional[np.ndarray] = None
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Create train/test splits based on strategy.
        
        Args:
            X: Feature matrix
            y: Target vector (optional, required for stratified)
            groups: Group labels for group-based splitting
            time_col: Time column for temporal splitting
            
        Returns:
            List of (train_indices, test_indices) tuples
        """
        n_samples = len(X)
        
        if self.strategy == 'kfold':
            cv = KFold(
                n_splits=self.n_splits,
                shuffle=self.shuffle,
                random_state=self.random_state
            )
            self.splits = list(cv.split(X))
        
        elif self.strategy == 'stratified':
            if y is None:
                raise ValueError("y required for stratified splitting")
            cv = StratifiedKFold(
                n_splits=self.n_splits,
                shuffle=self.shuffle,
                random_state=self.random_state
            )
            self.splits = list(cv.split(X, y))
        
        elif self.strategy == 'temporal':
            if time_col is None:
                warnings.warn("time_col not provided, using index as time")
                time_col = np.arange(n_samples)
            
            # Sort by time
            sort_idx = np.argsort(time_col)
            X_sorted = X[sort_idx]
            if y is not None:
                y_sorted = y[sort_idx]
            else:
                y_sorted = None
            
            cv = TimeSeriesSplit(n_splits=self.n_splits)
            splits_sorted = list(cv.split(X_sorted))
            
            # Map back to original indices
            self.splits = [
                (sort_idx[train], sort_idx[test])
                for train, test in splits_sorted
            ]
        
        elif self.strategy == 'holdout':
            test_size = 1.0 / self.n_splits if self.n_splits > 1 else 0.2
            train_idx, test_idx = train_test_split(
                np.arange(n_samples),
                test_size=test_size,
                shuffle=self.shuffle,
                random_state=self.random_state,
                stratify=y if y is not None else None
            )
            self.splits = [(train_idx, test_idx)]
        
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        return self.splits
    
    def cross_validate(
        self,
        model: BaseEstimator,
        X: np.ndarray,
        y: np.ndarray,
        scoring: Optional[Callable] = None,
        fit_params: Optional[Dict] = None
    ) -> Dict[str, List[float]]:
        """
        Perform cross-validation.
        
        Args:
            model: Scikit-learn compatible model
            X: Feature matrix
            y: Target vector
            scoring: Scoring function (y_true, y_pred) -> float
            fit_params: Additional parameters for fit()
            
        Returns:
            Dictionary with metric names and lists of scores
        """
        if not self.splits:
            self.create_splits(X, y)
        
        if scoring is None:
            # Default scoring for classification
            from sklearn.metrics import accuracy_score
            scoring = lambda y_true, y_pred: accuracy_score(y_true, y_pred)
        
        scores = {'score': []}
        
        for train_idx, test_idx in self.splits:
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Fit model
            if fit_params:
                model.fit(X_train, y_train, **fit_params)
            else:
                model.fit(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_test)
            
            # Score
            score = scoring(y_test, y_pred)
            scores['score'].append(score)
        
        return scores
    
    def temporal_split(
        self,
        data: pd.DataFrame,
        time_col: str,
        train_size: float = 0.7,
        val_size: Optional[float] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Create temporal train/val/test split.
        
        Args:
            data: DataFrame with temporal data
            time_col: Column name for time
            train_size: Proportion of data for training
            val_size: Proportion of data for validation (if None, remainder is test)
            
        Returns:
            Tuple of (train, val, test) DataFrames
        """
        data = data.sort_values(time_col)
        n = len(data)
        
        train_end = int(n * train_size)
        train_data = data.iloc[:train_end]
        
        if val_size is not None:
            val_end = int(n * (train_size + val_size))
            val_data = data.iloc[train_end:val_end]
            test_data = data.iloc[val_end:]
            return train_data, val_data, test_data
        else:
            test_data = data.iloc[train_end:]
            return train_data, None, test_data


class PatientLevelValidation:
    """Validation that respects patient-level grouping."""
    
    @staticmethod
    def patient_level_split(
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data at patient level (no patient in both train and test).
        
        Args:
            data: DataFrame with patient data
            patient_id_col: Column name for patient ID
            test_size: Proportion of patients for test set
            random_state: Random seed
            
        Returns:
            Tuple of (train_data, test_data)
        """
        patient_ids = data[patient_id_col].unique()
        np.random.seed(random_state)
        np.random.shuffle(patient_ids)
        
        n_test = int(len(patient_ids) * test_size)
        test_patients = patient_ids[:n_test]
        train_patients = patient_ids[n_test:]
        
        train_data = data[data[patient_id_col].isin(train_patients)]
        test_data = data[data[patient_id_col].isin(test_patients)]
        
        return train_data, test_data
    
    @staticmethod
    def patient_level_cv(
        data: pd.DataFrame,
        patient_id_col: str = 'patient_id',
        n_splits: int = 5,
        random_state: int = 42
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Create patient-level cross-validation splits.
        
        Args:
            data: DataFrame with patient data
            patient_id_col: Column name for patient ID
            n_splits: Number of folds
            random_state: Random seed
            
        Returns:
            List of (train_data, test_data) tuples
        """
        patient_ids = data[patient_id_col].unique()
        np.random.seed(random_state)
        np.random.shuffle(patient_ids)
        
        splits = []
        fold_size = len(patient_ids) // n_splits
        
        for i in range(n_splits):
            test_start = i * fold_size
            test_end = (i + 1) * fold_size if i < n_splits - 1 else len(patient_ids)
            test_patients = patient_ids[test_start:test_end]
            train_patients = np.concatenate([
                patient_ids[:test_start],
                patient_ids[test_end:]
            ])
            
            train_data = data[data[patient_id_col].isin(train_patients)]
            test_data = data[data[patient_id_col].isin(test_patients)]
            
            splits.append((train_data, test_data))
        
        return splits



