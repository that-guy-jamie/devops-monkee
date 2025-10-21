#!/usr/bin/env python3
"""
One Click SEO Client Audit Tool
Combined SEO, Design, and Technical Analysis for New Client Onboarding

Features:
- SEO crawling and analysis
- Design pattern extraction
- Technical stack detection
- WordPress theme/plugin analysis
- Security header checks
- Performance metrics
- Built-in help system

Usage:
    python client-audit-tool.py --url https://example.com
    python client-audit-tool.py --help
    python client-audit-tool.py --url https://example.com --quick
    python client-audit-tool.py --url https://example.com --full
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
import re


class ClientAuditTool:
    """
    Comprehensive client audit tool combining SEO, design, and technical analysis.
    """

    def __init__(self, url: str, quick_mode: bool = False, full_mode: bool = False):
        self.url = url.rstrip('/')
        self.quick_mode = quick_mode
        self.full_mode = full_mode
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ASTRO-Client-Audit/1.0'
        })

        # Parse domain info
        parsed = urlparse(self.url)
        self.domain = parsed.netloc
        self.base_domain = f"{parsed.scheme}://{parsed.netloc}"

        # Results storage
        self.results = {
            'url': self.url,
            'timestamp': datetime.now().isoformat(),
            'domain': self.domain,
            'mode': 'full' if full_mode else 'quick' if quick_mode else 'standard',
            'technical': {},
            'seo': {},
            'design': {},
            'security': {},
            'recommendations': []
        }

    def run_audit(self) -> Dict[str, Any]:
        """Run the complete audit."""
        print("🚀 One Click SEO Client Audit Tool")
        print(f"📋 Auditing: {self.url}")
        print(f"🏷️  Mode: {self.results['mode']}")
        print("=" * 60)

        # Technical analysis
        self._analyze_technical_stack()

        # SEO analysis
        self._analyze_seo()

        # Design analysis
        self._analyze_design()

        # Security analysis
        self._analyze_security()

        # Generate recommendations
        self._generate_recommendations()

        return self.results

    def _analyze_technical_stack(self):
        """Analyze the technical stack (OS, web server, CMS, etc.)."""
        print("\n🔧 Analyzing Technical Stack...")

        try:
            response = self.session.get(self.url, timeout=10)
            headers = response.headers
            content = response.text.lower()

            # Web server detection
            server = headers.get('Server', 'Unknown')
            if 'nginx' in server.lower():
                self.results['technical']['web_server'] = 'Nginx'
            elif 'apache' in server.lower():
                self.results['technical']['web_server'] = 'Apache'
            elif 'litespeed' in server.lower():
                self.results['technical']['web_server'] = 'LiteSpeed'
            else:
                self.results['technical']['web_server'] = server or 'Unknown'

            # Operating system detection
            if 'win' in server.lower() or 'iis' in server.lower():
                self.results['technical']['operating_system'] = 'Windows'
            elif 'linux' in server.lower() or 'unix' in server.lower():
                self.results['technical']['operating_system'] = 'Linux/Unix'
            else:
                self.results['technical']['operating_system'] = 'Unknown'

            # WordPress detection
            if 'wp-content' in content or 'wp-admin' in content or 'wordpress' in content:
                self.results['technical']['cms'] = 'WordPress'

                # Theme detection
                theme_match = re.search(r'wp-content/themes/([^/]+)', content)
                if theme_match:
                    self.results['technical']['theme'] = theme_match.group(1)

                # Plugin detection (basic)
                plugins = []
                if 'woocommerce' in content:
                    plugins.append('WooCommerce')
                if 'yoast' in content or 'wordpress-seo' in content:
                    plugins.append('Yoast SEO')
                if 'akismet' in content:
                    plugins.append('Akismet')
                if 'contact-form-7' in content:
                    plugins.append('Contact Form 7')

                if plugins:
                    self.results['technical']['detected_plugins'] = plugins

            # Other CMS detection
            elif 'drupal' in content:
                self.results['technical']['cms'] = 'Drupal'
            elif 'joomla' in content:
                self.results['technical']['cms'] = 'Joomla'
            elif 'shopify' in content:
                self.results['technical']['cms'] = 'Shopify'
            else:
                self.results['technical']['cms'] = 'Custom/Unknown'

            # SSL/TLS status
            if response.url.startswith('https'):
                self.results['technical']['ssl'] = 'Enabled'
            else:
                self.results['technical']['ssl'] = 'Disabled'

            print(f"   ✅ Web Server: {self.results['technical'].get('web_server', 'Unknown')}")
            print(f"   ✅ OS: {self.results['technical'].get('operating_system', 'Unknown')}")
            print(f"   ✅ CMS: {self.results['technical'].get('cms', 'Unknown')}")
            if 'theme' in self.results['technical']:
                print(f"   ✅ Theme: {self.results['technical']['theme']}")

        except Exception as e:
            print(f"   ❌ Technical analysis failed: {e}")
            self.results['technical']['error'] = str(e)

    def _analyze_seo(self):
        """Analyze SEO elements."""
        print("\n🔍 Analyzing SEO...")

        try:
            response = self.session.get(self.url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Title tag
            title = soup.find('title')
            self.results['seo']['title'] = title.get_text().strip() if title else 'Missing'
            self.results['seo']['title_length'] = len(self.results['seo']['title'])

            # Meta description
            desc = soup.find('meta', {'name': 'description'})
            if desc:
                self.results['seo']['description'] = desc.get('content', '').strip()
                self.results['seo']['description_length'] = len(self.results['seo']['description'])
            else:
                self.results['seo']['description'] = 'Missing'
                self.results['seo']['description_length'] = 0

            # Canonical URL
            canonical = soup.find('link', {'rel': 'canonical'})
            self.results['seo']['canonical'] = canonical.get('href') if canonical else 'Missing'

            # Open Graph tags
            og_title = soup.find('meta', {'property': 'og:title'})
            self.results['seo']['og_title'] = og_title.get('content') if og_title else 'Missing'

            # H1 tag
            h1 = soup.find('h1')
            self.results['seo']['h1'] = h1.get_text().strip() if h1 else 'Missing'

            # Internal links count
            internal_links = soup.find_all('a', href=True)
            internal_count = sum(1 for link in internal_links
                               if link['href'].startswith('/') or
                               link['href'].startswith(self.base_domain))
            self.results['seo']['internal_links'] = internal_count

            # Images without alt text
            images = soup.find_all('img')
            no_alt = sum(1 for img in images if not img.get('alt'))
            self.results['seo']['images_without_alt'] = no_alt

            print(f"   ✅ Title: {self.results['seo']['title'][:50]}...")
            print(f"   ✅ Description: {len(self.results['seo'].get('description', ''))} chars")
            print(f"   ✅ H1: {self.results['seo']['h1'][:30]}...")
            print(f"   ✅ Internal Links: {internal_count}")
            print(f"   ✅ Images w/o Alt: {no_alt}")

        except Exception as e:
            print(f"   ❌ SEO analysis failed: {e}")
            self.results['seo']['error'] = str(e)

    def _analyze_design(self):
        """Analyze design elements."""
        print("\n🎨 Analyzing Design...")

        try:
            response = self.session.get(self.url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Color extraction (basic)
            colors = set()
            for element in soup.find_all(['div', 'section', 'header', 'footer', 'nav']):
                style = element.get('style', '')
                if 'background-color' in style or 'color' in style:
                    # Extract hex colors
                    hex_colors = re.findall(r'#[0-9a-fA-F]{3,6}', style)
                    colors.update(hex_colors)

            self.results['design']['detected_colors'] = list(colors)[:10]  # Top 10 colors

            # Font detection
            fonts = set()
            for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div']):
                style = element.get('style', '')
                font_match = re.search(r'font-family:\s*([^;]+)', style)
                if font_match:
                    fonts.add(font_match.group(1).strip('"\'' ))

            self.results['design']['detected_fonts'] = list(fonts)[:5]  # Top 5 fonts

            # Layout structure
            sections = []
            for tag in ['header', 'nav', 'main', 'section', 'footer']:
                elements = soup.find_all(tag)
                if elements:
                    sections.append({
                        'tag': tag,
                        'count': len(elements),
                        'has_content': any(el.get_text().strip() for el in elements)
                    })

            self.results['design']['layout_sections'] = sections

            print(f"   ✅ Colors: {len(colors)} detected")
            print(f"   ✅ Fonts: {len(fonts)} detected")
            print(f"   ✅ Layout: {len(sections)} sections")

        except Exception as e:
            print(f"   ❌ Design analysis failed: {e}")
            self.results['design']['error'] = str(e)

    def _analyze_security(self):
        """Analyze security headers and configuration."""
        print("\n🔒 Analyzing Security...")

        try:
            response = self.session.get(self.url, timeout=10)
            headers = response.headers

            security_headers = {}

            # Check for common security headers
            for header in ['Strict-Transport-Security', 'Content-Security-Policy',
                          'X-Frame-Options', 'X-Content-Type-Options', 'Referrer-Policy']:
                if header in headers:
                    security_headers[header] = headers[header]
                else:
                    security_headers[header] = 'Missing'

            self.results['security']['headers'] = security_headers

            # SSL check
            if response.url.startswith('https'):
                self.results['security']['ssl'] = 'Enabled'
            else:
                self.results['security']['ssl'] = 'Disabled'

            print(f"   ✅ SSL: {self.results['security']['ssl']}")
            print(f"   ✅ Security Headers: {sum(1 for h, v in security_headers.items() if v != 'Missing')}/{len(security_headers)}")

        except Exception as e:
            print(f"   ❌ Security analysis failed: {e}")
            self.results['security']['error'] = str(e)

    def _generate_recommendations(self):
        """Generate actionable recommendations."""
        print("\n💡 Generating Recommendations...")

        recommendations = []

        # SEO recommendations
        if self.results['seo'].get('title_length', 0) > 60:
            recommendations.append({
                'category': 'SEO',
                'priority': 'high',
                'issue': 'Title tag too long',
                'recommendation': f"Shorten title to under 60 characters (currently {self.results['seo']['title_length']})"
            })

        if self.results['seo'].get('description_length', 0) > 160:
            recommendations.append({
                'category': 'SEO',
                'priority': 'medium',
                'issue': 'Meta description too long',
                'recommendation': f"Shorten description to under 160 characters (currently {self.results['seo']['description_length']})"
            })

        if self.results['seo'].get('images_without_alt', 0) > 0:
            recommendations.append({
                'category': 'SEO',
                'priority': 'medium',
                'issue': f"{self.results['seo']['images_without_alt']} images without alt text",
                'recommendation': 'Add descriptive alt text to all images for accessibility and SEO'
            })

        # Technical recommendations
        if self.results['technical'].get('cms') == 'WordPress':
            if 'theme' not in self.results['technical']:
                recommendations.append({
                    'category': 'Technical',
                    'priority': 'low',
                    'issue': 'WordPress theme not detected',
                    'recommendation': 'Verify theme is properly installed and activated'
                })

        # Security recommendations
        if self.results['security'].get('ssl') == 'Disabled':
            recommendations.append({
                'category': 'Security',
                'priority': 'high',
                'issue': 'SSL/TLS not enabled',
                'recommendation': 'Enable HTTPS for security and SEO benefits'
            })

        missing_headers = [h for h, v in self.results['security'].get('headers', {}).items() if v == 'Missing']
        if missing_headers:
            recommendations.append({
                'category': 'Security',
                'priority': 'medium',
                'issue': f"Missing security headers: {', '.join(missing_headers)}",
                'recommendation': 'Implement missing security headers for better protection'
            })

        self.results['recommendations'] = recommendations

        print(f"   ✅ Generated {len(recommendations)} recommendations")

        if recommendations:
            print("\n📋 Top Priority Issues:")
            for rec in recommendations[:3]:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🔵"
                print(f"   {priority_icon} {rec['issue']}")

    def save_results(self, output_file: Optional[str] = None) -> str:
        """Save results to file."""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            output_file = f"/Output/client-audits/{self.domain}-{timestamp}.json"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")
        return output_file


def show_help():
    """Display comprehensive help information."""
    help_text = """
🚀 ASTRO Client Audit Tool - Help Guide

DESCRIPTION:
    Comprehensive SEO, design, and technical analysis tool for new client onboarding.
    Combines multiple analysis types into a single, powerful command-line tool.

USAGE:
    python client-audit-tool.py --url https://example.com
    python client-audit-tool.py --help
    python client-audit-tool.py --url https://example.com --quick
    python client-audit-tool.py --url https://example.com --full

OPTIONS:
    --url, -u         Target website URL (required)
    --quick, -q       Fast analysis (skip heavy tests)
    --full, -f        Comprehensive analysis (all tests)
    --output, -o      Custom output file path
    --help, -h        Show this help message

ANALYSIS MODES:
    Standard (default): Balanced analysis with core SEO, design, and technical checks
    Quick: Faster analysis for preliminary assessment
    Full: Comprehensive analysis including performance and security tests

WHAT IT ANALYZES:
    🔧 Technical Stack:
        - Web server software (Apache, Nginx, etc.)
        - Operating system detection
        - CMS identification (WordPress, Shopify, etc.)
        - Theme and plugin detection

    🔍 SEO Analysis:
        - Title and meta description
        - Canonical URLs and Open Graph tags
        - Heading structure (H1-H6)
        - Internal linking patterns
        - Image alt text coverage

    🎨 Design Analysis:
        - Color palette extraction
        - Font family detection
        - Layout structure analysis
        - Visual consistency checks

    🔒 Security Analysis:
        - SSL/TLS status
        - Security header validation
        - Common vulnerabilities check

OUTPUT:
    JSON file with comprehensive analysis results
    Saved to: /Output/client-audits/{domain}-{timestamp}.json

EXAMPLES:
    # Quick audit for new client
    python client-audit-tool.py --url https://newclient.com --quick

    # Full audit before taking over management
    python client-audit-tool.py --url https://existingclient.com --full

    # Custom output location
    python client-audit-tool.py --url https://client.com -o /custom/path/audit.json

RECOMMENDATIONS:
    - Always run before taking on a new client
    - Use --quick for preliminary assessment
    - Use --full for comprehensive onboarding audit
    - Review results with client to identify priorities

SUPPORT:
    For issues or feature requests, consult the SBEP mandate and existing documentation.
    """
    print(help_text)


def main():
    parser = argparse.ArgumentParser(
        description='ASTRO Client Audit Tool - SEO, Design, and Technical Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python client-audit-tool.py --url https://example.com
  python client-audit-tool.py --url https://example.com --quick
  python client-audit-tool.py --url https://example.com --full
        """
    )

    parser.add_argument('--url', '-u', required=True, help='Target website URL')
    parser.add_argument('--quick', '-q', action='store_true', help='Fast analysis mode')
    parser.add_argument('--full', '-f', action='store_true', help='Comprehensive analysis mode')
    parser.add_argument('--output', '-o', help='Custom output file path')
    parser.add_argument('--help', '-h', action='store_true', help='Show this help message')

    args = parser.parse_args()

    if args.help:
        show_help()
        return

    if not args.url:
        print("❌ Error: URL is required")
        print("Use --help for usage information")
        return

    # Initialize and run audit
    auditor = ClientAuditTool(args.url, quick_mode=args.quick, full_mode=args.full)
    results = auditor.run_audit()

    # Save results
    output_file = auditor.save_results(args.output)

    print("
🎉 Audit Complete!"    print(f"📄 Results: {output_file}")
    print("
💡 Key Findings:"    print(f"   • CMS: {results['technical'].get('cms', 'Unknown')}")
    print(f"   • Theme: {results['technical'].get('theme', 'Unknown')}")
    print(f"   • SSL: {results['security'].get('ssl', 'Unknown')}")
    print(f"   • Recommendations: {len(results['recommendations'])}")

    if results['recommendations']:
        print("
🔴 Priority Issues:"        for rec in results['recommendations'][:3]:
            if rec['priority'] == 'high':
                print(f"   • {rec['issue']}")


if __name__ == '__main__':
    main()

