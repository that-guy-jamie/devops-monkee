# SEO Crawler & Website Analysis Tools

Comprehensive suite of tools for analyzing website SEO, performance, security, and mobile-friendliness.

## 🛠️ Tools Overview

### 1. **Advanced Crawler** (`advanced_crawler.py`)
Complete SEO audit with deep content analysis.

**Features:**
- robots.txt compliance
- Meta tag extraction (title, description, OG, Twitter)
- JSON-LD structured data parsing
- Heading hierarchy (H1-H6)
- Image analysis (src, alt, title)
- Link classification (internal/outbound)
- Indexability detection (noindex, X-Robots-Tag)

**Usage:**
```bash
python advanced_crawler.py --url https://example.com/ --depth 2 --output audit.json
```

### 2. **SEO Summary** (`seo_summary.py`)
Generate human-readable reports from crawler output.

**Usage:**
```bash
python seo_summary.py audit.json
```

### 3. **Audit Comparison** (`compare_audits.py`)
Compare before/after SEO improvements.

**Features:**
- Side-by-side metric comparison
- Coverage percentages
- Improvement tracking
- Overall grade calculation

**Usage:**
```bash
python compare_audits.py before.json after.json
```

### 4. **Page Speed Test** (`page_speed_test.py`)
Measure load time and performance.

**Metrics:**
- HTTP status
- Load time
- Response size
- Headers analysis
- Performance features (compression, caching, CDN)
- Resource availability (sitemap, robots.txt, favicon)

**Usage:**
```bash
python page_speed_test.py https://example.com/
```

### 5. **Security Headers Test** (`security_headers_test.py`)
Audit security posture.

**Checks:**
- HSTS
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Content-Security-Policy
- Referrer-Policy
- Permissions-Policy
- SSL/TLS certificate validity

**Usage:**
```bash
python security_headers_test.py https://example.com/
```

### 6. **Mobile-Friendly Test** (`mobile_friendly_test.py`)
Evaluate responsive design.

**Indicators:**
- Viewport meta tag
- CSS framework detection
- Touch icons
- Mobile meta tags
- Responsive CSS

**Usage:**
```bash
python mobile_friendly_test.py https://example.com/
```

---

## 📊 Complete Website Audit

Run all tools for comprehensive analysis:

```powershell
# Full audit suite
cd Tools\SEO-Crawler

# 1. SEO Audit
python advanced_crawler.py --url https://example.com/ --depth 2 --output full_audit.json
python seo_summary.py full_audit.json

# 2. Performance
python page_speed_test.py https://example.com/

# 3. Security
python security_headers_test.py https://example.com/

# 4. Mobile
python mobile_friendly_test.py https://example.com/
```

---

## 📁 Output Files

- `*.json` - Structured SEO data
- Console output - Human-readable reports

---

## 🎯 Use Cases

**Before Deployment:**
- Baseline SEO audit
- Security header review
- Performance benchmark

**After Changes:**
- Compare before/after (`compare_audits.py`)
- Verify meta tag updates
- Check schema markup

**Regular Monitoring:**
- Weekly crawls
- Track SEO score trends
- Monitor page speed

---

## 📦 Dependencies

```bash
pip install requests beautifulsoup4
```

---

## 🚀 Quick Start

```bash
# Install
pip install requests beautifulsoup4

# Run full audit on theastro.org
cd Tools\SEO-Crawler
python advanced_crawler.py --url https://theastro.org/ --depth 2 --output astro_audit.json
python seo_summary.py astro_audit.json
python page_speed_test.py https://theastro.org/
python security_headers_test.py https://theastro.org/
python mobile_friendly_test.py https://theastro.org/
```

---

## 📈 Interpreting Results

### SEO Grade Scale
- **A+ (95-100%)**: Excellent SEO
- **A (90-94%)**: Very Good SEO
- **B+ (85-89%)**: Good SEO
- **B (80-84%)**: Fair SEO
- **C (70-79%)**: Needs Improvement
- **D (<70%)**: Poor SEO

### Page Speed
- **<1s**: Excellent 🚀
- **1-2s**: Good ✅
- **2-3s**: Fair 🟡
- **3-5s**: Slow ⚠️
- **>5s**: Very Slow ❌

### Security Score
- **≥80%**: Good security posture 🟢
- **50-79%**: Moderate security 🟡
- **<50%**: Weak security headers 🔴

---

## 🔧 Helper Scripts Location

PHP helper scripts (WordPress integration):
- `helpers/import-to-wordpress.php`
- `helpers/update-seo-images.php`
- `helpers/configure-seo.php`

---

## 📝 Notes

- Crawler respects `robots.txt`
- Default depth: 2 levels
- JSON output is UTF-8 encoded
- All tools have `--help` flag for options

---

**Created:** 2025-10-09  
**Last Updated:** 2025-10-10  
**Version:** 1.1.0
