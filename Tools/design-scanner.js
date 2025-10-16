/**
 * Design Scanner Tool
 * Extracts visual design information from a website for AI analysis
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scanDesign(url) {
  console.log(`Scanning design from: ${url}`);
  
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set viewport for desktop
  await page.setViewportSize({ width: 1920, height: 1080 });
  
  try {
    await page.goto(url, { waitUntil: 'networkidle' });
    
    const outputDir = path.join(__dirname, 'design-analysis');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Take full page screenshot
    await page.screenshot({ 
      path: path.join(outputDir, 'full-page.png'), 
      fullPage: true 
    });
    console.log('✓ Screenshot captured');
    
    // Extract design data
    const designData = await page.evaluate(() => {
      const data = {
        colors: new Set(),
        fonts: new Set(),
        sections: [],
        buttons: [],
        headings: [],
        spacing: [],
        gradients: []
      };
      
      // Helper to get computed styles
      const getStyles = (el) => {
        const styles = window.getComputedStyle(el);
        return {
          color: styles.color,
          backgroundColor: styles.backgroundColor,
          backgroundImage: styles.backgroundImage,
          fontSize: styles.fontSize,
          fontFamily: styles.fontFamily,
          fontWeight: styles.fontWeight,
          padding: styles.padding,
          margin: styles.margin,
          borderRadius: styles.borderRadius,
          boxShadow: styles.boxShadow,
          lineHeight: styles.lineHeight
        };
      };
      
      // Extract colors from all visible elements
      document.querySelectorAll('*').forEach(el => {
        const styles = window.getComputedStyle(el);
        if (styles.color) data.colors.add(styles.color);
        if (styles.backgroundColor && styles.backgroundColor !== 'rgba(0, 0, 0, 0)') {
          data.colors.add(styles.backgroundColor);
        }
        if (styles.backgroundImage && styles.backgroundImage !== 'none') {
          if (styles.backgroundImage.includes('gradient')) {
            data.gradients.push(styles.backgroundImage);
          }
        }
        if (styles.fontFamily) data.fonts.add(styles.fontFamily);
      });
      
      // Extract sections (major containers)
      document.querySelectorAll('section, .section, [class*="section"], main > div').forEach((el, i) => {
        if (el.offsetHeight > 100) { // Only meaningful sections
          const rect = el.getBoundingClientRect();
          data.sections.push({
            index: i,
            tag: el.tagName,
            className: el.className,
            height: Math.round(rect.height),
            styles: getStyles(el),
            textContent: el.textContent.substring(0, 200)
          });
        }
      });
      
      // Extract buttons
      document.querySelectorAll('a[class*="btn"], button, .button, [class*="button"]').forEach(el => {
        data.buttons.push({
          text: el.textContent.trim(),
          href: el.href || null,
          styles: getStyles(el)
        });
      });
      
      // Extract headings
      document.querySelectorAll('h1, h2, h3, h4').forEach(el => {
        data.headings.push({
          level: el.tagName,
          text: el.textContent.trim(),
          styles: getStyles(el)
        });
      });
      
      // Get overall page spacing patterns
      const container = document.querySelector('.container, main, [class*="wrap"]');
      if (container) {
        const containerStyles = window.getComputedStyle(container);
        data.spacing.push({
          element: 'container',
          maxWidth: containerStyles.maxWidth,
          padding: containerStyles.padding,
          margin: containerStyles.margin
        });
      }
      
      return {
        colors: Array.from(data.colors),
        fonts: Array.from(data.fonts),
        sections: data.sections.slice(0, 10), // Top 10 sections
        buttons: data.buttons.slice(0, 15),
        headings: data.headings.slice(0, 20),
        spacing: data.spacing,
        gradients: [...new Set(data.gradients)].slice(0, 10)
      };
    });
    
    // Get HTML structure (simplified)
    const htmlStructure = await page.evaluate(() => {
      const getStructure = (el, depth = 0) => {
        if (depth > 3) return null; // Limit depth
        const children = Array.from(el.children)
          .filter(child => child.offsetHeight > 50) // Only visible elements
          .map(child => getStructure(child, depth + 1))
          .filter(Boolean);
        
        return {
          tag: el.tagName.toLowerCase(),
          id: el.id || null,
          classes: el.className.split(' ').filter(c => c).slice(0, 3),
          children: children.length ? children : undefined,
          text: children.length ? undefined : el.textContent.trim().substring(0, 100)
        };
      };
      
      const main = document.querySelector('main, body');
      return getStructure(main);
    });
    
    // Create design analysis report
    const report = {
      url,
      scannedAt: new Date().toISOString(),
      viewport: { width: 1920, height: 1080 },
      design: designData,
      structure: htmlStructure,
      summary: {
        totalColors: designData.colors.length,
        totalFonts: designData.fonts.length,
        totalSections: designData.sections.length,
        totalButtons: designData.buttons.length,
        hasGradients: designData.gradients.length > 0
      }
    };
    
    // Save as JSON
    fs.writeFileSync(
      path.join(outputDir, 'design-data.json'),
      JSON.stringify(report, null, 2)
    );
    console.log('✓ Design data extracted');
    
    // Create human-readable markdown report
    const markdown = generateMarkdownReport(report);
    fs.writeFileSync(
      path.join(outputDir, 'DESIGN-ANALYSIS.md'),
      markdown
    );
    console.log('✓ Analysis report generated');
    
    console.log(`\n✅ Complete! Check: ${outputDir}`);
    
  } catch (error) {
    console.error('Error scanning:', error);
    throw error;
  } finally {
    await browser.close();
  }
}

function generateMarkdownReport(data) {
  let md = `# Design Analysis: ${data.url}\n\n`;
  md += `**Scanned:** ${data.scannedAt}\n\n`;
  md += `## Summary\n\n`;
  md += `- **Colors Found:** ${data.summary.totalColors}\n`;
  md += `- **Fonts:** ${data.summary.totalFonts}\n`;
  md += `- **Major Sections:** ${data.summary.totalSections}\n`;
  md += `- **Buttons/CTAs:** ${data.summary.totalButtons}\n`;
  md += `- **Uses Gradients:** ${data.summary.hasGradients ? 'Yes' : 'No'}\n\n`;
  
  md += `## Color Palette\n\n`;
  md += '```css\n';
  data.design.colors.slice(0, 20).forEach(color => {
    md += `${color}\n`;
  });
  md += '```\n\n';
  
  if (data.design.gradients.length > 0) {
    md += `## Gradients\n\n`;
    data.design.gradients.forEach((grad, i) => {
      md += `${i + 1}. \`${grad}\`\n`;
    });
    md += '\n';
  }
  
  md += `## Typography\n\n`;
  md += '```css\n';
  data.design.fonts.forEach(font => {
    md += `${font}\n`;
  });
  md += '```\n\n';
  
  md += `## Headings\n\n`;
  data.design.headings.slice(0, 10).forEach(h => {
    md += `### ${h.level}: "${h.text}"\n`;
    md += `- Font: ${h.styles.fontFamily}\n`;
    md += `- Size: ${h.styles.fontSize}\n`;
    md += `- Weight: ${h.styles.fontWeight}\n`;
    md += `- Color: ${h.styles.color}\n\n`;
  });
  
  md += `## Buttons/CTAs\n\n`;
  data.design.buttons.slice(0, 10).forEach((btn, i) => {
    md += `${i + 1}. **"${btn.text}"**\n`;
    md += `   - Background: ${btn.styles.backgroundColor}\n`;
    md += `   - Color: ${btn.styles.color}\n`;
    md += `   - Border Radius: ${btn.styles.borderRadius}\n`;
    md += `   - Padding: ${btn.styles.padding}\n`;
    if (btn.styles.boxShadow !== 'none') {
      md += `   - Shadow: ${btn.styles.boxShadow}\n`;
    }
    md += '\n';
  });
  
  md += `## Layout Sections\n\n`;
  data.design.sections.forEach((section, i) => {
    md += `### Section ${i + 1}\n`;
    md += `- Element: \`${section.tag}.${section.className}\`\n`;
    md += `- Height: ${section.height}px\n`;
    md += `- Background: ${section.styles.backgroundColor}\n`;
    if (section.styles.backgroundImage !== 'none') {
      md += `- Background Image: ${section.styles.backgroundImage.substring(0, 100)}...\n`;
    }
    md += `- Preview: "${section.textContent.substring(0, 150)}..."\n\n`;
  });
  
  return md;
}

// Run if called directly
if (require.main === module) {
  const url = process.argv[2] || 'https://new1percent.wpenginepowered.com/';
  scanDesign(url).catch(console.error);
}

module.exports = { scanDesign };

