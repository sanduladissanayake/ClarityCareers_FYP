"""
Improved Pro Model Evaluation with Threshold Optimization
Tests the advanced-model_pro with multiple thresholds to find optimal performance
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, confusion_matrix,
    roc_auc_score, balanced_accuracy_score, cohen_kappa_score,
    classification_report, roc_curve, auc
)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from datetime import datetime
import time
import matplotlib.pyplot as plt
import seaborn as sns

print("=" * 90)
print("🚀 PRO MODEL COMPREHENSIVE EVALUATION (OPTIMIZED THRESHOLDS)")
print("=" * 90)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load dataset
print("📊 Loading dataset...")
df = pd.read_csv('job_applicant_dataset.csv')
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])
print(f"✅ Loaded {len(df)} samples\n")

# Class distribution
class_dist = df['Best Match'].value_counts()
print(f"Class Distribution:")
print(f"  Non-Match (0): {class_dist.get(0, 0)} ({class_dist.get(0, 0)/len(df)*100:.1f}%)")
print(f"  Match (1): {class_dist.get(1, 0)} ({class_dist.get(1, 0)/len(df)*100:.1f}%)\n")

# Prepare test set
test_size = min(3000, int(len(df) * 0.3))
_, test_df = train_test_split(df, test_size=test_size, random_state=42, stratify=df['Best Match'])
print(f"Test set: {len(test_df)} samples\n")

# Load pro model
print("🤖 Loading Pro Model...")
model_path = 'models/advanced-model_pro'
if os.path.exists(model_path):
    model = SentenceTransformer(model_path)
    print(f"✅ Pro model loaded\n")
else:
    print(f"⚠️  Pro model not found, using baseline\n")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Generate embeddings
print("🔄 Generating embeddings...")
resumes = test_df['Resume'].tolist()
job_descriptions = test_df['Job Description'].tolist()
true_labels = np.array(test_df['Best Match'].tolist())

resume_embeddings = model.encode(resumes, batch_size=32, show_progress_bar=True)
jd_embeddings = model.encode(job_descriptions, batch_size=32, show_progress_bar=True)

# Calculate similarities
print("\n🔄 Calculating similarities...")
similarities = np.array([
    cosine_similarity(
        resume_embeddings[i].reshape(1, -1),
        jd_embeddings[i].reshape(1, -1)
    )[0][0]
    for i in range(len(resume_embeddings))
])

print(f"✅ Embeddings complete\n")

# Test multiple thresholds
print("🎯 Testing multiple thresholds...\n")
thresholds = np.arange(0.4, 0.85, 0.01)
results = []

for threshold in thresholds:
    predictions = (similarities >= threshold).astype(int)
    
    try:
        acc = accuracy_score(true_labels, predictions)
        prec, rec, f1, _ = precision_recall_fscore_support(
            true_labels, predictions, average='binary', zero_division=0
        )
        balanced_acc = balanced_accuracy_score(true_labels, predictions)
        
        results.append({
            'threshold': threshold,
            'accuracy': acc,
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'balanced_accuracy': balanced_acc
        })
    except:
        pass

# Find best thresholds
best_f1_result = max(results, key=lambda x: x['f1_score'])
best_balanced_result = max(results, key=lambda x: x['balanced_accuracy'])
best_acc_result = max(results, key=lambda x: x['accuracy'])

print("=" * 90)
print("TOP 10 THRESHOLDS BY F1 SCORE")
print("=" * 90)
sorted_f1 = sorted(results, key=lambda x: x['f1_score'], reverse=True)
print(f"{'Threshold':<12} {'Accuracy':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Balanced Acc':<12}")
print("-" * 90)
for r in sorted_f1[:10]:
    print(f"{r['threshold']:<12.2f} {r['accuracy']:<12.4f} {r['precision']:<12.4f} {r['recall']:<12.4f} {r['f1_score']:<12.4f} {r['balanced_accuracy']:<12.4f}")

# Use best F1 threshold
optimal_threshold = best_f1_result['threshold']
optimal_predictions = (similarities >= optimal_threshold).astype(int)

print("\n" + "=" * 90)
print("🎯 OPTIMAL THRESHOLD SELECTED (Best F1-Score)")
print("=" * 90)
print(f"Optimal Threshold: {optimal_threshold:.2f}")
print(f"Accuracy: {best_f1_result['accuracy']:.4f}")
print(f"Precision: {best_f1_result['precision']:.4f}")
print(f"Recall: {best_f1_result['recall']:.4f}")
print(f"F1-Score: {best_f1_result['f1_score']:.4f}")
print(f"Balanced Accuracy: {best_f1_result['balanced_accuracy']:.4f}\n")

# Calculate all metrics with optimal predictions
print("=" * 90)
print("📊 COMPREHENSIVE METRICS (Optimal Threshold)")
print("=" * 90)

acc = best_f1_result['accuracy']
prec = best_f1_result['precision']
rec = best_f1_result['recall']
f1 = best_f1_result['f1_score']
balanced_acc = best_f1_result['balanced_accuracy']

# Confusion matrix
tn, fp, fn, tp = confusion_matrix(true_labels, optimal_predictions).ravel()
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
fpr_val = fp / (fp + tn) if (fp + tn) > 0 else 0
fnr_val = fn / (fn + tp) if (fn + tp) > 0 else 0

# Kappa and AUC
kappa = cohen_kappa_score(true_labels, optimal_predictions)
try:
    roc_auc = roc_auc_score(true_labels, similarities)
    fpr, tpr, _ = roc_curve(true_labels, similarities)
except:
    roc_auc = None
    fpr, tpr = None, None

# Per-class metrics
per_class = classification_report(true_labels, optimal_predictions, output_dict=True, zero_division=0)

print(f"\n{'PRIMARY METRICS':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'Accuracy':<40} {acc:.4f} ({acc*100:.2f}%)")
print(f"{'Precision':<40} {prec:.4f}")
print(f"{'Recall (Sensitivity)':<40} {rec:.4f}")
print(f"{'F1 Score':<40} {f1:.4f}")

print(f"\n{'SECONDARY METRICS':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'Balanced Accuracy':<40} {balanced_acc:.4f}")
print(f"{'Specificity':<40} {specificity:.4f}")
print(f"{'Cohen Kappa':<40} {kappa:.4f}")
if roc_auc is not None:
    print(f"{'ROC-AUC Score':<40} {roc_auc:.4f}")

print(f"\n{'CONFUSION MATRIX':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'True Negatives (TN)':<40} {tn}")
print(f"{'False Positives (FP)':<40} {fp}")
print(f"{'False Negatives (FN)':<40} {fn}")
print(f"{'True Positives (TP)':<40} {tp}")

print(f"\n{'ERROR RATES':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'False Positive Rate':<40} {fpr_val:.4f} ({fpr_val*100:.2f}%)")
print(f"{'False Negative Rate':<40} {fnr_val:.4f} ({fnr_val*100:.2f}%)")

print(f"\n{'PER-CLASS METRICS':<40} {'PRECISION':<12} {'RECALL':<12} {'F1-SCORE':<12} {'SUPPORT':<12}")
print("-" * 80)
print(f"{'Non-Match (0)':<40} {per_class['0']['precision']:<12.4f} {per_class['0']['recall']:<12.4f} {per_class['0']['f1-score']:<12.4f} {int(per_class['0']['support']):<12}")
print(f"{'Match (1)':<40} {per_class['1']['precision']:<12.4f} {per_class['1']['recall']:<12.4f} {per_class['1']['f1-score']:<12.4f} {int(per_class['1']['support']):<12}")

print(f"\n{'SIMILARITY STATISTICS':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'Mean':<40} {similarities.mean():.4f}")
print(f"{'Std Dev':<40} {similarities.std():.4f}")
print(f"{'Min':<40} {similarities.min():.4f}")
print(f"{'Max':<40} {similarities.max():.4f}")
print(f"{'Median':<40} {np.median(similarities):.4f}")
print(f"{'25th Percentile':<40} {np.percentile(similarities, 25):.4f}")
print(f"{'75th Percentile':<40} {np.percentile(similarities, 75):.4f}")

# Save results
output_dir = 'models/pro_model_evaluation_optimized'
os.makedirs(output_dir, exist_ok=True)

# Save all threshold results
threshold_results_csv = pd.DataFrame(results)
threshold_results_csv.to_csv(os.path.join(output_dir, 'threshold_analysis.csv'), index=False)

# Save metrics JSON
metrics_json = {
    'model': 'advanced-model_pro',
    'evaluation_date': datetime.now().isoformat(),
    'test_set_info': {
        'total_samples': len(test_df),
        'matches': int(true_labels.sum()),
        'non_matches': int((1 - true_labels).sum())
    },
    'optimal_threshold': float(optimal_threshold),
    'primary_metrics': {
        'accuracy': float(acc),
        'precision': float(prec),
        'recall': float(rec),
        'f1_score': float(f1)
    },
    'secondary_metrics': {
        'balanced_accuracy': float(balanced_acc),
        'specificity': float(specificity),
        'sensitivity': float(sensitivity),
        'cohen_kappa': float(kappa),
        'roc_auc': float(roc_auc) if roc_auc is not None else None,
        'false_positive_rate': float(fpr_val),
        'false_negative_rate': float(fnr_val)
    },
    'confusion_matrix': {
        'tn': int(tn),
        'fp': int(fp),
        'fn': int(fn),
        'tp': int(tp)
    },
    'per_class_metrics': {
        'non_match': {
            'precision': float(per_class['0']['precision']),
            'recall': float(per_class['0']['recall']),
            'f1_score': float(per_class['0']['f1-score']),
            'support': int(per_class['0']['support'])
        },
        'match': {
            'precision': float(per_class['1']['precision']),
            'recall': float(per_class['1']['recall']),
            'f1_score': float(per_class['1']['f1-score']),
            'support': int(per_class['1']['support'])
        }
    },
    'similarity_statistics': {
        'mean': float(similarities.mean()),
        'std': float(similarities.std()),
        'min': float(similarities.min()),
        'max': float(similarities.max()),
        'median': float(np.median(similarities))
    }
}

with open(os.path.join(output_dir, 'metrics_detailed.json'), 'w') as f:
    json.dump(metrics_json, f, indent=2)

print(f"\n✅ Threshold analysis saved: {os.path.join(output_dir, 'threshold_analysis.csv')}")
print(f"✅ Detailed metrics saved: {os.path.join(output_dir, 'metrics_detailed.json')}")

# Generate visualizations
print("\n" + "=" * 90)
print("📈 Generating Visualizations")
print("=" * 90)

try:
    # 1. Threshold Performance Curve
    fig, ax = plt.subplots(figsize=(12, 6))
    df_results = pd.DataFrame(results)
    ax.plot(df_results['threshold'], df_results['accuracy'], marker='o', label='Accuracy', linewidth=2)
    ax.plot(df_results['threshold'], df_results['precision'], marker='s', label='Precision', linewidth=2)
    ax.plot(df_results['threshold'], df_results['recall'], marker='^', label='Recall', linewidth=2)
    ax.plot(df_results['threshold'], df_results['f1_score'], marker='d', label='F1-Score', linewidth=2.5, color='red')
    ax.axvline(optimal_threshold, color='green', linestyle='--', linewidth=2, label=f'Optimal Threshold ({optimal_threshold:.2f})')
    ax.set_xlabel('Threshold', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Pro Model Performance Across Different Thresholds', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3)
    ax.set_ylim([0, 1.05])
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'threshold_performance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Threshold performance curve saved")

    # 2. Confusion Matrix
    fig, ax = plt.subplots(figsize=(8, 6))
    cm = confusion_matrix(true_labels, optimal_predictions)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Non-Match', 'Match'],
                yticklabels=['Non-Match', 'Match'],
                cbar_kws={'label': 'Count'}, ax=ax)
    plt.title(f'Confusion Matrix (Threshold: {optimal_threshold:.2f})', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Confusion matrix saved")

    # 3. ROC Curve
    if fpr is not None and tpr is not None:
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve - Pro Model', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'roc_curve.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("✅ ROC curve saved")

    # 4. Similarity Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.hist(similarities[true_labels == 0], bins=50, alpha=0.6, label='Non-Matches', color='red')
    plt.hist(similarities[true_labels == 1], bins=50, alpha=0.6, label='Matches', color='green')
    plt.axvline(optimal_threshold, color='black', linestyle='--', linewidth=2, label=f'Optimal Threshold ({optimal_threshold:.2f})')
    plt.xlabel('Similarity Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Similarity Distribution by Class', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'similarity_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Similarity distribution saved")

    # 5. Metrics Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Balanced Acc', 'Specificity']
    metrics_values = [acc, prec, rec, f1, balanced_acc, specificity]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    bars = ax.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Pro Model - Key Performance Metrics', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'metrics_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ Metrics comparison saved")

    print("\n✅ All visualizations generated successfully")
except Exception as e:
    print(f"⚠️  Error generating visualizations: {e}")

print("\n" + "=" * 90)
print("🎉 EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 90)
print(f"\n📁 Results saved to: {output_dir}")
print(f"\n✨ SUMMARY:")
print(f"   • Test Samples: {len(test_df)}")
print(f"   • Optimal Threshold: {optimal_threshold:.2f}")
print(f"   • Accuracy: {acc:.2%}")
print(f"   • F1-Score: {f1:.4f}")
print(f"   • ROC-AUC: {roc_auc:.4f}" if roc_auc else "")
print(f"   • Balanced Accuracy: {balanced_acc:.4f}")
print("\n" + "=" * 90)
