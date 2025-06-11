# 热水系统智能分析平台 - 附录文档

## 附录A：外部服务集成详细说明

### A.1 APISpace天气API集成

#### A.1.1 API基本信息
- **服务商**: APISpace
- **API文档**: https://www.apispace.com/eolinker/api/weather
- **认证方式**: API Key
- **请求限制**: 根据套餐不同，一般为1000-10000次/天
- **数据格式**: JSON

#### A.1.2 主要接口
```typescript
// 实时天气
GET https://eolink.o.apispace.com/weather/current
Headers: {
  "X-APISpace-Token": "your_api_key",
  "Authorization-Type": "apikey"
}
Params: {
  "location": "北京市",  // 城市名称
  "lang": "zh"          // 语言
}

// 天气预报
GET https://eolink.o.apispace.com/weather/forecast
Params: {
  "location": "北京市",
  "days": 7,            // 预报天数
  "lang": "zh"
}
```

#### A.1.3 数据结构
```typescript
interface APISpaceWeatherResponse {
  code: number;
  message: string;
  data: {
    current: {
      temperature: number;
      humidity: number;
      weather: string;
      windSpeed: number;
      pressure: number;
      visibility: number;
    };
    forecast: Array<{
      date: string;
      maxTemp: number;
      minTemp: number;
      weather: string;
      precipitation: number;
      windSpeed: number;
    }>;
  };
}
```

### A.2 阿里百炼大模型集成

#### A.2.1 API基本信息
- **服务商**: 阿里云
- **平台**: 百炼大模型平台
- **模型**: 通义千问系列（qwen-turbo, qwen-plus, qwen-max）
- **认证方式**: API Key
- **计费方式**: 按token计费

#### A.2.2 主要接口
```typescript
// 对话接口
POST https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
Headers: {
  "Authorization": "Bearer your_api_key",
  "Content-Type": "application/json"
}
Body: {
  "model": "qwen-turbo",
  "input": {
    "messages": [
      {
        "role": "system",
        "content": "你是一个热水系统专家助手"
      },
      {
        "role": "user",
        "content": "用户问题"
      }
    ]
  },
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}
```

#### A.2.3 响应结构
```typescript
interface DashScopeResponse {
  output: {
    text: string;
    finish_reason: string;
  };
  usage: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  request_id: string;
}
```

## 附录B：数据格式详细说明

### B.1 Excel数据格式要求

#### B.1.1 标准格式
```
| 时间              | 楼栋 | 水流量(T/h) | 温度(°C) | 备注     |
|-------------------|------|-------------|----------|----------|
| 2024-01-01 00:00 | A栋  | 0.125       | 45.2     | 正常     |
| 2024-01-01 01:00 | A栋  | 0.089       | 44.8     | 正常     |
| 2024-01-01 02:00 | A栋  | 0.056       | 44.1     | 正常     |
```

#### B.1.2 必需字段
- **时间**: 格式为 YYYY-MM-DD HH:MM 或 YYYY/MM/DD HH:MM
- **楼栋**: 楼栋标识，如"A栋"、"B栋"等
- **水流量**: 数值型，单位为吨/小时(T/h)

#### B.1.3 可选字段
- **温度**: 水温，单位摄氏度
- **压力**: 水压，单位MPa
- **备注**: 文本说明

#### B.1.4 数据质量要求
- 时间序列连续，间隔为1小时
- 数据量至少覆盖30天（720条记录）
- 缺失值不超过5%
- 异常值（负数、超大值）需要标注

### B.2 历史数据导入

#### B.2.1 批量导入流程
1. 用户选择多个Excel文件
2. 系统验证文件格式和数据质量
3. 数据预处理和清洗
4. 合并多个文件的数据
5. 存储到数据库
6. 生成导入报告

#### B.2.2 数据验证规则
```typescript
interface DataValidationRules {
  timeFormat: RegExp;           // 时间格式验证
  flowRange: [number, number];  // 水流量合理范围
  tempRange: [number, number];  // 温度合理范围
  requiredColumns: string[];    // 必需列
  maxMissingRate: number;       // 最大缺失率
  minRecords: number;           // 最少记录数
}
```

## 附录C：机器学习模型详细配置

### C.1 支持的算法类型

#### C.1.1 线性回归 (Linear Regression)
```typescript
interface LinearRegressionParams {
  fit_intercept: boolean;       // 是否拟合截距
  normalize: boolean;           // 是否标准化
  copy_X: boolean;             // 是否复制X
  n_jobs: number;              // 并行作业数
}

// 默认参数
const defaultLinearParams = {
  fit_intercept: true,
  normalize: false,
  copy_X: true,
  n_jobs: 1
};
```

#### C.1.2 随机森林 (Random Forest)
```typescript
interface RandomForestParams {
  n_estimators: number;         // 树的数量
  max_depth: number | null;     // 最大深度
  min_samples_split: number;    // 分割所需最小样本数
  min_samples_leaf: number;     // 叶节点最小样本数
  random_state: number;         // 随机种子
}

// 默认参数
const defaultRFParams = {
  n_estimators: 100,
  max_depth: null,
  min_samples_split: 2,
  min_samples_leaf: 1,
  random_state: 42
};
```

#### C.1.3 LSTM神经网络
```typescript
interface LSTMParams {
  sequence_length: number;      // 序列长度
  hidden_units: number;         // 隐藏单元数
  num_layers: number;           // 层数
  dropout_rate: number;         // Dropout率
  learning_rate: number;        // 学习率
  epochs: number;               // 训练轮数
  batch_size: number;           // 批次大小
  device: 'cpu' | 'gpu' | 'auto'; // 计算设备
}

// CPU模式默认参数（测试环境）
const defaultLSTMParamsCPU = {
  sequence_length: 24,          // 24小时序列
  hidden_units: 32,             // 减少隐藏单元以适应CPU
  num_layers: 1,                // 减少层数
  dropout_rate: 0.2,
  learning_rate: 0.001,
  epochs: 50,                   // 减少训练轮数
  batch_size: 16,               // 减少批次大小
  device: 'cpu'
};

// GPU模式默认参数（生产环境）
const defaultLSTMParamsGPU = {
  sequence_length: 24,          // 24小时序列
  hidden_units: 64,
  num_layers: 2,
  dropout_rate: 0.2,
  learning_rate: 0.001,
  epochs: 100,
  batch_size: 32,
  device: 'gpu'
};

// 自动检测模式参数
const defaultLSTMParamsAuto = {
  sequence_length: 24,
  hidden_units: 48,             // 中等配置
  num_layers: 2,
  dropout_rate: 0.2,
  learning_rate: 0.001,
  epochs: 75,                   // 中等训练轮数
  batch_size: 24,               // 中等批次大小
  device: 'auto'
};
```

### C.2 计算设备配置

#### C.2.1 设备选择策略
```typescript
interface DeviceConfig {
  device: 'cpu' | 'gpu' | 'auto';
  gpu_memory_limit?: number;    // GPU内存限制（MB）
  cpu_threads?: number;         // CPU线程数
  mixed_precision?: boolean;    // 混合精度训练（仅GPU）
}

// 设备配置
const deviceConfigs = {
  cpu: {
    device: 'cpu',
    cpu_threads: 0,             // 0表示使用所有可用核心
    mixed_precision: false
  },
  gpu: {
    device: 'gpu',
    gpu_memory_limit: 8192,     // 8GB GPU内存限制
    mixed_precision: true,      // 启用混合精度训练
    cpu_threads: 4              // 辅助CPU线程
  },
  auto: {
    device: 'auto',
    gpu_memory_limit: 4096,     // 保守的GPU内存限制
    mixed_precision: false,     // 保守配置
    cpu_threads: 0
  }
};
```

#### C.2.2 性能优化配置
```typescript
// CPU优化配置
const cpuOptimization = {
  use_multiprocessing: true,
  workers: 'auto',              // 自动检测CPU核心数
  inter_op_parallelism: 0,      // TensorFlow线程间并行
  intra_op_parallelism: 0,      // TensorFlow线程内并行
  allow_soft_placement: true
};

// GPU优化配置
const gpuOptimization = {
  memory_growth: true,          // 动态GPU内存分配
  allow_memory_growth: true,
  per_process_gpu_memory_fraction: 0.8,
  allow_soft_placement: true,
  log_device_placement: false
};
```

### C.3 模型评估指标

#### C.3.1 准确性指标
```typescript
interface ModelMetrics {
  mae: number;                  // 平均绝对误差
  rmse: number;                 // 均方根误差
  mape: number;                 // 平均绝对百分比误差
  r2_score: number;             // R²决定系数
  max_error: number;            // 最大误差
  training_time: number;        // 训练时间（秒）
  device_used: string;          // 实际使用的设备
}

// 准确性要求
const accuracyRequirements = {
  max_error: 0.1,               // 最大误差不超过0.1
  min_r2_score: 0.8,           // R²不低于0.8
  max_mape: 10,                 // MAPE不超过10%
  max_training_time_cpu: 1800,  // CPU模式最大训练时间30分钟
  max_training_time_gpu: 600    // GPU模式最大训练时间10分钟
};
```

### C.4 模型训练流程

#### C.4.1 设备检测与配置
1. **自动设备检测**
   ```python
   def detect_compute_device():
       if torch.cuda.is_available() and COMPUTE_DEVICE in ['gpu', 'auto']:
           return 'gpu'
       else:
           return 'cpu'
   ```

2. **设备特定配置加载**
   - CPU模式：加载CPU优化参数
   - GPU模式：加载GPU优化参数
   - 自动模式：根据检测结果选择配置

3. **资源限制设置**
   - 内存限制配置
   - 线程数配置
   - 批次大小自适应调整

#### C.4.2 数据预处理
1. 数据清洗（处理缺失值、异常值）
2. 特征工程（时间特征提取、滞后特征）
3. 数据标准化
4. 训练集/验证集/测试集划分
5. **设备特定的数据加载优化**
   - CPU模式：多进程数据加载
   - GPU模式：GPU内存预加载

#### C.4.3 模型训练
1. **设备配置初始化**
   ```python
   # 设备配置示例
   if device == 'cpu':
       torch.set_num_threads(cpu_threads)
       model = model.to('cpu')
   elif device == 'gpu':
       torch.cuda.set_per_process_memory_fraction(0.8)
       model = model.to('cuda')
   ```

2. **参数初始化**（根据设备调整）
3. **自适应训练策略**
   - CPU模式：较小的批次大小，较少的训练轮数
   - GPU模式：较大的批次大小，完整的训练轮数
4. **验证集评估**
5. **超参数调优**（设备特定的搜索空间）
6. **最终模型保存**（包含设备信息）

#### C.4.4 模型验证
1. **测试集评估**
2. **准确性检查**（设备无关的指标）
3. **性能分析**
   - 训练时间记录
   - 资源使用情况
   - 设备利用率
4. **模型解释性分析**
5. **性能报告生成**（包含设备信息）

#### C.4.5 部署适配
1. **模型格式转换**
   - CPU部署：ONNX格式优化
   - GPU部署：TensorRT优化（可选）
2. **推理优化**
   - 批量推理配置
   - 内存管理策略
3. **监控指标**
   - 推理延迟
   - 资源使用率
   - 准确性监控

### C.5 现有分析方法集成

基于提供的 `water_habit_analysis.py` 文件，系统将集成以下分析功能：

#### C.4.1 用水习惯分析
- **每小时用水模式分析**: 识别用水高峰时段
- **每周用水模式分析**: 工作日vs周末差异分析
- **时间段用水模式**: 早中晚夜四个时段的用水特征
- **楼栋差异分析**: 不同楼栋的用水习惯对比

#### C.4.2 增压泵控制建议
- **运行时间优化**: 基于用水高峰期的智能启停建议
- **节能效果预测**: 计算预期节能比例
- **控制策略**: 时间控制、压力控制、变频调速等

#### C.4.3 报告生成
- **自动化报告**: 基于分析结果生成详细的Markdown格式报告
- **可视化图表**: 包含多种图表类型（柱状图、热力图、箱线图等）
- **优化建议**: 提供具体的节能和优化建议

## 附录D：环境配置模板

### D.1 环境变量配置

#### D.1.1 .env文件模板
```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hot_water_system
DB_USER=root
DB_PASSWORD=your_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT配置
JWT_SECRET=your_jwt_secret_key
JWT_EXPIRES_IN=7d

# 文件存储配置
UPLOAD_PATH=./uploads
MAX_FILE_SIZE=100MB
ALLOWED_FILE_TYPES=.xlsx,.xls,.csv

# 外部API配置（用户在界面中配置）
# WEATHER_API_KEY=your_apispace_key
# AI_API_KEY=your_dashscope_key

# 计算设备配置
# 可选值: cpu, gpu, auto (自动检测)
COMPUTE_DEVICE=cpu
# GPU配置（仅当COMPUTE_DEVICE=gpu或auto时生效）
CUDA_VISIBLE_DEVICES=0
TENSORFLOW_GPU_MEMORY_GROWTH=true
# CPU配置
TENSORFLOW_INTER_OP_PARALLELISM_THREADS=0  # 0表示使用所有可用核心
TENSORFLOW_INTRA_OP_PARALLELISM_THREADS=0  # 0表示使用所有可用核心

# 系统配置
MAX_CONCURRENT_USERS=20
MAX_DATA_SIZE=1GB
MODEL_CACHE_SIZE=10

# 日志配置
LOG_LEVEL=info
LOG_FILE=./logs/app.log
LOG_MAX_SIZE=100MB
LOG_MAX_FILES=10
```

### D.2 Docker配置

#### D.2.1 docker-compose.yml
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./models:/app/models
    depends_on:
      - db
      - redis
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
        # GPU资源预留（可选，根据COMPUTE_DEVICE环境变量决定是否启用）
    profiles:
      - gpu  # 仅在需要GPU时启用此配置

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
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
      - app

volumes:
  mysql_data:
  redis_data:
```

### D.3 系统要求

#### D.3.1 硬件要求

**基础配置（CPU模式）**:
- **CPU**: 8核心以上（推荐16核心）
- **内存**: 16GB以上（推荐32GB）
- **存储**: 200GB SSD
- **网络**: 千兆网卡

**高性能配置（GPU模式）**:
- **CPU**: 8核心以上
- **内存**: 32GB以上
- **GPU**: NVIDIA RTX 4090（已配置）或其他支持CUDA的显卡
- **存储**: 500GB SSD
- **网络**: 千兆网卡

#### D.3.2 软件要求

**基础环境**:
- **操作系统**: Ubuntu 20.04 LTS 或 CentOS 8 或 Windows 10/11
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.9+
- **Node.js**: 18+

**GPU支持（可选）**:
- **NVIDIA Driver**: 470+
- **CUDA**: 11.8+
- **cuDNN**: 8.6+

#### D.3.3 部署模式选择

**测试/开发环境（CPU模式）**:
```bash
# 设置环境变量
COMPUTE_DEVICE=cpu

# 启动服务（不包含GPU资源）
docker-compose up -d
```

**生产环境（GPU模式）**:
```bash
# 设置环境变量
COMPUTE_DEVICE=gpu

# 启动服务（包含GPU资源）
docker-compose --profile gpu up -d
```

**自动检测模式**:
```bash
# 系统自动检测可用的计算资源
COMPUTE_DEVICE=auto
```

## 附录E：API接口详细文档

### E.1 数据管理API

#### E.1.1 文件上传接口
```typescript
// 上传Excel文件
POST /api/datasets/upload
Content-Type: multipart/form-data

Request:
{
  file: File,                    // Excel文件
  name: string,                  // 数据集名称
  description?: string,          // 描述
  tags?: string[]               // 标签
}

Response:
{
  success: boolean,
  data: {
    id: string,
    name: string,
    fileSize: number,
    rowCount: number,
    columns: Array<{
      name: string,
      type: string,
      sampleValues: any[]
    }>,
    qualityCheck: {
      missingValues: number,
      duplicateRows: number,
      outliers: number,
      dataRange: {
        start: string,
        end: string
      }
    }
  }
}
```

#### E.1.2 数据预览接口
```typescript
// 获取数据预览
GET /api/datasets/{id}/preview?page=1&limit=100

Response:
{
  success: boolean,
  data: {
    columns: string[],
    rows: any[][],
    total: number,
    page: number,
    limit: number
  }
}
```

### E.2 模型训练API

#### E.2.1 创建训练任务
```typescript
// 创建模型训练任务
POST /api/models/train

Request:
{
  name: string,
  algorithm: 'linear_regression' | 'random_forest' | 'lstm',
  datasetId: string,
  parameters: {
    // 根据算法类型的不同参数
  },
  targetColumn: string,
  featureColumns: string[]
}

Response:
{
  success: boolean,
  data: {
    taskId: string,
    status: 'pending' | 'training' | 'completed' | 'failed',
    estimatedTime: number  // 预估训练时间（秒）
  }
}
```

#### E.2.2 获取训练状态
```typescript
// 获取训练进度
GET /api/models/train/{taskId}/status

Response:
{
  success: boolean,
  data: {
    status: string,
    progress: number,      // 0-100
    currentEpoch?: number,
    totalEpochs?: number,
    currentLoss?: number,
    metrics?: {
      mae: number,
      rmse: number,
      r2Score: number
    },
    logs: string[]
  }
}
```

### E.3 预测API

#### E.3.1 单次预测
```typescript
// 单次预测
POST /api/predictions/single

Request:
{
  modelId: string,
  inputData: {
    [key: string]: any
  }
}

Response:
{
  success: boolean,
  data: {
    prediction: number,
    confidence: number,
    explanation?: {
      featureImportance: Array<{
        feature: string,
        importance: number
      }>
    }
  }
}
```

#### E.3.2 批量预测
```typescript
// 批量预测
POST /api/predictions/batch

Request:
{
  modelId: string,
  inputData: Array<{
    [key: string]: any
  }>,
  exportFormat: 'excel' | 'csv' | 'json'
}

Response:
{
  success: boolean,
  data: {
    taskId: string,
    status: 'pending' | 'processing' | 'completed',
    downloadUrl?: string
  }
}
```

## 附录F：错误处理和日志规范

### F.1 错误代码定义

```typescript
enum ErrorCodes {
  // 通用错误 (1000-1999)
  UNKNOWN_ERROR = 1000,
  INVALID_REQUEST = 1001,
  UNAUTHORIZED = 1002,
  FORBIDDEN = 1003,
  NOT_FOUND = 1004,
  
  // 数据相关错误 (2000-2999)
  INVALID_FILE_FORMAT = 2000,
  FILE_TOO_LARGE = 2001,
  INVALID_DATA_FORMAT = 2002,
  INSUFFICIENT_DATA = 2003,
  DATA_QUALITY_ISSUE = 2004,
  
  // 模型相关错误 (3000-3999)
  MODEL_TRAINING_FAILED = 3000,
  MODEL_NOT_FOUND = 3001,
  INVALID_MODEL_PARAMETERS = 3002,
  PREDICTION_FAILED = 3003,
  
  // 外部API错误 (4000-4999)
  WEATHER_API_ERROR = 4000,
  AI_API_ERROR = 4001,
  API_RATE_LIMIT = 4002,
  INVALID_API_KEY = 4003
}
```

### F.2 日志格式规范

```typescript
interface LogEntry {
  timestamp: string,
  level: 'debug' | 'info' | 'warn' | 'error',
  module: string,
  action: string,
  userId?: string,
  requestId?: string,
  message: string,
  data?: any,
  error?: {
    code: number,
    message: string,
    stack?: string
  }
}
```

### F.3 监控指标

#### F.3.1 系统性能指标
- **响应时间**: API接口平均响应时间
- **吞吐量**: 每秒处理请求数
- **错误率**: 错误请求占比
- **资源使用**: CPU、内存、GPU使用率

#### F.3.2 业务指标
- **用户活跃度**: 日活用户数、月活用户数
- **数据处理量**: 每日处理的数据量
- **模型训练**: 训练成功率、平均训练时间
- **预测准确性**: 模型预测的平均误差

---

**附录文档版本**: v2.0  
**最后更新**: 2024年12月  
**维护者**: 开发团队