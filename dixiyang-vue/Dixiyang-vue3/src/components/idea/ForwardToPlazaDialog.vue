<template>
  <el-dialog
    v-model="visible"
    title="转发到广场"
    width="640px"
    :close-on-click-modal="false"
  >
    <div class="plaza-dialog">
      <!-- 标题 + AI 候选 -->
      <div class="field">
        <div class="field-label">标题</div>
        <div class="title-row">
          <el-input
            v-model="title"
            maxlength="60"
            show-word-limit
            placeholder="帖子标题"
            @keyup.enter="enterSubmit(doSaveDraft, $event)"
          />
          <button
            class="ai-btn"
            type="button"
            :disabled="suggesting"
            :title="suggesting ? '生成中…' : 'AI 生成标题与标签候选'"
            @click="fetchSuggest"
          >
            <svg class="ai-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/>
              <circle cx="12" cy="12" r="3.2"/>
            </svg>
            {{ suggesting ? '生成中…' : 'AI 候选' }}
          </button>
        </div>

        <!-- 候选区：点击一键应用 -->
        <transition name="cand">
          <div v-if="cand.title || cand.tags.length" class="cand-box">
            <div class="cand-head">
              <span>AI 候选</span>
              <button class="cand-apply-all" type="button" @click="applyAll">一键应用</button>
            </div>
            <div v-if="cand.title" class="cand-title" :class="{ applied: cand.titleApplied }" @click="applyTitle">
              {{ cand.title }}
              <span class="cand-hint">{{ cand.titleApplied ? '已应用' : '点击应用到标题' }}</span>
            </div>
            <div v-if="cand.tags.length" class="cand-tags">
              <span
                v-for="t in cand.tags"
                :key="t"
                class="cand-tag"
                :class="{ applied: appliedTags.has(t) }"
                @click="applyTag(t)"
              >{{ appliedTags.has(t) ? '✓ ' : '+ ' }}{{ t }}</span>
            </div>
          </div>
        </transition>
      </div>

      <!-- 分区 + 标签 -->
      <div class="meta-row">
        <div class="field meta-cat">
          <div class="field-label">分区</div>
          <el-select v-model="category">
            <el-option v-for="c in CATEGORIES" :key="c.key" :label="c.label" :value="c.key" />
          </el-select>
        </div>
        <div class="field meta-tags">
          <div class="field-label">标签</div>
          <el-select
            v-model="tags"
            multiple
            filterable
            allow-create
            default-first-option
            :multiple-limit="5"
            placeholder="回车创建标签（最多 5 个）"
          >
            <el-option v-for="t in tags" :key="t" :label="t" :value="t" />
          </el-select>
        </div>
      </div>

      <!-- 正文 -->
      <div class="field">
        <div class="field-label">正文</div>
        <el-input v-model="body" type="textarea" :rows="7" maxlength="20000" show-word-limit placeholder="帖子正文" />
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button :loading="saving" @click="doSaveDraft">存草稿</el-button>
        <el-button type="primary" :loading="saving" @click="doPublish">立即发布</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { createDraft, publishDraft } from '@/api/ideaApi'
import type { IdeaCategory } from '@/api/ideaApi'
import http from '@/utils/http'
import { enterSubmit } from '@/utils/enterSubmit'

const props = defineProps<{
  modelValue: boolean
  /** AI 回答原文（作为正文初值） */
  content?: string
}>()
const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'done', mode: 'draft' | 'publish'): void
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const CATEGORIES: { key: IdeaCategory; label: string }[] = [
  { key: 'idea', label: '点子' },
  { key: 'character', label: '角色' },
  { key: 'setting', label: '设定' },
  { key: 'timeline', label: '时间线' },
  { key: 'tech', label: '技术' },
]

const title = ref('')
const body = ref('')
const category = ref<IdeaCategory>('setting')
const tags = ref<string[]>([])
const saving = ref(false)

// ===== AI 候选 =====
const suggesting = ref(false)
const cand = reactive({ title: '', titleApplied: false, tags: [] as string[] })
const appliedTags = computed(() => new Set(tags.value))

async function fetchSuggest() {
  if (!body.value.trim()) {
    ElMessage.warning('正文为空，无内容可分析')
    return
  }
  suggesting.value = true
  try {
    const res = await http.post('/idea/aiSuggest', { content: body.value })
    const data = res.data as { title?: string; tags?: string[] } | null
    if (!data?.title) {
      ElMessage.warning('AI 未生成有效候选')
      return
    }
    cand.title = data.title
    cand.titleApplied = false
    cand.tags = Array.isArray(data.tags) ? data.tags : []
    ElMessage.success('候选已生成，点击即可应用')
  } catch (err) {
    ElMessage.error((err as Error).message || '生成失败')
  } finally {
    suggesting.value = false
  }
}

function applyTitle() {
  if (!cand.title) return
  title.value = cand.title
  cand.titleApplied = true
}

function applyTag(t: string) {
  if (tags.value.includes(t)) {
    tags.value = tags.value.filter((x) => x !== t)
    return
  }
  if (tags.value.length >= 5) {
    ElMessage.warning('最多 5 个标签')
    return
  }
  tags.value = [...tags.value, t]
}

function applyAll() {
  applyTitle()
  for (const t of cand.tags) {
    if (!tags.value.includes(t) && tags.value.length < 5) tags.value = [...tags.value, t]
  }
}

// ===== 打开时初始化 =====
watch(
  () => props.modelValue,
  (open) => {
    if (!open) return
    title.value = ''
    body.value = (props.content ?? '').slice(0, 20000)
    tags.value = []
    category.value = 'setting'
    cand.title = ''
    cand.titleApplied = false
    cand.tags = []
    // 自动跑一次候选（失败静默，用户可手动重试）
    if (body.value.trim()) void fetchSuggestQuiet()
  },
)

/** 打开时的静默候选：不弹成功 toast，失败不打扰 */
async function fetchSuggestQuiet() {
  try {
    const res = await http.post('/idea/aiSuggest', { content: body.value })
    const data = res.data as { title?: string; tags?: string[] } | null
    if (data?.title) {
      cand.title = data.title
      cand.tags = Array.isArray(data.tags) ? data.tags : []
    }
  } catch {
    /* 静默 */
  }
}

// ===== 保存 / 发布 =====
async function saveDraft(): Promise<number | null> {
  if (!title.value.trim()) {
    ElMessage.warning('请输入标题')
    return null
  }
  if (!body.value.trim()) {
    ElMessage.warning('正文不能为空')
    return null
  }
  saving.value = true
  try {
    const res = await createDraft({
      category: category.value,
      title: title.value.trim(),
      content: body.value,
      tags: tags.value,
    })
    const data = res.data as { id?: number } | null
    if (!data?.id) {
      ElMessage.error('创建草稿失败')
      return null
    }
    return data.id
  } catch (err) {
    ElMessage.error((err as Error).message || '创建草稿失败')
    return null
  } finally {
    saving.value = false
  }
}

async function doSaveDraft() {
  const id = await saveDraft()
  if (id === null) return
  ElMessage.success('已存入广场草稿箱，可前往广场继续编辑发布')
  emit('done', 'draft')
  visible.value = false
}

async function doPublish() {
  const id = await saveDraft()
  if (id === null) return
  saving.value = true
  try {
    // previewed=true：本弹窗即发布前预览，满足后端"请先预览附件"约束
    await publishDraft(id, true)
    ElMessage.success('已发布到广场')
    emit('done', 'publish')
    visible.value = false
  } catch (err) {
    ElMessage.error((err as Error).message || '发布失败（草稿已保存，可去广场重发）')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.plaza-dialog {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.title-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ai-btn {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--surface-glass-border);
  border-radius: var(--radius-sm);
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 12.5px;
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--dur-fast) var(--ease-out);
}

.ai-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.ai-btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.ai-icon {
  width: 14px;
  height: 14px;
}

/* 候选区 */
.cand-box {
  margin-top: 8px;
  padding: 10px 12px;
  border: 1px dashed var(--accent-primary);
  border-radius: var(--radius-sm);
  background: var(--accent-soft);
}

.cand-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.cand-apply-all {
  border: none;
  background: transparent;
  color: var(--accent-primary);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
}

.cand-apply-all:hover {
  text-decoration: underline;
}

.cand-title {
  font-size: 14px;
  color: var(--text-on-glass);
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 6px;
  transition: background var(--dur-fast) var(--ease-out);
}

.cand-title:hover {
  background: rgba(255, 255, 255, 0.06);
}

.cand-title.applied {
  color: var(--accent-primary);
}

.cand-hint {
  margin-left: 8px;
  font-size: 11px;
  color: var(--text-muted);
}

.cand-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.cand-tag {
  padding: 3px 10px;
  border-radius: 999px;
  border: 1px solid var(--surface-glass-border);
  background: var(--surface-glass);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--dur-fast) var(--ease-out);
}

.cand-tag:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.cand-tag.applied {
  border-color: var(--accent-primary);
  background: var(--accent-soft-strong);
  color: var(--accent-primary);
}

.meta-row {
  display: flex;
  gap: 12px;
}

.meta-cat {
  width: 130px;
  flex-shrink: 0;
}

.meta-tags {
  flex: 1;
  min-width: 0;
}

/* 候选进出动画 */
.cand-enter-active,
.cand-leave-active {
  transition: opacity var(--dur) var(--ease-out), transform var(--dur) var(--ease-out);
}

.cand-enter-from,
.cand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 768px) {
  .meta-row {
    flex-direction: column;
    gap: 14px;
  }

  .meta-cat {
    width: 100%;
  }
}
</style>
