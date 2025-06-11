# 智能用水习惯分析与节能控制系统

本项目是一个基于Web的全栈应用，旨在通过分析历史用水数据，为楼宇的增压泵和热水系统提供智能化的节能控制策略。

## ✨ 主要功能

- **数据处理**: 支持上传CSV格式的用水数据，并进行自动化清洗和预处理。
- **多维度分析**: 从每小时、每周、不同楼栋等多个维度进行深入的用水习惯分析。
- **数据可视化**: 将复杂的分析结果通过直观的图表（柱状图、热力图、箱线图、饼图等）展示出来。
- **智能报告**: 自动生成详细的、包含量化指标和图表的分析报告，支持下载。
- **节能建议**: 根据分析结果，为增压泵的启停控制提供定量的运行时间建议和节能比例预测。
- **用户认证**: 使用JWT (JSON Web Tokens) 进行安全的用户认证。
- **历史追溯**: 保存并展示历次的分析结果，方便追溯和对比。

## 🚀 技术栈

- **后端**: 
  - **框架**: Flask
  - **数据库**: SQLite (可通过配置轻松更换为PostgreSQL, MySQL等)
  - **ORM**: SQLAlchemy
  - **数据库迁移**: Flask-Migrate
  - **认证**: Flask-JWT-Extended
  - **数据分析**: Pandas, NumPy, Scikit-learn
  - **可视化**: Matplotlib, Seaborn
- **前端**:
  - **框架**: React
  - **UI库**: (根据项目实际情况填写, e.g., Material-UI, Ant Design)
  - **图表**: (根据项目实际情况填写, e.g., Chart.js, ECharts)
  - **HTTP客户端**: Axios
- **开发环境**:
  - **后端**: Python 3.10+
  - **前端**: Node.js 16+

## 🔧 项目安装与运行

### 1. 后端 (Backend)

**a. 克隆仓库**
```bash
git clone <your-repository-url>
cd <project-folder>
```

**b. 创建并激活虚拟环境**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

**c. 安装依赖**
```bash
pip install -r backend/requirements.txt
```

**d. 初始化数据库**
```bash
# 在项目根目录下运行
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

**e. 运行后端服务**
> 默认运行在 `http://127.0.0.1:5000`
```bash
python backend/app.py
```

### 2. 前端 (Frontend)

**a. 进入前端目录**
```bash
cd frontend
```

**b. 安装依赖**
```bash
npm install
```

**c. 运行前端开发服务**
> 默认运行在 `http://127.0.0.1:5173` (Vite) 或 `http://127.0.0.1:3000` (Create React App)
```bash
npm run dev
```
之后，在浏览器中打开前端服务的地址即可访问应用。

## 📝 API 端点概览
- `POST /api/auth/register`: 用户注册
- `POST /api/auth/login`: 用户登录
- `POST /api/datasets/upload`: 上传数据集
- `POST /api/conversion/run`: 运行数据转换
- `POST /api/analysis/`: 运行分析
- `GET /api/analysis/results/<id>`: 获取分析结果
- `GET /api/analysis/results/<id>/report`: 下载分析报告
- `GET /api/analysis/history`: 获取历史分析列表

---
*本项目在Cursor的辅助下完成开发，展示了AI在全栈应用开发中的巨大潜力。* 