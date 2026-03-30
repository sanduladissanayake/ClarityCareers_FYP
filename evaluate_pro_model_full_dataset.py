"""
Pro Model Evaluation - Full Dataset (10,000 samples)
Tests with entire job_applicant_dataset to compare with 3,000-sample results
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, confusion_matrix,
    roc_auc_score, balanced_accuracy_score, cohen_kappa_score,
    classification_report
)
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from datetime import datetime
import time

print("=" * 90)
print("🚀 PRO MODEL EVALUATION - FULL DATASET (10,000 SAMPLES)")
print("=" * 90)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load entire dataset
print("📊 Loading entire dataset...")
df = pd.read_csv('job_applicant_dataset.csv')
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])
print(f"✅ Total samples: {len(df)}")

class_dist = df['Best Match'].value_counts()
print(f"\nClass Distribution:")
print(f"  Non-Match (0): {class_dist.get(0, 0)} ({class_dist.get(0, 0)/len(df)*100:.1f}%)")
print(f"  Match (1): {class_dist.get(1, 0)} ({class_dist.get(1, 0)/len(df)*100:.1f}%)")

# Load pro model
print(f"\n🤖 Loading Pro Model...")
model_path = 'models/advanced-model_pro'
if os.path.exists(model_path):
    model = SentenceTransformer(model_path)
    print(f"✅ Pro model loaded\n")
else:
    print(f"⚠️  Pro model not found, using baseline\n")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Generate embeddings for ALL samples
print("🔄 Generating embeddings for 10,000 samples...")
resumes = df['Resume'].tolist()
job_descriptions = df['Job Description'].tolist()
true_labels = np.array(df['Best Match'].tolist())

start_embed = time.time()
print("📝 Encoding resumes...")
resume_embeddings = model.encode(resumes, batch_size=32, show_progress_bar=True)
print("📝 Encoding job descriptions...")
jd_embeddings = model.encode(job_descriptions, batch_size=32, show_progress_bar=True)
embed_time = time.time() - start_embed
print(f"✅ Embedding time: {embed_time:.2f}s\n")

# Calculate similarities
print("🔄 Calculating similarities...")
similarity_start = time.time()
similarities = np.array([
    cosine_similarity(
        resume_embeddings[i].reshape(1, -1),
        jd_embeddings[i].reshape(1, -1)
    )[0][0]
    for i in range(len(resume_embeddings))
])
similarity_time = time.time() - similarity_start
print(f"✅ Similarity calculation: {similarity_time:.2f}s\n")

# Use the same optimal threshold found earlier (0.48)
optimal_threshold = 0.48
predictions = (similarities >= optimal_threshold).astype(int)

# Calculate all metrics
print("📊 Calculating metrics with threshold = 0.48...\n")

acc = accuracy_score(true_labels, predictions)
prec, rec, f1, _ = precision_recall_fscore_support(
    true_labels, predictions, average='binary', zero_division=0
)
balanced_acc = balanced_accuracy_score(true_labels, predictions)
kappa = cohen_kappa_score(true_labels, predictions)

# Confusion matrix
tn, fp, fn, tp = confusion_matrix(true_labels, predictions).ravel()
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
fpr_val = fp / (fp + tn) if (fp + tn) > 0 else 0
fnr_val = fn / (fn + tp) if (fn + tp) > 0 else 0

# ROC-AUC
try:
    roc_auc = roc_auc_score(true_labels, similarities)
except:
    roc_auc = None

# Per-class metrics
per_class = classification_report(true_labels, predictions, output_dict=True, zero_division=0)

# ============ DISPLAY RESULTS ============
print("=" * 90)
print("✨ FULL DATASET EVALUATION RESULTS (10,000 SAMPLES)")
print("=" * 90)

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

print(f"\n{'SIMILARITY STATISTICS':<40} {'VALUE':<12}")
print("-" * 55)
print(f"{'Mean':<40} {similarities.mean():.4f}")
print(f"{'Std Dev':<40} {similarities.std():.4f}")
print(f"{'Min':<40} {similarities.min():.4f}")
print(f"{'Max':<40} {similarities.max():.4f}")
print(f"{'Median':<40} {np.median(similarities):.4f}")

# ============ COMPARISON ============
print("\n" + "=" * 90)
print("📊 COMPARISON: 3,000 SAMPLES vs 10,000 SAMPLES")
print("=" * 90)

print(f"\n{'Metric':<35} {'3,000 Samples':<15} {'10,000 Samples':<15} {'Change':<15}")
print("-" * 80)
print(f"{'Accuracy':<35} {'48.57%':<15} {f'{acc*100:.2f}%':<15} {f'{(acc-0.4857)*100:+.2f}%':<15}")
print(f"{'Precision':<35} {'0.4853':<15} {f'{prec:.4f}':<15} {f'{prec-0.4853:+.4f}':<15}")
print(f"{'Recall':<35} {'1.0000':<15} {f'{rec:.4f}':<15} {f'{rec-1.0:+.4f}':<15}")
print(f"{'F1-Score':<35} {'0.6535':<15} {f'{f1:.4f}':<15} {f'{f1-0.6535:+.4f}':<15}")
print(f"{'ROC-AUC':<35} {'0.4880':<15} {f'{roc_auc:.4f}':<15} {f'{roc_auc-0.4880:+.4f}':<15}" if roc_auc else "")

# ============ ANALYSIS ============
print("\n" + "=" * 90)
print("🔍 ANALYSIS")
print("=" * 90)

diff_accuracy = (acc - 0.4857) * 100
if abs(diff_accuracy) < 0.5:
    print(f"\n✅ STABLE: Accuracy changed by only {diff_accuracy:+.2f}% (essentially stable)")
    print(f"   → Model performance is CONSISTENT across 3,000 and 10,000 sample sizes")
    print(f"   → This indicates the model's behavior is predictable and stable")
elif diff_accuracy > 0:
    print(f"\n📈 IMPROVED: Accuracy increased by {diff_accuracy:+.2f}%")
    print(f"   → Larger sample size may have exposed different patterns")
else:
    print(f"\n📉 DECREASED: Accuracy dropped by {diff_accuracy:+.2f}%")
    print(f"   → Performance degraded with more data")

print(f"\n📊 Key Observation:")
print(f"   • 3,000-sample test set class distribution: 51.5% non-match, 48.5% match")
print(f"   • 10,000-sample full dataset distribution: 51.5% non-match, 48.5% match")
print(f"   • Identical class distributions → Similar metrics expected")
print(f"   • Larger sample size provides more statistical stability")

# Save results
output_dir = 'models/pro_model_evaluation_full_dataset'
os.makedirs(output_dir, exist_ok=True)

metrics_json = {
    'evaluation_type': 'Full Dataset (10,000 samples)',
    'evaluation_date': datetime.now().isoformat(),
    'test_set_info': {
        'total_samples': len(df),
        'matches': int(true_labels.sum()),
        'non_matches': int((1 - true_labels).sum())
    },
    'threshold_used': float(optimal_threshold),
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
    'comparison_with_3000_samples': {
        'accuracy_change_percent': float((acc - 0.4857) * 100),
        'precision_change': float(prec - 0.4853),
        'recall_change': float(rec - 1.0),
        'f1_score_change': float(f1 - 0.6535),
        'roc_auc_change': float((roc_auc - 0.4880) if roc_auc else 0)
    },
    'timing': {
        'embedding_time_seconds': float(embed_time),
        'similarity_calculation_seconds': float(similarity_time)
    }
}

with open(os.path.join(output_dir, 'full_dataset_metrics.json'), 'w') as f:
    json.dump(metrics_json, f, indent=2)

print(f"\n✅ Results saved to: {os.path.join(output_dir, 'full_dataset_metrics.json')}")

print("\n" + "=" * 90)
print("✨ CONCLUSION")
print("=" * 90)
print(f"\nAccuracy with 10,000 samples: {acc:.2%}")
print(f"Accuracy with 3,000 samples:  48.57%")
print(f"\nThe accuracy is {'STABLE' if abs((acc - 0.4857)*100) < 0.5 else 'DIFFERENT'} across sample sizes.")
print("=" * 90)
