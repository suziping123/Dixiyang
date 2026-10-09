# 局域网/USB 设备访问与 launch 调试

## 1. 需求

通过**网线**接入的 Linux 设备、**USB 共享网络（tethering）**连接的安卓手机，能直接访问本机开发服务（前端 5173 / 后端 8084），并在 Trae/VS Code 中一键启动、断点调试。

## 2. 方案

四件套配合：

| 层 | 改动 | 作用 |
|----|------|------|
| Vite 配置 | `vite.config.ts` → `server.host: true` | 监听 `0.0.0.0` 所有网卡——**根因修复**，`npm run dev` 与 launch 启动均生效 |
| 调试启动 | 新建 `.vscode/launch.json` | 「前端 Vite」「后端 FastAPI」「全栈」三个启动项，Trae/VS Code 通用 |
| USB 自动隧道 | `vite.config.ts` → `autoAdbReverse()` 插件 | dev 启动即自动 `adb reverse tcp:5173/8084`，手机免手动 |
| 防火墙 | 手动放行 5173/8084（管理员） | 仅 IP 访问需要；adb reverse 走 USB 不经过防火墙 |

后端 `main.py` 本就 `uvicorn.run(host="0.0.0.0", port=8084)`，无需改动；前端 `/api` 代理指向 `localhost:8084` 在**本机回环执行**，手机请求走 Vite 转发，无跨域问题。

### launch.json 三个启动项

1. **前端 Vite (局域网)**：`npm run dev`（cwd 指向前端目录），`serverReadyAction` 自动开浏览器
2. **后端 FastAPI (局域网)**：debugpy + `.venv/Scripts/python.exe`，`PYTHONPATH=src`
3. **全栈 (前后端局域网)**：compound 一键全启，`stopAll: true`

### autoAdbReverse 插件（USB 手机免手动）

- dev server 启动时自动执行 `adb reverse tcp:5173 tcp:5173` 与 `tcp:8084`
- adb 路径按候选列表 `existsSync` 查找（platform-tools / Android SDK / Vivo pcsuite），找不到或手机未插则**静默跳过不阻塞**
- 成功时打 `➜  adb reverse tcp:5173 ✓`；插件对 `npm run dev` 与 Trae F5 两个入口都生效
- 注意：Vite 进程需重启才重建隧道；手机浏览器访问 `http://localhost:5173`

## 3. 踩坑：launch 里追加 `--host` 导致页面全黑

**症状**：从 launch 启动后 `> vite 0.0.0.0`、`Network: use --host to expose`、打开页面全黑。

**根因**：launch.json 曾写 `runtimeArgs: ["run","dev"] + args: ["--host","0.0.0.0"]`——npm 会**吞掉 `--host`**，只把 `0.0.0.0` 传给 vite，被当成 **root 目录参数** → Vite 去 `0.0.0.0/` 找配置找不到 → `vite.config.ts` 整个不加载 → `@` 别名、`/api` 代理、`host:true` 全失效 → 页面全黑。

**修法**：launch 里**不传任何 args**，host 由 `vite.config.ts` 全局负责。

## 4. 改动文件

- `dixiyang-vue/Dixiyang-vue3/vite.config.ts`：`server.host: true` + `autoAdbReverse()` 插件
- `.vscode/launch.json`：**新建**（三启动项）
- 根 `AGENTS.md`：新增准则 11「禁止死等，命令必设最长时间」
- 根 `docs/README.md`：登记本篇

## 5. 使用方式

### Trae/VS Code 一键启动
运行和调试面板 → 选「全栈 (前后端局域网)」→ F5。

### 手机访问（USB，推荐）
启动 dev 后隧道已自动建好，手机浏览器直接打开：
```
http://localhost:5173
```

### 设备访问地址（IP 方式，需防火墙放行）
- 安卓手机/网线 Linux：`http://10.24.142.24:5173`（有线网卡 IP）
- 查看启动日志中 `Network:` 行即可拿到当前可用地址

### 防火墙放行（管理员 PowerShell，需用户自行确认执行）
```powershell
New-NetFirewallRule -DisplayName "Dixiyang-Vite-5173" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
New-NetFirewallRule -DisplayName "Dixiyang-FastAPI-8084" -Direction Inbound -Protocol TCP -LocalPort 8084 -Action Allow
```

## 6. 已知问题

1. **debugpy 警告** `Expected: ...attach_amd64.dll to exist`：debugpy 附加 reload 子进程时的提示，**无害**，服务正常启动。
2. **暴露面**：`host: true` 使服务对所有网络接口可见，仅限开发机使用。
3. 防火墙放行未代执行（需管理员权限）；adb reverse 方式不依赖防火墙。

## 7. 验证方式（2026-10-09 实测）

```text
# 1. netstat 确认全网卡监听
netstat -ano | findstr :5173      → 0.0.0.0:5173 LISTENING

# 2. 启动日志出现自动隧道行
➜  adb reverse tcp:5173 ✓
➜  adb reverse tcp:8084 ✓
adb reverse --list → UsbFfs tcp:5173 tcp:5173 / UsbFfs tcp:8084 tcp:8084

# 3. /api 代理正常（JSON=config 已加载，HTML=坏实例黑屏）
curl http://127.0.0.1:5173/api/  → {"detail":"Not Found"}（转发到后端）

# 4. 手机浏览器打开 http://localhost:5173 正常渲染
```

---

*文档版本: v1.1（2026-10-09 首版，同日增补 autoAdbReverse 自动隧道 + AGENTS 准则 11）*
