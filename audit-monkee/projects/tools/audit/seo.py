import requests
import re
import json
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse, urlunparse
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def run_seo_checks(url: str) -> Dict[str, Any]:
    """
    Comprehensive SEO audit of a website
    Returns structured data about SEO elements found
    """
    try:
        # Parse base URL
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Fetch main page
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Audit-Monkee/1.0)'
        })
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        results = {
            "canonical": check_canonical(soup, url),
            "robots_meta": check_robots_meta(soup),
            "title": check_title(soup),
            "meta_description": check_meta_description(soup),
            "headings": check_headings(soup),
            "schema_detected": check_schema(soup),
            "internal_links": check_internal_links(soup, base_url),
            "external_links": check_external_links(soup, base_url),
            "images": check_images(soup, base_url),
            "robots_txt": check_robots_txt(base_url),
            "sitemap": check_sitemap(base_url),
            "ssl_certificate": check_ssl(url),
            "mobile_friendly": check_mobile_friendly(soup),
            "page_size": len(response.content),
            "load_time_ms": response.elapsed.total_seconds() * 1000
        }

        return results

    except Exception as e:
        logger.error(f"SEO audit failed for {url}: {e}")
        return {
            "error": str(e),
            "canonical": False,
            "robots_meta": "unknown",
            "schema_detected": False
        }

def check_canonical(soup: BeautifulSoup, url: str) -> bool:
    """Check if page has canonical URL"""
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        canonical_url = urljoin(url, canonical['href'])
        return canonical_url == url
    return False

def check_robots_meta(soup: BeautifulSoup) -> str:
    """Check robots meta directive"""
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots:
        return robots.get('content', 'index,follow')
    return 'index,follow'

def check_title(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check page title"""
    title = soup.find('title')
    if title:
        title_text = title.get_text().strip()
        return {
            "text": title_text,
            "length": len(title_text),
            "optimal_length": 30 <= len(title_text) <= 60
        }
    return {"text": "", "length": 0, "optimal_length": False}

def check_meta_description(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check meta description"""
    desc = soup.find('meta', attrs={'name': 'description'})
    if desc:
        desc_text = desc.get('content', '').strip()
        return {
            "text": desc_text,
            "length": len(desc_text),
            "optimal_length": 120 <= len(desc_text) <= 160
        }
    return {"text": "", "length": 0, "optimal_length": False}

def check_headings(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check heading structure"""
    headings = {}
    for i in range(1, 7):
        h_tags = soup.find_all(f'h{i}')
        headings[f'h{i}_count'] = len(h_tags)
        if i == 1 and h_tags:
            headings['h1_text'] = h_tags[0].get_text().strip()

    return headings

def check_schema(soup: BeautifulSoup) -> bool:
    """Check for structured data"""
    schemas = soup.find_all(['script'], type='application/ld+json')
    return len(schemas) > 0

def check_internal_links(soup: BeautifulSoup, base_url: str) -> int:
    """Count internal links"""
    internal_links = 0
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/') or href.startswith(base_url):
            internal_links += 1
    return internal_links

def check_external_links(soup: BeautifulSoup, base_url: str) -> int:
    """Count external links"""
    external_links = 0
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('http') and not href.startswith(base_url):
            external_links += 1
    return external_links

def check_images(soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
    """Check images for alt tags and optimization"""
    images = soup.find_all('img')
    total_images = len(images)
    images_with_alt = len([img for img in images if img.get('alt')])

    return {
        "total": total_images,
        "with_alt": images_with_alt,
        "alt_coverage": (images_with_alt / total_images * 100) if total_images > 0 else 0
    }

def check_robots_txt(base_url: str) -> Dict[str, Any]:
    """Check robots.txt"""
    try:
        response = requests.get(f"{base_url}/robots.txt", timeout=10)
        if response.status_code == 200:
            content = response.text
            return {
                "exists": True,
                "user_agents": len(re.findall(r'^User-agent:', content, re.MULTILINE)),
                "disallows": len(re.findall(r'^Disallow:', content, re.MULTILINE))
            }
    except:
        pass
    return {"exists": False}

def check_sitemap(base_url: str) -> Dict[str, Any]:
    """Check sitemap.xml"""
    try:
        response = requests.get(f"{base_url}/sitemap.xml", timeout=10)
        if response.status_code == 200:
            # Try to parse as XML
            try:
                root = ET.fromstring(response.content)
                urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                return {
                    "exists": True,
                    "url_count": len(urls),
                    "type": "xml"
                }
            except:
                # Check if it's a sitemap index
                if 'sitemapindex' in response.text.lower():
                    return {"exists": True, "type": "index"}
    except:
        pass
    return {"exists": False}

def check_ssl(url: str) -> bool:
    """Check if site uses HTTPS"""
    parsed = urlparse(url)
    return parsed.scheme == 'https'

def check_mobile_friendly(soup: BeautifulSoup) -> Dict[str, Any]:
    """Check mobile-friendly indicators"""
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    return {
        "viewport_configured": viewport is not None,
        "viewport_content": viewport.get('content') if viewport else None
    }
