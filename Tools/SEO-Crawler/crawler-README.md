# Simple Website Crawler

A lightweight, efficient Python CLI tool for crawling websites and extracting page information.

## Features

- ✅ Crawls internal links only (respects domain boundaries)
- ✅ Configurable depth limit
- ✅ Efficient (uses connection pooling)
- ✅ CSV export (URL, status code, page title)
- ✅ Graceful error handling
- ✅ Ctrl+C interrupt support (saves partial results)
- ✅ Prevents infinite loops (tracks visited URLs)
- ✅ Well-commented, production-ready code

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Crawl
```bash
# Crawl with default settings (depth=2, output=crawl_results.csv)
python crawler.py --url https://example.com
```

### Custom Depth
```bash
# Crawl 3 levels deep
python crawler.py --url https://example.com --depth 3
```

### Custom Output File
```bash
# Save to custom CSV file
python crawler.py --url https://example.com --output sitemap.csv
```

### Crawl Only Starting Page
```bash
# Depth 0 = no link following
python crawler.py --url https://example.com --depth 0
```

### Full Options
```bash
python crawler.py --url https://yoursite.com --depth 3 --output full_sitemap.csv
```

## Command-Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--url` | Yes | - | Starting URL to crawl (must include http:// or https://) |
| `--depth` | No | 2 | Maximum crawl depth (0 = only start page) |
| `--output` | No | `crawl_results.csv` | Output CSV filename |

## Output Format

The crawler generates a CSV file with three columns:

| Column | Description |
|--------|-------------|
| `url` | The full URL of the crawled page |
| `status_code` | HTTP status code (200, 404, etc.) or "ERROR" if request failed |
| `title` | Page title from the `<title>` tag |

### Example Output
```csv
url,status_code,title
https://example.com,200,Example Domain
https://example.com/about,200,About Us - Example
https://example.com/contact,200,Contact Us
https://example.com/products,404,
```

## How It Works

1. **Initialization:** Parses the starting URL to determine the base domain
2. **Queue Processing:** Uses breadth-first search (BFS) with a queue
3. **URL Normalization:** Converts relative links to absolute, removes fragments
4. **Visited Tracking:** Maintains a set of visited URLs to prevent duplicates
5. **Depth Limiting:** Tracks depth for each URL and respects max depth
6. **Internal Link Filter:** Only follows links on the same domain
7. **Data Extraction:** Fetches HTTP status and page title
8. **CSV Export:** Writes results to file

## Error Handling

- **Network Errors:** Logged to console, crawler continues with other pages
- **Timeout:** 10-second timeout per request (configurable in code)
- **Invalid HTML:** Handled gracefully with BeautifulSoup
- **Ctrl+C:** Saves partial results before exiting
- **Fatal Errors:** Attempts to save partial results before exit

## Best Practices Implemented

- ✅ **Connection Pooling:** Uses `requests.Session()` for efficiency
- ✅ **User-Agent:** Sets custom User-Agent header
- ✅ **URL Normalization:** Prevents duplicate crawls of same page
- ✅ **Fragment Removal:** Ignores URL fragments (#section)
- ✅ **Type Safety:** Uses type hints throughout
- ✅ **Separation of Concerns:** Class-based design with clear methods
- ✅ **Comprehensive Comments:** Well-documented code
- ✅ **Resource Management:** Proper cleanup and error handling

## Customization Options

### Increase Timeout
Edit line 27 in `crawler.py`:
```python
def __init__(self, start_url: str, max_depth: int = 2, timeout: int = 30):  # Changed from 10 to 30
```

### Add Rate Limiting
Add `time.sleep()` in the crawl loop:
```python
import time

# In crawl_page method, after successful request:
time.sleep(0.5)  # Wait 500ms between requests
```

### Change User-Agent
Edit line 49-51 in `crawler.py`:
```python
self.session.headers.update({
    'User-Agent': 'YourCustomBot/1.0'
})
```

## Limitations

- Only crawls links in `<a href="">` tags (not JavaScript-generated links)
- Only processes text/html content types
- No JavaScript execution (use Selenium/Playwright for SPA sites)
- No authentication support (add session cookies if needed)
- No robots.txt checking (add if crawling third-party sites)

## Dependencies

- **requests** (>=2.32.0): HTTP library
- **beautifulsoup4** (>=4.12.0): HTML parser

## Examples

### Crawl a Blog
```bash
python crawler.py --url https://yourblog.com --depth 2 --output blog_sitemap.csv
```

### Crawl Documentation Site
```bash
python crawler.py --url https://docs.example.com --depth 4 --output docs_structure.csv
```

### Quick Site Check
```bash
# Just check homepage and immediate links
python crawler.py --url https://example.com --depth 1
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install -r requirements.txt
```

### Slow Crawling
- Reduce `--depth` to crawl fewer pages
- Check network connection
- Site may have rate limiting

### Empty Output
- Check if site has internal links
- Try increasing `--depth`
- Verify URL is accessible

### SSL Errors
Site may have SSL certificate issues. To bypass (use cautiously):
```python
# In crawl_page method:
response = self.session.get(url, timeout=self.timeout, verify=False)
```

## License

Free to use and modify.

## Author

Created as a lightweight, production-ready CLI crawler tool.

