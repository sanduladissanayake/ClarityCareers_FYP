import pandas as pd

print("=" * 80)
print("JOB APPLICANT DATASET ANALYSIS")
print("=" * 80)

# Load the dataset
df = pd.read_csv('job_applicant_dataset.csv')

print(f"\n📊 DATASET STRUCTURE")
print("-" * 80)
print(f"Total Records: {len(df):,}")
print(f"Total Columns: {len(df.columns)}")
print(f"Columns: {', '.join(df.columns.tolist())}")

print(f"\n📋 FIRST 3 ROWS:")
print("-" * 80)
print(df.head(3).to_string())

print(f"\n🔍 COLUMN DATA TYPES:")
print("-" * 80)
print(df.dtypes)

print(f"\n📈 BASIC STATISTICS:")
print("-" * 80)
print(df.describe(include='all'))

print(f"\n🔎 SAMPLE VALUES PER COLUMN:")
print("-" * 80)
for col in df.columns:
    print(f"\n{col}:")
    print(f"  - Unique values: {df[col].nunique()}")
    print(f"  - Sample: {df[col].head(3).tolist()}")
    if df[col].dtype == 'object':
        print(f"  - Max length: {df[col].astype(str).str.len().max()}")

print(f"\n✅ ANALYSIS COMPLETE")
print("=" * 80)
