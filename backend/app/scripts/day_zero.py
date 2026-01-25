"""
Day Zero Script - Run the full pipeline to populate the database.

Pipeline:
1. Seed Outlets (if not exists)
2. Discover Topics (AP/Reuters)
3. Harvest Articles (20 outlets)
4. Score Articles (SPJ Rubric)
5. Rollup Outlet Scores

Run with: python -m app.scripts.day_zero
"""
import asyncio
import sys
from app.scripts.seed_outlets import seed_outlets
from app.tasks.discovery import discover_and_store_topics
from app.tasks.scraping import harvest_all_outlets
from app.tasks.scoring import score_pending_articles, rollup_outlet_scores

async def run_day_zero():
    print("🚀 STARTING DAY ZERO DATA SCRAPE...")
    
    # 1. Seed Outlets
    print("\n[1/5] Seeding Outlets...")
    try:
        await seed_outlets()
    except Exception as e:
        print(f"❌ Error seeding outlets: {e}")
        # Proceeding as outlets might already exist

    # 2. Discover Topics
    print("\n[2/5] Discovering Topics...")
    try:
        topic_count = await discover_and_store_topics()
        print(f"✅ Discovered {topic_count} topics.")
        if topic_count == 0:
            print("⚠️ No topics found. Scraper might assume default topics or fail.")
    except Exception as e:
        print(f"❌ Error discovering topics: {e}")
        if "Missing API Key" in str(e):
             print("⚠️ Please check your .env file.")
        
    # 3. Harvest Articles
    print("\n[3/5] Harvesting Articles (This may take a while)...")
    try:
        # Note: harvest_all_outlets checks for today's topics.
        # If run immediately after discovery, it should find them.
        article_count = await harvest_all_outlets()
        print(f"✅ Harvested {article_count} articles.")
    except Exception as e:
        print(f"❌ Error harvesting articles: {e}")

    # 4. Score Articles
    print("\n[4/5] Scoring Articles (AI Analysis)...")
    try:
        score_count = await score_pending_articles()
        print(f"✅ Scored {score_count} articles.")
    except Exception as e:
        print(f"❌ Error scoring articles: {e}")

    # 5. Rollup Scores
    print("\n[5/5] Rolling up Outlet Scores...")
    try:
        outlet_count = await rollup_outlet_scores()
        print(f"✅ Updated scores for {outlet_count} outlets.")
    except Exception as e:
        print(f"❌ Error rolling up scores: {e}")

    print("\n✨ DAY ZERO COMPLETE!")
    print("Check your dashboard to see the results.")

if __name__ == "__main__":
    import os
    
    # Ensure we can import app modules
    sys.path.append(os.getcwd())
    
    # Check for existing loop (e.g. jupyter)
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    try:
        if loop and loop.is_running():
            print("⚠️ Event loop already running. Use 'await run_day_zero()' if in REPL.")
            # Create task if in existing loop
            loop.create_task(run_day_zero())
        else:
            asyncio.run(run_day_zero())
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Script interrupted by user.")
    except Exception as e:
        print(f"\n\n💥 Fatal Error: {e}")
