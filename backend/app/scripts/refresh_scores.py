"""
Manual Score Refresh Script

Recalculates all outlet batting averages, applying the new Topic Skew Penalty.
"""
import asyncio
import sys
import os

# Add backend directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.tasks.scoring import rollup_outlet_scores

async def main():
    print("Starting manual score refresh...")
    count = await rollup_outlet_scores()
    print(f"Success: Recalculated scores for {count} outlets.")

if __name__ == "__main__":
    asyncio.run(main())
