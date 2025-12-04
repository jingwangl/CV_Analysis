# CV Analysis - 智能简历分析系统

基于阿里云 Serverless (函数计算 FC) 的简历分析 RESTful API 服务。

## 功能特性

### 1. 简历上传与解析
- 支持 PDF 格式简历上传
- 多页 PDF 解析支持
- 文本清洗和结构化处理

### 2. 关键信息提取
- **基本信息**: 姓名、电话、邮箱、地址
- **其他信息**: 求职意向、工作年限、学历背景
- **技能标签**: 自动识别技术技能

### 3. 简历评分与匹配
- 岗位需求关键词提取
- 技能匹配度计算
- 工作经验相关性分析
- 学历匹配度分析

### 4. 结果返回
- JSON 格式结构化输出
- 匹配度评分和建议
- 内存缓存支持

## 项目结构

```
CVAnalysis/
├── backend/
│   ├── s.yaml                    # Serverless Devs 配置
│   ├── requirements.txt          # Python 依赖
│   └── code/
│       ├── index.py              # API 入口
│       ├── resume_parser.py      # PDF 解析模块
│       ├── info_extractor.py     # 信息提取模块
│       ├── matcher.py            # 匹配评分模块
│       └── skills.py             # 技能关键词库
├── frontend/
│   ├── index.html                # 前端页面
│   ├── style.css                 # 样式文件
│   └── script.js                 # 交互脚本
└── README.md
```

## 部署指南

### 后端部署 (阿里云函数计算)

#### 前置条件
1. 安装 [Serverless Devs](https://www.serverless-devs.com/)
2. 配置阿里云账号

```bash
# 安装 Serverless Devs
npm install -g @serverless-devs/s

# 配置阿里云账号
s config add

# 选择 alibaba 云厂商，输入 AccessKey ID 和 AccessKey Secret
```

#### 部署步骤

```bash
# 进入后端目录
cd backend

# 部署到阿里云函数计算
s deploy
```

#### 部署成功后
部署成功会输出函数的 HTTP 触发器 URL，格式类似：
```
https://cv-analysis-api-xxxxx.cn-hangzhou.fcapp.run
```

### 前端部署 (GitHub Pages)

#### 方法一: 直接部署到 GitHub Pages

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/cv-analysis.git
   git push -u origin main
   ```

2. **配置 GitHub Pages**
   - 进入仓库 Settings → Pages
   - Source 选择 "Deploy from a branch"
   - Branch 选择 `main`，目录选择 `/frontend`
   - 点击 Save

3. **更新 API 地址**
   
   编辑 `frontend/script.js`，将 `API_BASE_URL` 更新为你的函数计算 URL：
   ```javascript
   const API_BASE_URL = 'https://your-fc-endpoint.cn-hangzhou.fcapp.run';
   ```

4. **访问**
   
   页面会部署到: `https://your-username.github.io/cv-analysis/`

#### 方法二: 使用 GitHub Actions 自动部署

1. 创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend
```

### 前端部署 (其他选择)

#### Vercel 部署
```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署前端
cd frontend
vercel
```

#### Netlify 部署
1. 登录 [Netlify](https://www.netlify.com/)
2. 拖拽 `frontend` 文件夹到 Netlify 部署面板

## API 文档

### 健康检查

```
GET /health
```

响应示例：
```json
{
    "success": true,
    "message": "简历分析 API 服务运行正常",
    "version": "1.0.0"
}
```

### 上传并解析简历

```
POST /upload
Content-Type: application/json

{
    "file": "<base64-encoded-pdf>"
}
```

响应示例：
```json
{
    "success": true,
    "message": "简历解析成功",
    "data": {
        "cache_key": "abc123...",
        "raw_text": "简历文本内容...",
        "pages": [...],
        "extracted_info": {
            "basic_info": {
                "name": "张三",
                "phone": "13800138000",
                "email": "example@email.com",
                "address": "北京市"
            },
            "optional_info": {
                "job_intention": "软件工程师",
                "experience_years": "3年",
                "education": "本科"
            },
            "skills": ["Python", "Java", "MySQL"]
        }
    }
}
```

### 简历与岗位匹配

```
POST /match
Content-Type: application/json

{
    "cache_key": "abc123...",
    "job_description": "招聘 Python 后端开发工程师，要求3年以上经验..."
}
```

或直接提供简历数据：
```json
{
    "resume_text": "简历文本...",
    "extracted_info": {...},
    "job_description": "岗位描述..."
}
```

响应示例：
```json
{
    "success": true,
    "message": "匹配分析完成",
    "data": {
        "overall_score": 75.5,
        "skill_match": {
            "score": 80,
            "matched_skills": ["Python", "MySQL"],
            "missing_skills": ["Docker"],
            "extra_skills": ["Java"]
        },
        "experience_match": {
            "score": 100,
            "analysis": "满足经验要求"
        },
        "education_match": {
            "score": 100,
            "analysis": "满足学历要求"
        },
        "recommendations": [
            "建议补充 Docker 相关技能"
        ]
    }
}
```

## 本地开发

### 后端本地测试

```bash
cd backend/code

# 安装依赖
pip install -r ../requirements.txt

# 本地运行 (需要实现简单的 HTTP 服务器)
python -c "
from index import handler
import json

# 测试健康检查
event = {'httpMethod': 'GET', 'path': '/health'}
result = handler(event, None)
print(json.dumps(json.loads(result['body']), indent=2, ensure_ascii=False))
"
```

### 前端本地测试

```bash
cd frontend

# 使用任意静态文件服务器
# Python
python -m http.server 8080

# 或 Node.js
npx serve
```

访问 `http://localhost:8080` 进行测试。

## 常见问题

### Q: CORS 错误？
A: 确保函数计算的 HTTP 触发器配置了正确的 CORS 头，代码中已包含 CORS 处理。

### Q: PDF 解析失败？
A: 确保上传的是有效的 PDF 文件，且文件大小不超过限制。某些扫描版 PDF 可能无法正确提取文字。

## 技术栈

- **后端**: Python 3.10, 阿里云函数计算 FC
- **PDF 解析**: PyMuPDF (fitz)
- **前端**: 原生 HTML/CSS/JavaScript
- **部署**: Serverless Devs, GitHub Pages

## License

MIT License

