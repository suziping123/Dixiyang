// 演示模式 mock 数据（静态站展示用）——只在 VITE_DEMO=1 构建中被动态加载
import type { Novel } from '@/api/types'

export const DEMO_USER = {
  userId: 1,
  username: 'demo',
  nickname: '演示用户',
  email: 'demo@example.com',
  role: 'admin' as const, // 演示环境放行管理后台
}

/** 小说列表（网文风格假数据，封面留空走默认封面） */
export const DEMO_NOVELS: Novel[] = [
  {
    id: 101,
    title: '长夜余火',
    pen_name: '演示笔名',
    description: '旧世界在核火中熄灭，文明的余烬沉入地底。少年从冬眠舱醒来，带着一段不属于自己的记忆，走进灰雾笼罩的废墟城市。',
    cover_url: '',
    createTime: '2026-06-12 10:00:00',
    updateTime: '2026-10-12 21:30:00',
    char_count: 128000,
    node_count: 42,
    relation_count: 6,
  },
  {
    id: 102,
    title: '山海客栈',
    pen_name: '演示笔名',
    description: '开在官道尽头的客栈，只做妖与人的生意。掌柜的算盘一响，来的都是要赊账的神仙。',
    cover_url: '',
    createTime: '2026-07-03 14:20:00',
    updateTime: '2026-10-10 18:05:00',
    char_count: 86000,
    node_count: 27,
    relation_count: 4,
  },
  {
    id: 103,
    title: '第七次重生后我决定摆烂',
    pen_name: '演示笔名',
    description: '拯救世界六次都失败了，第七次她收拾包袱回了老家：这世界谁爱救谁救。',
    cover_url: '',
    createTime: '2026-08-21 09:10:00',
    updateTime: '2026-10-13 11:44:00',
    char_count: 54000,
    node_count: 18,
    relation_count: 3,
  },
  {
    id: 104,
    title: '星轨之上',
    pen_name: '演示笔名',
    description: '人类向深空派出的第九艘移民船失联三百年后，地球突然再次收到了它的信号。',
    cover_url: '',
    createTime: '2026-09-01 16:00:00',
    updateTime: '2026-10-14 08:20:00',
    char_count: 23000,
    node_count: 9,
    relation_count: 2,
  },
]
