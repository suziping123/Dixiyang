# 实训日志

| 学校：成都工业学院 | 专业：数据科学与大数据技术 | 学号：2309021137 |
|------------------|------------------------|----------------|
| 日期：2026年6月29日 | 星期：星期一 | 姓名：李晓妤 |

## 内容

### 一、课程主要内容

今天的实训围绕**基于FastAPI的AI聊天服务全栈开发**展开。我从零开始搭建了一个完整的前后端项目，后端使用FastAPI提供AI聊天接口，前端使用Vue.js + Element Plus构建交互式聊天界面，核心是将DeepSeek大模型封装为Web服务，并实现流式输出功能。

整个开发过程中，我遇到了很多实际问题，比如模块导入路径、跨域请求、前端Vue模板解析失败等，通过不断排查和调试，最终完成了所有功能。

#### （1）Python环境配置与包管理

我使用了**uv**作为包管理器，这是一个比pip更快的现代Python包管理工具。项目根目录在`/home/lijiajia/项目/Dixiyang/DixyangFast`，所有依赖都通过`uv sync`管理，不需要手动激活虚拟环境。

在配置Python解释器时，确保使用项目目录下的`.venv`环境，避免系统Python版本冲突。FastAPI要求Python >= 3.10，我使用的是Python 3.11，完全满足要求。

#### （2）FastAPI后端开发

我采用了**模块化架构**来组织代码，将配置、模型、路由分别放在不同文件中：

**配置管理** (`app/config.py`)：创建了`Settings`类，集中管理所有配置项，包括API密钥、模型名称、服务端口、静态文件目录等。通过`os.getenv()`读取环境变量，支持灵活配置。关键代码：

```python
class Settings:
    DS_API_KEY: Optional[str] = os.getenv("DS_API_KEY")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "deepseek-v4-flash")
    BASE_URL: str = os.getenv("BASE_URL", "https://api.deepseek.com")
    STATIC_DIR: Path = BASE_DIR / "static"
```

**模型加载** (`app/core/model.py`)：使用**单例模式**确保模型只初始化一次，避免每次请求都重新创建模型实例。关键代码：

```python
_model_instance = None

def load_model() -> ChatOpenAI:
    global _model_instance
    if _model_instance is None:
        _model_instance = ChatOpenAI(
            api_key=settings.DS_API_KEY,
            base_url=settings.BASE_URL,
            model=settings.MODEL_NAME
        )
    return _model_instance
```

**路由设计** (`app/routes/chat.py`)：定义了四个接口：
- `/chat` - 普通聊天接口，接收`question`查询参数
- `/chat/stream` - 流式聊天接口，返回SSE格式响应
- `/hello/{name}` - 测试接口，演示路径参数
- `/search` - 搜索接口，演示可选查询参数

**主程序** (`app/main.py`)：配置了CORS中间件解决跨域问题，挂载静态文件服务，并设置了根路径返回聊天页面。特别注意了路由注册顺序——API路由必须放在静态文件路由前面，否则会被静态文件服务拦截。

#### （3）前端页面开发与调试

前端使用**Vue 3** + **Element Plus**构建聊天界面，全部静态资源放在`static/`目录下，包括Vue库、Axios、marked和DOMPurify。

页面功能包括：
- 消息列表动态渲染（区分用户、AI、系统消息）
- 输入框双向绑定，支持回车键发送
- 加载状态显示（思考中动画）
- 流式输出开关
- Markdown安全渲染（使用marked+DOMPurify）

在开发过程中遇到了很多前端问题：
- Vue模板语法未解析——检查后发现是Vue库未正确加载，后来重新下载了vue.global.js
- 前端请求接口失败——发现API路由被静态文件服务拦截，调整了路由注册顺序
- 环境变量未生效——修改系统环境变量后需要重启终端才能生效

#### （4）CSS页面美化

我自己设计了聊天界面的样式，包括：
- **毛玻璃效果**：`backdrop-filter: blur(20px)`实现背景模糊，使界面更有层次感
- **渐变背景**：从浅蓝到浅紫的柔和渐变，视觉效果舒适
- **消息气泡**：用户消息右对齐（紫色渐变），AI消息左对齐（白色边框），系统消息居中
- **动画效果**：消息淡入上滑动画、思考中的动态点点点、按钮悬停效果
- **响应式设计**：适配移动端屏幕，自定义紫色滚动条

### 二、本次实验代码 / 作业

#### 核心代码结构

```
daily-log/
├── app/
│   ├── main.py          # FastAPI入口，配置CORS和静态文件
│   ├── config.py        # 配置类，管理环境变量和路径
│   ├── core/
│   │   └── model.py     # 单例模型加载
│   └── routes/
│       └── chat.py      # API路由定义
└── static/
    └── index.html       # Vue聊天界面
```

#### 关键代码

**模型加载单例模式**：

```python
_model_instance = None

def load_model() -> ChatOpenAI:
    global _model_instance
    if _model_instance is None:
        _model_instance = ChatOpenAI(
            api_key=settings.DS_API_KEY,
            base_url=settings.BASE_URL,
            model=settings.MODEL_NAME
        )
    return _model_instance
```

**流式输出实现**：

```python
@router.get("/chat/stream")
def chat_stream(question: str = Query(...)):
    def stream_chat():
        model = load_model()
        for chunk in model.stream(question):
            yield f"data: {chunk.content}\n\n"
    return StreamingResponse(stream_chat(), media_type="text/event-stream")
```

**前端流式接收**：

```javascript
fetch('/chat/stream?question=' + encodeURIComponent(text))
    .then(res => {
        const reader = res.body.getReader();
        let content = '';
        function read() {
            reader.read().then(result => {
                if (result.done) return;
                content += decoder.decode(result.value);
                updateMessage(content);
                read();
            });
        }
        read();
    });
```

### 三、实验收获

#### 模块化架构设计

学会了如何将项目按功能模块划分，配置、模型、路由分离，使代码结构清晰，易于维护。特别是`Settings`类的设计，让所有配置集中管理，支持环境变量覆盖，非常灵活。

#### 单例模式应用

理解了单例模式在模型加载中的重要性——避免每次请求都重新初始化模型，显著提升性能。通过全局变量`_model_instance`实现懒加载，只有第一次调用时才创建实例。

#### 路由注册顺序

发现了FastAPI路由匹配的优先级问题——先注册的路由先匹配。因此API路由必须放在静态文件路由前面，否则动态路由会被静态文件服务拦截。

#### 前端调试技巧

掌握了使用浏览器开发者工具排查问题：
- **Network面板**：查看请求状态、参数、响应
- **Console面板**：查看JavaScript错误和日志
- **Elements面板**：检查DOM结构和样式

#### 环境变量管理

学会了通过`os.getenv()`读取环境变量，并理解了系统环境变量、终端环境变量、虚拟环境变量三者的区别——修改系统变量后需要重启软件才能生效。

### 四、实验感悟

今天的实训让我对**全栈开发**有了更深的理解。从后端API设计到前端界面实现，每个环节都需要细心处理。

**最让我印象深刻的是模块导入问题**。由于项目结构嵌套较深，`app/main.py`需要导入`app.routes.chat`，但Python解释器默认只搜索当前目录。我尝试了多种方法，最终通过在`config.py`中动态添加`sys.path`解决了问题。这个过程让我意识到，在Python项目中，路径管理是一个常见但容易忽略的问题。

**另一个重要的体会是前后端联调的复杂性**。前端页面写好了，但后端接口没响应；接口响应了，但前端解析失败。每个环节都可能出错，需要耐心排查。特别是跨域问题，一开始我以为是代码问题，后来发现是CORS中间件配置的问题。

**关于前端框架的选择**，我一开始尝试了很多种方式，最后选择了纯Vue 3 + Element Plus的方案。虽然过程中遇到了Vue未加载的问题，但通过调试最终解决了。这让我明白，选择合适的技术栈很重要，但更重要的是理解每种技术的原理。

**最后，项目部署的过程也让我学到了很多**。从环境配置到服务启动，每一步都需要细心。特别是环境变量的设置，一开始我直接在代码中写死密钥，后来改为通过环境变量读取，这样更安全也更灵活。

### 五、课程 / 实验建议

1. **后端日志优化**：建议使用`logging`模块替代`print`，便于控制日志级别和生产环境排查。

2. **前端工程化**：当前前端是单文件HTML，后续可以学习Vue CLI或Vite，实现组件化开发和打包构建。

3. **数据库集成**：如果需要保存聊天记录，可以集成SQLite或其他数据库。

4. **用户认证**：可以添加用户登录功能，实现多用户聊天记录隔离。

5. **模型切换**：当前只支持DeepSeek，可以扩展支持其他模型（如OpenAI、通义千问），通过配置动态切换。
