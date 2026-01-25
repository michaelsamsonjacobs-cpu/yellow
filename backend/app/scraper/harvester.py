"""
Article Scraper - The Harvester

Scrapes articles from configured news outlets using:
- Scrapy for simple sites
- Playwright for JavaScript-rendered sites
- BrightData proxies to avoid blocks
"""
import asyncio
import random
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import quote_plus, urljoin
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser

from app.config import get_settings
from app.scraper.outlets import OutletConfig, get_outlet_config
from app.scraper.taxonomy import TOPIC_CATEGORIES

settings = get_settings()


# User agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


@dataclass
class ScrapedArticle:
    url: str
    headline: str
    body: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    outlet_domain: str = ""
    category_tag: Optional[str] = None


class ArticleScraper:
    """Main scraper class for harvesting articles"""
    
    def __init__(self, use_proxy: bool = True):
        self.use_proxy = use_proxy
        self.browser: Optional[Browser] = None
        
    def _get_proxy_url(self) -> Optional[str]:
        """Get BrightData proxy URL"""
        if not self.use_proxy or not settings.brightdata_username:
            return None
        if "placeholder" in settings.brightdata_password:
             return None
        return f"http://{settings.brightdata_username}:{settings.brightdata_password}@{settings.brightdata_host}"
    
    def _get_random_user_agent(self) -> str:
        """Get random user agent for rotation"""
        return random.choice(USER_AGENTS)
    
    def classify_article(self, headline: str, body: str) -> Optional[str]:
        """Classify article into taxonomy category based on keywords"""
        text = (headline + " " + body).lower()
        
        best_category = None
        max_matches = 0
        
        for category, config in TOPIC_CATEGORIES.items():
            matches = sum(1 for keyword in config["keywords"] if keyword in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category
                
        # Only assign if we have a reasonable confidence (at least 2 keyword matches)
        if max_matches >= 2:
            return best_category
        return None
    
    async def _init_browser(self) -> Browser:
        """Initialize Playwright browser"""
        if self.browser:
            return self.browser
            
        playwright = await async_playwright().start()
        
        browser_args = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox"
            ]
        }
        
        if self.use_proxy and settings.brightdata_username and "placeholder" not in settings.brightdata_password:
            browser_args["proxy"] = {
                "server": f"http://{settings.brightdata_host}",
                "username": settings.brightdata_username,
                "password": settings.brightdata_password
            }
        
        self.browser = await playwright.chromium.launch(**browser_args)
        return self.browser
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def search_outlet(
        self,
        outlet_config: OutletConfig,
        query: str,
        max_articles: int = 10
    ) -> List[str]:
        """
        Search an outlet for articles matching a query.
        Returns list of article URLs.
        """
        search_url = outlet_config.search_url_template.format(
            query=quote_plus(query)
        )
        
        if outlet_config.needs_javascript:
            return await self._search_with_playwright(
                search_url, outlet_config, max_articles
            )
        else:
            return await self._search_with_httpx(
                search_url, outlet_config, max_articles
            )
    
    async def _search_with_httpx(
        self,
        search_url: str,
        config: OutletConfig,
        max_articles: int
    ) -> List[str]:
        """Search using httpx for non-JS sites"""
        headers = {"User-Agent": self._get_random_user_agent()}
        proxy = self._get_proxy_url()
        
        async with httpx.AsyncClient(proxy=proxy, timeout=30) as client:
            try:
                response = await client.get(search_url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                links = soup.select(config.article_selector)
                
                urls = []
                for link in links[:max_articles]:
                    href = link.get("href")
                    if href:
                        full_url = urljoin(f"https://{config.domain}", href)
                        urls.append(full_url)
                
                return urls
                
            except Exception as e:
                print(f"Search error for {config.domain}: {e}")
                return []
    
    async def _search_with_playwright(
        self,
        search_url: str,
        config: OutletConfig,
        max_articles: int
    ) -> List[str]:
        """Search using Playwright for JS-rendered sites"""
        browser = await self._init_browser()
        context = await browser.new_context(
            user_agent=self._get_random_user_agent()
        )
        page = await context.new_page()
        
        try:
            await page.goto(search_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(1, 3))  # Random delay
            
            links = await page.query_selector_all(config.article_selector)
            
            urls = []
            for link in links[:max_articles]:
                href = await link.get_attribute("href")
                if href:
                    full_url = urljoin(f"https://{config.domain}", href)
                    urls.append(full_url)
            
            return urls
            
        except Exception as e:
            print(f"Playwright search error for {config.domain}: {e}")
            return []
        finally:
            await context.close()
    
    async def scrape_article(
        self,
        url: str,
        outlet_config: OutletConfig
    ) -> Optional[ScrapedArticle]:
        """
        Scrape a single article.
        """
        if outlet_config.needs_javascript:
            return await self._scrape_with_playwright(url, outlet_config)
        else:
            return await self._scrape_with_httpx(url, outlet_config)
    
    async def _scrape_with_httpx(
        self,
        url: str,
        config: OutletConfig
    ) -> Optional[ScrapedArticle]:
        """Scrape article using httpx"""
        headers = {"User-Agent": self._get_random_user_agent()}
        proxy = self._get_proxy_url()
        
        async with httpx.AsyncClient(proxy=proxy, timeout=30) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                
                # Extract headline
                headline_el = soup.select_one(config.headline_selector)
                headline = headline_el.get_text(strip=True) if headline_el else ""
                
                # Extract body
                body_elements = soup.select(config.body_selector)
                body = "\n\n".join([p.get_text(strip=True) for p in body_elements])
                
                # Extract author
                author = None
                if config.author_selector:
                    author_el = soup.select_one(config.author_selector)
                    author = author_el.get_text(strip=True) if author_el else None
                
                # Extract date
                published_at = None
                if config.date_selector:
                    date_el = soup.select_one(config.date_selector)
                    if date_el:
                        date_str = date_el.get("datetime") or date_el.get_text(strip=True)
                        published_at = self._parse_date(date_str)
                
                if not headline or not body:
                    return None
                
                category_tag = self.classify_article(headline, body)
                
                return ScrapedArticle(
                    url=url,
                    headline=headline,
                    body=body,
                    author=author,
                    published_at=published_at,
                    outlet_domain=config.domain,
                    category_tag=category_tag
                )
                
            except Exception as e:
                print(f"Scrape error for {url}: {e}")
                return None
    
    async def _scrape_with_playwright(
        self,
        url: str,
        config: OutletConfig
    ) -> Optional[ScrapedArticle]:
        """Scrape article using Playwright"""
        browser = await self._init_browser()
        context = await browser.new_context(
            user_agent=self._get_random_user_agent()
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(random.uniform(1, 2))
            
            # Extract headline
            headline = ""
            headline_el = await page.query_selector(config.headline_selector)
            if headline_el:
                headline = await headline_el.inner_text()
            
            # Extract body
            body_elements = await page.query_selector_all(config.body_selector)
            body_parts = []
            for el in body_elements:
                text = await el.inner_text()
                if text.strip():
                    body_parts.append(text.strip())
            body = "\n\n".join(body_parts)
            
            # Extract author
            author = None
            if config.author_selector:
                author_el = await page.query_selector(config.author_selector)
                if author_el:
                    author = await author_el.inner_text()
            
            # Extract date
            published_at = None
            if config.date_selector:
                date_el = await page.query_selector(config.date_selector)
                if date_el:
                    date_str = await date_el.get_attribute("datetime")
                    if not date_str:
                        date_str = await date_el.inner_text()
                    published_at = self._parse_date(date_str)
            
            if not headline or not body:
                return None
            
            category_tag = self.classify_article(headline, body)
            
            return ScrapedArticle(
                url=url,
                headline=headline,
                body=body,
                author=author,
                published_at=published_at,
                outlet_domain=config.domain,
                category_tag=category_tag
            )
            
        except Exception as e:
            print(f"Playwright scrape error for {url}: {e}")
            return None
        finally:
            await context.close()
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_str:
            return None
            
        from dateutil import parser
        try:
            return parser.parse(date_str)
        except:
            return None


async def scrape_topic_from_outlet(
    outlet_config: OutletConfig,
    topic_query: str,
    max_articles: int = 5
) -> List[ScrapedArticle]:
    """
    Scrape articles about a topic from a single outlet.
    """
    scraper = ArticleScraper()
    articles = []
    
    try:
        # Search for articles
        urls = await scraper.search_outlet(outlet_config, topic_query, max_articles)
        
        # Add delay between requests
        for url in urls:
            await asyncio.sleep(random.uniform(2, 4))
            
            article = await scraper.scrape_article(url, outlet_config)
            if article:
                articles.append(article)
    finally:
        await scraper.close()
    
    return articles
