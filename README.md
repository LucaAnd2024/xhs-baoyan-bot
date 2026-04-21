# xhs-baoyan-bot

小红书保研情报追踪机器人

## 功能

每天自动搜索小红书上的计算机保研夏令营信息，包括：
- 6 个关键词搜索（夏令营、弱 com 分析、厦大、中科院等）
- 10 个保研博主的最新帖子追踪

结果输出为 Markdown 文件，并通过 Cron Job 推送到 Telegram。

## 环境要求

- Node.js + npm
- rednote-mcp (`npm install -g rednote-mcp`)
- Python 3
- 代理（Clash，默认端口 7897）

## 安装

```bash
# 1. 安装 rednote-mcp
npm install -g rednote-mcp

# 2. 初始化登录（需要代理）
HTTP_PROXY=http://127.0.0.1:7897 HTTPS_PROXY=http://127.0.0.1:7897 rednote-mcp init 60

# 3. 修改脚本中的 PROXY 地址（如有必要）
PROXY = "http://127.0.0.1:7897"

# 4. 运行
python3 xhs_baoyan.py
```

## 主要依赖

- `rednote-mcp`: 通过 Playwright 操控小红书网页版
- 小红书账号登录态（cookie 保存在 `~/.mcp/rednote/cookies.json`）

## 踩坑记录

详见博客文章：[《用 Agent + MCP 搭建小红书保研情报追踪机器人》](https://luca-wiki.tech/blog/rednote-mcp-guide)

## License

MIT
