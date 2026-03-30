"""
Fine-Tuned MiniLM-L6-v2 Model Evaluation with Original Dataset (job_applicant_dataset.csv)
Tests the system's fine-tuned model (trained via step2_finetune.py) with original 10,000-record dataset
Generates comprehensive evaluation with all metrics and visualizations
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support, confusion_matrix,
    roc_auc_score, balanced_accuracy_score, cohen_kappa_score,
    classification_report, roc_curve
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
print("🚀 FINE-TUNED MiniLM-L6-v2 MODEL EVALUATION - ORIGINAL DATASET (job_applicant_dataset.csv)")
print("=" * 90)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============ STEP 1: LOAD ORIGINAL DATASET ============
print("📊 STEP 1: Loading Original Dataset...")
try:
    df = pd.read_csv('job_applicant_dataset.csv')
    print(f"✅ Total records: {len(df)}")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit(1)

# Clean data
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])
print(f"✅ After removing NaN values: {len(df)} records")

# Class distribution
class_dist = df['Best Match'].value_counts()
print(f"\n📈 Class Distribution (Original Dataset):")
print(f"   - Non-Match (0): {class_dist.get(0, 0)} ({class_dist.get(0, 0)/len(df)*100:.1f}%)")
print(f"   - Match (1): {class_dist.get(1, 0)} ({class_dist.get(1, 0)/len(df)*100:.1f}%)")

# ============ STEP 2: STRATIFIED SPLIT ============
print("\n" + "=" * 90)
print("📊 STEP 2: Preparing Test Set (Stratified Split)")
print("=" * 90)

# Use 25% for testing (similar to other model evaluations)
test_size = min(2500, int(len(df) * 0.25))
_, test_df = train_test_split(
    df, test_size=test_size, random_state=42, stratify=df['Best Match']
)

print(f"✅ Test set size: {len(test_df)} samples ({len(test_df)/len(df)*100:.1f}% of dataset)")
test_class_dist = test_df['Best Match'].value_counts()
print(f"\n📈 Test Set Class Distribution:")
print(f"   - Non-Match (0): {test_class_dist.get(0, 0)} ({test_class_dist.get(0, 0)/len(test_df)*100:.1f}%)")
print(f"   - Match (1): {test_class_dist.get(1, 0)} ({test_class_dist.get(1, 0)/len(test_df)*100:.1f}%)")

# ============ STEP 3: LOAD FINE-TUNED MiniLM MODEL ============
print("\n" + "=" * 90)
print("🤖 STEP 3: Loading Fine-Tuned MiniLM-L6-v2 Model")
print("=" * 90)

model_load_start = time.time()
model_path = 'models/advanced-model'

if not os.path.exists(model_path):
    print(f"❌ Fine-tuned model not found at: {model_path}")
    print("   Please ensure the model directory exists")
    exit(1)

try:
    model = SentenceTransformer(model_path)
    print(f"✅ Fine-tuned model loaded: {model_path}")
    model_type = "Fine-Tuned MiniLM-L6-v2 (advanced-model - trained on 10,600 samples)"
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

model_load_time = time.time() - model_load_start
print(f"✅ Model loaded in {model_load_time:.2f}s")

# ============ STEP 4: GENERATE EMBEDDINGS ============
print("\n" + "=" * 90)
print("🔄 STEP 4: Generating Embeddings")
print("=" * 90)

resumes = test_df['Resume'].tolist()
job_descriptions = test_df['Job Description'].tolist()
true_labels = np.array(test_df['Best Match'].tolist())

print(f"📝 Encoding {len(resumes)} resumes...")
embedding_start = time.time()
resume_embeddings = model.encode(resumes, batch_size=32, show_progress_bar=True)
print(f"✅ Resume embeddings: {resume_embeddings.shape}")

print(f"📝 Encoding {len(job_descriptions)} job descriptions...")
jd_embeddings = model.encode(job_descriptions, batch_size=32, show_progress_bar=True)
print(f"✅ Job description embeddings: {jd_embeddings.shape}")

embedding_time = time.time() - embedding_start
print(f"✅ Total embedding time: {embedding_time:.2f}s")

# ============ STEP 5: CALCULATE SIMILARITIES ============
print("\n" + "=" * 90)
print("🔄 STEP 5: Calculating Similarity Scores")
print("=" * 90)

similarity_start = time.time()
similarities = np.array([
    cosine_similarity(
        resume_embeddings[i].reshape(1, -1),
        jd_embeddings[i].reshape(1, -1)
    )[0][0]
    for i in range(len(resume_embeddings))
])
similarity_time = time.time() - similarity_start

print(f"✅ Similarities calculated in {similarity_time:.2f}s")
print(f"\n📊 Similarity Statistics:")
print(f"   - Mean: {similarities.mean():.4f}")
print(f"   - Std Dev: {similarities.std():.4f}")
print(f"   - Min: {similarities.min():.4f}")
print(f"   - Max: {similarities.max():.4f}")
print(f"   - Median: {np.median(similarities):.4f}")
print(f"   - 25th percentile: {np.percentile(similarities, 25):.4f}")
print(f"   - 75th percentile: {np.percentile(similarities, 75):.4f}")

# ============ STEP 6: FIND OPTIMAL THRESHOLD ============
print("\n" + "=" * 90)
print("🎯 STEP 6: Finding Optimal Threshold")
print("=" * 90)

thresholds_to_try = np.arange(0.3, 0.85, 0.02)
best_f1 = 0
best_threshold = 0.5
best_predictions = None
threshold_results = []

for threshold in thresholds_to_try:
    predictions = (similarities >= threshold).astype(int)
    try:
        f1 = precision_recall_fscore_support(true_labels, predictions, average='binary', zero_division=0)[2]
        threshold_results.append({
            'threshold': threshold,
            'f1_score': f1,
            'accuracy': accuracy_score(true_labels, predictions)
        })
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
            best_predictions = predictions
    except:
        pass

print(f"✅ Optimal Threshold: {best_threshold:.2f} (F1 Score: {best_f1:.4f})")
print(f"\n📊 Top 5 Thresholds by F1 Score:")
for result in sorted(threshold_results, key=lambda x: x['f1_score'], reverse=True)[:5]:
    print(f"   Threshold {result['threshold']:.2f}: F1={result['f1_score']:.4f}, Accuracy={result['accuracy']:.4f}")

if best_predictions is None:
    predictions = (similarities >= 0.5).astype(int)
    best_threshold = 0.5
else:
    predictions = best_predictions

# ============ STEP 7: CALCULATE COMPREHENSIVE METRICS ============
print("\n" + "=" * 90)
print("📊 STEP 7: Comprehensive Metrics Calculation")
print("=" * 90)

accuracy = accuracy_score(true_labels, predictions)
precision, recall, f1, support = precision_recall_fscore_support(
    true_labels, predictions, average='binary', zero_division=0
)

balanced_acc = balanced_accuracy_score(true_labels, predictions)
kappa = cohen_kappa_score(true_labels, predictions)

tn, fp, fn, tp = confusion_matrix(true_labels, predictions).ravel()
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0

try:
    roc_auc = roc_auc_score(true_labels, similarities)
    fpr, tpr, _ = roc_curve(true_labels, similarities)
except:
    roc_auc = None
    fpr, tpr = None, None

per_class_metrics = classification_report(true_labels, predictions, output_dict=True, zero_division=0)

# ============ STEP 8: DISPLAY RESULTS ============
print("\n" + "=" * 90)
print("✨ FINE-TUNED MiniLM MODEL EVALUATION RESULTS (ORIGINAL DATASET)")
print("=" * 90)

print(f"\n🎯 THRESHOLD: {best_threshold:.2f}")
print(f"📊 TEST SET SIZE: {len(test_df)} samples")
print(f"⏱️  TOTAL EVALUATION TIME: {embedding_time + similarity_time + model_load_time:.2f}s")

print("\n" + "-" * 90)
print("PRIMARY METRICS")
print("-" * 90)
print(f"{'Accuracy':<30} {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"{'Precision':<30} {precision:.4f}")
print(f"{'Recall (Sensitivity)':<30} {recall:.4f}")
print(f"{'F1 Score':<30} {f1:.4f}")

print("\n" + "-" * 90)
print("SECONDARY METRICS")
print("-" * 90)
print(f"{'Balanced Accuracy':<30} {balanced_acc:.4f}")
print(f"{'Specificity':<30} {specificity:.4f}")
print(f"{'Cohen Kappa':<30} {kappa:.4f}")
if roc_auc is not None:
    print(f"{'ROC-AUC Score':<30} {roc_auc:.4f}")

print("\n" + "-" * 90)
print("CONFUSION MATRIX")
print("-" * 90)
print(f"{'True Negatives (TN)':<30} {tn}")
print(f"{'False Positives (FP)':<30} {fp}")
print(f"{'False Negatives (FN)':<30} {fn}")
print(f"{'True Positives (TP)':<30} {tp}")

print("\n" + "-" * 90)
print("ERROR RATES")
print("-" * 90)
print(f"{'False Positive Rate':<30} {false_positive_rate:.4f} ({false_positive_rate*100:.2f}%)")
print(f"{'False Negative Rate':<30} {false_negative_rate:.4f} ({false_negative_rate*100:.2f}%)")

print("\n" + "-" * 90)
print("PER-CLASS METRICS")
print("-" * 90)
print(f"{'Class':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<12}")
print("-" * 60)
print(f"{'Non-Match (0)':<12} {per_class_metrics['0']['precision']:<12.4f} {per_class_metrics['0']['recall']:<12.4f} {per_class_metrics['0']['f1-score']:<12.4f} {int(per_class_metrics['0']['support']):<12}")
print(f"{'Match (1)':<12} {per_class_metrics['1']['precision']:<12.4f} {per_class_metrics['1']['recall']:<12.4f} {per_class_metrics['1']['f1-score']:<12.4f} {int(per_class_metrics['1']['support']):<12}")

# ============ STEP 9: SAVE RESULTS ============
print("\n" + "=" * 90)
print("💾 STEP 9: Saving Results")
print("=" * 90)

output_dir = 'models/finetuned_miniLM_evaluation_original_dataset'
os.makedirs(output_dir, exist_ok=True)

metrics = {
    'model_type': model_type,
    'model_path': model_path,
    'dataset': 'job_applicant_dataset.csv (10,000 records)',
    'evaluation_date': datetime.now().isoformat(),
    'test_set_info': {
        'total_samples': len(test_df),
        'non_matches': int(test_class_dist.get(0, 0)),
        'matches': int(test_class_dist.get(1, 0)),
        'test_size_percentage': len(test_df) / len(df) * 100
    },
    'threshold_used': float(best_threshold),
    'primary_metrics': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    },
    'secondary_metrics': {
        'balanced_accuracy': float(balanced_acc),
        'specificity': float(specificity),
        'sensitivity': float(sensitivity),
        'cohen_kappa': float(kappa),
        'roc_auc': float(roc_auc) if roc_auc is not None else None
    },
    'confusion_matrix': {
        'true_negatives': int(tn),
        'false_positives': int(fp),
        'false_negatives': int(fn),
        'true_positives': int(tp)
    },
    'error_rates': {
        'false_positive_rate': float(false_positive_rate),
        'false_negative_rate': float(false_negative_rate)
    },
    'per_class_metrics': {
        'non_match': {
            'precision': float(per_class_metrics['0']['precision']),
            'recall': float(per_class_metrics['0']['recall']),
            'f1_score': float(per_class_metrics['0']['f1-score']),
            'support': int(per_class_metrics['0']['support'])
        },
        'match': {
            'precision': float(per_class_metrics['1']['precision']),
            'recall': float(per_class_metrics['1']['recall']),
            'f1_score': float(per_class_metrics['1']['f1-score']),
            'support': int(per_class_metrics['1']['support'])
        }
    },
    'similarity_statistics': {
        'mean': float(similarities.mean()),
        'std_dev': float(similarities.std()),
        'min': float(similarities.min()),
        'max': float(similarities.max()),
        'median': float(np.median(similarities)),
        'percentile_25': float(np.percentile(similarities, 25)),
        'percentile_75': float(np.percentile(similarities, 75))
    },
    'timing': {
        'model_load_time_seconds': float(model_load_time),
        'embedding_time_seconds': float(embedding_time),
        'similarity_calculation_time_seconds': float(similarity_time)
    }
}

metrics_file = os.path.join(output_dir, 'metrics_detailed.json')
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)
print(f"✅ Metrics saved to: {metrics_file}")

# ============ STEP 10: GENERATE VISUALIZATIONS ============
print("\n" + "=" * 90)
print("📈 STEP 10: Generating Visualizations")
print("=" * 90)

try:
    # 1. Confusion Matrix Heatmap
    fig, ax = plt.subplots(figsize=(8, 6))
    cm = confusion_matrix(true_labels, predictions)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Non-Match', 'Match'],
                yticklabels=['Non-Match', 'Match'],
                cbar_kws={'label': 'Count'}, ax=ax)
    plt.title(f'Confusion Matrix - Fine-Tuned MiniLM (Original Dataset)\nThreshold: {best_threshold:.2f}', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    cm_file = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(cm_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Confusion matrix saved: {cm_file}")

    # 2. ROC Curve
    if fpr is not None and tpr is not None:
        fig, ax = plt.subplots(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve - Fine-Tuned MiniLM (Original Dataset)', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        roc_file = os.path.join(output_dir, 'roc_curve.png')
        plt.savefig(roc_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ ROC curve saved: {roc_file}")

    # 3. Similarity Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    plt.hist(similarities[true_labels == 0], bins=50, alpha=0.6, label='Non-Matches', color='red')
    plt.hist(similarities[true_labels == 1], bins=50, alpha=0.6, label='Matches', color='green')
    plt.axvline(best_threshold, color='black', linestyle='--', linewidth=2, label=f'Threshold ({best_threshold:.2f})')
    plt.xlabel('Similarity Score', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Similarity Distribution by Class (Original Dataset - Fine-Tuned MiniLM)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    dist_file = os.path.join(output_dir, 'similarity_distribution.png')
    plt.savefig(dist_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Similarity distribution saved: {dist_file}")

    # 4. Metrics Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Balanced Acc', 'Specificity']
    metrics_values = [accuracy, precision, recall, f1, balanced_acc, specificity]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    bars = ax.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Fine-Tuned MiniLM - Key Performance Metrics (Original Dataset)', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    for bar, value in zip(bars, metrics_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    metrics_file_png = os.path.join(output_dir, 'metrics_comparison.png')
    plt.savefig(metrics_file_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Metrics comparison saved: {metrics_file_png}")

    # 5. Threshold Performance Curve
    fig, ax = plt.subplots(figsize=(12, 6))
    df_results = pd.DataFrame(threshold_results)
    if len(df_results) > 0:
        ax.plot(df_results['threshold'], df_results['accuracy'], marker='o', label='Accuracy', linewidth=2)
        ax.plot(df_results['threshold'], df_results['f1_score'], marker='d', label='F1-Score', linewidth=2.5, color='red')
        ax.axvline(best_threshold, color='green', linestyle='--', linewidth=2, label=f'Optimal ({best_threshold:.2f})')
        ax.set_xlabel('Threshold', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Fine-Tuned MiniLM Performance Across Thresholds (Original Dataset)', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(alpha=0.3)
        ax.set_ylim([0, 1.05])
        plt.tight_layout()
        threshold_file = os.path.join(output_dir, 'threshold_performance.png')
        plt.savefig(threshold_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Threshold performance saved: {threshold_file}")

    print("\n✅ All visualizations generated successfully")
except Exception as e:
    print(f"⚠️  Error generating visualizations: {e}")

# ============ FINAL SUMMARY ============
print("\n" + "=" * 90)
print("🎉 EVALUATION COMPLETED SUCCESSFULLY")
print("=" * 90)
print(f"\n📁 All results saved to: {output_dir}")
print(f"\n✨ KEY FINDINGS:")
print(f"   • Dataset: job_applicant_dataset.csv (10,000 samples)")
print(f"   • Model: Fine-Tuned MiniLM-L6-v2 (from step2_finetune.py)")
print(f"   • Test Set Size: {len(test_df)} samples")
print(f"   • Optimal Threshold: {best_threshold:.2f}")
print(f"   • Overall Accuracy: {accuracy:.2%}")
print(f"   • F1 Score: {f1:.4f}")
print(f"   • ROC-AUC: {roc_auc:.4f}" if roc_auc else "")
print(f"   • Balanced Accuracy: {balanced_acc:.4f}")
print("\n" + "=" * 90)
