# Tools Directory

**Location:** `/Tools/`  
**Purpose:** Centralized repository for development tools, scripts, and utilities  
**Output Location:** `/Output/` (organized by tool category)

---

## Overview

The Tools directory contains organized, reusable tools for various development tasks including SEO analysis, image processing, design analysis, and system management.

## Tool Categories

### 🚀 Client Audit Tool (NEW)
**Location:** `/Tools/client-audit-tool.py`  
**Purpose:** Combined SEO, design, and technical analysis for new client onboarding  
**Output:** `/Output/client-audits/`

**The Complete Solution:** Combines SEO crawling, design analysis, and technical stack detection into a single powerful tool for client support.

**Quick Start:**
```bash
cd /Tools
python client-audit-tool.py --url https://newclient.com
```

**Features:**
- SEO analysis (titles, meta, links, images)
- Design pattern extraction (colors, fonts, layout)
- Technical stack detection (CMS, themes, plugins, security)
- Built-in help system (`--help`)
- Multiple analysis modes (`--quick`, `--full`)
- Client-ready recommendations

**Why Combined:** For new clients, you need **all three** types of analysis in one tool:
- **SEO:** What needs fixing for search rankings
- **Design:** Visual consistency and branding
- **Technical:** What's the stack and security posture

**Output:** `/Output/client-audits/{domain}-{timestamp}.json`

---

### 🔍 SEO Tools
**Location:** `/Tools/seo-tools/`  
**Purpose:** SEO analysis, crawling, and auditing  
**Output:** `/Output/seo-audits/`

**Available Tools:**
- **SEO Crawler** - Comprehensive website auditing and analysis

**Quick Start:**
```bash
cd /Tools/seo-tools/crawler
python advanced_crawler.py --url https://example.com
```

**Results:** Check `/Output/seo-audits/{site-name}/` for audit files

---

### 🖼️ Image Tools
**Location:** `/Tools/image-tools/`  
**Purpose:** Image downloading, optimization, and processing  
**Output:** `/Output/processed-images/`

**Available Tools:**
- **ASTRO Images** - Image optimization and Pexels integration

**Quick Start:**
```bash
cd /Tools/image-tools/astro-images/scripts
python optimize-astro-images.py
```

**Results:** Check `/Output/processed-images/{project}/` for processed images

---

### 🎨 Design Tools
**Location:** `/Tools/design-tools/`  
**Purpose:** Design analysis and UI/UX tools  
**Output:** `/Output/design-analysis/` (when applicable)

**Available Tools:**
- **Design Analysis** - Extract and analyze design elements
- **Design Scanner** - JavaScript-based design scanner

**Quick Start:**
```bash
cd /Tools/design-tools/design-scanner
node design-scanner.js https://example.com
```

---

## Output Organization Strategy

### Centralized Output Location
All important tool outputs are saved to `/Output/` organized by tool category:

```
/Output/
├── seo-audits/
│   ├── astro/
│   ├── site-a/
│   └── site-b/
├── processed-images/
│   ├── astro/
│   └── other-projects/
└── design-analysis/
    └── {project}/
```

### Output Naming Conventions

**SEO Audits:**
- Format: `{domain}-{audit-type}-{date}.{ext}`
- Example: `theastro-seo-audit-2025-10-18.json`

**Processed Images:**
- Structure: `{project}/original/` and `{project}/optimized/`
- Descriptive names: `astro-homepage-og.jpg`

**Design Analysis:**
- Format: `{project}-design-data-{date}.json`
- Screenshots: `{project}-screenshot-{date}.png`

### Local Tool Outputs
Tools may keep test/development outputs locally:
- `.tmp/` - Temporary test files
- `output/` - Quick reference outputs
- These are not moved to `/Output/` unless important

---

## Finding Your Outputs

After running any tool, your results will be in:

**✅ Important Results:** `/Output/{category}/{project}/`
**🔬 Test/Debug Files:** `{tool}/.tmp/` or `{tool}/output/`

**Quick Check:**
```powershell
# See all SEO audits
dir C:\Users\james\Desktop\Projects\Output\seo-audits\astro

# See all processed images
dir C:\Users\james\Desktop\Projects\Output\processed-images\astro
```

---

## Tool Development Guidelines

### Creating a New Tool

1. **Choose Category:** SEO, Image, Design, or create new category
2. **Create Structure:**
   ```
   /Tools/{category}/{tool-name}/
   ├── README.md          # Tool documentation
   ├── {scripts}          # Tool files
   ├── .tmp/             # Temporary outputs
   └── requirements.txt   # Dependencies (if needed)
   ```

3. **Configure Output:** Point to `/Output/{category}/{project}/`

4. **Naming Convention:** Follow category-specific conventions

5. **Update Indexes:** Add to category README and this master README

### Tool README Template

Every tool should have a README.md with:
- **Purpose:** What the tool does
- **Installation:** How to set it up
- **Usage:** How to run it with examples
- **Output Location:** Where results are saved
- **Configuration:** Any customization options
- **End Message:** Direct users to output folder

**Example End Message:**
```markdown
## After Running

**✅ Your results are saved in:** `/Output/seo-audits/astro/`

Navigate there to find your latest audit files.
```

---

## Integration with SBEP

### Housekeeping
After using tools, run housekeeping to organize:
```powershell
.\SBEP_Core\Invoke-ProjectHousekeeping.ps1
```

**What it does:**
- Moves temporary files to `.tmp/` folders
- Keeps `/Output/` clean and organized
- Archives obsolete results

### Temporary Files
Write test outputs to:
- `{tool}/.tmp/` for tool-specific tests
- `/. tmp/` for cross-tool tests

---

## Quick Reference

| Task | Command | Output Location |
|------|---------|----------------|
| **Client Audit** | `cd /Tools && python client-audit-tool.py --url URL` | `/Output/client-audits/{domain}/` |
| SEO Audit | `cd /Tools/seo-tools/crawler && python advanced_crawler.py --url URL` | `/Output/seo-audits/{site}/` |
| Optimize Images | `cd /Tools/image-tools/astro-images/scripts && python optimize-astro-images.py` | `/Output/processed-images/{project}/` |
| Design Scan | `cd /Tools/design-tools/design-scanner && node design-scanner.js URL` | Tool folder or `/Output/design-analysis/` |

**Note:** The Client Audit Tool combines SEO, design, and technical analysis into one comprehensive command for new client onboarding.

---

## Maintenance

### Monthly Review
- Check `/Output/` for outdated files
- Archive old audits if no longer needed
- Update tool documentation
- Review naming conventions

### Adding Categories
When adding a new tool category:

1. Create `/Tools/{new-category}/` directory
2. Create category `README.md`
3. Create `/Output/{new-category}/` structure
4. Update this master README
5. Define naming conventions for category
6. Update SBEP housekeeping if needed

---

## Related Documentation

- **SBEP Manifest:** `/SBEP-MANIFEST.md` - Protocol and guidelines
- **Housekeeping SOP:** `/SBEP_Core/HOUSEKEEPING-SOP.md` - Cleanup procedures
- **Output Folder:** `/Output/README.md` (if exists) - Output organization

---

## Support

For questions about:
- **Tool Usage:** Check tool-specific README in tool folder
- **Output Organization:** See this README
- **SBEP Compliance:** See `/SBEP-MANIFEST.md`
- **Housekeeping:** See `/SBEP_Core/HOUSEKEEPING-SOP.md`

---

**Remember:** All important outputs go to `/Output/{category}/` for easy access and backup! 🎯






