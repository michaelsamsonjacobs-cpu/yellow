"""
Topic Taxonomy Configuration

Defines the specific topic categories and priority keywords
that Yellow tracks for news integrity analysis.
"""

# ============================================================
# TOPIC CATEGORIES - Ordered by bias detection priority
# ============================================================

TOPIC_CATEGORIES = {
    # --------------------------------------------------------
    # TIER 1: HIGHEST BIAS RISK (Political & Contested)
    # --------------------------------------------------------
    "elections": {
        "priority": 1,
        "keywords": [
            "election", "voting", "ballot", "polls", "campaign",
            "primary", "caucus", "swing state", "electoral college",
            "voter fraud", "mail-in voting", "election integrity"
        ],
        "bias_indicators": ["rigged", "stolen", "landslide", "mandate"]
    },
    
    "legislation": {
        "priority": 1,
        "keywords": [
            "bill", "congress", "senate", "house", "legislation",
            "filibuster", "veto", "executive order", "amendment",
            "bipartisan", "partisan", "gridlock"
        ],
        "bias_indicators": ["radical", "extreme", "common-sense", "slam"]
    },
    
    "presidential_actions": {
        "priority": 1,
        "keywords": [
            "president", "white house", "oval office", "executive action",
            "administration", "cabinet", "press secretary", "state of the union"
        ],
        "bias_indicators": ["regime", "dictator", "historic", "unprecedented"]
    },
    
    "supreme_court": {
        "priority": 1,
        "keywords": [
            "supreme court", "scotus", "justice", "ruling", "opinion",
            "constitutional", "overturn", "precedent", "dissent"
        ],
        "bias_indicators": ["activist", "partisan", "packed", "stolen seat"]
    },
    
    # --------------------------------------------------------
    # TIER 2: HIGH BIAS RISK (Socially Divisive)
    # --------------------------------------------------------
    "immigration": {
        "priority": 2,
        "keywords": [
            "immigration", "border", "migrant", "asylum", "deportation",
            "sanctuary", "ice", "daca", "dreamer", "visa", "refugee"
        ],
        "bias_indicators": ["invasion", "flood", "crisis", "open borders", "illegal alien"]
    },
    
    "gun_policy": {
        "priority": 2,
        "keywords": [
            "gun", "firearm", "second amendment", "nra", "shooting",
            "mass shooting", "gun control", "gun rights", "ar-15"
        ],
        "bias_indicators": ["gun grab", "assault weapon", "common-sense", "slaughter"]
    },
    
    "abortion_reproductive": {
        "priority": 2,
        "keywords": [
            "abortion", "roe", "dobbs", "reproductive rights", "pro-life",
            "pro-choice", "planned parenthood", "fetal", "trimester"
        ],
        "bias_indicators": ["baby killer", "forced birth", "murder", "healthcare"]
    },
    
    "race_civil_rights": {
        "priority": 2,
        "keywords": [
            "civil rights", "racism", "discrimination", "blm", "police brutality",
            "systemic racism", "diversity", "equity", "inclusion", "dei", "crt"
        ],
        "bias_indicators": ["woke", "cancel culture", "white supremacy", "reverse racism"]
    },
    
    "lgbtq": {
        "priority": 2,
        "keywords": [
            "lgbtq", "transgender", "gay rights", "same-sex", "gender identity",
            "drag", "pride", "conversion therapy", "bathroom bill"
        ],
        "bias_indicators": ["groomer", "agenda", "lifestyle", "indoctrination"]
    },
    
    # --------------------------------------------------------
    # TIER 3: MEDIUM BIAS RISK (Economic & Policy)
    # --------------------------------------------------------
    "economy_inflation": {
        "priority": 3,
        "keywords": [
            "economy", "inflation", "recession", "gdp", "unemployment",
            "jobs report", "federal reserve", "interest rates", "stock market"
        ],
        "bias_indicators": ["bidenomics", "trumponomics", "disaster", "booming"]
    },
    
    "healthcare": {
        "priority": 3,
        "keywords": [
            "healthcare", "obamacare", "medicare", "medicaid", "insurance",
            "prescription drugs", "hospital", "public option", "single payer"
        ],
        "bias_indicators": ["socialist", "death panel", "government takeover"]
    },
    
    "climate_environment": {
        "priority": 3,
        "keywords": [
            "climate change", "global warming", "emissions", "green new deal",
            "renewable", "fossil fuel", "epa", "carbon", "paris agreement"
        ],
        "bias_indicators": ["hoax", "alarmist", "denier", "existential threat"]
    },
    
    "education": {
        "priority": 3,
        "keywords": [
            "education", "school", "teacher", "curriculum", "book ban",
            "school board", "charter school", "voucher", "student loan"
        ],
        "bias_indicators": ["indoctrination", "grooming", "parental rights", "censorship"]
    },
    
    # --------------------------------------------------------
    # TIER 4: INTERNATIONAL (Narrative Divergence)
    # --------------------------------------------------------
    "china_relations": {
        "priority": 4,
        "keywords": [
            "china", "beijing", "xi jinping", "taiwan", "south china sea",
            "tariffs", "trade war", "tiktok", "spy balloon", "uyghur"
        ],
        "bias_indicators": ["communist", "regime", "threat", "partner"]
    },
    
    "russia_ukraine": {
        "priority": 4,
        "keywords": [
            "russia", "ukraine", "putin", "zelensky", "nato", "crimea",
            "invasion", "sanctions", "military aid", "wagner"
        ],
        "bias_indicators": ["puppet", "nazi", "provocation", "unprovoked"]
    },
    
    "israel_palestine": {
        "priority": 4,
        "keywords": [
            "israel", "palestine", "gaza", "hamas", "netanyahu",
            "west bank", "settler", "ceasefire", "idf", "hostage"
        ],
        "bias_indicators": ["genocide", "terrorist", "apartheid", "resistance"]
    },
    
    # --------------------------------------------------------
    # TIER 5: BREAKING NEWS (Verification Critical)
    # --------------------------------------------------------
    "mass_casualty": {
        "priority": 5,
        "keywords": [
            "shooting", "attack", "explosion", "casualties", "victims",
            "breaking", "developing", "active shooter", "terror"
        ],
        "bias_indicators": ["terrorist", "lone wolf", "mental illness", "false flag"]
    },
    
    "natural_disaster": {
        "priority": 5,
        "keywords": [
            "hurricane", "tornado", "earthquake", "wildfire", "flood",
            "evacuation", "fema", "emergency", "death toll"
        ],
        "bias_indicators": ["climate", "mismanaged", "abandoned"]
    },
}


# ============================================================
# OUTLET PRIORITY CONFIGURATION
# ============================================================

OUTLET_TIERS = {
    "tier_1_critical": {
        "description": "Highest reach, must-track for comprehensive coverage",
        "outlets": [
            {"domain": "nytimes.com", "lean": "left", "monthly_visits": 500_000_000},
            {"domain": "foxnews.com", "lean": "right", "monthly_visits": 450_000_000},
            {"domain": "cnn.com", "lean": "left", "monthly_visits": 400_000_000},
        ]
    },
    
    "tier_2_major": {
        "description": "Major broadcast and prestige print",
        "outlets": [
            {"domain": "washingtonpost.com", "lean": "left", "monthly_visits": 300_000_000},
            {"domain": "nbcnews.com", "lean": "left", "monthly_visits": 280_000_000},
            {"domain": "abcnews.go.com", "lean": "center-left", "monthly_visits": 250_000_000},
            {"domain": "cbsnews.com", "lean": "center-left", "monthly_visits": 220_000_000},
            {"domain": "wsj.com", "lean": "center-right", "monthly_visits": 200_000_000},
        ]
    },
    
    "tier_3_political": {
        "description": "Political and business specialist outlets",
        "outlets": [
            {"domain": "politico.com", "lean": "center", "monthly_visits": 150_000_000},
            {"domain": "thehill.com", "lean": "center", "monthly_visits": 120_000_000},
            {"domain": "cnbc.com", "lean": "center", "monthly_visits": 180_000_000},
            {"domain": "yahoo.com/news", "lean": "center", "monthly_visits": 350_000_000},
        ]
    },
    
    "tier_4_ideological": {
        "description": "Outlets with strong ideological identity",
        "outlets": [
            {"domain": "nypost.com", "lean": "right", "monthly_visits": 150_000_000},
            {"domain": "huffpost.com", "lean": "left", "monthly_visits": 100_000_000},
            {"domain": "breitbart.com", "lean": "far-right", "monthly_visits": 80_000_000},
            {"domain": "msnbc.com", "lean": "left", "monthly_visits": 90_000_000},
        ]
    },
    
    "wire_services": {
        "description": "Ground truth sources for fact verification",
        "outlets": [
            {"domain": "apnews.com", "lean": "center", "is_ground_truth": True},
            {"domain": "reuters.com", "lean": "center", "is_ground_truth": True},
        ]
    }
}


# ============================================================
# SUMMARY STATISTICS
# ============================================================

def get_taxonomy_summary():
    """Return summary of configured topics and outlets"""
    topic_count = len(TOPIC_CATEGORIES)
    tier_1_topics = len([t for t, v in TOPIC_CATEGORIES.items() if v["priority"] == 1])
    
    outlet_count = sum(
        len(tier["outlets"]) 
        for tier in OUTLET_TIERS.values()
    )
    
    return {
        "total_topic_categories": topic_count,
        "tier_1_high_priority": tier_1_topics,
        "total_outlets": outlet_count,
        "wire_services": 2,
    }


if __name__ == "__main__":
    summary = get_taxonomy_summary()
    print("YELLOW TOPIC TAXONOMY")
    print("=" * 40)
    print(f"Topic Categories: {summary['total_topic_categories']}")
    print(f"  - Tier 1 (Highest Priority): {summary['tier_1_high_priority']}")
    print(f"Outlets Tracked: {summary['total_outlets']}")
    print(f"  - Wire Services (Ground Truth): {summary['wire_services']}")
