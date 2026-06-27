# Dixiyang

## 项目简介

Dixiyang 是一个小说创作管理平台，采用前后端分离架构，为小说创作者提供全方位的工具支持。

## 项目结构

```
Dixiyang/
├── dixiyang-engine/     # 后端服务 (Spring Boot)
│   ├── src/
│   ├── docs/            # 后端文档
│   │   └── 后端接口文档.md
│   └── AGENTS.md        # 后端开发指南
├── dixiyang-vue/        # 前端应用 (Vue 3)
│   ├── Dixiyang-vue3/
│   ├── docs/            # 前端文档
│   │   └── 前端接口需求文档.md
│   └── AGENTS.md        # 前端开发指南
└── docs/                # 项目总体文档
    ├── README.md                    # 文档索引
    ├── 项目总体情况总结.md           # 项目概览
    ├── 前后端接口对照分析.md         # 接口对照分析
    ├── 后端开发技术文档.md           # 后端技术详解
    └── HELP.md                      # 帮助文档
```

## 快速开始

### 环境要求

- JDK 17+
- Maven 3.6+
- MySQL 8.0+
- Node.js 18+
- Docker（推荐，用于 MySQL/Redis/Qdrant）

### 1. 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 填入你自己的配置
```

**必须配置的变量：**

| 变量 | 说明 | 示例 |
|------|------|------|
| `DB_USERNAME` | MySQL 用户名 | `root` |
| `DB_PASSWORD` | MySQL 密码 | `your_password` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxx` |

> ⚠️ **安全提醒**：`.env` 文件包含敏感信息，已在 `.gitignore` 中排除，不要提交到 git！

### 2. 启动数据库（Docker）

```bash
docker run -d --name mysql-hmdp \
  -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=123321 \
  -e MYSQL_DATABASE=dixiyang \
  mysql:8.0
```

### 3. 后端启动

```bash
cd dixiyang-engine

# IDEA 用户：确保项目 SDK 设置为 JDK 17
# 命令行用户：
export JAVA_HOME=~/.sdkman/candidates/java/17.0.10-tem
mvn spring-boot:run
```

后端启动后访问：http://localhost:8084/api

### 4. 前端启动

```bash
cd dixiyang-vue/Dixiyang-vue3
npm install
npm run dev
```

前端启动后访问：http://localhost:5173

> 前端通过 Vite 代理将 `/api` 请求转发到后端 8084 端口

## 文档导航

- 📚 [**文档索引**](./docs/README.md) - 所有文档的导航中心
- 📋 [**项目总体情况总结**](./docs/项目总体情况总结.md) - 了解项目全貌
- 🔍 [**前后端接口对照分析**](./docs/前后端接口对照分析.md) - 接口完成状态
- 🔧 [**后端开发指南**](./dixiyang-engine/AGENTS.md) - 后端开发者必读
- 📖 [**后端接口文档**](./dixiyang-engine/docs/后端接口文档.md) - API 详细说明
- 🎨 [**前端开发指南**](./dixiyang-vue/AGENTS.md) - 前端开发者必读
- 📝 [**前端接口需求文档**](./dixiyang-vue/docs/前端接口需求文档.md) - 接口需求说明
- 🏗️ [**后端开发技术文档**](./docs/后端开发技术文档.md) - 技术架构详解

## 技术栈

### 后端
- Spring Boot 3.4.2
- MyBatis Plus 3.5.10.1
- Spring Security + JWT
- MySQL 8.0+
- Qdrant (向量数据库)
- Redis
- Spring AI

### 前端
- Vue 3.5.29
- Vite 7.3.1
- Pinia 3.0.4
- Vue Router 5.0.3
- Element Plus 2.13.5
- Axios 1.13.6
- Tailwind CSS 4.2.1

## 核心功能

- ✅ 用户认证与授权
- ✅ 小说管理（CRUD）
- ✅ 角色管理（CRUD）
- ✅ 时间线管理（CRUD + 行内编辑）
- ✅ 故事节点管理（CRUD）
- ✅ 封面上传（MD5去重）
- ✅ RAG 智能创作助手
- ⚠️ 用户配置（待完善）

## 开发状态

详见 [前后端接口对照分析](./docs/前后端接口对照分析.md)

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

---
*最后更新: 2026-05-31*
