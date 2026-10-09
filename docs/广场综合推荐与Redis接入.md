# 广场改名 + 综合推荐 + Redis P0/P1 接入

## 需求
1. 「点子库」更名为「广场」。
2. 新增「综合推荐」排序，为广场默认排序。
3. Redis：频控 TTL 化、热门 ZSET 榜、浏览去重+增量回写（降级回原路径）。

## 方案
- **改名**：`IdeaLibraryView` 标题、`FloatingNav` 菜单项、路由 title 统一「广场」；tab/分区/「写点子」保留。
- **综合推荐**（v1.50 升级）：前端 `sorts` 首位加 `recommend`，默认值改 `recommend`；后端 `_recommend_rows`：候选池=最新200+14天内帖子，打分 = Redis ZSET 热度(`hot_top_scores`)×时间衰减(48h) + 点/藏标签兴趣加成(近似 ItemCF，藏3/赞2，单项封顶6×1.5)；与 最新(纯时间)/热门(纯ZSET) 拉开区分度。
- **Redis 接入**（`services/idea_cache.py` + `idea_service.py`）：
  - 频控：`_limit_check/_limit_mark` Redis 优先（SET EX），down 时内存 dict 降级；
  - 热门：点赞3/收藏2/评论2/浏览1 增量 `ZINCRBY`，10min 后台重建（tmp+RENAME 原子）；
  - 浏览：`SETNX 600s` 去重 + `idea:vcnt:{pid}` INCRBY，60s 后台 Lua GET+DEL 回写 DB；详情响应叠加未回写增量；
  - 降级：3s 冷却快速失败，全回原路径；计数列权威仍在 DB。
- 连接串经环境变量 `REDIS_URL` 注入（本机密码 123321 不入库）；redis-py 强制 `protocol=2`（老版 Windows Redis 无 RESP3）。

## 改动文件
- `dixiyang-vue/.../views/IdeaLibraryView.vue`、`components/FloatingNav.vue`、`router/index.ts`、`api/ideaApi.ts`
- `DixyangFast/.../services/idea_cache.py`（新）、`services/idea_service.py`、`main.py`（lifespan 挂后台任务）
- `vite.config.ts`（host:true + adb auto-reverse）、`.vscode/launch.json`、`docs/局域网访问与launch调试.md`

## 已知问题
- 旧版 Windows Redis 不支持 RESP3/HELLO，redis-py 必须 `protocol=2`。
- 同一用户 600s 内重复浏览不再涨浏览数（新预期行为，旧测试用例已改断言）。
- JMeter 压测与效果对比文档待做。

## 验证
- `sort=recommend` 接口 200 返回正常列表。
- Redis up/down 双态回归见后续对比文档。
