"""
Train models using sklearn (works without OpenMP dependency).
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
import joblib
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns


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
    
    # Fill remaining NaN with median
    for col in X.select_dtypes(include=[np.number]).columns:
        X[col].fillna(X[col].median(), inplace=True)
    
    print(f"✓ Feature columns: {len(X.columns)}")
    print(f"✓ Target distribution: {y.value_counts().to_dict()}")
    print(f"✓ Positive rate: {y.mean()*100:.2f}%")
    
    return X, y, feature_cols


def train_random_forest(X, y, test_size=0.2):
    """Train Random Forest model."""
    print("\n" + "="*70)
    print("Training Random Forest Model")
    print("="*70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train):,} patients")
    print(f"Test set: {len(X_test):,} patients")
    
    # Initialize model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',  # Handle imbalance
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    # Train
    print("\nTraining model...")
    model.fit(X_train, y_train)
    print("✓ Training complete")
    
    # Evaluate on test set
    print("\nEvaluating on test set...")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Compute metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1': f1_score(y_test, y_pred, zero_division=0),
        'auroc': roc_auc_score(y_test, y_pred_proba),
        'auprc': average_precision_score(y_test, y_pred_proba),
        'brier_score': brier_score_loss(y_test, y_pred_proba)
    }
    
    print("\nTest Set Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 Most Important Features:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Save model
    model_path = Path("models/random_forest.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to: {model_path}")
    
    return model, metrics, X_test, y_test, y_pred_proba, feature_importance


def train_gradient_boosting(X, y, test_size=0.2):
    """Train Gradient Boosting model."""
    print("\n" + "="*70)
    print("Training Gradient Boosting Model")
    print("="*70)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Initialize model
    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42,
        verbose=1
    )
    
    # Train
    print("\nTraining model...")
    model.fit(X_train, y_train)
    print("✓ Training complete")
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'auroc': roc_auc_score(y_test, y_pred_proba),
        'auprc': average_precision_score(y_test, y_pred_proba),
        'brier_score': brier_score_loss(y_test, y_pred_proba)
    }
    
    print("\nTest Set Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Save model
    model_path = Path("models/gradient_boosting.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\n✓ Model saved to: {model_path}")
    
    return model, metrics


def create_visualizations(y_test, y_pred_proba, model_name="RandomForest"):
    """Create evaluation visualizations."""
    print("\n" + "="*70)
    print("Creating Visualizations")
    print("="*70)
    
    output_dir = Path("results/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ROC Curve
    from sklearn.metrics import roc_curve
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(10, 6))
    plt.plot(fpr, tpr, label=f'{model_name} (AUC = {auc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_dir / "roc_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_dir / 'roc_curve.png'}")
    
    # PR Curve
    from sklearn.metrics import precision_recall_curve
    precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
    ap = average_precision_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(10, 6))
    plt.plot(recall, precision, label=f'{model_name} (AP = {ap:.3f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_dir / "pr_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_dir / 'pr_curve.png'}")
    
    # Calibration Curve
    from sklearn.calibration import calibration_curve
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_test, y_pred_proba, n_bins=10
    )
    
    plt.figure(figsize=(10, 6))
    plt.plot(mean_predicted_value, fraction_of_positives, 's-', label=model_name)
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title('Calibration Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(output_dir / "calibration_curve.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {output_dir / 'calibration_curve.png'}")


def cross_validate(X, y, model_type='random_forest', n_splits=5):
    """Perform cross-validation."""
    print("\n" + "="*70)
    print(f"Cross-Validation ({model_type})")
    print("="*70)
    
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    if model_type == 'random_forest':
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
    else:
        model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
    
    # Cross-validation scores
    cv_auroc = cross_val_score(model, X, y, cv=cv, scoring='roc_auc', n_jobs=-1)
    cv_auprc = cross_val_score(model, X, y, cv=cv, scoring='average_precision', n_jobs=-1)
    
    print(f"\nAUROC: {cv_auroc.mean():.4f} (+/- {cv_auroc.std()*2:.4f})")
    print(f"AUPRC: {cv_auprc.mean():.4f} (+/- {cv_auprc.std()*2:.4f})")
    
    return {
        'auroc': cv_auroc.tolist(),
        'auprc': cv_auprc.tolist()
    }


def save_training_summary(metrics, cv_scores, feature_importance, output_path="results/training_summary.txt"):
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
        
        f.write("\nTop 20 Features:\n")
        f.write("-"*70 + "\n")
        for idx, row in feature_importance.head(20).iterrows():
            f.write(f"  {row['feature']}: {row['importance']:.4f}\n")
    
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
    
    # Train Random Forest
    model, test_metrics, X_test, y_test, y_pred_proba, feature_importance = train_random_forest(X, y)
    
    # Create visualizations
    create_visualizations(y_test, y_pred_proba, "RandomForest")
    
    # Cross-validation
    cv_scores = cross_validate(X, y, model_type='random_forest', n_splits=5)
    
    # Save summary
    save_training_summary(test_metrics, cv_scores, feature_importance)
    
    # Also train Gradient Boosting
    print("\n" + "="*70)
    print("Training Additional Model: Gradient Boosting")
    print("="*70)
    gb_model, gb_metrics = train_gradient_boosting(X, y)
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print("\nResults:")
    print(f"  Models: models/random_forest.pkl, models/gradient_boosting.pkl")
    print(f"  Visualizations: results/visualizations/")
    print(f"  Summary: results/training_summary.txt")
    print("\nModel Performance:")
    print(f"  Random Forest AUROC: {test_metrics['auroc']:.4f}")
    print(f"  Gradient Boosting AUROC: {gb_metrics['auroc']:.4f}")
    print("\nNext steps:")
    print("  1. Review visualizations and metrics")
    print("  2. Train Patient Digital Twin model (hybrid architecture)")
    print("  3. Fine-tune hyperparameters")
    print("  4. Deploy model via API")


if __name__ == "__main__":
    main()



