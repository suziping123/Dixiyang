#!/usr/bin/env python3
"""
迁移脚本：将 novel_character.extra 从 MySQL 迁移到文件系统
执行方式：cd DixyangFast && .venv/bin/python scripts/migrate_character_extra.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dixiyang.services.storage_service import save_json, CHARACTER_DIR, STORAGE_ROOT
from dixiyang.config import DATABASE_URL

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session


def migrate():
    engine = create_engine(DATABASE_URL)

    with Session(engine) as db:
        # 查询所有有 extra 数据的角色
        result = db.execute(
            text("SELECT id, extra FROM novel_character WHERE extra IS NOT NULL AND extra != '' AND extra != '{}'")
        )
        rows = result.fetchall()

        if not rows:
            print("没有需要迁移的 extra 数据")
            return

        print(f"找到 {len(rows)} 条需要迁移的 extra 数据")
        print(f"存储目录: {STORAGE_ROOT}/{CHARACTER_DIR}/")
        print()

        migrated = 0
        skipped = 0
        errors = 0

        for row in rows:
            char_id = row[0]
            extra_raw = row[1]

            try:
                # 解析 extra
                if isinstance(extra_raw, dict):
                    extra_data = extra_raw
                elif isinstance(extra_raw, str):
                    extra_data = json.loads(extra_raw)
                else:
                    print(f"  跳过 #{char_id}: 未知类型 {type(extra_raw)}")
                    skipped += 1
                    continue

                # 如果是空对象，跳过
                if not extra_data:
                    print(f"  跳过 #{char_id}: 空对象")
                    skipped += 1
                    continue

                # 保存到文件，获取路径引用
                db_value = save_json(CHARACTER_DIR, char_id, extra_data)

                # 更新 DB
                db.execute(
                    text("UPDATE novel_character SET extra = :val WHERE id = :id"),
                    {"val": db_value, "id": char_id}
                )
                db.commit()

                print(f"  ✓ #{char_id}: {json.dumps(extra_data, ensure_ascii=False)[:60]}...")
                migrated += 1

            except Exception as e:
                print(f"  ✗ #{char_id}: 错误 - {e}")
                errors += 1

        print()
        print(f"迁移完成: 成功 {migrated}, 跳过 {skipped}, 失败 {errors}")


if __name__ == "__main__":
    migrate()
