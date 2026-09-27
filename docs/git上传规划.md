# Git 上传规划与执行记录

## 需求
梳理工作区中哪些文件会被上传、哪些被忽略，并完成一次安全的 commit + push。

## 分析结论

### 会被上传
- 修改/删除：`AGENTS.md`、`dixiyang-vue/AGENTS.md`、`docs/README.md`、`chat_service.py`、前端 8 个视图/组件、`main.ts`、`router`、`http.ts`、`confirm.ts`，以及 `daily-log/` 下 2 个删除项
- 新增：`utils/auth.ts`、`utils/enterSubmit.ts`、`docs/介绍.md`、`docs/求职项目介绍.md`、`docs/登录鉴权与表单回车.md`（根目录与 vue 各一份）、`logoByGpt.png`

### 不会被上传（.gitignore 拦截，约 11GB+）
`.env`、`node_modules/`、`uploads/`、`DixyangFast/storage/`(3.3G)、`models/bge-m3`(2.2G)、`models/bge-reranker-base`(3.2G)、`.venv/`(1.9G)、`datasets/`、`dist/`、`__pycache__/`、`*.docx`、`*.mp4`、`chroma_data/`、`dixiyang-engine/`

### 发现的遗留问题
1. `DixyangFast/models/cache/`（93M，`BAAI/bge-small-zh-v1.5` 早期缓存，实际运行用 `bge-m3`）被 `.gitignore` 命中却仍被跟踪
2. `package-lock.json`/`pnpm-lock.yaml` 规则与跟踪状态矛盾
3. 2 个 `.docx` 已跟踪且命中忽略规则

## 方案与改动文件
- `.gitignore`：删除 `package-lock.json`/`yarn.lock`/`pnpm-lock.yaml` 三行，lock 文件纳入版本管理
- `git rm -r --cached DixyangFast/models/cache/`（本地文件保留）
- `git rm --cached` 遗留 docx（本地保留）
- 暂存时仅加入 `logoByGpt.png`，`logoByGM/GPT.png` 保持未跟踪

## 提交记录
- `a23b827` chore: 移出误跟踪的模型缓存与二进制文档，lock 文件纳入版本管理
- `8382a50` feat: 登录鉴权与表单回车，多视图改版并补充介绍文档
- 已推送至 `origin/main`

## 已知问题
- 92M 模型 blob 仍存于历史（`.git` 约 146M），需 `git filter-repo` + 强推才能清除，暂不做
- `logoByGpt.png` 2.0M 偏大，logo 建议 <500K，可后续压缩
- `logoByGM.png`、`logoByGPT.png` 未跟踪，建议本地删除或压缩后二选一

## 验证方式
```bash
git status --ignored --short        # 确认大文件/敏感项为忽略态
git diff --cached --stat            # 无 >5M 新文件
git log --oneline -3 && git status -sb   # main 与 origin/main 同步
```
