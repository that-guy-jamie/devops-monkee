# ASTRO Brand Color Palette Options

**Requirements:**
- Clean & sleek
- No gradients
- Professional for property/hospitality platform
- Works with Astra + Beaver Builder

---

## Option 1: **Ocean Blue + Warm Neutrals** (Recommended)

### Primary
- **Deep Ocean Blue**: `#0A4D68` - Trust, stability, professionalism
  - Use for: Headers, CTAs, nav links, emphasis

### Secondary  
- **Soft Teal**: `#088395` - Modern, fresh, travel-friendly
  - Use for: Hover states, icons, secondary CTAs

### Neutrals
- **Warm White**: `#FAFAFA` - Clean backgrounds
- **Soft Gray**: `#F5F5F5` - Section backgrounds
- **Medium Gray**: `#6B7280` - Body text
- **Dark Charcoal**: `#1F2937` - Headings

### Accent
- **Warm Amber**: `#F59E0B` - Call attention, positive actions
  - Use sparingly for: Important CTAs, badges, notifications

**Why this works:**
- Ocean blue = trust + vacation/travel
- Warm neutrals = inviting, not sterile
- No gradients, just solid professional colors
- Similar professional feel to 1 Percent Lists but with hospitality vibe

---

## Option 2: **Modern Navy + Crisp White**

### Primary
- **Navy Blue**: `#1E3A8A` - Professional, trustworthy
  
### Secondary
- **Sky Blue**: `#0EA5E9` - Fresh, modern

### Neutrals
- **Pure White**: `#FFFFFF`
- **Light Gray**: `#F3F4F6`
- **Text Gray**: `#4B5563`
- **Black**: `#111827`

### Accent
- **Coral**: `#F97316` - Energy, action

**Why this works:**
- High contrast for readability
- Very clean, modern aesthetic
- Navy conveys professionalism
- Works great for SaaS/platform feel

---

## Option 3: **Slate + Indigo** (Tech-Forward)

### Primary
- **Deep Indigo**: `#4F46E5` - Innovation, tech-forward

### Secondary
- **Cool Teal**: `#14B8A6` - Modern, fresh

### Neutrals
- **Slate 50**: `#F8FAFC`
- **Slate 100**: `#F1F5F9`
- **Slate 600**: `#475569` - Text
- **Slate 900**: `#0F172A` - Headings

### Accent
- **Violet**: `#8B5CF6` - Premium, distinctive

**Why this works:**
- Modern tech platform aesthetic
- Distinctive without being loud
- Great for innovation-focused brand
- Still professional

---

## Recommended: **Option 1 - Ocean Blue**

For ASTRO's property/hospitality focus, **Option 1** provides:
- ✅ Professional trust (blue)
- ✅ Hospitality warmth (warm neutrals)
- ✅ Travel/vacation vibe (ocean/teal)
- ✅ Clean, no gradients
- ✅ High contrast for accessibility

### Implementation in Astra

```css
/* Add to Appearance → Customize → Additional CSS */

:root {
  /* Primary Colors */
  --ast-global-color-primary: #0A4D68;
  --ast-global-color-secondary: #088395;
  
  /* Neutrals */
  --ast-global-color-bg: #FAFAFA;
  --ast-global-color-section: #F5F5F5;
  --ast-global-color-text: #6B7280;
  --ast-global-color-heading: #1F2937;
  
  /* Accent */
  --ast-global-color-accent: #F59E0B;
  
  /* Overrides */
  --ast-global-color-0: #0A4D68; /* Primary */
  --ast-global-color-1: #FAFAFA; /* Background */
  --ast-global-color-2: #F5F5F5; /* Section BG */
}

/* Button Styling */
.fl-button,
.ast-button {
  background-color: var(--ast-global-color-primary);
  border-color: var(--ast-global-color-primary);
}

.fl-button:hover,
.ast-button:hover {
  background-color: var(--ast-global-color-secondary);
  border-color: var(--ast-global-color-secondary);
}

/* Links */
a {
  color: var(--ast-global-color-primary);
}

a:hover {
  color: var(--ast-global-color-secondary);
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
  color: var(--ast-global-color-heading);
}

/* Emphasis/Highlights */
.highlight,
.brand-color {
  color: var(--ast-global-color-primary);
}
```

---

## Next Step

**Which option resonates with your vision for ASTRO?**

1. Ocean Blue + Warm Neutrals (hospitality-focused)
2. Modern Navy + Crisp White (clean professional)
3. Slate + Indigo (tech-forward)

Or want me to create a variation? Just describe the vibe!

