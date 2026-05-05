---
name: leo-pdf-brand-kit
description: >
  Use this skill whenever Leo (Leonardo Teles) asks to create a PDF report,
  executive brief, feasibility study, or any formal document output as a .pdf file.
  This skill enforces Leo's visual brand system (NAVY/TEAL/GOLD palette), 
  standardised chart patterns via matplotlib, HeaderFooterCanvas, cover page 
  template, KPI boxes, callout boxes, SCR narrative blocks, and all reusable 
  layout components. Always read this skill before writing any reportlab/matplotlib 
  code. Trigger on: "create a PDF report", "build a report", "make a brief", 
  "produce a PDF", "turn this into a report", any request for a .pdf deliverable, 
  or any request to analyse/present data in a polished document format.
  Also trigger when Leo uploads a document and asks for it to be turned into
  a professional PDF report.
license: Proprietary — Leo T / Estamina
---

# Leo PDF Brand Kit — ReportLab + Matplotlib Production Guide

## 0. PHILOSOPHY

Every PDF you produce for Leo must look like it came from a McKinsey/Estamina 
boutique practice. No generic reportlab defaults. Apply this skill completely — 
do not skip any section.

The output must always be placed at `/mnt/user-data/outputs/` and presented 
with `present_files`.

---

## 1. BRAND PALETTE (MANDATORY — never deviate)

```python
from reportlab.lib.colors import HexColor

NAVY      = HexColor('#0D2137')   # Primary — headings, cover bg, table headers
TEAL      = HexColor('#00788A')   # Accent — rules, chart primary, callout borders
GOLD      = HexColor('#C8982A')   # Accent — highlights, payback markers, warnings
LIGHT_BG  = HexColor('#F4F7F9')   # Section backgrounds, alternating rows
MID_GREY  = HexColor('#7F8C9A')   # Captions, sub-labels, secondary text
DARK_TEXT = HexColor('#1A2A3A')   # Body text
WHITE     = HexColor('#FFFFFF')
RULE_CLR  = HexColor('#D0DCE4')   # Grid lines, borders
```

Matplotlib charts must use the same palette:
```python
CHART_PALETTE = ['#0D2137', '#00788A', '#C8982A', '#4A90B8', '#7F8C9A', '#A8C0CC', '#D0DCE4']
```

All matplotlib figures must set `facecolor='white'` and use:
```python
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=0)
ax.set_facecolor('white')
```

---

## 2. PAGE SETUP

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm

W, H = A4   # 595.27 x 841.89 pts
MARGINS = dict(leftMargin=40, rightMargin=40, topMargin=38, bottomMargin=28)
```

Always use `SimpleDocTemplate` with these margins.

---

## 3. TYPOGRAPHY STYLES (build_styles function)

Always define and call `build_styles()` before building the story:

```python
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

def build_styles():
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
            leading=14, leftIndent=14, spaceAfter=3),
    }
```

---

## 4. HEADER / FOOTER CANVAS (MANDATORY on all content pages)

Always use this pattern — never skip it:

```python
from reportlab.pdfgen import canvas

class HeaderFooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, page_count):
        page = self._pageNumber
        if page == 1:
            draw_cover(self)   # See Section 5
            return

        # Header — NAVY bar with TEAL left accent
        self.saveState()
        self.setFillColor(NAVY)
        self.rect(0, H - 28, W, 28, fill=1, stroke=0)
        self.setFillColor(TEAL)
        self.rect(0, H - 28, 4, 28, fill=1, stroke=0)
        self.setFont('Helvetica-Bold', 8)
        self.setFillColor(WHITE)
        self.drawString(14, H - 18, REPORT_TITLE.upper())   # Set REPORT_TITLE as constant
        self.setFont('Helvetica', 8)
        self.drawRightString(W - 14, H - 18, 'CONFIDENCIAL  |  ' + REPORT_YEAR)

        # Footer — NAVY bar with TEAL/GOLD rule
        self.setFillColor(NAVY)
        self.rect(0, 0, W, 20, fill=1, stroke=0)
        self.setFillColor(GOLD)
        self.rect(0, 0, W * 0.3, 3, fill=1, stroke=0)
        self.setFillColor(TEAL)
        self.rect(W * 0.3, 0, W * 0.7, 3, fill=1, stroke=0)
        self.setFont('Helvetica', 7)
        self.setFillColor(WHITE)
        self.drawString(14, 6, REPORT_CLIENT)
        self.drawRightString(W - 14, 6, f'Página {page} de {page_count}')
        self.restoreState()
```

Set these constants at top of each script:
```python
REPORT_TITLE = 'SHORT REPORT TITLE HERE'   # Max ~60 chars
REPORT_YEAR  = '2026'
REPORT_CLIENT = 'Organisation / Context'
```

---

## 5. COVER PAGE TEMPLATE

Always draw a bespoke cover using the canvas. Page 1 of `story` must be:
```python
story.append(Spacer(1, 1))
story.append(PageBreak())
```

The `draw_cover(c_obj)` function must include:
- Full NAVY background (`c_obj.rect(0, 0, W, H, fill=1, stroke=0)`)
- TEAL left accent stripe + GOLD right accent at bottom (6mm height)
- Category label line in GOLD (small caps)
- TEAL horizontal rule under the category label
- Main title in WHITE Helvetica-Bold 26pt
- Sub-title in TEAL 13pt
- GOLD short divider rule (40px wide)
- **4 KPI metric boxes** in a row showing the report's headline numbers
  (background `#0A1D2E`, TEAL/GOLD left accent alternating, value in WHITE Bold 14pt)
- Description paragraph in `#A8C0CC` 9pt (3-line max)
- Footer: location + date left; "Confidencial — Uso Restrito" right in MID_GREY

Template structure:
```python
def draw_cover(c_obj, title_line1, title_line2, subtitle, 
               metrics,    # list of (value_str, label_str) — exactly 4
               description, location='Salvador, Bahia, Brasil', year='2026'):
    c_obj.saveState()
    # ... (full implementation as in the airport report)
    c_obj.restoreState()
```

---

## 6. REUSABLE COMPONENTS

### Section Rule
```python
from reportlab.platypus import HRFlowable

def section_rule(color=TEAL):
    return HRFlowable(width='100%', thickness=1.5, color=color, 
                      spaceAfter=6, spaceBefore=2)
```

### Callout Box
```python
from reportlab.platypus import Table, TableStyle

def callout_box(text, styles, bg=LIGHT_BG, border=TEAL, label=None):
    content = []
    if label:
        content.append(Paragraph(f'<b>{label}</b>', 
            ParagraphStyle('cl', parent=styles['body'],
            textColor=border, fontSize=8, fontName='Helvetica-Bold', spaceAfter=3)))
    content.append(Paragraph(text, styles['body']))
    t = Table([[content]], colWidths=[W - 80 - 30])
    t.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), bg),
        ('LINEBEFORE',   (0,0), (0,-1), 3, border),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING',   (0,0), (-1,-1), 10),
        ('BOTTOMPADDING',(0,0), (-1,-1), 10),
    ]))
    return t
```

### KPI Row (4 cells)
Each KPI cell: LIGHT_BG background, value in brand colour (TEAL/GOLD/NAVY), 
label in MID_GREY, 2pt coloured bottom rule. Width: 123pt per cell.

### Styled Data Table
```python
def styled_table(header_cells, data_rows, col_widths):
    """header_cells = list of Paragraph objects"""
    t = Table([header_cells] + data_rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,0), NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
        ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,-1), 8),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ('TOPPADDING',    (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING',   (0,0), (-1,-1), 8),
        ('RIGHTPADDING',  (0,0), (-1,-1), 8),
        ('GRID',          (0,0), (-1,-1), 0.4, RULE_CLR),
        ('LINEBELOW',     (0,0), (-1,0), 1.5, TEAL),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t
```

### Total Row (TEAL background, WHITE text)
Add as last row of any table with financial totals:
```python
('BACKGROUND', (0,-1), (-1,-1), TEAL),
('TEXTCOLOR',  (0,-1), (-1,-1), WHITE),
```

### SCR Narrative Blocks (McKinsey)
Three rows: Situação (TEAL), Complicação (RED `#C0392B`), Resolução (GOLD).
Each: 70pt label column + 390pt text column. 10pt padding all sides.

---

## 7. CHART PATTERNS

### Figure-to-Image helper (ALWAYS use)
```python
import io, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def fig_to_rl_image(fig, dpi=150, width_cm=14, height_cm=None):
    buf = io.BytesIO()
    fig.savefig(buf, format='PNG', dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close(fig)
    from reportlab.platypus import Image
    from reportlab.lib.units import cm
    if height_cm:
        return Image(buf, width=width_cm*cm, height=height_cm*cm)
    return Image(buf, width=width_cm*cm)
```

### Chart Size Standards
| Chart type         | figsize (w, h) | RL width (cm) |
|--------------------|---------------|---------------|
| Full-width bar/line | (6.5, 3.8)   | 14            |
| Half-width donut   | (5, 4)        | 8.5           |
| Side-by-side pair  | 2× (5.5, 3.6) | 8.5 each      |
| CAPEX pie          | (6, 4.5)      | 13            |
| KPI gauge row      | (7, 3.2)      | 14            |

### Side-by-side charts
```python
from reportlab.platypus import Table
pair = Table([[img_left, img_right]], colWidths=[240, 250], hAlign='CENTER')
pair.setStyle(TableStyle([('LEFTPADDING',(0,0),(-1,-1),4),
                           ('RIGHTPADDING',(0,0),(-1,-1),4)]))
story.append(pair)
```

### Always follow a chart with a caption
```python
story.append(Paragraph('Figura N — Description of what the chart shows, '
                        'including data source/period where relevant.', styles['caption']))
```

---

## 8. STANDARD PAGE STRUCTURE

Every report follows this page sequence:

| Page | Content |
|------|---------|
| 1    | Cover (canvas-drawn) |
| 2    | Executive Summary (KPI row + tese callout + 2 charts side-by-side) |
| 3    | Context / Market / Ecosystem analysis + line/bar chart |
| 4    | Product / Service / Offer analysis + mix chart + data table |
| 5    | Financial — CAPEX table + pie chart |
| 6    | Financial — OPEX/Revenue + bar chart |
| 7    | KPIs & Payback — KPI boxes + payback curve |
| 8    | Pitch / Narrative — SCR blocks + pitch metrics |
| 9    | Synthesis — 3 directives + conclusion callout + final KPI row |

Adapt structure to content — compress to fewer pages for briefs, expand for full studies.

---

## 9. INSTALLATION CHECK

Before running, always verify:
```bash
pip install reportlab matplotlib pillow --break-system-packages -q
```

---

## 10. OUTPUT NAMING CONVENTION

```
/mnt/user-data/outputs/[Topic]_[Type]_[YYYY].pdf
```

Examples:
- `Quiosque_Aeroporto_Salvador_Relatorio_Executivo.pdf`
- `Missao_China_Viabilidade_2026.pdf`
- `Estamina_Pitch_Deck_Report_2026.pdf`

---

## 11. CRITICAL DON'TS

- NEVER use default reportlab grey table headers
- NEVER use Unicode subscripts/superscripts in canvas text (use `<sub>/<super>` in Paragraphs)
- NEVER use `facecolor` other than white on matplotlib figures intended for PDF embedding
- NEVER skip the `fig_to_rl_image` helper (direct savefig without BytesIO breaks embedding)
- NEVER use `story.append(Spacer(1, H))` for cover — use `Spacer(1, 1)` + `PageBreak()`
- NEVER output a PDF without `canvasmaker=HeaderFooterCanvas` in `doc.build()`
