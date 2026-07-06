#!/usr/bin/env python3
"""
迁移脚本：将 user_config 中的 JSON 字段迁移到文件系统
执行方式：cd DixyangFast && .venv/bin/python scripts/migrate_user_config.py
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from dixiyang.config import DATABASE_URL, CHAT_STORAGE_PATH
from dixiyang.services.storage_service import save_json, USER_DIR, STORAGE_ROOT


def migrate():
    engine = create_engine(DATABASE_URL)

    # 确保存储目录存在
    os.makedirs(os.path.join(STORAGE_ROOT, USER_DIR), exist_ok=True)

    with Session(engine) as db:
        # 1. 迁移 custom_bgs
        print("=== 迁移 user_config.custom_bgs ===")
        result = db.execute(
            text("SELECT id, user_id, custom_bgs FROM user_config WHERE custom_bgs IS NOT NULL AND custom_bgs != '' AND custom_bgs != 'null'")
        )
        rows = result.fetchall()
        migrated = 0
        for row in rows:
            config_id, user_id, custom_bgs = row
            if custom_bgs and '__file__:' in str(custom_bgs):
                print(f"  跳过 user_id={user_id}: 已是文件引用")
                continue
            try:
                data = json.loads(custom_bgs) if isinstance(custom_bgs, str) else custom_bgs
                if not data:
                    continue
                ref = save_json(f"{USER_DIR}/customBgs", user_id, data)
                db.execute(
                    text("UPDATE user_config SET custom_bgs = :val WHERE id = :id"),
                    {"val": ref, "id": config_id}
                )
                db.commit()
                print(f"  ✓ user_id={user_id}: 迁移成功")
                migrated += 1
            except Exception as e:
                print(f"  ✗ user_id={user_id}: {e}")
        print(f"  共迁移 {migrated} 条 custom_bgs\n")

        # 2. 迁移 font_colors_json
        print("=== 迁移 user_config.font_colors_json ===")
        result = db.execute(
            text("SELECT id, user_id, font_colors_json FROM user_config WHERE font_colors_json IS NOT NULL AND font_colors_json != '' AND font_colors_json != 'null'")
        )
        rows = result.fetchall()
        migrated = 0
        for row in rows:
            config_id, user_id, font_colors = row
            if font_colors and '__file__:' in str(font_colors):
                print(f"  跳过 user_id={user_id}: 已是文件引用")
                continue
            try:
                data = json.loads(font_colors) if isinstance(font_colors, str) else font_colors
                if not data:
                    continue
                ref = save_json(f"{USER_DIR}/fontColors", user_id, data)
                db.execute(
                    text("UPDATE user_config SET font_colors_json = :val WHERE id = :id"),
                    {"val": ref, "id": config_id}
                )
                db.commit()
                print(f"  ✓ user_id={user_id}: 迁移成功")
                migrated += 1
            except Exception as e:
                print(f"  ✗ user_id={user_id}: {e}")
        print(f"  共迁移 {migrated} 条 font_colors_json\n")

        # 3. 验证
        print("=== 验证迁移结果 ===")
        result = db.execute(text("SELECT id, user_id, custom_bgs, font_colors_json FROM user_config"))
        for row in result.fetchall():
            config_id, user_id, cb, fc = row
            cb_status = "文件" if cb and '__file__:' in str(cb) else "空" if not cb else "JSON"
            fc_status = "文件" if fc and '__file__:' in str(fc) else "空" if not fc else "JSON"
            print(f"  user_id={user_id}: custom_bgs=[{cb_status}] font_colors=[{fc_status}]")


if __name__ == "__main__":
    migrate()
