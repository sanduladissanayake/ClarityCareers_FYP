"""
Stage 3: Evaluate Fine-Tuned Model and Compare
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os
from datetime import datetime

print("=" * 80)
print("🟢 FINE-TUNED MODEL EVALUATION")
print("=" * 80)
print(f"📅 {datetime.now().strftime('%H:%M:%S')}")

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv('job_applicant_dataset.csv')
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])

# Get test set
_, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Best Match'])
_, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['Best Match'])
test_sample = test_df.sample(n=200, random_state=42)
print(f"✅ Using {len(test_sample)} test samples")

# Load fine-tuned model
print("\n🤖 Loading fine-tuned model...")
if not os.path.exists('models/fine-tuned-sbert'):
    print("❌ Fine-tuned model not found!")
    print("   Please run step2_finetune.py first")
    exit(1)

model = SentenceTransformer('models/fine-tuned-sbert')
print("✅ Model loaded")

# Evaluate
print("\n🔄 Computing embeddings...")
resumes = test_sample['Resume'].tolist()
job_descriptions = test_sample['Job Description'].tolist()
true_labels = test_sample['Best Match'].tolist()

resume_embeddings = model.encode(resumes, batch_size=8, show_progress_bar=True)
jd_embeddings = model.encode(job_descriptions, batch_size=8, show_progress_bar=True)

print("\n🔄 Calculating similarities...")
similarities = np.array([
    cosine_similarity(
        resume_embeddings[i].reshape(1, -1),
        jd_embeddings[i].reshape(1, -1)
    )[0][0]
    for i in range(len(resume_embeddings))
])

# Predictions
threshold = 0.5
predictions = (similarities >= threshold).astype(int)

# Metrics
accuracy = accuracy_score(true_labels, predictions)
precision, recall, f1, _ = precision_recall_fscore_support(
    true_labels, predictions, average='binary', zero_division=0
)

finetuned_metrics = {
    'accuracy': accuracy,
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'threshold': threshold,
    'num_samples': len(test_sample),
    'timestamp': datetime.now().isoformat()
}

print("\n" + "=" * 80)
print("📊 FINE-TUNED MODEL RESULTS")
print("=" * 80)
print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

# Save
os.makedirs('models/fine-tuned-evaluation', exist_ok=True)
with open('models/fine-tuned-evaluation/metrics.json', 'w') as f:
    json.dump(finetuned_metrics, f, indent=2)

# Load baseline metrics
print("\n" + "=" * 80)
print("📊 MODEL COMPARISON")
print("=" * 80)

with open('models/baseline-evaluation/metrics.json') as f:
    baseline_metrics = json.load(f)

print(f"\n{'Metric':<15} {'Baseline':<12} {'Fine-tuned':<12} {'Improvement':<12}")
print("-" * 80)

improvements = {}
for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
    baseline_val = baseline_metrics[metric]
    finetuned_val = finetuned_metrics[metric]
    improvement = ((finetuned_val - baseline_val) / baseline_val) * 100 if baseline_val > 0 else 0
    improvements[metric] = improvement
    
    print(f"{metric:<15} {baseline_val:<12.4f} {finetuned_val:<12.4f} {improvement:+.2f}%")

avg_improvement = np.mean(list(improvements.values()))
print(f"\n{'Average':<15} {'':<12} {'':<12} {avg_improvement:+.2f}%")

# Save comparison
comparison = {
    'baseline': baseline_metrics,
    'finetuned': finetuned_metrics,
    'improvements': improvements,
    'average_improvement': avg_improvement,
    'timestamp': datetime.now().isoformat()
}

os.makedirs('results', exist_ok=True)
with open('results/model_comparison.json', 'w') as f:
    json.dump(comparison, f, indent=2)

print("\n" + "=" * 80)
if avg_improvement > 0:
    print(f"✅ SUCCESS: Model improved by {avg_improvement:+.2f}% on average!")
else:
    print(f"⚠️  Model performance changed by {avg_improvement:+.2f}%")
print("=" * 80)
print(f"💾 Results saved to: results/model_comparison.json")
print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
print("=" * 80)
