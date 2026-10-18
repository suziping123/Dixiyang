# 前端 type-check 存量错误清零（2026-10-12）

## 需求

`npm run build`（= `type-check` + `build-only`）因 9 个存量类型错误永远失败，被迫长期用 `build-only` 绕过。绕过路径常态化后，**以后新增的真类型错误也会被静默放行到产物里**。目标：清零这 9 个错误，让 `npm run build` 恢复绿灯、摘掉"免检"标签。

## 定性（先核实再动手）

9 处全部是**类型层告警、非真 bug**，且与同期便签改动无关（报错 4 文件与便签 3 文件零重叠，报错文件最后改动在 v1.40 前）：

| 文件（处数） | 根因 | 运行时保护 |
|---|---|---|
| `localImages.ts`（1） | tsconfig 开 `noUncheckedIndexedAccess`，`presetModules[path]` 标 `\| undefined` | key 来自 `Object.keys`，必存在 |
| `storyMappings.ts`（2） | 同上：`GENDER_COLORS.male/female` 字面量 key 被标 `\| undefined` | key 硬编码存在 |
| `RagAssistantView.vue`（2） | `readonly()` 包装的 DeepReadonly 数组赋给 mutable prop | readonly 是 TS 层概念，运行时无影响 |
| `TimelineView.vue`（4） | `timelines.value[0].id` 标 `\| undefined` | 上一行已有 `length` 判断 |

## 方案与改动文件

1. **`src/utils/localImages.ts`** — `thumb: presetModules[path] ?? ''`（`??` 收敛类型，兜底分支实际不可达）。
2. **`src/utils/storyMappings.ts`** — `GENDER_COLORS` 去掉 `Record<string,...>` 标注改为字面量推断：键是 `male/female` 字面量而非动态查表，字面量类型让索引访问不再带 `|undefined`（动态查表场景才需要 `Record` + `noUncheckedIndexedAccess` 下的 `??` 兜底）。
3. **`src/components/chat/ChatMessage.vue`** — `Props` 中 `references/streamingReferences/versions/paired` 数组字段改 `readonly T[]`：父组件 `messages`/`currentReferences` 经 `readonly()` 包装（DeepReadonly → `readonly T[]`），组件内部对这些数组**只读不写**（仅 `v-for`/`.length`/取值），放宽方向安全。`barList`/`displayList` 两个 computed 注解同步改 `readonly string[]`。
4. **`src/views/TimelineView.vue`（393、410 行）** — `timelines.value[0]?.id ?? null`：`?.` 应对索引 undefined、`?? null` 收敛为 `number | null`（与原三元/`if(length)` 语义等价）。

> 说明：`RagAssistantView.vue` 的 2 处错误**未直接改该文件**——根因在 `ChatMessage` 的 prop 类型过窄，放宽 prop 后其错误随之消除。

## 验证方式

- `npm run type-check` → **0 错误**（原 9 错）。
- `npm run build` → **EXIT=0**（type-check + vite build 双绿，11.8s）。
- ESLint：4 个改动文件中 `TimelineView` 有 8 个报错，经与 HEAD 基线对比**同为 8 个**（仅行号 +1 偏移），确认零引入；`localImages/storyMappings/ChatMessage` 0 错。

## 文档同步

- 根 `README.md`：「打包注意（存量错误→用 build-only）」改为「type-check 0 错误，`npm run build` 直接可用」；删除 FAQ「npm run build 报一堆 TS 类型错误」条目。

## 已知问题

- `TimelineView.vue` 另有 8 个**ESLint** 存量错误（`updateTimeline` 未使用 + 7 处 `@typescript-eslint/no-explicit-any`），属代码风格层面，不影响 build，本轮未处理。
- `npm run build` 仍提示 `index-*.js` chunk 超 500kB（9.4MB 单包），为全量 import 现状，需路由级 code-splitting 单独立项。

---

*文档版本: v1.0 — 2026-10-12 创建*
