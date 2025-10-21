# Headcore Add-on (Apply Fixes)

**Purpose**: convert Audit Monkee findings → versioned site config and inject `<head>` best practices.

## Config (signed JSON; Ed25519)
```json
{
  "site": "https://example.com",
  "generated_at": "2025-10-21T17:05:00Z",
  "version": "1.0.0",
  "seo": {
    "title_pattern": "%page_title% | Brand",
    "canonical": true,
    "robots": "index,follow",
    "hreflang": [{"lang":"en","href":"https://example.com/"}]
  },
  "social": {
    "og": {"type":"website","image":"https://cdn.example.com/og.jpg"},
    "twitter": {"card":"summary_large_image"}
  },
  "structured_data": [
    {"@context":"https://schema.org","@type":"Organization","name":"Brand","url":"https://example.com"}
  ],
  "performance": {
    "preconnect": ["https://fonts.gstatic.com","https://cdn.example.com"],
    "preload": [{"href":"/fonts/brand.woff2","as":"font","type":"font/woff2","crossorigin":"anonymous"}],
    "critical_css_url": "https://cdn.example.com/crit/home.css"
  },
  "security": {
    "csp": "default-src 'self'; img-src 'self' https: data:; style-src 'self' 'unsafe-inline' https:; script-src 'self' https:"
  },
  "signature": "base64url-ed25519"
}
```

## Rules Map (examples)
- `MISSING_CANONICAL` → `seo.canonical = true`
- `OG_IMAGE_MISSING` → merge default OG image & type
- `LCP_IMAGE_NOT_PRELOADED` → append preload for `{lcp_src}`
