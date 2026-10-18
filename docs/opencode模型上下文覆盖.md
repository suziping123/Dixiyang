# opencode 免费模型上下文覆盖（DeepSeek V4.1 Flash Free → 1M）

> 版本：v1.0 ｜ 日期：2026-10-16 ｜ 用途：把本地 opencode 客户端对 `opencode/deepseek-v4.1-flash-free` 的上下文上限从 **200K 提到 1M**，与付费/Go 版 `deepseek-v4.1-flash` 对齐

## 1. 需求

用户要求：免费模型 **DeepSeek V4.1 Flash Free** 的上下文窗口「弄成 Go 一样」= **1M（1,000,000 tokens）**。

## 2. 现状（改前实测）

| 模型 | catalog `limit`（context / output） |
|---|---|
| `opencode/deepseek-v4.1-flash`（付费 / Go） | **1,000,000** / 384,000 |
| `opencode/deepseek-v4.1-flash-free`（免费） | **200,000** / 32,000 |

- 来源：models.dev 目录（`https://models.dev/api.json` → `opencode.models`）
- 本地服务实测：`opencode api get /api/model`（opencode **v2.0.26**，服务 `http://127.0.0.1:49374`）

## 3. 方案

在**全局配置** `~/.config/opencode/opencode.json` 顶层新增 **V2 原生 `providers`** 覆盖块（不动文件里旧的 V1 `provider` 块，二者可共存）：

```jsonc
"providers": {
  "opencode": {
    "models": {
      "deepseek-v4.1-flash-free": {
        "limit": {
          "context": 1000000,
          "output": 32000
        }
      }
    }
  }
}
```

要点：

1. **键名**：V2 原生用 `providers`（复数）；旧的 V1 `provider`（单数）仍兼容，两键可同时在顶层共存（V2 迁移指南明确允许，同值冲突时原生 V2 优先）。
2. **`limit` 是整体替换、不是深合并**（深合并只针对 `settings` / `body`），所以 `output` 必须一起写；此处**保留免费档真实输出上限 32000，只抬上下文**（`context` 抬到 1M 后，可用输入预算 ≈ 968K）。
3. **无需重启**：改完执行 `POST /api/location/reload`（或等配置自动重载），当前会话的后续请求即按新上限计算。
4. 影响面只有 **opencode 客户端的上下文预算与自动压缩（compaction）触发点**——不再在 ~200K 附近自动压缩，可跑到 1M。

## 4. 改动文件

| 文件 | 说明 |
|---|---|
| `C:\Users\Lenovo\.config\opencode\opencode.json` | 全局 opencode 配置（**不在本仓库内**），新增顶层 `providers.opencode.models."deepseek-v4.1-flash-free".limit` |
| `~/.config/opencode/opencode.json.bak.20261016-142755` | 改前自动备份（同目录） |

> 本任务不涉及仓库代码，`dixiyang-vue/`、`dixiyang-engine/` 等均未改动。

## 5. 验证方式（已执行）

```powershell
opencode api post /api/location/reload
opencode api get /api/model        # 找 deepseek-v4.1-flash-free.limit
```

结果：

```json
{ "id": "deepseek-v4.1-flash-free", "limit": { "context": 1000000, "output": 32000 } }
```

✅ 改前 200000/32000 → 改后 **1000000/32000**，生效。

## 6. 已知问题 / 风险

1. **本地上限 ≠ 服务端上限**：本次只改客户端记账。若免费档（`https://opencode.ai/inference/v1`）网关仍按 200K 截断，超出后请求会**直接报错**（而不是像以前那样优雅自动压缩）。
2. **服务端上限未能探针验证**：免费端点对非 opencode 客户端一律 `403 FreeTierError`（"free tier can only be used from within OpenCode"，要求 opencode 自身的 UA / 会话头），所以无法用脚本低成本试探真实窗口。可在实际长会话中出现报错后再回滚。
3. **连带影响**：`opencode` 提供方的其他免费模型未改动；付费 `deepseek-v4.1-flash` 未改动。

## 7. 回滚

1. 删除配置里的整个顶层 `"providers"` 块（保留旧 `provider` 块），或
2. 恢复备份：`Copy-Item ~/.config/opencode/opencode.json.bak.20261016-142755 ~/.config/opencode/opencode.json -Force`，
3. 然后 `opencode api post /api/location/reload` 并复查 `/api/model` 应回到 `200000/32000`。
