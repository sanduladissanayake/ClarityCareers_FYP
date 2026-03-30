"""
Fine-Tuned MiniLM Model - Visualization Generator from Existing Metrics
Generates comprehensive visualizations from the metrics.json evaluation data
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

print("=" * 90)
print("📊 GENERATING VISUALIZATIONS FROM EVALUATION METRICS")
print("=" * 90)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load metrics from JSON
metrics_path = 'models/advanced-model/metrics.json'
try:
    with open(metrics_path, 'r') as f:
        metrics = json.load(f)
    print(f"✅ Metrics loaded from: {metrics_path}")
except Exception as e:
    print(f"❌ Error loading metrics: {e}")
    exit(1)

# Extract metrics
accuracy = metrics['accuracy']
precision = metrics['precision']
recall = metrics['recall']
f1_score = metrics['f1_score']
auc_roc = metrics['auc_roc']
threshold = metrics['threshold']
skill_weight = metrics['skill_weight']
epochs = metrics['epochs']
sample_size = metrics['sample_size']
confusion_data = metrics['confusion_matrix']
timestamp = metrics['timestamp']

# Parse confusion matrix
tn, fp = confusion_data[0]
fn, tp = confusion_data[1]

print(f"\n📊 EXTRACTED METRICS:")
print(f"   • Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   • Precision: {precision:.4f}")
print(f"   • Recall: {recall:.4f}")
print(f"   • F1-Score: {f1_score:.4f}")
print(f"   • ROC-AUC: {auc_roc:.4f}")
print(f"   • Threshold: {threshold:.2f}")
print(f"   • Training Epochs: {epochs}")
print(f"   • Training Sample Size: {sample_size:,}")
print(f"\n📊 CONFUSION MATRIX:")
print(f"   TN: {tn}, FP: {fp}")
print(f"   FN: {fn}, TP: {tp}")

# Calculate additional metrics
total = tn + fp + fn + tp
specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
false_negative_rate = fn / (fn + tp) if (fn + tp) > 0 else 0
balanced_accuracy = (sensitivity + specificity) / 2

print(f"\n📊 CALCULATED METRICS:")
print(f"   • Specificity: {specificity:.4f}")
print(f"   • Sensitivity: {sensitivity:.4f}")
print(f"   • False Positive Rate: {false_positive_rate:.4f}")
print(f"   • False Negative Rate: {false_negative_rate:.4f}")
print(f"   • Balanced Accuracy: {balanced_accuracy:.4f}")

# ============ CREATE VISUALIZATIONS ============
print("\n" + "=" * 90)
print("📈 GENERATING VISUALIZATIONS")
print("=" * 90)

output_dir = 'models/advanced-model/evaluation_visualizations'
os.makedirs(output_dir, exist_ok=True)

try:
    # 1. Confusion Matrix Heatmap
    print("📊 Generating Confusion Matrix Heatmap...")
    fig, ax = plt.subplots(figsize=(8, 6))
    cm = np.array([[tn, fp], [fn, tp]])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Non-Match', 'Match'],
                yticklabels=['Non-Match', 'Match'],
                cbar_kws={'label': 'Count'}, ax=ax)
    plt.title(f'Confusion Matrix - Fine-Tuned MiniLM\nAccuracy: {accuracy:.2%}, Threshold: {threshold:.2f}', 
              fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    cm_file = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(cm_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {cm_file}")

    # 2. Key Metrics Bar Chart
    print("📊 Generating Metrics Comparison...")
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Balanced Acc', 'Specificity']
    metrics_values = [accuracy, precision, recall, f1_score, balanced_accuracy, specificity]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    bars = ax.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Fine-Tuned MiniLM - Key Performance Metrics', fontsize=14, fontweight='bold')
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
    print(f"   ✅ Saved: {metrics_file_png}")

    # 3. Precision vs Recall Trade-off
    print("📊 Generating Precision-Recall Trade-off...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Create a simple trade-off visualization
    thresholds_sim = np.linspace(0.1, 0.9, 20)
    # Use current metrics as reference point
    ax.scatter([recall], [precision], s=500, c='red', marker='o', label=f'Current (θ={threshold:.2f})', zorder=5, edgecolors='darkred', linewidth=2)
    ax.axhline(y=precision, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=recall, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.set_xlabel('Recall (True Positive Rate)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision (Positive Predictive Value)', fontsize=12, fontweight='bold')
    ax.set_title('Precision vs Recall Trade-off\nFine-Tuned MiniLM Model', fontsize=14, fontweight='bold')
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1])
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    # Add annotations
    ax.annotate(f'Recall: {recall:.3f}', xy=(recall, 0), xytext=(recall, -0.08),
                ha='center', fontsize=10, color='darkred', fontweight='bold')
    ax.annotate(f'Precision: {precision:.3f}', xy=(0, precision), xytext=(-0.1, precision),
                ha='right', fontsize=10, color='darkred', fontweight='bold')
    
    plt.tight_layout()
    pr_file = os.path.join(output_dir, 'precision_recall_tradeoff.png')
    plt.savefig(pr_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {pr_file}")

    # 4. Sensitivity vs Specificity
    print("📊 Generating Sensitivity-Specificity Analysis...")
    fig, ax = plt.subplots(figsize=(10, 6))
    sens_spec_labels = ['Sensitivity\n(True Positive Rate)', 'Specificity\n(True Negative Rate)']
    sens_spec_values = [sensitivity, specificity]
    colors_ss = ['#2ca02c', '#8c564b']
    bars = ax.bar(sens_spec_labels, sens_spec_values, color=colors_ss, alpha=0.7, edgecolor='black', linewidth=1.5, width=0.6)
    
    ax.set_ylabel('Rate', fontsize=12, fontweight='bold')
    ax.set_title('Model Balance: Sensitivity vs Specificity\nFine-Tuned MiniLM', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.1])
    ax.grid(axis='y', alpha=0.3)
    
    for bar, value in zip(bars, sens_spec_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{value:.3f}\n({value*100:.1f}%)', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    ss_file = os.path.join(output_dir, 'sensitivity_specificity.png')
    plt.savefig(ss_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {ss_file}")

    # 5. Classification Results Breakdown
    print("📊 Generating Classification Breakdown...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    labels = ['True Negatives\n(Correct Non-Matches)', 'False Positives\n(Wrong Matches)', 
              'False Negatives\n(Missed Matches)', 'True Positives\n(Correct Matches)']
    values = [tn, fp, fn, tp]
    colors_breakdown = ['#2ca02c', '#d62728', '#ff7f0e', '#1f77b4']
    
    bars = ax.bar(labels, values, color=colors_breakdown, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Classification Results Breakdown\nTotal Samples: {:,}'.format(total), 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    for bar, value in zip(bars, values):
        height = bar.get_height()
        percentage = (value / total) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                f'{value}\n({percentage:.1f}%)', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.xticks(rotation=0, ha='center')
    plt.tight_layout()
    breakdown_file = os.path.join(output_dir, 'classification_breakdown.png')
    plt.savefig(breakdown_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {breakdown_file}")

    # 6. Model Performance Summary Dashboard
    print("📊 Generating Performance Summary Dashboard...")
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Top metrics
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    summary_text = f"""
    💡 FINE-TUNED MiniLM MODEL - PERFORMANCE SUMMARY
    
    Overall Accuracy: {accuracy:.2%}  |  F1-Score: {f1_score:.4f}  |  ROC-AUC: {auc_roc:.4f}
    Precision: {precision:.4f}  |  Recall: {recall:.4f}  |  Threshold: {threshold:.2f}
    
    Training Configuration: {epochs} epochs, {sample_size:,} samples, Skill Weight: {skill_weight}
    """
    ax1.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11,
            family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Confusion Matrix
    ax2 = fig.add_subplot(gs[1, 0])
    cm_data = np.array([[tn, fp], [fn, tp]])
    sns.heatmap(cm_data, annot=True, fmt='d', cmap='Blues', ax=ax2,
                xticklabels=['Non-Match', 'Match'], yticklabels=['Non-Match', 'Match'],
                cbar_kws={'label': 'Count'})
    ax2.set_title('Confusion Matrix', fontweight='bold')
    ax2.set_ylabel('True Label')
    ax2.set_xlabel('Predicted Label')
    
    # Metrics
    ax3 = fig.add_subplot(gs[1, 1])
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']
    metric_values = [accuracy, precision, recall, f1_score, auc_roc]
    colors_m = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    ax3.barh(metric_labels, metric_values, color=colors_m, alpha=0.7, edgecolor='black')
    ax3.set_xlim([0, 1])
    ax3.set_title('Key Metrics', fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    for i, v in enumerate(metric_values):
        ax3.text(v + 0.02, i, f'{v:.3f}', va='center', fontweight='bold')
    
    # Error Rates
    ax4 = fig.add_subplot(gs[2, 0])
    error_labels = ['False Positive\nRate', 'False Negative\nRate']
    error_values = [false_positive_rate, false_negative_rate]
    colors_e = ['#d62728', '#ff7f0e']
    ax4.bar(error_labels, error_values, color=colors_e, alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Rate', fontweight='bold')
    ax4.set_title('Error Rates', fontweight='bold')
    ax4.set_ylim([0, 1])
    ax4.grid(axis='y', alpha=0.3)
    for i, v in enumerate(error_values):
        ax4.text(i, v + 0.02, f'{v:.3f}', ha='center', fontweight='bold')
    
    # Prediction Distribution
    ax5 = fig.add_subplot(gs[2, 1])
    confusion_values = [tn + fn, fp + tp]  # Predicted negative vs positive
    confusion_labels = ['Predicted\nNon-Match', 'Predicted\nMatch']
    colors_dist = ['#8c564b', '#1f77b4']
    ax5.bar(confusion_labels, confusion_values, color=colors_dist, alpha=0.7, edgecolor='black')
    ax5.set_ylabel('Count', fontweight='bold')
    ax5.set_title('Prediction Distribution', fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    for i, v in enumerate(confusion_values):
        ax5.text(i, v + max(confusion_values)*0.01, f'{v}', ha='center', fontweight='bold')
    
    plt.suptitle('Fine-Tuned MiniLM - Performance Dashboard', fontsize=16, fontweight='bold', y=0.995)
    dashboard_file = os.path.join(output_dir, 'performance_dashboard.png')
    plt.savefig(dashboard_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {dashboard_file}")

    print("\n✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY\n")

except Exception as e:
    print(f"❌ Error generating visualizations: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ============ FINAL SUMMARY ============
print("=" * 90)
print("🎉 VISUALIZATION GENERATION COMPLETE")
print("=" * 90)
print(f"\n📁 All visualizations saved to: {output_dir}")
print(f"\n📊 GENERATED FILES:")
print(f"   ✅ confusion_matrix.png - Confusion matrix heatmap")
print(f"   ✅ metrics_comparison.png - Key metrics bar chart")
print(f"   ✅ precision_recall_tradeoff.png - Precision vs Recall visualization")
print(f"   ✅ sensitivity_specificity.png - Sensitivity-Specificity analysis")
print(f"   ✅ classification_breakdown.png - Classification results breakdown")
print(f"   ✅ performance_dashboard.png - Comprehensive performance dashboard")
print(f"\n✨ KEY FINDINGS:")
print(f"   • Accuracy: {accuracy:.2%}")
print(f"   • Precision: {precision:.4f} (positive predictive value)")
print(f"   • Recall: {recall:.4f} (true positive rate)")
print(f"   • F1-Score: {f1_score:.4f}")
print(f"   • ROC-AUC: {auc_roc:.4f}")
print(f"   • Balanced Accuracy: {balanced_accuracy:.4f}")
print("\n" + "=" * 90)
