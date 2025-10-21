import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_pdf(audit_id: str, audit_data: Dict[str, Any], out_dir: str = "./reports") -> str:
    """
    Generate a comprehensive PDF audit report
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{audit_id}.pdf")

    # Create PDF document
    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.darkblue,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkgreen
    )

    score_style = ParagraphStyle(
        'Score',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.darkred,
        alignment=TA_CENTER
    )

    # Build content
    content = []

    # Title page
    content.append(Paragraph("Website Audit Report", title_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Audit ID: {audit_id}", styles['Normal']))
    content.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
    content.append(Spacer(1, 30))

    # Overall scores section
    content.append(Paragraph("Overall Scores", section_style))

    if audit_data.get('overall_score') is not None:
        # Create score visualization
        scores_data = [
            ['Performance', audit_data.get('lighthouse_perf', 0)],
            ['Accessibility', audit_data.get('lighthouse_accessibility', 0)],
            ['Best Practices', audit_data.get('lighthouse_best_practices', 0)],
            ['SEO', audit_data.get('lighthouse_seo', 0)]
        ]

        scores_table = Table(scores_data, colWidths=[3*inch, 1*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        content.append(scores_table)
        content.append(Spacer(1, 20))

        # Overall score
        overall_score = audit_data.get('overall_score', 0)
        content.append(Paragraph(f"Overall Score: {overall_score}/100", score_style))
        content.append(Spacer(1, 30))

    # SEO findings
    if 'seo' in audit_data:
        content.append(Paragraph("SEO Analysis", section_style))

        seo_data = audit_data['seo']
        seo_findings = []

        if seo_data.get('title'):
            seo_findings.append(f"Page Title: {seo_data['title']['text']}")
            if not seo_data['title']['optimal_length']:
                seo_findings.append(f"⚠️ Title length ({seo_data['title']['length']} chars) is not optimal (30-60 recommended)")

        if seo_data.get('meta_description'):
            seo_findings.append(f"Meta Description: {seo_data['meta_description']['text'][:100]}...")
            if not seo_data['meta_description']['optimal_length']:
                seo_findings.append(f"⚠️ Description length ({seo_data['meta_description']['length']} chars) is not optimal (120-160 recommended)")

        if seo_data.get('canonical'):
            seo_findings.append("✅ Canonical URL properly configured")
        else:
            seo_findings.append("❌ Missing canonical URL")

        if seo_data.get('schema_detected'):
            seo_findings.append("✅ Structured data detected")
        else:
            seo_findings.append("❌ No structured data found")

        if seo_data.get('robots_txt', {}).get('exists'):
            seo_findings.append("✅ robots.txt found")
        else:
            seo_findings.append("❌ robots.txt missing")

        if seo_data.get('sitemap', {}).get('exists'):
            seo_findings.append("✅ XML sitemap found")
        else:
            seo_findings.append("❌ XML sitemap missing")

        for finding in seo_findings:
            content.append(Paragraph(finding, styles['Normal']))
        content.append(Spacer(1, 20))

    # Tech stack
    if 'tech' in audit_data:
        content.append(Paragraph("Technology Stack", section_style))

        tech_data = audit_data['tech']
        tech_findings = []

        if tech_data.get('cms'):
            tech_findings.append(f"CMS: {', '.join(tech_data['cms'])}")

        if tech_data.get('cdn'):
            tech_findings.append(f"CDN: {', '.join(tech_data['cdn'])}")

        if tech_data.get('analytics'):
            tech_findings.append(f"Analytics: {', '.join(tech_data['analytics'])}")

        if tech_data.get('frameworks'):
            tech_findings.append(f"Frameworks: {', '.join(tech_data['frameworks'])}")

        tech_findings.append(f"Server: {tech_data.get('server', 'Unknown')}")

        for finding in tech_findings:
            content.append(Paragraph(finding, styles['Normal']))
        content.append(Spacer(1, 20))

    # Performance metrics
    if 'cwv' in audit_data:
        content.append(Paragraph("Core Web Vitals", section_style))

        cwv_data = audit_data['cwv']
        cwv_findings = []

        if cwv_data.get('LCP'):
            cwv_findings.append(f"Largest Contentful Paint: {cwv_data['LCP']}ms")
        if cwv_data.get('INP'):
            cwv_findings.append(f"Interaction to Next Paint: {cwv_data['INP']}ms")
        if cwv_data.get('CLS'):
            cwv_findings.append(f"Cumulative Layout Shift: {cwv_data['CLS']}")

        for finding in cwv_findings:
            content.append(Paragraph(finding, styles['Normal']))
        content.append(Spacer(1, 20))

    # Summary and recommendations
    content.append(Paragraph("Summary & Recommendations", section_style))

    overall_score = audit_data.get('overall_score', 0)
    if overall_score >= 90:
        summary_text = "Excellent! Your website performs very well across all audit categories. Minor optimizations may still be beneficial."
    elif overall_score >= 75:
        summary_text = "Good performance overall. Focus on the areas with lower scores to improve user experience."
    elif overall_score >= 60:
        summary_text = "Moderate performance. Several areas need improvement to provide a better user experience."
    else:
        summary_text = "Significant improvements needed. Prioritize fixing critical issues affecting performance and accessibility."

    content.append(Paragraph(summary_text, styles['Normal']))
    content.append(Spacer(1, 20))

    # Generate PDF
    doc.build(content)

    return path
