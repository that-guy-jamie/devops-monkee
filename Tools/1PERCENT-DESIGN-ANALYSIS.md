# 1 Percent Lists Design Analysis

**Source:** https://new1percent.wpenginepowered.com/  
**Platform:** WordPress + Beaver Builder + Astra Theme (WPEngine hosting)  
**Analysis Date:** 2025-10-16

---

## 🎨 Brand Colors

### Primary Color
- **Blue**: `#0b6ca6` - Used for headings, CTAs, emphasis text
- This is a professional, trustworthy blue perfect for real estate

### Neutral/Background Colors (from CSS variables)
- Code block background: `#ECEFF3`
- Comment inputs background: `#F9FAFB`
- Style guide background: `#F8FAFC`
- Widget background: `#fafafa`
- Light fills: `#fbfbfb`
- White: `#fff`

---

## 📐 Layout Structure

### Container Widths
- Normal container: `1200px`
- Narrow container: `750px`

### Responsive Padding
- XLG: `2.5em`
- LG: `2.5em`
- SLG: `2em`
- MD: `2.5em`
- SM: `2.5em`
- XS: `2.4em`
- XXS: `1.8em`

---

## ✨ Key Design Elements

### Floating/Sticky Header ⭐
- **`.fl-theme-builder-header-floating-header`** class
- Header stays fixed at top of page as you scroll
- Provides persistent navigation and brand presence
- Clean, professional look that follows users down the page

### Hero Section
- **Full-width background** with photo
- **Centered alignment** 
- Primary CTA: "Sell My Home"
- Clean, minimal design

### Section Headers Pattern
```
"Get Started with [1 Percent Lists]"  (Blue highlight on brand name)
```

### Content Blocks (3-Column Grid)
Each service card has:
1. **Colored Heading** with blue accent: "Sell a Home", "Buy a Home"
2. **Checkmark list** items with Font Awesome icons (`far fa-check-square`)
3. **Underlined emphasis** on key words (Full-Service, Thousands, expert guidance)
4. **CTA Button** at bottom ("Learn More")

### Button Styling
- Class: `.fl-button`
- Auto-width with left alignment
- Standard Beaver Builder button module styling

### Stats/Social Proof Section
Displays metrics like:
- $100M+ Saved for Clients
- 8K+ Transactions  
- 1200+ 5⭐ Reviews
- 4000+ Homes Sold

### Video Section
- Video lightbox popups (YouTube embeds)
- Custom thumbnail images
- "What Our Clients Have to Say" testimonial section

---

## 🔤 Typography

### Font Weights
- Blog title font weight: `600`
- Blog meta weight: `600`

### Emphasis Patterns
- **Brand name** in blue spans: `<span style="color: #0b6ca6;">`
- **Underlined** key terms: `<u>`
- **Bold** for emphasis

---

## 🏗️ Beaver Builder Structure

### Rows
- `.fl-row` - Full-width rows
- `.fl-row-bg-photo` - Photo background rows
- **`.fl-row-bg-multiple`** ⭐ - **STACKED/LAYERED backgrounds** (newer BB feature!)
- `.fl-row-bg-overlay` - Background overlay for contrast/depth
- `.fl-row-default-height` - Standard height
- `.fl-row-align-center` - Centered content

### Columns with Backgrounds
- **`.fl-col-bg-photo`** ⭐ - Photo backgrounds on individual columns
- **`.column-overlay-link`** - Makes entire column clickable (great UX!)
- Used for interactive service cards: "Sell a Home", "Buy a Home", "Locations"

### Modules Used
- `fl-module-button` - Call-to-action buttons
- `fl-module-heading` - Headers
- `fl-module-rich-text` - Content blocks
- `fl-module-photo` - Images
- `fl-module-video` - Video lightboxes
- `fl-module-list` - Icon lists

### Column Grid
- `.fl-col-group` - Column groups
- Responsive grid (`.ast-grid-2`, `.ast-grid-3`, `.ast-grid-4`)

---

## 🎯 Key Conversion Elements

### Primary CTAs
1. "Sell My Home" (Hero)
2. "Learn More" (Service cards)
3. "Sell a Home ➔" (Footer CTA)
4. "Buy a Home ➔" (Footer CTA)
5. "Find a Location ➔" (Footer CTA)

### Trust Indicators
- Large statistics display
- Client testimonials section
- Video testimonials
- Professional imagery

---

## 📱 Mobile Strategy
- Breakpoint at `921px`
- Separate container adjusts width to `100%`
- Padding reduces for smaller screens
- Grid collapses to single column

---

## 🎨 Design Principles to Apply to ASTRO

### 1. **Clean, Professional Aesthetic**
- Lots of white space
- Clear visual hierarchy
- Blue accent color for brand consistency

### 2. **Service-Oriented Layout**
- Hero with clear value proposition
- 3-column service cards with icons/checkmarks
- Strong CTAs throughout

### 3. **Trust & Social Proof**
- Statistics prominently displayed
- Video testimonials
- Clean, professional imagery

### 4. **Conversion-Focused**
- Multiple CTA placements
- Clear next-step arrows (➔)
- Simple, direct language

### 5. **Beaver Builder Best Practices**
- Full-width hero rows
- **Stacked/layered backgrounds** for depth (`.fl-row-bg-multiple`)
- **Clickable columns** with photo backgrounds for interactive cards
- Background overlays for text contrast
- Icon lists for benefits
- Button modules for CTAs

---

## 🚀 Implementation Notes for ASTRO

1. **Enable Astra Floating Header** ⭐ - This is a key UX feature
   - Go to Appearance → Customize → Header Builder
   - Enable "Sticky Header" option
   - Configure to float on scroll
2. **Use Astra + Beaver Builder** (already in place)
3. **Define primary brand color** for ASTRO (similar to their #0b6ca6)
4. **Create reusable Beaver Builder templates** for:
   - Hero sections
   - 3-column service cards
   - Stats/metrics displays
   - CTA button rows
5. **Implement mobile-first** responsive design
6. **Add Font Awesome** for icons/checkmarks
7. **Use underline + color** for emphasis on key terms
8. **Keep container at 1200px** max-width
9. **Add video lightbox** capability for testimonials
10. **Mobile hamburger menu** (`.fl-menu-mobile-toggle`) for responsive nav

---

## Next Steps

1. ✅ Extract design system
2. ⏭️ Choose ASTRO brand colors
3. ⏭️ Create Beaver Builder layouts matching this structure
4. ⏭️ Implement hero section
5. ⏭️ Build service card components
6. ⏭️ Add stats/metrics section
7. ⏭️ Integrate testimonials/video

