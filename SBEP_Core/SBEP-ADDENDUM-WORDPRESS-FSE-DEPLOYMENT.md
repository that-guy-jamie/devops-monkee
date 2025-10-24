# SBEP Addendum: WordPress FSE Design-Blueprint Deployment
**SBEP v2.2 Compliance Document**  
**Purpose:** Proven process for deploying beautiful WordPress Full Site Editing implementations  
**Validated:** 2025-10-24 on ownersnetworkd.wpengine.com

---

## Critical Discovery: Pattern Rendering Issue

### THE PROBLEM
WordPress FSE patterns referenced in templates often show as HTML comments instead of rendering:
```html
<!-- wp:pattern {"slug":"astro/section-hero"} /-->
```

**SYMPTOMS:**
- Site technically works (child theme active, CSS loaded)
- Design appears bland with minimal visual elements
- Pattern files exist but don't render in templates
- Technical validation passes but site "isn't pretty"

### THE SOLUTION
**Replace pattern references with inline pattern content in critical templates**

**❌ Pattern Reference (unreliable):**
```html
<!-- wp:pattern {"slug":"astro/section-hero"} /-->
```

**✅ Inline Content (guaranteed):**
```html
<section class="wp-block-group alignfull has-white-background-color">
  <h1 class="wp-block-heading has-4-xl-font-size">Swap Your Property, Expand Your World</h1>
  <!-- actual hero content here -->
</section>
```

**IMPACT:** Site transformation from "technically working but bland" to "visually stunning"

---

## Proven Deployment Process

### Phase 1: Technical Foundation (SCP Method)
```powershell
# Core theme files - 100% reliable
scp -O -P 22 -i ~/.ssh/key theme.json user@host:/path/
scp -O -P 22 -i ~/.ssh/key style.css user@host:/path/  
scp -O -P 22 -i ~/.ssh/key functions.php user@host:/path/

# Supporting assets
scp -O -P 22 -i ~/.ssh/key -r patterns/ user@host:/path/
scp -O -P 22 -i ~/.ssh/key -r parts/ user@host:/path/
scp -O -P 22 -i ~/.ssh/key -r templates/ user@host:/path/
```

**SUCCESS CRITERIA:**
- Files deployed without errors
- Child theme shows as active
- CSS custom properties loading in page source

### Phase 2: Content Structure
```bash
# Create core pages
wp post create --post_type=page --post_title="Home" --post_status=publish
wp post create --post_type=page --post_title="Membership" --post_status=publish  
wp post create --post_type=page --post_title="How It Works" --post_status=publish

# Set homepage
wp option update show_on_front page
wp option update page_on_front $(wp post list --post_type=page --name=home --field=ID)
```

### Phase 3: Visual Implementation (CRITICAL)
**Fix pattern rendering by replacing references with content:**

1. **Read pattern files** to get actual content
2. **Replace pattern references** in templates with inline content
3. **Deploy updated templates** using SCP
4. **Test visual appearance** with real tools

**DEPLOYMENT METHOD:**
```powershell
# Create fixed template with inline content
scp -O -P 22 -i ~/.ssh/key front-page-fixed.html user@host:/themes/child/templates/front-page.html
```

### Phase 4: Visual Quality Assurance
**CRITICAL:** Technical success ≠ Visual success

**Visual QA Checklist:**
- [ ] Design colors visible (not just CSS tokens loaded)
- [ ] Typography scaling working (4xl headlines, responsive)  
- [ ] Card styling active (hover effects, shadows)
- [ ] Button styling applied (accent colors, radius)
- [ ] Layout constraints working (720px content, 1280px wide)
- [ ] Background alternation visible (white/paper sections)

**Testing Tools:**
```powershell
python Tools\client-audit-tool.py --url https://site.com --quick
```

**Visual Verification Commands:**
```powershell
(Invoke-WebRequest -Uri https://site.com).Content | Select-String -Pattern "has-accent-background-color"
(Invoke-WebRequest -Uri https://site.com).Content | Select-String -Pattern "Hero-Headline-Text"
```

---

## WordPress FSE Deployment Checklist

### Pre-Deployment
- [ ] Child theme files ready (`theme.json`, `style.css`, `functions.php`)
- [ ] Pattern files created (`patterns/*.html`)
- [ ] Template files ready (`templates/*.html`)
- [ ] Supporting files ready (`parts/*.html`, `inc/*.php`)

### Technical Deployment
- [ ] Deploy core files via SCP method
- [ ] Deploy supporting assets via SCP method  
- [ ] Activate child theme via SSH/WP-CLI
- [ ] Verify technical loading (CSS tokens, theme active)

### Content Deployment  
- [ ] Create core pages via WP-CLI
- [ ] Set static homepage with proper template
- [ ] **FIX PATTERN RENDERING**: Replace references with inline content
- [ ] Deploy updated templates with pattern content

### Visual Quality Assurance
- [ ] Test homepage visual appearance
- [ ] Verify design tokens are visually applied
- [ ] Check card styling and hover effects
- [ ] Confirm button styling and interactions
- [ ] Test responsive behavior
- [ ] Validate interior page layouts

### Site Completion
- [ ] Build interior page content with design patterns
- [ ] Test all pages for visual consistency  
- [ ] Verify navigation and user experience
- [ ] Document deployment process and lessons learned

---

## Troubleshooting Guide

### "Site Technically Works But Isn't Pretty"
**CAUSE:** Pattern references not rendering  
**SOLUTION:** Replace pattern references with inline content in templates

### "CSS Tokens Loading But No Visual Design"
**CAUSE:** Pattern content missing, only structural HTML showing  
**SOLUTION:** Deploy actual pattern content, not just pattern file references

### "Child Theme Active But Default Appearance"
**CAUSE:** Template not using child theme patterns  
**SOLUTION:** Verify front-page.html exists and contains design content

### "SCP Works But SSH Commands Hang"
**CAUSE:** Known Windows/Cursor terminal limitation  
**SOLUTION:** Use SCP for files, SSH + output capture for commands

---

## Success Patterns Library

### Beautiful Hero Section Template
```html
<section class="wp-block-group alignfull has-white-background-color">
  <h1 class="wp-block-heading has-text-align-center has-4-xl-font-size">
    Your Compelling Headline
  </h1>
  <p class="has-text-align-center has-xl-font-size">
    Supporting value proposition
  </p>
  <div class="wp-block-buttons">
    <div class="wp-block-button">
      <a class="wp-block-button__link has-white-color has-accent-background-color" href="/action/">
        Primary CTA
      </a>
    </div>
  </div>
</section>
```

### Stats Block with Design Tokens
```html
<dl class="wp-block-group astro-stat-item">
  <dt class="has-primary-color has-text-color" style="font-size:3rem;font-weight:800">
    1,200+
  </dt>
  <dd class="has-s-font-size">Verified Members</dd>
</dl>
```

### Soft Card Component
```html
<div class="wp-block-group is-style-soft-card">
  <p class="has-accent-color has-text-color" style="font-size:4rem;line-height:1">1</p>
  <h3 class="wp-block-heading has-xl-font-size">Step Title</h3>
  <p>Step description with proper spacing and typography.</p>
</div>
```

---

## File Locations for Future Reference

**Core Documentation:**
- `/SBEP_Core/SBEP-ADDENDUM-WORDPRESS-FSE-DEPLOYMENT.md` (this file)
- `/astro/reports/deployment/DESIGN-BLUEPRINT-DEPLOYMENT-LESSONS-LEARNED.md`

**Proven Working Files:**
- `/astro/src-themes/astro-tt5-child/` (complete working child theme)
- `/astro/src-themes/astro-tt5-child/patterns/` (all design patterns)
- `/astro/src-themes/astro-tt5-child/templates/front-page.html` (working template)

**Example Commands:**
- See lesson learned documentation for exact PowerShell commands that work

---

**This addendum ensures other agents can achieve the same beautiful visual results by following the proven pattern rendering solution and visual QA process.**
