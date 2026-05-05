# ⚡ QUICK START — Deploy in 10 Minutes

**Follow these steps exactly. Copy/paste every command.**

---

## Step 1: GitHub Setup (2 min)

Go to https://github.com/new

**Create repo with:**
- Name: `leo-pdf-mcp-vercel`
- Public ✓
- Click **Create repository**

You'll see:
```
git clone https://github.com/YOUR_USERNAME/leo-pdf-mcp-vercel.git
cd leo-pdf-mcp-vercel
```

**Copy your USERNAME and run:**
```bash
git clone https://github.com/YOUR_USERNAME/leo-pdf-mcp-vercel.git
cd leo-pdf-mcp-vercel
```

---

## Step 2: Add Files (1 min)

The files I built for you are in `/mnt/user-data/outputs/leo-pdf-mcp-vercel/`

**Download that folder and place ALL files into your local `leo-pdf-mcp-vercel/` directory:**

```
leo-pdf-mcp-vercel/
├── api/
│   └── generate_pdf.py
├── .gitignore
├── leo_reportlab_brand_kit.py
├── mcp.json
├── README.md
├── requirements.txt
└── vercel.json
```

---

## Step 3: Push to GitHub (2 min)

```bash
cd leo-pdf-mcp-vercel

git add .
git commit -m "Initial setup"
git push origin main
```

You should see:
```
Enumerating objects: XX, done.
Writing objects: 100% (XX/XX), done.
```

---

## Step 4: Deploy to Vercel (5 min)

### Install Vercel CLI
```bash
npm install -g vercel@latest
```

### Login & Deploy
```bash
vercel login
# Follow the prompts (browser will open for auth)

vercel --prod
```

When asked:
- **Set up and deploy?** → Yes
- **Project name?** → `leo-pdf-mcp-vercel`
- **Link to existing project?** → No
- **Root directory?** → `./` (just press Enter)
- **Override settings?** → No

**Wait for it to complete (~2 min).**

You'll see a green checkmark and:
```
✓ Production: https://leo-pdf-mcp-vercel.vercel.app
```

**Copy this URL. Save it.**

---

## Step 5: Test It (1 min)

Paste this into your terminal (replace `YOUR_URL` with your Vercel URL from Step 4):

```bash
curl -X POST https://leo-pdf-mcp-vercel.vercel.app/api/generate_pdf \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Report",
    "client": "Sebrae Bahia",
    "year": "2026",
    "cover_description": "Test",
    "cover_metrics": [["R$ 1", "A"], ["R$ 2", "B"], ["R$ 3", "C"], ["R$ 4", "D"]],
    "content": {"sections": [{"type": "h1", "text": "Test"}, {"type": "body", "text": "Body"}]}
  }'
```

**Expected response:**
```json
{
  "success": true,
  "filename": "Test_Report_2026.pdf",
  "message": "PDF generated successfully"
}
```

If you see that → **You're done! ✅**

---

## Step 6: Connect to Claude (1 min)

Go to **Claude.ai → Settings → Connectors → Add Connector**

Fill in:
- **Name:** `Leo PDF Generator`
- **API URL:** `https://leo-pdf-mcp-vercel.vercel.app/api/generate_pdf`
- **Auth:** None
- **MCP Manifest:** `https://leo-pdf-mcp-vercel.vercel.app/mcp.json`

Click **Save**.

---

## You're Live! 🚀

Now in **any Claude conversation**, type:

```
Build a PDF report with title "My Report" and 
cover metrics showing [R$ 158K, R$ 177K, 6.7 mo, 16.6%].
Include a bar chart with Q1-Q4 values [120, 145, 158, 172].
Use generate_pdf_report tool.
```

Claude will call your Vercel API and give you a download link.

---

## If Anything Breaks

```bash
# Check deployment status
vercel --prod

# View logs
vercel logs https://leo-pdf-mcp-vercel.vercel.app

# Force redeploy
vercel --prod --force
```

---

**Questions? Check the full README.md for detailed docs.**
