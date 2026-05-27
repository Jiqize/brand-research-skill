---
name: brand-research
description: >
  Generate comprehensive visual brand research reports combining 小红书 social listening data with web research.
  Produces a magazine-quality HTML/PDF report with data cards, note galleries, engagement charts,
  competitive analysis, and strategic insights. Use this skill whenever the user wants to:
  research a brand (品牌调研), analyze brand presence on 小红书, create a competitive brand analysis,
  produce a visual brand deck, or investigate any brand's market position. Also triggers for fashion
  brand analysis, Korean/Chinese designer brand research, 小红书品牌分析, or any request involving
  小红书 data for brand intelligence. Even casual mentions like "帮我看看XX品牌" should trigger this skill.
---

# Brand Research Report Generator

Generate a magazine-quality brand research report from 小红书 data + web research.

## What This Skill Produces

A complete brand research package saved to `~/Desktop/output/<brand>品牌调研/`:

```
<brand>品牌调研/
├── notes.json              # 小红书 note data
├── images/                 # Downloaded note images (img_001.jpg ~ img_NNN.jpg)
├── ai_images/              # Generated data visualization charts
│   ├── chart_interactions.jpg
│   └── chart_scatter.jpg
├── report_data.json        # Structured report content
└── output/
    ├── report.html         # Magazine-style HTML report (self-contained, images embedded)
    ├── report.pdf          # PDF version
    └── (screenshot PNG saved to parent output directory)
```

## Input

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `brand_name` | Yes | — | Brand to research |
| `keywords` | No | Auto | 小红书 search keyword groups |
| `focus` | No | General | Research focus area |
| `output_dir` | No | `~/Desktop/output/<brand>品牌调研` | Output directory |

---

## Phase 1: Data Collection

### 1.1 Create output directory

```bash
mkdir -p <output_dir>/{images,ai_images,output}
```

### 1.2 Define search keywords

Generate 4-5 keyword groups. Use this pattern:

| Group | Pattern | Example (TIME brand) |
|-------|---------|---------------------|
| Brand + Category | `{brand}{品类}` | TIME韩国时装 |
| Brand + Style | `{brand}穿搭` | TIME品牌穿搭 |
| Brand + Event | `{brand}秀场` | TIME秀场 |
| Brand + Role | `{brand}设计师` | TIME韩国设计师 |
| Brand + Season | `{brand} {season}系列` | TIME 2025秋冬 |

### 1.3 Search 小红书 and collect notes

For each keyword group, search and collect notes. Target **10-15 high-quality notes** total, sorted by engagement (`likes + collects`).

Use whatever 小红书 tool is available. **Recommended order:**

1. **Playwright browser** (most reliable) — Navigate to search page, extract DOM with JS:
   ```
   Navigate to: https://www.xiaohongshu.com/search_result?keyword={keyword}&source=web_search_result_notes
   Wait 3 seconds, then run the extraction JS below
   ```
   Extraction JS (use `browser_evaluate`):
   ```javascript
   () => {
     const notes = document.querySelectorAll('section.note-item');
     const results = [];
     notes.forEach(el => {
       if (el.classList.contains('query-note-item')) return;
       const title = (el.querySelector('.title, .title span')?.textContent || '').trim();
       const author = (el.querySelector('.name, .nick-name')?.textContent || '').trim();
       const likes = (el.querySelector('.count, .like-count')?.textContent || '0').trim();
       const href = el.querySelector('a[href*="/explore/"]')?.getAttribute('href') || '';
       const noteId = href.match(/\/explore\/([a-zA-Z0-9]+)/)?.[1] || '';
       const cover = el.querySelector('img')?.getAttribute('src') || '';
       if (noteId) results.push({ title, author, likes: parseInt(likes)||0, note_id: noteId, cover });
     });
     return JSON.stringify(results);
   }
   ```
   Note: Requires user to scan QR login first if session is not active.

2. **OpenCLI** (`~/Desktop/git/opencli`) — `node dist/main.js xiaohongshu search "keyword" -f json --limit 20`

3. **Web search** — fallback, limited by search engine indexing of 小红书

After collecting from all keyword groups, deduplicate by `note_id`, sort by `likes` descending, keep top 15.

Save as `notes.json`:
```json
{
  "notes": [
    {
      "id": "note_id",
      "title": "笔记标题",
      "content": "完整正文",
      "url": "https://www.xiaohongshu.com/explore/{id}",
      "likes": 0,
      "collects": 0,
      "comments": 0,
      "author": "作者名",
      "images": ["url1", "url2"]
    }
  ]
}
```

### 1.4 Download images

Download the **first image** from each note. Number sequentially: `img_001.jpg`, `img_002.jpg`, ...

```bash
curl -s -o images/img_001.jpg "image_url_here"
```

Keep a mapping of note index → image filename for `report_data.json` references.

### 1.5 Web research for brand background

Search the web for supplementary brand information. Target sources:
- Brand official site
- Fashion media (WWD, Vogue Business, BoF)
- Business media (Korea Times, KED Global, 品牌方舟)
- Industry reports

Collect: founding year, ownership/group, revenue, creative director, international expansion, recent collections, key milestones.

---

## Phase 2: Analysis

### 2.1 Categorize notes

Classify each note into categories. Common types:

| Category | Example Topics |
|----------|---------------|
| Shopping Guide | 首尔购物攻略, 汉南洞必逛, 买手店集合 |
| Brand Review | 韩国品牌排名, 设计师评测, 从夯到拉 |
| Brand Feature | 秀场报道, 新系列介绍, 品牌故事 |
| Cultural/Location | 建筑设计, 城市探索, 旗舰店打卡 |

### 2.2 Calculate metrics

Compute for the note set:
- Total engagement (likes + collects + comments)
- Average likes, collects, comments per note
- **Save-to-like ratio** (collects / likes) — ratio > 1.0 indicates high purchase intent
- **Comment-to-like ratio** — high ratio indicates discussion/controversy
- Category distribution (count + percentage)

### 2.3 Identify competitors

Based on brand positioning, identify 4-5 competitor brands. Compare across:
- Ownership (group vs independent)
- Price segment
- Core style/aesthetic
- International presence
- 小红书 voice (high/medium/low)

### 2.4 Extract insights

Identify 3-4 key findings:
- How is the brand perceived on 小红书? (Direct mentions vs. indirect exposure through guides)
- What content types drive the most engagement?
- Brand strengths and gaps in the Chinese market
- Strategic recommendations

---

## Phase 3: Report Generation

### 3.1 Write report_data.json

Create `report_data.json` following the schema in `references/report_schema.md`.

Required sections in order:
1. **text: 研究背景与方法** — research scope, keyword groups, methodology
2. **data_cards: 核心数据概览** — 4-6 key metrics (founding year, revenue, sample size, engagement)
3. **text: 品牌核心洞察** — brand DNA, strategy, recent developments (use markdown subsections)
4. **note_gallery: 热门笔记 Top N** — top 8-10 notes with images, sorted by engagement
5. **text: 内容主题拆解** — content category analysis with table, key findings
6. **moodboard: 互动数据可视化** — references to chart images
7. **comparison: 竞品对比** — competitor comparison table
8. **text: 研究结论与建议** — core conclusions + actionable recommendations

### 3.2 Generate charts

```bash
python3 <skill-path>/scripts/generate_charts.py \
  --notes <output_dir>/notes.json \
  --output <output_dir>/ai_images/
```

Produces:
- `chart_interactions.jpg` — grouped bar chart (likes, collects, comments for top notes)
- `chart_scatter.jpg` — scatter plot of likes vs collects with diagonal reference line

Requires: `matplotlib` (`pip install matplotlib` if missing)

### 3.3 Build HTML report

```bash
python3 <skill-path>/scripts/build_report.py \
  --data <output_dir>/report_data.json \
  --images <output_dir>/images/ \
  --ai-images <output_dir>/ai_images/ \
  --output <output_dir>/output/report.html
```

The HTML is self-contained (images embedded as base64). Uses Playfair Display serif font + Helvetica Neue sans-serif, black-and-white magazine aesthetic.

### 3.4 Convert to PDF

Use Playwright browser to print HTML to PDF:

```javascript
async (page) => {
  await page.goto('file:///<absolute-path-to-report.html>', { waitUntil: 'networkidle0' });
  await page.pdf({ path: '<output_dir>/output/report.pdf', format: 'A4', printBackground: true, margin: { top: '0', bottom: '0', left: '0', right: '0' } });
  return 'PDF saved';
}
```

### 3.5 Take screenshot for sharing

Use Playwright to capture a full-page PNG:

1. Set viewport width to 1000px
2. Navigate to `file:///<path-to-report.html>`
3. Take full-page screenshot
4. Save as `~/Desktop/output/<brand>品牌调研.png`

---

## Quality Checklist

Before delivering, verify:
- [ ] At least 10 notes collected with complete data
- [ ] Note images downloaded successfully
- [ ] `report_data.json` has all 8 required sections
- [ ] Charts render with readable Chinese text
- [ ] HTML report opens correctly in browser
- [ ] PDF is properly formatted with no clipped content
- [ ] Screenshot PNG captured and saved to output directory

## Adapting to Different Tools

This skill is tool-agnostic for data collection. The agent should use whatever 小红书 access is available:

- **OpenCLI** (`~/Desktop/git/opencli`) — CLI tool for 小红书 search
- **MCP servers** — any configured 小红书 MCP tools
- **Web search + scraping** — fallback if no direct access

The critical contract is the `notes.json` format — as long as data arrives in that structure, the rest of the pipeline works identically.
