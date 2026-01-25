
import asyncio
import logging
import sys
from app.tasks.scraping import harvest_single_outlet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

if __name__ == "__main__":
    print("Starting single outlet harvest test...")
    count = harvest_single_outlet("foxnews.com")
    print(f"Harvested {count} articles.")
