# Leo T PDF Report Generator — Vercel MCP Server

**Complete deployment guide for setting up a serverless PDF generation service on Vercel, integrated with Claude as an MCP connector.**

---

## What This Does

Once deployed:
- Claude calls a single tool: `generate_pdf_report()`
- You pass report structure (sections, charts, data) as JSON
- Vercel serverless function generates a branded PDF in ~3 seconds
- Returns a download link (no local Python required)
- Works from any Claude conversation, any device

**Zero uploads. Zero local dependencies.**

---

## Architecture

```
You (in Claude)
    ↓
    Prompt: "Build a PDF on [topic]"
    ↓
Claude calls MCP Tool: generate_pdf_report()
    ↓
Vercel Serverless Function (Python runtime)
    ↓
leo_reportlab_brand_kit.py (all the styling)
    ↓
reportlab + matplotlib (rendering)
    ↓
PDF bytes → returned to Claude → you download
```

---

## Prerequisites

1. **Vercel account** (free tier OK) — https://vercel.com
2. **GitHub account** (to push the project repo) — https://github.com
3. **CLI tools installed:**
   ```bash
   npm install -g vercel@latest
   # or: brew install vercel-cli (if using Homebrew)
   ```

---

## Step 1: Create a GitHub Repository

1. Go to https://github.com/new
2. Create a **public** repo named `leo-pdf-mcp-vercel`
3. Clone it locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/leo-pdf-mcp-vercel.git
   cd leo-pdf-mcp-vercel
   ```

---

## Step 2: Add Project Files

Copy these files into the repo root:

```
leo-pdf-mcp-vercel/
├── api/
│   └── generate_pdf.py          (the serverless function)
├── leo_reportlab_brand_kit.py   (the styling library)
├── vercel.json                  (Vercel config)
├── requirements.txt             (Python dependencies)
├── mcp.json                     (MCP manifest for Claude)
├── .gitignore                   (ignore cache/tmp)
└── README.md                    (this file)
```

Create `.gitignore`:
```
__pycache__/
*.pyc
.vercel/
.env.local
node_modules/
```

---

## Step 3: Push to GitHub

```bash
git add .
git commit -m "Initial Vercel MCP setup for Leo PDF reports"
git push origin main
```

---

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI (Recommended)

```bash
vercel login
vercel --prod
```

Follow the prompts:
- **Project name?** → `leo-pdf-mcp-vercel`
- **Link to existing project?** → No
- **Framework?** → Other
- **Root directory?** → `./` (default)
- **Build command?** → `pip install -r requirements.txt`

Once complete, you'll see:
```
✓ Production: https://leo-pdf-mcp-vercel.vercel.app
```

**Save this URL.** You'll need it in Step 5.

### Option B: Using Vercel Web UI

1. Go to https://vercel.com/new
2. **Import Git Repository** → select your `leo-pdf-mcp-vercel` repo
3. **Framework Preset** → Python (select from dropdown)
4. **Environment Variables** → Skip for now (none needed)
5. Click **Deploy**

Wait ~2 minutes for the build to complete.

---

## Step 5: Verify the Deployment

Test the API endpoint:

```bash
curl -X POST https://leo-pdf-mcp-vercel.vercel.app/api/generate_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "client": "Sebrae Bahia",
    "year": "2026",
    "cover_description": "Test PDF generation",
    "cover_metrics": [
      ["R$ 158K", "Revenue"],
      ["R$ 177K", "CAPEX"],
      ["6.7 mo", "Payback"],
      ["16.6%", "Margin"]
    ],
    "content": {
      "sections": [
        {
          "type": "h1",
          "text": "Test Section"
        },
        {
          "type": "body",
          "text": "This is a test report body paragraph."
        }
      ]
    }
  }'
```

**Success response:**
```json
{
  "success": true,
  "filename": "Test_Report_2026.pdf",
  "message": "PDF generated successfully"
}
```

---

## Step 6: Register as Claude MCP Connector

**This is the final integration step.**

In **Claude.ai Settings → Connectors → Add Custom Connector:**

1. **Connector Name:** `Leo PDF Report Generator`
2. **API URL:** `https://leo-pdf-mcp-vercel.vercel.app/api/generate_pdf`
3. **Authentication Type:** `None (public endpoint)`
4. **MCP Manifest URL:** `https://leo-pdf-mcp-vercel.vercel.app/mcp.json`

Click **Save & Connect**.

Claude will now see the `generate_pdf_report` tool in every conversation.

---

## Step 7: Use in Claude

In **any Claude conversation**, now use it like this:

```
Build a PDF report on the Salvador Airport quiosque project.

Structure:
- Cover with metrics: [R$ 158K, R$ 177K, 6.7 mo, 16.6%]
- Executive Summary page with body text
- Chart: bar chart showing revenue by month
- Conclusions with callout

Use the generate_pdf_report tool to create the PDF.
```

Claude will automatically invoke the MCP tool and return a download link.

---

## Common Errors & Fixes

### "Module not found: leo_reportlab_brand_kit"
- Make sure `leo_reportlab_brand_kit.py` is in the **repo root** (same level as `vercel.json`)
- Redeploy: `vercel --prod`

### "ImportError: No module named 'reportlab'"
- Make sure `requirements.txt` is in the repo root
- Check that all three dependencies are listed: `reportlab`, `matplotlib`, `pillow`
- Redeploy: `vercel --prod`

### "Function timeout" (> 60 seconds)
- Large multi-page reports with many charts can exceed 60s timeout
- Solution: Split into smaller reports, or increase timeout in `vercel.json` → `maxDuration: 120`
- Edit `vercel.json`, push, redeploy

### API returns 405 Method Not Allowed
- Make sure you're doing a **POST** request (not GET)
- Check your `curl` command has `-X POST`

### PDF looks wrong / charts missing
- Check that the request JSON is valid
- Ensure `content.sections` array is not empty
- Verify chart specs have required fields (categories, values, etc.)

---

## Advanced: Custom Styling

To change brand colours or fonts:

1. Edit `leo_reportlab_brand_kit.py` at the top where colours are defined:
   ```python
   NAVY = HexColor('#0D2137')   # change hex code
   TEAL = HexColor('#00788A')   # change hex code
   ```

2. Push to GitHub:
   ```bash
   git add leo_reportlab_brand_kit.py
   git commit -m "Update brand colours"
   git push origin main
   ```

3. Redeploy:
   ```bash
   vercel --prod
   ```

---

## Advanced: Monitoring & Logs

Check deployment logs in **Vercel Dashboard**:
1. Go to https://vercel.com/dashboard
2. Select `leo-pdf-mcp-vercel`
3. **Functions** tab → `api/generate_pdf.py` → **Logs**

You can see every API call, errors, and performance metrics.

---

## Testing Payload Examples

### Example 1: Simple Report with Text

```json
{
  "title": "Test Report",
  "client": "Sebrae Bahia",
  "year": "2026",
  "subtitle": "Strategic Analysis",
  "cover_description": "A simple test report with basic sections.",
  "cover_metrics": [
    ["R$ 100K", "Metric 1"],
    ["+25%", "Growth"],
    ["12 mo", "Timeline"],
    ["95%", "Success"]
  ],
  "content": {
    "sections": [
      {"type": "h1", "text": "Introduction"},
      {"type": "body", "text": "This is the introduction paragraph."},
      {"type": "spacer", "height": 6},
      {"type": "h2", "text": "Main Findings"},
      {"type": "body", "text": "Key findings go here."}
    ]
  }
}
```

### Example 2: Report with Charts

```json
{
  "title": "Revenue Analysis",
  "client": "Estamina",
  "year": "2026",
  "cover_description": "Quarterly revenue forecast and analysis.",
  "cover_metrics": [
    ["R$ 158K", "Monthly\nRevenue"],
    ["R$ 177K", "CAPEX"],
    ["6.7 mo", "Payback"],
    ["16.6%", "Margin"]
  ],
  "content": {
    "sections": [
      {"type": "h1", "text": "Revenue Forecast"},
      {
        "type": "chart",
        "chart_type": "bar",
        "categories": ["Q1", "Q2", "Q3", "Q4"],
        "values": [120000, 145000, 158400, 172000],
        "title": "Quarterly Revenue (R$)",
        "ylabel": "R$ Mensal",
        "value_fmt": "R${v:,.0f}",
        "width_cm": 14,
        "height_cm": 5.5,
        "caption": "Figura 1 — Projected revenue growth across four quarters."
      }
    ]
  }
}
```

### Example 3: KPI Dashboard Report

```json
{
  "title": "KPI Dashboard",
  "client": "Sebrae Bahia",
  "year": "2026",
  "cover_description": "Key performance indicators for Q1 2026.",
  "cover_metrics": [
    ["8M+", "Passengers"],
    ["87%", "Food Spend"],
    ["R$80", "Avg Ticket"],
    ["46%", "Frequent Flyers"]
  ],
  "content": {
    "sections": [
      {"type": "h1", "text": "Performance Metrics"},
      {
        "type": "kpi_row",
        "kpis": [
          {"value": "R$ 26.232", "label": "Monthly\nProfit", "color": "teal"},
          {"value": "16.56%", "label": "Profit\nMargin", "color": "navy"},
          {"value": "6.7 mo", "label": "Payback", "color": "gold"},
          {"value": "+28%", "label": "YoY\nGrowth", "color": "teal"}
        ]
      },
      {"type": "spacer", "height": 8},
      {"type": "callout", "text": "All metrics show strong positive momentum across the quarter.", "label": "Key Insight"}
    ]
  }
}
```

---

## Maintenance

### Weekly
- Check Vercel logs for errors
- Monitor function execution time (target < 30s)

### Monthly
- Review Vercel usage (free tier: 100 invocations/month)
- Update dependencies if needed:
  ```bash
  pip list --outdated
  # Update version pins in requirements.txt
  git add requirements.txt && git commit -m "Update deps" && git push && vercel --prod
  ```

### Yearly
- Renew Vercel account (free tier is free forever, no renewal needed)
- Archive old deployment logs if storage fills up

---

## Support & Debugging

If something breaks:

1. **Check Vercel logs:**
   ```bash
   vercel logs https://leo-pdf-mcp-vercel.vercel.app
   ```

2. **Test the API directly:**
   ```bash
   curl -X POST https://leo-pdf-mcp-vercel.vercel.app/api/generate_pdf \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","client":"Test","year":"2026","cover_description":"Test","cover_metrics":[["A","B"],["C","D"],["E","F"],["G","H"]],"content":{"sections":[{"type":"h1","text":"Test"}]}}'
   ```

3. **Redeploy from scratch:**
   ```bash
   vercel --prod --force
   ```

---

## Done! 🎉

Your PDF generation MCP server is now live. Every time you ask Claude for a report, it will:
1. Call the Vercel API
2. Generate a branded PDF with your data
3. Return a download link

**No local Python. No file uploads. Pure cloud-native automation.**

---

**Created for Leo T — Estamina / Sebrae Bahia, 2026**
