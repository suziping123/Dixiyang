<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { getNovelOptions, getCharacters, getChatSessions } from '@/api/ideaApi'

/**
 * 来源选择器（小说→角色 / 小说→对话 级联），写点子与下架编辑共用。
 * v-model=sourceRef、v-model:novelId；暴露 echo() 供父在回显值设置后反查小说。
 * @change = 用户改动（供写点子重置预览）。
 */
const props = defineProps<{
  category: string
  modelValue: string
  novelId: number | ''
  label?: string
}>()
const emit = defineEmits<{
  'update:modelValue': [string]
  'update:novelId': [number | '']
  change: []
}>()

const unwrap = <T,>(res: unknown): T | null => {
  const r = res as { code?: number; msg?: string; data?: T }
  if (r && r.code === 200) return r.data as T
  ElMessage.warning((r && r.msg) || '操作失败')
  return null
}

const isChar = computed(() => props.category === 'character')
const fieldLabel = computed(
  () =>
    props.label ??
    (isChar.value
      ? '来源角色（发布时导出为角色卡附件）'
      : '来源对话（可选；先选小说再选对话，发布时导出为对话快照附件）'),
)

const sourceRef = computed({
  get: () => props.modelValue,
  set: (v: string) => emit('update:modelValue', v),
})
const novelId = computed({
  get: () => props.novelId,
  set: (v: number | '') => emit('update:novelId', v),
})

const novels = ref<{ id: number; title: string }[]>([])
const characters = ref<{ id: number; name: string }[]>([])
const charsLoading = ref(false)
const sessions = ref<{ sessionId: string; title: string; novelId?: number | null }[]>([])
const sessionsLoading = ref(false)

const loadSessions = async (nid?: number | '') => {
  sessionsLoading.value = true
  try {
    const list = unwrap<{ sessionId: string; title: string; novelId?: number | null }[]>(
      await getChatSessions(nid ? Number(nid) : null),
    )
    sessions.value = list ?? []
  } finally {
    sessionsLoading.value = false
  }
}

// 初始化：小说列表 + 全量对话（对话回显反查 novelId 要用）。
// 懒且可重入：首次调用才发请求；失败清缓存，下次交互自动重试（未登录/网络抖动不炸 console）。
let readyPromise: Promise<void> | null = null
const ensureReady = () => {
  if (!readyPromise) {
    readyPromise = (async () => {
      const [novelRes, sessRes] = await Promise.all([getNovelOptions(), getChatSessions()])
      novels.value = unwrap<{ records: { id: number; title: string }[] }>(novelRes)?.records ?? []
      sessions.value = unwrap<{ sessionId: string; title: string; novelId?: number | null }[]>(sessRes) ?? []
    })().catch((e) => {
      readyPromise = null
      throw e
    })
  }
  return readyPromise
}

/** 父设置好 modelValue 后调用：按来源反查所属小说并填充二级列表 */
const echo = async () => {
  await ensureReady()
  if (!props.modelValue) return
  if (isChar.value) {
    const cid = Number(props.modelValue)
    const all = await Promise.all(novels.value.map((n) => getCharacters(n.id)))
    for (let i = 0; i < all.length; i++) {
      const list = unwrap<{ id: number; name: string }[]>(all[i]) ?? []
      const hit = list.find((c) => c.id === cid)
      const nv = novels.value[i]
      if (hit && nv) {
        emit('update:novelId', nv.id)
        characters.value = list
        break
      }
    }
  } else {
    const hit = sessions.value.find((s) => s.sessionId === props.modelValue)
    if (hit?.novelId) {
      emit('update:novelId', hit.novelId)
      await loadSessions(hit.novelId)
    }
  }
}

const onNovelChange = async () => {
  emit('update:modelValue', '')
  emit('change')
  await ensureReady().catch(() => {})
  if (isChar.value) {
    characters.value = []
    if (!novelId.value) return
    charsLoading.value = true
    try {
      const list = unwrap<{ id: number; name: string }[]>(await getCharacters(Number(novelId.value)))
      characters.value = list ?? []
    } finally {
      charsLoading.value = false
    }
  } else {
    await loadSessions(novelId.value)
  }
}

defineExpose({ echo, characters, sessions, ensureReady })
</script>

<template>
  <div class="field">
    <label class="field-label">{{ fieldLabel }}</label>
    <div class="source-row">
      <el-select
        v-model="novelId"
        placeholder="选择小说"
        :clearable="!isChar"
        filterable
        @visible-change="(v: boolean) => v && ensureReady().catch(() => {})"
        @change="onNovelChange"
      >
        <el-option v-if="!isChar" label="未绑定小说" :value="''" />
        <el-option v-for="n in novels" :key="n.id" :label="n.title" :value="n.id" />
      </el-select>
      <el-select
        v-if="isChar"
        v-model="sourceRef"
        placeholder="选择角色"
        filterable
        :loading="charsLoading"
        @change="emit('change')"
      >
        <el-option v-for="c in characters" :key="c.id" :label="c.name" :value="String(c.id)" />
      </el-select>
      <el-select
        v-else
        v-model="sourceRef"
        placeholder="选择对话（不选则纯文字发布）"
        clearable
        filterable
        :loading="sessionsLoading"
        @change="emit('change')"
      >
        <el-option v-for="s in sessions" :key="s.sessionId" :label="s.title" :value="s.sessionId" />
      </el-select>
    </div>
  </div>
</template>

<style scoped>
.source-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

@media (max-width: 768px) {
  .source-row {
    grid-template-columns: 1fr;
  }
}
</style>
