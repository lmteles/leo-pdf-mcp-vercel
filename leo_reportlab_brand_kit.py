"""
leo_reportlab_brand_kit.py
==========================
Reusable brand kit for Leo T (Estamina / Sebrae Bahia) PDF reports.
Built on ReportLab + Matplotlib.

USAGE
-----
Upload this file to any Claude session, then reference it in your prompt:
  "Use leo_reportlab_brand_kit.py to build a PDF report on [topic]."

Claude will import from this module and apply the full brand system automatically.

VERSION: 1.0  |  2026
"""

import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

# ─────────────────────────────────────────────────────────────
# 1. BRAND PALETTE
# ─────────────────────────────────────────────────────────────

NAVY      = HexColor('#0D2137')
TEAL      = HexColor('#00788A')
GOLD      = HexColor('#C8982A')
LIGHT_BG  = HexColor('#F4F7F9')
MID_GREY  = HexColor('#7F8C9A')
DARK_TEXT = HexColor('#1A2A3A')
WHITE     = HexColor('#FFFFFF')
RULE_CLR  = HexColor('#D0DCE4')
RED_COMPL = HexColor('#C0392B')   # SCR Complication block
DARK_COVER= HexColor('#0A1D2E')   # KPI boxes on cover

CHART_PALETTE = ['#0D2137','#00788A','#C8982A','#4A90B8','#7F8C9A','#A8C0CC','#D0DCE4']

W, H = A4
MARGINS = dict(leftMargin=40, rightMargin=40, topMargin=38, bottomMargin=28)

# ─────────────────────────────────────────────────────────────
# 2. TYPOGRAPHY
# ─────────────────────────────────────────────────────────────

def build_styles():
    """Return the full Leo T typography style dictionary."""
    base = getSampleStyleSheet()
    return {
        'h1': ParagraphStyle('h1', parent=base['Normal'],
            fontSize=17, textColor=NAVY, spaceAfter=6, spaceBefore=18,
            fontName='Helvetica-Bold', leading=22),
        'h2': ParagraphStyle('h2', parent=base['Normal'],
            fontSize=12, textColor=TEAL, spaceAfter=4, spaceBefore=14,
            fontName='Helvetica-Bold', leading=16),
        'h3': ParagraphStyle('h3', parent=base['Normal'],
            fontSize=10, textColor=NAVY, spaceAfter=3, spaceBefore=10,
            fontName='Helvetica-Bold', leading=14),
        'body': ParagraphStyle('body', parent=base['Normal'],
            fontSize=9, textColor=DARK_TEXT, spaceAfter=6, spaceBefore=2,
            fontName='Helvetica', leading=14, alignment=TA_JUSTIFY),
        'caption': ParagraphStyle('caption', parent=base['Normal'],
            fontSize=7.5, textColor=MID_GREY, spaceAfter=4, spaceBefore=2,
            fontName='Helvetica', leading=11, alignment=TA_CENTER),
        'kpi_val': ParagraphStyle('kpi_val', parent=base['Normal'],
            fontSize=20, textColor=TEAL, fontName='Helvetica-Bold',
            leading=24, alignment=TA_CENTER),
        'kpi_lbl': ParagraphStyle('kpi_lbl', parent=base['Normal'],
            fontSize=7.5, textColor=MID_GREY, fontName='Helvetica',
            leading=10, alignment=TA_CENTER),
        'bullet': ParagraphStyle('bullet', parent=base['Normal'],
            fontSize=9, textColor=DARK_TEXT, fontName='Helvetica',
            leading=14, leftIndent=14, spaceAfter=3, spaceBefore=1),
        'white_bold': ParagraphStyle('white_bold', parent=base['Normal'],
            fontSize=8.5, textColor=WHITE, fontName='Helvetica-Bold',
            leading=12, alignment=TA_CENTER),
        'total_row': ParagraphStyle('total_row', parent=base['Normal'],
            fontSize=8, textColor=WHITE, fontName='Helvetica-Bold', leading=12),
    }

# ─────────────────────────────────────────────────────────────
# 3. CHART UTILITIES
# ─────────────────────────────────────────────────────────────

def apply_chart_style(ax, title='', xlabel='', ylabel='', palette=None):
    """Apply Leo's standard chart style to any matplotlib Axes."""
    p = palette or CHART_PALETTE
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
    ax.set_facecolor('white')
    if title:
        ax.set_title(title, fontsize=9, fontweight='bold', color='#0D2137', pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=8, color='#7F8C9A')
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=8, color='#7F8C9A')
    ax.tick_params(axis='both', labelsize=8)


def fig_to_rl_image(fig, dpi=150, width_cm=14, height_cm=None):
    """Convert a matplotlib Figure to a ReportLab Image flowable."""
    buf = io.BytesIO()
    fig.savefig(buf, format='PNG', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    if height_cm:
        return Image(buf, width=width_cm * cm, height=height_cm * cm)
    return Image(buf, width=width_cm * cm)


def bar_chart(categories, values, title='', xlabel='', ylabel='',
              palette=None, figsize=(6.5, 3.8), orientation='vertical',
              value_fmt='R$ {v:,.0f}', width_cm=14, height_cm=5.5):
    """
    Generic bar chart (vertical or horizontal).
    orientation: 'vertical' | 'horizontal'
    value_fmt: format string; use {v} as placeholder.
    """
    p = palette or CHART_PALETTE
    clrs = [p[i % len(p)] for i in range(len(categories))]
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    if orientation == 'vertical':
        bars = ax.bar(categories, values, color=clrs, edgecolor='white',
                      linewidth=1.2, width=0.6, zorder=3)
        for bar, val in zip(bars, values):
            label = value_fmt.format(v=val)
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.015,
                    label, ha='center', va='bottom', fontsize=7.5,
                    fontweight='bold', color='#0D2137')
    else:
        bars = ax.barh(categories, values, color=clrs, edgecolor='white',
                       linewidth=1, height=0.55, zorder=3)
        ax.xaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
        for bar, val in zip(bars, values):
            label = value_fmt.format(v=val)
            ax.text(val * 1.01, bar.get_y() + bar.get_height()/2,
                    label, va='center', fontsize=8, fontweight='bold',
                    color='#0D2137')
    apply_chart_style(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    if orientation == 'horizontal':
        ax.spines['left'].set_visible(False)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=width_cm, height_cm=height_cm)


def line_chart(x_labels, y_series, series_names=None, title='',
               xlabel='', ylabel='', figsize=(5.5, 3.4),
               width_cm=13, height_cm=6.0):
    """
    Line chart. y_series = list of value lists (one per series).
    Markers: circle, teal primary, gold secondary.
    """
    marker_styles = ['o', 's', '^', 'D']
    line_colors   = ['#00788A','#C8982A','#0D2137','#4A90B8']
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    for i, (y, name) in enumerate(zip(y_series, series_names or [f'Série {i+1}' for i in range(len(y_series))])):
        ax.plot(x_labels, y, color=line_colors[i % 4],
                marker=marker_styles[i % 4], linewidth=2.5,
                markersize=8, markerfacecolor=CHART_PALETTE[(i+2) % 7],
                markeredgecolor='white', markeredgewidth=1.5,
                zorder=4, label=name)
        ax.fill_between(x_labels, y, alpha=0.06, color=line_colors[i % 4])
    apply_chart_style(ax, title=title, xlabel=xlabel, ylabel=ylabel)
    if series_names and len(series_names) > 1:
        ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=width_cm, height_cm=height_cm)


def donut_chart(values, labels, title='', center_text='', center_subtext='',
                palette=None, figsize=(5, 4), width_cm=8.5, height_cm=6.5):
    """Donut chart with optional centre label."""
    p = palette or CHART_PALETTE
    clrs = [p[i % len(p)] for i in range(len(values))]
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.pie(values, colors=clrs, startangle=90,
           wedgeprops=dict(width=0.52, edgecolor='white', linewidth=2))
    if center_text:
        ax.text(0, 0.1,  center_text, ha='center', va='center',
                fontsize=26, fontweight='bold', color='#0D2137')
    if center_subtext:
        ax.text(0, -0.25, center_subtext, ha='center', va='center',
                fontsize=8, color='#0D2137')
    legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(clrs, labels)]
    ax.legend(handles=legend_patches, loc='lower center',
              bbox_to_anchor=(0.5, -0.12), fontsize=8, frameon=False)
    if title:
        ax.set_title(title, fontsize=9, color='#0D2137', pad=10, fontweight='bold')
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=width_cm, height_cm=height_cm)


def pie_chart(values, labels, title='', palette=None,
              figsize=(6, 4.5), width_cm=13, height_cm=6.0):
    """Full pie chart with percentage labels and legend."""
    p = palette or CHART_PALETTE
    clrs = [p[i % len(p)] for i in range(len(values))]
    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    _, _, autotexts = ax.pie(
        values, colors=clrs, autopct='%1.1f%%', startangle=140,
        wedgeprops=dict(edgecolor='white', linewidth=1.5),
        pctdistance=0.75, textprops={'fontsize': 8})
    for at in autotexts:
        at.set_color('white')
        at.set_fontweight('bold')
        at.set_fontsize(7.5)
    if title:
        ax.set_title(title, fontsize=9, fontweight='bold', color='#0D2137', pad=12)
    legend_patches = [mpatches.Patch(color=c, label=l) for c, l in zip(clrs, labels)]
    ax.legend(handles=legend_patches, loc='lower center',
              bbox_to_anchor=(0.5, -0.28), fontsize=7.5, frameon=False, ncol=2)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=width_cm, height_cm=height_cm)


def payback_chart(investment, monthly_profit, months=10,
                  title='Curva de Payback — Recuperação do Investimento',
                  figsize=(5.5, 3.4), width_cm=13.5, height_cm=6.0):
    """Standard payback cumulative cash flow chart."""
    m_range  = list(range(0, months))
    cum_cf   = [(-investment) + (m * monthly_profit) for m in m_range]
    pb_month = investment / monthly_profit
    bar_clrs = ['#C8982A' if v < 0 else '#00788A' for v in cum_cf]

    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.bar(m_range, cum_cf, color=bar_clrs, edgecolor='white',
           linewidth=1, width=0.6, zorder=3)
    ax.axhline(0, color='#0D2137', linewidth=1.2, linestyle='--')
    ax.axvline(pb_month, color='#C8982A', linewidth=1.5, linestyle=':',
               label=f'Payback ~{pb_month:.1f} meses')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R${x/1000:.0f}k'))
    ax.set_xticks(m_range)
    ax.set_xticklabels([f'M{m}' for m in m_range], fontsize=8)
    apply_chart_style(ax, title=title,
                      xlabel='Meses de Operação',
                      ylabel='Fluxo de Caixa Acumulado (R$)')
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    return fig_to_rl_image(fig, width_cm=width_cm, height_cm=height_cm)


def side_by_side_charts(img_left, img_right, col_widths=(240, 250)):
    """Lay two chart images side by side in a ReportLab Table."""
    t = Table([[img_left, img_right]], colWidths=list(col_widths), hAlign='CENTER')
    t.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

# ─────────────────────────────────────────────────────────────
# 4. LAYOUT COMPONENTS
# ─────────────────────────────────────────────────────────────

def section_rule(color=TEAL):
    """Horizontal rule between section heading and content."""
    return HRFlowable(width='100%', thickness=1.5, color=color,
                      spaceAfter=6, spaceBefore=2)


def callout_box(text, styles, bg=LIGHT_BG, border=TEAL, label=None):
    """Teal left-border callout/insight box."""
    content = []
    if label:
        content.append(Paragraph(f'<b>{label}</b>',
            ParagraphStyle('cl', parent=styles['body'],
            textColor=border, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3)))
    content.append(Paragraph(text, styles['body']))
    t = Table([[content]], colWidths=[W - 80 - 30])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), bg),
        ('LINEBEFORE',    (0,0), (0,-1), 3, border),
        ('LEFTPADDING',   (0,0), (-1,-1), 12),
        ('RIGHTPADDING',  (0,0), (-1,-1), 12),
        ('TOPPADDING',    (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    return t


def kpi_row(kpi_items, styles, col_width=123):
    """
    Row of KPI boxes.
    kpi_items: list of (value_str, label_str, color) — max 4
    """
    cells = []
    for val, lbl, clr in kpi_items:
        inner = Table([
            [Paragraph(f'<b>{val}</b>', ParagraphStyle('kv', parent=styles['body'],
                fontSize=16, textColor=clr, fontName='Helvetica-Bold',
                leading=20, alignment=TA_CENTER))],
            [Paragraph(lbl, styles['kpi_lbl'])]
        ], colWidths=[col_width - 5])
        inner.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,-1), LIGHT_BG),
            ('TOPPADDING',    (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LINEBELOW',     (0,0), (-1,0), 2, clr),
            ('LEFTPADDING',   (0,0), (-1,-1), 6),
            ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ]))
        cells.append(inner)
    t = Table([cells], colWidths=[col_width] * len(cells), hAlign='LEFT')
    t.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    return t


def styled_table(header_cells, data_rows, col_widths, has_total_row=False):
    """
    Standard branded data table.
    header_cells: list of Paragraph objects (or strings).
    has_total_row: if True, last row gets TEAL bg + WHITE text.
    """
    # Wrap plain strings in Paragraph if needed
    def _p(cell, style):
        if isinstance(cell, str):
            return Paragraph(cell, style)
        return cell
    S = build_styles()
    hdr = [_p(c, ParagraphStyle('th', parent=S['body'], textColor=WHITE,
                                  fontName='Helvetica-Bold')) for c in header_cells]
    t = Table([hdr] + data_rows, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ('BACKGROUND',    (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1 if not has_total_row else -2), [WHITE, LIGHT_BG]),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.4, RULE_CLR),
        ('LINEBELOW',     (0,0), (-1,0), 1.5, TEAL),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]
    if has_total_row:
        style_cmds += [
            ('BACKGROUND', (0,-1), (-1,-1), TEAL),
            ('TEXTCOLOR',  (0,-1), (-1,-1), WHITE),
            ('FONTNAME',   (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]
    t.setStyle(TableStyle(style_cmds))
    return t


def scr_blocks(situation, complication, resolution, styles):
    """
    McKinsey SCR narrative blocks.
    Returns a list of flowables.
    """
    blocks = [
        ('SITUAÇÃO',    TEAL,      situation),
        ('COMPLICAÇÃO', RED_COMPL, complication),
        ('RESOLUÇÃO',   GOLD,      resolution),
    ]
    flowables = []
    for label, clr, text in blocks:
        row = Table([[
            Paragraph(f'<b>{label}</b>',
                ParagraphStyle('scrl', parent=styles['body'],
                textColor=WHITE, fontSize=8.5, fontName='Helvetica-Bold')),
            Paragraph(text, styles['body'])
        ]], colWidths=[70, 390])
        row.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (0,0), clr),
            ('BACKGROUND',    (1,0), (1,0), LIGHT_BG),
            ('TOPPADDING',    (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING',   (0,0), (-1,-1), 10),
            ('RIGHTPADDING',  (0,0), (-1,-1), 10),
            ('VALIGN',        (0,0), (-1,-1), 'TOP'),
        ]))
        flowables.append(row)
        flowables.append(Spacer(1, 4))
    return flowables

# ─────────────────────────────────────────────────────────────
# 5. COVER PAGE
# ─────────────────────────────────────────────────────────────

def draw_cover(c_obj, title_line1, title_line2, subtitle,
               metrics,       # list of exactly 4 tuples: (value_str, label_str)
               description,   # 2–3 line summary, max ~240 chars
               category_label='RELATÓRIO EXECUTIVO  ·  ESTUDO DE VIABILIDADE',
               location='Salvador, Bahia, Brasil',
               year='2026'):
    """
    Draw a full bespoke cover on the canvas for page 1.

    metrics: [(val, lbl), (val, lbl), (val, lbl), (val, lbl)]
    """
    c_obj.saveState()

    # Background
    c_obj.setFillColor(NAVY)
    c_obj.rect(0, 0, W, H, fill=1, stroke=0)

    # Bottom accent strips
    c_obj.setFillColor(TEAL)
    c_obj.rect(0, 0, W * 0.42, 6, fill=1, stroke=0)
    c_obj.setFillColor(GOLD)
    c_obj.rect(W * 0.42, 0, W * 0.58, 6, fill=1, stroke=0)

    # Decorative diagonal top-right
    c_obj.setFillColor(TEAL)
    c_obj.setFillAlpha(0.12)
    p = c_obj.beginPath()
    p.moveTo(W * 0.5, H); p.lineTo(W, H * 0.55); p.lineTo(W, H); p.close()
    c_obj.drawPath(p, fill=1, stroke=0)
    c_obj.setFillAlpha(1)

    # Decorative circles
    for alpha, radius, color in [(0.15, 90, TEAL), (0.2, 60, GOLD)]:
        c_obj.setFillColor(color)
        c_obj.setFillAlpha(alpha)
        c_obj.circle(W * 0.82, H * 0.72, radius, fill=1, stroke=0)
    c_obj.setFillAlpha(1)

    # Plane icon
    c_obj.setFont('Helvetica-Bold', 38)
    c_obj.setFillColor(WHITE)
    c_obj.setFillAlpha(0.6)
    c_obj.drawCentredString(W * 0.82, H * 0.70, '✈')
    c_obj.setFillAlpha(1)

    # Category label
    c_obj.setFont('Helvetica', 10)
    c_obj.setFillColor(GOLD)
    c_obj.drawString(40, H - 60, category_label)

    # Rule
    c_obj.setStrokeColor(TEAL)
    c_obj.setLineWidth(1.5)
    c_obj.line(40, H - 70, W - 40, H - 70)

    # Title
    c_obj.setFont('Helvetica-Bold', 26)
    c_obj.setFillColor(WHITE)
    c_obj.drawString(40, H - 120, title_line1)
    if title_line2:
        c_obj.drawString(40, H - 152, title_line2)

    # Subtitle
    c_obj.setFont('Helvetica', 13)
    c_obj.setFillColor(TEAL)
    sub_y = H - 182 if title_line2 else H - 152
    c_obj.drawString(40, sub_y, subtitle)

    # Gold divider
    c_obj.setStrokeColor(GOLD)
    c_obj.setLineWidth(2)
    c_obj.line(40, sub_y - 18, 200, sub_y - 18)

    # Metric boxes (4 across)
    box_w, box_h = 118, 62
    y_box = sub_y - 100
    for i, (val, lbl) in enumerate(metrics[:4]):
        bx = 40 + i * (box_w + 8)
        c_obj.setFillColor(DARK_COVER)
        c_obj.roundRect(bx, y_box, box_w, box_h, 4, fill=1, stroke=0)
        c_obj.setFillColor(TEAL if i % 2 == 0 else GOLD)
        c_obj.roundRect(bx, y_box, 4, box_h, 2, fill=1, stroke=0)
        c_obj.setFont('Helvetica-Bold', 14)
        c_obj.setFillColor(WHITE)
        c_obj.drawString(bx + 10, y_box + 38, val)
        c_obj.setFont('Helvetica', 7.5)
        c_obj.setFillColor(MID_GREY)
        for j, line in enumerate(lbl.split('\n')):
            c_obj.drawString(bx + 10, y_box + 22 - j * 11, line)

    # Description text
    c_obj.setFont('Helvetica', 9)
    c_obj.setFillColor(HexColor('#A8BCC8'))
    words = description.split()
    lines_out, cur = [], ''
    for w in words:
        if len(cur) + len(w) + 1 > 78:
            lines_out.append(cur.strip()); cur = w + ' '
        else:
            cur += w + ' '
    if cur.strip():
        lines_out.append(cur.strip())
    y_desc = y_box - 28
    for line in lines_out[:4]:
        c_obj.drawString(40, y_desc, line)
        y_desc -= 14

    # Footer
    c_obj.setFont('Helvetica', 8)
    c_obj.setFillColor(MID_GREY)
    c_obj.drawString(40, 20, f'{location}  ·  {year}')
    c_obj.drawRightString(W - 40, 20, 'Confidencial — Uso Restrito')
    c_obj.restoreState()

# ─────────────────────────────────────────────────────────────
# 6. HEADER / FOOTER CANVAS
# ─────────────────────────────────────────────────────────────

def make_header_footer_canvas(report_title, report_client, report_year,
                               cover_fn=None, cover_kwargs=None):
    """
    Factory that returns a HeaderFooterCanvas class with the given metadata.

    cover_fn:     callable(canvas_obj) that draws the cover — defaults to 
                  a plain navy cover if None.
    cover_kwargs: dict passed to cover_fn if provided.
    """
    class _HFC(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            canvas.Canvas.__init__(self, *args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            n = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self._draw_chrome(n)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def _draw_chrome(self, page_count):
            page = self._pageNumber
            if page == 1:
                if cover_fn:
                    cover_fn(self, **(cover_kwargs or {}))
                else:
                    self._plain_cover()
                return
            self.saveState()
            # Header
            self.setFillColor(NAVY)
            self.rect(0, H - 28, W, 28, fill=1, stroke=0)
            self.setFillColor(TEAL)
            self.rect(0, H - 28, 4, 28, fill=1, stroke=0)
            self.setFont('Helvetica-Bold', 8)
            self.setFillColor(WHITE)
            self.drawString(14, H - 18, report_title.upper())
            self.setFont('Helvetica', 8)
            self.drawRightString(W - 14, H - 18, f'CONFIDENCIAL  |  {report_year}')
            # Footer
            self.setFillColor(NAVY)
            self.rect(0, 0, W, 20, fill=1, stroke=0)
            self.setFillColor(GOLD)
            self.rect(0, 0, W * 0.3, 3, fill=1, stroke=0)
            self.setFillColor(TEAL)
            self.rect(W * 0.3, 0, W * 0.7, 3, fill=1, stroke=0)
            self.setFont('Helvetica', 7)
            self.setFillColor(WHITE)
            self.drawString(14, 6, report_client)
            self.drawRightString(W - 14, 6, f'Página {page} de {page_count}')
            self.restoreState()

        def _plain_cover(self):
            self.setFillColor(NAVY)
            self.rect(0, 0, W, H, fill=1, stroke=0)

    return _HFC

# ─────────────────────────────────────────────────────────────
# 7. DOCUMENT BUILDER
# ─────────────────────────────────────────────────────────────

def build_document(output_path, story, report_title, report_client,
                   report_year='2026', cover_fn=None, cover_kwargs=None,
                   pdf_title=None, pdf_subject=''):
    """
    Build the final PDF.

    Always call this instead of doc.build() directly.
    The first item in `story` should be:
        Spacer(1, 1) + PageBreak()   ← reserves page 1 for the cover
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        **MARGINS,
        title=pdf_title or report_title,
        author='Leo T — Estamina / Sebrae Bahia',
        subject=pdf_subject,
    )
    HFC = make_header_footer_canvas(
        report_title, report_client, report_year,
        cover_fn=cover_fn, cover_kwargs=cover_kwargs
    )
    doc.build(story, canvasmaker=HFC)
    print(f'✅  PDF saved → {output_path}')
    return output_path


def cover_placeholder():
    """Returns the two standard flowables that reserve page 1 for the canvas cover."""
    return [Spacer(1, 1), PageBreak()]


# ─────────────────────────────────────────────────────────────
# 8. QUICK-START TEMPLATE
# ─────────────────────────────────────────────────────────────
"""
COPY THIS BLOCK INTO A NEW SCRIPT TO START ANY REPORT:

─────────────────────────────────────────────────────────────
import sys
sys.path.insert(0, '/path/to/leo_reportlab_brand_kit.py directory')
from leo_reportlab_brand_kit import *

S = build_styles()
story = []

# ── COVER ──────────────────────────────────────────────────
def my_cover(c):
    draw_cover(c,
        title_line1='Report Main Title',
        title_line2='Subtitle Line (or empty string)',
        subtitle='One-line strategic framing',
        metrics=[
            ('R$ 158K', 'Monthly Revenue\\nProjected'),
            ('R$ 177K', 'Initial CAPEX'),
            ('6.7 mo',  'Payback\\nPeriod'),
            ('16.6%',   'Profit\\nMargin'),
        ],
        description='Brief 2–3 sentence abstract of the report purpose and scope.',
    )

story += cover_placeholder()

# ── PAGE 2: EXECUTIVE SUMMARY ──────────────────────────────
story.append(Paragraph('Executive Summary', S['h1']))
story.append(section_rule())
story.append(Spacer(1, 6))
story.append(Paragraph('Your body text here...', S['body']))
story.append(Spacer(1, 8))

story.append(kpi_row([
    ('8M+', 'Passengers\\n2025', TEAL),
    ('87%',  'Food/Conv.\\nSpend Share', NAVY),
    ('R$80', 'Average\\nTicket', TEAL),
    ('46%',  'Frequent\\nFlyers', GOLD),
], S))

story.append(Spacer(1, 8))
story.append(callout_box('Key insight here.', S, label='Investment Thesis'))
story.append(PageBreak())

# ── CHARTS ─────────────────────────────────────────────────
img = bar_chart(
    categories=['Q1','Q2','Q3','Q4'],
    values=[120000, 145000, 158400, 172000],
    title='Revenue Projection (R$)',
    ylabel='R$ Mensal',
    value_fmt='R${v:,.0f}',
)
story.append(img)
story.append(Paragraph('Figura 1 — Caption here.', S['caption']))
story.append(PageBreak())

# ── BUILD ───────────────────────────────────────────────────
build_document(
    output_path='/mnt/user-data/outputs/My_Report_2026.pdf',
    story=story,
    report_title='SHORT HEADER TITLE',
    report_client='Estamina / Sebrae Bahia',
    report_year='2026',
    cover_fn=my_cover,
)
─────────────────────────────────────────────────────────────
"""
