# 微信云托管部署指南

## 部署代码

### 方式一：使用微信云托管 CLI（推荐）

```bash
# 1. 登录微信云托管
wxcloud login

# 2. 在 backend 目录下执行部署
cd backend
wxcloud deploy

# 3. 等待构建和部署完成
```

### 方式二：通过 Git 推送部署

```bash
# 1. 关联远程仓库（首次配置）
git remote add wxcloud <云托管提供的 Git 地址>

# 2. 推送代码触发自动部署
git add .
git commit -m "Update: Add Markdown conversion support"
git push wxcloud main

# 3. 在控制台查看构建进度
```

### 快速部署脚本

```bash
# 使用提供的部署脚本
chmod +x deploy.sh
./deploy.sh
```

## 环境变量配置

在微信云托管控制台中，需要配置以下环境变量：

### 必需配置

| 变量名            | 说明         | 示例值                     |
| ----------------- | ------------ | -------------------------- |
| `PUBLIC_BASE_URL` | 公网访问地址 | `https://convertease.site` |
| `PORT`            | 服务端口     | `8080`                     |
| `HOST`            | 监听地址     | `0.0.0.0`                  |

### 可选配置

| 变量名               | 说明                         | 默认值  |
| -------------------- | ---------------------------- | ------- |
| `DEBUG`              | 调试模式                     | `false` |
| `REDIS_URL`          | Redis 连接地址（多实例必需） | 空      |
| `MAX_CONCURRENT`     | 最大并发转换数               | `2`     |
| `CONVERSION_TIMEOUT` | 转换超时时间（秒）           | `300`   |
| `MAX_FILE_SIZE_MB`   | 最大文件大小（MB）           | `100`   |

## 配置步骤

### 1. 微信云托管控制台

1. 登录微信云托管控制台
2. 进入你的服务 → 版本管理
3. 编辑版本或新建版本
4. 在"环境变量"选项卡中添加配置：

```
PUBLIC_BASE_URL=https://convertease.site
PORT=8080
HOST=0.0.0.0
```

### 2. 域名配置

确保 `convertease.site` 域名已经：

- ✅ 在微信云托管控制台中绑定
- ✅ DNS 解析已生效
- ✅ SSL 证书已配置（云托管会自动处理）

### 3. Redis 配置（推荐用于生产环境）

如果你的服务配置了多个实例，需要配置 Redis 来共享任务状态：

1. 在云托管控制台创建 Redis 实例
2. 获取内网连接地址，格式如：`redis://:password@10.0.0.123:6379/0`
3. 添加环境变量：

```
REDIS_URL=redis://:your_password@your_host:6379/0
```

## 验证部署

部署完成后，访问以下接口验证：

```bash
# 健康检查
curl https://convertease.site/health

# 查看服务器状态
curl https://convertease.site/server-status

# 查看支持的格式（检查是否包含 .md）
curl https://convertease.site/supported-formats
```

预期返回：

- 健康检查应该返回 `{"ok": true}`
- 服务器状态中的 `publicUrl` 应该显示 `https://convertease.site`
- 支持的格式中的 `allowedExtensions` 应包含 `".md"`

## Markdown 转换支持

最新版本新增了 Markdown 文件转换支持：

- **支持格式**: `.md` → `.html`, `.pdf`, `.docx`
- **转换脚本**:
  - `md_to_html.py` - Markdown 转 HTML
  - `md_to_pdf.py` - Markdown 转 PDF（通过 HTML 中间格式）
  - `md_to_docx.py` - Markdown 转 Word 文档

确保部署时包含这些脚本文件。

## 常见问题

### Q: 部署后 Markdown 转换返回 400 错误

**A:** 检查：

1. 云端代码是否已更新（查看 `/supported-formats` 是否包含 `.md`）
2. 转换脚本是否已上传（`app/scripts/md_*.py`）
3. 环境变量配置是否正确

### Q: 公网地址仍然显示 localhost

**A:** 检查环境变量是否正确设置，重新部署服务后需要重启所有实例。

### Q: 文件上传后无法访问

**A:** 确保：

1. `PUBLIC_BASE_URL` 设置正确
2. 云托管的文件存储持久化已配置
3. 端口映射正确（容器端口 8080）

### Q: 转换任务状态不同步

**A:** 如果配置了多个实例，必须配置 Redis 来共享任务状态。

## 监控和日志

在微信云托管控制台查看：

- **日志** - 实时查看服务日志，确认启动信息和错误
- **监控** - 查看 CPU、内存、请求量
- **告警** - 配置异常告警规则

## 本地测试

在本地测试时，创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置本地配置：

```
PUBLIC_BASE_URL=http://localhost:8080
```

启动服务：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

测试 Markdown 转换：

```bash
# 测试 MD 转 HTML
curl -X POST http://localhost:8080/convert/upload \
  -F "file=@tests/samples/sample.md" \
  -F "category=document" \
  -F "source=md" \
  -F "target=html"

# 测试 MD 转 PDF
curl -X POST http://localhost:8080/convert/upload \
  -F "file=@tests/samples/sample.md" \
  -F "category=document" \
  -F "source=md" \
  -F "target=pdf"
```
