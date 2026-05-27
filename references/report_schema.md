# report_data.json Schema

## Top-level

```json
{
  "meta": { ... },
  "sections": [ ... ]
}
```

## meta

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | string | Yes | Report title (e.g. "TIME 韩国时装品牌调研") |
| subtitle | string | Yes | Subtitle line |
| date | string | Yes | Research date (YYYY-MM-DD) |
| cover_image | string | No | Cover image filename from images/ directory |

## sections[]

Ordered array of section objects. Each has `type` and optional `title`.

---

### type: "text"

Long-form content section. Supports markdown: **bold**, *italic*, ### headers, - lists, > blockquotes, | tables |.

```json
{
  "type": "text",
  "title": "品牌核心洞察",
  "content_md": "### 品牌基因\n\nTIME 的品牌口号为「Poetic Scenes」...\n\n### 全球化战略\n\n1. **第一步**：...\n2. **第二步**：..."
}
```

### type: "data_cards"

Grid of 4-6 metric cards.

```json
{
  "type": "data_cards",
  "title": "核心数据概览",
  "cards": [
    { "label": "品牌创立", "value": "1993", "sub": "33年历史" },
    { "label": "年销售额", "value": "2.5亿€", "sub": "韩国第一" }
  ]
}
```

### type: "note_gallery"

Top notes displayed as image cards.

```json
{
  "type": "note_gallery",
  "title": "热门笔记 Top 10",
  "notes": [
    {
      "image": "img_001.jpg",
      "title": "笔记标题",
      "url": "https://www.xiaohongshu.com/explore/{id}",
      "likes": 8665,
      "collects": 14189,
      "comments": 61,
      "author": "作者名"
    }
  ]
}
```

### type: "moodboard"

Chart/visualization images with optional caption.

```json
{
  "type": "moodboard",
  "title": "互动数据可视化",
  "images": ["chart_interactions.jpg", "chart_scatter.jpg"],
  "caption": "左：互动数据对比 | 右：点赞 vs 收藏分布"
}
```

### type: "comparison"

Competitor comparison table.

```json
{
  "type": "comparison",
  "title": "竞品对比",
  "columns": ["品牌", "所属集团", "价位段", "核心风格", "小红书声量"],
  "rows": [
    ["TIME", "Handsome", "高端", "知性优雅", "低"],
    ["Low Classic", "独立", "中端", "极简建筑感", "高"]
  ]
}
```
