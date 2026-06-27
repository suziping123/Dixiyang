# Dixiyang Engine 后端开发指南
## OpenCode Global Rules

你是一个顶级的程序员。在每次对话中，你必须严格遵循以下“准则”：

### 核心准则

1. **绝对中文**：必须使用**简体中文**进行交流（除非是代码、专有名词等特殊情况）。
2. **言简意赅**：解释或评论代码时，必须附带**清晰且极为精简**的中文文档。
3. **先查后问**：遇到代码问题，优先在本项目的 `**/docs/` 目录或相关代码文件中寻找答案，找不到再向我提问。
4. **规划先行**：开始写代码前，必须先简要说明你的计划，并清晰扼要地分析其利弊。
5. **环境**：在每次实现完一个功能后进行git项目管理
6. **记录习惯**：在每次提交代码后，必须记录下你的操作在对应的md文档里面。


## 项目概述

Dixiyang Engine 是基于 Spring Boot 3 的后端服务，为 Dixiyang 前端应用提供 API 支持。项目采用分层架构设计，集成了 AI 能力、向量数据库和缓存系统，为小说创作提供全方位的工具支持。

## 技术栈

- **Spring Boot**: 3.4.2
- **MyBatis Plus**: 3.5.10.1
- **Spring Security + JWT**: 身份认证
- **MySQL**: 8.0+
- **Qdrant**: 向量数据库（RAG系统）
- **Redis**: 缓存系统
- **Spring AI**: 1.0.0-M5

## 项目结构

```
src/main/java/com/dixiyang/server/
├── Common/          # 通用工具类和常量
│   └── Result.java   # 统一响应结果类
├── Config/          # 配置类
│   ├── JwtAuthenticationFilter.java  # JWT 认证过滤器
│   ├── MybatisPlusConfig.java        # MyBatis Plus 配置
│   ├── SecurityConfig.java           # 安全配置
│   └── WebMvcConfig.java             # Web MVC 配置
├── Controller/      # 控制器层
│   ├── AppUserController.java        # 用户控制器
│   ├── AuthController.java           # 认证控制器
│   ├── ChatController.java           # 聊天控制器（RAG系统）
│   ├── FileController.java           # 文件控制器
│   ├── NovelCharacterController.java # 角色控制器
│   ├── NovelController.java          # 小说控制器
│   ├── NovelRelationController.java  # 关系控制器
│   ├── StoryNodeController.java      # 故事节点控制器
│   ├── TimelineController.java       # 时间线控制器
│   ├── UserConfigController.java     # 用户配置控制器
│   └── UserController.java           # 用户控制器
├── Entity/          # 实体类
│   ├── VO/          # 视图对象
│   │   ├── NovelVO.java              # 小说视图对象
│   │   └── UserVO.java               # 用户视图对象
│   ├── dto/         # 数据传输对象
│   │   ├── AuthDTO.java              # 认证DTO
│   │   ├── BackgroundConfigDTO.java  # 背景配置DTO
│   │   ├── FontColorsDTO.java        # 字体颜色DTO
│   │   ├── NovelDTO.java             # 小说DTO
│   │   ├── PasswordDTO.java          # 密码DTO
│   │   └── UserUpdateDTO.java        # 用户更新DTO
│   ├── AppUser.java                  # 应用用户实体
│   ├── File.java                     # 文件实体
│   ├── NovelCharacter.java           # 角色实体
│   ├── NovelRelation.java            # 关系实体
│   ├── Novels.java                   # 小说实体
│   ├── StoryNode.java                # 故事节点实体
│   ├── Timeline.java                 # 时间线实体
│   └── UserConfig.java               # 用户配置实体
├── Mapper/          # MyBatis 映射接口
│   ├── AppUserMapper.java            # 用户映射接口
│   ├── FileMapper.java               # 文件映射接口
│   ├── NovelCharacterMapper.java     # 角色映射接口
│   ├── NovelMapper.java              # 小说映射接口
│   ├── NovelRelationMapper.java      # 关系映射接口
│   ├── StoryNodeMapper.java          # 故事节点映射接口
│   ├── TimelineMapper.java           # 时间线映射接口
│   └── UserConfigMapper.java         # 用户配置映射接口
├── Service/         # 服务层
│   ├── impl/        # 服务实现
│   │   ├── AppUserServiceImpl.java   # 用户服务实现
│   │   ├── AuthServiceImpl.java      # 认证服务实现
│   │   ├── FileServiceImpl.java      # 文件服务实现
│   │   ├── NovelCharacterServiceImpl.java # 角色服务实现
│   │   ├── NovelRelationServiceImpl.java  # 关系服务实现
│   │   ├── NovelServiceImpl.java     # 小说服务实现
│   │   ├── StoryNodeServiceImpl.java # 故事节点服务实现
│   │   ├── TimelineServiceImpl.java  # 时间线服务实现
│   │   ├── UserConfigServiceImpl.java # 用户配置服务实现
│   │   └── UserServiceIml.java       # 用户服务实现
│   ├── AuthService.java              # 认证服务接口
│   ├── EmbeddingService.java         # 嵌入服务接口（RAG）
│   ├── IAppUserService.java          # 用户服务接口
│   ├── IFileService.java             # 文件服务接口
│   ├── INovelCharacterService.java   # 角色服务接口
│   ├── INovelRelationService.java    # 关系服务接口
│   ├── IStoryNodeService.java        # 故事节点服务接口
│   ├── ITimelineService.java         # 时间线服务接口
│   ├── IUserConfigService.java       # 用户配置服务接口
│   ├── NovelService.java             # 小说服务接口
│   └── UserService.java              # 用户服务接口
├── Utils/           # 工具类
│   └── JwtUtils.java                 # JWT 工具类
├── CodeGenerator.java                # 代码生成器
└── DixiyangEngineApplication.java    # 主应用类
```

## 核心功能模块

### 1. 用户认证与授权
- 基于 Spring Security 和 JWT 的身份认证
- 用户注册和登录功能
- 权限控制机制

### 2. 小说管理
- 小说的 CRUD 操作
- 分页查询功能
- 小说详情获取

### 3. 角色管理
- 角色的 CRUD 操作
- 按小说分类管理角色
- 角色属性管理

### 4. RAG 系统
- 基于向量数据库的检索增强生成
- AI 对话功能
- 上下文感知回答

### 5. 文件管理
- 文件上传和存储
- 封面图片管理

## API 接口规范

### 统一响应格式
所有 API 接口使用统一的响应格式：
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

### 认证相关接口
- `POST /auth/login` - 用户登录
- `POST /auth/register` - 用户注册

### 小说管理接口
- `GET /novel/listall?page=1&pageSize=10` - 获取小说列表
- `GET /novel/{id}` - 获取小说详情
- `POST /novel/create` - 创建小说
- `POST /novel/update/{novelId}` - 更新小说
- `POST /novel/delete/{novelId}` - 删除小说

### 角色管理接口
- `GET /novelCharacter/list/{novelId}?page=1&pageSize=10` - 获取角色列表（分页）
- `GET /novelCharacter/all/{novelId}` - 获取所有角色
- `GET /novelCharacter/{id}` - 获取角色详情
- `POST /novelCharacter/create` - 创建角色
- `POST /novelCharacter/update/{id}` - 更新角色
- `POST /novelCharacter/delete/{id}` - 删除角色

### 时间线管理接口
- `GET /timeline/all/{novelId}` - 获取小说所有时间线
- `POST /timeline/create` - 创建时间线
- `POST /timeline/update/{id}` - 更新时间线
- `POST /timeline/delete/{id}` - 删除时间线

### 故事节点接口
- `GET /storyNode/all/{novelId}` - 获取小说所有故事节点
- `GET /storyNode/timeline/{timelineId}` - 获取时间线下的故事节点
- `POST /storyNode/create` - 创建故事节点
- `POST /storyNode/update/{id}` - 更新故事节点
- `POST /storyNode/delete/{id}` - 删除故事节点

### 文件上传接口
- `POST /upload/novel-cover` - 上传小说封面（MD5去重）

### RAG 聊天接口
- `GET /chat?message=xxx&useRag=true` - GET 方式聊天
- `POST /chat` - POST 方式聊天（推荐）

## 开发规范

### 代码风格
- 使用驼峰命名法
- 添加适当的类和方法注释
- 遵循 SOLID 原则

### 异常处理
- 统一异常处理机制
- 使用 @ControllerAdvice 全局异常处理
- 返回友好的错误信息

### 日志记录
- 使用 SLF4J 记录日志
- 关键操作记录详细日志
- 生产环境调整日志级别

### 安全最佳实践
- 密码使用 BCrypt 加密
- SQL 注入防护（使用 MyBatis Plus 参数绑定）
- XSS 防护（对用户输入进行过滤）
- CSRF 防护
- 基于角色的访问控制

## 部署说明

### 环境要求
- JDK 17+
- Maven 3.6+
- MySQL 8.0+
- Redis
- Qdrant 向量数据库

### 启动步骤
1. 配置 application.yml 中的数据库连接信息
2. 设置环境变量 DASHSCOPE_API_KEY 和 Qdrant_API_KEY
3. 运行 `mvn spring-boot:run` 或执行主类

### Docker 部署
项目包含 docker-compose.yml 配置文件，可用于容器化部署。

## 功能完成状态对照

### ✅ 后端已实现 + 前端已调用

| 功能模块 | 后端接口 | 前端调用 | 状态 |
|---------|---------|---------|------|
| **用户认证** | ✅ POST /auth/login<br>✅ POST /auth/register | ✅ LoginView.vue<br>✅ useAuth.ts | ✅ 完成 |
| **小说列表** | ✅ GET /novel/listall | ✅ HomeView.vue<br>✅ novelApi.ts | ✅ 完成 |
| **创建小说** | ✅ POST /novel/create | ✅ CreateNovelModal.vue<br>✅ novelApi.ts | ✅ 完成 |
| **删除小说** | ✅ POST /novel/delete/{id} | ✅ HomeView.vue<br>✅ novelApi.ts | ✅ 完成 |
| **更新小说** | ✅ POST /novel/update/{id} | ⚠️ 前端有API但未使用 | ✅ 完成 |
| **角色列表(分页)** | ✅ GET /novelCharacter/list/{id} | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **角色列表(全部)** | ✅ GET /novelCharacter/all/{id} | ✅ RagAssistantView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **角色详情** | ✅ GET /novelCharacter/{id} | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **创建角色** | ✅ POST /novelCharacter/create | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **更新角色** | ✅ POST /novelCharacter/update/{id} | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **删除角色** | ✅ POST /novelCharacter/delete/{id} | ✅ CharacterManagerView.vue<br>✅ characterApi.ts | ✅ 完成 |
| **RAG聊天(GET)** | ✅ GET /chat | ⚠️ 前端未使用 | ✅ 完成 |
| **RAG聊天(POST)** | ✅ POST /chat | ✅ RagAssistantView.vue<br>✅ http.ts | ✅ 完成 |
| **故事节点查询** | ✅ GET /storyNode/all/{novelId} | ✅ RagAssistantView.vue (部分) | ✅ 完成 |

### ⚠️ 后端已实现 + 前端未完全使用

| 功能模块 | 后端状态 | 前端状态 | 说明 |
|---------|---------|---------|------|
| **小说更新** | ✅ POST /novel/update/{id}<br>(完整实现) | ⚠️ API已定义但未在UI中使用 | 需要在前端添加编辑界面 |

### ❌ 后端未实现 + 前端有需求

| 功能模块 | 后端状态 | 前端需求 | 需要实现的接口 |
|---------|---------|---------|------------------|
| **文件上传** | ❌ FileController为空 | ❌ 前端需要封面上传 | - POST /upload/novel-cover |
| **用户配置获取** | ❌ UserConfigController为空 | ⚠️ SettingsView.vue需要 | - GET /userConfig/get |
| **用户配置更新** | ❌ UserConfigController为空 | ⚠️ SettingsView.vue需要 | - POST /userConfig/update |
| **故事节点创建** | ❌ StoryNodeController缺少 | ⚠️ 编辑器需要 | - POST /storyNode/create |
| **故事节点更新** | ❌ StoryNodeController缺少 | ⚠️ 编辑器需要 | - POST /storyNode/update/{id} |
| **故事节点删除** | ❌ StoryNodeController缺少 | ⚠️ 编辑器需要 | - POST /storyNode/delete/{id} |
| **时间线列表** | ❌ TimelineController为空 | ⚠️ SettingsView.vue配置项 | - GET /timeline/list/{novelId} |
| **时间线创建** | ❌ TimelineController为空 | ⚠️ 编辑器需要 | - POST /timeline/create |
| **时间线更新** | ❌ TimelineController为空 | ⚠️ 编辑器需要 | - POST /timeline/update/{id} |
| **时间线删除** | ❌ TimelineController为空 | ⚠️ 编辑器需要 | - POST /timeline/delete/{id} |
| **小说关系管理** | ❌ NovelRelationController为空 | ❌ 前端未实现 | - 完整的CRUD接口 |

### 📊 完成度统计

#### 后端接口完成度
- ✅ 完全实现：**14个接口**
  - 认证：2个
  - 小说：4个
  - 角色：6个
  - RAG：2个
  - 故事节点：1个（查询）
  
- ⚠️ 部分实现：**0个接口**

- ❌ 未实现：**10个接口**
  - 文件上传：1个
  - 用户配置：2个
  - 故事节点：3个（CRUD）
  - 时间线：4个（CRUD）
  - 小说关系：待统计

- **后端总体完成度：约 58%** (14/24)

#### 前后端对接情况
- ✅ 完全对接：**11个功能** (前后端都完成且已连接)
- ⚠️ 部分对接：**2个功能** (后端完成但前端未充分使用)
- ❌ 未对接：**10个功能** (前端有需求但后端缺失)

- **对接匹配度：约 69%** (11/16)

### 🎯 下一步开发优先级

#### 高优先级（立即实现）

1. **文件上传功能** 🔴
   - **影响**: 小说封面无法上传
   - **需要实现**:
     ```java
     @PostMapping("/upload/novel-cover")
     public Result<Map<String, String>> uploadCover(@RequestParam("file") MultipartFile file)
     ```
   - **工作量**: 小（1-2天）

2. **故事节点 CRUD** 🔴
   - **影响**: 核心创作功能不完整
   - **需要实现**:
     ```java
     @PostMapping("/create")
     public Result<StoryNode> create(@RequestBody StoryNode node)
     
     @PostMapping("/update/{id}")
     public Result<StoryNode> update(@PathVariable Long id, @RequestBody StoryNode node)
     
     @PostMapping("/delete/{id}")
     public Result<String> delete(@PathVariable Long id)
     ```
   - **工作量**: 中（3-5天）

3. **时间线管理** 🔴
   - **影响**: 无法管理故事时间线
   - **需要实现**: 完整的 TimelineController
   - **工作量**: 中（3-5天）

#### 中优先级（近期实现）

4. **用户配置管理** 🟡
   - **影响**: 个性化设置无法保存
   - **需要实现**: UserConfigController 的 get/update 接口
   - **工作量**: 小（2-3天）

5. **小说关系管理** 🟡
   - **影响**: 无法建立小说间的关联
   - **需要实现**: NovelRelationController
   - **工作量**: 中（3-4天）

#### 低优先级（后续优化）

6. **RAG 功能优化** 🟢
   - 改进向量检索算法
   - 增加更多上下文类型支持
   - 优化 AI 响应质量

7. **性能优化** 🟢
   - 添加 Redis 缓存
   - 优化数据库查询
   - 实现分页优化

### 💡 开发建议

#### 1. 统一异常处理
建议添加全局异常处理器：
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(Exception.class)
    public Result<String> handleException(Exception e) {
        log.error("系统异常", e);
        return Result.error("服务器内部错误: " + e.getMessage());
    }
    
    @ExceptionHandler(RuntimeException.class)
    public Result<String> handleRuntimeException(RuntimeException e) {
        return Result.error(e.getMessage());
    }
}
```

#### 2. 接口版本管理
建议为 API 添加版本控制：
```
/api/v1/novel/listall
/api/v2/novel/listall
```

#### 3. 参数验证
使用 @Valid 注解进行参数验证：
```java
@PostMapping("/create")
public Result<NovelVO> create(@Valid @RequestBody Novels novel) {
    // ...
}
```

#### 4. 缓存优化
对频繁访问的数据添加 Redis 缓存：
```java
@Cacheable(value = "novels", key = "#userId + ':' + #page")
public Page<NovelVO> getUserNovelList(Long userId, int page, int pageSize) {
    // ...
}
```

#### 5. 日志记录
在关键操作添加详细日志：
```java
log.info("用户 {} 创建了小说: {}", userId, novel.getTitle());
log.warn("删除小说失败: novelId={}, userId={}", novelId, userId);
```

---
*文档版本: v1.0*
*最后更新: 2026-05-31*