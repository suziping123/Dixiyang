# 存储架构迁移指南

## 概述

本文档描述了 Dixiyang 项目从「数据库存储 JSON」到「文件系统存储 + 数据库存路径」的架构迁移。

## 迁移背景

### 原有问题
1. `novel_character.extra` 字段使用 MySQL JSON 类型存储角色扩展设定
2. JSON 数据直接存在数据库中，不利于备份和迁移
3. 数据库体积随 JSON 数据增长而膨胀

### 迁移目标
1. 所有 JSON 数据统一存储到文件系统
2. 数据库只存储文件路径引用（`__file__:relative/path.json`）
3. 支持从本地磁盘迁移到云存储（S3、OSS 等）

## 存储架构

### 目录结构

```
/home/lijiajia/项目/Dixiyang/uploads/
├── covers/                       # 小说封面图片
│   └── {md5hash}.{ext}
├── backgrounds/                  # 自定义背景图
│   └── {md5hash}.{ext}
└── storage/                      # 统一 JSON 存储根目录
    ├── chat/                     # 聊天链文件
    │   └── {userId}/{sessionId}/
    │       ├── {timestamp}_{random}.json
    │       ├── edits.json
    │       └── summary.json
    ├── character/                # 角色设定 JSON
    │   └── {characterId}.json
    └── user/                     # 用户配置 JSON
        ├── customBgs/{userId}.json
        └── fontColors/{userId}.json
```

### 数据格式

#### 统一引用格式（`__file__:` 前缀）

所有文件引用字段统一使用 `__file__:` 前缀 + 相对路径（相对于 `STORAGE_ROOT`）：

| 字段 | 格式示例 | 说明 |
|------|---------|------|
| `extra` | `__file__:character/8.json` | 角色设定 JSON |
| `head_path` | `__file__:chat/1/abc/1719500000_1234.json` | 聊天链头文件 |
| `custom_bgs` | `__file__:user/customBgs/1.json` | 用户自定义背景图 |
| `font_colors_json` | `__file__:user/fontColors/1.json` | 用户字体颜色配置 |
| `cover_url` | `/api/uploads/covers/abc.png` | **不改**：HTTP URL，前端直接使用 |

#### 数据库存储格式

```sql
-- 文件引用（推荐）
extra = '__file__:character/10.json'

-- 旧格式（兼容）：直接存储 JSON 字符串
extra = '{"技能": "竹书纪年"}'

-- head_path 统一格式
head_path = '__file__:chat/1/abc/1719500000_1234.json'
```

#### 读取逻辑

读取文件引用时自动判断前缀：
- 以 `__file__:` 开头 → 读取对应文件
- 以 `{` 开头 → 直接解析为 JSON（兼容旧数据）
- 其他 → 返回 `None`

#### 文件存储格式
```json
{
  "势力": "魔族",
  "技能": ["竹书纪年", "时空穿梭"],
  "武器": "草薙剑",
  "弱点": ["怕水"],
  "性格特点": "冷静果断",
  "外貌特征": "银色长发",
  "背景故事": "来自魔族的王子...",
  "人际关系": {
    "卡卡西": "挚友"
  }
}
```

## 迁移步骤

### 1. 本地开发环境迁移

```bash
# 进入项目目录
cd DixyangFast

# 执行迁移脚本
.venv/bin/python scripts/migrate_character_extra.py
```

### 2. 生产环境迁移（ECS）

#### 2.1 准备文件存储目录

```bash
# 创建存储目录
sudo mkdir -p /data/dixiyang/storage/character
sudo mkdir -p /data/dixiyang/storage/chat
sudo mkdir -p /data/dixiyang/storage/rag

# 设置权限
sudo chown -R www-data:www-data /data/dixiyang/storage
sudo chmod -R 755 /data/dixiyang/storage
```

#### 2.2 配置环境变量

```bash
# .env
CHAT_STORAGE_PATH=/data/dixiyang/storage
```

#### 2.3 执行迁移

```bash
# 连接生产数据库
python scripts/migrate_character_extra.py
```

#### 2.4 验证迁移

```bash
# 检查文件是否创建
ls -la /data/dixiyang/storage/character/

# 检查数据库记录
mysql -u root -p dixiyang -e "SELECT id, extra FROM novel_character WHERE extra IS NOT NULL;"
```

### 3. 迁移到云存储（S3/OSS）

#### 3.1 安装依赖

```bash
pip install boto3  # AWS S3
# 或
pip install oss2   # 阿里云 OSS
```

#### 3.2 修改 storage_service.py

```python
# 替换文件读写为 S3 操作
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = 'your-bucket-name'

def save_json(subdir, record_id, data):
    key = f"settings/{subdir}/{record_id}.json"
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(data, ensure_ascii=False),
        ContentType='application/json'
    )
    return f"__s3__:{BUCKET_NAME}/{key}"

def load_json(subdir, record_id, db_value):
    if db_value.startswith('__s3__:'):
        parts = db_value.replace('__s3__:', '').split('/', 1)
        bucket, key = parts[0], parts[1]
        response = s3.get_object(Bucket=bucket, Key=key)
        return json.loads(response['Body'].read())
```

## API 接口

### 提取角色设定

```http
POST /api/novelCharacter/extractSettings
Content-Type: application/json

{
  "conversation": "用户：卡卡西的血继限界是什么？\nAI：写轮眼..."
}

Response:
{
  "code": 200,
  "data": {
    "settings": {
      "血继限界": "写轮眼",
      "所属": "木叶忍者村"
    }
  }
}
```

### 保存角色设定

```http
POST /api/novelCharacter/saveSettings
Content-Type: application/json

{
  "characterId": 123,
  "settings": {
    "血继限界": "写轮眼",
    "所属": "木叶忍者村"
  }
}

Response:
{
  "code": 200,
  "msg": "设定保存成功"
}
```

## 前端使用

### AI 设定助手弹窗

在 RAG 聊天页面，点击 AI 回复下方的「📋 总结为设定」按钮，会弹出设定助手弹窗：

1. **左侧**：显示对话上下文（当前消息前后各2条）
2. **右侧**：AI 自动生成的结构化 JSON 预览
3. **角色选择**：从下拉列表选择要关联的角色
4. **操作**：
   - 「保存」：将设定写入角色 extra 字段
   - 「修改」：切换到编辑模式，直接修改 JSON
   - 「打回」：关闭弹窗，不保存

### 角色管理页面

角色卡片新增「📋 有设定」标签，表示该角色有扩展设定数据。

## 回滚方案

如果需要回滚到数据库存储：

```sql
-- 将文件路径引用转回 JSON
UPDATE novel_character
SET extra = (
    SELECT JSON_EXTRACT(
        LOAD_FILE(CONCAT('/data/dixiyang/storage/', REPLACE(extra, '__file__:', ''))),
        '$'
    )
)
WHERE extra LIKE '__file__:%';
```

## 注意事项

1. **备份**：迁移前务必备份数据库和 storage 目录
2. **权限**：确保应用有 storage 目录的读写权限
3. **路径**：`CHAT_STORAGE_PATH` 环境变量必须正确配置
4. **并发**：迁移时建议暂停服务，避免数据不一致
5. **验证**：迁移后必须验证所有 API 接口正常工作

## 更新日志

### 2026-07-05 存储引用格式统一 + extra 解引用修复

**变更内容：**

1. **统一文件引用格式**：所有 DB 文件引用字段使用 `__file__:` 前缀
   - `extra`: `__file__:character/{id}.json`（已有，不变）
   - `head_path`: `__file__:chat/{userId}/{sessionId}/{file}.json`（**新增**）
   - `custom_bgs`: `__file__:user/customBgs/{userId}.json`（已有，不变）
   - `font_colors_json`: `__file__:user/fontColors/{userId}.json`（已有，不变）
   - `cover_url`: `/api/uploads/covers/{filename}.png`（**不改**，HTTP URL）

2. **修复 extra 解引用 Bug**（P0）
   - **问题**：聊天上下文中直接把 `__file__:character/8.json` 路径字符串传给 AI
   - **影响**：AI 看不到角色自定义设定内容
   - **修复**：
     - Java `ChatController.java:307` → `loadJson()` 后再传给 AI
     - Python `chat_service.py:86` → 同上

3. **统一 head_path 格式**
   - **问题**：Java 存绝对路径 `storage/chat/1/.../file.json`，Python 存相对路径 `chat/1/.../file.json`
   - **影响**：共享 DB 时两端互读失败
   - **修复**：
     - Java `ChatContentFileService.append()` 返回 `__file__:chat/...`
     - Python `chat.py` 的 hp 改为 `__file__:chat/...`
     - Java `ChatContentFileService` 新增 `resolvePath()` / `toRef()` 辅助方法

4. **saveSettings 合并模式**
   - **问题**：`saveSettings` 直接覆盖已有设定
   - **修复**：改为合并模式（`{**existing, **settings}`），保留已有字段

**修改文件：**

| 文件 | 改动 |
|------|------|
| `ChatController.java` | extra 解引用 + StorageService 依赖注入 |
| `ChatContentFileService.java` | `resolvePath()` / `toRef()` + append/readChain/deleteChain 等方法适配 |
| `chat_service.py` | extra 解引用 + import `load_json`/`CHARACTER_DIR` |
| `chat.py` | hp 改为 `__file__:chat/...` 格式（4 处） |
| `character_service.py` | `saveSettings` 合并模式 |

**测试要求：**

⚠️ **所有测试必须使用新数据（新小说、新角色、新会话），不能用旧数据验证。**

验证步骤：
1. 创建新小说 → 创建角色（带 extra）→ 验证 extra 为 `__file__:character/{id}.json`
2. `saveSettings` 追加字段 → 验证已有字段保留
3. `saveSettings` 覆盖同名字段 → 验证仅同名字段更新
4. 发送聊天消息 → 验证 `head_path` 为 `__file__:chat/...` 格式
5. 读取会话消息 → 验证能正确加载

### 2026-07-05 统一存储路径迁移

**变更内容：**

将所有 JSON 存储文件从分散目录迁移到统一根目录 `/home/lijiajia/项目/Dixiyang/uploads/storage/`。

**迁移前（分散）：**
- Python: `DixyangFast/src/storage/`（character/ chat/ user/）
- Java: `dixiyang-engine/storage/`（chat/）
- 上传文件: `/home/lijiajia/项目/Dixiyang/uploads/`（covers/ backgrounds/）

**迁移后（统一）：**
```
/home/lijiajia/项目/Dixiyang/uploads/
├── covers/          # 小说封面（不变）
├── backgrounds/     # 自定义背景图（不变）
└── storage/         # 【统一】JSON 存储根
    ├── chat/        # 聊天链文件
    ├── character/   # 角色设定
    └── user/        # 用户配置
```

**修改文件：**

| 文件 | 改动 |
|------|------|
| `config.py` | `STORAGE_DIR` 默认值改为 `uploads/storage` |
| `application.yml` | `CHAT_STORAGE_PATH` 默认值改为绝对路径 |
| `ChatContentFileService.java` | `resolvePath()` / `toRef()` 适配绝对路径（基于 parent） |
| MySQL `chat_session.head_path` | 12 条记录从旧格式迁移到 `__file__:chat/...` |

**配置对齐：**

| 后端 | 配置项 | 值 |
|------|--------|-----|
| Python | `STORAGE_DIR` | `/home/lijiajia/项目/Dixiyang/uploads/storage` |
| Python | `CHAT_STORAGE_PATH` | = `STORAGE_DIR` |
| Java | `CHAT_STORAGE_PATH` | `/home/lijiajia/项目/Dixiyang/uploads/storage/chat` |
| Java | `StorageService.getStorageRoot()` | `chatBaseDir.getParent()` = `/home/.../uploads/storage` |
