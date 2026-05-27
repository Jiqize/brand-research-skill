#!/usr/bin/env python3
"""Build a magazine-style HTML report from report_data.json.

Generates a self-contained HTML file with all images embedded as base64.
Design: ELLE/杂志风 — Playfair Display serif + Helvetica Neue sans, black-and-white.
"""

import json
import argparse
import os
import base64
import re

# ─── CSS (magazine-style design system) ──────────────────────────────────────

CSS = """
:root {
  --color-primary: #000;
  --color-bg: #fff;
  --color-bg-alt: #f7f7f7;
  --color-text: #1a1a1a;
  --color-text-sec: #737373;
  --color-text-muted: #a3a3a3;
  --color-border: #e5e5e5;
  --cover-bg: #000;
  --cover-text: #fff;
  --font-serif: "Playfair Display","Noto Serif SC",Georgia,serif;
  --font-sans: "Helvetica Neue","PingFang SC","Noto Sans SC",Arial,sans-serif;
  --fs-cover: 64px;
  --fs-h2: 34px;
  --fs-h3: 20px;
  --fs-body: 15px;
  --width: 1000px;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:var(--font-sans);background:var(--color-bg);color:var(--color-text);font-size:var(--fs-body);line-height:1.6}
.container{max-width:var(--width);margin:0 auto;padding:40px 20px}
a{color:var(--color-text);text-decoration:none;transition:color .2s}
a:hover{color:var(--color-text-sec)}

/* Cover */
.cover{background:var(--cover-bg);min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;page-break-after:always}
.cover-inner{padding:40px}
.cover-inner::before{content:"";display:block;width:80px;height:1px;background:var(--cover-text);margin:0 auto 40px}
.cover-title{font-family:var(--font-serif);font-size:var(--fs-cover);font-weight:800;color:var(--cover-text);margin-bottom:16px;letter-spacing:3px;line-height:1.2}
.cover-subtitle{font-size:18px;color:rgba(255,255,255,.7);margin-bottom:8px}
.cover-date{font-size:14px;color:rgba(255,255,255,.5)}
.cover-inner::after{content:"";display:block;width:80px;height:1px;background:var(--cover-text);margin:40px auto 0}

/* Sections */
.section{padding:56px 0;border-bottom:1px solid var(--color-border)}
.section:last-child{border-bottom:none}
.section-title{font-family:var(--font-serif);font-size:var(--fs-h2);margin-bottom:32px;letter-spacing:2px}

/* Data cards */
.data-cards{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}
.card{background:var(--color-bg-alt);padding:28px;text-align:center}
.card-value{font-family:var(--font-serif);font-size:36px;font-weight:700;margin-bottom:4px}
.card-label{font-size:13px;color:var(--color-text-sec);margin-bottom:2px;text-transform:uppercase;letter-spacing:1px}
.card-sub{font-size:12px;color:var(--color-text-muted)}

/* Rich text */
.content p{margin-bottom:16px}
.content h3{font-family:var(--font-serif);font-size:var(--fs-h3);margin:28px 0 16px}
.content ul,.content ol{margin:12px 0 16px 24px}
.content li{margin-bottom:6px}
.content blockquote{border-left:3px solid var(--color-text);padding-left:20px;margin:20px 0;color:var(--color-text-sec);font-style:italic}
.content strong{font-weight:600}
.content table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px}
.content th{background:var(--color-bg-alt);padding:12px 16px;text-align:left;font-weight:600;border-bottom:2px solid var(--color-border)}
.content td{padding:12px 16px;border-bottom:1px solid var(--color-border)}

/* Note gallery */
.note-gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.note-card{overflow:hidden}
.note-card img{width:100%;height:240px;object-fit:cover;display:block}
.note-info{padding:12px 0}
.note-title{font-size:14px;font-weight:500;margin-bottom:4px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.note-meta{font-size:12px;color:var(--color-text-muted)}
.note-stats{display:flex;gap:12px;font-size:12px;color:var(--color-text-sec);margin-top:4px}

/* Moodboard */
.moodboard{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.moodboard img{width:100%;height:auto;display:block}
.moodboard-caption{font-size:13px;color:var(--color-text-muted);margin-top:12px;text-align:center}

/* Comparison table */
.comparison-table{width:100%;border-collapse:collapse;font-size:14px}
.comparison-table th{background:var(--color-bg-alt);padding:14px 16px;text-align:left;font-weight:600;border-bottom:2px solid var(--color-border);white-space:nowrap}
.comparison-table td{padding:14px 16px;border-bottom:1px solid var(--color-border);vertical-align:top}
.comparison-table tr:hover td{background:var(--color-bg-alt)}

@media print{
  .cover{min-height:auto;padding:120px 40px}
  .section{page-break-inside:avoid}
}
"""


# ─── Helpers ──────────────────────────────────────────────────────────────────

def img_to_b64(path):
    """Read an image file and return a data-URI base64 string."""
    if not os.path.exists(path):
        return ''
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode()
    return f'data:image/jpeg;base64,{data}'


def render_md(text):
    """Minimal markdown → HTML converter (good enough for report content)."""
    # Bold / italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    # Blockquote
    text = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', text, flags=re.MULTILINE)

    # Unordered list
    lines = text.split('\n')
    out = []
    in_ul = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('- '):
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            out.append(f'<li>{stripped[2:]}</li>')
        else:
            if in_ul:
                out.append('</ul>')
                in_ul = False
            out.append(line)
    if in_ul:
        out.append('</ul>')
    text = '\n'.join(out)

    # Ordered list
    text = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', text, flags=re.MULTILINE)

    # Table
    lines = text.split('\n')
    out = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if not in_table:
                out.append('<table>')
                out.append('<tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
                in_table = True
            elif all(set(c) <= set('-: ') for c in cells):
                pass  # separator
            else:
                out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        else:
            if in_table:
                out.append('</table>')
                in_table = False
            out.append(line)
    if in_table:
        out.append('</table>')
    text = '\n'.join(out)

    # Paragraphs
    paras = text.split('\n\n')
    html = []
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<'):
            html.append(p)
        else:
            html.append(f'<p>{p}</p>')
    return '\n'.join(html)


# ─── Section renderers ───────────────────────────────────────────────────────

def render_text(section):
    return f'<div class="content">{render_md(section["content_md"])}</div>'


def render_data_cards(section):
    cards = ''.join(
        f'<div class="card">'
        f'<div class="card-label">{c["label"]}</div>'
        f'<div class="card-value">{c["value"]}</div>'
        f'<div class="card-sub">{c["sub"]}</div>'
        f'</div>'
        for c in section['cards']
    )
    return f'<div class="data-cards">{cards}</div>'


def render_note_gallery(section, images_dir):
    items = []
    for n in section['notes']:
        src = img_to_b64(os.path.join(images_dir, n['image']))
        img_tag = f'<img src="{src}" alt="{n["title"]}">' if src else ''
        items.append(
            f'<div class="note-card">'
            f'{img_tag}'
            f'<div class="note-info">'
            f'<div class="note-title"><a href="{n["url"]}" target="_blank">{n["title"]}</a></div>'
            f'<div class="note-meta">{n["author"]}</div>'
            f'<div class="note-stats">'
            f'<span>♡ {n["likes"]}</span>'
            f'<span>★ {n["collects"]}</span>'
            f'<span>✎ {n["comments"]}</span>'
            f'</div></div></div>'
        )
    return f'<div class="note-gallery">{"".join(items)}</div>'


def render_moodboard(section, ai_images_dir):
    imgs = ''.join(
        f'<img src="{img_to_b64(os.path.join(ai_images_dir, name))}" alt="{name}">'
        for name in section['images']
    )
    caption = f'<div class="moodboard-caption">{section["caption"]}</div>' if section.get('caption') else ''
    return f'<div class="moodboard">{imgs}</div>{caption}'


def render_comparison(section):
    header = '<tr>' + ''.join(f'<th>{c}</th>' for c in section['columns']) + '</tr>'
    rows = ''.join(
        '<tr>' + ''.join(f'<td>{c}</td>' for c in row) + '</tr>'
        for row in section['rows']
    )
    return f'<table class="comparison-table">{header}{rows}</table>'


# ─── Main builder ────────────────────────────────────────────────────────────

def build_report(data_path, images_dir, ai_images_dir, output_path):
    with open(data_path, encoding='utf-8') as f:
        report = json.load(f)

    meta = report['meta']
    sections = report['sections']

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    parts = [
        '<!DOCTYPE html><html lang="zh-CN"><head>',
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,800;1,400&display=swap" rel="stylesheet">',
        f'<title>{meta["title"]}</title>',
        f'<style>{CSS}</style>',
        '</head><body>',
    ]

    # Cover
    parts.append('<div class="cover"><div class="cover-inner">')
    parts.append(f'<div class="cover-title">{meta["title"]}</div>')
    if meta.get('subtitle'):
        parts.append(f'<div class="cover-subtitle">{meta["subtitle"]}</div>')
    if meta.get('date'):
        parts.append(f'<div class="cover-date">{meta["date"]}</div>')
    parts.append('</div></div>')

    parts.append('<div class="container">')

    for sec in sections:
        stype = sec['type']
        stitle = sec.get('title', '')

        parts.append('<div class="section">')
        if stitle:
            parts.append(f'<h2 class="section-title">{stitle}</h2>')

        if stype == 'text':
            parts.append(render_text(sec))
        elif stype == 'data_cards':
            parts.append(render_data_cards(sec))
        elif stype == 'note_gallery':
            parts.append(render_note_gallery(sec, images_dir))
        elif stype == 'moodboard':
            parts.append(render_moodboard(sec, ai_images_dir))
        elif stype == 'comparison':
            parts.append(render_comparison(sec))

        parts.append('</div>')

    parts.append('</div></body></html>')

    html = '\n'.join(parts)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Report generated: {output_path}")
    print(f"  Size: {len(html) / 1024:.0f} KB")


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Build brand research HTML report')
    p.add_argument('--data', required=True, help='Path to report_data.json')
    p.add_argument('--images', default='images/', help='Path to note images directory')
    p.add_argument('--ai-images', default='ai_images/', help='Path to chart images directory')
    p.add_argument('--output', default='output/report.html', help='Output HTML file path')
    args = p.parse_args()
    build_report(args.data, args.images, args.ai_images, args.output)
