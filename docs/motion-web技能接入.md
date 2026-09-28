# motion-web 技能接入（opencode / Trae）

> 最后更新: 2026-09-27

## 需求

让本机的 AI Agent 工具（opencode、Trae 国内版）能发现并加载 `motion-web-main/` 这个动效网页 Agent Skill。dsh 已卸载（确认无残留）、Codex CLI 未安装，均不配置。

## 背景事实

- `motion-web-main/` 是标准 Agent Skill：`SKILL.md`（frontmatter `name: motion-web`）+ `references/` + `cases/` + `scripts/`
- 文件夹名 `motion-web-main` 与 skill 名 `motion-web` 不一致，多数工具要求两者一致 → **入口统一命名为 `motion-web`（软链）**
- Trae 为国内版：`/usr/bin/trae → /usr/share/trae-cn/trae-cn`，配置根 `~/.trae-cn/`
- opencode 会自动扫描外部技能目录 `~/.agents/skills/`

## 方案

以 `motion-web-main/` 为唯一数据源，各工具入口全部用软链（单一来源，改动即时全局生效）：

```
数据源: /home/lijiajia/项目/Dixiyang/motion-web-main

软链入口（4 处）:
~/.agents/skills/motion-web   → motion-web-main   # opencode 自动扫描（零配置生效）
~/.trae-cn/skills/motion-web  → motion-web-main   # Trae 全局技能
.agents/skills/motion-web     → ../../motion-web-main   # 项目级（Agent Skills 开放标准）
.trae/skills/motion-web       → ../../motion-web-main   # Trae 项目技能官方路径

兜底: 根 AGENTS.md 追加「motion-web 技能」索引节（读 AGENTS.md 的工具均可见）
```

## 改动文件

| 文件 | 说明 |
|------|------|
| `~/.agents/skills/motion-web` | 新建软链（全局） |
| `~/.trae-cn/skills/motion-web` | 新建软链（全局） |
| `.agents/skills/motion-web` | 新建软链（项目） |
| `.trae/skills/motion-web` | 新建软链（项目） |
| `AGENTS.md` | 末尾追加 motion-web 技能索引（约 4 行） |
| `docs/motion-web技能接入.md` | 本文档 |
| `docs/README.md` | 登记索引 + 版本记录 |

未改动：`motion-web-main/` 内任何文件；opencode 全局配置 `~/.config/opencode/opencode.jsonc`。

## 使用方式

- **opencode**：重启后技能列表出现 `motion-web`；触发词见其 `SKILL.md` description（做网页/落地页/官网/作品集/动效/复刻/手感调优等）
- **Trae**：设置中心 →「技能」面板应显示全局技能 `motion-web`；对话中匹配描述自动按需加载
- 也可手动：对任意工具说「读 ~/.agents/skills/motion-web/SKILL.md 并按其 Build Order 执行」

## 已知问题

1. **Trae 对软链的解析未实测**：若 Trae 技能面板不显示，备选方案：将 `.trae/skills/motion-web` 改为真实目录复制（失去同步，需配同步脚本）
2. **Codex CLI 未安装**（`which codex` 找不到）：`.agents/skills` 为开放标准，以后装上 Codex 即自动生效，本次按要求跳过
3. **dsh 已卸载**：确认 `~/.dsh`、`~/.config/dsh`、npm 全局均无残留，不配置
4. `motion-web-main/` 在 git 中为未跟踪状态（`??`），软链入口同样未跟踪——本机个人使用，不入库

## 验证方式

```bash
# 1. 软链指向核对
ls -l ~/.agents/skills/ ~/.trae-cn/skills/ .agents/skills/ .trae/skills/
head -3 .agents/skills/motion-web/SKILL.md   # 应输出 name: motion-web

# 2. opencode：退出重启，技能列表应出现 motion-web

# 3. Trae：设置 → 技能面板应出现 motion-web（全局或项目）
```
