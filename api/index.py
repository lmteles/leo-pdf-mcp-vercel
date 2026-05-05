"""
Vercel Serverless Function: PDF Report Generator
Leo T — Estamina / Sebrae Bahia
"""

from flask import Flask, request, jsonify
import json
import sys
import os
import traceback
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from leo_reportlab_brand_kit import *
except ImportError as e:
    print(f"ERROR: Could not import leo_reportlab_brand_kit: {e}")

app = Flask(__name__)

@app.route('/api/generate_pdf', methods=['POST'])
def generate_pdf():
    """Generate a branded PDF report."""
    try:
        payload = request.get_json()
        
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
        cover_description = payload.get('cover_description', 'Executive summary.')
        
        S = build_styles()
        story = cover_placeholder()
        
        sections = content_spec.get('sections', [])
        for section in sections:
            s_type = section.get('type', 'body')
            
            if s_type == 'h1':
                story.append(Paragraph(section['text'], S['h1']))
                story.append(section_rule())
                story.append(Spacer(1, 6))
            elif s_type == 'h2':
                story.append(Paragraph(section['text'], S['h2']))
                story.append(Spacer(1, 4))
            elif s_type == 'body':
                story.append(Paragraph(section['text'], S['body']))
                story.append(Spacer(1, 6))
            elif s_type == 'chart':
                chart_type = section.get('chart_type', 'bar')
                chart_img = _build_chart(chart_type, section, S)
                if chart_img:
                    story.append(chart_img)
                    if section.get('caption'):
                        story.append(Paragraph(section['caption'], S['caption']))
                    story.append(Spacer(1, 6))
            elif s_type == 'callout':
                story.append(callout_box(
                    section['text'], S,
                    label=section.get('label'),
                    border=_parse_color(section.get('border', 'teal'))
                ))
                story.append(Spacer(1, 6))
        
        def draw_leo_cover(c):
            draw_cover(c,
                title_line1=report_title,
                title_line2='',
                subtitle=payload.get('subtitle', 'Strategic Analysis'),
                metrics=cover_metrics,
                description=cover_description,
                year=report_year
            )
        
        pdf_buffer = BytesIO()
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
        
        return jsonify({
            'success': True,
            'filename': f'{report_title.replace(" ", "_")}_{report_year}.pdf',
            'message': 'PDF generated successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _parse_color(color_str):
    color_map = {
        'navy': NAVY, 'teal': TEAL, 'gold': GOLD,
        'light': LIGHT_BG, 'dark': DARK_TEXT,
    }
    return color_map.get(color_str.lower(), TEAL)

def _build_chart(chart_type, spec, styles):
    try:
        if chart_type == 'bar':
            return bar_chart(
                categories=spec.get('categories', []),
                values=spec.get('values', []),
                title=spec.get('title', ''),
                value_fmt=spec.get('value_fmt', '{v}'),
            )
        elif chart_type == 'line':
            return line_chart(
                x_labels=spec.get('x_labels', []),
                y_series=spec.get('y_series', []),
                series_names=spec.get('series_names'),
                title=spec.get('title', ''),
            )
        elif chart_type == 'pie':
            return pie_chart(
                values=spec.get('values', []),
                labels=spec.get('labels', []),
                title=spec.get('title', ''),
            )
    except Exception as e:
        print(f'Chart error: {e}')
    return None

if __name__ == '__main__':
    app.run()
