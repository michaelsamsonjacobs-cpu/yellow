
import asyncio
from datetime import datetime
from app.db.database import AsyncSessionLocal
from app.db.models import Article, Topic, Outlet
from sqlalchemy import select

MOCK_ARTICLES = [
    {
        "headline": "Senate Passes Historic Border Bill Amidst Controversy",
        "body": "The Senate passed the new border security legislative package late last night. Supporters call it a necessary step for national security, while opponents argue it violates human rights. The bill includes funding for more agents and physical barriers...",
        "outlet_domain": "foxnews.com",
        "topic": "Immigration"
    },
    {
        "headline": "Border Legislation Stalls: A Victory for Human Rights",
        "body": "The draconian border bill faced stiff resistance in the Senate, with activists celebrating the delay as a win for immigrant rights. Critics labeled the bill as 'inhumane' and 'ineffective'...",
        "outlet_domain": "msnbc.com",
        "topic": "Immigration"
    },
    {
        "headline": "Inflation Cools to 3.1%, Signals Soft Landing",
        "body": "Consumer prices rose less than expected in January, fueling hopes that the Federal Reserve can cut interest rates. The 'soft landing' scenario appears increasingly likely as the economy remains resilient...",
        "outlet_domain": "cnbc.com",
        "topic": "Economy"
    },
    {
        "headline": "Prices Remain high as Bidenonomics Fails Working Families",
        "body": "Despite claims of cooling inflation, everyday Americans are still struggling at the grocery store. The administration's policies have entrenched high prices, leaving families behind...",
        "outlet_domain": "nypost.com",
        "topic": "Economy"
    }
]

async def inject_mock_data():
    async with AsyncSessionLocal() as db:
        print("Injecting mock articles...")
        for data in MOCK_ARTICLES:
            # Get Outlet
            outlet = (await db.execute(select(Outlet).where(Outlet.domain == data["outlet_domain"]))).scalar_one_or_none()
            if not outlet:
                print(f"Skipping {data['outlet_domain']} - not found")
                continue
                
            # Get Topic
            topic = (await db.execute(select(Topic).where(Topic.name == data["topic"]))).scalar_one_or_none()
            if not topic:
                 # Create topic if missing (just in case)
                 topic = Topic(name=data["topic"], slug=data["topic"].lower(), category="us", date=datetime.utcnow(), article_count=0)
                 db.add(topic)
                 await db.commit()
                 await db.refresh(topic)

            article = Article(
                outlet_id=outlet.id,
                topic_id=topic.id,
                headline=data["headline"],
                body=data["body"],
                url=f"https://{data['outlet_domain']}/article/{datetime.now().timestamp()}",
                published_at=datetime.utcnow()
            )
            db.add(article)
            topic.article_count += 1
        
        await db.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(inject_mock_data())
