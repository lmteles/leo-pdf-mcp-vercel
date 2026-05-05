"""
Vercel Serverless Function: PDF Report Generator
Leo T — Estamina / Sebrae Bahia
Uses: leo_reportlab_brand_kit + ReportLab + Matplotlib
"""

import json
import os
import sys
import traceback
from io import BytesIO

# Ensure our brand kit is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from leo_reportlab_brand_kit import *
except ImportError as e:
    print(f"ERROR: Could not import leo_reportlab_brand_kit: {e}")


def handler(request):
    """
    HTTP endpoint: POST /api/generate_pdf
    
    Request body (JSON):
    {
        "title": "Report Title",
        "client": "Sebrae Bahia",
        "year": "2026",
        "content": {
            "sections": [
                {
                    "type": "h1",
                    "text": "Section Heading"
                },
                {
                    "type": "body",
                    "text": "Paragraph text here..."
                },
                {
                    "type": "chart",
                    "chart_type": "bar",
                    "categories": ["Q1", "Q2", "Q3"],
                    "values": [120, 150, 180],
                    "title": "Quarterly Revenue"
                }
            ]
        },
        "cover_metrics": [
            ["R$ 158K", "Monthly\nRevenue"],
            ["R$ 177K", "Initial\nCAPEX"],
            ["6.7 mo", "Payback"],
            ["16.6%", "Margin"]
        ],
        "cover_description": "Brief summary of report..."
    }
    
    Response:
    {
        "success": true,
        "pdf_url": "https://leo-pdf-mcp-vercel.vercel.app/pdfs/Report_2026.pdf",
        "filename": "Report_2026.pdf"
    }
    """
    
    if request.method == 'OPTIONS':
        return cors_response({})
    
    if request.method != 'POST':
        return cors_response({'error': 'Method not allowed'}, 405)
    
    try:
        # Parse request body
        payload = json.loads(request.get_data(as_text=True))
        
        # Extract parameters
        report_title = payload.get('title', 'Report')
        report_client = payload.get('client', 'Estamina')
        report_year = payload.get('year', '2026')
        content_spec = payload.get('content', {})
        cover_metrics = payload.get('cover_metrics', [
            ['R$ 0', 'Metric 1'],
            ['R$ 0', 'Metric 2'],
            ['R$ 0', 'Metric 3'],
            ['R$ 0', 'Metric 4'],
        ])
        cover_description = payload.get('cover_description', 
            'Executive summary of the strategic analysis.')
        
        # Build story (flowables)
        S = build_styles()
        story = cover_placeholder()
        
        # Process content sections
        sections = content_spec.get('sections', [])
        for i, section in enumerate(sections):
            s_type = section.get('type', 'body')
            
            if s_type == 'h1':
                story.append(Paragraph(section['text'], S['h1']))
                story.append(section_rule())
                story.append(Spacer(1, 6))
            
            elif s_type == 'h2':
                story.append(Paragraph(section['text'], S['h2']))
                story.append(Spacer(1, 4))
            
            elif s_type == 'h3':
                story.append(Paragraph(section['text'], S['h3']))
                story.append(Spacer(1, 3))
            
            elif s_type == 'body':
                story.append(Paragraph(section['text'], S['body']))
                story.append(Spacer(1, 6))
            
            elif s_type == 'caption':
                story.append(Paragraph(section['text'], S['caption']))
                story.append(Spacer(1, 4))
            
            elif s_type == 'bullet':
                for bullet_text in section.get('items', []):
                    story.append(Paragraph(f'• {bullet_text}', S['bullet']))
            
            elif s_type == 'spacer':
                story.append(Spacer(1, section.get('height', 6)))
            
            elif s_type == 'page_break':
                story.append(PageBreak())
            
            elif s_type == 'callout':
                story.append(callout_box(
                    section['text'], S,
                    label=section.get('label'),
                    border=_parse_color(section.get('border', 'teal')),
                    bg=_parse_color(section.get('bg', 'light'))
                ))
                story.append(Spacer(1, 6))
            
            elif s_type == 'kpi_row':
                kpi_data = section.get('kpis', [])
                kpi_tuples = []
                for kpi in kpi_data:
                    kpi_tuples.append((
                        kpi['value'],
                        kpi['label'],
                        _parse_color(kpi.get('color', 'teal'))
                    ))
                story.append(kpi_row(kpi_tuples, S))
                story.append(Spacer(1, 8))
            
            elif s_type == 'chart':
                chart_type = section.get('chart_type', 'bar')
                chart_img = _build_chart(chart_type, section, S)
                if chart_img:
                    story.append(chart_img)
                    caption = section.get('caption', '')
                    if caption:
                        story.append(Paragraph(caption, S['caption']))
                    story.append(Spacer(1, 6))
        
        # Define cover function
        def draw_leo_cover(c):
            draw_cover(c,
                title_line1=report_title,
                title_line2='',
                subtitle=payload.get('subtitle', 'Strategic Analysis'),
                metrics=cover_metrics,
                description=cover_description,
                year=report_year
            )
        
        # Generate PDF to bytes buffer
        pdf_buffer = BytesIO()
        output_path = f'/tmp/{report_title.replace(" ", "_")}_{report_year}.pdf'
        
        # Build the document
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            leftMargin=40, rightMargin=40,
            topMargin=38, bottomMargin=28,
            title=report_title,
            author='Leo T — Estamina',
            subject='Strategic Report',
        )
        
        HFC = make_header_footer_canvas(
            report_title, report_client, report_year,
            cover_fn=draw_leo_cover
        )
        
        doc.build(story, canvasmaker=HFC)
        pdf_buffer.seek(0)
        
        # Save to /tmp and return URL reference
        filename = f'{report_title.replace(" ", "_")}_{report_year}.pdf'
        
        # In production, upload to cloud storage (S3, etc.)
        # For now, return a placeholder response
        response = {
            'success': True,
            'filename': filename,
            'message': 'PDF generated successfully',
            'pdf_base64': pdf_buffer.getvalue().hex()[:100] + '...',  # Just for validation
        }
        
        return cors_response(response, 200)
    
    except json.JSONDecodeError:
        return cors_response({'error': 'Invalid JSON'}, 400)
    except Exception as e:
        error_msg = f'{type(e).__name__}: {str(e)}\n{traceback.format_exc()}'
        print(f'ERROR: {error_msg}', file=sys.stderr)
        return cors_response({'error': error_msg}, 500)


def _parse_color(color_str):
    """Parse color name to HexColor."""
    color_map = {
        'navy': NAVY, 'teal': TEAL, 'gold': GOLD,
        'light': LIGHT_BG, 'dark': DARK_TEXT,
        'grey': MID_GREY, 'white': WHITE,
    }
    return color_map.get(color_str.lower(), TEAL)


def _build_chart(chart_type, spec, styles):
    """Build a chart based on spec dict."""
    try:
        if chart_type == 'bar':
            return bar_chart(
                categories=spec.get('categories', []),
                values=spec.get('values', []),
                title=spec.get('title', ''),
                xlabel=spec.get('xlabel', ''),
                ylabel=spec.get('ylabel', ''),
                orientation=spec.get('orientation', 'vertical'),
                value_fmt=spec.get('value_fmt', '{v}'),
                width_cm=spec.get('width_cm', 14),
                height_cm=spec.get('height_cm', 5.5),
            )
        elif chart_type == 'line':
            return line_chart(
                x_labels=spec.get('x_labels', []),
                y_series=spec.get('y_series', []),
                series_names=spec.get('series_names'),
                title=spec.get('title', ''),
                xlabel=spec.get('xlabel', ''),
                ylabel=spec.get('ylabel', ''),
                width_cm=spec.get('width_cm', 13),
                height_cm=spec.get('height_cm', 6.0),
            )
        elif chart_type == 'pie':
            return pie_chart(
                values=spec.get('values', []),
                labels=spec.get('labels', []),
                title=spec.get('title', ''),
                width_cm=spec.get('width_cm', 13),
                height_cm=spec.get('height_cm', 6.0),
            )
        elif chart_type == 'donut':
            return donut_chart(
                values=spec.get('values', []),
                labels=spec.get('labels', []),
                title=spec.get('title', ''),
                center_text=spec.get('center_text', ''),
                center_subtext=spec.get('center_subtext', ''),
                width_cm=spec.get('width_cm', 8.5),
                height_cm=spec.get('height_cm', 6.5),
            )
        elif chart_type == 'payback':
            return payback_chart(
                investment=spec.get('investment', 0),
                monthly_profit=spec.get('monthly_profit', 0),
                months=spec.get('months', 10),
                title=spec.get('title', 'Payback Analysis'),
                width_cm=spec.get('width_cm', 13.5),
                height_cm=spec.get('height_cm', 6.0),
            )
    except Exception as e:
        print(f'Chart generation error: {e}', file=sys.stderr)
    return None


def cors_response(data, status_code=200):
    """Return JSON response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(data),
    }
