"""
Email service using Resend
"""
import resend
from app.config import get_settings

settings = get_settings()

# Initialize Resend
resend.api_key = settings.resend_api_key


async def send_magic_link_email(email: str, link_url: str) -> None:
    """Send passwordless magic link email"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Georgia', serif; background: #1A1A1A; color: #F5F5DC; padding: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ border-bottom: 3px solid #FFD700; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo {{ font-size: 36px; font-weight: bold; color: #FFD700; }}
            h1 {{ color: #FFD700; font-size: 24px; }}
            .button {{ 
                display: inline-block; 
                background: #FFD700; 
                color: #1A1A1A !important; 
                padding: 15px 30px; 
                text-decoration: none; 
                font-weight: bold;
                margin: 20px 0;
            }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">YELLOW</div>
            </div>
            <h1>Sign in to Yellow</h1>
            <p>Click the button below to sign in to your account. This link expires in 15 minutes.</p>
            <a href="{link_url}" class="button">Sign In to Yellow</a>
            <p style="font-size: 14px; color: #888;">Or copy this link: {link_url}</p>
            <div class="footer">
                <p>If you didn't request this email, you can safely ignore it.</p>
                <p>© 2026 Yellow. Hold the press accountable.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    print("="*50)
    print(f"MAGIC LINK EMAIL TO: {email}")
    print(f"LINK: {link_url}")
    print("="*50)
    
    resend.Emails.send({
        "from": settings.resend_from_email,
        "to": email,
        "subject": "Sign in to Yellow",
        "html": html_content
    })


async def send_newsletter_welcome_email(email: str, unsubscribe_token: str) -> None:
    """Send welcome email to new newsletter subscribers"""
    
    unsubscribe_url = f"{settings.api_url}/newsletter/unsubscribe?token={unsubscribe_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Georgia', serif; background: #1A1A1A; color: #F5F5DC; padding: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ border-bottom: 3px solid #FFD700; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo {{ font-size: 36px; font-weight: bold; color: #FFD700; }}
            h1 {{ color: #FFD700; font-size: 24px; }}
            .highlight {{ background: #FFD700; color: #1A1A1A; padding: 2px 6px; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #888; }}
            a {{ color: #FFD700; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">YELLOW</div>
            </div>
            <h1>Welcome to The Daily Briefing</h1>
            <p>You're now subscribed to Yellow's Daily Briefing newsletter.</p>
            <p>Every day, you'll receive:</p>
            <ul>
                <li><span class="highlight">Top 3</span> most accurate articles of the day</li>
                <li><span class="highlight">Top 3</span> most biased articles (with our Fair Redrafts)</li>
                <li>The outlet with the highest and lowest integrity scores</li>
            </ul>
            <p>Want the full experience? <a href="{settings.frontend_url}/pricing">Subscribe to Yellow</a> for just $9.95/month.</p>
            <div class="footer">
                <p><a href="{unsubscribe_url}">Unsubscribe</a> from this newsletter.</p>
                <p>© 2026 Yellow. Hold the press accountable.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    resend.Emails.send({
        "from": settings.resend_from_email,
        "to": email,
        "subject": "Welcome to Yellow's Daily Briefing",
        "html": html_content
    })


async def send_daily_briefing(
    email: str,
    unsubscribe_token: str,
    top_accurate: list,
    top_biased: list,
    highest_outlet: dict,
    lowest_outlet: dict
) -> None:
    """Send daily briefing newsletter"""
    
    unsubscribe_url = f"{settings.api_url}/newsletter/unsubscribe?token={unsubscribe_token}"
    
    # Build article lists HTML
    accurate_html = ""
    for article in top_accurate[:3]:
        accurate_html += f"""
        <li>
            <strong>{article['headline'][:80]}...</strong><br>
            <span style="color: #228B22;">Score: {article['score']}/100</span> — {article['outlet']}
        </li>
        """
    
    biased_html = ""
    for article in top_biased[:3]:
        biased_html += f"""
        <li>
            <strong>{article['headline'][:80]}...</strong><br>
            <span style="color: #C41E3A;">Score: {article['score']}/100</span> — {article['outlet']}
            <br><a href="{settings.frontend_url}/articles/{article['id']}">See Fair Redraft →</a>
        </li>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Georgia', serif; background: #1A1A1A; color: #F5F5DC; padding: 40px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ border-bottom: 3px solid #FFD700; padding-bottom: 20px; margin-bottom: 30px; }}
            .logo {{ font-size: 36px; font-weight: bold; color: #FFD700; }}
            h1 {{ color: #FFD700; font-size: 24px; }}
            h2 {{ color: #FFD700; font-size: 18px; margin-top: 30px; }}
            .ticker {{ background: #2A2A2A; padding: 15px; margin: 20px 0; }}
            .high {{ color: #228B22; }}
            .low {{ color: #C41E3A; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 15px; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #888; border-top: 1px solid #444; padding-top: 20px; }}
            a {{ color: #FFD700; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">YELLOW</div>
                <div style="font-size: 14px; color: #888;">The Daily Briefing</div>
            </div>
            
            <div class="ticker">
                <span class="high">🟢 HIGHEST TODAY: {highest_outlet['name']} ({highest_outlet['score']}/100)</span><br>
                <span class="low">🔴 LOWEST TODAY: {lowest_outlet['name']} ({lowest_outlet['score']}/100)</span>
            </div>
            
            <h2>✓ Top 3 Most Accurate</h2>
            <ul>{accurate_html}</ul>
            
            <h2>✗ Top 3 Most Biased</h2>
            <ul>{biased_html}</ul>
            
            <p style="text-align: center; margin-top: 30px;">
                <a href="{settings.frontend_url}/dashboard" style="background: #FFD700; color: #1A1A1A; padding: 12px 24px; text-decoration: none; font-weight: bold;">
                    See Full Dashboard →
                </a>
            </p>
            
            <div class="footer">
                <p><a href="{unsubscribe_url}">Unsubscribe</a> from this newsletter.</p>
                <p>© 2026 Yellow. Hold the press accountable.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    resend.Emails.send({
        "from": settings.resend_from_email,
        "to": email,
        "subject": f"Yellow Daily Briefing — {highest_outlet['name']} leads, {lowest_outlet['name']} trails",
        "html": html_content
    })
