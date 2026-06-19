# 念张师（Missing Mr.Zhang）开发说明

## 项目边界

本项目基于 `alchaincyf/zhangxuefeng-skill` 建立志愿填报互动网站，保留上游 `SKILL.md`、`references/`、`examples/`、`assets/` 与 MIT License。网站不得声称 skill 内容由本站原创。

产品对外定位为“非官方张雪峰风格志愿顾问”。它不是张雪峰本人，不是官方招生机构，也不能替代各省教育考试院、院校招生章程、官方投档线和人工复核。

## 本地启动

```powershell
cd D:\念张师
python app\server.py
```

打开官网 `http://127.0.0.1:8787`。

Agent 工作台位于二级页面：

```text
http://127.0.0.1:8787/agent.html
```

## DeepSeek 配置

复制 `.env.example` 的变量到你的本机环境变量或 PowerShell 会话：

```powershell
$env:DEEPSEEK_API_KEY="你的 key"
$env:DEEPSEEK_MODEL="deepseek-v4-pro"
python app\server.py
```

不要把 API Key、Server 酱 SendKey 或任何私密 token 提交到 Git。

## Vercel 部署

仓库已支持 Vercel Import：

- `vercel.json` 将构建命令设为 `python build_vercel.py`
- `build_vercel.py` 将 `app/static/` 和 `assets/` 输出到 `public/`
- `api/*.py` 与 `api/sync/schools.py` 是 Vercel Python Functions

Vercel UI 中可使用：

```text
Build Command: python build_vercel.py
Output Directory: public
Install Command: 留空
```

如果 Vercel 预览显示 404，优先检查构建日志里是否成功生成 `public/index.html`。

## 院校库同步

`POST /api/sync/schools` 只接受 `SCHOOL_SOURCE_URL` 指向的授权 JSON 数据源。支持两种格式：

Vercel 环境变量配置：

```text
Name: SCHOOL_SOURCE_URL
Value: 一个可公开访问或服务端可访问的 JSON 文件 URL
Environment: Production / Preview / Development
```

保存后 Redeploy。运行时 `/api/schools` 会优先读取该 URL；失败时回退到本地 seed。

```json
[
  { "name": "郑州大学", "province": "河南" }
]
```

或：

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

不要抓取夸克高考等商业网站页面来伪装实时权威库。若要接入这类平台，应先取得明确 API 授权或使用其正式开放能力。
