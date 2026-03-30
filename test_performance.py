"""
Performance Test for Batch Encoding Optimizations
Tests CV analysis timing with the new batch encoding fixes
"""
import time
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.nlp_service import NLPModelService

# Sample data for testing
SAMPLE_RESUME = """
John Smith
Senior Software Engineer

EXPERIENCE
Worked as Full Stack Developer at Tech Company for 5 years. 
Responsible for building scalable Python applications and leading team.
Designed microservices architecture using Django and FastAPI.
Implemented machine learning models using TensorFlow and PyTorch.
Led CI/CD pipeline improvements using Jenkins and Docker.

Python Programming
JavaScript Development
React Framework
Node.js Backend
API Development
REST Services
Microservices Architecture
Docker Containerization
Kubernetes Orchestration
AWS Cloud Services
PostgreSQL Database
MongoDB NoSQL
git Version Control
Agile Methodology
Scrum Framework

EDUCATION
BS Computer Science - State University, 2018
Certification: AWS Solutions Architect - 2020

CERTIFICATIONS
AWS Solutions Architect Associate
Google Cloud Professional Data Engineer
"""

SAMPLE_JOB_DESCRIPTION = """
Position: Senior Software Engineer

Requirements:
- 5+ years of Python development experience
- Strong expertise in FastAPI and Django
- Experience with microservices architecture
- Proficient with Docker and Kubernetes
- AWS cloud platform experience
- PostgreSQL and MongoDB knowledge
- React and JavaScript frontend skills
- RESTful API design
- CI/CD pipeline management
- Git version control
- Agile/Scrum methodologies
- Machine learning frameworks (TensorFlow/PyTorch)

Nice to Have:
- Google Cloud Platform experience
- Kubernetes certifications
- Open source contributions

Education:
- Bachelor's degree in Computer Science or related field
"""

def test_cv_analysis():
    """Test CV analysis with timing"""
    print("=" * 80)
    print("CV ANALYSIS PERFORMANCE TEST - BATCH ENCODING OPTIMIZATIONS")
    print("=" * 80)
    
    try:
        # Initialize NLP service
        print("\n1️⃣  Initializing NLP Service...")
        start_init = time.time()
        nlp_service = NLPModelService()
        init_time = time.time() - start_init
        print(f"   Initialization time: {init_time:.2f}s")
        
        # Test analyze_skills (which now uses batch encoding for resume chunks)
        print("\n2️⃣  Testing analyze_skills() with Batch Encoding...")
        start_skills = time.time()
        skills_result = nlp_service.analyze_skills(SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION)
        skills_time = time.time() - start_skills
        print(f"   ✅ Skill analysis complete in {skills_time:.2f}s")
        print(f"   📊 Missing Skills Found: {len(skills_result.get('missing_skills', []))}")
        print(f"   📊 Matched Skills: {len(skills_result.get('matched_skills', []))}")
        
        # Test generate_shap_explanation (which now uses batch encoding for tokens)
        print("\n3️⃣  Testing generate_shap_explanation() with Batch Token Encoding...")
        start_shap = time.time()
        
        # First extract hard requirements for complete analysis
        hard_reqs = nlp_service.extract_hard_requirements(SAMPLE_JOB_DESCRIPTION)
        
        shap_result = nlp_service.generate_shap_explanation(
            resume=SAMPLE_RESUME,
            job_description=SAMPLE_JOB_DESCRIPTION,
            match_score=0.75,
            cached_skills=skills_result
        )
        shap_time = time.time() - start_shap
        print(f"   ✅ SHAP explanation generated in {shap_time:.2f}s")
        print(f"   📊 Top Positive Features: {len(shap_result.get('top_positive_features', []))}")
        print(f"   📊 Top Negative Features: {len(shap_result.get('top_negative_features', []))}")
        
        # Calculate total time for full analysis
        total_time = init_time + skills_time + shap_time
        print("\n" + "=" * 80)
        print("📈 PERFORMANCE SUMMARY")
        print("=" * 80)
        print(f"Initialization:        {init_time:7.2f}s")
        print(f"Skill Analysis:        {skills_time:7.2f}s (with batch chunk encoding)")
        print(f"SHAP Explanation:      {shap_time:7.2f}s (with batch token encoding)")
        print(f"{'─' * 45}")
        print(f"TOTAL ANALYSIS TIME:   {total_time:7.2f}s")
        print("=" * 80)
        
        # Performance expectations
        print("\n✨ OPTIMIZATION RESULTS:")
        print(f"  • Total time should be < 10 seconds (target: 5-8s)")
        print(f"  • Skill analysis should be < 3 seconds (batch chunk encoding)")
        print(f"  • SHAP explanation should be < 2 seconds (batch token encoding)")
        
        if total_time < 10:
            print(f"\n✅ PASS: Total analysis time ({total_time:.2f}s) is under 10 seconds!")
        else:
            print(f"\n⚠️  WARNING: Total analysis time ({total_time:.2f}s) exceeds target of 10 seconds")
        
        # Show sample results
        print("\n" + "=" * 80)
        print("📋 SAMPLE RESULTS")
        print("=" * 80)
        print(f"\nTop Positive Features (Strengths):")
        for feature in shap_result.get('top_positive_features', [])[:3]:
            print(f"  • {feature['token']}: impact={feature['impact']:.4f}")
        
        print(f"\nTop Negative Features (Gaps):")
        for feature in shap_result.get('top_negative_features', [])[:3]:
            print(f"  • {feature['token']}: impact={feature['impact']:.4f}")
        
        print("\n✅ Performance test complete!")
        
    except Exception as e:
        print(f"\n❌ Error during performance test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_cv_analysis()
    sys.exit(0 if success else 1)
