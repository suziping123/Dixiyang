# Redis 优化效果对比（JMeter 压测）

## 需求
量化 Redis 接入（频控 TTL / 热门 ZSET / 浏览去重+增量回写）对广场读接口的性能收益，产出可见对比。

## 压测方案
- 工具：JMeter 5.6.3 CLI（`idea_bench.jmx`，Temp 目录，不入库）
- 负载：20 线程 × 100 轮 × 3 接口 = 每态 6000 请求，思考时间 200ms，0 错误
- 目标接口：
  - `GET /api/idea/posts?sort=recommend`（综合推荐：ZSET 热度×时间衰减+标签加成）
  - `GET /api/idea/posts?sort=hot`（热门：ZSET 排序）
  - `GET /api/idea/posts/{id}`（详情：浏览去重+Redis 增量）
- 双态：**UP** = Redis 6379 运行；**DOWN** = kill redis-server，后端走内存降级路径（3s 冷却快速失败回源 DB）

## 结果（Windows 本机，SQLite，2026-10-10）

| 接口 | 指标 | Redis UP | Redis DOWN | 提升 |
|------|------|----------|------------|------|
| 推荐 recommend | 均值 | **129.5ms** | 305.9ms | 2.4× |
| 推荐 recommend | P95 | **204ms** | 1649ms | 8.1× |
| 推荐 recommend | P99 | **245ms** | 1684ms | 6.9× |
| 热门 hot | 均值 | **134.1ms** | 297.4ms | 2.2× |
| 热门 hot | P95 | **207ms** | 1649ms | 8.0× |
| 热门 hot | P99 | **253ms** | 1687ms | 6.7× |
| 详情 view | 均值 | **113.0ms** | 265.8ms | 2.4× |
| 详情 view | P95 | **192ms** | 1626ms | 8.5× |
| 详情 view | P99 | **227ms** | 1665ms | 7.3× |
| 吞吐（三接口合计） | req/s | **57.5** | 38.7 | 1.49× |

## 结论
1. **P95/P99 是最大收益点**（8×/7×）：DOWN 态每次请求都要回源 DB（频控 dict 无 TTL 语义、热门走 `hot_score` 全表排序、浏览每次同步 commit），并发下写锁排队导致长尾飙到 1.6s+；UP 态这些写全部进 Redis（ZSET INCRBY / SETNX / 原子 Lua），DB 只在 60s 周期批量回写。
2. **均值提升 2.2-2.4×**：热点读路径短路。
3. **吞吐 +49%**：同硬件同数据量。
4. **降级铁律成立**：Redis 挂掉后 0 错误、业务全部可用（仅性能回退），3s 冷却防止雪崩。
5. **附加收益（非压测项）**：频控 TTL 跨重启不丢、多实例共享；浏览 600s 去重减少无效计数写。

## 已知问题
- 本机 SQLite + Windows 有放大效应（写锁竞争比 MySQL/PG 更激烈），生产库收益比例会不同，但方向一致。
- JMX 里 `${threads}` 直接写变量不解析，需用 `${__P(threads,20)}`（JMeter 属性函数）。

## 验证方式
```powershell
# UP 态
D:\Redis\redis-server.exe D:\Redis\redis.windows.conf   # 或桌面 start_redis.bat
D:\apache-jmeter-5.6.3\bin\jmeter.bat -n -t idea_bench.jmx -l up.jtl
# DOWN 态：kill redis-server 后
D:\apache-jmeter-5.6.3\bin\jmeter.bat -n -t idea_bench.jmx -l down.jtl
```
