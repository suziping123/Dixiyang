# Dixiyang Vue 前端开发指南

## 项目概述

Dixiyang Vue 是基于 Vue 3 的前端应用，为用户提供小说创作管理的图形界面。项目采用现代化的前端技术栈，提供了丰富的交互体验和响应式设计。

## 技术栈

- **Vue**: 3.5.29
- **Vite**: 7.3.1
- **Pinia**: 3.0.4 (状态管理)
- **Vue Router**: 5.0.3 (路由管理)
- **Element Plus**: 2.13.5 (UI组件库)
- **Axios**: 1.13.6 (HTTP客户端)
- **GSAP**: 3.14.2 (动画库)
- **Motion**: 12.38.0 (动画库)
- **Tailwind CSS**: 4.2.1 (CSS框架)

## 项目结构

```
src/
├── api/              # API接口定义
│   ├── characterApi.ts    # 角色相关API
│   ├── novelApi.ts        # 小说相关API
│   └── types.ts           # 类型定义
├── assets/           # 静态资源
│   ├── logo.svg
│   └── main.css
├── components/       # 可复用组件
│   ├── BackgroundControl.vue    # 背景控制组件
│   ├── CreateCard.vue           # 创建卡片组件
│   ├── CreateNovelModal.vue     # 创建小说模态框
│   ├── FloatingNav.vue          # 浮动导航组件
│   ├── FontControl.vue          # 字体控制组件
│   ├── NovelCard.vue            # 小说卡片组件
│   ├── SettingsSection.vue      # 设置部分组件
│   └── TextColorCustomizer.vue  # 文本颜色定制组件
├── composables/      # 组合式函数
│   ├── useAuth.ts               # 认证相关
│   ├── useBackgroundConfig.ts   # 背景配置
│   ├── useFontConfig.ts         # 字体配置
│   ├── useTextColorAdapter.ts   # 文本颜色适配器
│   ├── useTextColorCustomizer.ts # 文本颜色定制
│   ├── useThemeSystem.ts        # 主题系统
│   └── useUser.ts               # 用户相关
├── images/           # 图片资源
├── router/           # 路由配置
│   └── index.ts
├── stores/           # 状态管理
│   ├── UserStore.ts             # 用户状态
│   └── counter.ts               # 计数器示例
├── utils/            # 工具函数
│   ├── colorUtils.ts            # 颜色工具
│   ├── confirm.ts               # 确认对话框
│   ├── http.ts                  # HTTP客户端封装
│   └── textColorAdaptationDemo.ts # 文本颜色适配演示
├── views/            # 页面视图
│   ├── AboutView.vue            # 关于页面
│   ├── CharacterManagerView.vue # 角色管理页面
│   ├── HomeView.vue             # 首页
│   ├── LoginView.vue            # 登录页面
│   ├── NovelEditorView.vue      # 小说编辑页面
│   ├── RagAssistantView.vue     # RAG助手页面
│   └── SettingsView.vue         # 设置页面
├── App.vue           # 根组件
└── main.ts           # 入口文件
```

## 核心功能模块

### 1. 用户认证
- 登录/注册功能
- JWT Token 管理
- 用户状态持久化

### 2. 小说管理
- 小说列表展示
- 创建新小说
- 编辑小说信息
- 删除小说

### 3. 角色管理
- 角色列表展示
- 创建/编辑/删除角色
- 角色属性管理

### 4. RAG 智能助手
- AI 对话界面
- 上下文选择（小说、角色、节点）
- 智能创作建议

### 5. 个性化设置
- 背景定制
- 字体设置
- 主题切换
- 创作偏好配置

## API 接口调用

### HTTP 客户端配置

项目使用 Axios 作为 HTTP 客户端，并在 `src/utils/http.ts` 中进行了封装：

```typescript
import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 1000000
})

// 请求拦截器：自动携带 Token
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一处理响应
http.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      return res
    }
    return Promise.reject(new Error(res.msg || '操作失败'))
  },
  (error) => {
    const errMsg = error.response?.data?.msg || error.message || '网络异常，请重试'
    return Promise.reject(new Error(errMsg))
  }
)
```

### 主要 API 接口

#### 认证相关
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册

#### 小说管理
- `GET /novel/listall?page=1&pageSize=10` - 获取小说列表
- `POST /novel/create` - 创建小说
- `POST /novel/update/{novelId}` - 更新小说
- `POST /novel/delete/{novelId}` - 删除小说

#### 角色管理
- `GET /novelCharacter/list/{novelId}?page=1&pageSize=10` - 获取角色列表（分页）
- `GET /novelCharacter/all/{novelId}` - 获取所有角色
- `GET /novelCharacter/{id}` - 获取角色详情
- `POST /novelCharacter/create` - 创建角色
- `POST /novelCharacter/update/{id}` - 更新角色
- `POST /novelCharacter/delete/{id}` - 删除角色

#### RAG 聊天
- `POST /chat` - AI 对话

## 状态管理

使用 Pinia 进行状态管理，主要 store 包括：

### UserStore
管理用户相关信息：
- 用户登录状态
- 用户信息
- Token 管理

## 路由配置

使用 Vue Router 进行路由管理，主要路由包括：
- `/login` - 登录页面
- `/home` - 首页
- `/character-manager/:id` - 角色管理页面
- `/novel-editor/:id` - 小说编辑页面
- `/rag-assistant` - RAG 助手页面
- `/settings` - 设置页面

## 组件设计原则

1. **单一职责**: 每个组件只负责一个功能
2. **可复用性**: 提取通用组件供多处使用
3. **props 向下，events 向上**: 父子组件通信规范
4. **组合式 API**: 使用 `<script setup>` 语法

## 样式规范

1. **Scoped CSS**: 使用 scoped 样式避免冲突
2. **CSS 变量**: 使用 CSS 变量实现主题切换
3. **响应式设计**: 支持不同屏幕尺寸
4. **动画效果**: 使用 GSAP 和 Motion 实现流畅动画

## 开发规范

### 代码风格
- 使用 TypeScript 提供类型安全
- 遵循 Vue 3 组合式 API 最佳实践
- 使用 ESLint 和 Prettier 保证代码质量

### 命名规范
- 组件名使用 PascalCase
- 文件名使用 kebab-case
- 变量和函数使用 camelCase

### 注释规范
- 关键逻辑添加注释说明
- 复杂算法提供详细说明
- 公共 API 提供 JSDoc 注释

## 构建和部署

### 开发环境
```bash
npm run dev
```

### 生产构建
```bash
npm run build
```

### 预览构建结果
```bash
npm run preview
```

## 测试

### 单元测试
```bash
npm run test:unit
```

## 性能优化

1. **代码分割**: 使用动态导入实现路由级代码分割
2. **图片优化**: 使用合适的图片格式和尺寸
3. **懒加载**: 对非关键资源使用懒加载
4. **缓存策略**: 合理设置浏览器缓存

## 功能完成状态对照

### ✅ 前端已完成 + 后端已实现

| 功能模块 | 前端实现 | 后端接口 | 状态 |
|---------|---------|---------|------|
| **用户认证** | ✅ LoginView.vue<br>✅ useAuth.ts | ✅ POST /auth/login<br>✅ POST /auth/register | ✅ 完成 |
| **小说列表** | ✅ HomeView.vue<br>✅ novelApi.ts | ✅ GET /novel/listall | ✅ 完成 |
| **创建小说** | ✅ CreateNovelModal.vue<br>✅ novelApi.ts | ✅ POST /novel/create | ✅ 完成 |
| **删除小说** | ✅ HomeView.vue<br>✅ novelApi.ts | ✅ POST /novel/delete/{id} | ✅ 完成 |
| **角色列表** | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ GET /novelCharacter/list/{id}<br>✅ GET /novelCharacter/all/{id} | ✅ 完成 |
| **角色详情** | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ GET /novelCharacter/{id} | ✅ 完成 |
| **创建角色** | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ POST /novelCharacter/create | ✅ 完成 |
| **更新角色** | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ POST /novelCharacter/update/{id} | ✅ 完成 |
| **删除角色** | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ POST /novelCharacter/delete/{id} | ✅ 完成 |
| **RAG聊天** | ✅ RagAssistantView.vue<br>✅ http.ts | ✅ POST /chat<br>✅ GET /chat | ✅ 完成 |
| **故事节点查询** | ✅ RagAssistantView.vue (部分) | ✅ GET /storyNode/all/{novelId} | ✅ 完成 |

### ⚠️ 前端已实现 + 后端未完全实现

| 功能模块 | 前端实现 | 后端状态 | 缺失内容 |
|---------|---------|---------|----------|
| **小说编辑** | ⚠️ NovelEditorView.vue (占位页面) | ❌ 无完整实现 | 需要实现编辑器相关接口 |
| **故事节点CRUD** | ⚠️ RagAssistantView.vue (仅查询) | ❌ 缺少 CRUD | 需要实现：<br>- POST /storyNode/create<br>- POST /storyNode/update/{id}<br>- POST /storyNode/delete/{id} |
| **时间线管理** | ⚠️ SettingsView.vue (配置项) | ❌ 完全未实现 | 需要实现：<br>- GET /timeline/list/{novelId}<br>- POST /timeline/create<br>- POST /timeline/update/{id}<br>- POST /timeline/delete/{id} |

### ❌ 前端未实现 + 后端未实现

| 功能模块 | 前端状态 | 后端状态 | 说明 |
|---------|---------|---------|------|
| **文件上传** | ❌ 未实现 | ❌ FileController为空 | 需要实现：<br>- 前端：上传组件<br>- 后端：POST /upload/novel-cover |
| **用户配置** | ⚠️ SettingsView.vue (UI完成) | ❌ UserConfigController为空 | 需要实现：<br>- GET /userConfig/get<br>- POST /userConfig/update |
| **小说关系** | ❌ 未实现 | ❌ NovelRelationController为空 | 需要实现前后端完整功能 |
| **小说更新** | ⚠️ 前端有需求 | ✅ POST /novel/update/{id} | 前端需要添加更新界面 |

### 📊 完成度统计

#### 前端完成度
- ✅ 完全实现：**11个功能**
- ⚠️ 部分实现：**3个功能**
- ❌ 未实现：**4个功能**
- **前端总体完成度：约 65%**

#### 后端完成度
- ✅ 完全实现：**14个接口**
- ⚠️ 部分实现：**1个接口** (storyNode)
- ❌ 未实现：**10个接口**
- **后端总体完成度：约 55%**

#### 前后端匹配度
- ✅ 完全匹配：**11个功能**
- ⚠️ 不匹配：**5个功能** (前端有需求但后端缺失，或后端有接口但前端未调用)
- **匹配度：约 69%**

### 🎯 下一步开发优先级

#### 高优先级（立即开发）
1. **文件上传功能** - 影响小说封面功能
   - 前端：创建上传组件
   - 后端：实现 FileController

2. **故事节点完整 CRUD** - 核心创作功能
   - 后端：补充 create/update/delete 接口
   - 前端：完善编辑器界面

3. **时间线管理** - 核心创作功能
   - 后端：完整实现 TimelineController
   - 前端：创建时间线管理界面

#### 中优先级（近期开发）
4. **用户配置管理** - 提升用户体验
   - 后端：实现 UserConfigController
   - 前端：连接 SettingsView 到后端

5. **小说更新界面** - 完善小说管理
   - 前端：创建小说编辑/更新界面

#### 低优先级（后续开发）
6. **小说关系管理** - 丰富功能体系
   - 前后端同时开发

---
## 主题系统

### 全局主题（3套）
每个主题是完整的 CSS class，定义所有页面元素的配色和风格。

| 主题 | class | 背景 | 文字 | 适用场景 |
|------|-------|------|------|---------|
| 动态暗色 | `theme-dynamic` | 暗色动画渐变 | 浅色 | 沉浸式创作 |
| 极简暗色 | `theme-minimal-dark` | 纯黑 | 浅色 | 专注写作 |
| 极简亮色 | `theme-minimal-light` | 纯白 | 深色 | **默认**，日常使用 |

切换主题只需修改 `<html>` 的 class，全部 CSS 变量由 `main.css` 中的 class 定义。

### 背景图预设
图片存放在 `src/images/back/`，通过 `import.meta.glob` 自动发现。
新增背景图只需将图片放入该目录，重启 dev server 即可自动识别。
背景图以 QQ 聊天背景风格叠加（半透明 + 轻微模糊），不影响前方内容可读性。

### 使用方式
```typescript
// 获取主题配置 composable
const bgConfig = useBackgroundConfig()

// 切换主题
bgConfig.setTheme('minimal-light')

// 切换背景图（null 为无背景图）
bgConfig.setBgImage('my-image-name')

// 恢复默认
bgConfig.resetToDefault()
```

---
*文档版本: v1.2*
*最后更新: 2026-05-31*