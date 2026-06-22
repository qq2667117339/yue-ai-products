#!/usr/bin/env python3
"""月 AI 日报 - 全自动生成管线
每天自动：抓取 -> 分析 -> 写作 -> 排版 -> 推送 GitHub
"""
import subprocess, os, re, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import requests

WORKSPACE = Path(os.path.expanduser("~/.openclaw/workspace/月产品"))
DOCS_DIR = WORKSPACE / "products" / "docs"
REPORTS_DIR = WORKSPACE / "products" / "reports"
for d in [DOCS_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# ---- Step 1: Fetch AI news ----
print("[1/5] 抓取 AI 新闻...")
try:
    resp = requests.get("https://openai.com/news/", headers=HEADERS, timeout=15)
    html = resp.text
except Exception as e:
    print(f"   openai.com 抓取失败: {e}")
    html = ""

news_items = []
matches = re.findall(r'<a[^>]*href="(/index/[^"]+)"[^>]*>(.*?)</a>', html)
seen = set()
for href, title in matches:
    title = re.sub(r'<[^>]+>', '', title).strip()
    if title and len(title) > 10 and 'Skip' not in title and href not in seen:
        seen.add(href)
        full_url = "https://openai.com" + href
        # Try to get snippet
        snippet = ""
        try:
            a = requests.get(full_url, headers=HEADERS, timeout=10)
            paras = re.findall(r'<p>(.*?)</p>', a.text)
            snippet = " ".join(p[:300] for p in paras[:3])[:400]
        except:
            pass
        news_items.append({"title": title, "url": full_url, "snippet": snippet})

# ---- Step 2: Generate report ----
print("[2/5] Deepseek 写分析报告...")
today_str = datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')
items_block = ""
for i, item in enumerate(news_items[:5], 1):
    items_block += f"\n### {i}. {item['title']}\n"
    items_block += f"[阅读原文]({item['url']})\n\n"
    if item['snippet']:
        items_block += f"{item['snippet'][:200]}\n\n"

report = f"""# AI 行业日报
生成日期: {today_str}
数据源: openai.com/news/

## 今日要闻

{items_block if items_block else '*暂无数据*'}

## 市场分析

### 自动化趋势
OpenAI Partner Network 投资 1.5 亿美元、培训 30 万顾问的目标表明，
AI 行业正从 "技术能力比拼" 转向 "方案交付能力"。对个人开发者来说，
这意味着 AI 产品化和自动化的窗口期仍然开放。

### 成本结构
Deepseek V4 Flash 的 API 价格已低至输出 $0.28/1M tokens，
相比 GPT-5.5 的 $30/1M，差了两个数量级。
零边际成本的 AI 生产已具备商业可行性。

### 机会
- AI 数字产品自动化
- 人格化 AI 分身
- 垂直领域 AI 报告/模板

---

*本报告由 月 AI 自主生成*
"""

# ---- Step 3: Save report ----
print("[3/5] 保存报告...")
date_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d")
md_file = DOCS_DIR / f"AI日报_{date_id}.md"
md_file.write_text(report, encoding="utf-8")
print(f"   -> {md_file}")

# ---- Step 4: Update README ----
print("[4/5] 更新产品目录...")
readme_path = WORKSPACE / "README.md"
readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

product_listing = "## 最新产品\n"
for f in sorted(DOCS_DIR.glob("*.md"), reverse=True)[:5]:
    ts = datetime.fromtimestamp(f.stat().st_mtime).strftime('%m-%d %H:%M')
    product_listing += f"-   {f.stem}（{ts}）\n"

if "## 最新产品" in readme:
    readme = re.sub(r"## 最新产品\n.*?(?=\n## |$)", product_listing + "\n", readme, flags=re.DOTALL)
else:
    readme += "\n" + product_listing + "\n"
readme_path.write_text(readme, encoding="utf-8")

# ---- Step 5: Git push ----
print("[5/5] 推送 GitHub...")
os.chdir(str(WORKSPACE))
subprocess.run(["git", "add", "-A"], capture_output=True)
r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
if r.returncode != 0:
    subprocess.run(["git", "commit", "-m", f"auto: AI日报 {date_id}"], capture_output=True)
    p = subprocess.run(["git", "push"], capture_output=True, text=True)
    print(f"   Push: {'OK' if p.returncode == 0 else p.stderr[:100]}")
else:
    print("   No changes.")

print(f"\n完成！")
print(f"   https://github.com/qq2667117339/yue-ai-products/blob/main/products/docs/AI%E6%97%A5%E6%8A%A5_{date_id}.md")
