// 演示 mock —— 小说域（卷/章节/正文/AI 补全/角色/时间线/故事节点/RAG 知识库）
// 字段命名刻意保持与真实后端一致：Novel/Volume/Chapter 为 snake_case，Character/Timeline/StoryNode 为 camelCase

export const DEMO_VOLUMES = [
  { id: 1, novel_id: 101, title: '第一卷 · 灰雾之下', sort_order: 1, description: '从冬眠舱醒来的最初三十天' },
  { id: 2, novel_id: 101, title: '第二卷 · 余火燎原', sort_order: 2, description: '地表远征与营地攻防' },
]

export const DEMO_CHAPTERS = [
  { id: 11, novel_id: 101, volume_id: 1, title: '第一章 冬眠舱', sort_order: 1, content_path: 'demo', content_hash: 'h1', content_size: 2400, version: 3, local_version: 3, word_count: 2400 },
  { id: 12, novel_id: 101, volume_id: 1, title: '第二章 灰白色的城', sort_order: 2, content_path: 'demo', content_hash: 'h2', content_size: 2100, version: 1, local_version: 1, word_count: 2100 },
  { id: 13, novel_id: 101, volume_id: 1, title: '第三章 第一缕信号', sort_order: 3, content_path: 'demo', content_hash: 'h3', content_size: 1900, version: 1, local_version: 1, word_count: 1900 },
  { id: 21, novel_id: 101, volume_id: 2, title: '第四章 远征队', sort_order: 4, content_path: 'demo', content_hash: 'h4', content_size: 2300, version: 2, local_version: 2, word_count: 2300 },
  { id: 22, novel_id: 101, volume_id: 2, title: '第五章 火光里的旧世界', sort_order: 5, content_path: 'demo', content_hash: 'h5', content_size: 1800, version: 1, local_version: 1, word_count: 1800 },
]

export const DEMO_CHAPTER_CONTENT = {
  chapterId: 11,
  title: '第一章 冬眠舱',
  version: 3,
  contentHash: 'h1',
  wordCount: 2400,
  updatedAt: '2026-10-12 21:30:00',
  content:
    '他是被冷气呛醒的。\n\n' +
    '冬眠舱的玻璃盖弹开的一瞬间，灰白色的雾顺着缝隙涌进来，带着一股铁锈和腐叶混在一起的味道。江末躺在舱里，盯着头顶那盏忽明忽暗的应急灯，花了整整三十秒才想起自己是谁。\n\n' +
    '"低温休眠第七百一十二天，"机械音说，"欢迎回到地表，编号 0712。"\n\n' +
    '他撑着舱沿坐起来，膝盖撞上什么东西——那是一具倒在舱边的骸骨，工装口袋里还插着半支笔。江末认得那支笔，那是出发前陈站长塞给他的，说等到了新世界，留着写家书。\n\n' +
    '窗外，旧城市的天际线在灰雾里只剩一排高低不平的剪影。没有灯，没有人，只有风穿过高楼时发出的、像叹息一样的声音。\n\n' +
    '江末把笔收进怀里，跨过骸骨，推开了避难所的大门。',
}

export const DEMO_AI_COMPLETION = {
  text: '他摸了摸口袋，那支笔还在——笔帽上有一道浅浅的刻痕，是陈站长当年亲手刻下的编号。',
  model: 'deepseek-chat',
  requestId: 'demo-001',
  latency: 380,
  finishReason: 'stop',
}

export const DEMO_CHARACTERS = [
  {
    id: 201, novelId: 101, name: '江末', gender: '男', age: '26',
    appearance: '瘦高，左眼下有一道旧疤，常年穿洗得发白的灰色工装。',
    background: '原地表勘测队队员，避难所 0712 号冬眠者。醒来时全队只剩他一人。',
    personality: '寡言，观察力极强；对陌生人保持距离，但一旦认定就不会放手。',
    extra: '{"口头禅":"先看看再说"}',
    createTime: '2026-06-13 10:00:00',
  },
  {
    id: 202, novelId: 101, name: '林晚', gender: '女', age: '24',
    appearance: '短发，右手虎口有烧伤疤痕，随身背一只金属工具箱。',
    background: '拾荒者聚落"灯塔"的机械师，能修好任何带齿轮的东西。',
    personality: '嘴硬心软，话多，怕黑，从不提家人。',
    extra: '{"技能":"机械维修/地图绘制"}',
    createTime: '2026-06-15 14:20:00',
  },
  {
    id: 203, novelId: 101, name: '老白', gender: '男', age: '58',
    appearance: '花白胡子，左腿是机械义肢，走路时有轻微的金属摩擦声。',
    background: '"灯塔"现任负责人，前避难所副所长，知道地表广播中断的真相。',
    personality: '慈和外表下藏着极端的决断力；睡前必听一段旧世界的电台录音。',
    extra: '{"秘密":"隐瞒了第九次广播的内容"}',
    createTime: '2026-06-20 09:00:00',
  },
]

export const DEMO_TIMELINES = [
  { id: 301, novelId: 101, name: '主线 · 复燃纪元', description: '从苏醒到重建地表基站', parentId: null },
  { id: 302, novelId: 101, name: '支线 · 灯塔往事', description: '聚落建立前后的旧事', parentId: 301 },
]

export const DEMO_NODES = [
  { id: 401, novelId: 101, timelineId: 301, title: '江末苏醒', content: '冬眠舱开启，全队罹难，江末成为 0712 号唯一幸存者。', eventDate: '复燃纪元 1 年春', eventType: '起点', importance: '高', characterNames: '江末', tags: '开篇,幸存' },
  { id: 402, novelId: 101, timelineId: 301, title: '抵达灯塔', content: '徒步七天抵达拾荒者聚落"灯塔"，初见林晚与老白。', eventDate: '复燃纪元 1 年春', eventType: '相遇', importance: '高', characterNames: '江末,林晚,老白', tags: '聚落' },
  { id: 403, novelId: 101, timelineId: 301, title: '第一缕信号', content: '检修旧电台时收到一段重复三遍的呼号，方向指向北方废墟。', eventDate: '复燃纪元 1 年夏', eventType: '转折', importance: '高', characterNames: '江末,林晚', tags: '伏笔,广播' },
  { id: 404, novelId: 101, timelineId: 302, title: '灯塔建立', content: '老白带三十人从避难所出逃，在山顶点亮第一盏太阳能灯。', eventDate: '复燃纪元前 3 年', eventType: '回忆', importance: '中', characterNames: '老白', tags: '旧事' },
]

/** RAG 知识库文档（平行数组口径：ids/documents/metadatas） */
export const DEMO_RAG_DOCUMENTS = {
  ids: ['doc-1', 'doc-2', 'doc-3', 'doc-4'],
  documents: [
    '江末：26 岁，原地表勘测队队员，左眼下有旧疤，避难所 0712 号冬眠者……',
    '林晚：24 岁，灯塔聚落机械师，短发，右手虎口有烧伤疤痕，怕黑……',
    '复燃纪元：旧文明终结后的纪年方式，以首批避难所重返地表为元年……',
    '灯塔：建立在原气象站山顶的拾荒者聚落，以夜间点灯作为归巢信号……',
  ],
  metadatas: [
    { source: '长夜余火', category: '角色设定', book: '设定文档' },
    { source: '长夜余火', category: '角色设定', book: '设定文档' },
    { source: '长夜余火', category: '世界观', book: '设定文档' },
    { source: '长夜余火', category: '势力', book: '设定文档' },
  ],
  page: 1,
  page_size: 20,
  total: 4,
}

export const DEMO_RAG_STATS = {
  total_collections: 3,
  total_documents: 4,
  embedding_model: 'bge-m3',
  embedding_dimension: 1024,
  connected: true,
  collection_details: [
    { name: '长夜余火', id: 'c-101', count: 4, metadata: { source: '长夜余火' } },
    { name: '山海客栈', id: 'c-102', count: 0, metadata: { source: '山海客栈' } },
    { name: '星轨之上', id: 'c-103', count: 0, metadata: { source: '星轨之上' } },
  ],
  source_distribution: [{ source: '长夜余火', count: 4 }],
  category_distribution: [
    { category: '角色设定', count: 2 },
    { category: '世界观', count: 1 },
    { category: '势力', count: 1 },
  ],
}
