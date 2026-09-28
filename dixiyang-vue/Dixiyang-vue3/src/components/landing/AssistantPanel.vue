<script setup lang="ts">
/**
 * 03 · 助手：五模式流式对话（打字机）+ 语料墙检索之光
 * 面板激活（或移动端常显）时首轮运行；事实与机制来自 docs/介绍.md
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps<{ isActive: boolean }>()

type Mode = {
  id: string
  label: string
  q: string
  a: string
  refs: { src: string; text: string }[]
}

const modes: Mode[] = [
  {
    id: 'write',
    label: '创作',
    q: '写一段沈砚回到旧宅的开场',
    a: '门轴发出一声长音，堂屋里的座钟仍停在三点十分——三年前他离开的那一刻。沈砚没有去碰那只钟，只是把青铜钥匙放在八仙桌上，等着身后的人先开口。',
    refs: [
      { src: '第三章 · 旧宅', text: '座钟停在三点十分，堂屋积了一指厚的灰。' },
      { src: '角色卡 · 沈砚', text: '左撇子；说谎时会摸耳垂；随身物：青铜钥匙。' },
    ],
  },
  {
    id: 'discuss',
    label: '讨论',
    q: '沈砚这个时候该不该说出真相？',
    a: '从角色卡看，他惯于让证据先开口——第十四章他已把密信副本交给阿箬。此刻说出来反而违背人设；更好的处理是让知府自己撞上那枚松烟墨的落款。',
    refs: [
      { src: '第九章 · 书房', text: '密信落款只有一滴松烟墨，是知府的旧习惯。' },
      { src: '时间线 · 支线', text: '第十四章：沈砚将密信副本交给阿箬。' },
    ],
  },
  {
    id: 'analyze',
    label: '分析',
    q: '分析第十二到十五章的伏笔密度',
    a: '三章共埋设 4 处伏笔：第九个灯架的无名灯笼、老艄公的少找铜板、知府换印、阿箬怕水。其中灯笼与换印在第二十二章收束，另两处尚未回收——建议在第二十五章前处理，否则会成为断线。',
    refs: [
      { src: '第十二章 · 灯会', text: '无名灯笼挂在第九个灯架，无人认领。' },
      { src: '故事节点 · 转折', text: '知府换印，重要性 4，支线未收束。' },
    ],
  },
  {
    id: 'brainstorm',
    label: '头脑风暴',
    q: '给主线加三条可能的背叛线索',
    a: '其一，少找的那枚铜板其实是漕帮的暗记；其二，阿箬怕水却熟识渡口，她可能早与老艄公相识；其三，座钟停摆不是意外，是有人要沈砚记住三点十分这个不在场证明。',
    refs: [
      { src: '第七章 · 渡口', text: '老艄公收了双倍船钱，却少找一枚铜板。' },
      { src: '角色卡 · 阿箬', text: '怕水，却在第十五章跳了河。' },
    ],
  },
  {
    id: 'ask',
    label: '提问',
    q: '雨夜刺杀发生在哪家客栈？',
    a: '望月客栈，在西市第三巷，后门通护城河——第二章的刺客正是从后门离开，刀柄缠的白布在雨里始终没松。刺杀时间是主线第七日的亥时三刻。',
    refs: [
      { src: '设定 · 地理', text: '望月客栈，西市第三巷，后门通护城河。' },
      { src: '时间线 · 主线', text: '雨夜刺杀 → 沈砚离城，间隔七日。' },
    ],
  },
]

/* 语料墙：私有知识库片段（示意内容，非数据证明） */
const corpus: { text: string; hit?: string }[] = [
  { text: '第三章·旧宅：沈砚推开门时，堂屋的座钟停在三点十分。', hit: 'q3' },
  { text: '角色卡·沈砚：三十岁，左撇子，说谎时会摸耳垂。', hit: 'q1' },
  { text: '时间线·主线：雨夜刺杀 → 沈砚离城，间隔七日。', hit: 'q2' },
  { text: '设定·势力：漕帮与知府衙门表面交好，实则互握把柄。' },
  { text: '第七章·渡口：老艄公收了双倍船钱，却少找了一枚铜板。', hit: 'q1' },
  { text: '故事节点·高潮：城门对峙，重要性 5，主线必经。' },
  { text: '第十二章·灯会：无名灯笼挂在第九个灯架，无人认领。' },
  { text: '角色卡·阿箬：怕水，却在第十五章跳了河。' },
  { text: '设定·地理：望月客栈在西市第三巷，后门通护城河。', hit: 'q2' },
  { text: '第十五章·河畔：血混进雨水，把青石缝染成褐色。' },
  { text: '时间线·支线：漕帮内斗，与主线并行十八日。' },
  { text: '设定·物件：青铜钥匙，齿纹对应旧宅东厢的锁。', hit: 'q3' },
  { text: '第二章·雨夜：刺客左手持刀，刀柄缠着白布。', hit: 'q1' },
  { text: '故事节点·转折：知府换印，重要性 4，支线。' },
  { text: '角色卡·知府：靠漕运起家，怕见血，左手有旧疤。' },
  { text: '第九章·书房：密信落款只有一滴松烟墨。' },
  { text: '设定·律法：城门酉时落锁，迟开须虎符。' },
  { text: '第十八章·对峙：阿箬亮出钥匙，全场安静。', hit: 'q3' },
]

const queries = [
  { id: 'q1', text: '沈砚"左撇子"的细节在哪些章节出现过？', hits: 3 },
  { id: 'q2', text: '雨夜刺杀前后的时间线', hits: 2 },
  { id: 'q3', text: '青铜钥匙的来历', hits: 3 },
]

const activeMode = ref(0)
const activeQuery = ref('q1')
const thinking = ref(false)
const typed = ref('')
const refsVisible = ref(false)
const searching = ref(false)
const started = ref(false)

const reduced = () =>
  typeof window !== 'undefined' &&
  window.matchMedia('(prefers-reduced-motion: reduce)').matches

let typeTimer: ReturnType<typeof setInterval> | null = null
let searchTimers: ReturnType<typeof setTimeout>[] = []

const clearType = () => {
  if (typeTimer) {
    clearInterval(typeTimer)
    typeTimer = null
  }
}
const clearTimers = () => {
  searchTimers.forEach(clearTimeout)
  searchTimers = []
}

const runTypewriter = (mode: Mode) => {
  clearType()
  clearTimers()
  refsVisible.value = false

  if (reduced()) {
    thinking.value = false
    typed.value = mode.a
    refsVisible.value = true
    return
  }

  thinking.value = true
  typed.value = ''
  let i = 0
  searchTimers.push(
    setTimeout(() => {
      thinking.value = false
      typeTimer = setInterval(() => {
        i += 2
        typed.value = mode.a.slice(0, i)
        if (i >= mode.a.length) {
          clearType()
          refsVisible.value = true
        }
      }, 34)
    }, 750),
  )
}

const runSearch = (qid: string) => {
  activeQuery.value = qid
  if (reduced()) {
    searching.value = false
    return
  }
  searching.value = false
  searchTimers.push(
    setTimeout(() => {
      searching.value = true
      searchTimers.push(setTimeout(() => (searching.value = false), 950))
    }, 30),
  )
}

const start = () => {
  if (started.value) return
  started.value = true
  runSearch('q1')
  runTypewriter(modes[0]!)
}

const pickMode = (idx: number) => {
  activeMode.value = idx
  const m = modes[idx]
  if (m) runTypewriter(m)
}

const current = computed(() => modes[activeMode.value] ?? modes[0]!)

/* 面板激活时首轮运行；移动端降级为常显，挂载即运行 */
if (typeof window !== 'undefined') {
  if (window.matchMedia('(max-width: 768px)').matches) {
    start()
  }
}
const unwatch = watch(
  () => props.isActive,
  (v) => {
    if (v) start()
  },
)

onBeforeUnmount(() => {
  clearType()
  clearTimers()
  unwatch()
})
</script>

<template>
  <section
    id="panel-assistant"
    class="ld-panel ld-p-assistant"
    role="tabpanel"
    aria-labelledby="tab-assistant"
  >
    <div class="ld-panel__head">
      <p class="ld-eyebrow" data-ld-in>
        ASSISTANT <span class="zh">· 它不是在猜，是在查</span>
      </p>
      <h2 class="ld-h2" data-ld-in>先检索你的知识库，再回答你。</h2>
      <p class="ld-p-assistant__lead" data-ld-in>
        电子书与设定文档构建为私有知识库；回答前先召回、再精排，引用来源随回答一起推到前端。
      </p>
    </div>

    <div class="ld-p-assistant__grid" data-ld-in>
      <!-- 左：流式对话演示 -->
      <div>
        <div class="ld-modes" role="group" aria-label="对话模式">
          <button
            v-for="(m, i) in modes"
            :key="m.id"
            class="ld-mode"
            type="button"
            :aria-pressed="activeMode === i"
            @click="pickMode(i)"
          >
            {{ m.label }}
          </button>
        </div>

        <div class="ld-chat" aria-live="polite">
          <div class="ld-chat__meta">
            <span>MODE · {{ current.label }}</span>
            <span>STREAM · SSE</span>
          </div>
          <p class="ld-chat__thinking" v-if="thinking">thinking… 检索角色卡与时间线</p>
          <div class="ld-chat__bubble">
            <span>{{ typed }}</span
            ><span
              v-if="thinking || typed.length < current.a.length"
              class="caret"
              aria-hidden="true"
            ></span>
          </div>
          <div class="ld-chat__refs" v-show="refsVisible">
            <p class="ld-chat__ref" v-for="r in current.refs" :key="r.src">
              <i>REF</i>
              <span><b>{{ r.src }}</b> —— {{ r.text }}</span>
            </p>
          </div>
          <div class="ld-chat__input" aria-hidden="true">
            <span>继续追问，或换个模式再问一次</span>
            <kbd>ENTER</kbd>
          </div>
        </div>
      </div>

      <!-- 右：语料墙 + 检索之光 -->
      <div class="ld-corpus" :class="{ 'is-searching': searching }">
        <div class="ld-corpus__queries" role="group" aria-label="检索示例">
          <button
            v-for="q in queries"
            :key="q.id"
            class="ld-query"
            type="button"
            :aria-pressed="activeQuery === q.id"
            @click="runSearch(q.id)"
          >
            <svg viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="7" cy="7" r="4.5" />
              <path d="m10.5 10.5 4 4" stroke-linecap="round" />
            </svg>
            {{ q.text }}
          </button>
        </div>

        <div class="ld-corpus__wall">
          <div class="ld-corpus__beam" aria-hidden="true"></div>
          <p
            v-for="(line, i) in corpus"
            :key="i"
            class="ld-corpus__line"
            :class="{ 'is-hit': line.hit === activeQuery }"
            :style="{ transitionDelay: `${(i % 6) * 45}ms` }"
          >
            {{ line.text }}
          </p>
        </div>

        <div class="ld-corpus__stats">
          <span>RECALL topK×4 = <b>40</b></span>
          <span>RERANK → <b>5</b> · HIT {{ queries.find((q) => q.id === activeQuery)?.hits ?? 0 }}</span>
        </div>
      </div>
    </div>

    <p class="ld-p-assistant__facts" data-ld-in>
      <span><b>两级检索</b>：bge-m3 召回 topK×4 → bge-reranker 精排取 topK</span>
      <span><b>工具循环</b>：Agent 最多 5 轮调用，来源结构化回推</span>
      <span><b>纠错学习</b>：改掉 AI 的回答，修正会注入后续对话</span>
    </p>
  </section>
</template>
