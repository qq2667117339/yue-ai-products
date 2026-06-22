import requests, re
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
resp = requests.get("https://openai.com/news/", headers=headers, timeout=15)
html = resp.text[:5000]
# Find all links and their context
matches = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]*(?:<(?!a)[^>]*>[^<]*)*)</a>', html)
print(f"Total links found: {len(matches)}")
for href, title in matches[:30]:
    title_clean = re.sub(r'<[^>]+>', '', title).strip()
    if title_clean and len(title_clean) > 5:
        print(f"  [{href[:60]}] -> {title_clean[:80]}")
