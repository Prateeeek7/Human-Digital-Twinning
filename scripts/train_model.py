"""
Train Patient Digital Twin models on combined dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdt.models.baseline_xgboost import XGBoostBaseline
from pdt.evaluation.metrics import ClassificationMetrics
from pdt.evaluation.validation import ValidationPipeline, PatientLevelValidation
from pdt.evaluation.visualization import EvaluationVisualizer
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime


def load_combined_dataset():
    """Load the combined dataset."""
    print("="*70)
    print("Loading Combined Dataset")
    print("="*70)
    
    dataset_path = Path("data/processed/combined_dataset.csv")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Combined dataset not found: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    print(f"✓ Loaded {len(df):,} patients")
    print(f"✓ Features: {len(df.columns)}")
    
    return df


def prepare_features(df):
    """Prepare features for training."""
    print("\n" + "="*70)
    print("Preparing Features")
    print("="*70)
    
    # Exclude metadata columns
    exclude_cols = ['patient_id', 'target', 'dataset_source']
    feature_cols = [c for c in df.columns if c not in exclude_cols]
    
    X = df[feature_cols].copy()
    y = df['target'].copy()
    
    # Remove columns with all NaN
    X = X.loc[:, X.notna().any(axis=0)]
    
    print(f"✓ Feature columns: {len(X.columns)}")
    print(f"✓ Target distribution: {y.value_counts().to_dict()}")
    print(f"✓ Positive rate: {y.mean()*100:.2f}%")
    
    return X, y, feature_cols


def train_baseline_xgboost(X, y, test_size=0.2):
    """Train XGBoost baseline model."""
    print("\n" + "="*70)
    print("Training XGBoost Baseline Model")
    print("="*70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train):,} patients")
    print(f"Test set: {len(X_test):,} patients")
    
    # Initialize model
    model = XGBoostBaseline(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum()  # Handle imbalance
    )
    
    # Train
    print("\nTraining model...")
    train_metrics = model.train(
        X_train, y_train,
        validation_split=0.2,
        early_stopping_rounds=20,
        verbose=True
    )
    
    print("\nTraining Metrics:")
    for metric, value in train_metrics.get('train', {}).items():
        print(f"  {metric}: {value:.4f}")
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    test_metrics = ClassificationMetrics.compute_all_metrics(
        y_test, y_pred, y_pred_proba
    )
    
    print("\nTest Set Metrics:")
    for metric, value in test_metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Feature importance
    feature_importance = model.get_feature_importance()
    print(f"\nTop 10 Most Important Features:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.2f}")
    
    # Save model
    model_path = Path("models/baseline_xgboost.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    print(f"\n✓ Model saved to: {model_path}")
    
    return model, test_metrics, X_test, y_test, y_pred_proba


def create_visualizations(y_test, y_pred_proba, model_name="XGBoost"):
    """Create evaluation visualizations."""
    print("\n" + "="*70)
    print("Creating Visualizations")
    print("="*70)
    
    viz = EvaluationVisualizer()
    output_dir = Path("results/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ROC Curve
    print("Generating ROC curve...")
    ax = viz.plot_roc_curve(y_test, y_pred_proba, label=model_name)
    ax.figure.savefig(output_dir / "roc_curve.png", dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_dir / 'roc_curve.png'}")
    
    # PR Curve
    print("Generating PR curve...")
    ax = viz.plot_pr_curve(y_test, y_pred_proba, label=model_name)
    ax.figure.savefig(output_dir / "pr_curve.png", dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_dir / 'pr_curve.png'}")
    
    # Calibration Curve
    print("Generating calibration curve...")
    ax = viz.plot_calibration_curve(y_test, y_pred_proba, label=model_name)
    ax.figure.savefig(output_dir / "calibration_curve.png", dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved: {output_dir / 'calibration_curve.png'}")


def cross_validate(X, y, n_splits=5):
    """Perform cross-validation."""
    print("\n" + "="*70)
    print("Cross-Validation")
    print("="*70)
    
    validator = ValidationPipeline(
        strategy='stratified',
        n_splits=n_splits,
        random_state=42
    )
    
    # Convert to numpy for cross-validation
    X_array = X.values
    y_array = y.values
    
    # Create splits
    splits = validator.create_splits(X_array, y_array)
    
    cv_scores = {'auroc': [], 'auprc': [], 'brier_score': []}
    
    for fold, (train_idx, val_idx) in enumerate(splits, 1):
        print(f"\nFold {fold}/{n_splits}...")
        
        X_train_cv = X_array[train_idx]
        X_val_cv = X_array[val_idx]
        y_train_cv = y_array[train_idx]
        y_val_cv = y_array[val_idx]
        
        # Convert back to DataFrame for XGBoost
        X_train_df = pd.DataFrame(X_train_cv, columns=X.columns)
        X_val_df = pd.DataFrame(X_val_cv, columns=X.columns)
        y_train_series = pd.Series(y_train_cv)
        y_val_series = pd.Series(y_val_cv)
        
        # Train model
        model = XGBoostBaseline(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            scale_pos_weight=(y_train_cv == 0).sum() / (y_train_cv == 1).sum()
        )
        
        model.train(X_train_df, y_train_series, validation_split=0, verbose=False)
        
        # Evaluate
        y_val_pred_proba = model.predict_proba(X_val_df)[:, 1]
        
        auroc = ClassificationMetrics.compute_auroc(y_val_series, y_val_pred_proba)
        auprc = ClassificationMetrics.compute_auprc(y_val_series, y_val_pred_proba)
        brier = ClassificationMetrics.compute_brier_score(y_val_series, y_val_pred_proba)
        
        cv_scores['auroc'].append(auroc)
        cv_scores['auprc'].append(auprc)
        cv_scores['brier_score'].append(brier)
        
        print(f"  AUROC: {auroc:.4f}, AUPRC: {auprc:.4f}, Brier: {brier:.4f}")
    
    # Summary
    print("\n" + "-"*70)
    print("Cross-Validation Summary:")
    print("-"*70)
    for metric, scores in cv_scores.items():
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        print(f"  {metric.upper()}: {mean_score:.4f} (+/- {std_score:.4f})")
    
    return cv_scores


def save_training_summary(metrics, cv_scores, output_path="results/training_summary.txt"):
    """Save training summary."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("Training Summary\n")
        f.write("="*70 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Test Set Metrics:\n")
        f.write("-"*70 + "\n")
        for metric, value in metrics.items():
            f.write(f"  {metric}: {value:.4f}\n")
        
        f.write("\nCross-Validation Results:\n")
        f.write("-"*70 + "\n")
        for metric, scores in cv_scores.items():
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            f.write(f"  {metric.upper()}: {mean_score:.4f} (+/- {std_score:.4f})\n")
    
    print(f"\n✓ Training summary saved to: {output_path}")


def main():
    """Main training function."""
    print("="*70)
    print("Patient Digital Twin - Model Training")
    print("="*70)
    print()
    
    # Load data
    df = load_combined_dataset()
    
    # Prepare features
    X, y, feature_cols = prepare_features(df)
    
    # Train baseline XGBoost
    model, test_metrics, X_test, y_test, y_pred_proba = train_baseline_xgboost(X, y)
    
    # Create visualizations
    create_visualizations(y_test, y_pred_proba)
    
    # Cross-validation
    cv_scores = cross_validate(X, y, n_splits=5)
    
    # Save summary
    save_training_summary(test_metrics, cv_scores)
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print("\nResults:")
    print(f"  Model: models/baseline_xgboost.pkl")
    print(f"  Visualizations: results/visualizations/")
    print(f"  Summary: results/training_summary.txt")
    print("\nNext steps:")
    print("  1. Review visualizations and metrics")
    print("  2. Train Patient Digital Twin model (hybrid architecture)")
    print("  3. Fine-tune hyperparameters")
    print("  4. Deploy model via API")


if __name__ == "__main__":
    main()



