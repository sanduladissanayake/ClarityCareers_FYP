"""
Pro Model - Visualization Generator (ORIGINAL DATASET)
Generates visualizations from metrics.json for original dataset evaluation
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

print("=" * 90)
print("📊 PRO MODEL - GENERATING VISUALIZATIONS (ORIGINAL DATASET)")
print("=" * 90)

# Load metrics
metrics_path = 'models/pro_model_evaluation_full_dataset/full_dataset_metrics.json'
try:
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    print(f"✅ Metrics loaded: {metrics_path}\n")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Extract metrics
accuracy = metrics['primary_metrics']['accuracy']
precision = metrics['primary_metrics']['precision']
recall = metrics['primary_metrics']['recall']
f1_score = metrics['primary_metrics']['f1_score']
auc_roc = metrics['secondary_metrics']['roc_auc']
threshold = metrics['threshold_used']
specificity = metrics['secondary_metrics']['specificity']
sensitivity = metrics['secondary_metrics']['sensitivity']
balanced_accuracy = metrics['secondary_metrics']['balanced_accuracy']

cm = metrics['confusion_matrix']
tn, fp, fn, tp = cm['tn'], cm['fp'], cm['fn'], cm['tp']
total = tn + fp + fn + tp

fpr = metrics['secondary_metrics']['false_positive_rate']
fnr = metrics['secondary_metrics']['false_negative_rate']

print(f"📊 METRICS EXTRACTED:")
print(f"   Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   Precision: {precision:.4f}")
print(f"   Recall: {recall:.4f}")
print(f"   F1-Score: {f1_score:.4f}")
print(f"   ROC-AUC: {auc_roc:.4f}")
print(f"   Threshold: {threshold:.2f}\n")

output_dir = 'models/pro_model_original_dataset_visualizations'
os.makedirs(output_dir, exist_ok=True)

try:
    # 1. Confusion Matrix
    print("📊 Generating Confusion Matrix...")
    fig, ax = plt.subplots(figsize=(8, 6))
    cm_array = np.array([[tn, fp], [fn, tp]])
    sns.heatmap(cm_array, annot=True, fmt='d', cmap='RdYlGn_r',
                xticklabels=['Non-Match', 'Match'],
                yticklabels=['Non-Match', 'Match'],
                cbar_kws={'label': 'Count'}, ax=ax)
    plt.title(f'Pro Model - Confusion Matrix (Original Dataset)\nAccuracy: {accuracy:.2%}, Threshold: {threshold:.2f}', 
              fontsize=14, fontweight='bold')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: confusion_matrix.png")

    # 2. Metrics Comparison
    print("📊 Generating Metrics Comparison...")
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Balanced Acc', 'Specificity']
    metrics_values = [accuracy, precision, recall, f1_score, balanced_accuracy, specificity]
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#9467bd', '#8c564b', '#1f77b4']
    bars = ax.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Pro Model - Performance Metrics (Original Dataset)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'metrics_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: metrics_comparison.png")

    # 3. Error Analysis
    print("📊 Generating Error Analysis...")
    fig, ax = plt.subplots(figsize=(10, 6))
    error_types = ['False Positive\nRate', 'False Negative\nRate']
    error_values = [fpr, fnr]
    colors_err = ['#d62728', '#ff7f0e']
    bars = ax.bar(error_types, error_values, color=colors_err, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Rate', fontsize=12, fontweight='bold')
    ax.set_title('Pro Model - Error Rates (Original Dataset)', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, error_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}\n({value*100:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'error_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: error_analysis.png")

    # 4. Classification Breakdown
    print("📊 Generating Classification Breakdown...")
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = ['True Negatives', 'False Positives', 'False Negatives', 'True Positives']
    values = [tn, fp, fn, tp]
    colors_bd = ['#2ca02c', '#d62728', '#ff7f0e', '#1f77b4']
    bars = ax.bar(labels, values, color=colors_bd, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(f'Pro Model - Classification Results (Total: {total:,} samples)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, values):
        height = bar.get_height()
        pct = (value / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value}\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'classification_breakdown.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: classification_breakdown.png")

    # 5. Sensitivity vs Specificity
    print("📊 Generating Sensitivity vs Specificity...")
    fig, ax = plt.subplots(figsize=(8, 6))
    labels_ss = ['Sensitivity\n(TPR)', 'Specificity\n(TNR)']
    values_ss = [sensitivity, specificity]
    colors_ss = ['#2ca02c', '#8c564b']
    bars = ax.bar(labels_ss, values_ss, color=colors_ss, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Rate', fontsize=12, fontweight='bold')
    ax.set_title('Pro Model - Sensitivity vs Specificity (Original Dataset)', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, values_ss):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}\n({value*100:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sensitivity_specificity.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: sensitivity_specificity.png")

    print("\n✅ ALL VISUALIZATIONS GENERATED\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("=" * 90)
print(f"📁 Saved to: {output_dir}")
print(f"🎉 Pro Model (Original Dataset) Visualization Complete")
print("=" * 90)
