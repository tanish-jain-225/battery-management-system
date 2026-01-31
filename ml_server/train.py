"""
EV Battery Thermal Runaway Prediction Model Training
=====================================================
Advanced ML pipeline with ensemble methods, feature engineering,
and comprehensive model selection for optimal accuracy.
"""

import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier, 
    VotingClassifier,
    AdaBoostClassifier
)
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.metrics import (
    classification_report, 
    confusion_matrix, 
    accuracy_score,
    f1_score,
    precision_recall_fscore_support
)
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# TUNING CONFIGURATION - Adjust these for better performance
# ============================================================

# Data Configuration
# DATA_FILE = 'EV_Battery_Charging_TR_Dataset_with_Notes.csv' # Dataset file path
DATA_FILE = 'EV_Battery_Charging_5000_Extended.csv' # Dataset file path - extended version with more samples - for better training

TEST_SIZE = 0.2  # Percentage of data for testing (0.2 = 20%)
RANDOM_STATE = 42  # For reproducibility
CV_FOLDS = 5  # Cross-validation folds (higher = more reliable but slower)

# RandomForest Hyperparameters
# More estimators = better but slower | Typical range: 100-500
RF_N_ESTIMATORS = 200
# Tree depth - higher = more complex | Typical range: 10-30
RF_MAX_DEPTH = 20
# Min samples to split node | Typical range: 2-10
RF_MIN_SAMPLES_SPLIT = 5

# GradientBoosting Hyperparameters
# More estimators = better but slower | Typical range: 100-300
GB_N_ESTIMATORS = 150
# Tree depth - lower than RF | Typical range: 3-10
GB_MAX_DEPTH = 10
# Learning rate - lower = slower but better | Typical range: 0.01-0.3
GB_LEARNING_RATE = 0.1

# AdaBoost Hyperparameters
# Number of weak learners | Typical range: 50-200
ADA_N_ESTIMATORS = 100
# Learning rate - higher = faster learning | Typical range: 0.1-1.0
ADA_LEARNING_RATE = 0.5

# ============================================================

def load_and_preprocess_data(filepath):
    """Load and preprocess the battery dataset with feature engineering."""
    print("📂 Loading dataset...")
    df = pd.read_csv(filepath)
    print(f"   Dataset shape: {df.shape}")
    print(f"   Target distribution:\n{df['EventFlag'].value_counts()}\n")
    
    # Columns to drop (non-predictive features)
    drop_cols = ['Timestamp', 'ChargerID', 'CellID', 'Notes', 'TR_Probability', 'EventFlag']
    
    X = df.drop(columns=drop_cols)
    y = df['EventFlag']
    
    # Convert boolean to int
    X['MoistureDetected'] = X['MoistureDetected'].astype(int)
    
    # Feature Engineering - create derived features for better predictions
    X['TempRange'] = X['MaxTemp_C'] - X['MinTemp_C']  # Temperature variance
    X['TempDelta'] = X['MaxTemp_C'] - X['AmbientTemp_C']  # Temp above ambient
    X['VoltageDiff'] = abs(X['PackVoltage_V'] - X['DemandVoltage_V'])  # Voltage deviation
    X['CurrentDiff'] = abs(X['ChargeCurrent_A'] - X['DemandCurrent_A'])  # Current deviation
    X['PowerDensity'] = X['ChargePower_kW'] / (X['SOC_%'] + 1)  # Power per SOC
    X['ThermalRisk'] = X['MaxTemp_C'] * X['InternalResistance_mOhm'] / 100  # Thermal risk index
    X['HealthRisk'] = (100 - X['StateOfHealth_%']) * X['VibrationLevel_mg'] / 100  # Degradation risk
    
    # One-hot encode categorical variables
    X = pd.get_dummies(X)
    
    return X, y, list(X.columns)

def train_and_evaluate_model(X, y):
    """Train multiple models and select the best one using ensemble methods."""
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"🏷️  Classes: {list(le.classes_)}\n")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y_encoded
    )
    print(f"📊 Train set: {X_train.shape[0]} samples")
    print(f"📊 Test set: {X_test.shape[0]} samples\n")
    
    # Scale features for better performance
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("🔧 Training multiple models for comparison...\n")
    
    # Define multiple models to compare (using tunable hyperparameters from config)
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            min_samples_split=RF_MIN_SAMPLES_SPLIT,
            class_weight='balanced',
            random_state=RANDOM_STATE
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=GB_N_ESTIMATORS,
            max_depth=GB_MAX_DEPTH,
            learning_rate=GB_LEARNING_RATE,
            random_state=RANDOM_STATE
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=ADA_N_ESTIMATORS,
            learning_rate=ADA_LEARNING_RATE,
            random_state=RANDOM_STATE
        )
    }
    
    results = {}
    best_model = None
    best_f1 = 0
    best_name = ""
    
    for name, model in models.items():
        print(f"   Training {name}...")
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        results[name] = {'accuracy': acc, 'f1_score': f1}
        print(f"   {name}: Accuracy={acc:.4f}, F1={f1:.4f}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_name = name
    
    print(f"\n✅ Best model: {best_name} (F1={best_f1:.4f})\n")
    
    # Create Voting Ensemble for even better predictions
    print("🔗 Creating Voting Ensemble...")
    ensemble = VotingClassifier(
        estimators=[(name, model) for name, model in models.items()],
        voting='soft'  # Use probability-based voting
    )
    ensemble.fit(X_train_scaled, y_train)
    
    y_pred_ensemble = ensemble.predict(X_test_scaled)
    ensemble_acc = accuracy_score(y_test, y_pred_ensemble)
    ensemble_f1 = f1_score(y_test, y_pred_ensemble, average='weighted')
    print(f"   Ensemble: Accuracy={ensemble_acc:.4f}, F1={ensemble_f1:.4f}\n")
    
    # Use ensemble if it's better, otherwise use best single model
    if ensemble_f1 >= best_f1:
        final_model = ensemble
        final_name = "VotingEnsemble"
        final_f1 = ensemble_f1
        final_acc = ensemble_acc
    else:
        final_model = best_model
        final_name = best_name
        final_f1 = best_f1
        final_acc = accuracy_score(y_test, best_model.predict(X_test_scaled))
    
    print(f"🏆 Final model selected: {final_name}")
    
    # Cross-validation on final model
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(final_model, X_train_scaled, y_train, cv=cv, scoring='accuracy')
    print(f"📈 Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    print(f"📈 Test set accuracy: {final_acc:.4f}\n")
    
    # Detailed classification report
    y_final_pred = final_model.predict(X_test_scaled)
    print("📋 Classification Report:")
    print("-" * 50)
    print(classification_report(y_test, y_final_pred, target_names=le.classes_))
    
    # Feature importance (for RandomForest-based models)
    print("🔑 Top 10 Most Important Features:")
    print("-" * 50)
    
    # Get feature importance from the best single RandomForest model
    rf_model = models['RandomForest']
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    return final_model, le, scaler, final_acc, final_f1, feature_importance

def save_model_artifacts(model, label_encoder, scaler, model_columns, accuracy, f1, feature_importance):
    """Save model and related artifacts for production deployment."""
    print("\n💾 Saving model artifacts...")
    
    # Save model
    joblib.dump(model, 'battery_model.pkl')
    print("   ✓ battery_model.pkl")
    
    # Save label encoder
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print("   ✓ label_encoder.pkl")
    
    # Save scaler for consistent preprocessing
    joblib.dump(scaler, 'scaler.pkl')
    print("   ✓ scaler.pkl")
    
    # Save model columns for inference
    joblib.dump(model_columns, 'model_columns.pkl')
    print("   ✓ model_columns.pkl")
    
    # Save comprehensive model metadata
    metadata = {
        'accuracy': float(accuracy),
        'f1_score': float(f1),
        'n_features': len(model_columns),
        'classes': list(label_encoder.classes_),
        'model_type': type(model).__name__,
        'trained_at': datetime.now().isoformat(),
        'top_features': feature_importance.head(10).to_dict('records')
    }
    joblib.dump(metadata, 'model_metadata.pkl')
    print("   ✓ model_metadata.pkl")
    
    # Save metadata as JSON for easy reading
    with open('model_info.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("   ✓ model_info.json")

def main():
    """Main training pipeline."""
    print("=" * 60)
    print("🔋 EV Battery Thermal Runaway Prediction - Model Training")
    print("=" * 60 + "\n")
    
    # Load and preprocess data
    X, y, model_columns = load_and_preprocess_data(DATA_FILE)
    
    # Train and evaluate
    model, label_encoder, scaler, accuracy, f1, feature_importance = train_and_evaluate_model(X, y)
    
    # Save artifacts
    save_model_artifacts(model, label_encoder, scaler, model_columns, accuracy, f1, feature_importance)
    
    print("\n" + "=" * 60)
    print(f"✅ Training complete! Final Accuracy: {accuracy:.2%}, F1: {f1:.2%}")
    print("✅ Model ready for deployment.")
    print("=" * 60)

if __name__ == '__main__':
    main()