"""
Baseline Model - Visualization Generator from Existing Metrics
Generates comprehensive visualizations from the metrics.json evaluation data
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

print("=" * 90)
print("📊 GENERATING BASELINE MODEL VISUALIZATIONS")
print("=" * 90)
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Load metrics from JSON
metrics_path = 'models/baseline-evaluation/metrics.json'
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
threshold = metrics['threshold']
num_samples = metrics['num_samples']
timestamp = metrics['timestamp']

print(f"\n📊 EXTRACTED METRICS:")
print(f"   • Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"   • Precision: {precision:.4f}")
print(f"   • Recall: {recall:.4f}")
print(f"   • F1-Score: {f1_score:.4f}")
print(f"   • Threshold: {threshold:.2f}")
print(f"   • Sample Size: {num_samples:,}")

# Calculate additional metrics
specificity = 1 - (1 - accuracy) / (1 - recall) if recall < 1 else 1
sensitivity = recall
balanced_accuracy = (recall + specificity) / 2

# Estimate confusion matrix from metrics (approximate)
total_positives = num_samples * recall / (recall + (1-precision) / precision) if precision > 0 else 0
tp = max(0, recall * num_samples * recall / (recall + (1-accuracy)/accuracy) if accuracy > 0 else 0)
fp = max(0, num_samples - accuracy * num_samples)

print(f"\n📊 CALCULATED METRICS:")
print(f"   • Specificity: {specificity:.4f}")
print(f"   • Sensitivity: {sensitivity:.4f}")
print(f"   • Balanced Accuracy: {balanced_accuracy:.4f}")

# ============ CREATE VISUALIZATIONS ============
print("\n" + "=" * 90)
print("📈 GENERATING VISUALIZATIONS")
print("=" * 90)

output_dir = 'models/baseline-evaluation/evaluation_visualizations'
os.makedirs(output_dir, exist_ok=True)

try:
    # 1. Key Metrics Bar Chart
    print("📊 Generating Metrics Comparison...")
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics_names = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'Balanced Acc']
    metrics_values = [accuracy, precision, recall, f1_score, balanced_accuracy]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    bars = ax.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylim([0, 1.1])
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Baseline Model - Key Performance Metrics', fontsize=14, fontweight='bold')
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

    # 2. Precision vs Recall Trade-off
    print("📊 Generating Precision-Recall Trade-off...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot curve showing relationship
    recall_range = np.linspace(0, 1, 100)
    # Inverse relationship approximation
    precision_range = np.maximum(recall_range * (precision / recall) * 0.8, 0.1)
    
    ax.plot(recall_range, precision_range, 'b-', alpha=0.3, linewidth=2, label='Expected Trade-off')
    ax.scatter([recall], [precision], s=500, c='red', marker='o', label=f'Current (θ={threshold:.2f})', 
               zorder=5, edgecolors='darkred', linewidth=2)
    ax.axhline(y=precision, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.axvline(x=recall, color='gray', linestyle='--', alpha=0.5, linewidth=1)
    
    ax.set_xlabel('Recall (True Positive Rate)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precision (Positive Predictive Value)', fontsize=12, fontweight='bold')
    ax.set_title('Precision vs Recall Trade-off\nBaseline Model', fontsize=14, fontweight='bold')
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

    # 3. Sensitivity vs Specificity
    print("📊 Generating Sensitivity-Specificity Analysis...")
    fig, ax = plt.subplots(figsize=(10, 6))
    sens_spec_labels = ['Sensitivity\n(True Positive Rate)', 'Specificity\n(True Negative Rate)']
    sens_spec_values = [sensitivity, specificity]
    colors_ss = ['#2ca02c', '#8c564b']
    bars = ax.bar(sens_spec_labels, sens_spec_values, color=colors_ss, alpha=0.7, edgecolor='black', 
                   linewidth=1.5, width=0.6)
    
    ax.set_ylabel('Rate', fontsize=12, fontweight='bold')
    ax.set_title('Model Balance: Sensitivity vs Specificity\nBaseline Model', fontsize=14, fontweight='bold')
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

    # 4. Model Efficiency Gauge
    print("📊 Generating Performance Gauge...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy gauge
    categories = ['Accuracy', 'F1-Score']
    values = [accuracy, f1_score]
    angles = np.linspace(0, np.pi, len(categories), endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]
    
    ax1 = plt.subplot(121, projection='polar')
    ax1.plot(angles_plot, values_plot, 'o-', linewidth=2, color='#1f77b4')
    ax1.fill(angles_plot, values_plot, alpha=0.25, color='#1f77b4')
    ax1.set_xticks(angles)
    ax1.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax1.set_ylim([0, 1])
    ax1.set_title('Performance Metrics\nBaseline Model', fontsize=12, fontweight='bold', pad=20)
    ax1.grid(True)
    
    # All metrics radar
    ax2 = plt.subplot(122, projection='polar')
    all_metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    all_values = [accuracy, precision, recall, f1_score]
    angles_all = np.linspace(0, 2*np.pi, len(all_metrics), endpoint=False).tolist()
    all_values_plot = all_values + [all_values[0]]
    angles_all_plot = angles_all + [angles_all[0]]
    
    ax2.plot(angles_all_plot, all_values_plot, 'o-', linewidth=2, color='#ff7f0e')
    ax2.fill(angles_all_plot, all_values_plot, alpha=0.25, color='#ff7f0e')
    ax2.set_xticks(angles_all)
    ax2.set_xticklabels(all_metrics, fontsize=11, fontweight='bold')
    ax2.set_ylim([0, 1])
    ax2.set_title('All Metrics Comparison\nBaseline Model', fontsize=12, fontweight='bold', pad=20)
    ax2.grid(True)
    
    gauge_file = os.path.join(output_dir, 'performance_gauge.png')
    plt.tight_layout()
    plt.savefig(gauge_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"   ✅ Saved: {gauge_file}")

    # 5. Performance Summary Dashboard
    print("📊 Generating Performance Summary Dashboard...")
    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    
    # Top metrics summary
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis('off')
    summary_text = f"""
    💡 BASELINE MODEL - PERFORMANCE SUMMARY
    
    Overall Accuracy: {accuracy:.2%}  |  F1-Score: {f1_score:.4f}  |  Recall: {recall:.4f}
    Precision: {precision:.4f}  |  Threshold: {threshold:.2f}  |  Samples: {num_samples:,}
    
    Generated: {timestamp}
    """
    ax1.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=11,
            family='monospace', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Main metrics bar chart
    ax2 = fig.add_subplot(gs[1, 0])
    metric_labels = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    metric_values = [accuracy, precision, recall, f1_score]
    colors_m = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    ax2.barh(metric_labels, metric_values, color=colors_m, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.set_xlim([0, 1])
    ax2.set_title('Key Performance Metrics', fontweight='bold', fontsize=11)
    ax2.grid(axis='x', alpha=0.3)
    for i, v in enumerate(metric_values):
        ax2.text(v + 0.02, i, f'{v:.3f}', va='center', fontweight='bold', fontsize=10)
    
    # Sensitivity vs Specificity
    ax3 = fig.add_subplot(gs[1, 1])
    sens_spec = ['Sensitivity', 'Specificity']
    sens_spec_vals = [sensitivity, specificity]
    colors_e = ['#2ca02c', '#8c564b']
    ax3.bar(sens_spec, sens_spec_vals, color=colors_e, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.set_ylabel('Rate', fontweight='bold', fontsize=10)
    ax3.set_title('Sensitivity vs Specificity', fontweight='bold', fontsize=11)
    ax3.set_ylim([0, 1.15])
    ax3.grid(axis='y', alpha=0.3)
    for i, v in enumerate(sens_spec_vals):
        ax3.text(i, v + 0.03, f'{v:.3f}', ha='center', fontweight='bold', fontsize=10)
    
    # Sample distribution
    ax4 = fig.add_subplot(gs[2, 0])
    sample_labels = ['Evaluated\nSamples']
    sample_vals = [num_samples]
    ax4.bar(sample_labels, sample_vals, color='#9467bd', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax4.set_ylabel('Count', fontweight='bold', fontsize=10)
    ax4.set_title('Dataset Size', fontweight='bold', fontsize=11)
    ax4.grid(axis='y', alpha=0.3)
    ax4.text(0, num_samples + 5, f'{num_samples}', ha='center', fontweight='bold', fontsize=11)
    
    # Threshold info
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    threshold_text = f"""
    🎯 DECISION THRESHOLD: {threshold:.2f}
    
    • Predictions >= {threshold:.2f} → Match
    • Predictions < {threshold:.2f} → Non-Match
    
    Balanced Accuracy: {balanced_accuracy:.4f}
    """
    ax5.text(0.5, 0.5, threshold_text, ha='center', va='center', fontsize=10,
            family='monospace', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5),
            fontweight='bold')
    
    plt.suptitle('Baseline Model - Performance Dashboard', fontsize=16, fontweight='bold', y=0.995)
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
print(f"   ✅ metrics_comparison.png - Key metrics bar chart")
print(f"   ✅ precision_recall_tradeoff.png - Precision vs Recall visualization")
print(f"   ✅ sensitivity_specificity.png - Sensitivity-Specificity analysis")
print(f"   ✅ performance_gauge.png - Radar charts for model performance")
print(f"   ✅ performance_dashboard.png - Comprehensive performance dashboard")
print(f"\n✨ KEY FINDINGS:")
print(f"   • Accuracy: {accuracy:.2%}")
print(f"   • Precision: {precision:.4f} (positive predictive value)")
print(f"   • Recall: {recall:.4f} (true positive rate)")
print(f"   • F1-Score: {f1_score:.4f} (harmonic mean of precision & recall)")
print(f"\n" + "=" * 90 + "\n")
