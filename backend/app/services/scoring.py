"""
AI Scoring Service - The Editor Engine

Implements the SPJ-based scoring rubric:
- Category A: Discipline of Verification (40 pts)
- Category B: Neutrality & Tone (30 pts)
- Category C: Fairness & Consistency (20 pts)

Starting score: 100
Redraft triggered if score < 70
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from openai import AsyncOpenAI

from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)


# Loaded language terms to detect
LOADED_TERMS = [
    "blasts", "slams", "destroys", "disastrous", "shocking", "bombshell",
    "scheme", "crisis", "explosive", "outrage", "rages", "fiery", "scathing",
    "surge", "surged", "flood", "flooded", "invasion", "invaded", "radical",
    "extremist", "controversial", "stunning", "unprecedented", "chaos",
    "chaotic", "slammed", "attacked", "ripped", "torched", "eviscerated",
    "shredded", "crushed", "demolished", "annihilated", "obliterated"
]


@dataclass
class Violation:
    type: str
    category: str
    description: str
    deduction: int
    instances: List[str]


@dataclass
class ScoringResult:
    initial_score: int
    final_score: int
    verification_score: int
    neutrality_score: int
    fairness_score: int
    violations: List[Violation]
    needs_redraft: bool
    processing_time_ms: int


SCORING_SYSTEM_PROMPT = """You are a strict Academic Journalism Professor trained on the SPJ Code of Ethics and Kovach & Rosenstiel's "Elements of Journalism."

Your task is to analyze news articles for violations of professional journalism standards. You must be objective and thorough.

IMPORTANT RULES:
1. Do NOT flag content inside direct quotes as loaded language (speakers can be emotional)
2. Wire services (AP, Reuters) are the "ground truth" - compare claims against them
3. Consider context - some strong words may be appropriate for the story
4. Be specific about each violation with exact text examples

SCORING RUBRIC:

CATEGORY A: DISCIPLINE OF VERIFICATION (Max 40 points deduction)
- Single-Source Reporting: -15 pts if story relies on one source without corroboration
- Unchallenged Official Narrative: -10 pts if repeating press releases without second source
- Unverified Statistics: -10 pts if citing numbers from biased entities without verification
- Anonymous Sourcing Abuse: -5 pts if using "Officials say" without explaining why anonymity granted

CATEGORY B: NEUTRALITY & TONE (Max 30 points deduction)
- Loaded Language: -2 pts per word (max -12) for emotive adjectives/adverbs outside quotes
- Straw Man Arguments: -10 pts for misrepresenting opposing views
- Opinion as News: -20 pts for subjective prescriptions ("The President should...")

CATEGORY C: FAIRNESS & CONSISTENCY (Max 20 points deduction)
- Lack of Right of Reply: -10 pts for negative claims without seeking comment
- Headline Bait: -10 pts if headline implies conclusion body doesn't support

THRESHOLDS:
- 90+: Professional Standard
- 70-89: Acceptable with concerns
- <70: Yellow Journalism (Triggers Redraft)

Respond ONLY in valid JSON format."""


async def analyze_article(
    headline: str,
    body: str,
    outlet_name: str,
    historical_context: Optional[str] = None
) -> ScoringResult:
    """
    Analyze an article and return scoring results.
    """
    start_time = time.time()
    
    # Step 1: Quick loaded language scan (rule-based for speed)
    loaded_language_violations = detect_loaded_language(headline, body)
    
    # Step 2: AI-powered deep analysis
    ai_violations = await run_ai_analysis(headline, body, outlet_name, historical_context)
    
    # Step 3: Combine and calculate final score
    all_violations = loaded_language_violations + ai_violations
    
    # Calculate category scores
    verification_deductions = sum(
        v.deduction for v in all_violations if v.category == "verification"
    )
    neutrality_deductions = sum(
        v.deduction for v in all_violations if v.category == "neutrality"
    )
    fairness_deductions = sum(
        v.deduction for v in all_violations if v.category == "fairness"
    )
    
    # Cap deductions per category
    verification_score = max(0, 40 - verification_deductions)
    neutrality_score = max(0, 30 - neutrality_deductions)
    fairness_score = max(0, 20 - fairness_deductions)
    
    # 10 points baseline for structure/grammar (not scored)
    final_score = 10 + verification_score + neutrality_score + fairness_score
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return ScoringResult(
        initial_score=100,
        final_score=final_score,
        verification_score=verification_score,
        neutrality_score=neutrality_score,
        fairness_score=fairness_score,
        violations=all_violations,
        needs_redraft=final_score < 70,
        processing_time_ms=processing_time
    )


def detect_loaded_language(headline: str, body: str) -> List[Violation]:
    """
    Rule-based detection of loaded language.
    Fast first pass before AI analysis.
    """
    violations = []
    found_terms = []
    
    # Combine text (lowercase for matching)
    text = f"{headline} {body}".lower()
    
    # Simple quote detection - remove quoted content
    # This is a simplification; AI does more nuanced detection
    import re
    text_no_quotes = re.sub(r'"[^"]*"', '', text)
    text_no_quotes = re.sub(r"'[^']*'", '', text_no_quotes)
    
    for term in LOADED_TERMS:
        if term.lower() in text_no_quotes:
            found_terms.append(term)
    
    if found_terms:
        # Cap at 6 terms (-12 points max for loaded language)
        capped_terms = found_terms[:6]
        deduction = len(capped_terms) * 2
        
        violations.append(Violation(
            type="Loaded Language",
            category="neutrality",
            description=f"Emotive language detected outside of quotes",
            deduction=deduction,
            instances=capped_terms
        ))
    
    return violations


async def run_ai_analysis(
    headline: str,
    body: str,
    outlet_name: str,
    historical_context: Optional[str] = None
) -> List[Violation]:
    """
    Run GPT-4 analysis for deeper journalism violations.
    """
    context_section = ""
    if historical_context:
        context_section = f"\n\nHISTORICAL CONTEXT (how this outlet covered similar topics):\n{historical_context}"
    
    user_prompt = f"""Analyze this article from {outlet_name}:

HEADLINE: {headline}

BODY:
{body}
{context_section}

Identify all journalism violations. Return JSON in this exact format:
{{
    "violations": [
        {{
            "type": "Single-Source Reporting" | "Unchallenged Official Narrative" | "Unverified Statistics" | "Anonymous Sourcing Abuse" | "Straw Man Arguments" | "Opinion as News" | "Lack of Right of Reply" | "Headline Bait",
            "category": "verification" | "neutrality" | "fairness",
            "description": "Specific explanation of the violation",
            "deduction": <number>,
            "instances": ["exact text examples from the article"]
        }}
    ]
}}

If no violations found, return {{"violations": []}}"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": SCORING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=2000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        violations = []
        for v in result.get("violations", []):
            violations.append(Violation(
                type=v.get("type", "Unknown"),
                category=v.get("category", "neutrality"),
                description=v.get("description", ""),
                deduction=v.get("deduction", 0),
                instances=v.get("instances", [])
            ))
        
        return violations
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        return []


def violations_to_json(violations: List[Violation]) -> dict:
    """Convert violations list to JSON-serializable dict"""
    return {
        "violations": [
            {
                "type": v.type,
                "category": v.category,
                "description": v.description,
                "deduction": v.deduction,
                "instances": v.instances
            }
            for v in violations
        ]
    }
