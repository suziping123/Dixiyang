# 02 · Web 前端与 Vue3

> **定位**：从浏览器机制到 Vue3 工程实践，覆盖"能写、能调、能审、能评测"四层能力。
> **层级**：L1-L7（核心到方案设计与追问）
> **对应岗位能力**：页面真实性判断、交互缺陷复现、前端代码审查、性能与移动端验收。


> **来源约定**：未标来源的段落为通用技术知识；标 `[项目]` 的有仓库代码/脚本/文档依据；`[项目-冲突]` 表示材料互相矛盾；`[推断]`/`[待确认]` 表示分析或尚需验证。

---

## 1. 浏览器与 Web 基础

### 1.1 一次页面访问发生了什么

```text
输入 URL
 → DNS / TCP / TLS
 → 请求 HTML
 → 解析 HTML，构建 DOM
 → 遇到 CSS/JS/图片，发起请求
 → CSSOM + DOM → Render Tree
 → Layout（布局）→ Paint（绘制）→ Composite（合成）
 → JS 执行、事件、请求、渲染循环
```

**排查视角**：

| 现象 | 先看 |
|---|---|
| 白屏 | Network 是否有 HTML/JS；Console 是否报错；`#app` 是否挂载 |
| 样式不生效 | Elements 看命中规则/优先级；Network 看 CSS 是否 404 |
| 图片不显示 | URL、CORS、缓存、路径 base、防盗链 |
| 请求 404/500 | Network 的 URL/Method/Payload/Response；代理是否生效 |
| 页面卡 | Performance 长任务、布局抖动、大量 DOM、重复请求 |

### 1.2 同源、CORS 与代理

- 同源：协议 + 域名 + 端口都相同。
- 跨域是浏览器限制；服务端要返回 `Access-Control-Allow-Origin` 等头。
- 开发期常用 Vite `server.proxy` 把 `/api` 转到后端，浏览器看到同源，避免 CORS。[项目]
- 生产期由 Nginx 反向代理承担同样角色。
- 带 Cookie 的跨域请求需要 `credentials` + 明确 Origin，不能用 `*`。

```ts
// vite.config.ts（示意）
export default defineConfig({
  server: {
    proxy: {
      "/api": { target: "http://127.0.0.1:8084", changeOrigin: true },
    },
  },
});
```

**易错**：

- 代理只影响开发服务器，生产构建不会自动带代理。
- `base` 配错会导致部署到子路径后资源 404。
- CORS 报错不等于后端没返回，可能是预检 `OPTIONS` 失败。

### 1.3 缓存与存储

| 机制 | 特点 | 适用 |
|---|---|---|
| 强缓存 `Cache-Control: max-age` | 不发请求，直接用本地 | 带 hash 的静态资源 |
| 协商缓存 `ETag/Last-Modified` | 发请求，304 复用 | HTML、频繁变更资源 |
| `localStorage` | 同步、持久、约 5MB、字符串 | 非敏感偏好、token（有 XSS 风险） |
| `sessionStorage` | 会话级 | 多页签临时状态 |
| Cookie | 自动携带、可 HttpOnly | 会话、CSRF 防护 |
| IndexedDB | 异步、大容量 | 离线数据、大量缓存 |

**安全**：token 放 `localStorage` 会被 XSS 读取；放 `HttpOnly Cookie` 可降低 XSS 窃取，但要处理 CSRF。没有绝对安全，取决于威胁模型。

---

## 2. HTML / CSS / 布局

### 2.1 盒模型与布局

```css
.box {
  box-sizing: border-box;
  width: 300px;
  padding: 16px;
  border: 1px solid #333;
}
```

- `content-box`：width 只算内容；`border-box`：包含 padding/border。
- Flex：一维布局；`flex: 1` 是 `flex-grow/shrink/basis` 简写。
- Grid：二维布局；`minmax(140px, 1fr)` 适合自适应双列。
- `position`：`relative` 作为绝对定位参照；`absolute` 脱离文档流；`fixed` 相对视口；`sticky` 滚动吸附。

### 2.2 层叠上下文（项目高频坑）

**症状**：页面配了背景图，但被内容卡片盖住/看不到。

**根因**：根容器没有 `position: relative`，背景层 `position: absolute` 相对更外层定位，层叠关系错乱。

**修法**：

```css
.page {
  position: relative;
  isolation: isolate; /* 可选：建立独立层叠上下文 */
}
.page__bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.page__content {
  position: relative;
  z-index: 1;
}
```

**判断**：`z-index` 只在同一层叠上下文内比较；父级 `opacity < 1`、`transform`、`filter`、`will-change` 都会创建新上下文。

### 2.3 `backdrop-filter` 白雾坑

**症状**：弹窗输入框/下拉聚焦时出现白雾毛玻璃，失焦消失。

**根因**：

1. 全局 `input, textarea, select { backdrop-filter: blur(10px) }`；
2. 控件半透明背景；
3. Element Plus 的 `input.el-select__input` 聚焦时命中全局规则，把下层 placeholder 模糊。

**修法（三层）**：

```css
html .el-dialog {
  background: #191c27 !important;
}
html .el-dialog input,
html .el-dialog textarea,
html .el-dialog select {
  backdrop-filter: none !important;
}
html input.el-select__input,
html .el-input-number__input {
  backdrop-filter: none !important;
}
```

**易错**：EP 浮层 teleport 到 `body`，不在 `.el-dialog` 内；选择器要用 `html .el-select__popper` / `html .el-popper`，不能用 `.el-dialog .el-option`（实际类是 `.el-select-dropdown__item`）。

### 2.4 响应式与移动端

**断点统一 768**：

```css
@media (max-width: 768px) {
  /* 移动端 */
}
```

**弹窗**：全局贴底抽屉，宽 100%，`margin: auto auto 0`，内容可滚动；新弹窗不要自设宽高，避免被全局 `!important` 压掉。[项目]

**悬浮球避让**：FAB 在右侧，右锚条约 74px（球 46 + 右缘 14 + 缓冲）。页面右侧 `padding-right: 64px`，内容右界不压球；不要盲目 88px，否则 375 视口内容被压到 273px，双列退化单列。[项目]

```css
@media (max-width: 768px) {
  .page {
    padding-right: 64px;
  }
  .card-grid {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
  }
}
```

**横向溢出防呆**：

- 筛选行/chips 组各自 `flex-wrap: wrap`，组内 `overflow-x: auto`。
- 禁止整行 `flex-shrink: 0` + `white-space: nowrap` 长组，否则 375 视口会被撑到 500+。
- `nowrap` 只用于单行标签头，不用于整行组。

**输入字号**：移动端输入至少 16px，否则 iOS Safari 聚焦时放大页面。

**验收**：CDP 设 375×812，断言 `document.documentElement.scrollWidth === 375`、卡片双列、弹窗宽 375、Tab 不溢出；最后必须截图肉眼复核。

### 2.5 回流与重绘

- 修改几何属性（宽高、位置、字体）触发 layout；修改颜色/背景触发 paint；`transform/opacity` 通常只合成。
- 批量 DOM 修改、离线 `DocumentFragment`、避免读写交替（强制同步布局）。
- 动画优先 `transform`/`opacity`；`will-change` 不要滥用。

---

## 3. JavaScript 运行时、DOM 与事件

### 3.1 事件循环（浏览器）

```text
执行同步代码（调用栈）
 → 清空微任务：Promise.then、queueMicrotask、MutationObserver
 → 取一个宏任务：setTimeout、setInterval、I/O、UI 事件
 → 清空微任务
 → 必要时渲染
 → 下一轮
```

```js
console.log("script start");
setTimeout(() => console.log("timeout"), 0);
Promise.resolve().then(() => console.log("promise"));
console.log("script end");
// script start → script end → promise → timeout
```

**结论**：微任务优先于下一个宏任务；`await` 后面的代码是微任务；`setTimeout(0)` 不是立即执行。

### 3.2 DOM 事件模型

```text
捕获阶段：window → document → ... → target
目标阶段：target
冒泡阶段：target → ... → document → window
```

```js
document.querySelector(".list").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;
  console.log(btn.dataset.action);
});
```

- 事件委托减少监听器，适合列表。
- `stopPropagation` 阻止继续传播；`preventDefault` 阻止默认行为（表单提交/链接跳转），两者不同。
- 被动监听 `{ passive: true }` 可提升滚动性能，但不能在里面 `preventDefault`。

### 3.3 表单与中文输入法（IME）

**坑**：用户用中文输入法按 Enter 选词，`keydown.enter` 也触发提交，导致"选词就发送"。

```vue
<input
  v-model="text"
  @compositionstart="composing = true"
  @compositionend="composing = false"
  @keydown.enter="onEnter"
/>
```

```ts
function onEnter(e: KeyboardEvent) {
  if (composing || e.isComposing) return;
  submit();
}
```

**要点**：`compositionstart/end` + `event.isComposing` 双保险；不要只看 `keyCode === 13`。

### 3.4 竞态与取消

**场景**：快速切换会话/小说/筛选条件，旧请求晚返回覆盖新结果。

```ts
let seq = 0;
async function load(id: string) {
  const my = ++seq;
  const data = await fetchData(id);
  if (my !== seq) return; // 旧请求丢弃
  state.value = data;
}
```

更强：`AbortController` 取消网络请求；流式请求要同时校验会话 ID。

**项目对照**：

- RAG 助手切换会话时，旧 SSE 继续推送会把内容写进新会话；需要 `AbortController` + `sessionId` 校验。[项目]
- 小说编辑器章节切换存在竞态，旧章节响应可能覆盖新章节内容。[项目]

---

## 4. Vue3 响应式原理

### 4.1 `Proxy` 与依赖收集

Vue3 用 `Proxy` 拦截对象读写：

```text
读取属性 → track：把当前 effect 加入该属性的依赖集合
修改属性 → trigger：取出依赖，重新执行 effect
```

简化实现：

```js
let activeEffect = null;
const targetMap = new WeakMap();

function track(target, key) {
  if (!activeEffect) return;
  let deps = targetMap.get(target);
  if (!deps) targetMap.set(target, (deps = new Map()));
  let set = deps.get(key);
  if (!set) deps.set(key, (set = new Set()));
  set.add(activeEffect);
}

function trigger(target, key) {
  const deps = targetMap.get(target);
  const set = deps?.get(key);
  set?.forEach((effect) => effect());
}

function reactive(obj) {
  return new Proxy(obj, {
    get(target, key, receiver) {
      track(target, key);
      const value = Reflect.get(target, key, receiver);
      return typeof value === "object" && value !== null ? reactive(value) : value;
    },
    set(target, key, value, receiver) {
      const ok = Reflect.set(target, key, value, receiver);
      trigger(target, key);
      return ok;
    },
  });
}
```

真实 Vue3 还处理：数组方法、`Map/Set`、`ref` 解包、调度器（`queueJob`）、`effect` 嵌套、`shallowReactive` 等。

### 4.2 `ref` vs `reactive`

| 项 | `ref` | `reactive` |
|---|---|---|
| 任意类型 | 是（基本类型/对象） | 仅对象/数组/Map/Set |
| 脚本访问 | `.value` | 直接属性 |
| 模板解包 | 自动解包 | 直接属性 |
| 替换整个值 | 可以 | 会丢失响应式（除非用 `Object.assign`） |
| 解构 | 解构后失去响应式（除非 `toRefs`） | 解构后失去响应式 |

```ts
const count = ref(0);
count.value++;
const state = reactive({ name: "A" });
state.name = "B";

const { name } = toRefs(state); // 保持响应式
```

**易错**：

- `reactive` 对象整体重新赋值：`state = reactive({...})` 会断开原引用。
- 把 `ref` 放进数组/对象，模板里可能不会自动解包；脚本里要 `.value`。
- `shallowRef` 只跟踪引用变化，适合大对象/第三方实例（ECharts）。

### 4.3 `computed` 与 `watch`

```ts
const list = ref<number[]>([]);
const total = computed(() => list.value.reduce((a, b) => a + b, 0));

watch(
  () => props.id,
  async (id, oldId) => {
    if (id === oldId) return;
    await load(id);
  },
  { immediate: true }
);
```

- `computed` 有缓存，依赖不变不重算；不要在 computed 里做副作用/异步。
- `watch` 适合副作用（请求、日志、存储）；`watchEffect` 自动收集依赖，但依赖不直观。
- 深度监听大对象开销大；优先监听具体字段。
- 异步 `watch` 回调仍可能竞态，需要取消/序号。

### 4.4 渲染与更新

- 模板编译成 render 函数；响应式变化触发组件更新。
- 虚拟 DOM diff 同层比较；`key` 帮助识别节点复用，列表不要用 index 作为 key（插入/删除会错位）。
- `nextTick` 在 DOM 更新后执行；需要拿更新后的尺寸/滚动位置时使用。
- `v-if` 销毁/重建；`v-show` 只切换 `display`。频繁切换用 `v-show`，条件稳定用 `v-if`。

---

## 5. Composition API、组件与生命周期

### 5.1 `setup` 与组合式函数

```vue
<script setup lang="ts">
import { ref, onMounted } from "vue";

const loading = ref(false);
const data = ref<Item[]>([]);

async function load() {
  loading.value = true;
  try {
    data.value = await api.list();
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>
```

- `<script setup>` 顶层变量/函数自动暴露给模板。
- 组合式函数（composable）以 `use` 开头，返回状态和方法；适合复用请求、表单、拖拽、轮询。
- 组合式函数内部可以使用生命周期，但必须在组件 `setup` 同步调用栈中调用。

### 5.2 Props / Emits / v-model

```vue
<script setup lang="ts">
const props = defineProps<{ modelValue: string; disabled?: boolean }>();
const emit = defineEmits<{ "update:modelValue": [value: string] }>();

function onInput(e: Event) {
  emit("update:modelValue", (e.target as HTMLInputElement).value);
}
</script>
```

- Props 单向数据流；子组件不要直接改 prop。
- `v-model` 是 `modelValue` + `update:modelValue` 的语法糖。
- 复杂表单用 `defineModel`（Vue 3.4+）或显式 emit；注意类型与默认值。

### 5.3 生命周期

| 选项式 | 组合式 | 时机 |
|---|---|---|
| `beforeCreate/created` | `setup` | 实例创建 |
| `beforeMount` | `onBeforeMount` | 挂载前 |
| `mounted` | `onMounted` | DOM 可用 |
| `beforeUpdate` | `onBeforeUpdate` | 更新前 |
| `updated` | `onUpdated` | 更新后 |
| `beforeUnmount` | `onBeforeUnmount` | 卸载前 |
| `unmounted` | `onUnmounted` | 卸载后 |

**清理**：定时器、事件监听、ResizeObserver、WebSocket/SSE、ECharts 实例都要在卸载时释放。

```ts
onMounted(() => {
  const ro = new ResizeObserver(onResize);
  ro.observe(el.value!);
  onUnmounted(() => ro.disconnect());
});
```

### 5.4 插槽与 `keep-alive`

- 默认插槽/具名插槽/作用域插槽；作用域插槽把子组件数据暴露给父级模板。
- `keep-alive` 缓存组件实例，切换不销毁；配合 `activated/deactivated` 刷新数据。
- 缓存过多会占内存；用 `include/exclude/max` 控制。
- 后台多页签常用 `keep-alive :include` 保持页面状态。[项目]

---

## 6. Vue Router 与 Pinia

### 6.1 路由模式

- `createWebHistory`：URL 干净，需要服务端 rewrite 到 `index.html`。
- `createWebHashHistory`：`#/path`，静态托管无需 rewrite；后台独立入口采用 hash。[项目]
- 懒加载：`component: () => import("./View.vue")`，按路由拆包。
- 守卫：`beforeEach` 做登录/角色校验；不要在守卫里做大量同步阻塞。

```ts
router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (to.meta.requiresAuth && !token) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }
});
```

**易错**：

- 登录后直接 `router.push("/home")`，丢失用户原本要去的页面；应读取 `redirect` 并校验是站内路径。
- 守卫只查 `localStorage.role` 是前端判断，可被篡改；后端必须再次鉴权。
- 后台与用户端共用路由/守卫会导致权限边界模糊；项目改为独立入口 + 独立 token。[项目]

### 6.2 Pinia 设计

```ts
export const useStickyStore = defineStore("sticky", () => {
  const items = ref<Sticky[]>([]);

  async function add(input: StickyInput) {
    const temp = { ...input, id: `temp-${Date.now()}` };
    items.value.unshift(temp);
    try {
      const saved = await api.create(input);
      Object.assign(temp, saved);
    } catch (e) {
      items.value = items.value.filter((x) => x.id !== temp.id);
      throw e;
    }
  }

  return { items, add };
});
```

**乐观更新**：先改 UI，失败回滚；优点是响应快，缺点是失败处理复杂。必须：

- 生成临时 ID；
- 失败时精确回滚（不要整表重拉）；
- 防重复提交；
- 给用户错误提示，不能静默。

**项目对照**：便签 Store 曾乐观更新失败后不回滚，用户以为保存成功。[项目]

### 6.3 状态设计原则

- 全局状态只放跨页面/跨组件共享的数据；局部状态留在组件。
- 服务端数据与 UI 状态分开：列表缓存、筛选条件、loading、错误。
- 派生数据用 getter/computed，不要重复存储。
- 避免把大对象/非响应式实例放进 store；用 `shallowRef`/`markRaw`。

---

## 7. TypeScript、Axios、表单与鉴权

### 7.1 Axios 封装

```ts
const http = axios.create({ baseURL: "/api", timeout: 15000 });

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status;
    if (status === 401) {
      clearSession();
      router.replace({ path: "/login", query: { redirect: router.currentRoute.value.fullPath } });
    }
    return Promise.reject(error);
  }
);
```

**关键点**：

- 401：清会话、跳登录、带 redirect；要防止多个请求同时 401 重复跳转。
- 403：无权限，不应一律登出；后台 403 与用户端 403 处理不同。[项目]
- 业务码：HTTP 200 但 `code !== 200` 时，`unwrap` 必须抛错/提示，不能返回 `data: null` 当成功。[项目]
- 超时、取消、重试：按接口配置；上传/流式请求单独处理。
- 原生 `fetch`（SSE）不经过 axios 拦截器，必须单独处理 401。[项目]

### 7.2 `unwrap` 与分页口径

```ts
type Page<T> = { records: T[]; total: number; current: number; size: number };

function unwrap<T>(res: ApiResponse<T>): T {
  if (res.code !== 200) throw new Error(res.msg);
  return res.data;
}

const page = unwrap<Page<Novel>>(await getNovelOptions());
const novels = page?.records ?? [];
```

**项目坑**：`GET /novel/listall` 返回 `{ records, total }`，但前端按数组 unwrap，导致下拉恒空。[项目]

**防呆**：

- API 层为每个接口写明确的返回类型；
- 在 `unwrap` 后立即规范化（数组/分页对象）；
- 联调时打印一次响应结构，不靠猜。

### 7.3 表单

- 校验：必填、长度、格式、范围、跨字段（确认密码/结束时间）。
- 错误展示：字段级 + 表单级；提交失败保留用户输入。
- 防重复提交：按钮 loading + 请求锁 + 后端幂等。
- 中文输入：`compositionstart/end` + `isComposing`。
- 移动端：输入字号 ≥16px；键盘类型 `inputmode`；回车行为明确。

```ts
const submitting = ref(false);
async function submit() {
  if (submitting.value) return;
  submitting.value = true;
  try {
    await api.save(form);
  } finally {
    submitting.value = false;
  }
}
```

### 7.4 登录态

- 登录成功存 token、用户信息、角色；刷新时恢复并校验。
- 退出登录清理**本应用相关键**，不要 `localStorage.clear()` 清掉其他应用/用户数据。[项目]
- 多标签页同步：`storage` 事件监听 token 变化，避免一个标签退出另一个仍显示登录。
- 单点登录顶号：后端 401 带原因，前端提示"账号已在其他设备登录"并跳登录。[项目]

---

## 8. 测试、构建与部署

### 8.1 测试层次

| 类型 | 工具 | 测什么 |
|---|---|---|
| 单元 | Vitest | 纯函数、composable、store |
| 组件 | Vitest + @vue/test-utils | props/emit/渲染/交互 |
| E2E | Playwright/Cypress | 真实浏览器全链路 |
| 类型 | `vue-tsc` | 类型契约 |
| 构建 | Vite build | 入口/资源/环境变量 |

```ts
import { describe, it, expect } from "vitest";
import { formatDate } from "./date";

describe("formatDate", () => {
  it("formats ISO date", () => {
    expect(formatDate("2026-01-02T03:04:05Z")).toBe("2026-01-02");
  });
});
```

**测试原则**：断言行为，不测实现细节；避免快照过大；时间/随机/网络要可控。

### 8.2 Vite 构建

- `build.rollupOptions.input` 支持多入口（用户端 `index.html` + 后台 `admin.html`）。[项目]
- `base` 影响资源路径；部署到 GitHub Pages 子路径要设 `--base=/Dixiyang/`。
- `VITE_*` 构建时注入；演示模式 `VITE_DEMO=1` 通过 mock 适配器，不是生产逻辑。[项目]
- 产物分析：chunk 过大时按路由/依赖拆分；不要把整个 UI 库打进首屏。

### 8.3 Nginx 与静态部署

```nginx
location / {
  try_files $uri $uri/ /index.html;
}
location /api/ {
  proxy_pass http://127.0.0.1:8084/;
  proxy_http_version 1.1;
  proxy_set_header Host $host;
  proxy_buffering off; # SSE
}
```

- History 路由需要 `try_files` 回退。
- SSE 要关闭代理缓冲、延长超时。
- 静态资源带 hash 可长缓存；`index.html` 不缓存或短缓存。

---

## 9. 性能、移动端与可观测性

### 9.1 加载性能

- 路由懒加载、组件异步加载、图片懒加载/响应式图片。
- 首屏只加载必要 chunk；第三方库按需引入。
- 预加载关键资源，避免瀑布请求。
- 压缩/缓存/CDN；开启 gzip/brotli。

### 9.2 运行时性能

- 长列表：虚拟列表/分页/游标加载；不要一次渲染上万 DOM。
- 瀑布流：短列优先插入，避免 CSS columns 的阅读顺序/重排问题。[项目]
- 高频事件：防抖/节流；滚动监听用 `passive`；避免布局抖动。
- 重计算：`computed` 缓存、Web Worker、后端计算。
- 图表：实例复用、`dispose`、按需 resize。

### 9.3 无限滚动与游标

```ts
let cursor: string | null = null;
let loading = false;

async function loadMore() {
  if (loading || cursor === null) return;
  loading = true;
  try {
    const page = await api.feed({ cursor, size: 20 });
    list.value.push(...page.items);
    cursor = page.nextCursor;
  } finally {
    loading = false;
  }
}
```

**易错**：

- 用 `page` 递增但后端按 `offset` 分页，数据插入后重复/漏项。
- 在 `finally` 里递归调用，失败也继续，形成无限请求。[项目]
- 没有"没有更多"状态，触底后反复请求。
- 并发触发（滚动事件密集）没有 loading 锁。

### 9.4 移动端验收

```text
1. CDP 设 375×812，mobile=true
2. 断言 scrollWidth === 375（无横向溢出）
3. 断言卡片双列（瀑布流按 left 分档，不按 top）
4. 断言弹窗宽 375、控件单列
5. 断言 tab-bar.scrollWidth <= clientWidth
6. 截图肉眼复核：列数、截断、空白带、悬浮球遮挡
```

**只跑数字断言不够**：单列大卡可能"没有溢出"但明显没适配。

### 9.5 可观测性

- Console：未捕获异常、Vue warn、网络错误。
- Network：请求 URL/状态/耗时/响应体；SSE 看 EventStream。
- Performance：LCP、CLS、长任务、主线程火焰图。
- 错误上报：Sentry 类服务，带 release、路由、用户 ID（脱敏）、breadcrumb。
- 埋点：关键转化/失败率；不要采集敏感信息。

---

## 10. 项目案例与审查清单

### 10.1 项目真实问题

| 问题 | 位置 | 根因 | 修复方向 |
|---|---|---|---|
| 聊天串会话 | `useChatStream.ts` / RAG 视图 | 旧流未取消/未校验 sessionId | Abort + 序号/会话校验 |
| 中文选词误发送 | 聊天输入框 | 只监听 Enter | composition + `isComposing` |
| 下拉恒空 | 小说选项接口 | 分页对象当数组 | `records` unwrap |
| 业务 500 当成功 | `RagKnowledgeView` | 只看 HTTP 200 | `unwrap` 校验业务码 |
| 时间线逐字显示 | `TimelineView` | JSON 字符串直接渲染 | `JSON.parse` + 容错 |
| 章节串台 | `NovelEditorView` | 切换竞态 | 请求序号/取消 |
| 灵感流无限请求 | `IdeaLibraryView` | `finally` 递归 | 成功才继续 + 锁 |
| 便签假保存 | `stickyStore` | 乐观更新失败不回滚 | 回滚 + 提示 |
| 删除小说假成功 | `HomeView` | 未检查业务 code | unwrap + 刷新 |
| 后台 403 误登出 | `admin/api/http.ts` | 403 当 401 | 区分处理 |
| 退出清空全部存储 | `UserStore` | `localStorage.clear()` | 只删本应用键 |
| 登录后丢 redirect | 路由/登录页 | 固定跳首页 | 读取并校验 redirect |
| 背景被盖 | 页面根容器 | 缺 `position: relative` | 建立层叠上下文 |
| 下拉白雾 | 全局 `backdrop-filter` | 聚焦输入命中规则 | 三层覆盖 |
| 375 单列 | 移动端网格 | `minmax(150px)` 放不下 | `minmax(140px)` + 避让精算 |

### 10.2 页面真实性审查（评测岗核心）

看到一个页面，按下面顺序判断"是不是真的"：

1. **数据来源**：Network 有没有真实请求？响应是真实数据还是固定 JSON？
2. **状态变化**：提交后是否发请求？失败是否提示/回滚？刷新后是否保留？
3. **权限**：换普通账号/未登录是否仍能操作？后端是否真的校验？
4. **边界**：空数据、超长文本、特殊字符、0 条/1 条/很多条。
5. **交互**：loading/禁用/重复点击/取消/断网。
6. **一致性**：列表与详情、前端显示与 DB、接口字段与类型。
7. **证据**：HAR、Console、DOM、DB、日志能否互相对上。

**假实现常见信号**：

- 所有请求都返回同一份数据；
- 只改前端数组，刷新即丢；
- 删除/保存没有网络请求；
- 错误被 `catch {}` 吞掉；
- 时间/ID/统计是硬编码；
- 只在 demo 模式可用，生产路径未接。

### 10.3 前端代码审查清单

- [ ] 请求是否有 loading/错误/空态？
- [ ] 是否检查业务码，不只看 HTTP 200？
- [ ] 异步回调是否校验当前会话/路由/组件仍有效？
- [ ] 事件/定时器/观察者/图表是否清理？
- [ ] 列表 key 是否稳定？
- [ ] 表单是否防重复提交？中文输入是否处理？
- [ ] 权限是否前端隐藏 + 后端校验？
- [ ] 敏感信息是否进 localStorage/日志/URL？
- [ ] 移动端 375 是否无横向溢出、双列、弹窗贴底？
- [ ] 背景层/弹窗/下拉是否有层叠与毛玻璃问题？
- [ ] 构建是否 type-check + build 双通过？

---

## 11. 高频错误与追问

### 11.1 错误表

| 错误 | 后果 | 正确做法 |
|---|---|---|
| 用 index 作 key | 列表错位/状态串 | 稳定唯一 ID |
| `watch` 里不发请求取消 | 竞态覆盖 | 序号/Abort |
| `computed` 里发请求 | 重复请求/难追踪 | 用 watch/显式调用 |
| 直接改 props | 数据流混乱 | emit |
| `reactive` 整体替换 | 失去响应式 | `Object.assign`/`ref` |
| 卸载不清理 | 内存泄漏/报错 | `onUnmounted` |
| 403 当 401 | 误登出 | 区分状态码 |
| 只判断 HTTP 200 | 业务失败当成功 | 校验 code |
| 移动端只做缩放 | 点击/滚动体验差 | 响应式布局 + 真机验收 |
| 只跑构建不看产物 | base/代理/环境变量错 | preview + 真机 |

### 11.2 追问

1. **Vue3 为什么用 Proxy？** 能拦截新增/删除/数组索引/Map/Set，比 `Object.defineProperty` 更完整；代价是兼容性和性能细节。
2. **`ref` 和 `reactive` 怎么选？** 基本类型/需要整体替换用 `ref`；固定对象结构用 `reactive`；不确定时 `ref` 更稳。
3. **`computed` 和 `watch` 区别？** computed 派生值、有缓存、无副作用；watch 监听变化做副作用。
4. **`v-if` 和 `v-show` 区别？** 销毁重建 vs display 切换；频繁切换用 v-show。
5. **`keep-alive` 什么时候用？** 需要保留表单/滚动/页签状态；注意内存和 `activated` 刷新。
6. **SSE 和 WebSocket 区别？** SSE 单向服务器推送、HTTP 友好、自动重连；WebSocket 双向、协议升级。
7. **如何防止重复提交？** 前端 loading/锁 + 后端幂等键/唯一约束。
8. **如何做前端权限？** 路由/按钮隐藏只是体验，后端必须校验；前端不可信。
9. **Vite 为什么快？** 开发期基于 ESM 按需编译，不打包全量；生产仍用 Rollup。
10. **如何定位白屏？** Network 看入口/JS、Console 看异常、Elements 看挂载点、Source 断点、构建 base。

---

## 12. 自检

- [ ] 能解释从 URL 到渲染的完整流程。
- [ ] 能画出浏览器事件循环并预测输出顺序。
- [ ] 能解释 Vue3 依赖收集/触发更新。
- [ ] 能写出带竞态保护的请求/流式逻辑。
- [ ] 能解释 401/403、业务码、unwrap 的处理差异。
- [ ] 能写出可用的 Pinia 乐观更新与回滚。
- [ ] 能配置 Vite 代理、base、多入口，并解释生产差异。
- [ ] 能在 375 视口完成移动端验收并截图复核。
- [ ] 能识别 mock/假交互/静默失败。
- [ ] 能给出 3 个前端真实缺陷的取证与修复方案。

---

*上一卷：[软件工程与编程基础](./01-软件工程与编程基础.md) ｜ 下一卷：[Python 与 FastAPI 后端](./03-Python与FastAPI后端.md)*
