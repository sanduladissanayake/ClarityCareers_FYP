"""
Stage 2: Fine-Tuning
Train model on job_applicant_dataset.csv
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import os
from datetime import datetime

print("=" * 80)
print("🚀 FINE-TUNING SENTENCE-BERT")
print("=" * 80)
print(f"📅 {datetime.now().strftime('%H:%M:%S')}")

# Load dataset
print("\n📊 Loading dataset...")
df = pd.read_csv('job_applicant_dataset.csv')
df = df.dropna(subset=['Resume', 'Job Description', 'Best Match'])

# Split
train_df, _ = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Best Match'])
print(f"✅ Training set: {len(train_df):,} samples")

# Create training examples
print("\n🔄 Preparing training data...")
train_examples = []
for _, row in train_df.iterrows():
    train_examples.append(InputExample(
        texts=[row['Resume'], row['Job Description']],
        label=float(row['Best Match'])
    ))
print(f"✅ {len(train_examples):,} training pairs created")

# Load model
print("\n🤖 Loading base model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("✅ Model loaded")

# Prepare training
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

print("\n⚙️  Training Configuration:")
print(f"   Batch Size: 16")
print(f"   Epochs: 2")
print(f"   Training Steps: {len(train_dataloader) * 2}")

# Train
print("\n🏋️  Starting training...")
print("   This will take approximately 5-8 minutes")
print("=" * 80)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=2,
    warmup_steps=100,
    output_path='models/fine-tuned-sbert',
    save_best_model=True,
    show_progress_bar=True
)

print("\n" + "=" * 80)
print("✅ FINE-TUNING COMPLETE")
print("=" * 80)
print(f"💾 Model saved to: models/fine-tuned-sbert/")
print(f"📅 {datetime.now().strftime('%H:%M:%S')}")
print("=" * 80)
