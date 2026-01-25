"""
AI Redrafting Service - The Redraft Room

Rewrites biased articles to be neutral, maintaining facts.
Triggered when article score < 70.
"""
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from openai import AsyncOpenAI
import difflib

from app.config import get_settings
from app.services.scoring import Violation

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)


@dataclass
class DiffSegment:
    type: str  # 'unchanged', 'removed', 'added'
    text: str


@dataclass
class RedraftResult:
    original_headline: str
    redraft_headline: str
    original_body: str
    redraft_body: str
    headline_diff: List[DiffSegment]
    body_diff: List[DiffSegment]
    changes_made: List[str]


REDRAFT_SYSTEM_PROMPT = """You are an AP Stylebook editor. Your task is to rewrite biased news articles to be neutral and factual.

RULES:
1. Preserve ALL facts and quotes exactly as written
2. Remove loaded/emotive language (replace with neutral alternatives)
3. Do NOT add your own opinions or analysis
4. Keep quotes exactly as stated (they represent what someone said)
5. Maintain the same structure and length approximately
6. Use AP Style guidelines for word choices

SPECIFIC CHANGES TO MAKE:
- "Blasts" → "Criticizes" or "Responds to"
- "Slams" → "Criticizes"
- "Scheme" → "Plan" or "Policy"
- "Disastrous" → (remove or use specific factual description)
- "Fiery" → "Strongly worded"
- "Rages" → "Said"
- "Flood" → "Increase" (unless literally about water)
- "Invasion" → (remove unless military context)
- "Crisis" → (use specific factual description)
- "Shocking" → (remove)
- "Bombshell" → "Report" or "Announcement"

You MUST return valid JSON only."""


async def generate_redraft(
    headline: str,
    body: str,
    violations: List[Violation]
) -> RedraftResult:
    """
    Generate a fair redraft of a biased article.
    """
    violations_summary = "\n".join([
        f"- {v.type}: {v.description} (instances: {', '.join(v.instances[:3])})"
        for v in violations
    ])
    
    user_prompt = f"""Rewrite this article to be neutral and factual.

ORIGINAL HEADLINE:
{headline}

ORIGINAL BODY:
{body}

VIOLATIONS TO FIX:
{violations_summary}

Return JSON in this exact format:
{{
    "redraft_headline": "The neutral headline",
    "redraft_body": "The neutral body text",
    "changes_made": ["List of specific changes you made"]
}}"""

    try:
        response = await client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": REDRAFT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=3000
        )
        
        result = json.loads(response.choices[0].message.content)
        
        redraft_headline = result.get("redraft_headline", headline)
        redraft_body = result.get("redraft_body", body)
        changes_made = result.get("changes_made", [])
        
        # Generate diffs
        headline_diff = generate_word_diff(headline, redraft_headline)
        body_diff = generate_word_diff(body, redraft_body)
        
        return RedraftResult(
            original_headline=headline,
            redraft_headline=redraft_headline,
            original_body=body,
            redraft_body=redraft_body,
            headline_diff=headline_diff,
            body_diff=body_diff,
            changes_made=changes_made
        )
        
    except Exception as e:
        print(f"Redraft error: {e}")
        # Return original if redraft fails
        return RedraftResult(
            original_headline=headline,
            redraft_headline=headline,
            original_body=body,
            redraft_body=body,
            headline_diff=[DiffSegment(type="unchanged", text=headline)],
            body_diff=[DiffSegment(type="unchanged", text=body)],
            changes_made=[]
        )


def generate_word_diff(original: str, redraft: str) -> List[DiffSegment]:
    """
    Generate word-level diff between original and redraft.
    Returns segments marked as unchanged, removed, or added.
    """
    # Split into words while preserving whitespace
    import re
    
    def tokenize(text: str) -> List[str]:
        return re.findall(r'\S+|\s+', text)
    
    original_tokens = tokenize(original)
    redraft_tokens = tokenize(redraft)
    
    # Use difflib to get opcodes
    matcher = difflib.SequenceMatcher(None, original_tokens, redraft_tokens)
    
    segments = []
    
    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == 'equal':
            text = ''.join(original_tokens[i1:i2])
            if text.strip():
                segments.append(DiffSegment(type="unchanged", text=text))
        elif opcode == 'replace':
            removed_text = ''.join(original_tokens[i1:i2])
            added_text = ''.join(redraft_tokens[j1:j2])
            if removed_text.strip():
                segments.append(DiffSegment(type="removed", text=removed_text))
            if added_text.strip():
                segments.append(DiffSegment(type="added", text=added_text))
        elif opcode == 'delete':
            text = ''.join(original_tokens[i1:i2])
            if text.strip():
                segments.append(DiffSegment(type="removed", text=text))
        elif opcode == 'insert':
            text = ''.join(redraft_tokens[j1:j2])
            if text.strip():
                segments.append(DiffSegment(type="added", text=text))
    
    # Merge adjacent segments of the same type
    merged = []
    for segment in segments:
        if merged and merged[-1].type == segment.type:
            merged[-1] = DiffSegment(
                type=segment.type,
                text=merged[-1].text + segment.text
            )
        else:
            merged.append(segment)
    
    return merged


def redraft_to_json(result: RedraftResult) -> dict:
    """Convert RedraftResult to JSON-serializable dict"""
    return {
        "headline": {
            "segments": [
                {"type": s.type, "text": s.text}
                for s in result.headline_diff
            ]
        },
        "body": {
            "segments": [
                {"type": s.type, "text": s.text}
                for s in result.body_diff
            ]
        },
        "changes_made": result.changes_made
    }
