// 演示 mock —— 用户域与广场/便签：user/info、userConfig、管理后台、点子库、便签

export const DEMO_USER_INFO = { nickname: '演示用户', email: 'demo@example.com' }

export const DEMO_ADMIN_STATS = {
  totals: { users: 128, novels: 46, posts: 312, sessions: 89 },
  postCategories: [
    { category: 'setting', count: 128 },
    { category: 'plot', count: 96 },
    { category: 'character', count: 88 },
  ],
  postTrend: [
    { date: '10-08', count: 12 },
    { date: '10-09', count: 18 },
    { date: '10-10', count: 9 },
    { date: '10-11', count: 24 },
    { date: '10-12', count: 31 },
    { date: '10-13', count: 22 },
    { date: '10-14', count: 27 },
  ],
}

export const DEMO_ADMIN_USERS = {
  total: 4,
  list: [
    { id: 1, username: 'demo', nickname: '演示用户', email: 'demo@example.com', role: 'admin', createTime: '2026-04-22 10:30:00' },
    { id: 2, username: 'writer_lin', nickname: '林间写手', email: 'lin@example.com', role: 'user', createTime: '2026-07-11 12:00:00' },
    { id: 3, username: 'nightowl', nickname: '夜航船', email: 'night@example.com', role: 'user', createTime: '2026-08-02 23:15:00' },
    { id: 4, username: 'sea_breeze', nickname: '海风章节', email: 'sea@example.com', role: 'user', createTime: '2026-09-19 08:45:00' },
  ],
}

/** 点子库帖子（广场/我发布的/收藏共用） */
const post = (over: Partial<Record<string, unknown>>): Record<string, unknown> => ({
  id: 501,
  category: 'setting',
  title: '如果魔药成本是「记忆」',
  content:
    '设定脑洞：炼金术的硬通货不是金币而是记忆。喝下治疗药水要交出一段快乐的童年，晋升药剂要交出一个人的名字。\n\n推演三个方向：① 谁垄断了记忆的储存与销毁；② 忘记爱人的人还在不在爱；③ 记忆商人这个职业的道德困境。',
  tags: ['魔药', '代价设定', '硬奇幻'],
  images: [],
  coverUrl: '',
  authorId: 2,
  authorName: '林间写手',
  viewCount: 1284,
  likeCount: 231,
  collectCount: 87,
  commentCount: 19,
  likedByMe: false,
  collectedByMe: false,
  createTime: '2026-10-12 15:30:00',
  status: 'published',
  ...over,
})

export const DEMO_IDEA_POSTS = [
  post({}),
  post({
    id: 502,
    category: 'plot',
    title: '反派动机清单：别再写「毁灭世界」了',
    content: '整理 8 类站得住脚的反派动机：守护错误的东西、被承诺背叛、逻辑自洽的救世主、爱你所以毁掉你的世界……每类配一部作品案例与主角应对思路。',
    tags: ['反派', '创作方法论'],
    authorId: 3,
    authorName: '夜航船',
    viewCount: 2210,
    likeCount: 415,
    collectCount: 198,
    commentCount: 44,
    createTime: '2026-10-11 21:02:00',
  }),
  post({
    id: 503,
    category: 'character',
    title: '给「嘴硬心软」写十层：从台词到肢体',
    content: '同一个性格标签怎么写出层次：嘴上嫌弃却把伞先递给对方、话说到一半改口、吵架时手里还端着给对方的热水……附十个可直接用的微动作句式。',
    tags: ['角色塑造', '微表情', '台词'],
    authorId: 4,
    authorName: '海风章节',
    viewCount: 967,
    likeCount: 172,
    collectCount: 63,
    commentCount: 12,
    createTime: '2026-10-13 10:20:00',
  }),
  post({
    id: 504,
    category: 'setting',
    title: '《长夜余火》可复用的废土资源表',
    content: '水、电池、罐头、药品、燃料五类资源的稀缺度与交换比设计，附一张聚落内部价格随季节波动的曲线思路。',
    tags: ['废土', '资源设计'],
    authorId: 2,
    authorName: '林间写手',
    viewCount: 534,
    likeCount: 88,
    collectCount: 41,
    commentCount: 6,
    createTime: '2026-10-14 08:50:00',
  }),
]

export const DEMO_IDEA_TAGS = [
  { tag: '创作方法论', count: 42 },
  { tag: '角色塑造', count: 36 },
  { tag: '废土', count: 28 },
  { tag: '反派', count: 21 },
  { tag: '魔药', count: 17 },
  { tag: '台词', count: 14 },
]

export const DEMO_IDEA_COMMENTS = {
  total: 2,
  list: [
    { id: 9001, authorId: 3, authorName: '夜航船', content: '第②条直接戳中我，已加入书单细读。', createTime: '2026-10-12 16:10:00' },
    { id: 9002, authorId: 4, authorName: '海风章节', content: '记忆商人这个职业太有戏了，求展开！', createTime: '2026-10-12 18:44:00' },
  ],
}

export const DEMO_DRAFTS = {
  total: 1,
  list: [
    {
      id: 701, category: 'plot', title: '未完成：时间循环里的三个谎言',
      summary: '主角每次循环都会忘记一句关键的话，而那句话正是解开循环的钥匙……',
      sourceRef: null, updateTime: '2026-10-13 22:10:00',
    },
  ],
}

/** 便签（灵感墙） */
export const DEMO_STICKY_NOTES = [
  { id: 801, content: '灵感：让信号只在雨夜出现', color: '#fff3b0', x: 60, y: 80, pinnedRoute: '/inspiration', inPool: false, rotation: -2, zIndex: 1, images: [], done: false, createTime: '2026-10-12 20:00:00', updateTime: '2026-10-12 20:00:00' },
  { id: 802, content: '林晚的工具箱里应该有一件她从不使用的旧物', color: '#cdeffd', x: 340, y: 130, pinnedRoute: '/inspiration', inPool: false, rotation: 1.5, zIndex: 2, images: [], done: false, createTime: '2026-10-13 09:12:00', updateTime: '2026-10-13 09:12:00' },
  { id: 803, content: '读完《故事》第三章：冲突的升级要换维度，不是加量', color: '#ffd6e0', x: 150, y: 320, pinnedRoute: '/inspiration', inPool: false, rotation: -1, zIndex: 3, images: [], done: true, createTime: '2026-10-13 21:40:00', updateTime: '2026-10-14 08:00:00' },
]

/** 用户背景/外观配置（demo 下返回空配置 = 默认外观） */
export const DEMO_USER_CONFIG: Record<string, unknown> = { backgroundId: null, customBgs: '' }
