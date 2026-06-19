# 念张师（Missing Mr.Zhang）

> 非官方张雪峰风格志愿填报互动网站。基于 `alchaincyf/zhangxuefeng-skill` 的表达框架，面向普通家庭考生，把省份、选科、分数、位次、城市、专业和就业风险放回同一张决策桌。

<p align="center">
  <img src="assets/hero.gif" alt="zhangxuefeng-skill hero animation" />
</p>

## 这是什么

《念张师》（Missing Mr.Zhang）是一个本地可运行的网站原型：

- 官网首页：`/`
- 志愿填报 Agent 工作台：`/agent.html`
- DeepSeek Chat Completions 代理接口：`/api/chat`
- 院校库查询接口：`/api/schools`
- 授权院校数据源同步接口：`/api/sync/schools`

它不是张雪峰本人，不是张雪峰官方账号，也不是官方招生服务。它只使用上游 skill 的公开表达和分析框架做模拟式分析。

## 当前能力

- 使用 Python 标准库启动 Web 服务，无第三方运行依赖。
- 官网首页使用上游真实视觉资产，说明项目定位、数据纪律和来源。
- Agent 二级页面提供考生画像表单、互动对话、院校库检索和同步入口。
- DeepSeek 模型默认配置为 `deepseek-v4-pro`，可通过环境变量切换。
- 院校库同步只接受已授权 JSON 数据源，不抓取商业网站页面冒充实时权威数据库。
- 保留上游 `SKILL.md`、`references/`、`examples/`、`assets/`、`LICENSE` 和 attribution。

## 快速启动

```powershell
cd D:\念张师
python app\server.py
```

打开：

- 官网：`http://127.0.0.1:8787`
- Agent：`http://127.0.0.1:8787/agent.html`

健康检查：

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/health
```

## 部署到 Vercel

本项目已包含 Vercel 配置：

- `vercel.json`：指定 `python build_vercel.py` 为构建命令，输出目录为 `public`
- `build_vercel.py`：把 `app/static/` 和 `assets/` 复制到 Vercel 静态输出目录
- `api/`：Vercel Python Functions，提供 `/api/health`、`/api/schools`、`/api/chat`、`/api/sync/schools`

在 Vercel 导入 GitHub 仓库时，保持默认 Framework Preset 即可；如果页面要求手动填写：

```text
Build Command: python build_vercel.py
Output Directory: public
Install Command: 留空
```

第一次部署后如果预览页显示 404，通常是因为 Vercel 没有找到根目录 `index.html` 或静态输出目录。当前配置会在构建时生成 `public/index.html`，用于修复这个问题。

## DeepSeek 配置

可以在 PowerShell 会话中配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 DeepSeek API Key"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
python app\server.py
```

也可以参考 `.env.example` 管理变量。不要把 API Key、Server 酱 SendKey 或任何私密 token 提交到 Git。

## 院校库同步

生产环境应把 `SCHOOL_SOURCE_URL` 指向已授权的 JSON 数据源。支持两种格式。

数组格式：

```json
[
  { "name": "郑州大学", "province": "河南" }
]
```

对象格式：

```json
{
  "source": "authorized-provider",
  "license": "授权说明",
  "schools": [
    {
      "name": "郑州大学",
      "province": "河南",
      "city": "郑州",
      "level": "211 / 双一流",
      "type": "综合",
      "tags": ["省内龙头"],
      "officialUrl": "https://www.zzu.edu.cn/",
      "admissionUrl": "https://ao.zzu.edu.cn/"
    }
  ]
}
```

同步接口：

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/sync/schools -Method Post
```

如果配置了 `SYNC_TOKEN`，请求需要携带 `X-Sync-Token`。

## 项目结构

```text
.
├── app/
│   ├── server.py                 # Python 标准库 Web/API 服务
│   ├── data/
│   │   └── schools.seed.json      # 本地演示院校数据
│   └── static/
│       ├── index.html             # 官网首页
│       ├── agent.html             # 志愿填报 Agent 二级页面
│       ├── app.js                 # Agent 前端逻辑
│       └── styles.css             # 官网与 Agent 统一视觉系统
├── assets/                        # 上游视觉资产
├── examples/                      # 上游示例
├── references/                    # 上游研究材料
├── SKILL.md                       # 上游 skill 主文件
├── PROJECT.md                     # 项目简版说明
├── ATTRIBUTION.md                 # 来源与署名说明
└── docs/DEVELOPMENT.md            # 开发说明
```

## 责任边界

志愿填报是高风险教育决策。本站输出只能作为信息整理和决策辅助，不能替代：

- 各省教育考试院发布的招生政策和投档数据
- 院校招生章程、招生计划、专业限制和学费信息
- 官方录取分数线、位次表和征集志愿公告
- 家长、考生和人工顾问的最终复核

没有正式授权数据源时，系统只使用本地演示数据，不会声称自己拥有实时权威院校库。

## Attribution

本项目分支自：

- Upstream: [alchaincyf/zhangxuefeng-skill](https://github.com/alchaincyf/zhangxuefeng-skill)
- Original author: Huashu
- License: MIT, preserved in [`LICENSE`](LICENSE)

页面视觉参考：

- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)

本项目尊重 skill 开发者和原始资料来源，不声称上游 skill 内容由本站原创。
