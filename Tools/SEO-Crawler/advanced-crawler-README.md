# Advanced SEO & Content Analysis Crawler

A comprehensive Python CLI tool for crawling websites with full SEO analysis, robots.txt compliance, and AI-ready JSON output.

## Features

### Crawling Etiquette
- ✅ **Respects robots.txt** - Fetches and parses before crawling
- ✅ **Honors noindex directives** - Detects and respects meta robots tags
- ✅ **Same-domain only** - Won't crawl external sites
- ✅ **Configurable depth** - Control how deep to crawl
- ✅ **Custom user-agent** - Identify your crawler

### SEO Data Extraction
- ✅ **Title tags** - Page titles
- ✅ **Meta descriptions** - SEO descriptions
- ✅ **Canonical URLs** - Duplicate content detection
- ✅ **Open Graph tags** - Social media metadata (og:title, og:image, etc.)
- ✅ **All meta tags** - Complete metadata inventory
- ✅ **Language detection** - HTML lang attribute

### Content Analysis
- ✅ **Heading hierarchy** - H1 through H6 extraction
- ✅ **Image inventory** - All images with src, alt, title
- ✅ **JSON-LD extraction** - Structured data schemas
- ✅ **Link analysis** - Internal vs outbound link classification

### Output
- ✅ **JSON format** - AI-ready structured data
- ✅ **Comprehensive schema** - All data in one place
- ✅ **Pretty-printed** - Human-readable JSON
- ✅ **Timestamped** - ISO 8601 crawl timestamps

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic SEO Audit
```bash
python advanced_crawler.py --url https://yoursite.com
```

### Deep Crawl
```bash
python advanced_crawler.py --url https://yoursite.com --depth 4 --output full_audit.json
```

### Custom User-Agent
```bash
python advanced_crawler.py --url https://site.com --user-agent "MySEOBot/1.0"
```

### Single Page Analysis
```bash
python advanced_crawler.py --url https://site.com/page --depth 0
```

## Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--url` | Yes | - | Starting URL (must include http:// or https://) |
| `--depth` | No | 2 | Maximum crawl depth (0 = only start page) |
| `--output` | No | `advanced_crawl.json` | Output JSON filename |
| `--user-agent` | No | `SimpleSEOCrawler/2.0` | User-agent string |

## JSON Output Schema

### Complete Page Object
```json
{
  "url": "https://example.com",
  "crawled_at_utc": "2025-10-09T19:30:00.000000",
  "http_status_code": 200,
  "is_indexable": true,
  "metadata": {
    "title": "Example Domain",
    "meta_description": "Example description...",
    "canonical_url": "https://example.com",
    "og_tags": {
      "og:title": "Example Domain",
      "og:description": "...",
      "og:image": "https://example.com/image.jpg"
    },
    "all_meta_tags": [
      {"name": "viewport", "content": "width=device-width"},
      {"name": "keywords", "content": "example, domain"}
    ]
  },
  "content": {
    "language": "en",
    "headings": {
      "h1": ["Main Heading"],
      "h2": ["Subheading 1", "Subheading 2"],
      "h3": [],
      "h4": [],
      "h5": [],
      "h6": []
    },
    "images": [
      {
        "src": "https://example.com/image.jpg",
        "alt": "Image description",
        "title": "Image title"
      }
    ],
    "structured_data_json_ld": [
      {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Example"
      }
    ]
  },
  "links": {
    "total_internal_links": 5,
    "total_outbound_links": 2,
    "internal_links": [
      "https://example.com/about",
      "https://example.com/contact"
    ],
    "outbound_links": [
      "https://external-site.com"
    ]
  }
}
```

## How It Works

### 1. Initialization
- Parses starting URL to determine domain
- Loads robots.txt for the domain
- Sets up session with custom user-agent

### 2. Robots.txt Respect
- Fetches `/robots.txt` from domain
- Parses using `urllib.robotparser`
- Checks `can_fetch()` before each URL
- Skips disallowed URLs

### 3. Page Crawling
- Fetches HTML content
- Checks for noindex directives
- Extracts comprehensive metadata
- Parses content structure
- Classifies all links

### 4. Noindex Handling
- Detects `<meta name="robots" content="noindex">`
- Detects `X-Robots-Tag: noindex` header
- Sets `is_indexable: false`
- Scrapes data but doesn't follow links

### 5. Data Extraction
- **Metadata:** All meta tags, OG tags, canonical
- **Content:** Headings, images, JSON-LD
- **Links:** Internal vs outbound classification
- **Status:** HTTP code, indexability

### 6. JSON Export
- Structured output matching schema
- ISO 8601 timestamps
- Pretty-printed (indent=2)
- UTF-8 encoding

## Use Cases

### SEO Audit
```bash
# Crawl entire site for SEO analysis
python advanced_crawler.py --url https://yoursite.com --depth 3 --output seo_audit.json

# Analyze with jq
cat seo_audit.json | jq '.[] | select(.metadata.title == "") | .url'
# Find pages with missing titles
```

### Content Inventory
```bash
# Build complete content map
python advanced_crawler.py --url https://docs.site.com --depth 5 --output content_map.json

# Extract all H1s
cat content_map.json | jq '.[] | {url, h1: .content.headings.h1}'
```

### AI Analysis
```bash
# Crawl site for AI processing
python advanced_crawler.py --url https://site.com --depth 3

# Feed to AI agent
cat advanced_crawl.json  # AI can analyze structure, find issues, recommend changes
```

### Structured Data Audit
```bash
# Find all pages with JSON-LD
cat advanced_crawl.json | jq '.[] | select(.content.structured_data_json_ld | length > 0)'
```

### Link Analysis
```bash
# Pages with most internal links
cat advanced_crawl.json | jq 'sort_by(-.links.total_internal_links) | .[0:10] | .[] | {url, links: .links.total_internal_links}'
```

## Error Handling

### Robots.txt Issues
- **Missing robots.txt:** Proceeds with crawl (logs warning)
- **Malformed robots.txt:** Catches errors, proceeds
- **Network error:** Logs and continues

### Page Errors
- **Timeout:** Logs error, marks status as "ERROR", continues
- **404/500 errors:** Records status code, doesn't parse
- **Non-HTML:** Records status, skips parsing
- **Malformed HTML:** BeautifulSoup handles gracefully

### Interruption
- **Ctrl+C:** Saves all data collected so far
- **Fatal error:** Attempts to save partial results
- **Network outage:** Continues with accessible pages

## Comparison: Basic vs Advanced Crawler

| Feature | Basic Crawler | Advanced Crawler |
|---------|--------------|------------------|
| Output Format | CSV | JSON |
| Data Fields | 3 (url, status, title) | 20+ fields |
| robots.txt | No | Yes ✅ |
| Noindex Detection | No | Yes ✅ |
| Meta Tags | Title only | All meta tags ✅ |
| Open Graph | No | Yes ✅ |
| Headings | No | H1-H6 ✅ |
| Images | No | Full inventory ✅ |
| JSON-LD | No | Yes ✅ |
| Link Classification | No | Internal/Outbound ✅ |
| Canonical URLs | No | Yes ✅ |
| Language Detection | No | Yes ✅ |

## SEO Checks You Can Perform

### Missing Metadata
```bash
# Pages without meta description
cat audit.json | jq '.[] | select(.metadata.meta_description == "") | .url'

# Pages without title
cat audit.json | jq '.[] | select(.metadata.title == "") | .url'
```

### Duplicate Content
```bash
# Group by title (potential duplicates)
cat audit.json | jq 'group_by(.metadata.title) | .[] | select(length > 1)'
```

### Image Optimization
```bash
# Images without alt text
cat audit.json | jq '.[] | .content.images[] | select(.alt == "")'
```

### Heading Structure
```bash
# Pages without H1
cat audit.json | jq '.[] | select(.content.headings.h1 | length == 0) | .url'

# Pages with multiple H1s
cat audit.json | jq '.[] | select(.content.headings.h1 | length > 1) | {url, h1s: .content.headings.h1}'
```

### Indexability Issues
```bash
# Non-indexable pages
cat audit.json | jq '.[] | select(.is_indexable == false)'
```

## Advanced Features

### Robots.txt Compliance
The crawler automatically:
1. Fetches `/robots.txt` from domain
2. Parses user-agent rules
3. Checks each URL before crawling
4. Skips disallowed URLs
5. Logs skipped URLs

### Noindex Detection
Checks both:
- `<meta name="robots" content="noindex">`
- `X-Robots-Tag: noindex` HTTP header

Pages marked noindex:
- Are scraped for data
- Are marked `is_indexable: false`
- Do NOT have their links followed

### Structured Data Extraction
Finds and parses:
- `<script type="application/ld+json">` tags
- Validates JSON
- Includes raw parsed data in output
- Useful for schema.org analysis

## Performance

### Speed
- ~1-2 seconds per page
- Connection pooling (efficient)
- Handles 500+ pages easily

### Memory
- Streaming results to JSON
- Efficient HTML parsing
- Suitable for large sites

### Limits
- Default timeout: 10 seconds per page
- No JavaScript execution (static HTML only)
- No browser rendering (use Selenium for SPAs)

## Troubleshooting

### "Robots.txt disallows crawling"
- Your user-agent is blocked in robots.txt
- Use custom user-agent: `--user-agent "MyBot/1.0"`
- Or check site's robots.txt policy

### Slow Crawling
- Reduce depth: `--depth 2`
- Check network speed
- Site may be slow to respond

### Empty JSON Output
- Check if site allows crawling (robots.txt)
- Verify URL is accessible
- Check for noindex on start page

### Memory Issues on Large Sites
- Reduce depth
- Crawl sections separately
- Process results incrementally

## Best Practices

### Respectful Crawling
1. Use identifiable user-agent
2. Respect robots.txt always
3. Add rate limiting for large crawls
4. Don't crawl too frequently

### Rate Limiting (Manual Addition)
```python
# Add to crawl_page method:
import time
time.sleep(1)  # Wait 1 second between requests
```

### Custom User-Agent
```bash
python advanced_crawler.py --url https://site.com --user-agent "MyCompany SEO Audit Bot/1.0; contact@company.com"
```

## Dependencies

- **requests** (>=2.32.0) - HTTP library
- **beautifulsoup4** (>=4.12.0) - HTML/XML parser
- **urllib.robotparser** (stdlib) - robots.txt parsing
- **json** (stdlib) - JSON handling
- **datetime** (stdlib) - Timestamps

## Example Output Analysis

### Find SEO Issues
```python
import json

# Load results
with open('seo_audit.json') as f:
    pages = json.load(f)

# Check for issues
for page in pages:
    issues = []
    
    if not page['metadata']['title']:
        issues.append('Missing title')
    
    if not page['metadata']['meta_description']:
        issues.append('Missing meta description')
    
    if len(page['content']['headings']['h1']) == 0:
        issues.append('No H1 tag')
    
    if len(page['content']['headings']['h1']) > 1:
        issues.append('Multiple H1 tags')
    
    if issues:
        print(f"\n{page['url']}")
        for issue in issues:
            print(f"  - {issue}")
```

## License

Free to use and modify.

## Changelog

**v2.0** (2025-10-09)
- Advanced SEO crawler with full metadata extraction
- robots.txt compliance
- noindex detection
- JSON-LD structured data parsing
- Link classification
- JSON output

**v1.0** (2025-10-09)
- Basic crawler with CSV output

---

**Built for SEO professionals, content strategists, and AI agents.** 🚀

