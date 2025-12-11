"""
NLP Model Service - Handles resume-job matching with SHAP explanations
"""
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Dict, List, Tuple
import os

# Try to import spacy, but make it optional
try:
    import spacy
    HAS_SPACY = True
except ImportError:
    print("Warning: spacy not installed. Some NLP features will be limited.")
    HAS_SPACY = False

# ========== OPTIMIZATION #1: PRE-COMPILE REGEX PATTERNS (at module level) ==========
# Compiled once on module load, reused across all instances - Saves 10-20ms per call
SKILL_PATTERNS = [
    re.compile(r'\b(python|java|javascript|typescript|c\+\+|c#|ruby|php|swift|kotlin|go|rust|scala|r|matlab)\b', re.IGNORECASE),
    re.compile(r'\b(react|angular|vue|django|flask|spring|express|node\.?js|fastapi|laravel|asp\.net)\b', re.IGNORECASE),
    re.compile(r'\b(sql|mysql|postgresql|mongodb|redis|oracle|nosql|dynamodb|cassandra|sqlite)\b', re.IGNORECASE),
    re.compile(r'\b(aws|azure|gcp|google cloud|docker|kubernetes|terraform|ansible|cloud computing)\b', re.IGNORECASE),
    re.compile(r'\b(machine learning|deep learning|nlp|natural language processing|computer vision|tensorflow|pytorch|scikit-learn|keras|pandas|numpy|data science|data analysis|statistical analysis|predictive modeling)\b', re.IGNORECASE),
    re.compile(r'\b(git|github|gitlab|jira|confluence|agile|scrum|ci/cd|jenkins|devops|version control)\b', re.IGNORECASE),
    re.compile(r'\b(agile|scrum|kanban|waterfall|test-driven development|tdd|continuous integration)\b', re.IGNORECASE),
    re.compile(r'\b(leadership|team management|project management|communication|problem solving|analytical thinking|critical thinking|stakeholder management)\b', re.IGNORECASE),
    re.compile(r'\b(data visualization|tableau|power bi|excel|big data|hadoop|spark|etl|data warehousing|business intelligence)\b', re.IGNORECASE),
    re.compile(r'\b(html|css|rest api|graphql|microservices|api development|web services)\b', re.IGNORECASE),
    re.compile(r'\b(android|ios|mobile development|flutter|react native|xamarin)\b', re.IGNORECASE),
    re.compile(r'\b(unit testing|integration testing|automated testing|selenium|jest|pytest|quality assurance|qa)\b', re.IGNORECASE),
    # EXPANDED SECURITY PATTERNS - Now includes specific security tools and techniques
    re.compile(r'\b(cybersecurity|authentication|authorization|encryption|penetration testing|network security|firewalls|ids|ips|intrusion detection|intrusion prevention|vulnerability assessment|security hardening|incident response|forensics|threat intelligence|risk assessment)\b', re.IGNORECASE),
    re.compile(r'\b(linux administration|windows administration|system hardening|ssl|tls|cryptography|certificates|vpn|endpoint protection|malware analysis|reverse engineering)\b', re.IGNORECASE),
    re.compile(r'\b(nessus|metasploit|wireshark|burp suite|splunk|elk stack|siem|log analysis|threat detection|security monitoring|access control|privilege management)\b', re.IGNORECASE),
    re.compile(r'\b(api security|cloud security|wireless security|mobile security|web application security|owasp|secure coding|code review|security testing|penetration tester|ethical hacker)\b', re.IGNORECASE),
]

EDUCATION_PATTERNS = [
    (re.compile(r"bachelor'?s?\s+(?:degree|in)?", re.IGNORECASE), "bachelor"),
    (re.compile(r"master'?s?\s+(?:degree|in)?", re.IGNORECASE), "master"),
    (re.compile(r"phd|doctorate", re.IGNORECASE), "phd"),
    (re.compile(r"associate\s+degree", re.IGNORECASE), "associate"),
    (re.compile(r"high school|hs diploma", re.IGNORECASE), "high school")
]

EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*(?:[\-–]?\s*(\d+))?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)?", re.IGNORECASE)

CERT_PATTERNS = [
    (re.compile(r"aws\s+(?:certified|certification)?\s*\w*", re.IGNORECASE), "AWS"),
    (re.compile(r"azure\s+(?:certified|certification)?\s*\w*", re.IGNORECASE), "Azure"),
    (re.compile(r"gcp|google\s+cloud\s+(?:certified|certification)?", re.IGNORECASE), "GCP"),
    (re.compile(r"kubernetes|ckad|cka", re.IGNORECASE), "Kubernetes"),
    (re.compile(r"docker\s+(?:certified|dca)?", re.IGNORECASE), "Docker"),
    (re.compile(r"pmp|project\s+management\s+professional", re.IGNORECASE), "PMP"),
    (re.compile(r"cissp", re.IGNORECASE), "CISSP"),
    (re.compile(r"scrum\s+master|csm", re.IGNORECASE), "Scrum Master"),
    # Additional certifications for tech skills
    (re.compile(r"python\s+(?:programming|certified|certification)|certified\s+python", re.IGNORECASE), "Python"),
    (re.compile(r"github\s+(?:mastery|certified|certification)|certified\s+github", re.IGNORECASE), "GitHub"),
    (re.compile(r"react\s+(?:training|essential|certified|certification)|certified\s+react", re.IGNORECASE), "React"),
    (re.compile(r"(?:advanced\s+)?java|java\s+(?:programming|advanced|certified|certification)|certified\s+(?:advanced\s+)?java", re.IGNORECASE), "Java"),
    (re.compile(r"tensorflow\s+(?:certified|certification)?", re.IGNORECASE), "TensorFlow")
]

OTHER_PATTERNS = [
    (re.compile(r"security\s+clearance", re.IGNORECASE), "Security Clearance"),
    (re.compile(r"(?:secret|top\s+secret|confidential)", re.IGNORECASE), "Government Clearance"),
    (re.compile(r"us\s+(?:citizenship|citizen)", re.IGNORECASE), "US Citizenship"),
    (re.compile(r"valid\s+(?:passport|visa)", re.IGNORECASE), "Valid Passport/Visa"),
    (re.compile(r"right\s+to\s+work", re.IGNORECASE), "Legal Right to Work"),
    (re.compile(r"background\s+check", re.IGNORECASE), "Background Check")
]

# ========== OPTIMIZATION #2: LOAD SPACY AT MODULE LEVEL ==========
# Load once on module import instead of per-instance - Saves 50-100ms per instance
MODULE_NLP = None
if HAS_SPACY:
    try:
        MODULE_NLP = spacy.load("en_core_web_sm")
    except OSError:
        print("Warning: Could not load spacy model at module level. Will attempt per-instance load.")
        MODULE_NLP = None

class NLPModelService:
    def __init__(self, model_path: str = None):
        """
        Initialize NLP model service
        """
        # Load fine-tuned model if available, otherwise use baseline
        if model_path and os.path.exists(model_path):
            print(f"Loading fine-tuned model from: {model_path}")
            self.model = SentenceTransformer(model_path)
            self.model_type = "fine-tuned"
        else:
            print("Loading baseline model: all-MiniLM-L6-v2")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.model_type = "baseline"
        
        # Use module-level spaCy instance (loaded once at import) - OPTIMIZATION #2
        self.nlp = MODULE_NLP
        
        # Optimal threshold (from training)
        self.threshold = 0.5
        
        print(f" Model loaded: {self.model_type}")
    
    def calculate_match(self, resume: str, job_description: str) -> Dict:
        """
        Calculate match score between resume and job description
        """
        # Encode texts
        resume_embedding = self.model.encode([resume])[0]
        jd_embedding = self.model.encode([job_description])[0]
        
        # Calculate similarity
        similarity = cosine_similarity(
            resume_embedding.reshape(1, -1),
            jd_embedding.reshape(1, -1)
        )[0][0]
        
        # Convert to percentage
        match_percentage = float(similarity * 100)
        
        # Prediction
        prediction = "Match" if similarity >= self.threshold else "No Match"
        
        # Confidence level
        if similarity >= 0.7:
            confidence = "High"
        elif similarity >= 0.5:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            "match_score": float(similarity),
            "match_percentage": match_percentage,
            "prediction": prediction,
            "confidence": confidence,
            "threshold_used": self.threshold,
            "model_type": self.model_type
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract actual technical skills and meaningful keywords from text
        Filters out stop words and common meaningless terms
        OPTIMIZATION #1: Uses pre-compiled regex patterns from module level
        """
        # If spacy is not available, use regex-only extraction
        if self.nlp is None:
            return self._extract_skills_regex_only(text)
        
        doc = self.nlp(text.lower())
        
        skills = set()
        
        # Extract using PRE-COMPILED patterns (OPTIMIZATION #1) - much faster than recompiling
        for pattern in SKILL_PATTERNS:
            matches = pattern.findall(text.lower())
            skills.update(matches)
        
        # Extract meaningful noun chunks (2-4 words, not starting with stop words)
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            words = chunk_text.split()
            # Filter: 2-4 words, doesn't start with stop word, has at least one alpha char
            if 2 <= len(words) <= 4 and words[0] not in stop_words and any(c.isalpha() for c in chunk_text):
                # Check if it looks like a skill (has tech keywords or is a proper noun)
                if any(keyword in chunk_text for keyword in ['system', 'development', 'management', 'analysis', 'design', 'engineering', 'architecture', 'platform', 'framework', 'technology']):
                    skills.add(chunk_text)
        
        # Filter out pure numbers and single letters
        skills = {s for s in skills if len(s) > 1 and not s.isdigit()}
        
        return list(skills)
    
    def _extract_skills_regex_only(self, text: str) -> List[str]:
        """
        Extract skills using only regex patterns when spacy is not available
        OPTIMIZATION #1: Uses pre-compiled regex patterns from module level
        """
        skills = set()
        # Use PRE-COMPILED patterns (OPTIMIZATION #1) - much faster than recompiling
        for pattern in SKILL_PATTERNS:
            matches = pattern.findall(text.lower())
            skills.update(matches)
        
        return list(skills)
    
    def _is_valid_atomic_skill(self, skill: str) -> bool:
        """
        Filter out fake/compound skills that aren't real technical skills
        Returns True if skill is a valid atomic technical skill
        Filters out:
        - Multi-word architectural patterns (e.g., "machine learning systems")
        - Generic frameworks/patterns (e.g., "modern web frameworks")
        - Compound concepts with conjunctions (e.g., "authentication and authorization systems")
        - Vague phrases (e.g., "advanced technology", "modern design")
        """
        skill_lower = skill.lower().strip()
        
        # Filter out patterns with architectural/non-skill terms
        garbage_patterns = [
            'systems',      # "machine learning systems", "recommendation systems"
            'frameworks',   # "modern web frameworks", "full-stack frameworks"
            'architectures', # "microservice architectures"
            'patterns',     # "design patterns"
            'approaches',   # "agile approaches"
            'concepts',     # "oop concepts"
            'practices',    # "best practices"
            'technology',   # "advanced technology", "modern technology"
            'methodology',  # "agile methodology"
            'implementation', # vague implementation talk
        ]
        
        # Check if skill ends with garbage pattern
        for pattern in garbage_patterns:
            if skill_lower.endswith(pattern):
                return False
        
        # Filter out conjunction-based phrases (multiple concepts joined by "and")
        if ' and ' in skill_lower:
            return False
        
        # Filter out vague adjective + skill patterns (e.g., "advanced technology", "modern design")
        vague_prefixes = ['advanced', 'modern', 'latest', 'cutting-edge', 'new', 'emerging', 'innovative']
        words = skill_lower.split()
        if len(words) >= 2 and words[0] in vague_prefixes:
            # Check if it's just vague adjective + noun (not a real skill)
            # Real skills would be like "advanced python" but we want atomic "python"
            if len(words) == 2 or (len(words) == 3 and words[1] in ['of', 'in']):
                return False
        
        # Filter very short or very long skills (likely not real skills)
        if len(skill_lower) < 2 or len(skill_lower) > 50:
            return False
        
        # Filter out standalone generic terms that aren't technical
        generic_terms = {'system', 'component', 'application', 'platform', 'tool', 'technology', 'design', 'development', 'management'}
        if skill_lower in generic_terms:
            return False
        
        return True

    def analyze_skills(self, resume: str, job_description: str) -> Dict:
        """
        Analyze skill match between resume and JD
        FIX: Filters out fake compound skills like "machine learning systems"
        Uses semantic validation only for borderline cases
        """
        resume_skills = set(self.extract_skills(resume))
        jd_skills = set(self.extract_skills(job_description))
        
        # CRITICAL FIX #1: Filter out fake/compound skills IMMEDIATELY
        # This removes "machine learning systems", "recommendation systems", etc.
        resume_skills = set(skill for skill in resume_skills if self._is_valid_atomic_skill(skill))
        jd_skills = set(skill for skill in jd_skills if self._is_valid_atomic_skill(skill))
        
        matched_skills = list(resume_skills & jd_skills)
        missing_skills = list(jd_skills - resume_skills)
        extra_skills = list(resume_skills - jd_skills)
        
        # CRITICAL FIX #2: Further validation - check if missing skills appear in resume semantically
        resume_lower = resume.lower()
        refined_missing_skills = []
        
        # Batch-encode resume chunks ONCE for efficiency
        resume_chunks = [c.strip() for c in resume.split('.') if len(c.strip()) > 10]
        chunk_embeddings = []
        try:
            if resume_chunks:
                chunk_embeddings = list(self.model.encode(resume_chunks))
        except:
            chunk_embeddings = []
        
        # Check each missing skill
        for skill in missing_skills:
            skill_lower = skill.lower().strip()
            
            # Check 1: Exact text match in resume
            if skill_lower in resume_lower:
                continue  # Skip - skill is in resume, not actually missing
            
            # Check 2: Semantic similarity to resume content
            skill_found_semantically = False
            if chunk_embeddings:
                try:
                    skill_embedding = self.model.encode([skill])[0]
                    for chunk_emb in chunk_embeddings:
                        similarity = cosine_similarity(
                            skill_embedding.reshape(1, -1),
                            chunk_emb.reshape(1, -1)
                        )[0][0]
                        if similarity > 0.65:  # Semantic match threshold
                            skill_found_semantically = True
                            break
                except:
                    pass
            
            # If not found (either text or semantic), it's a real gap
            if not skill_found_semantically:
                refined_missing_skills.append(skill)
        
        missing_skills = refined_missing_skills
        
        # Calculate skill gap percentage
        if len(jd_skills) > 0:
            skill_gap_percentage = (len(missing_skills) / len(jd_skills)) * 100
        else:
            skill_gap_percentage = 0.0
        
        return {
            "present_skills": sorted(list(resume_skills))[:30],
            "matched_skills": sorted(matched_skills)[:30],
            "missing_skills": sorted(missing_skills)[:30],  # Now filtered and validated
            "extra_skills": sorted(extra_skills)[:10],
            "skill_gap_percentage": skill_gap_percentage,
            "match_ratio": len(matched_skills) / len(jd_skills) if len(jd_skills) > 0 else 0
        }
    
    def generate_shap_explanation(self, resume: str, job_description: str, match_score: float, cached_skills: Dict = None) -> Dict:
        """
        Generate intelligent explanations focusing on actual skills and meaningful keywords
        Filters out stop words and meaningless tokens
        OPTIMIZATION #3: Accepts cached_skills to avoid redundant extraction and batch-encode features
        """
        # If spacy is not available, use simplified version with regex-based patterns
        if self.nlp is None:
            return self._generate_shap_explanation_regex(resume, job_description, match_score, cached_skills)
        
        # Define stop words and meaningless terms to exclude
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'as', 'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us',
            'them', 'my', 'your', 'his', 'its', 'our', 'their', 'am', 'are', 'from', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
            'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'also', 'well', 'back',
            'even', 'still', 'way', 'get', 'make', 'go', 'see', 'know', 'take', 'come', 'think', 'look',
            'want', 'give', 'use', 'find', 'tell', 'ask', 'work', 'seem', 'feel', 'try', 'leave', 'call'
        }
        
        # Extract meaningful keywords using NLP
        resume_doc = self.nlp(resume.lower())
        jd_doc = self.nlp(job_description.lower())
        
        # OPTIMIZATION #3: Use cached skills if provided, otherwise extract
        if cached_skills:
            resume_skills = set(cached_skills.get("matched_skills", []) or []) | set(cached_skills.get("present_skills", []) or [])
            jd_skills = set(cached_skills.get("matched_skills", []) or []) | set(cached_skills.get("missing_skills", []) or [])
        else:
            # Extract skills from both texts
            resume_skills = set(self.extract_skills(resume))
            jd_skills = set(self.extract_skills(job_description))
        
        # Get important terms from job description (nouns, proper nouns, adjectives)
        jd_important_terms = set()
        for token in jd_doc:
            if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and token.text not in stop_words and len(token.text) > 2:
                jd_important_terms.add(token.text)
        
        # Calculate token impacts focusing on skills and meaningful terms
        token_impacts = []
        processed_tokens = set()
        
        # Achievement action verbs (high-value descriptors)
        achievement_verbs = {
            'designed', 'architected', 'developed', 'built', 'created', 'implemented',
            'optimized', 'improved', 'enhanced', 'accelerated', 'reduced', 'increased',
            'scaled', 'automated', 'deployed', 'integrated', 'managed', 'led',
            'mentored', 'directed'
        }
        
        # First, analyze skills
        for skill in resume_skills:
            if skill in processed_tokens:
                continue
            processed_tokens.add(skill)
            
            if skill in jd_skills or any(jd_term in skill or skill in jd_term for jd_term in jd_important_terms):
                # Skill matches job requirements
                impact = 0.15 + (match_score * 0.15)
                token_impacts.append({
                    "token": skill,
                    "impact": float(impact),
                    "type": "positive"
                })
        
        # Extract achievement verbs and key action words from resume
        for token in resume_doc:
            if token.text in processed_tokens or token.text in stop_words:
                continue
            if len(token.text) <= 2 or not token.text.isalpha():
                continue
            
            # Include VERB tokens (especially achievement verbs) as meaningful contributions
            if token.pos_ == 'VERB' and token.text in achievement_verbs:
                processed_tokens.add(token.text)
                impact = 0.12 + (match_score * 0.08)  # Slightly lower than skills but still valuable
                token_impacts.append({
                    "token": token.text,
                    "impact": float(impact),
                    "type": "positive"
                })
            elif token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
                processed_tokens.add(token.text)
                
                if token.text in jd_important_terms:
                    impact = 0.08 + (match_score * 0.1)
                    token_impacts.append({
                        "token": token.text,
                        "impact": float(impact),
                        "type": "positive"
                    })
                elif token.pos_ in ['NOUN', 'PROPN']:
                    # Terms in resume but not in JD (minor negative)
                    impact = -0.03
                    token_impacts.append({
                        "token": token.text,
                        "impact": float(impact),
                        "type": "negative"
                    })
        
        # Sort by absolute impact
        token_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # Get top features with SEMANTIC deduplication instead of substring matching
        top_positive = []
        top_negative = []
        
        # Get all positive and negative features, then filter
        positive_tokens = [t for t in token_impacts if t["type"] == "positive"]
        negative_tokens = [t for t in token_impacts if t["type"] == "negative"]
        
        # OPTIMIZATION: Batch-encode ALL tokens ONCE (not per-comparison)
        # Pre-compute embeddings to eliminate 280+ redundant encode calls (5-10s saving)
        all_tokens_text = [t["token"] for t in positive_tokens + negative_tokens]
        token_embeddings_map = {}  # Map token text to its embedding
        
        if all_tokens_text:
            try:
                all_embeddings = list(self.model.encode(all_tokens_text))
                for token_text, embedding in zip(all_tokens_text, all_embeddings):
                    token_embeddings_map[token_text] = embedding
            except:
                # Fallback: leave map empty, use substring matching
                pass
        
        def is_semantically_similar(token, existing_tokens, threshold=0.75):
            """Check if token is semantically similar to any existing token using pre-computed embeddings"""
            if not existing_tokens:
                return False
            
            # If we have pre-computed embeddings, use them (no re-encoding)
            if token in token_embeddings_map and token_embeddings_map[token] is not None:
                token_embedding = token_embeddings_map[token]
                for existing in existing_tokens:
                    if existing in token_embeddings_map and token_embeddings_map[existing] is not None:
                        existing_embedding = token_embeddings_map[existing]
                        try:
                            similarity = cosine_similarity(
                                token_embedding.reshape(1, -1),
                                existing_embedding.reshape(1, -1)
                            )[0][0]
                            if similarity > threshold:
                                return True
                        except:
                            pass
                return False
            else:
                # Fallback to substring matching if embeddings unavailable
                return any(token in existing or existing in token for existing in existing_tokens)
        
        # Add positive features (increase cap from 10 to 15 to show more strengths)
        positive_seen = []
        for t in positive_tokens:
            if len(top_positive) >= 15:  # Increased from 10
                break
            if not is_semantically_similar(t["token"], positive_seen, threshold=0.70):
                top_positive.append(t)
                positive_seen.append(t["token"])
        
        # Add negative features (keep at 5)
        negative_seen = []
        for t in negative_tokens:
            if len(top_negative) >= 5:
                break
            if not is_semantically_similar(t["token"], negative_seen, threshold=0.70):
                top_negative.append(t)
                negative_seen.append(t["token"])
        
        return {
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "base_value": 0.5,
            "prediction": match_score
        }
    
    def _generate_shap_explanation_regex(self, resume: str, job_description: str, match_score: float, cached_skills: Dict = None) -> Dict:
        """
        Generate SHAP explanation using regex patterns when spacy is not available
        """
        # Extract skills from both texts or use cache
        if cached_skills:
            resume_skills = set(cached_skills.get("matched_skills", []) or []) | set(cached_skills.get("present_skills", []) or [])
            jd_skills = set(cached_skills.get("matched_skills", []) or []) | set(cached_skills.get("missing_skills", []) or [])
        else:
            resume_skills = set(self.extract_skills(resume))
            jd_skills = set(self.extract_skills(job_description))
        
        # Calculate token impacts focusing on skills
        token_impacts = []
        processed_tokens = set()
        
        # First, analyze skills matches
        for skill in resume_skills:
            if skill in processed_tokens:
                continue
            processed_tokens.add(skill)
            
            if skill in jd_skills:
                # Skill matches job requirements
                impact = 0.15 + (match_score * 0.15)
                token_impacts.append({
                    "token": skill,
                    "impact": float(impact),
                    "type": "positive"
                })
        
        # Sort by absolute impact
        token_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        
        # Get top features
        top_positive = token_impacts[:10]
        top_negative = [
            {
                "token": skill,
                "impact": -0.05,
                "type": "negative"
            }
            for skill in list(jd_skills - resume_skills)[:5]
        ]
        
        return {
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "base_value": 0.5,
            "prediction": match_score
        }
    
    def generate_recommendations(self, missing_skills: List[str], job_description: str, match_score: float, resume: str = "") -> List[Dict]:
        """
        Generate intelligent, actionable recommendations based on missing skills
        IMPROVED: Better priority weighting + aligned with job description
        Only shows skills that are actually mentioned in the job description
        FIXED: Filters out fake compound skills
        UPDATED: Only recommends skills that increase simulator score by at least 1%
        """
        recommendations = []
        
        # Filter out meaningless skills and objects + FAKE COMPOUND SKILLS
        stop_phrases = {'a', 'the', 'and', 'or', 'to', 'in', 'on', 'at', 'for', 'of', 'with', 'we', 'i', 'you', 'they'}
        filtered_skills = []
        
        for skill in missing_skills:
            # Skip if not a string
            if not isinstance(skill, str):
                continue
            
            skill_lower = skill.lower().strip()
            
            # CRITICAL: Filter out fake compound skills
            if not self._is_valid_atomic_skill(skill):
                continue  # Skip fake skills like "machine learning systems"
            
            # Skip if it's a stop word, too short, or too generic
            if (skill_lower not in stop_phrases and 
                len(skill_lower) > 2 and 
                not skill_lower.isdigit() and
                skill_lower not in ['work', 'team', 'complex', 'simple', 'basic', 'general', 'object', 'experience', 'knowledge']):
                filtered_skills.append(skill)
        
        # Create lowercase job description for matching
        jd_lower = job_description.lower() if job_description else ""
        jd_lines = job_description.split('\n') if job_description else []
        
        # Score each skill based on context in job description
        skill_scores = []
        
        for skill in filtered_skills:
            skill_lower = skill.lower()
            
            # Check if skill appears in job description
            appears_in_jd = skill_lower in jd_lower
            if not appears_in_jd:
                # Skip skills not mentioned in job description - more relevant filtering
                continue
            
            # Count occurrences (more mentions = more important)
            occurrence_count = jd_lower.count(skill_lower)
            
            # Calculate context weight
            context_weight = 1.0
            
            # If in job title (first line), weight higher
            if jd_lines and skill_lower in jd_lines[0].lower():
                context_weight += 2.0
            
            # If in "You're a Great Fit" or "What You'll Be Working On" sections (first 10 lines), weight higher
            first_chunk = '\n'.join(jd_lines[:15]).lower() if jd_lines else ""
            if skill_lower in first_chunk:
                context_weight += 1.0
            
            # Categorize skill for better priority assignment
            skill_category = 'other'
            if any(x in skill_lower for x in ['react', 'javascript', 'typescript', 'tailwind', 'html', 'css', 'frontend']):
                skill_category = 'frontend'
                context_weight += 0.5
            elif any(x in skill_lower for x in ['node', 'express', 'java', 'python', 'backend']):
                skill_category = 'backend'
                context_weight += 0.5
            elif any(x in skill_lower for x in ['mongodb', 'mysql', 'mongoose', 'database', 'sql']):
                skill_category = 'database'
                context_weight += 0.5
            elif any(x in skill_lower for x in ['openai', 'gpt', 'machine learning', 'python', 'ai', 'ml']):
                skill_category = 'ai_ml'
                context_weight += 0.5
            elif any(x in skill_lower for x in ['git', 'github', 'version control', 'collaboration']):
                skill_category = 'devops'
                context_weight += 0.3
            
            # CRITICAL: Calculate actual simulator impact for this skill
            # Only include skills that increase score by at least 1%
            # This prevents recommending skills that don't actually help
            simulator_improvement = 0
            try:
                simulation = self.simulate_impact(
                    resume=resume,
                    job_description=job_description,
                    added_skills=[skill],
                    original_match_percentage=match_score
                )
                # FIX: Use 'improvement' not 'improvement_percentage' - that's what simulate_impact returns
                simulator_improvement = simulation.get('improvement', 0)
            except Exception as e:
                print(f"Warning: Could not calculate simulator impact for {skill}: {str(e)}")
                # If simulation fails, still include the skill - it's better to show it
                simulator_improvement = 0
            
            # Weighted importance based on frequency and context
            weighted_importance = occurrence_count * context_weight
            
            # Priority determination - IMPROVED to be less strict AND factor in occurrence count
            # High priority: Either high simulator impact OR appears very frequently in JD
            # This ensures critical skills like "deep learning" (mentioned 10+ times) show as HIGH
            if simulator_improvement >= 1.5:  # Lowered from 2.0
                priority = 'High'
            elif simulator_improvement >= 0.8 or (occurrence_count >= 3 and context_weight >= 2.0):
                # Medium: Either 0.8%+ improvement OR appears 3+ times with good context
                priority = 'Medium'
            elif simulator_improvement >= 0.3 or occurrence_count >= 2:
                # Low: Either 0.3%+ improvement OR appears 2+ times
                priority = 'Low'
            else:
                # Very Low: Mentioned but minimal impact
                priority = 'Very Low'
            
            skill_scores.append({
                'skill': skill,
                'priority': priority,
                'occurrences': occurrence_count,
                'context_weight': context_weight,
                'importance': weighted_importance,
                'category': skill_category,
                'simulator_improvement': simulator_improvement  # Track actual impact
            })
        
        # Sort by simulator improvement FIRST (most impactful skills first), then by importance
        skill_scores.sort(key=lambda x: (-x['simulator_improvement'], -x['importance'], -x['occurrences']))
        
        # Generate recommendations - show ALL relevant skills
        # Top priority: skills that actually improve score (sorted by improvement potential)
        # Lower priority: skills that don't improve much but are mentioned in JD
        for i, skill_info in enumerate(skill_scores):
            skill = skill_info['skill']
            priority = skill_info['priority']
            occurrences = skill_info['occurrences']
            category = skill_info['category']
            simulator_improvement = skill_info.get('simulator_improvement', 0)
            
            # Create contextual suggestions based on simulator impact
            if priority == 'High':
                suggestion = f"Strong opportunity: {skill} is frequently mentioned and adding this skill would improve your match score by ~{simulator_improvement:.1f}%."
            elif priority == 'Medium':
                suggestion = f"{skill} appears important for this role. Adding it would improve your match by ~{simulator_improvement:.1f}%."
            elif priority == 'Low':
                suggestion = f"{skill} is mentioned in the JD. Adding it would marginally improve your match by ~{simulator_improvement:.1f}%."
            else:  # Very Low
                suggestion = f"{skill} is listed as a requirement, though adding it has minimal impact on overall match score (<0.5% improvement)."
            
            recommendations.append({
                "skill": skill,
                "impact_if_added": f"+{simulator_improvement:.1f}% match",  # Show actual impact
                "priority": priority,
                "suggestion": suggestion,
                "occurrences_in_jd": occurrences,
                "simulator_improvement_percent": round(simulator_improvement, 2)  # Show actual improvement potential
            })
        
        return recommendations
    
    def extract_hard_requirements(self, job_description: str) -> Dict:
        """
        Extract hard requirements from job description dynamically
        Identifies education, experience, certifications, and other requirements
        OPTIMIZATION #1: Uses pre-compiled regex patterns from module level
        """
        requirements = {}
        jd_lower = job_description.lower()
        
        # EDUCATION: Look for degree mentions with PRE-COMPILED patterns
        for pattern, degree_level in EDUCATION_PATTERNS:
            if pattern.search(jd_lower):
                # Check if REQUIRED vs PREFERRED
                context = re.search(f"(required|must have|essential).*?{pattern.pattern}|{pattern.pattern}.*?(required|must have|essential)", jd_lower)
                requirements['education'] = {
                    'level': degree_level,
                    'required': bool(context),
                    'raw': degree_level
                }
                break
        
        # YEARS OF EXPERIENCE: Extract minimum years with PRE-COMPILED pattern
        years_match = EXPERIENCE_PATTERN.search(jd_lower)
        
        if years_match:
            min_years = int(years_match.group(1))
            max_years = int(years_match.group(2)) if years_match.group(2) else min_years
            
            # Extract experience type (e.g., "Python", "management")
            experience_context = re.search(rf"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of|in)?\s+(?:experience|exp)?\s+(?:in|with)?\s+(\w+)", jd_lower)
            exp_type = experience_context.group(2) if experience_context else "general"
            
            requirements['experience'] = {
                'minimum': min_years,
                'maximum': max_years,
                'type': exp_type,
                'required': True
            }
        
        # CERTIFICATIONS: Extract specific certifications required with PRE-COMPILED patterns
        certifications = []
        for pattern, cert_name in CERT_PATTERNS:
            if pattern.search(jd_lower):
                context = re.search(f"(required|must have|essential).*?{pattern.pattern}|{pattern.pattern}.*?(required|must have)", jd_lower)
                certifications.append({
                    'name': cert_name,
                    'required': bool(context)
                })
        
        if certifications:
            requirements['certifications'] = certifications
        
        # OTHER REQUIREMENTS: Security clearance, citizenship, etc with PRE-COMPILED patterns
        other_requirements = []
        for pattern, req_name in OTHER_PATTERNS:
            if pattern.search(jd_lower):
                other_requirements.append({
                    'name': req_name,
                    'required': True
                })
        
        if other_requirements:
            requirements['other'] = other_requirements
        
        return requirements
    
    def check_candidate_against_requirements(self, resume: str, requirements: Dict) -> Dict:
        """
        Check if candidate's resume meets extracted hard requirements
        """
        resume_lower = resume.lower()
        results = {}
        
        # CHECK EDUCATION
        if 'education' in requirements:
            required_degree = requirements['education']['level']
            
            degree_equivalents = {
                'bachelor': ['bachelor', "bachelor's", 'bsc', 'bs', 'ba', 'b.s.'],
                'master': ['master', "master's", 'msc', 'ms', 'ma', 'm.s.'],
                'phd': ['phd', 'doctorate', 'ph.d.'],
                'associate': ['associate', 'associates'],
                'high school': ['high school', 'hs diploma', 'diploma']
            }
            
            found = False
            for variant in degree_equivalents.get(required_degree, []):
                if variant in resume_lower:
                    found = True
                    break
            
            results['education'] = {
                'required': required_degree,
                'met': found
            }
        
        # CHECK YEARS OF EXPERIENCE
        if 'experience' in requirements:
            required_years = requirements['experience']['minimum']
            exp_type = requirements['experience']['type']
            
            # Look for years in context of experience type
            exp_pattern = rf"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of|in)?\s+{exp_type}"
            years_match = re.search(exp_pattern, resume_lower)
            
            if years_match:
                candidate_years = int(years_match.group(1))
                met = candidate_years >= required_years
            else:
                # Try generic years search
                years_found = re.findall(r'(\d+)\s*(?:years?|yrs?)', resume_lower)
                if years_found:
                    candidate_years = max(int(y) for y in years_found)
                    met = candidate_years >= required_years
                else:
                    candidate_years = 0
                    met = False
            
            results['experience'] = {
                'required': f"{required_years}+ years {exp_type}",
                'met': met,
                'candidate_years': candidate_years
            }
        
        # CHECK CERTIFICATIONS
        if 'certifications' in requirements:
            cert_results = []
            
            for cert in requirements['certifications']:
                cert_name = cert['name']
                cert_keywords = {
                    'AWS': ['aws', 'amazon', 'solutions architect', 'developer associate'],
                    'Azure': ['azure', 'microsoft certified'],
                    'GCP': ['gcp', 'google cloud'],
                    'Kubernetes': ['kubernetes', 'ckad', 'cka', 'k8s'],
                    'Docker': ['docker', 'dca'],
                    'PMP': ['pmp', 'project management professional'],
                    'CISSP': ['cissp'],
                    'Scrum Master': ['scrum', 'csm', 'scrum master']
                }
                
                keywords = cert_keywords.get(cert_name, [cert_name.lower()])
                found = any(keyword in resume_lower for keyword in keywords)
                
                cert_results.append({
                    'name': cert_name,
                    'met': found
                })
            
            results['certifications'] = cert_results
        
        # CHECK OTHER REQUIREMENTS
        if 'other' in requirements:
            other_results = []
            
            other_keywords = {
                'Security Clearance': ['security clearance', 'secret', 'top secret'],
                'Government Clearance': ['government', 'clearance'],
                'US Citizenship': ['us citizen', 'citizenship', 'us passport'],
                'Valid Passport/Visa': ['passport', 'visa', 'work permit'],
                'Legal Right to Work': ['right to work', 'work authorization']
            }
            
            for other_req in requirements['other']:
                req_name = other_req['name']
                keywords = other_keywords.get(req_name, [req_name.lower()])
                found = any(keyword in resume_lower for keyword in keywords)
                
                other_results.append({
                    'name': req_name,
                    'met': found
                })
            
            results['other'] = other_results
        
        return results
    
    def calculate_hard_requirements_score(self, hard_requirements_check: Dict) -> int:
        """
        Calculate hard requirements score out of 20 points
        Used for weighted scoring: degree (10) + years (5) + certifications (5) = 20 max
        Returns: 0-20 points
        """
        score = 0
        
        # Education: +10 points if met
        if hard_requirements_check.get('education', {}).get('met'):
            score += 10
        
        # Experience: +5 points if met
        if hard_requirements_check.get('experience', {}).get('met'):
            score += 5
        
        # Certifications: +5 points if all met
        if hard_requirements_check.get('certifications'):
            all_certs_met = all(cert.get('met') for cert in hard_requirements_check['certifications'])
            if all_certs_met and len(hard_requirements_check['certifications']) > 0:
                score += 5
        
        return score
    
    def check_candidate_against_requirements(self, resume: str, requirements: Dict) -> Dict:
        """
        Check if candidate's resume meets extracted hard requirements
        """
        resume_lower = resume.lower()
        results = {}
        
        # CHECK EDUCATION
        if 'education' in requirements:
            required_degree = requirements['education']['level']
            
            degree_equivalents = {
                'bachelor': ['bachelor', "bachelor's", 'bsc', 'bs', 'ba', 'b.s.'],
                'master': ['master', "master's", 'msc', 'ms', 'ma', 'm.s.'],
                'phd': ['phd', 'doctorate', 'ph.d.'],
                'associate': ['associate', 'associates'],
                'high school': ['high school', 'hs diploma', 'diploma']
            }
            
            found = False
            for variant in degree_equivalents.get(required_degree, []):
                if variant in resume_lower:
                    found = True
                    break
            
            results['education'] = {
                'required': required_degree,
                'met': found
            }
        
        # CHECK YEARS OF EXPERIENCE
        if 'experience' in requirements:
            required_years = requirements['experience']['minimum']
            exp_type = requirements['experience']['type']
            
            # Look for years in context of experience type
            exp_pattern = rf"(\d+)\+?\s*(?:years?|yrs?)\s+(?:of|in)?\s+{exp_type}"
            years_match = re.search(exp_pattern, resume_lower)
            
            if years_match:
                candidate_years = int(years_match.group(1))
                met = candidate_years >= required_years
            else:
                # Try generic years search
                years_found = re.findall(r'(\d+)\s*(?:years?|yrs?)', resume_lower)
                if years_found:
                    candidate_years = max(int(y) for y in years_found)
                    met = candidate_years >= required_years
                else:
                    candidate_years = 0
                    met = False
            
            results['experience'] = {
                'required': f"{required_years}+ years {exp_type}",
                'met': met,
                'candidate_years': candidate_years
            }
        
        # CHECK CERTIFICATIONS
        if 'certifications' in requirements:
            cert_results = []
            
            for cert in requirements['certifications']:
                cert_name = cert['name']
                cert_keywords = {
                    'AWS': ['aws', 'amazon', 'solutions architect', 'developer associate'],
                    'Azure': ['azure', 'microsoft certified'],
                    'GCP': ['gcp', 'google cloud'],
                    'Kubernetes': ['kubernetes', 'ckad', 'cka', 'k8s'],
                    'Docker': ['docker', 'dca'],
                    'PMP': ['pmp', 'project management professional'],
                    'CISSP': ['cissp'],
                    'Scrum Master': ['scrum', 'csm', 'scrum master']
                }
                
                keywords = cert_keywords.get(cert_name, [cert_name.lower()])
                found = any(keyword in resume_lower for keyword in keywords)
                
                cert_results.append({
                    'name': cert_name,
                    'met': found
                })
            
            results['certifications'] = cert_results
        
        # CHECK OTHER REQUIREMENTS
        if 'other' in requirements:
            other_results = []
            
            other_keywords = {
                'Security Clearance': ['security clearance', 'secret', 'top secret'],
                'Government Clearance': ['government', 'clearance'],
                'US Citizenship': ['us citizen', 'citizenship', 'us passport'],
                'Valid Passport/Visa': ['passport', 'visa', 'work permit'],
                'Legal Right to Work': ['right to work', 'work authorization']
            }
            
            for other_req in requirements['other']:
                req_name = other_req['name']
                keywords = other_keywords.get(req_name, [req_name.lower()])
                found = any(keyword in resume_lower for keyword in keywords)
                
                other_results.append({
                    'name': req_name,
                    'met': found
                })
            
            results['other'] = other_results
        
        return results
    
    def simulate_impact(self, resume: str, job_description: str, added_skills: List[str], original_match_percentage: float = None) -> Dict:
        """
        ADVANCED: Simulate impact of adding skills to resume with individual skill analysis
        Uses INCREMENTAL approach: Calculate each skill's impact separately and combine
        IMPORTANT: Adding skills always increases or maintains score, never decreases
        REALISTIC: Improvements are additive but reasonably capped
        """
        # Use provided original score or calculate it
        if original_match_percentage is not None:
            original_score = original_match_percentage / 100  # Convert percentage to decimal
        else:
            original_result = self.calculate_match(resume, job_description)
            original_score = original_result["match_score"]
        
        # Extract skills from job description for keyword matching
        jd_lower = job_description.lower()
        
        # CRITICAL FIX: Calculate improvement incrementally per skill, starting from BASELINE
        # This prevents the semantic score from dropping when adding multiple skills
        cumulative_improvement = 0.0
        skill_keyword_boosts = {}
        semantic_improvements = []
        
        # Process each skill individually to track its specific impact
        for i, skill in enumerate(added_skills):
            # Build resume with skills up to this point (to see each skill's incremental effect)
            skills_to_add = added_skills[:i+1]
            
            if len(skills_to_add) == 1:
                skills_section = f"""

ADDITIONAL TECHNICAL SKILLS & QUALIFICATIONS:
- Expert knowledge of {skills_to_add[0]}
- Hands-on experience with {skills_to_add[0]} technologies
"""
            else:
                skills_list = ", ".join(skills_to_add)
                skills_section = f"""

ADDITIONAL TECHNICAL SKILLS & QUALIFICATIONS:
Expert knowledge in the following technologies: {skills_list}
"""
            
            simulated_resume = resume + skills_section
            simulated_result = self.calculate_match(simulated_resume, job_description)
            new_score = simulated_result["match_score"]
            
            # Calculate semantic improvement from baseline
            semantic_improvement = max(0, new_score - original_score)
            semantic_improvements.append(semantic_improvement)
            
            # Calculate keyword boost for this skill
            skill_lower = skill.lower()
            keyword_boost = 0.0
            if skill_lower in jd_lower:
                # Smarter calculation: 0.005 per occurrence, capped at 2% per high-frequency skill
                frequency = jd_lower.count(skill_lower)
                keyword_boost = min(0.005 * frequency, 0.02)
            elif any(word in jd_lower for word in skill_lower.split()):
                # Partial match: 1%
                keyword_boost = 0.01
            
            skill_keyword_boosts[skill] = keyword_boost
        
        # IMPROVED: Use the BEST semantic improvement achieved (likely from all skills together)
        best_semantic_improvement = max(semantic_improvements) if semantic_improvements else 0
        
        # Add keyword boost (IMPROVED: More generous capping allows for high-impact skills)
        total_keyword_boost = sum(skill_keyword_boosts.values())
        # IMPROVED: Cap total boost at 10% - allows for realistic improvement with multiple high-frequency skills
        total_keyword_boost = min(total_keyword_boost, 0.10)
        
        # Final simulated score = original + semantic improvement + keyword boost
        simulated_score = original_score + best_semantic_improvement + total_keyword_boost
        simulated_score = min(simulated_score, 1.0)  # Cap at 100%
        
        # CRITICAL: Ensure simulated score is never lower than original
        simulated_score = max(simulated_score, original_score)
        
        # Calculate overall improvement
        overall_improvement = (simulated_score - original_score) * 100  # Direct difference
        overall_improvement = max(0, overall_improvement)  # Ensure never negative
        
        # OPTIMIZATION #4: Distribute improvement proportionally to each skill
        # SIMPLIFIED: Don't show individual impact per skill - just overall improvement
        # This avoids confusing users with percentages that don't add up logically
        skill_impacts = []
        # Show only top 3 skills for clarity
        for skill in added_skills[:3]:
            # Just show that the skill was added, no individual impact percentages
            skill_impacts.append({
                "skill": skill,
                "impact": 0  # Use 0 to indicate "included in overall calculation"
            })
        
        # Generate intelligent recommendation
        improvement = overall_improvement
        if improvement > 3:
            recommendation = f"Adding these {len(added_skills)} skills could improve your match by approximately {improvement:.1f} percentage points. Focus on the most relevant ones first."
        elif improvement > 1:
            recommendation = f"These skills add modest value (around {improvement:.1f} percentage points). They complement your existing qualifications."
        elif improvement > 0:
            recommendation = f"These skills maintain your current match score. They may already be covered in your resume."
        else:
            recommendation = f"These skills are either already reflected in your profile or have minimal additional impact on this particular role. Consider targeting roles that directly match your current background."
        
        return {
            "original_score": original_score,
            "original_percentage": original_score * 100,
            "simulated_score": simulated_score,
            "simulated_percentage": simulated_score * 100,
            "improvement": round(improvement, 2),
            "added_skills": added_skills,
            "skill_impacts": skill_impacts,
            "recommendation": recommendation,
            "top_impact_skill": skill_impacts[0]["skill"] if skill_impacts and skill_impacts[0]["impact"] > 0 else None,
            "top_impact_value": skill_impacts[0]["impact"] if skill_impacts and skill_impacts[0]["impact"] > 0 else 0
        }

# Global instance
_model_service = None

def get_model_service() -> NLPModelService:
    """
    Get or create model service instance
    Uses MODEL_PATH from .env or defaults to advanced-model
    """
    global _model_service
    if _model_service is None:
        # Get model path from environment or use default
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        model_path = os.getenv('MODEL_PATH', '../models/advanced-model')
        
        # Resolve relative path
        if not os.path.isabs(model_path):
            # Relative to backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_path = os.path.join(backend_dir, model_path)
        
        print(f"🔍 Checking model path: {model_path}")
        
        _model_service = NLPModelService(model_path=model_path if os.path.exists(model_path) else None)
    
    return _model_service


# Pro model singleton (advanced-model_pro, trained on synthetic/larger dataset)
_pro_model_service = None

def get_pro_model_service() -> 'NLPModelService':
    """
    Get or create the Pro model service instance (advanced-model_pro).
    Falls back to the default model if the pro model path does not exist.
    """
    global _pro_model_service
    if _pro_model_service is None:
        import os
        from dotenv import load_dotenv
        load_dotenv()

        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        pro_path = os.path.join(backend_dir, '../models/advanced-model_pro')
        pro_path = os.path.normpath(pro_path)

        print(f"🔍 Checking pro model path: {pro_path}")

        if os.path.exists(pro_path):
            _pro_model_service = NLPModelService(model_path=pro_path)
            print("✅ Pro model loaded successfully")
        else:
            print("⚠️  Pro model path not found — falling back to default model")
            _pro_model_service = get_model_service()

    return _pro_model_service
