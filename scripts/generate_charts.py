#!/usr/bin/env python3
"""Generate engagement charts from notes.json for brand research reports."""

import json
import argparse
import os
import sys


def setup_chinese_font():
    """Configure matplotlib for Chinese text rendering."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    # macOS and Linux Chinese font candidates
    candidates = [
        'PingFang SC', 'Heiti SC', 'STHeiti', 'Songti SC',
        'Noto Sans SC', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei',
        'Microsoft YaHei', 'Arial Unicode MS', 'SimHei',
    ]

    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams['font.sans-serif'] = [font, 'DejaVu Sans']
            break
    else:
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

    plt.rcParams['axes.unicode_minus'] = False
    return plt


def strip_emoji(text):
    """Remove emoji and special Unicode symbols that fonts can't render."""
    import re
    return re.sub(r'[\U00010000-\U0010ffff︀-️\U0001f600-\U0001f64f'
                  r'\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff'
                  r'\U00002702-\U000027b0\U000024c2-\U0001f251‍☀-➿'
                  r'\U0001f900-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff]',
                  '', text).strip()


def generate_charts(notes_path, output_dir):
    plt = setup_chinese_font()
    os.makedirs(output_dir, exist_ok=True)

    with open(notes_path, encoding='utf-8') as f:
        data = json.load(f)

    notes = data['notes']
    notes_sorted = sorted(
        notes,
        key=lambda n: n.get('likes', 0) + n.get('collects', 0),
        reverse=True,
    )
    top = notes_sorted[:12]

    # --- Chart 1: Grouped bar chart of interactions ---
    fig, ax = plt.subplots(figsize=(12, 7))

    titles = [
        strip_emoji(n['title'])[:10] + '..' if len(strip_emoji(n['title'])) > 10 else strip_emoji(n['title'])
        for n in top
    ]
    x = list(range(len(titles)))
    w = 0.25

    ax.bar([i - w for i in x], [n.get('likes', 0) for n in top],
           w, label='点赞', color='#1a1a1a')
    ax.bar(x, [n.get('collects', 0) for n in top],
           w, label='收藏', color='#737373')
    ax.bar([i + w for i in x], [n.get('comments', 0) for n in top],
           w, label='评论', color='#d4d4d4')

    ax.set_xticks(x)
    ax.set_xticklabels(titles, rotation=45, ha='right', fontsize=9)
    ax.legend(frameon=False, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('热门笔记互动数据', fontsize=14, pad=15)

    plt.tight_layout()
    path1 = os.path.join(output_dir, 'chart_interactions.jpg')
    fig.savefig(path1, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    # --- Chart 2: Scatter plot likes vs collects ---
    fig, ax = plt.subplots(figsize=(10, 8))

    likes = [n.get('likes', 0) for n in notes_sorted]
    collects = [n.get('collects', 0) for n in notes_sorted]

    ax.scatter(likes, collects, s=80, alpha=0.7, c='#1a1a1a',
               edgecolors='white', linewidth=0.5)

    max_val = max(max(likes, default=1), max(collects, default=1))
    ax.plot([0, max_val], [0, max_val], '--', color='#d4d4d4',
            label='收藏 = 点赞')

    ax.set_xlabel('点赞数', fontsize=11)
    ax.set_ylabel('收藏数', fontsize=11)
    ax.set_title('点赞 vs 收藏分布', fontsize=14, pad=15)
    ax.legend(frameon=False, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    path2 = os.path.join(output_dir, 'chart_scatter.jpg')
    fig.savefig(path2, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    print(f"Charts generated:")
    print(f"  {path1}")
    print(f"  {path2}")


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Generate brand research charts')
    p.add_argument('--notes', required=True, help='Path to notes.json')
    p.add_argument('--output', required=True, help='Output directory')
    args = p.parse_args()
    generate_charts(args.notes, args.output)
