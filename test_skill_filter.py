"""
Quick test to verify the skill filtering fix is working
"""
import sys
sys.path.insert(0, 'backend')

from app.services.nlp_service import get_model_service

# Create service
nlp = get_model_service()

# Test case: Job description with fake and real skills
jd = """
Work with machine learning systems using Python
Develop authentication and authorization systems
Build recommendation systems
Create web frameworks
Use numpy for data processing
Work with React and Node.js
"""

# Test filter function
print("="*70)
print("TEST 1: Atomic Skill Validation")
print("="*70)

test_skills = [
    ("machine learning systems", False, "ends with 'systems'"),
    ("authentication and authorization systems", False, "has 'and' + ends with 'systems'"),
    ("recommendation systems", False, "ends with 'systems'"),
    ("web frameworks", False, "ends with 'frameworks'"),
    ("numpy", True, "real skill"),
    ("React", True, "real skill"),
    ("Node.js", True, "real skill"),
    ("Python", True, "real skill"),
]

all_pass = True
for skill, expected, reason in test_skills:
    result = nlp._is_valid_atomic_skill(skill)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_pass = False
    print(f"{status} | {skill:40s} | {reason} | Expected: {expected}, Got: {result}")

print("\n" + "="*70)
print("TEST 2: Skill Extraction with Filtering")
print("="*70)

extracted = nlp.extract_skills(jd)
print(f"\nRaw extracted skills: {sorted(extracted)}")

filtered = [s for s in extracted if nlp._is_valid_atomic_skill(s)]
print(f"\nFiltered skills: {sorted(filtered)}")

fake_in_extracted = [s for s in extracted if not nlp._is_valid_atomic_skill(s)]
if fake_in_extracted:
    print(f"\nFake skills that were extracted: {fake_in_extracted}")
else:
    print(f"\n✓ No fake skills in extracted set!")

print("\n" + "="*70)
print("TEST 3: Analyze Skills Function")
print("="*70)

resume = "I have Python, numpy, and React experience"
result = nlp.analyze_skills(resume, jd)

print(f"\nMatched skills: {result['matched_skills']}")
print(f"Missing skills: {result['missing_skills']}")
print(f"Skill gap: {result['skill_gap_percentage']:.1f}%")

# Check for fake skills in missing
fake_in_missing = [s for s in result['missing_skills'] if s in ["machine learning systems", "recommendation systems", "authentication and authorization systems", "web frameworks"]]
if fake_in_missing:
    print(f"\n✗ FAIL: Fake skills in missing_skills: {fake_in_missing}")
else:
    print(f"\n✓ SUCCESS: No fake compound skills in missing_skills!")

print("\n" + "="*70)
if all_pass and not fake_in_missing:
    print("ALL TESTS PASSED - FIX IS WORKING!")
else:
    print("TESTS FAILED - Fix needs adjustment")
print("="*70)
