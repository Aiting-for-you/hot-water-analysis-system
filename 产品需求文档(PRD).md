# 热水系统智能分析平台产品需求文档 (PRD)

## 文档信息
- **产品名称**: 热水系统智能分析平台
- **版本**: v2.0
- **创建日期**: 2025-01-21
- **更新日期**: 2025-01-21
- **文档类型**: 产品需求文档 (PRD)
- **作者**: 热水系统分析团队

## 1. 产品概述

### 1.1 产品定位
热水系统智能分析平台是一个基于Web的数据分析和智能预测系统，专门为热水系统的节能优化提供科学决策支持。平台集成了数据管理、用水习惯分析、机器学习建模和智能预测等核心功能。

### 1.2 产品目标
- 提供高效的热水系统数据处理和管理能力
- 实现多维度用水习惯分析和可视化展示
- 构建智能预测模型，支持用水量预测和系统优化
- 为热水系统节能运行提供数据驱动的决策支持

### 1.3 目标用户
- **主要用户**: 热水系统管理员、能源管理工程师
- **次要用户**: 数据分析师、系统运维人员
- **决策用户**: 能源管理部门负责人、设施管理者

## 2. 技术架构

### 2.1 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用层     │    │   后端服务层     │    │   数据存储层     │
│                 │    │                 │    │                 │
│ React + Ant D   │◄──►│ Flask + API     │◄──►│ SQLite/PostgreSQL│
│ Redux Toolkit   │    │ ML Services     │    │ File Storage    │
│ ECharts/Recharts│    │ Data Processing │    │ Model Storage   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 前端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2.0 | 前端框架 |
| TypeScript | 5.2.2 | 类型安全 |
| Ant Design | 5.11.1 | UI组件库 |
| Redux Toolkit | 1.9.7 | 状态管理 |
| React Router | 6.17.0 | 路由管理 |
| ECharts | 5.4.3 | 图表库 |
| Recharts | 2.8.0 | 图表库 |
| Axios | 1.6.0 | HTTP客户端 |
| Day.js | 1.11.10 | 时间处理 |
| Lodash | 4.17.21 | 工具库 |

### 2.3 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| Flask | 2.3.3 | Web框架 |
| Flask-SQLAlchemy | 3.0.5 | ORM |
| Flask-JWT-Extended | 4.5.3 | 身份认证 |
| Pandas | 2.1.1 | 数据处理 |
| NumPy | 1.24.3 | 数值计算 |
| Scikit-learn | 1.3.0 | 机器学习 |
| XGBoost | 1.7.6 | 梯度提升 |
| Matplotlib | 3.7.2 | 图表生成 |
| Celery | 5.3.1 | 异步任务 |
| Redis | 4.6.0 | 缓存/消息队列 |

## 3. 功能模块详细设计

### 3.1 用户认证模块

#### 3.1.1 功能描述
- 用户登录/登出
- 会话管理
- 权限控制
- 密码安全

#### 3.1.2 页面设计
**登录页面 (`/login`)**
- **组件**: `pages/Login/index.tsx`
- **样式**: `pages/Login/index.css`
- **功能**:
  - 用户名/密码登录
  - 记住登录状态
  - 登录状态验证
  - 错误提示

#### 3.1.3 数据对象
```typescript
interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user' | 'viewer';
  permissions: string[];
  lastLogin: string;
  createdAt: string;
}

interface LoginRequest {
  username: string;
  password: string;
  remember?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}
```

#### 3.1.4 API接口
```typescript
// 用户登录
POST /api/auth/login
Request: LoginRequest
Response: { user: User, token: string }

// 用户登出
POST /api/auth/logout
Response: { message: string }

// 获取用户信息
GET /api/auth/me
Response: User

// 刷新令牌
POST /api/auth/refresh
Response: { token: string }
```

### 3.2 数据管理模块

#### 3.2.1 功能描述
- 数据文件上传
- 数据预览和验证
- 数据格式转换
- 数据集管理
- 数据质量检查

#### 3.2.2 页面设计
**数据管理页面 (`/data`)**
- **组件**: `pages/Data/index.tsx`
- **样式**: `pages/Data/index.css`
- **功能**:
  - 数据集列表展示
  - 文件上传（拖拽/点击）
  - 数据预览
  - 数据集详情查看
  - 数据集分享
  - 批量操作

#### 3.2.3 数据对象
```typescript
interface Dataset {
  id: string;
  name: string;
  description?: string;
  fileName: string;
  fileSize: number;
  fileType: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  rowCount: number;
  columnCount: number;
  tags: string[];
  creator: string;
  createdAt: string;
  updatedAt: string;
  isPublic: boolean;
  downloadCount: number;
}

interface UploadProgress {
  percent: number;
  status: 'uploading' | 'success' | 'error';
  message?: string;
}

interface DataPreview {
  columns: string[];
  data: Record<string, any>[];
  totalRows: number;
  sampleRows: number;
}
```

#### 3.2.4 API接口
```typescript
// 获取数据集列表
GET /api/datasets
Query: { page?, size?, search?, tags?, status? }
Response: { datasets: Dataset[], total: number, page: number, size: number }

// 上传数据文件
POST /api/datasets/upload
Request: FormData (file)
Response: { datasetId: string, uploadId: string }

// 获取上传进度
GET /api/datasets/upload/{uploadId}/progress
Response: UploadProgress

// 数据预览
GET /api/datasets/{id}/preview
Query: { rows?, offset? }
Response: DataPreview

// 数据集详情
GET /api/datasets/{id}
Response: Dataset

// 更新数据集
PUT /api/datasets/{id}
Request: Partial<Dataset>
Response: Dataset

// 删除数据集
DELETE /api/datasets/{id}
Response: { message: string }

// 下载数据集
GET /api/datasets/{id}/download
Response: File
```

### 3.3 数据分析模块

#### 3.3.1 功能描述
- 多维度用水分析
- 交互式图表展示
- 分析报告生成
- 分析任务管理
- 结果导出

#### 3.3.2 页面设计
**分析页面 (`/analysis`)**
- **组件**: `pages/Analysis/index.tsx`
- **样式**: `pages/Analysis/index.css`
- **功能**:
  - 分析任务列表
  - 创建分析任务
  - 分析进度监控
  - 结果可视化
  - 报告生成和分享

#### 3.3.3 数据对象
```typescript
interface AnalysisTask {
  id: string;
  name: string;
  type: 'temporal' | 'spatial' | 'statistical' | 'pattern';
  status: 'pending' | 'running' | 'completed' | 'failed';
  datasetId: string;
  datasetName: string;
  parameters: AnalysisParameters;
  progress: number;
  results?: AnalysisResults;
  creator: string;
  createdAt: string;
  completedAt?: string;
  duration?: number;
  viewCount: number;
}

interface AnalysisParameters {
  timeRange?: [string, string];
  buildings?: string[];
  analysisType: string;
  granularity?: 'hour' | 'day' | 'week' | 'month';
  includeWeekends?: boolean;
  customFilters?: Record<string, any>;
}

interface AnalysisResults {
  charts: ChartData[];
  statistics: StatisticsData;
  insights: string[];
  reportUrl?: string;
}

interface ChartData {
  id: string;
  type: 'line' | 'bar' | 'pie' | 'heatmap' | 'scatter';
  title: string;
  data: any[];
  options: any;
}
```

#### 3.3.4 API接口
```typescript
// 获取分析任务列表
GET /api/analysis/tasks
Query: { page?, size?, status?, type?, creator? }
Response: { tasks: AnalysisTask[], total: number }

// 创建分析任务
POST /api/analysis/tasks
Request: { name: string, type: string, datasetId: string, parameters: AnalysisParameters }
Response: AnalysisTask

// 获取分析任务详情
GET /api/analysis/tasks/{id}
Response: AnalysisTask

// 获取分析结果
GET /api/analysis/tasks/{id}/results
Response: AnalysisResults

// 导出分析报告
GET /api/analysis/tasks/{id}/export
Query: { format: 'pdf' | 'excel' | 'json' }
Response: File

// 停止分析任务
POST /api/analysis/tasks/{id}/stop
Response: { message: string }
```

### 3.4 模型管理模块

#### 3.4.1 功能描述
- 机器学习模型管理
- 模型训练和评估
- 模型部署和版本控制
- 性能监控
- 模型比较

#### 3.4.2 页面设计
**模型管理页面 (`/models`)**
- **组件**: `pages/Models/index.tsx`
- **样式**: `pages/Models/index.css`
- **功能**:
  - 模型列表展示
  - 创建训练任务
  - 模型性能对比
  - 模型部署管理
  - 模型详情查看

#### 3.4.3 数据对象
```typescript
interface Model {
  id: string;
  name: string;
  type: 'linear' | 'tree' | 'ensemble' | 'neural' | 'timeseries';
  algorithm: string;
  status: 'training' | 'trained' | 'deployed' | 'failed';
  datasetId: string;
  datasetName: string;
  parameters: ModelParameters;
  performance: ModelPerformance;
  creator: string;
  createdAt: string;
  trainedAt?: string;
  deployedAt?: string;
  version: string;
  size: number;
  downloadCount: number;
}

interface ModelParameters {
  algorithm: string;
  hyperparameters: Record<string, any>;
  features: string[];
  target: string;
  trainTestSplit: number;
  crossValidation?: number;
}

interface ModelPerformance {
  mae: number;
  rmse: number;
  mape: number;
  r2: number;
  trainingTime: number;
  validationScore: number;
}
```

#### 3.4.4 API接口
```typescript
// 获取模型列表
GET /api/models
Query: { page?, size?, status?, type?, creator? }
Response: { models: Model[], total: number }

// 创建模型训练任务
POST /api/models/train
Request: { name: string, type: string, datasetId: string, parameters: ModelParameters }
Response: Model

// 获取模型详情
GET /api/models/{id}
Response: Model

// 获取训练进度
GET /api/models/{id}/progress
Response: { progress: number, status: string, logs: string[] }

// 模型评估
GET /api/models/{id}/evaluate
Response: ModelPerformance

// 部署模型
POST /api/models/{id}/deploy
Response: { deploymentId: string, endpoint: string }

// 下载模型
GET /api/models/{id}/download
Response: File
```

### 3.5 预测模块

#### 3.5.1 功能描述
- 基于训练模型的预测
- 批量预测和实时预测
- 预测结果可视化
- 预测准确性评估
- 预测任务管理

#### 3.5.2 页面设计
**预测页面 (`/predictions`)**
- **组件**: `pages/Predictions/index.tsx`
- **样式**: `pages/Predictions/index.css`
- **功能**:
  - 预测任务列表
  - 创建预测任务
  - 预测结果展示
  - 准确性分析
  - 结果导出

#### 3.5.3 数据对象
```typescript
interface PredictionTask {
  id: string;
  name: string;
  type: 'single' | 'batch' | 'realtime';
  status: 'pending' | 'running' | 'completed' | 'failed';
  modelId: string;
  modelName: string;
  datasetId?: string;
  datasetName?: string;
  parameters: PredictionParameters;
  progress: number;
  results?: PredictionResults;
  accuracy?: number;
  creator: string;
  createdAt: string;
  completedAt?: string;
  resultCount: number;
}

interface PredictionParameters {
  predictionHorizon: number;
  startDate: string;
  endDate: string;
  buildings?: string[];
  confidence: number;
  includeUncertainty: boolean;
}

interface PredictionResults {
  predictions: PredictionPoint[];
  charts: ChartData[];
  statistics: PredictionStatistics;
  accuracy: AccuracyMetrics;
}

interface PredictionPoint {
  timestamp: string;
  building: string;
  predicted: number;
  actual?: number;
  confidence: [number, number];
}
```

#### 3.5.4 API接口
```typescript
// 获取预测任务列表
GET /api/predictions/tasks
Query: { page?, size?, status?, type?, modelId? }
Response: { tasks: PredictionTask[], total: number }

// 创建预测任务
POST /api/predictions/tasks
Request: { name: string, type: string, modelId: string, parameters: PredictionParameters }
Response: PredictionTask

// 获取预测结果
GET /api/predictions/tasks/{id}/results
Response: PredictionResults

// 实时预测
POST /api/predictions/realtime
Request: { modelId: string, features: Record<string, any> }
Response: { prediction: number, confidence: [number, number] }

// 导出预测结果
GET /api/predictions/tasks/{id}/export
Query: { format: 'csv' | 'excel' | 'json' }
Response: File
```

### 3.6 系统设置模块

#### 3.6.1 功能描述
- 个人资料管理
- 密码安全设置
- 通知偏好设置
- 隐私设置
- 系统配置（管理员）

#### 3.6.2 页面设计
**设置页面 (`/settings`)**
- **组件**: `pages/Settings/index.tsx`
- **样式**: `pages/Settings/index.css`
- **功能**:
  - 多标签页设置界面
  - 个人资料编辑
  - 密码修改
  - 通知设置
  - 系统配置

#### 3.6.3 数据对象
```typescript
interface UserProfile {
  id: string;
  username: string;
  email: string;
  fullName: string;
  avatar?: string;
  phone?: string;
  department?: string;
  role: string;
  preferences: UserPreferences;
}

interface UserPreferences {
  language: 'zh' | 'en';
  theme: 'light' | 'dark' | 'auto';
  timezone: string;
  dateFormat: string;
  notifications: NotificationSettings;
}

interface SystemSettings {
  siteName: string;
  siteDescription: string;
  maxFileSize: number;
  allowedFileTypes: string[];
  sessionTimeout: number;
  enableRegistration: boolean;
  enableGuestAccess: boolean;
  maintenanceMode: boolean;
}
```

#### 3.6.4 API接口
```typescript
// 获取用户资料
GET /api/users/profile
Response: UserProfile

// 更新用户资料
PUT /api/users/profile
Request: Partial<UserProfile>
Response: UserProfile

// 修改密码
POST /api/users/change-password
Request: { currentPassword: string, newPassword: string }
Response: { message: string }

// 上传头像
POST /api/users/avatar
Request: FormData (file)
Response: { avatarUrl: string }

// 获取系统设置（管理员）
GET /api/system/settings
Response: SystemSettings

// 更新系统设置（管理员）
PUT /api/system/settings
Request: Partial<SystemSettings>
Response: SystemSettings
```
### 3.7 天气预报模块

通过接入后端的天气预报API，实现实时天气查询和天气预报功能。
#### 3.7.1 功能描述
- 实时天气查询
- 天气预报查询
- 未来一天的24小时逐时天气预报
- 未来三天的24小时逐时天气预报

#### 3.7.2 外部API集成
- **天气API提供商**: APISpace天气预报API
- **API文档**: https://www.apispace.com/eolinker/api/weather
- **数据更新频率**: 每小时更新一次
- **获取数据**: 当前天气、24小时预报、7天预报
- **关键参数**: 温度、湿度、降水量、风速等

#### 3.7.3 页面设计

**组件结构**
```typescript
// 天气预报组件
interface WeatherForecastProps {
  location: string;
  apiKey: string;
}

interface WeatherData {
  current: {
    temperature: number;
    humidity: number;
    weather: string;
    windSpeed: number;
  };
  hourly: Array<{
    time: string;
    temperature: number;
    precipitation: number;
  }>;
  daily: Array<{
    date: string;
    maxTemp: number;
    minTemp: number;
    weather: string;
    precipitation: number;
  }>;
}
```

**样式设计**
- 天气卡片布局，显示当前天气状况
- 24小时温度趋势图表
- 7天天气预报列表
- 天气对用水量影响的分析图表

#### 3.7.4 数据对象
```typescript
interface WeatherForecast {
  id: string;
  location: string;
  currentWeather: {
    temperature: number;
    humidity: number;
    weather: string;
    windSpeed: number;
    updateTime: Date;
  };
  hourlyForecast: Array<{
    time: Date;
    temperature: number;
    precipitation: number;
    humidity: number;
  }>;
  dailyForecast: Array<{
    date: Date;
    maxTemp: number;
    minTemp: number;
    weather: string;
    precipitation: number;
  }>;
  createdAt: Date;
  updatedAt: Date;
}
```

#### 3.7.5 API接口
```typescript
// 获取天气数据
GET /api/weather/current?location={location}
GET /api/weather/forecast?location={location}&days={days}

// 天气数据分析
GET /api/weather/analysis?startDate={date}&endDate={date}
POST /api/weather/impact-analysis
```
### 3.8 AI助手模块
#### 3.8.1 实施方案
- **大模型平台**: 阿里百炼大模型平台
- **模型选择**: 通义千问系列模型
- **API集成**: 通过阿里云百炼API接口
- **功能定位**: 智能问答、数据分析、优化建议

#### 3.8.2 功能描述
- 回答用户关于热水系统的问题
- 提供数据分析解读
- 生成节能优化建议
- 协助故障诊断
- 解释预测结果和分析报告

#### 3.8.3 页面设计

**组件结构**
```typescript
// AI助手组件
interface AIAssistantProps {
  apiKey: string;
  context: {
    userData: any;
    analysisResults: any;
    systemStatus: any;
  };
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  attachments?: Array<{
    type: 'chart' | 'data' | 'report';
    content: any;
  }>;
}
```

**样式设计**
- 聊天界面布局，支持文本和图表展示
- 快捷问题按钮，常见问题一键询问
- 上下文感知，结合当前页面数据提供建议
- 支持语音输入和输出（可选）

#### 3.8.4 数据对象
```typescript
interface AIConversation {
  id: string;
  userId: string;
  title: string;
  messages: ChatMessage[];
  context: {
    currentPage: string;
    relevantData: any;
    userPreferences: any;
  };
  createdAt: Date;
  updatedAt: Date;
}

interface AIResponse {
  content: string;
  confidence: number;
  suggestions: string[];
  relatedCharts?: any[];
  actionItems?: string[];
}
```

#### 3.8.5 API接口
```typescript
// AI对话接口
POST /api/ai/chat
{
  message: string;
  context: {
    userId: string;
    currentData: any;
    conversationHistory: ChatMessage[];
  };
  apiKey: string;
}

// 获取对话历史
GET /api/ai/conversations?userId={userId}
GET /api/ai/conversations/{conversationId}

// 删除对话
DELETE /api/ai/conversations/{conversationId}
```
## 4. 用户界面设计

### 4.1 设计原则
- **一致性**: 统一的视觉风格和交互模式
- **易用性**: 直观的操作流程和清晰的信息架构
- **响应式**: 适配不同屏幕尺寸和设备
- **可访问性**: 支持键盘导航和屏幕阅读器
- **性能**: 快速加载和流畅的用户体验

### 4.2 视觉设计
- **主色调**: #1890ff (Ant Design 蓝)
- **辅助色**: #52c41a (成功), #faad14 (警告), #f5222d (错误)
- **中性色**: #000000, #262626, #595959, #8c8c8c, #bfbfbf, #d9d9d9, #f0f0f0, #fafafa, #ffffff
- **字体**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif
- **圆角**: 6px (默认), 4px (小), 8px (大)
- **阴影**: 0 2px 8px rgba(0, 0, 0, 0.15)

### 4.3 布局设计
- **顶部导航**: 固定高度64px，包含Logo、导航菜单、用户信息
- **侧边栏**: 可折叠，宽度200px/80px，包含主要功能导航
- **内容区域**: 自适应宽度，包含面包屑、页面标题、主要内容
- **响应式断点**: xs(<576px), sm(≥576px), md(≥768px), lg(≥992px), xl(≥1200px), xxl(≥1600px)

### 4.4 组件规范
- **按钮**: 主要按钮(primary)、次要按钮(default)、危险按钮(danger)
- **表单**: 标签对齐、验证提示、必填标识
- **表格**: 斑马纹、悬停效果、排序、筛选、分页
- **图表**: 统一配色、交互提示、数据标签
- **模态框**: 居中显示、遮罩层、关闭按钮

## 5. 数据库设计

### 5.1 数据表结构

#### 5.1.1 用户表 (users)
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(255),
    phone VARCHAR(20),
    department VARCHAR(100),
    role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    api_keys JSON COMMENT 'API密钥配置 {"weather": "key", "ai": "key"}',
    preferences JSON COMMENT '用户偏好设置',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 5.1.2 数据集表 (datasets)
```sql
CREATE TABLE datasets (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type ENUM('excel', 'csv') NOT NULL,
    status ENUM('uploading', 'processing', 'ready', 'error') DEFAULT 'uploading',
    row_count INT DEFAULT 0,
    column_count INT DEFAULT 0,
    columns JSON NOT NULL COMMENT '列信息：[{"name": "时间", "type": "datetime"}, {"name": "水流量", "type": "number"}]',
    data_range JSON COMMENT '数据时间范围 {"start": "2024-01-01", "end": "2024-12-31"}',
    buildings JSON COMMENT '楼栋信息 ["A栋", "B栋", "C栋"]',
    quality_check JSON COMMENT '数据质量检查结果',
    tags JSON,
    is_public BOOLEAN DEFAULT FALSE,
    download_count INT DEFAULT 0,
    creator_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 5.1.3 分析任务表 (analysis_tasks)
```sql
CREATE TABLE analysis_tasks (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('temporal', 'spatial', 'statistical', 'pattern') NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    dataset_id VARCHAR(36) NOT NULL,
    parameters JSON,
    progress INT DEFAULT 0,
    results JSON,
    error_message TEXT,
    view_count INT DEFAULT 0,
    creator_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 5.1.4 模型表 (models)
```sql
CREATE TABLE models (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('linear', 'tree', 'ensemble', 'neural', 'timeseries') NOT NULL,
    algorithm VARCHAR(50) NOT NULL COMMENT '算法类型：linear_regression, random_forest, lstm, etc.',
    status ENUM('training', 'trained', 'deployed', 'failed') DEFAULT 'training',
    dataset_id VARCHAR(36) NOT NULL,
    parameters JSON COMMENT '模型参数配置',
    performance JSON,
    model_path VARCHAR(500) COMMENT '模型文件存储路径',
    model_size BIGINT DEFAULT 0,
    version VARCHAR(20) DEFAULT '1.0.0',
    mae DECIMAL(10,6) COMMENT '平均绝对误差',
    rmse DECIMAL(10,6) COMMENT '均方根误差',
    training_duration INT COMMENT '训练耗时（秒）',
    data_requirements JSON COMMENT '数据要求 {"min_records": 720, "min_days": 30}',
    error_message TEXT COMMENT '训练失败时的错误信息',
    download_count INT DEFAULT 0,
    creator_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trained_at TIMESTAMP,
    deployed_at TIMESTAMP,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 5.1.5 预测任务表 (prediction_tasks)
```sql
CREATE TABLE prediction_tasks (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('single', 'batch', 'realtime') NOT NULL,
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    model_id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36),
    parameters JSON COMMENT '输入数据或参数',
    progress INT DEFAULT 0,
    results JSON COMMENT '预测结果数据',
    accuracy_check JSON COMMENT '准确性验证结果 {"actual": [], "predicted": [], "mae": 0.05}',
    export_format ENUM('excel', 'csv', 'json') DEFAULT 'excel',
    export_path VARCHAR(255) COMMENT '导出文件路径',
    accuracy DECIMAL(5,4),
    result_count INT DEFAULT 0,
    error_message TEXT COMMENT '执行失败时的错误信息',
    execution_time INT COMMENT '执行耗时（毫秒）',
    creator_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE
);
```

#### 5.1.6 天气数据表 (weather_data)
```sql
CREATE TABLE weather_data (
    id VARCHAR(36) PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    hour TINYINT NOT NULL,
    temperature DECIMAL(4,1) COMMENT '温度（摄氏度）',
    humidity TINYINT COMMENT '湿度（%）',
    precipitation DECIMAL(5,2) COMMENT '降水量（mm）',
    wind_speed DECIMAL(4,1) COMMENT '风速（m/s）',
    weather_type VARCHAR(50) COMMENT '天气类型',
    api_source VARCHAR(50) DEFAULT 'apispace' COMMENT 'API来源',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_weather_location_datetime (location, date, hour)
);
```

#### 5.1.7 AI对话记录表 (ai_conversations)
```sql
CREATE TABLE ai_conversations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(200) NOT NULL,
    messages JSON NOT NULL COMMENT '对话消息列表',
    context JSON COMMENT '对话上下文信息',
    model_used VARCHAR(50) DEFAULT 'qwen' COMMENT '使用的AI模型',
    total_tokens INT COMMENT '总token消耗',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### 5.2 索引设计
```sql
-- 用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- 数据集表索引
CREATE INDEX idx_datasets_creator ON datasets(creator_id);
CREATE INDEX idx_datasets_status ON datasets(status);
CREATE INDEX idx_datasets_created ON datasets(created_at);
CREATE INDEX idx_datasets_public ON datasets(is_public);
CREATE INDEX idx_datasets_file_type ON datasets(file_type);

-- 分析任务表索引
CREATE INDEX idx_analysis_dataset ON analysis_tasks(dataset_id);
CREATE INDEX idx_analysis_creator ON analysis_tasks(creator_id);
CREATE INDEX idx_analysis_status ON analysis_tasks(status);
CREATE INDEX idx_analysis_type ON analysis_tasks(type);

-- 模型表索引
CREATE INDEX idx_models_dataset ON models(dataset_id);
CREATE INDEX idx_models_creator ON models(creator_id);
CREATE INDEX idx_models_status ON models(status);
CREATE INDEX idx_models_type ON models(type);
CREATE INDEX idx_models_accuracy ON models(mae);

-- 预测任务表索引
CREATE INDEX idx_predictions_model ON prediction_tasks(model_id);
CREATE INDEX idx_predictions_dataset ON prediction_tasks(dataset_id);
CREATE INDEX idx_predictions_creator ON prediction_tasks(creator_id);
CREATE INDEX idx_predictions_status ON prediction_tasks(status);
CREATE INDEX idx_predictions_type ON prediction_tasks(type);

-- 天气数据表索引
CREATE INDEX idx_weather_location_date ON weather_data(location, date);
CREATE INDEX idx_weather_date_hour ON weather_data(date, hour);

-- AI对话表索引
CREATE INDEX idx_ai_conversations_user_id ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_created_at ON ai_conversations(created_at);
```

## 6. 安全设计

### 6.1 身份认证
- **JWT令牌**: 基于JSON Web Token的无状态认证
- **令牌过期**: 访问令牌2小时，刷新令牌7天
- **密码策略**: 最少8位，包含大小写字母、数字和特殊字符
- **登录限制**: 连续失败5次后锁定账户30分钟

### 6.2 权限控制
- **角色权限**: 管理员、普通用户、访客三级权限
- **资源权限**: 基于资源所有者的访问控制
- **API权限**: 接口级别的权限验证
- **前端权限**: 基于用户角色的UI元素显示控制

### 6.3 数据安全
- **文件上传**: 类型白名单、大小限制、病毒扫描
- **SQL注入**: 使用ORM和参数化查询
- **XSS防护**: 输入验证和输出编码
- **CSRF防护**: CSRF令牌验证
- **数据加密**: 敏感数据加密存储

### 6.4 网络安全
- **HTTPS**: 强制使用SSL/TLS加密传输
- **CORS**: 跨域资源共享配置
- **请求限制**: API请求频率限制
- **安全头**: 设置安全相关的HTTP头

## 7. 性能优化

### 7.1 前端优化
- **代码分割**: 基于路由的懒加载
- **资源压缩**: Gzip压缩、图片优化
- **缓存策略**: 浏览器缓存、CDN缓存
- **虚拟滚动**: 大数据量表格和列表优化
- **防抖节流**: 搜索和输入事件优化

### 7.2 后端优化
- **数据库优化**: 索引优化、查询优化
- **缓存机制**: Redis缓存热点数据
- **异步处理**: Celery处理耗时任务
- **连接池**: 数据库连接池管理
- **分页查询**: 大数据量分页处理

### 7.3 系统优化
- **负载均衡**: 多实例部署和负载分发
- **CDN加速**: 静态资源CDN分发
- **监控告警**: 性能监控和异常告警
- **日志管理**: 结构化日志和日志分析

## 8. 部署方案

### 8.1 容器化部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:5000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/hotwater
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
      - ./models:/app/models
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hotwater
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 8.2 环境配置
- **开发环境**: 本地开发，热重载，调试模式，CPU计算模式
- **测试环境**: 自动化测试，性能测试，安全测试，CPU计算模式
- **生产环境**: 高可用部署，监控告警，备份恢复，GPU计算模式（可选）

#### 8.2.1 计算模式配置
- **CPU模式**: 适用于开发和测试环境，资源要求较低
- **GPU模式**: 适用于生产环境，需要NVIDIA GPU支持
- **自动模式**: 系统自动检测可用资源并选择最优配置

### 8.3 CI/CD流程
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm test
          python -m pytest
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: |
          docker build -t hotwater-frontend ./frontend
          docker build -t hotwater-backend ./backend
  
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker-compose up -d
```

## 9. 测试策略

### 9.1 测试类型
- **单元测试**: 组件和函数级别测试
- **集成测试**: API接口和数据库集成测试
- **端到端测试**: 完整用户流程测试
- **性能测试**: 负载测试和压力测试
- **安全测试**: 漏洞扫描和渗透测试

### 9.2 测试工具
- **前端测试**: Jest, React Testing Library, Cypress
- **后端测试**: Pytest, Flask-Testing, Factory Boy
- **API测试**: Postman, Newman, Swagger
- **性能测试**: JMeter, Locust
- **安全测试**: OWASP ZAP, Bandit

### 9.3 测试覆盖率
- **代码覆盖率**: 目标80%以上
- **功能覆盖率**: 核心功能100%覆盖
- **API覆盖率**: 所有接口100%覆盖
- **浏览器覆盖率**: 主流浏览器兼容性测试

## 10. 运维监控

### 10.1 监控指标
- **系统指标**: CPU、内存、磁盘、网络使用率
- **应用指标**: 响应时间、吞吐量、错误率
- **业务指标**: 用户活跃度、功能使用率、数据处理量
- **安全指标**: 登录失败次数、异常访问、文件上传

### 10.2 日志管理
- **应用日志**: 结构化日志记录
- **访问日志**: Nginx访问日志
- **错误日志**: 异常和错误信息
- **审计日志**: 用户操作记录

### 10.3 告警机制
- **阈值告警**: 指标超过预设阈值
- **异常告警**: 系统异常和错误
- **业务告警**: 业务指标异常
- **通知方式**: 邮件、短信、钉钉、微信

## 11. 项目计划

### 11.1 开发阶段
| 阶段 | 时间 | 主要任务 | 交付物 |
|------|------|----------|--------|
| 需求分析 | 1周 | 需求调研、原型设计 | PRD、原型图 |
| 架构设计 | 1周 | 技术选型、架构设计 | 技术方案、数据库设计 |
| 基础开发 | 2周 | 项目搭建、基础功能 | 项目框架、认证模块 |
| 核心开发 | 4周 | 数据管理、分析、预测 | 核心功能模块 |
| 集成测试 | 1周 | 功能测试、性能测试 | 测试报告 |
| 部署上线 | 1周 | 生产部署、监控配置 | 生产环境 |

### 11.2 里程碑
- **M1**: 基础框架和API密钥管理完成（第2周末）
- **M2**: 数据管理和Excel解析功能完成（第4周末）
- **M3**: 数据分析和可视化功能完成（第6周末）
- **M4**: 机器学习模型和外部API集成完成（第9周末）
- **M5**: 系统测试和性能优化完成（第11周末）
- **M6**: 项目部署上线（第12周末）

### 11.3 风险控制

#### 技术风险
- **机器学习模型性能**: 建立模型评估标准，确保预测误差不超过0.1
- **外部API稳定性**: APISpace和阿里百炼API的可用性监控
- **数据处理性能**: 优化Excel解析和大数据量处理算法
- **计算资源配置**: 支持CPU和GPU两种模式，测试阶段使用CPU，生产部署可选择GPU（4090显卡）
- **系统稳定性**: 完善错误处理和日志记录

#### 进度风险
- **开发延期**: 合理分配任务，设置缓冲时间
- **需求变更**: 建立变更管理流程
- **资源不足**: 提前识别关键资源需求
- **API集成复杂度**: 预留额外时间进行外部服务集成测试

#### 数据风险
- **数据质量**: 建立数据验证机制，确保至少一个月的有效数据
- **数据安全**: 内部服务器部署，确保数据不外泄
- **历史数据迁移**: 制定详细的数据导入和验证方案

## 12. 维护升级

### 12.1 版本管理
- **版本号规则**: 主版本.次版本.修订版本 (如: 2.1.3)
- **发布周期**: 主版本6个月，次版本2个月，修订版本按需
- **兼容性**: 向后兼容，API版本控制
- **升级策略**: 灰度发布，回滚机制

### 12.2 功能扩展
- 支持更多数据格式（CSV、JSON等）
- 增加更多机器学习算法（深度学习、时间序列等）
- 扩展可视化图表类型
- 集成更多外部服务（其他天气API、IoT设备等）
- 增加移动端支持
- 支持多租户架构

### 12.3 技术债务
- 定期代码重构
- 性能优化（CPU/GPU自适应配置和资源利用率优化）
- 安全更新
- 依赖库升级
- API密钥安全性增强

### 12.4 数据管理优化
- 实现数据自动备份
- 增加数据压缩和归档功能
- 优化大文件上传性能
- 支持增量数据更新

---

**文档状态**: 已完成  
**审核状态**: 待审核  
**批准状态**: 待批准  
**生效日期**: 2025-01-21