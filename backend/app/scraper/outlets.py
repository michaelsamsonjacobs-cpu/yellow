"""
Outlet-specific scraper configurations.

Each outlet has different HTML structures, so we need custom selectors.
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class OutletConfig:
    name: str
    domain: str
    search_url_template: str  # URL template for topic search
    article_selector: str  # CSS selector for article links
    headline_selector: str  # CSS selector for headline in article
    body_selector: str  # CSS selector for body in article
    author_selector: Optional[str] = None
    date_selector: Optional[str] = None
    needs_javascript: bool = False  # Use Playwright if True
    monthly_visits: int = 0
    is_wire_service: bool = False


# Top 20 News Outlets Configuration
OUTLET_CONFIGS: List[OutletConfig] = [
    # Wire Services (Ground Truth - not scored)
    OutletConfig(
        name="Associated Press",
        domain="apnews.com",
        search_url_template="https://apnews.com/search?q={query}",
        article_selector="a.Link",
        headline_selector="h1.Page-headline",
        body_selector="div.RichTextStoryBody",
        author_selector="span.Component-bylines",
        date_selector="span.Timestamp",
        monthly_visits=148_000_000,
        is_wire_service=True
    ),
    OutletConfig(
        name="Reuters",
        domain="reuters.com",
        search_url_template="https://www.reuters.com/site-search/?query={query}",
        article_selector="a[data-testid='Heading']",
        headline_selector="h1[data-testid='Heading']",
        body_selector="div[data-testid='paragraph']",
        author_selector="a[data-testid='AuthorLink']",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=148_000_000,
        is_wire_service=True
    ),
    
    # Major Outlets (Scored)
    OutletConfig(
        name="New York Times",
        domain="nytimes.com",
        search_url_template="https://www.nytimes.com/search?query={query}",
        article_selector="a.css-1l4spti",
        headline_selector="h1[data-testid='headline']",
        body_selector="section[name='articleBody'] p",
        author_selector="span.css-1baulvz",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=620_000_000
    ),
    OutletConfig(
        name="CNN",
        domain="cnn.com",
        search_url_template="https://www.cnn.com/search?q={query}",
        article_selector="a.container__link",
        headline_selector="h1.headline__text",
        body_selector="div.article__content p",
        author_selector="span.byline__name",
        date_selector="div.timestamp",
        needs_javascript=True,
        monthly_visits=300_000_000
    ),
    OutletConfig(
        name="Fox News",
        domain="foxnews.com",
        search_url_template="https://www.foxnews.com/search-results/search?q={query}",
        article_selector="article.article a",
        headline_selector="h1.headline",
        body_selector="div.article-body p",
        author_selector="span.author-byline a",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=250_000_000
    ),
    OutletConfig(
        name="Washington Post",
        domain="washingtonpost.com",
        search_url_template="https://www.washingtonpost.com/search/?query={query}",
        article_selector="a.font--headline",
        headline_selector="h1#main-content",
        body_selector="article p",
        author_selector="a.author-name",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=180_000_000
    ),
    OutletConfig(
        name="USA Today",
        domain="usatoday.com",
        search_url_template="https://www.usatoday.com/search/?q={query}",
        article_selector="a.gnt_m_flm_a",
        headline_selector="h1.gnt_ar_hl",
        body_selector="article p.gnt_ar_b_p",
        author_selector="a.gnt_ar_by_a",
        date_selector="div.gnt_ar_dt",
        monthly_visits=150_000_000
    ),
    OutletConfig(
        name="CNBC",
        domain="cnbc.com",
        search_url_template="https://www.cnbc.com/search/?query={query}",
        article_selector="a.Card-title",
        headline_selector="h1.ArticleHeader-headline",
        body_selector="div.ArticleBody-articleBody p",
        author_selector="a.Author-authorName",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=127_000_000
    ),
    OutletConfig(
        name="NBC News",
        domain="nbcnews.com",
        search_url_template="https://www.nbcnews.com/search/?q={query}",
        article_selector="a.styles_headline__ice3t",
        headline_selector="h1.article-hero-headline__htag",
        body_selector="div.article-body__content p",
        author_selector="span.byline-name a",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=91_000_000
    ),
    OutletConfig(
        name="CBS News",
        domain="cbsnews.com",
        search_url_template="https://www.cbsnews.com/search/?q={query}",
        article_selector="article.item a",
        headline_selector="h1.content__title",
        body_selector="section.content__body p",
        author_selector="span.byline__name",
        date_selector="time",
        monthly_visits=103_000_000
    ),
    OutletConfig(
        name="ABC News",
        domain="abcnews.go.com",
        search_url_template="https://abcnews.go.com/search?searchtext={query}",
        article_selector="div.ContentRoll__Item a",
        headline_selector="h1.Story__Headline__Title",
        body_selector="article p",
        author_selector="span.Byline__Author",
        date_selector="div.Byline__Meta--publishDate",
        needs_javascript=True,
        monthly_visits=85_000_000
    ),
    OutletConfig(
        name="Wall Street Journal",
        domain="wsj.com",
        search_url_template="https://www.wsj.com/search?query={query}",
        article_selector="a.WSJTheme--headline--7VCzo7Ay",
        headline_selector="h1.wsj-article-headline",
        body_selector="div.article-content p",
        author_selector="span.author",
        date_selector="time.timestamp",
        needs_javascript=True,
        monthly_visits=80_000_000
    ),
    OutletConfig(
        name="Newsweek",
        domain="newsweek.com",
        search_url_template="https://www.newsweek.com/search/site/{query}",
        article_selector="a.title",
        headline_selector="h1.title",
        body_selector="article p",
        author_selector="span.author a",
        date_selector="time",
        monthly_visits=80_000_000
    ),
    OutletConfig(
        name="New York Post",
        domain="nypost.com",
        search_url_template="https://nypost.com/?s={query}",
        article_selector="h3.entry-heading a",
        headline_selector="h1.headline",
        body_selector="div.single__content p",
        author_selector="p.byline a",
        date_selector="span.date",
        monthly_visits=75_000_000
    ),
    OutletConfig(
        name="Yahoo News",
        domain="news.yahoo.com",
        search_url_template="https://news.search.yahoo.com/search?p={query}",
        article_selector="a.thmb",
        headline_selector="h1.caas-title",
        body_selector="div.caas-body p",
        author_selector="span.caas-author-byline-collapse",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=220_000_000
    ),
    OutletConfig(
        name="Politico",
        domain="politico.com",
        search_url_template="https://www.politico.com/search?q={query}",
        article_selector="article a.pos-relative",
        headline_selector="h1.headline",
        body_selector="div.story-text p",
        author_selector="span.byline a",
        date_selector="time.timestamp",
        monthly_visits=54_000_000
    ),
    OutletConfig(
        name="The Hill",
        domain="thehill.com",
        search_url_template="https://thehill.com/?s={query}",
        article_selector="h4.featured-default__title a",
        headline_selector="h1.headline__title",
        body_selector="div.article__text p",
        author_selector="span.submitted-by a",
        date_selector="span.submitted-by-date",
        monthly_visits=50_000_000
    ),
    OutletConfig(
        name="HuffPost",
        domain="huffpost.com",
        search_url_template="https://www.huffpost.com/search?q={query}",
        article_selector="a.card__headline-text",
        headline_selector="h1.headline__title",
        body_selector="div.primary-cli p",
        author_selector="a.author-card__link--author",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=45_000_000
    ),
    OutletConfig(
        name="Business Insider",
        domain="businessinsider.com",
        search_url_template="https://www.businessinsider.com/s?q={query}",
        article_selector="a.tout-title-link",
        headline_selector="h1.post-headline",
        body_selector="div.content-lock-content p",
        author_selector="span.byline-author a",
        date_selector="div.byline-timestamp",
        needs_javascript=True,
        monthly_visits=40_000_000
    ),
    OutletConfig(
        name="MSN",
        domain="msn.com",
        search_url_template="https://www.msn.com/en-us/search?q={query}",
        article_selector="a.title",
        headline_selector="h1.title",
        body_selector="article p",
        author_selector="span.author",
        date_selector="time",
        needs_javascript=True,
        monthly_visits=490_000_000
    ),
]


def get_outlet_config(domain: str) -> Optional[OutletConfig]:
    """Get config for a specific outlet domain"""
    for config in OUTLET_CONFIGS:
        if config.domain == domain or domain.endswith(config.domain):
            return config
    return None


def get_all_configs() -> List[OutletConfig]:
    """Get all outlet configurations"""
    return OUTLET_CONFIGS


def get_scored_outlets() -> List[OutletConfig]:
    """Get outlets that should be scored (excluding wire services)"""
    return [c for c in OUTLET_CONFIGS if not c.is_wire_service]


def get_wire_services() -> List[OutletConfig]:
    """Get wire service outlets (ground truth)"""
    return [c for c in OUTLET_CONFIGS if c.is_wire_service]
