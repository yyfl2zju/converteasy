# ConvertEasy

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/WeChat-MiniProgram-07C160.svg" alt="WeChat">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

> 🔄 专业的文档和音频格式转换工具，支持微信小程序和 Web API

## 📖 项目简介

ConvertEasy 是一个功能强大的文件格式转换平台，包含：

- **后端服务** (`backend/`)：基于 Python FastAPI 的高性能异步转换服务
- **微信小程序** (`miniprogram/`)：便捷的移动端用户界面

## ✨ 主要特性

### 🔄 丰富的格式支持

| 类型 | 源格式                                               | 目标格式                                                                 |
| ---- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| 文档 | PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF, HTML | PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, RTF, HTML, CSV, ODT, ODS, ODP |
| 音频 | MP3, WAV, AAC, FLAC, M4A, OGG, WMA                   | MP3, WAV, AAC, FLAC, M4A, OGG, WMA                                       |

### 🚀 技术亮点

- **异步处理**：基于 FastAPI 的异步架构，支持高并发
- **任务队列**：后台任务处理，避免请求超时
- **自动清理**：定时清理过期文件，节省存储空间
- **安全防护**：速率限制、CORS 配置、文件类型白名单
- **Docker 支持**：提供优化的多阶段构建配置

## 📂 项目结构

```text
converteasy/
├── backend/                    # 后端服务
│   ├── app/                    # 应用代码
│   │   ├── main.py            # 入口文件
│   │   ├── config.py          # 配置管理
│   │   ├── models.py          # 数据模型
│   │   ├── routers/           # API 路由
│   │   ├── scripts/           # 转换脚本
│   │   ├── middleware/        # 中间件
│   │   └── utils/             # 工具函数
│   ├── tests/                  # 测试用例
│   ├── Dockerfile             # Docker 构建文件
│   └── requirements.txt       # Python 依赖
│
├── miniprogram/                # 微信小程序
│   ├── pages/                  # 页面目录
│   │   ├── index/             # 首页
│   │   ├── document/          # 文档转换
│   │   └── audio/             # 音频转换
│   ├── utils/                  # 工具函数
│   ├── __tests__/             # 测试用例
│   └── app.js                 # 入口文件
│
├── .pre-commit-config.yaml    # pre-commit 配置
└── README.md                  # 项目说明
```

## 🚀 快速开始

### 后端服务

```bash
# 进入后端目录
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 安装系统依赖（LibreOffice + FFmpeg）
# macOS
brew install --cask libreoffice && brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install libreoffice-core libreoffice-writer libreoffice-calc libreoffice-impress ffmpeg

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

详细说明请查看 [backend/README.md](./backend/README.md)

### 微信小程序

1. 使用微信开发者工具打开 `miniprogram` 目录
2. 在 `project.config.json` 中配置你的 AppID
3. 编译并预览

详细说明请查看 [miniprogram/README.md](./miniprogram/README.md)

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=app --cov-report=html
```

### 前端测试

```bash
cd miniprogram

# 安装依赖
npm install

# 运行测试
npm test

# 运行测试并显示覆盖率
npm run test:coverage
```

## 🔧 开发工具

### Pre-commit Hooks

项目配置了 pre-commit hooks 来保证代码质量：

```bash
# 安装 pre-commit
pip install pre-commit

# 安装 git hooks
pre-commit install

# 手动运行所有检查
pre-commit run --all-files
```

配置的检查项包括：

- **通用**：尾随空格、文件结尾、YAML/JSON 格式
- **Python**：Black 格式化、isort 导入排序、Flake8 代码检查、mypy 类型检查
- **JavaScript**：ESLint 代码检查、Prettier 格式化

## 📡 API 文档

服务启动后可访问自动生成的 API 文档：

- **Swagger UI**: <http://localhost:8080/docs>
- **ReDoc**: <http://localhost:8080/redoc>

### 核心接口

| 接口                     | 方法 | 说明                   |
| ------------------------ | ---- | ---------------------- |
| `/convert/upload`        | POST | 上传文件并创建转换任务 |
| `/convert/task/{taskId}` | GET  | 查询任务状态           |
| `/supported-formats`     | GET  | 获取支持的格式         |
| `/detect-targets`        | POST | 检测可转换的目标格式   |
| `/download/{filename}`   | GET  | 下载转换结果           |
| `/health`                | GET  | 健康检查               |

## 🐳 Docker 部署

```bash
cd backend

# 构建镜像
docker build -t converteasy-backend .

# 运行容器
docker run -d -p 8080:8080 --name converteasy converteasy-backend
```

## 📝 环境变量

| 变量名                 | 说明                 | 默认值          |
| ---------------------- | -------------------- | --------------- |
| `PORT`                 | 服务端口             | 8080            |
| `MAX_CONCURRENT_TASKS` | 最大并发任务数       | 5               |
| `FILE_EXPIRE_HOURS`    | 文件过期时间（小时） | 24              |
| `MAX_FILE_SIZE`        | 最大文件大小（字节） | 52428800 (50MB) |

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 提交 Pull Request

请确保：

- 代码通过所有 pre-commit 检查
- 新功能包含相应的测试用例
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Python Web 框架
- [LibreOffice](https://www.libreoffice.org/) - 强大的开源办公套件
- [FFmpeg](https://ffmpeg.org/) - 领先的多媒体处理框架
