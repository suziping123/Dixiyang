#!/bin/bash
BASE="http://localhost:8084"
PASS=0
FAIL=0
TOKEN=""

assert() {
  local desc="$1" expected="$2" actual="$3"
  if echo "$actual" | grep -q "$expected"; then
    echo "  ✅ $desc"
    ((PASS++))
  else
    echo "  ❌ $desc"
    echo "     expected contains '$expected', got: ${actual:0:150}"
    ((FAIL++))
  fi
}

echo "===== 1. Auth ====="
echo "--- POST /api/auth/register ---"
R=$(curl -s -X POST "$BASE/api/auth/register" -H 'Content-Type: application/json' \
  -d '{"username":"testapi2","password":"test123","nickname":"测试员"}')
assert "注册" '"code":200' "$R"

echo "--- POST /api/auth/login (admin) ---"
R=$(curl -s -X POST "$BASE/api/auth/login" -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"123456"}')
assert "登录" '"code":200' "$R"
TOKEN=$(echo "$R" | sed 's/.*"token":"\([^"]*\)".*/\1/')

echo ""
echo "===== 2. Novel ====="
echo "--- GET /api/novel/listall ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/novel/listall?page=1&page_size=10")
assert "列表" '"code":200' "$R"

echo "--- POST /api/novel/create ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novel/create" \
  -d '{"title":"测试小说","description":"这是测试","coverUrl":""}')
assert "创建" '"code":200' "$R"
NOVEL_ID=$(echo "$R" | sed 's/.*"id":\([0-9]*\).*/\1/')
echo "   NOVEL_ID=$NOVEL_ID"

echo "--- GET /api/novel/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/novel/$NOVEL_ID")
assert "详情" '"code":200' "$R"

echo "--- POST /api/novel/update/$NOVEL_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novel/update/$NOVEL_ID" \
  -d '{"title":"测试小说(已修改)"}')
assert "更新" '"code":200' "$R"

echo ""
echo "===== 3. Character ====="
echo "--- POST /api/novelCharacter/create ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novelCharacter/create" \
  -d "{\"novelId\":$NOVEL_ID,\"name\":\"测试角色\",\"personality\":\"开朗\",\"appearance\":\"高大\"}")
assert "创建" '"code":200' "$R"
CHAR_ID=$(echo "$R" | sed 's/.*"characterId":\([0-9]*\).*/\1/')
echo "   CHAR_ID=$CHAR_ID"

echo "--- GET /api/novelCharacter/$CHAR_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/novelCharacter/$CHAR_ID")
assert "详情" '"code":200' "$R"

echo "--- GET /api/novelCharacter/list/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/novelCharacter/list/$NOVEL_ID?page=1&page_size=10")
assert "分页列表" '"code":200' "$R"

echo "--- GET /api/novelCharacter/all/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/novelCharacter/all/$NOVEL_ID")
assert "全部" '"code":200' "$R"

echo "--- POST /api/novelCharacter/update/$CHAR_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novelCharacter/update/$CHAR_ID" \
  -d '{"name":"测试角色(已修改)"}')
assert "更新" '"code":200' "$R"

echo "--- POST /api/novelCharacter/extractSettings ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novelCharacter/extractSettings" \
  -d '{"conversation":"角色说: 我要变强。系统说: 你准备好了吗？"}')
assert "提取设定" '"code":200' "$R"

echo "--- POST /api/novelCharacter/saveSettings ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/novelCharacter/saveSettings" \
  -d "{\"characterId\":$CHAR_ID,\"settings\":{\"test\":\"value\"}}")
assert "保存设定" '"code":200' "$R"

echo ""
echo "===== 4. StoryNode ====="
echo "--- POST /api/storyNode/create ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/storyNode/create" \
  -d "{\"novelId\":$NOVEL_ID,\"title\":\"测试节点\",\"content\":\"这是节点内容\"}")
assert "创建" '"code":200' "$R"
NODE_ID=$(echo "$R" | sed 's/.*"nodeId":\([0-9]*\).*/\1/')
echo "   NODE_ID=$NODE_ID"

echo "--- GET /api/storyNode/$NODE_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/storyNode/$NODE_ID")
assert "详情" '"code":200' "$R"

echo "--- GET /api/storyNode/all/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/storyNode/all/$NOVEL_ID")
assert "全部" '"code":200' "$R"

echo "--- GET /api/storyNode/list/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/storyNode/list/$NOVEL_ID?page=1&page_size=10")
assert "分页列表" '"code":200' "$R"

echo "--- POST /api/storyNode/update/$NODE_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/storyNode/update/$NODE_ID" \
  -d '{"title":"测试节点(已修改)"}')
assert "更新" '"code":200' "$R"

echo ""
echo "===== 5. Timeline ====="
echo "--- POST /api/timeline/create ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/timeline/create" \
  -d "{\"novelId\":$NOVEL_ID,\"name\":\"第一章\",\"description\":\"故事开始\"}")
assert "创建" '"code":200' "$R"
TIMELINE_ID=$(echo "$R" | sed 's/.*"timelineId":\([0-9]*\).*/\1/')
echo "   TIMELINE_ID=$TIMELINE_ID"

echo "--- GET /api/timeline/$TIMELINE_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/timeline/$TIMELINE_ID")
assert "详情" '"code":200' "$R"

echo "--- GET /api/timeline/all/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/timeline/all/$NOVEL_ID")
assert "全部" '"code":200' "$R"

echo "--- GET /api/timeline/list/$NOVEL_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/timeline/list/$NOVEL_ID?page=1&page_size=10")
assert "分页列表" '"code":200' "$R"

echo "--- POST /api/timeline/update/$TIMELINE_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/timeline/update/$TIMELINE_ID" \
  -d '{"name":"第一章(已修改)"}')
assert "更新" '"code":200' "$R"

echo "--- GET /api/storyNode/timeline/$TIMELINE_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/storyNode/timeline/$TIMELINE_ID")
assert "按时间线获取节点" '"code":200' "$R"

echo ""
echo "===== 6. File ====="
echo "--- DELETE /api/upload/novel-cover (skip file upload) ---"
R=$(curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/api/upload/novel-cover?url=/test.png&novelId=$NOVEL_ID")
assert "删除封面(不存在应正常)" '"code"' "$R"

echo "--- DELETE /api/upload/background (skip file upload) ---"
R=$(curl -s -X DELETE -H "Authorization: Bearer $TOKEN" "$BASE/api/upload/background?url=/test.png&userId=1")
assert "删除背景(不存在应正常)" '"code"' "$R"

echo ""
echo "===== 7. User ====="
echo "--- GET /api/user/info ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/user/info")
assert "信息" '"code":200' "$R"

echo "--- POST /api/user/update ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/user/update" \
  -d '{"nickname":"管理员(已修改)"}')
assert "更新" '"code":200' "$R"

echo "--- GET /api/user/bg-config ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/user/bg-config")
assert "背景配置" '"code":200' "$R"

echo "--- POST /api/user/bg-config ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/user/bg-config" \
  -d '{"backgroundId":"default"}')
assert "更新背景配置" '"code":200' "$R"

echo ""
echo "===== 8. Chat (stream) ====="
echo "--- POST /api/chat/stream ---"
R=$(curl -s -N -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/chat/stream" \
  -d "{\"message\":\"你好\",\"novel_id\":$NOVEL_ID}" --max-time 10 2>&1)
assert "流式" '"type"' "$R"
SESSION_ID=$(echo "$R" | grep -o '"sessionId":"[^"]*"' | head -1 | sed 's/"sessionId":"//;s/"//')
echo "   SESSION_ID=$SESSION_ID"

echo "--- POST /api/chat/regenerate (use session above) ---"
R=$(curl -s -N -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/chat/regenerate" \
  -d "{\"message\":\"你好\",\"novel_id\":$NOVEL_ID,\"session_id\":\"$SESSION_ID\"}" --max-time 10 2>&1)
assert "重新生成" '"type"' "$R"

echo ""
echo "===== 9. UserConfig ====="
echo "--- GET /api/userConfig/background?userId=1 ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/userConfig/background?userId=1")
assert "背景" '"code":200' "$R"

echo "--- POST /api/userConfig/background ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/userConfig/background" \
  -d '{"userId":1,"backgroundId":"default"}')
assert "更新背景" '"code":200' "$R"

echo "--- GET /api/userConfig/fontColors?userId=1 ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/userConfig/fontColors?userId=1")
assert "字体颜色" '"code":200' "$R"

echo "--- POST /api/userConfig/fontColors ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/userConfig/fontColors" \
  -d '{"userId":1,"colors":{"primary":"#fff","secondary":"#000"}}')
assert "更新字体颜色" '"code":200' "$R"

echo ""
echo "===== 10. ChatHistory ====="
echo "--- GET /api/chatHistory/sessions ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/chatHistory/sessions")
assert "会话列表" '"code":200' "$R"

echo "--- POST /api/chatHistory/createSession ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/chatHistory/createSession" \
  -d "{\"novelId\":$NOVEL_ID,\"title\":\"测试会话\"}")
assert "创建会话" '"code":200' "$R"
SESSION_ID=$(echo "$R" | sed 's/.*"sessionId":"\([^"]*\)".*/\1/')
echo "   SESSION_ID=$SESSION_ID"

echo "--- GET /api/chatHistory/session/$SESSION_ID ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/chatHistory/session/$SESSION_ID")
assert "会话详情" '"code":200' "$R"

echo "--- PUT /api/chatHistory/message/$SESSION_ID ---"
R=$(curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/chatHistory/message/$SESSION_ID" \
  -d '{"messageIndex":0,"role":"user","content":"编辑后的消息"}')
assert "编辑消息" '"code":200' "$R"

echo "--- POST /api/chatHistory/batchSave ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/chatHistory/batchSave" \
  -d "{\"sessionId\":\"$SESSION_ID\",\"novelId\":$NOVEL_ID,\"messages\":[{\"role\":\"user\",\"content\":\"test\"}]}")
assert "批量保存" '"code":200' "$R"

echo "--- POST /api/chatHistory/generate-title/$SESSION_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" "$BASE/api/chatHistory/generate-title/$SESSION_ID")
assert "生成标题" '"code":200' "$R"

echo ""
echo "===== 11. RAG ====="
echo "--- GET /api/rag/stats ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/rag/stats")
assert "统计" '"code":200' "$R"

echo "--- GET /api/rag/count ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/rag/count")
assert "计数" '"code":200' "$R"

echo "--- GET /api/rag/documents ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE/api/rag/documents?page=1&page_size=10")
assert "文档列表" '"code":200' "$R"

echo "--- POST /api/rag/search?query=测试&topK=3 ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/rag/search?query=%E6%B5%8B%E8%AF%95&topK=3")
assert "搜索" '"code":200' "$R"

echo "--- POST /api/rag/search?source_filter=book ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/rag/search?query=%E6%B5%8B%E8%AF%95&topK=3&source_filter=book")
assert "搜索(来源筛选)" '"code":200' "$R"

echo "--- GET /api/rag/documents?source=book ---"
R=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/rag/documents?page=1&page_size=5&source=book")
assert "文档列表(来源筛选)" '"code":200' "$R"

echo "--- POST /api/rag/embed ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  "$BASE/api/rag/embed" \
  -d '{"text":"你好世界"}')
assert "嵌入" '"code":200' "$R"

echo ""
echo "===== 清理 ====="
echo "--- DELETE /api/novel/delete/$NOVEL_ID ---"
R=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" "$BASE/api/novel/delete/$NOVEL_ID")
assert "删除小说" '"code":200' "$R"

echo ""
echo "=========================================="
echo "  DONE: ✅ $PASS 通过, ❌ $FAIL 失败"
echo "=========================================="
