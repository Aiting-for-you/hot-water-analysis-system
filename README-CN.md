<div align="center">
  <img src="https://raw.githubusercontent.com/Aiting-for-you/smart-water-system/main/.github/assets/logo.png" alt="logo" width="200"/>

  <h1 align="center">智能用水习惯分析与节能控制系统</h1>
  
  <p align="center">
    一个旨在通过深度数据分析，为现代楼宇提供智能化、可视化用水管理与节能策略的全栈Web应用。
  </p>
  
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-2.x-black?logo=flask&logoColor=white" alt="Flask Version">
    <img src="https://img.shields.io/badge/React-18.x-blue?logo=react&logoColor=white" alt="React Version">
    <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
    <img src="https://img.shields.io/github/last-commit/Aiting-for-you/smart-water-system" alt="last commit">
  </p>
  
  <p align="center">
    <a href="README.md">English</a> | <a href="README-CN.md">简体中文</a>
  </p>
</div>

---

## 🌟 项目简介

在现代楼宇管理中，水资源的有效利用与能源节约是两大核心挑战。"智能用水习惯分析与节能控制系统" 应运而生，它不仅仅是一个数据分析工具，更是一个决策支持平台。通过上传历史用水数据（CSV格式），系统能够自动进行多维度的深度分析，并以高度可视化的方式呈现结果，最终生成包含具体节能建议的专业分析报告。

![应用截图预览](https://raw.githubusercontent.com/Aiting-for-you/smart-water-system/main/.github/assets/preview.gif)
> *提示: 上图是一个示例GIF，您可以替换为您自己录制的应用操作录屏。*

## ✨ 核心功能

| 功能模块 | 详细描述 |
| :--- | :--- |
| **📊 数据洞察** | 支持CSV文件上传，自动完成数据清洗、转换和预处理。 |
| **🧠 智能分析** | 从**每小时**、**每周**、**不同楼栋**、**工作日与周末**等多个维度进行深入分析。|
| **📈 可视化仪表盘** | 将复杂的分析结果通过一系列直观的图表（柱状图、热力图、箱线图、饼图等）清晰展示。|
| **📄 报告自动生成** | 一键生成图文并茂的专业分析报告（Markdown格式），并支持下载为TXT文件。|
| **💡 节能策略建议** | 基于用水高峰时段，为增压泵的启停控制提供**定量的运行时间建议**和**节能比例预测**。|
| **🔒 安全与认证** | 使用 **JWT (JSON Web Tokens)** 提供安全的、基于令牌的用户注册与登录认证。|
| **🗂️ 历史追溯** | 自动保存并展示历次的分析结果，方便用户随时追溯和对比不同时期的用水模式。|

## 🚀 技术栈

| 分类 | 技术 | 描述 |
|:--- |:---|:---|
| **后端** | `Python`, `Flask`, `SQLAlchemy` | 强大的后端逻辑与数据处理能力。 |
| | `Pandas`, `NumPy`, `Scikit-learn` | 专业的数据分析与机器学习库。 |
| | `Matplotlib`, `Seaborn` | 灵活的后台图表生成。 |
| **前端** | `React`, `TypeScript` | 现代化的、类型安全的前端框架。 |
| | `Vite` | 极速的下一代前端构建工具。 |
| | `Axios` | 成熟的、基于Promise的HTTP客户端。 |
| **数据库**| `SQLite` / `PostgreSQL` | 开发环境使用SQLite，生产环境推荐PostgreSQL。 |
| **认证** | `Flask-JWT-Extended` | 业内标准的JWT实现，保障API安全。|
| **部署** | `Docker`, `Docker Compose` | 提供容器化的一键部署方案。 |

## 🔧 本地开发指南

### 1. 环境准备
- 安装 `Python 3.10+`, `Node.js 16+`, `Git`。
- 克隆本项目到本地。

### 2. 后端启动
```bash
# 1. 进入项目根目录
cd smart-water-system

# 2. 创建并激活Python虚拟环境 (推荐)
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 3. 安装后端依赖
pip install -r backend/requirements.txt

# 4. 初始化数据库 (首次运行时需要)
# flask db init
flask db migrate -m "Initial migration."
flask db upgrade

# 5. 运行后端服务 (默认 http://127.0.0.1:5000)
python backend/app.py
```

### 3. 前端启动
```bash
# 1. 打开一个新的终端，进入前端目录
cd frontend

# 2. 安装前端依赖
npm install

# 3. 运行前端开发服务器 (默认 http://127.0.0.1:5173)
npm run dev
```
启动成功后，在浏览器中打开前端地址即可开始使用。

## 📁 项目结构概览
```
smart-water-system/
├── backend/            # 后端Flask应用
│   ├── services/       # 核心分析服务 (water_habit_analysis.py)
│   ├── routes/         # API路由定义
│   ├── models/         # SQLAlchemy数据模型
│   ├── fonts/          # 存放字体文件
│   └── app.py          # 应用入口
├── frontend/           # 前端React应用
│   ├── src/
│   │   ├── pages/      # 各页面组件
│   │   ├── api/        # API请求模块
│   │   ├── context/    # React Context
│   └── vite.config.ts  # Vite配置
├── .gitignore          # Git忽略配置
├── README.md           # 就是你正在看的这个文件
└── requirements.txt    # 顶层依赖(可选)
```

## 🤝 贡献
我们欢迎任何形式的贡献！无论是提交Bug、建议新功能还是直接贡献代码。
1.  Fork 本仓库
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  创建一个新的 Pull Request

## 📄 许可证
本项目采用 [MIT](https://opensource.org/licenses/MIT) 许可证。

---
<p align="center">
  <em>本项目在Cursor的辅助下高效完成开发，生动展示了AI在全栈应用开发中的巨大潜力和价值。</em>
</p> 