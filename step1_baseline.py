"""
Stage 1: Baseline Evaluation Only
Quick evaluation to establish baseline performance
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
print("🔵 BASELINE MODEL EVALUATION")
print("=" * 80)
print(f"📅 {datetime.now().strftime('%H:%M:%S')}")

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv('job_applicant_dataset.csv')
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])
print(f"✅ {len(df):,} records")

# Split data
_, temp_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Best Match'])
_, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['Best Match'])

# Use sample for faster evaluation
test_sample = test_df.sample(n=200, random_state=42)
print(f"📦 Using {len(test_sample)} test samples")

# Load model
print("\n🤖 Loading Sentence-BERT...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
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

metrics = {
    'accuracy': accuracy,
    'precision': precision,
    'recall': recall,
    'f1_score': f1,
    'threshold': threshold,
    'num_samples': len(test_sample),
    'timestamp': datetime.now().isoformat()
}

print("\n" + "=" * 80)
print("📊 BASELINE RESULTS")
print("=" * 80)
print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")

# Save
os.makedirs('models/baseline-evaluation', exist_ok=True)
with open('models/baseline-evaluation/metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"\n💾 Saved to: models/baseline-evaluation/metrics.json")
print("=" * 80)
print("✅ BASELINE EVALUATION COMPLETE")
print("=" * 80)
