#!/usr/bin/env python3
"""小红书保研情报搜索 - 含博主追踪版"""
import subprocess, signal, os, json, time, re

PROXY = "http://127.0.0.1:7897"
OUT_FILE = "/Users/lijialiang/Projects/baoyaninfo/xiaohongshu_baoyan_notes.md"
TODAY = time.strftime("%Y-%m-%d")

KEYWORD_GROUPS = [
    ("xlyx", "计算机保研 夏令营 2026"),
    ("985rc", "985弱com 保研 经验"),
    ("qbhq", "清北华五 各学院 强弱com"),
    ("xmutj", "厦门大学 计算机 保研 夏令营"),
    ("zkyjs", "中科院 计算机 夏令营 2026"),
    ("baoyan", "保研经验分享 计算机"),
]

# 博主追踪 - 直接用博主名字搜索，不加限定词（避免过滤掉真实结果）
BLOGGERS = [
    ("wenjing", "文静是也"),
    ("huahua", "花花suki"),
    ("lili", "猫果梨梨"),
    ("tudou", "土豆学姐"),
    ("xingxing", "见过星星之后"),
    ("eric", "Eric学长"),
    ("damifan", "爱吃大米饭"),
    ("bei", "北 保研"),
    ("tutu", "涂涂 保研"),
    ("xiaomao", "忙碌小猫"),
]

def mcp_call(keyword, limit=5):
    env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": os.environ.get("HOME", "/Users/lijialiang"),
        "HTTP_PROXY": PROXY,
        "HTTPS_PROXY": PROXY,
        "http_proxy": PROXY,
        "https_proxy": PROXY,
    }
    init = json.dumps({"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"xhs","version":"1.0"}}})
    notif = json.dumps({"jsonrpc":"2.0","method":"notifications/initialized","params":{}})
    call = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_notes","arguments":{"keywords":keyword,"limit":limit}}})
    input_data = init + "\n" + notif + "\n" + call + "\n"

    proc = subprocess.Popen(
        ["/usr/local/bin/rednote-mcp", "--stdio"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        env=env, start_new_session=True
    )

    try:
        stdout, _ = proc.communicate(input=input_data.encode(), timeout=55)
        return stdout.decode("utf-8", errors="ignore")
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), 9)
        except:
            pass
        return ""

def parse_notes(raw):
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if d.get("id") == 1:
                text = d.get("result", {}).get("content", [{}])[0].get("text", "")
                if not text or "Timeout" in text or "page.goto" in text:
                    continue
                for block in re.split(r'(?=标题:)', text):
                    block = block.strip()
                    if not block:
                        continue
                    title_m = re.search(r'标题:\s*(.+?)(?:\n|$)', block)
                    url_m = re.search(r'(https://www\.xiaohongshu\.com/explore/[a-f0-9]+)', block)
                    likes_m = re.search(r'点赞:\s*(\d+)', block)
                    author_m = re.search(r'作者:\s*(.+?)(?:\n|$)', block)
                    if title_m and url_m:
                        results.append({
                            "title": title_m.group(1).strip(),
                            "url": url_m.group(1).strip(),
                            "likes": likes_m.group(1).strip() if likes_m else "?",
                            "author": author_m.group(1).strip() if author_m else ""
                        })
        except:
            continue
    return results

def main():
    lines = []
    lines.append(f"# 小红书保研情报\n\n")
    lines.append(f"> 自动采集 · {TODAY}\n\n")

    lines.append(f"## 关键词搜索\n\n")
    for label, kw in KEYWORD_GROUPS:
        print(f"[关键词] {kw}", flush=True)
        raw = mcp_call(kw, limit=5)
        notes = parse_notes(raw)
        lines.append(f"### 【{label}】 {kw}\n\n")
        if not notes:
            lines.append("(未找到相关笔记)\n\n")
            print(f"  -> 无结果")
        else:
            for n in notes:
                lines.append(f"- [{n['title']}]({n['url']}) [👍{n['likes']}]\n")
            print(f"  -> 找到 {len(notes)} 条")
        time.sleep(12)

    lines.append(f"\n## 博主追踪\n\n")
    for label, kw in BLOGGERS:
        print(f"[博主] {kw}", flush=True)
        raw = mcp_call(kw, limit=5)
        notes = parse_notes(raw)
        lines.append(f"### @{label} ({kw})\n\n")
        if not notes:
            lines.append("(未找到相关笔记)\n\n")
            print(f"  -> 无结果")
        else:
            for n in notes:
                author_str = f"[@{n['author']}]" if n['author'] else ""
                lines.append(f"- [{n['title']}]({n['url']}) {author_str} [👍{n['likes']}]\n")
            print(f"  -> 找到 {len(notes)} 条")
        time.sleep(12)

    lines.append(f"\n---\n采集时间: {TODAY}\n")

    with open(OUT_FILE, "w") as f:
        f.write("".join(lines))

    print(f"\n写入完成: {OUT_FILE}")
    with open(OUT_FILE) as f:
        print(f.read(), flush=True)

if __name__ == "__main__":
    main()
