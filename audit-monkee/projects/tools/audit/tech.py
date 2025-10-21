import requests
import re
import json
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

# Technology signatures database
TECH_SIGNATURES = {
    "cms": {
        "WordPress": {
            "meta": [r"generator.*wordpress", r"wp-content", r"wp-includes"],
            "scripts": [r"wp-content", r"wp-includes", r"wp-json"],
            "headers": ["x-powered-by.*wordpress"]
        },
        "Shopify": {
            "meta": [r"shopify"],
            "scripts": [r"cdn\.shopify\.com"],
            "cookies": [r"_shopify"]
        },
        "Squarespace": {
            "meta": [r"squarespace"],
            "scripts": [r"squarespace\.com"],
            "headers": [r"x-servedby.*squarespace"]
        },
        "Wix": {
            "meta": [r"wix\.com"],
            "scripts": [r"wixpress\.com"],
            "cookies": [r"wixLanguageCode"]
        },
        "Joomla": {
            "meta": [r"generator.*joomla"],
            "scripts": [r"media/jui", r"components/com_"]
        },
        "Drupal": {
            "meta": [r"generator.*drupal"],
            "scripts": [r"misc/drupal\.js"]
        }
    },
    "cdn": {
        "Cloudflare": {
            "headers": [r"cf-ray", r"cf-cache-status", r"server.*cloudflare"]
        },
        "AWS CloudFront": {
            "headers": [r"x-amz-cf-id", r"x-amz-cf-pop"]
        },
        "Fastly": {
            "headers": [r"x-served-by.*fastly"]
        },
        "Akamai": {
            "headers": [r"x-akamai-transformed"]
        }
    },
    "analytics": {
        "Google Analytics": {
            "scripts": [r"googletagmanager\.com", r"google-analytics\.com"],
            "cookies": [r"_ga", r"_gid"]
        },
        "Google Tag Manager": {
            "scripts": [r"googletagmanager\.com/gtm"],
            "cookies": [r"_ga"]
        },
        "Facebook Pixel": {
            "scripts": [r"connect\.facebook\.net", r"facebook\.com/tr"],
            "cookies": [r"_fbp"]
        },
        "Adobe Analytics": {
            "scripts": [r"adobe.*analytics", r"omniture"],
            "cookies": [r"s_cc", r"s_sq"]
        },
        "Hotjar": {
            "scripts": [r"hotjar\.com"],
            "cookies": [r"_hjid"]
        }
    },
    "frameworks": {
        "React": {
            "scripts": [r"react.*\.js", r"react-dom"],
            "meta": [r"_reactroot"]
        },
        "Vue.js": {
            "scripts": [r"vue.*\.js"],
            "meta": [r"vue-ssr"]
        },
        "Angular": {
            "scripts": [r"angular.*\.js"],
            "meta": [r"ng-version"]
        },
        "jQuery": {
            "scripts": [r"jquery.*\.js"],
            "cookies": [r"jquery"]
        }
    },
    "ecommerce": {
        "WooCommerce": {
            "scripts": [r"woocommerce"],
            "meta": [r"woocommerce"]
        },
        "Magento": {
            "meta": [r"magento"],
            "headers": [r"x-magento"]
        },
        "BigCommerce": {
            "scripts": [r"bigcommerce\.com"]
        }
    }
}

def detect_stack(url: str) -> Dict[str, Any]:
    """
    Comprehensive technology stack detection
    Returns detailed information about detected technologies
    """
    try:
        # Parse URL
        parsed = urlparse(url)
        domain = parsed.netloc

        # Fetch page content
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Audit-Monkee/1.0)'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get response headers
        headers = {k.lower(): v.lower() for k, v in response.headers.items()}

        # Get cookies
        cookies = {k.lower(): v for k, v in response.cookies.items()}

        detected = {
            "cms": detect_category(soup, headers, cookies, "cms"),
            "cdn": detect_category(soup, headers, cookies, "cdn"),
            "analytics": detect_category(soup, headers, cookies, "analytics"),
            "frameworks": detect_category(soup, headers, cookies, "frameworks"),
            "ecommerce": detect_category(soup, headers, cookies, "ecommerce"),
            "server": detect_server(headers),
            "dns": detect_dns_info(domain),
            "confidence": calculate_confidence(soup, headers, cookies)
        }

        return detected

    except Exception as e:
        logger.error(f"Tech stack detection failed for {url}: {e}")
        return {
            "error": str(e),
            "cms": [],
            "cdn": [],
            "analytics": [],
            "frameworks": [],
            "ecommerce": [],
            "confidence": 0
        }

def detect_category(soup: BeautifulSoup, headers: Dict[str, str], cookies: Dict[str, str], category: str) -> List[str]:
    """Detect technologies in a specific category"""
    detected = []

    for tech, signatures in TECH_SIGNATURES[category].items():
        score = 0
        total_checks = 0

        # Check meta tags
        if "meta" in signatures:
            for pattern in signatures["meta"]:
                total_checks += 1
                meta_tags = soup.find_all('meta', attrs={
                    'name': lambda x: x and re.search(pattern, x, re.I),
                    'content': lambda x: x and re.search(pattern, x, re.I)
                })
                if meta_tags:
                    score += 1

        # Check scripts
        if "scripts" in signatures:
            for pattern in signatures["scripts"]:
                total_checks += 1
                scripts = soup.find_all('script', src=lambda x: x and re.search(pattern, x, re.I))
                if scripts:
                    score += 1

        # Check headers
        if "headers" in signatures:
            for pattern in signatures["headers"]:
                total_checks += 1
                for header_value in headers.values():
                    if re.search(pattern, header_value, re.I):
                        score += 1
                        break

        # Check cookies
        if "cookies" in signatures:
            for pattern in signatures["cookies"]:
                total_checks += 1
                for cookie_name in cookies.keys():
                    if re.search(pattern, cookie_name, re.I):
                        score += 1
                        break

        # If we have enough evidence, add the technology
        if total_checks > 0 and (score / total_checks) >= 0.3:
            detected.append(tech)

    return detected

def detect_server(headers: Dict[str, str]) -> str:
    """Detect server technology"""
    server_header = headers.get('server', '')
    if 'nginx' in server_header:
        return 'Nginx'
    elif 'apache' in server_header:
        return 'Apache'
    elif 'litespeed' in server_header:
        return 'LiteSpeed'
    elif 'microsoft-iis' in server_header:
        return 'IIS'
    elif 'cloudflare' in server_header:
        return 'Cloudflare'
    return 'Unknown'

def detect_dns_info(domain: str) -> Dict[str, Any]:
    """Basic DNS information (simplified)"""
    # In a real implementation, you'd query DNS records
    # For now, return basic info based on common patterns
    return {
        "nameservers": "unknown",
        "mx_records": "unknown",
        "ssl_expiry": "unknown"
    }

def calculate_confidence(soup: BeautifulSoup, headers: Dict[str, str], cookies: Dict[str, str]) -> float:
    """Calculate overall confidence in detection"""
    total_signals = 0
    detected_signals = 0

    # Count scripts, meta tags, etc. as signals
    scripts = len(soup.find_all('script'))
    meta_tags = len(soup.find_all('meta'))
    links = len(soup.find_all('link'))

    total_signals = scripts + meta_tags + links + len(headers) + len(cookies)

    # Simple heuristic - more elements = more confidence
    if total_signals > 100:
        return 0.9
    elif total_signals > 50:
        return 0.7
    elif total_signals > 20:
        return 0.5
    else:
        return 0.3
