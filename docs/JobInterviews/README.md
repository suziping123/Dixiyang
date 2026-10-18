# 前端面试知识索引（JobInterviews）

> **用途**：全栈面试弹药库，分两大区——
> ① **Practical**：本项目实战档案（真实踩坑 + 取证过程 + 修复代码）；
> ② **五领域面试常问**：每个领域拆两篇——`01 项目已用`（问题 + 项目真实代码 + 定位）和 `02 通用高频`（项目未直接涉及但面试必考，配可背代码）。
>
> **用法**：面试前挑岗位相关的 2-3 篇过一遍；答题三段式 = **原理 → 本项目真实案例（带代码/定位）→ 边界与取舍**。

## 一、Practical · 项目实战档案（8 类）

> 每条 = 说明 + 真实代码引用（标注来源文件）+ 分析 + 面试话术 + 文档佐证。

| # | 分类 | 一句话概括 |
|---|------|-----------|
| 01 | [工程化与代码质量](./Practical/01-工程化与代码质量.md) | TS 严格类型清零、构建双闸、lint 基线、文档驱动、Git hooks |
| 02 | [Vue3 架构与状态管理](./Practical/02-Vue3架构与状态管理.md) | Pinia 乐观更新、轮询改状态直连、API 封装、Local First |
| 03 | [CSS 视觉与主题系统](./Practical/03-CSS视觉与主题系统.md) | 层叠上下文、backdrop-filter 三层修复、design token |
| 04 | [响应式与移动端适配](./Practical/04-响应式与移动端适配.md) | 断点、悬浮球精算避让、横滑防溢出、CDP 真机验证 |
| 05 | [前后端协作与接口层](./Practical/05-前后端协作与接口层.md) | axios 拦截器 6 层、unwrap 口径坑、`__file__` 存储协议 |
| 06 | [交互体验与表单](./Practical/06-交互体验与表单.md) | 回车提交数焦点、拖拽三信号状态机、完成态勾选改版 |
| 07 | [性能与稳定性](./Practical/07-性能与稳定性.md) | 短列优先瀑布流、游标分页、启动自愈补列、清理降级 |
| 08 | [排错方法论](./Practical/08-排错方法论.md) | CDP 探针取证、DB↔磁盘对账、四大坑速查表 |

## 二、五领域面试常问

| 领域 | 01 · 项目已用（真实代码 + 定位） | 02 · 通用高频（未涉及，配代码） |
|------|--------------------------------|-------------------------------|
| 前端 | [Frontend/01](./Frontend/01-面试常问·项目已用.md) | [Frontend/02](./Frontend/02-面试常问·通用高频.md) |
| Java 后端 | [JavaBackend/01](./JavaBackend/01-面试常问·项目已用.md) | [JavaBackend/02](./JavaBackend/02-面试常问·通用高频.md) |
| Python 后端 | [PythonBackend/01](./PythonBackend/01-面试常问·项目已用.md) | [PythonBackend/02](./PythonBackend/02-面试常问·通用高频.md) |
| 运维 | [Operations/01](./Operations/01-面试常问·项目已用.md) | [Operations/02](./Operations/02-面试常问·通用高频.md) |
| 实施 | [Implementation/01](./Implementation/01-面试常问·项目已用.md) | [Implementation/02](./Implementation/02-面试常问·通用高频.md) |

## 必读前置（方法论源头）

- [根 AGENTS.md](../../AGENTS.md) —— 前端四大必读（层叠/蒙板/unwrap/移动适配）+ 工作准则
- [dixiyang-vue/AGENTS.md](../../dixiyang-vue/AGENTS.md) —— 技术栈、http 拦截器、主题系统
- [dixiyang-engine/AGENTS.md](../../dixiyang-engine/AGENTS.md) —— Spring Boot 分层、安全规范、接口约定

## 面试使用建议

1. **讲坑必讲根因与取证**：不说"改好了"，说"CDP dump `getComputedStyle` 定位到全局 `blur(10px)`"——过程比结论值钱。
2. **讲性能必带数字**：P95 1844ms→368ms（5×）、吞吐 +71%、命中 99.99%（[Redis优化效果对比](../Redis优化效果对比.md)）。
3. **讲工程必讲机制**：type-check 清零是治理思路；双后端共存期的双 401 处理是现实约束下的取舍。
4. **总包装**：[求职项目介绍](../求职项目介绍.md) / [系统总览](../系统总览.md)。

---
*返回 [docs 总索引](../README.md)*
