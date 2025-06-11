# 部署指南：热水系统智能分析平台

本文档提供了使用 Docker 和 Docker Compose 在生产环境中部署"热水系统智能分析平台"的详细步骤。

## 1. 先决条件

在开始之前，请确保您的系统中已安装以下软件：

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 2. 环境配置

在部署应用之前，您需要配置一些必要的环境变量。

### a. 数据库配置

`docker-compose.yml` 文件需要一个名为 `.env.db` 的文件来配置数据库连接。请在项目的根目录下 **手动创建** 此文件：

```bash
# 在 Linux 或 macOS 中
touch .env.db

# 在 Windows (PowerShell) 中
New-Item .env.db
```

然后，将以下内容复制到 `.env.db` 文件中，并 **务必修改密码** 为一个强密码：

```ini
# .env.db
# PostgreSQL 连接设置
DB_NAME=hotwater_system
DB_USER=hotwater_user
DB_PASSWORD=a_very_secure_password_change_me
```

### b. 中文字体 (重要)

PDF报告生成功能需要一个中文字体文件才能正确显示中文。

1.  请从您的操作系统中（例如 Windows 的 `C:\Windows\Fonts` 目录）找到一个名为 `simsun.ttf` (宋体) 的字体文件。
2.  将这个 `simsun.ttf` 文件复制到后端的 `backend/fonts/` 目录下。如果该目录不存在，请创建它。

## 3. 启动应用

完成上述配置后，您可以在项目根目录下运行以下命令来构建并启动所有服务（前端、后端、数据库）：

```bash
docker-compose up --build -d
```

- `--build` 标志会强制重新构建镜像，确保应用代码的最新更改被应用。
- `-d` 标志（detached mode）会在后台运行容器。

首次启动时，Docker 会下载所有必需的镜像并构建您的应用，这可能需要几分钟时间。

## 4. 访问应用

所有服务成功启动后：

- **前端应用** 将在 `http://localhost:8080` 上可用。
- **后端API** 将在 `http://localhost:5000` 上可用（主要由前端代理访问）。
- **PostgreSQL数据库** 将在主机的 `5432` 端口上可用（主要用于开发或调试）。

## 5. 初始化数据库

在首次启动应用后，数据库是空的。您需要执行数据库初始化命令来创建所有必要的表。

在容器启动并运行后，打开一个新的终端，并执行以下命令：

```bash
docker-compose exec backend flask init-db
```

这条命令会在 `backend` 服务的容器内执行 `flask init-db` 命令，该命令会根据您在代码中定义的模型创建数据库表。

**恭喜！** 至此，您的热水系统智能分析平台已成功部署并可以开始使用。

## 6. 管理应用

以下是一些有用的 Docker Compose 命令来管理您的应用：

- **查看日志**:
  ```bash
  # 查看所有服务的日志
  docker-compose logs -f

  # 只查看后端服务的日志
  docker-compose logs -f backend
  ```

- **停止应用**:
  ```bash
  # 停止并移除容器
  docker-compose down
  ```

- **停止应用并删除数据卷**:
  > **警告**: 这将删除所有数据库数据，请谨慎操作！
  ```bash
  docker-compose down -v
  ``` 