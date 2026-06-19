# 念张师（Missing Mr.Zhang）

一个基于 `alchaincyf/zhangxuefeng-skill` 的非官方志愿填报互动网站原型。

## 已实现

- Python 标准库 Web 服务，无第三方依赖。
- 官网首页 `/`，使用上游真实视觉资产并介绍项目边界。
- Agent 二级页面 `/agent.html`，承载完整互动志愿填报工作台。
- 前端互动表单：省份、选科、分数、位次、家庭预算、城市和专业偏好。
- DeepSeek Chat Completions 代理接口，默认模型 `deepseek-v4-pro`。
- 院校库查询接口和授权 JSON 数据源同步接口。
- 上游 skill attribution 与 MIT License 保留。

## 启动

```powershell
cd D:\念张师
python app\server.py
```

打开官网 `http://127.0.0.1:8787`，或直接进入 Agent 页面 `http://127.0.0.1:8787/agent.html`。

更多配置见 `docs/DEVELOPMENT.md`。

## 责任边界

本项目不是张雪峰本人、官方账号或官方招生服务。志愿填报必须以各省教育考试院、院校招生章程、官方投档线和正式授权数据源为准。生产环境不得抓取未经授权的商业网站数据来冒充实时权威数据库。
